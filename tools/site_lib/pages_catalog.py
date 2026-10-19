"""Crawlable catalogue: one static page per tyre (kupi-gume/<slug>/), category
pages (kategorija-proizvoda/<x>/) and brand pages (proizvodjac/<x>/), with
WordPress-style pagination (…/page/2/). Every value comes from data/products.json;
the product page JS (product.js) hydrates the same markup for cart, quantity,
compare and the "same size" rail."""
import re
from urllib.parse import quote

from .base import (R, BIZ, PRODUCTS, CATS, BRANDS, esc, fmt, n, icon, page, km, rail, card, img_url, season_label, UPLOADS)
from . import seo

# Standard ETRTO tables (general reference, not shop data) - same as product.js.
LOAD = {70: 335, 71: 345, 72: 355, 73: 365, 74: 375, 75: 387, 76: 400, 77: 412, 78: 425, 79: 437, 80: 450, 81: 462,
        82: 475, 83: 487, 84: 500, 85: 515, 86: 530, 87: 545, 88: 560, 89: 580, 90: 600, 91: 615, 92: 630, 93: 650,
        94: 670, 95: 690, 96: 710, 97: 730, 98: 750, 99: 775, 100: 800, 101: 825, 102: 850, 103: 875, 104: 900,
        105: 925, 106: 950, 107: 975, 108: 1000, 109: 1030, 110: 1060, 111: 1090, 112: 1120, 113: 1150, 114: 1180,
        115: 1215, 116: 1250, 117: 1285, 118: 1320, 119: 1360, 120: 1400, 121: 1450, 122: 1500, 123: 1550, 124: 1600,
        125: 1650, 126: 1700, 127: 1750, 128: 1800, 129: 1850, 130: 1900, 131: 1950, 132: 2000, 133: 2060, 134: 2120,
        135: 2180, 136: 2240, 137: 2300, 138: 2360, 139: 2430, 140: 2500, 141: 2575, 142: 2650, 143: 2725, 144: 2800,
        145: 2900, 146: 3000, 147: 3075, 148: 3150, 149: 3250, 150: 3350, 151: 3450, 152: 3550, 153: 3650, 154: 3750,
        155: 3875, 156: 4000, 157: 4125, 158: 4250, 159: 4375, 160: 4500}
SPEED = {'J': 100, 'K': 110, 'L': 120, 'M': 130, 'N': 140, 'P': 150, 'Q': 160, 'R': 170, 'S': 180, 'T': 190, 'U': 200,
         'H': 210, 'V': 240, 'W': 270, 'Y': 300}
CAT_LABEL = {c: t for c, t, _, _ in CATS} | {'ostalo': 'Ostalo'}
CAT_FOR = {'putnicke': 'putnička vozila, SUV i 4x4', 'poluteretne': 'kombije i laka dostavna vozila',
           'teretne': 'kamione, autobuse i prikolice', 'industrijske': 'viljuškare i radne mašine',
           'poljoprivredne': 'traktore i priključne mašine', 'ostalo': 'vozila'}
FLAG = {'XL': 'Ojačana (XL)', 'RunFlat': 'Run Flat', 'FR': 'Zaštita felne (FR)', 'M+S': 'M+S'}
OUT_OF_STOCK = 'Proizvod trenutno nije na zalihama. Molimo vas da nas pozovete za više informacija na broj: 032/546-10-11'
PER_PAGE = 48


def on_sale(p):
    return 'r' in p and 0 < p['p'] < p['r'] and not p.get('np')


def load_kg(p):
    return LOAD.get(int(p['li'].split('/')[0])) if p.get('li') and p['li'].split('/')[0].isdigit() else None


def full_title(p):
    return ' '.join(x for x in (p['sz'] or p['n'], p['b'], p['m']) if x).strip()


def season_word(z):
    return {'letnja': 'letnja', 'zimska': 'zimska', 'sve': 'za sve sezone'}.get(z, '')


