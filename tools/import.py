"""Import real catalogue + content from the live cajkam.rs (WooCommerce Store API
and the WP REST API) into compact JSON the static site reads.

    python tools/import.py            # normalise the cached raw dumps
    python tools/import.py --fetch    # re-download products, posts and media first

Nothing here invents data. Fields the source does not provide are left empty;
the only derived values are:
  * load / speed index and XL/RunFlat flags, parsed from the product name
    (the shop prints them only there), and
  * a category for the ~1.6k products the shop left uncategorised, inferred
    from the size code (C-suffix -> poluteretne, 17.5/19.5/22.5 -> teretne,
    otherwise putnicke). Those carry `ci: 1` so the UI/README can say so.
"""
import html
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'data'
UA = {'User-Agent': 'Mozilla/5.0 (cajka-m redesign importer)'}
UPLOADS = 'https://cajkam.rs/wp-content/uploads/'


def get(url):
    for attempt in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60)
            return json.load(r), r.headers
        except Exception as e:  # noqa: BLE001 - flaky shared hosting
            print('  retry', url, e)
            time.sleep(3)
    raise SystemExit('failed: ' + url)


def fetch_products():
    out, page = [], 1
    while True:
        data, h = get(f'https://cajkam.rs/wp-json/wc/store/v1/products?per_page=100&page={page}')
        if not data:
            break
        out += data
        print('products page', page, '/', h.get('X-WP-TotalPages'), len(out))
        if page >= int(h.get('X-WP-TotalPages') or page):
            break
        page += 1
        time.sleep(0.4)
    (RAW / 'products.json').write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')


def fetch_pages():
    pages, _ = get('https://cajkam.rs/wp-json/wp/v2/pages?per_page=100&_fields=id,slug,title,content,link')
    (RAW / 'pages.json').write_text(json.dumps(pages, ensure_ascii=False), encoding='utf-8')


LEGAL = ['uslovi-koriscenja', 'uslovi-isporuke', 'zastita-potrosaca', 'politika-privatnosti', 'reklamacije',
         'najcesce-postavljana-pitanja']


def fetch_posts():
    posts, _ = get('https://cajkam.rs/wp-json/wp/v2/posts?per_page=100&_embed=wp:featuredmedia,wp:term')
    (RAW / 'posts.json').write_text(json.dumps(posts, ensure_ascii=False), encoding='utf-8')


# ---------------------------------------------------------------- products
SIZE_RE = re.compile(
    r'(\d{2,3}(?:[.,]\d+)?)\s*/\s*(\d{2,3}(?:[.,]\d+)?)\s*Z?R\s*[- ]?\s*(\d{2}(?:[.,]\d)?C?)', re.I)
ANY_SIZE_RE = re.compile(r'\s*((?:\d{1,3}[Xx])?\d{1,3}(?:[.,]\d+)?(?:/\d{1,3}(?:[.,]\d+)?)?'
                         r'(?:\s*-\s*\d{1,2}(?:[.,]\d)?|\s*Z?R\s*\d{1,2}(?:[.,]\d)?C?))\b')
INDUSTRIAL = re.compile(r'LIFT KING|MPT|MONSTER|ROCK|TRACKING|SKID|SOLID', re.I)
LISI_RE = re.compile(r'(?<![\w/])(\d{2,3}(?:/\d{2,3})?)\s?([JKLMNPQRSTUHVWY])(?![\w])')
FLAGS = [('XL', r'\bXL\b'), ('RunFlat', r'\b(?:RUN ?FLAT|ROF|RFT|SSR|ZP)\b'),
         ('FR', r'\bFR\b'), ('M+S', r'\bM\+S\b|\bMS\b')]

BRAND_CANON = {
    'WEST LAKE': 'Westlake', 'WESTLAKE': 'Westlake', 'BF GOODRICH': 'BFGoodrich', 'BFGOODRICH': 'BFGoodrich',
    'LAUFENN': 'Laufenn', 'SPEEDWAYS': 'Speedways', 'DURATURN': 'Duraturn', 'TOURADOR': 'Tourador',
    'GRIPMAX': 'Gripmax', 'NEXEN': 'Nexen', 'BOTO': 'Boto', 'SEHA': 'Seha', 'KAMA': 'Kama',
    'VOLTYRE': 'Voltyre', 'BKT': 'BKT', 'MITAS': 'Mitas', 'TRAYAL': 'Trayal', 'PETLAS': 'Petlas',
}