def description(p):
    """A factual paragraph built only from the product's own fields."""
    t = full_title(p)
    kind = f'{season_word(p["z"])} guma' if p['z'] and p['z'] != 'sve' else ('guma za sve sezone' if p['z'] == 'sve' else 'guma')
    s = [f'{t} je {kind} za {CAT_FOR.get(p["c"], "vozila")}.']
    if p.get('li') and p.get('si'):
        kg, kmh = load_kg(p), SPEED.get(p['si'])
        s.append(f'Indeks nosivosti {p["li"]}{f" (do {n(kg)} kg po gumi)" if kg else ""} i indeks brzine {p["si"]}'
                 f'{f" (do {kmh} km/h)" if kmh else ""}.')
    if p.get('f'):
        s.append('Oznake: ' + ', '.join(FLAG.get(f, f) for f in p['f']) + '.')
    if p.get('np'):
        s.append('Cena je na upit.')
    else:
        s.append(f'Cena {fmt(p["p"])} po komadu sa PDV-om' + (f' (umesto {fmt(p["r"])})' if on_sale(p) else '') + '.')
    s.append('Na stanju, isporuka 1-3 radna dana.' if p['st'] else 'Trenutno nije na stanju - pozovite nas za rok nabavke.')
    s.append('Montažu i balansiranje radimo u Guma Servisu u Čačku.')
    return ' '.join(s)


def meta_desc(p):
    bits = [full_title(p)]
    if p['z']:
        bits.append(f'{season_word(p["z"])} guma' if p['z'] != 'sve' else 'guma za sve sezone')
    price = 'cena na upit' if p.get('np') else f'{fmt(p["p"])} sa PDV-om'
    stock = 'na stanju' if p['st'] else 'na upit'
    return f'{", ".join(bits)}. {price[0].upper() + price[1:]}, {stock}. Dostava 1-3 radna dana, montaža u Čačku. Čajka M.'


def product_ld(p, url):
    d = {'@type': 'Product', '@id': url + '#product', 'name': full_title(p), 'sku': str(p['id']),
         'image': [img_url(p, True)] if p.get('i') else [], 'description': description(p),
         'category': f'Gume > {CAT_LABEL.get(p["c"], "")}'}
    if p['b']:
        d['brand'] = {'@type': 'Brand', 'name': p['b']}
    props = [('Širina', p['w']), ('Visina', p['h']), ('Prečnik', p['d']), ('Sezona', season_label(p['z'])),
             ('Indeks nosivosti', p.get('li')), ('Indeks brzine', p.get('si'))]
    d['additionalProperty'] = [{'@type': 'PropertyValue', 'name': k, 'value': v} for k, v in props if v]
    if not p.get('np'):
        d['offers'] = {'@type': 'Offer', 'url': url, 'priceCurrency': 'RSD', 'price': f'{p["p"]:.2f}',
                       'availability': 'https://schema.org/InStock' if p['st'] else 'https://schema.org/OutOfStock',
                       'itemCondition': 'https://schema.org/NewCondition',
                       'seller': {'@id': seo.CANONICAL_BASE + '#org'}}
    return d


def specs(p):
    kg, kmh = load_kg(p), SPEED.get(p.get('si') or '')
    rows = [('Proizvođač', esc(p['b'])), ('Model', esc(p['m'])), ('Dimenzija', f'<span class="sz">{esc(p["sz"])}</span>' if p['sz'] else ''),
            ('Širina', p['w'] and f'{p["w"]}{" mm" if re.fullmatch(r"[0-9]{3}", p["w"]) else ""}'),
            ('Visina (profil)', p['h'] and f'{p["h"]}{" %" if re.fullmatch(r"[0-9]{2}", p["h"]) else ""}'),
            ('Prečnik felne', p['d'] and f'{p["d"]}"'), ('Sezona', season_label(p['z'])), ('Tip gume', CAT_LABEL.get(p['c'])),
            ('Indeks nosivosti', p.get('li') and f'{p["li"]}{f" - do {n(kg)} kg po gumi" if kg else ""}'),
            ('Indeks brzine', p.get('si') and f'{p["si"]}{f" - do {kmh} km/h" if kmh else ""}'),
            ('Pozicija', p.get('pos') and esc(p['pos'])), ('Karakteristike', ', '.join(p.get('f', []))),
            ('Zemlja porekla', f'<span class="todo">{icon("info")}Podatak za dopunu</span>'), ('Šifra', str(p['id']))]
    return ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in rows if v)