SEASON = {
    'letnja': 'letnja', 'letnje': 'letnja', 'summer': 'letnja',
    'zimska': 'zimska', 'zimske': 'zimska', 'winter': 'zimska',
    'all season': 'sve', 'sve sezone': 'sve', 'za sva godišnja doba': 'sve',
}
SOFT3 = {'ALL', 'MAX', 'PRO', 'ECO', 'VAN', 'ICE', 'SUN', 'AIR', 'ONE', 'DUO'}
POSITION = {'vodeća': 'Vodeća', 'vodeca': 'Vodeća', 'pogonska': 'Pogonska', 'prikolica': 'Prikolica',
            'bus': 'Bus'}


def canon_brand(b):
    b = html.unescape(b or '').strip()
    if not b:
        return ''
    up = b.upper()
    if up in BRAND_CANON:
        return BRAND_CANON[up]
    return b if not b.isupper() or len(b) <= 3 else b.title()


def num(s):
    s = s.replace(',', '.')
    return s[:-2] if s.endswith('.0') else s


def attr(p, *names):
    for a in p['attributes']:
        if a['name'] in names and a['terms']:
            return html.unescape(a['terms'][0]['name']).strip()
    return ''


def card_image(img):
    """Smallest uncropped rendition that is still sharp on a card.

    WordPress hard-crops the 300×300 'thumbnail' from the centre, so any
    non-square original (500×600 is common) loses its top and bottom. The
    proportional sizes in 'srcset' keep the whole tyre."""
    sizes = []
    for part in (img.get('srcset') or '').split(','):
        bits = part.split()
        if len(bits) == 2 and bits[1].endswith('w'):
            sizes.append((int(bits[1][:-1]), bits[0]))
    ok = sorted(s for s in sizes if s[0] >= 240)
    return ok[0][1] if ok else (img.get('src') or img.get('thumbnail'))


def normalise(p):
    name = re.sub(r'\s+', ' ', html.unescape(p['name'])).strip()
    brand = canon_brand(attr(p, 'Proizvođač', 'Proizvodjač'))
    w = attr(p, 'Širina', 'Širina gume')
    h = attr(p, 'Visina', 'Visina gume')
    d = attr(p, 'Prečnik', 'Prečnik gume')
    m = SIZE_RE.search(name)
    if m:  # the name is more reliable than half-filled attributes
        w, h, d = w or m.group(1), h or m.group(2), d or m.group(3)
    w, h, d = num(w), num(h), num(d).upper()

    raw_season = attr(p, 'Sezona').lower()
    season, pos = '', attr(p, 'Pozicija')
    ms = False
    if raw_season in SEASON:
        season = SEASON[raw_season]
    elif raw_season:
        base = raw_season.replace(' ms', '')
        ms = raw_season.endswith(' ms')
        pos = pos or POSITION.get(base, raw_season.title())

    # printable size code, exactly as a sidewall would show it
    if m:
        sz = f'{w}/{h} R{d}'
        rest = SIZE_RE.sub(' ', name, count=1)
    else:
        mm = ANY_SIZE_RE.match(name)
        sz = re.sub(r'\s+', ' ', mm.group(1)).strip() if mm else ''
        rest = name[mm.end():] if mm else name
        if not w and mm:
            w = num(re.split(r'[-/xX ]', sz)[0])

    li = si = ''
    hits = list(LISI_RE.finditer(rest))
    if hits:  # the index sits after the model name, so take the last match
        mm = hits[-1]
        li, si = mm.group(1), mm.group(2)
        rest = rest[:mm.start()] + ' ' + rest[mm.end():]
    flags = [f for f, rx in FLAGS if re.search(rx, rest, re.I)]
    if ms and 'M+S' not in flags:
        flags.append('M+S')
    model = rest
    for _, rx in FLAGS:
        model = re.sub(rx, ' ', model, flags=re.I)
    model = re.sub(r'^\s*(putničke|poluteretne|teretne)\s+(letnja|zimska|sve sezone)\s*', ' ', model, flags=re.I)
    if brand:
        model = re.sub(re.escape(brand).replace(r'\ ', r'\s?'), ' ', model, flags=re.I)
        model = re.sub(r'\bwest\s?lake\b', ' ', model, flags=re.I) if brand == 'Westlake' else model
    model = re.sub(r'\s+', ' ', model).strip(' -*,')
    if sz and model.startswith(sz):
        model = model[len(sz):].strip()
    model = ' '.join(t.title() if t.isalpha() and t.isupper() and (len(t) >= 4 or t in SOFT3) else t
                     for t in model.split())

    cats = p['categories']
    ci = 0
    if cats:
        cat = cats[0]['slug']
    else:
        ci = 1
        if not sz:
            cat = 'ostalo'  # e.g. washer fluid sold alongside tyres
        elif brand == 'Speedways' or (not m and re.search(r'\bPR\s?\d|\d\s?PR\b', name)):
            cat = 'industrijske' if INDUSTRIAL.search(name) else 'poljoprivredne'
        elif d in ('17.5', '19.5', '22.5') or pos or (d == '20' and '.' in w):
            cat = 'teretne'
        elif d.endswith('C') or '/' in li:
            cat = 'poluteretne'
        else:
            cat = 'putnicke'

    pr = p['prices']
    price = int(pr['price']) / 100
    reg = int(pr['regular_price']) / 100
    img = p['images'][0] if p['images'] else {}
    tail = lambda u: u.replace(UPLOADS, '') if u else ''  # noqa: E731

    o = {
        'id': p['id'], 's': p['slug'], 'n': name, 'b': brand, 'm': model,
        'sz': sz, 'w': w, 'h': h, 'd': d, 'z': season, 'c': cat,
        'p': price, 'st': 1 if p['is_in_stock'] else 0,
    }
    if reg and reg != price:
        o['r'] = reg
    if li:
        o['li'], o['si'] = li, si
    if flags:
        o['f'] = flags
    if pos:
        o['pos'] = pos
    if ci:
        o['ci'] = 1
    if img:
        o['i'] = tail(card_image(img))
        o['I'] = tail(img.get('src'))
    if not p['is_purchasable'] or not price:
        o['np'] = 1  # price on request
    return o


# ---------------------------------------------------------------- posts
KEEP = {'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'a', 'table', 'thead',
        'tbody', 'tr', 'th', 'td', 'blockquote', 'br', 'figure', 'img', 'figcaption'}


def clean_html(s):
    s = re.sub(r'(?is)<(script|style|iframe)[^>]*>.*?</\1>', '', s)

    def tag(m):
        close, name, attrs = m.group(1), m.group(2).lower(), m.group(3) or ''
        if name not in KEEP:
            return ''
        if close:
            return f'</{name}>'
        keep = ''
        if name == 'a':
            href = re.search(r'href="([^"]+)"', attrs)
            if href:
                keep = f' href="{href.group(1)}"'
        if name == 'img':
            src = re.search(r'src="([^"]+)"', attrs)
            alt = re.search(r'alt="([^"]*)"', attrs)
            if not src:
                return ''
            keep = f' src="{src.group(1)}" alt="{alt.group(1) if alt else ""}" loading="lazy"'
        return f'<{name}{keep}>'

    s = re.sub(r'<img[^>]+/plugins/[^>]+>', '', s)  # theme demo art
    s = re.sub(r'<(/?)([a-zA-Z0-9]+)([^>]*)>', tag, s)
    s = re.sub(r'<(i|em|strong|b)>\s*</\1>', '', s)
    s = re.sub(r'[ \t]*\n\s*', '\n', s)
    s = re.sub(r'<p>\s*(&nbsp;)?\s*</p>', '', s)
    return re.sub(r'\n{3,}', '\n\n', s).strip()