def code_parts(p):
    kg, kmh = load_kg(p), SPEED.get(p.get('si') or '')
    parts = [(p['w'], 'Širina', 'mm' if re.fullmatch(r'[0-9]{3}', p['w'] or '') else ''),
             (p['h'], 'Visina', '% širine' if re.fullmatch(r'[0-9]{2}', p['h'] or '') else ''),
             (p['d'] and f'R{p["d"]}', 'Prečnik', 'cola'),
             (p.get('li'), 'Nosivost', f'{n(kg)} kg' if kg else ''), (p.get('si'), 'Brzina', f'{kmh} km/h' if kmh else '')]
    return ''.join(f'<div><b>{esc(v)}</b><span>{k}{f"<br>{u}" if u else ""}</span></div>' for v, k, u in parts if v)


def tags(p):
    t = []
    if p['z']:
        t.append(f'<li data-s="{p["z"]}"><i></i>{season_label(p["z"])}</li>')
    t.append(f'<li>{CAT_LABEL.get(p["c"], "")}</li>')
    if p.get('li'):
        kg, kmh = load_kg(p), SPEED.get(p.get('si') or '')
        t.append(f'<li>{p["li"]}{p.get("si", "")} · {f"do {n(kg)} kg" if kg else ""}{f", {kmh} km/h" if kmh else ""}</li>')
    t += [f'<li>{FLAG.get(f, f)}</li>' for f in p.get('f', [])]
    if p.get('pos'):
        t.append(f'<li>{esc(p["pos"])}</li>')
    return ''.join(t)


def same_model(p, by_model):
    others = [x for x in by_model.get((p['b'], p['m']), []) if x['id'] != p['id']][:24]
    return ''.join(f'<a href="{R}guma.html?p={x["s"]}"><span class="sz">{esc(x["sz"])}</span><small>{"Cena na upit" if x.get("np") else fmt(x["p"])} · '
                   f'{"na stanju" if x["st"] else "nije na stanju"}</small></a>' for x in others)


def product_page(p, by_model):
    title = full_title(p)
    url = seo.canonical(f'kupi-gume/{p["s"]}/')
    sale = on_sale(p)
    pct = round((1 - p['p'] / p['r']) * 100) if sale else 0
    price = ('<p class="price price--ask">Cena na upit</p>' if p.get('np') else
             f'<p class="price">{f"<s>{fmt(p["r"])}</s>" if sale else ""}<b>{fmt(p["p"])}</b><small>po komadu, sa PDV-om</small></p>'
             + (f'<span class="save">Ušteda {fmt(p["r"] - p["p"])} po gumi</span>' if sale else ''))
    stock = (f'<p class="stock stock--ok" data-pdp-stock><i></i>Na stanju - isporuka 1–3 radna dana</p>' if p['st'] else
             f'<p class="stock stock--no" data-pdp-stock><i></i>{OUT_OF_STOCK}</p>')
    model = same_model(p, by_model)
    full = img_url(p, True)
    size_q = (f'sirina={p["w"]}' + (f'&amp;visina={p["h"]}' if p['h'] else '') + f'&amp;precnik={p["d"]}&amp;tip={p["c"]}') if p['w'] and p['d'] else f'tip={p["c"]}'
    cat_link = f'kategorija-proizvoda/{p["c"]}/' if p['c'] in CAT_LABEL and p['c'] != 'ostalo' else 'gume.html'
    li_note = 'Indeksi nosivosti i brzine preuzeti su iz naziva proizvoda' + ('; tip gume određen je prema dimenziji' if p.get('ci') else '') + '. Kilogrami i km/h su standardne vrednosti za dati indeks.'
    body = f'''
<section class="pdp" data-pdp data-slug="{esc(p['s'])}"><div class="wrap">
 <nav class="crumbs" aria-label="Putanja"><ol data-crumbs><li><a href="{R}index.html">Početna</a></li><li><a href="{R}gume.html">Gume</a></li><li><a href="{R}{cat_link}">{CAT_LABEL.get(p['c'], 'Gume')}</a></li><li aria-current="page">{esc(p['sz'] or p['n'])}</li></ol></nav>
 <div class="pdp__grid">
  <div class="pdp__gallery">
   <div class="pdp__stage" data-stage>
    <figure class="pdp__view is-on" data-view-i="0"><div class="pdp__zoom" data-zoom><img data-pdp-img src="{full}" alt="{esc(title)}" width="600" height="600" fetchpriority="high"></div></figure>
    <figure class="pdp__view" data-view-i="1"><div class="pdp__code-art" data-pdp-art></div><figcaption class="fine">Ilustracija: gde se oznaka nalazi na bočnici.</figcaption></figure>
    <span class="card__sale" data-pdp-sale{'' if sale else ' hidden'}>{f'−{pct} %' if sale else ''}</span>
    <span class="pdp__zhint" aria-hidden="true">{icon('search')}Pređite mišem preko slike za uveličanje</span>
   </div>
   <div class="pdp__thumbs" role="tablist" aria-label="Prikaz">
    <button role="tab" aria-selected="true" data-thumb="0"><img data-pdp-thumb src="{img_url(p)}" alt="" loading="lazy"><span>Fotografija</span></button>
    <button role="tab" aria-selected="false" data-thumb="1"><span class="pdp__thumb-code" data-pdp-thumbcode>{esc(p['sz'].split(' ')[0] if p['sz'] else '-')}</span><span>Oznaka na bočnici</span></button>
   </div>
   <p class="fine">Fotografija je ilustrativna; izgled šare odgovara modelu, ne nužno i dimenziji.</p>
  </div>
  <div class="pdp__info">
   <p class="pdp__brand" data-pdp-brand>{esc(p['b'])}{f'<span class="season" data-s="{p["z"]}"><i></i>{season_label(p["z"])}</span>' if p['z'] else ''}</p>
   <h1 class="pdp__t"><span class="sz sz--xl" data-pdp-size>{esc(p['sz'] or p['n'])}</span><span class="pdp__model" data-pdp-model>{esc(p['m'] or p['n'])}</span></h1>
   <ul class="pdp__tags" data-pdp-tags>{tags(p)}</ul>
   <div class="pdp__buy">
    <div class="pdp__price" data-pdp-price>{price}</div>
    {stock}
    <div class="qty-row">
     <div class="qty" data-qty>
      <button type="button" class="icon-btn" data-q="-1" aria-label="Manje">{icon('minus')}</button>
      <input type="number" min="1" max="99" value="4" inputmode="numeric" aria-label="Količina" data-q-input>
      <button type="button" class="icon-btn" data-q="1" aria-label="Više">{icon('plus')}</button>
     </div>
     <div class="qty-presets" role="group" aria-label="Brzi izbor"><button type="button" data-qp="1">1</button><button type="button" data-qp="2">Par</button><button type="button" data-qp="4" aria-pressed="true">Komplet (4)</button></div>
    </div>
    <p class="pdp__total" data-pdp-total aria-live="polite"></p>
    <div class="pdp__cta">
     <button class="btn btn--go btn--lg" data-pdp-add>{icon('cart')}<span>Dodaj u korpu</span></button>
     <button class="btn btn--line btn--lg" data-pdp-compare aria-pressed="false">{icon('compare')}<span>Uporedi</span></button>
    </div>
    <p class="pdp__call">Veća količina ili guma nije na stanju? <a href="tel:{BIZ['phone_href']}">{icon('phone')}{BIZ['phone']}</a></p>
   </div>
   <p class="pdp__desc">{esc(description(p))}</p>
   <ul class="pdp__assure">
    <li>{icon('shield')}<span>Garancija 24 meseca</span></li><li>{icon('truck')}<span>Dostava 1–3 radna dana</span></li>
    <li>{icon('cash')}<span>Plaćanje pouzećem</span></li><li>{icon('wrench')}<span><a href="{R}servis.html">Montaža od {fmt(400)}</a>, plaća se posebno</span></li>
   </ul>
  </div>
 </div>

 <div class="pdp__lower">
  <section class="pdp__specs" aria-labelledby="specs-t">
   {km(1, 'Specifikacija')}
   <h2 id="specs-t" class="d3">Tehnički podaci</h2>
   <dl class="specs" data-pdp-specs>{specs(p)}</dl>
   <p class="fine" data-pdp-specnote>{li_note}</p>
  </section>
  <section class="pdp__read" aria-labelledby="read-t">
   {km(2, 'Oznaka')}
   <h2 id="read-t" class="d3">Kako čitati ovu oznaku</h2>
   <div class="pdp__code" data-pdp-code>{code_parts(p)}</div>
   <p class="fine">Proverite da se oznaka poklapa sa bočnicom gume na vašem vozilu ili sa saobraćajnom dozvolom.</p>
  </section>
 </div>

 <section class="pdp__rel" aria-labelledby="same-t">
  <div class="sec__head">{km(3, 'Ista dimenzija')}<h2 id="same-t" class="d2" data-same-title>Druge gume iste dimenzije</h2><a class="more" data-same-link href="{R}gume.html?{size_q}">Sve u ovoj dimenziji {icon('arrow')}</a></div>
  {rail('', 'Gume iste dimenzije').replace('class="rail__track"', 'class="rail__track" data-same')}
 </section>
 <section class="pdp__rel" aria-labelledby="model-t" data-model-sec{'' if model else ' hidden'}>
  <div class="sec__head">{km(4, 'Isti model')}<h2 id="model-t" class="d2">Druge dimenzije ovog modela</h2></div>
  <div class="sizes-list" data-model>{model}</div>
 </section>
</div>
<div class="buybar" data-buybar hidden><div class="wrap buybar__in"><div><b class="sz" data-bb-size></b><span data-bb-price></span></div><button class="btn btn--go" data-bb-add>{icon('cart')}<span>U korpu</span></button></div></div>
</section>'''
    season = f' {season_word(p["z"])} guma' if p['z'] and p['z'] != 'sve' else (' guma za sve sezone' if p['z'] == 'sve' else ' guma')
    return page(f'kupi-gume/{p["s"]}/index.html', f'{title}{season} - cena | Čajka M', body, active='gume',
                desc=meta_desc(p), scripts=('product',), cls='is-shop', ld=[product_ld(p, url)],
                og_image=full or None, og_type='product', sitemap='proizvodi', images=[full] if full else [])