def normalise_post(p):
    emb = p.get('_embedded', {})
    media = (emb.get('wp:featuredmedia') or [{}])[0]
    img = media.get('source_url', '') if isinstance(media, dict) else ''
    terms = [t['name'] for group in emb.get('wp:term', []) for t in group if t.get('taxonomy') == 'category']
    text = re.sub(r'<[^>]+>', ' ', html.unescape(p['content']['rendered']))
    words = len(text.split())
    excerpt = re.sub(r'<[^>]+>', '', html.unescape(p['excerpt']['rendered'])).strip()
    excerpt = re.sub(r'\s*\[&hellip;\]|\s*\[…\]', '…', excerpt)
    return {
        'slug': p['slug'], 'date': p['date'][:10], 'title': html.unescape(p['title']['rendered']),
        'excerpt': excerpt, 'img': img, 'cat': terms[0] if terms else '',
        'min': max(1, round(words / 200)), 'html': clean_html(p['content']['rendered']),
        'src': p['link'],
    }


# ---------------------------------------------------------------- brands
def brand_logos():
    h = (RAW / 'brendovi.html').read_text(encoding='utf-8', errors='ignore')
    files = sorted(set(re.findall(r'uploads/(2024/09/[A-Za-z-]+\.png)', h)))
    out = []
    for f in files:
        stem = f.split('/')[-1][:-4]
        if stem.startswith(('ikonice', 'social')):
            continue
        name = re.sub(r'-(tyres|tires|tire|gume|guma)$', '', stem).replace('-', ' ')
        out.append({'name': canon_brand(name) if name.upper() in BRAND_CANON else name, 'logo': f})
    return out


def main():
    if '--fetch' in sys.argv:
        fetch_products()
    if '--fetch' in sys.argv or not (RAW / 'posts.json').exists():
        fetch_posts()
    if '--fetch' in sys.argv or not (RAW / 'pages.json').exists():
        fetch_pages()

    pages = {p['slug']: {'title': html.unescape(p['title']['rendered']),
                         'html': re.sub(r'^[^<]*', '', clean_html(p['content']['rendered'])),
                         'src': p['link']}
             for p in json.loads((RAW / 'pages.json').read_text(encoding='utf-8')) if p['slug'] in LEGAL}
    (OUT / 'pages.json').write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding='utf-8')

    raw = json.loads((RAW / 'products.json').read_text(encoding='utf-8'))
    prods = [normalise(p) for p in raw]
    prods.sort(key=lambda o: (-o['st'], 'r' not in o, o['b'], o['w'], o['h'], o['d']))
    (OUT / 'products.json').write_text(json.dumps(prods, ensure_ascii=False, separators=(',', ':')),
                                       encoding='utf-8')

    posts = [normalise_post(p) for p in json.loads((RAW / 'posts.json').read_text(encoding='utf-8'))]
    (OUT / 'posts.json').write_text(json.dumps(posts, ensure_ascii=False, indent=1), encoding='utf-8')

    counts = Counter(o['b'] for o in prods)
    logos = brand_logos()
    lower = {b.lower().replace(' ', ''): b for b in counts}
    for lg in logos:
        key = lg['name'].lower().replace(' ', '')
        lg['brand'] = lower.get(key, '')
        lg['count'] = counts.get(lg['brand'], 0) if lg['brand'] else 0
    (OUT / 'brands.json').write_text(json.dumps({'logos': logos, 'counts': counts.most_common()},
                                                ensure_ascii=False, indent=1), encoding='utf-8')

    print('products', len(prods), 'in stock', sum(o['st'] for o in prods),
          'on sale', sum('r' in o for o in prods), 'inferred cat', sum('ci' in o for o in prods))
    print('cats', Counter(o['c'] for o in prods))
    print('seasons', Counter(o['z'] for o in prods))
    print('no li/si', sum('li' not in o for o in prods), 'no size', sum(not o['w'] for o in prods))
    print('posts', len(posts), 'brand logos', len(logos), 'matched', sum(bool(lg['brand']) for lg in logos))
    print('bytes', (OUT / 'products.json').stat().st_size)


if __name__ == '__main__':
    main()