# ----------------------------------------------------------------- listings
def rec_sort(items):
    return sorted(items, key=lambda p: (-p['st'], -on_sale(p), p.get('np', 0), -p['id']))


def pager(base, cur, total):
    if total < 2:
        return ''
    href = lambda k: f'{R}{base}' + ('' if k == 1 else f'page/{k}/')  # noqa: E731
    nums = sorted({1, total, *range(max(1, cur - 2), min(total, cur + 2) + 1)})
    out, prev = [], 0
    for k in nums:
        if k - prev > 1:
            out.append('<span class="pager__gap">…</span>')
        out.append(f'<a href="{href(k)}"{" aria-current=page" if k == cur else ""}>{k}</a>')
        prev = k
    nav = ''.join(out)
    pv = f'<a class="pager__step" href="{href(cur - 1)}" rel="prev">{icon("arrow-left")}<span>Prethodna</span></a>' if cur > 1 else ''
    nx = f'<a class="pager__step" href="{href(cur + 1)}" rel="next"><span>Sledeća</span>{icon("arrow")}</a>' if cur < total else ''
    return f'<nav class="pager" aria-label="Strane">{pv}<div class="pager__nums">{nav}</div>{nx}</nav>'


def listing(base, name, h1, lede, items, filter_q, label, trail_title=None):
    """Write base/index.html and base/page/N/index.html with prerendered cards."""
    items = rec_sort(items)
    pages = max(1, -(-len(items) // PER_PAGE))
    for k in range(1, pages + 1):
        chunk = items[(k - 1) * PER_PAGE:k * PER_PAGE]
        path = base + ('' if k == 1 else f'page/{k}/') + 'index.html'
        title = f'{h1} - cene i stanje' + (f' (strana {k})' if k > 1 else '') + ' | Čajka M'
        crumbs = (f'<nav class="crumbs" aria-label="Putanja"><ol><li><a href="{R}index.html">Početna</a></li>'
                  f'<li><a href="{R}gume.html">Gume</a></li><li aria-current="page">{esc(trail_title or h1)}</li></ol></nav>')
        body = f'''<section class="phead"><div class="wrap">
 {crumbs}
 {km(1, label)}
 <h1 class="phead__t" data-split>{esc(h1)}</h1>
 <p class="phead__lede">{lede}</p>
 <div class="phead__road" aria-hidden="true"></div>
</div></section>
<section class="sec sec--tight listing"><div class="wrap">
 <div class="toolbar"><p class="toolbar__count">{f'Strana {k} od {pages}' if pages > 1 else ''}</p>
  <a class="btn btn--ink btn--sm" href="{R}gume.html?{filter_q}">{icon('filter')}<span>Filtriraj po dimenziji i sezoni</span></a></div>
 <div class="grid grid--4 listing__grid">{''.join(card(p) for p in chunk)}</div>
 {pager(base, k, pages)}
</div></section>'''
        urls = [seo.canonical(f'kupi-gume/{p["s"]}/') for p in chunk]
        ld = [{'@type': 'ItemList', 'name': h1, 'numberOfItems': len(chunk),
               'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': u} for i, u in enumerate(urls)]}]
        desc = f'{h1} u ponudi Čajka M. {re.sub("<[^>]+>", "", lede)}'[:158]
        page(path, title, body, active='gume', desc=desc, ld=ld, cls='is-shop')
    return pages


def slugify(s):
    s = s.lower().translate(str.maketrans('čćžšđ', 'cczsd'))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def _norm(s):
    return re.sub(r'[^a-z0-9]', '', slugify(s))


LIVE_BRAND = {_norm(x.split('/')[1]): x.split('/')[1] for x in seo.LIVE if x.startswith('proizvodjac/') and x.count('/') == 2}


def brand_slug(b):
    """Same address as the current cajkam.rs brand archive when there is one."""
    return LIVE_BRAND.get(_norm(b), slugify(b))


def all_pages():
    by_model = {}
    for p in PRODUCTS:
        by_model.setdefault((p['b'], p['m']), []).append(p)
    for v in by_model.values():
        v.sort(key=lambda x: (float(re.match(r'[\d.]+', x['d'] or '0').group() or 0), x['w']))
    for p in PRODUCTS:
        product_page(p, by_model)
    count = len(PRODUCTS)
    for c, label, d, _ in CATS:
        items = [p for p in PRODUCTS if p['c'] == c]
        count += listing(f'kategorija-proizvoda/{c}/', label, f'{label} gume', f'{d}. Cene su po komadu, sa PDV-om.',
                         items, f'tip={c}', 'Kategorija')
    brands = sorted({p['b'] for p in PRODUCTS if p['b']}, key=str.lower)
    for b in brands:
        items = [p for p in PRODUCTS if p['b'] == b]
        count += listing(f'proizvodjac/{brand_slug(b)}/', b, f'{b} gume', f'Sve {b} gume u ponudi Čajka M - putničke, poluteretne i ostale dimenzije. Cene su po komadu, sa PDV-om.',
                         items, f'brend={quote(b)}', 'Proizvođač')
    return count
