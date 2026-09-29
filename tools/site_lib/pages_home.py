"""Homepage."""
from .base import (ROOT, R, BIZ, CATS, SEASONS, RECOMMENDED, SERVICES, TIRES, IN_STOCK, ON_SALE, CAT_COUNT, CAT_STOCK,
                   SEASON_STOCK, BY_SLUG, MAX_DISCOUNT, POPULAR_SIZES, BRANDS, BRAND_COUNT, POSTS, UPLOADS,
                   esc, fmt, n, numkey, icon, vehicle, km, card, rail, media_slot, post_card, explainer, page,
                   size_query, cat_image, img_url, todo)


def hero():
    has_video = (ROOT / 'media' / 'hero.mp4').exists()
    video = ('<video class="hero__video" autoplay muted loop playsinline preload="none" poster="media/hero-poster.jpg" data-hero-video>'
             + ('<source src="media/hero-720.mp4" type="video/mp4" media="(max-width: 767px)">' if (ROOT / 'media' / 'hero-720.mp4').exists() else '')
             + '<source src="media/hero.mp4" type="video/mp4"></video>') if has_video else ''
    widths = sorted({p['w'] for p in TIRES if p['c'] == 'putnicke' and p['h']}, key=numkey)
    wopts = ''.join(f'<option>{w}</option>' for w in widths)
    tips = ''.join(f'<option value="{c}"{" selected" if c == "putnicke" else ""}>{t}</option>' for c, t, _, _ in CATS)
    seasons = ''.join(
        f'<label><input type="radio" name="sezona" value="{s}"><span>{icon({"letnja": "sun", "zimska": "snow", "sve": "drop"}[s])}{t}</span></label>'
        for s, t in SEASONS)
    chips = ''.join(f'<a class="size-chip size-chip--light" href="gume.html?{size_query(s)}">{s}</a>' for s in POPULAR_SIZES[:5])
    return f'''
<section class="hero" data-hero aria-labelledby="hero-t">
 <div class="hero__media" aria-hidden="true">
  <img class="hero__poster" src="media/hero-poster.jpg" alt="" width="1600" height="900" fetchpriority="high" decoding="async">
  <canvas class="hero__film" data-film{' hidden' if has_video else ''}></canvas>
  {video}
  <div class="hero__shade"></div>
 </div>
 <div class="wrap hero__top">
  {km(0, 'Čajka M · Čačak, od 1992.', light=True)}
  <h1 id="hero-t" class="hero__t"><span class="ln"><span>Drži</span></span> <span class="ln"><span>put.</span></span></h1>
  <p class="hero__lede">Gume za automobile, kombije, kamione i radne mašine. {n(len(IN_STOCK))} modela je odmah na stanju — izaberite dimenziju i pogledajte šta imamo.</p>
 </div>
 <div class="hero__cond" aria-hidden="true">
  <span class="hero__cond-i" data-cond-icon>{icon('sun')}</span><span data-cond-label>Suv asfalt</span>
 </div>
 <button class="hero__ctl" type="button" data-film-ctl aria-label="Pauziraj video">{icon('pause')}</button>
 {'' if has_video else f'<p class="hero__tmp">{todo("Privremeni kadar — zameniti snimkom")}</p>'}

 <div class="wrap hero__dock">
  <form class="finder" action="gume.html" data-finder aria-labelledby="finder-t">
   <div class="finder__head">
    <h2 id="finder-t" class="finder__t">Pronađite gume</h2>
    <button type="button" class="linkbtn" data-explain>{icon('info')}Gde piše dimenzija?</button>
   </div>
   <div class="finder__row">
    <label class="ff ff--tip"><span class="ff__l">Vozilo</span>
     <select name="tip" data-f-tip>{tips}</select>{icon('down', 'i ff__caret')}</label>
    <fieldset class="ff ff--season"><legend class="ff__l">Sezona</legend>
     <div class="seg" data-f-season><label><input type="radio" name="sezona" value="" checked><span>Sve</span></label>{seasons}</div>
    </fieldset>
    <div class="ff-size" role="group" aria-label="Dimenzija">
     <label class="ff"><span class="ff__l">Širina</span><select name="sirina" data-dim="w"><option value="">—</option>{wopts}</select></label>
     <span class="ff-size__sep" aria-hidden="true">/</span>
     <label class="ff"><span class="ff__l">Visina</span><select name="visina" data-dim="h"><option value="">—</option></select></label>
     <span class="ff-size__sep" aria-hidden="true">R</span>
     <label class="ff"><span class="ff__l">Prečnik</span><select name="precnik" data-dim="d"><option value="">—</option></select></label>
    </div>
    <button class="btn btn--go btn--lg finder__go" type="submit"><span data-finder-label>Pronađi gume</span>{icon('arrow')}</button>
   </div>
   <div class="finder__foot">
    <p class="finder__pop"><span>Najtraženije:</span>{chips}</p>
    <a class="finder__all" href="gume.html">Pogledaj sve gume ({n(len(TIRES))}) {icon('arrow')}</a>
   </div>
  </form>
 </div>
</section>'''


def categories():
    cards = []
    for i, (c, t, d, v) in enumerate(CATS):
        p = cat_image(c)
        pic = f'<img src="{img_url(p, True)}" alt="" loading="lazy" decoding="async">' if p else ''
        cards.append(f'''<a class="catcard" href="gume.html?tip={c}" data-reveal style="--i:{i}">
 <span class="catcard__tread" style="background-image:url(assets/img/tread-{"zimska" if c in ("teretne", "poljoprivredne") else "letnja"}.svg)" aria-hidden="true"></span>
 <span class="catcard__img">{pic}</span>
 <span class="catcard__veh">{vehicle(v)}</span>
 <span class="catcard__t">{t}</span>
 <span class="catcard__d">{d}</span>
 <span class="catcard__n"><b>{n(CAT_COUNT[c])}</b> guma · {n(CAT_STOCK[c])} na stanju</span>
 <span class="catcard__go" aria-hidden="true">{icon('arrow')}</span>
</a>''')
    return f'''
<section class="sec cats" aria-labelledby="cats-t"><div class="wrap">
 <div class="sec__head">{km(1, 'Kategorije')}<h2 id="cats-t" class="d2" data-split>Za šta tražite gume?</h2>
  <a class="more" href="gume.html">Sve gume {icon('arrow')}</a></div>
 <div class="cats__row">{''.join(cards)}</div>
</div></section>'''


def tread_section():
    copy = {
        'letnja': ('Leto', 'Suv i topao asfalt', 'Letnje gume',
                   'Tvrđa smeša ostaje stabilna na toplom asfaltu, a široki blokovi drže više gume u dodiru sa putem. Uzdužni kanali odvode vodu kad počne kiša.',
                   'sun', 'Iznad 7 °C'),
        'sve': ('Cele godine', 'Kiša i promenljivi uslovi', 'Gume za sve sezone',
                'Usmerena šara u obliku slova V izbacuje vodu ka ivicama. Kompromis za blage zime i gradsku vožnju — jedna garnitura tokom cele godine.',
                'drop', 'Blage zime'),
        'zimska': ('Zima', 'Sneg, bljuzgavica i led', 'Zimske gume',
                   'Mekša smeša ostaje elastična na hladnom, a gusti lamelni urezi hvataju sneg i led. Svaka ivica je još jedna tačka prianjanja.',
                   'snow', 'Ispod 7 °C'),
    }
    order = ['letnja', 'sve', 'zimska']
    steps = ''.join(f'''<article class="tstep" data-tstep="{s}">
 <p class="tstep__k">{icon(copy[s][4])}<span>{copy[s][0]}</span><em>{copy[s][5]}</em></p>
 <h3 class="tstep__t">{copy[s][2]}</h3>
 <p class="tstep__cond">{copy[s][1]}</p>
 <div class="tstep__band" aria-hidden="true" style="background-image:url(assets/img/tread-{s}.svg)"></div>
 <p class="tstep__x">{copy[s][3]}</p>
 <a class="btn btn--line-light" href="gume.html?sezona={s}"><span>{n(SEASON_STOCK[s])} na stanju — pogledaj</span>{icon('arrow')}</a>
</article>''' for s in order)
    layers = ''.join(f'<div class="tv__pat" data-pat="{s}" style="background-image:url(assets/img/tread-{s}.svg)"></div>' for s in order)
    prints = ''.join(f'<div class="tv__print" data-print="{s}" style="background-image:url(assets/img/tread-{s}.svg)"></div>' for s in order)
    return f'''
<section class="tread" data-tread data-cond="letnja" aria-labelledby="tread-t">
 <div class="tread__stage" aria-hidden="true">
  <div class="tv">
   <div class="tv__sky"></div>
   <canvas class="tv__fx" data-tread-fx></canvas>
   <div class="tv__road"><div class="tv__prints">{prints}</div></div>
   <div class="tv__tyre">
    <div class="tv__band">{layers}<div class="tv__shade"></div></div>
    <div class="tv__wall tv__wall--l"></div><div class="tv__wall tv__wall--r"></div>
   </div>
   <div class="tv__contact"></div>
   <div class="tv__hud"><span data-tv-label>Suv asfalt</span><span class="tv__temp" data-tv-temp>Iznad 7 °C</span></div>
  </div>
 </div>
 <div class="wrap tread__copy">
  <div class="tread__intro">
   {km(2, 'Gazeći sloj', light=True)}
   <h2 id="tread-t" class="d2" data-split>Put se menja. Šara odlučuje.</h2>
   <p>Otisak gume je mali kao dlan — i to je sve što vas drži na putu. Skrolujte i pogledajte kako se šara menja sa podlogom.</p>
  </div>
  {steps}
 </div>
</section>'''


def offers():
    sale = sorted(ON_SALE, key=lambda p: (-p['st'], -(1 - p['p'] / p['r'])))[:12]
    rec = [BY_SLUG[s] for s in RECOMMENDED if s in BY_SLUG]
    return f'''
<section class="sec offers" aria-labelledby="sale-t"><div class="wrap">
 <div class="offers__head">
  <div>{km(3, 'Akcije')}<h2 id="sale-t" class="d2" data-split>Na popustu</h2></div>
  <p class="offers__big" data-max="{MAX_DISCOUNT}" aria-label="Sniženja do {MAX_DISCOUNT} procenata"><small>do</small><b>−<span data-countup>{MAX_DISCOUNT}</span></b><small>%</small></p>
  <p class="offers__aside">{len(ON_SALE)} modela sa sniženom cenom. Cene su po komadu, sa PDV-om.<br><a class="more" href="akcije.html">Sve akcije {icon('arrow')}</a></p>
 </div>
 {rail(''.join(card(p) for p in sale), 'Gume na popustu')}
</div></section>

<section class="sec sec--paper" aria-labelledby="rec-t"><div class="wrap">
 <div class="sec__head">{km(4, 'Izdvojeno')}<h2 id="rec-t" class="d2" data-split>Naša preporuka</h2>
  <a class="more" href="gume.html">Pogledajte sve gume {icon('arrow')}</a></div>
 <div class="grid grid--4">{''.join(card(p) for p in rec[:8])}</div>
</div></section>'''


def brands():
    logos = [lg for lg in BRANDS['logos'] if lg['count']] + [lg for lg in BRANDS['logos'] if not lg['count']]
    row = ''.join(f'<a class="brandlogo" href="{"gume.html?brend=" + lg["brand"] if lg["brand"] else "brendovi.html"}">'
                  f'<img src="{UPLOADS}{lg["logo"]}" alt="{esc(lg["name"])}" loading="lazy" decoding="async"></a>'
                  for lg in logos)
    return f'''
<section class="brands" aria-labelledby="brands-t">
 <div class="wrap brands__head">
  {km(5, 'Brendovi')}
  <h2 id="brands-t" class="d2" data-split>{BRAND_COUNT} proizvođača u ponudi</h2>
  <p>Ovlašćeni smo uvoznik brendova <b>Kama</b> i <b>Voltyre</b>. <a class="more" href="brendovi.html">Svi brendovi {icon('arrow')}</a></p>
 </div>
 <div class="belt" data-belt><div class="belt__row">{row}</div><div class="belt__row" aria-hidden="true">{row.replace('<a ', '<a tabindex="-1" ')}</div></div>
</section>'''


def service():
    items = ''.join(f'''<li class="svc__item" data-svc="{k}"{' data-on' if i == 0 else ''}>
 <button type="button" class="svc__btn" aria-expanded="{str(i == 0).lower()}" aria-controls="svc-{k}">
  <span class="svc__no">0{i + 1}</span><span class="svc__name">{t}</span><span class="svc__price">{pr}</span>{icon('plus', 'i svc__plus')}
 </button>
 <div class="svc__body" id="svc-{k}"><p>{d}</p></div>
</li>''' for i, (k, t, pr, d, _, _) in enumerate(SERVICES))
    media = ''.join(f'<div class="svc__media" data-svc-media="{k}"{"" if i == 0 else " hidden"}>{media_slot(ph, "4/5", "slot--dark", ico)}</div>'
                    for i, (k, _, _, _, ph, ico) in enumerate(SERVICES))
    return f'''
<section class="svc" aria-labelledby="svc-t"><div class="svc__panel">
 <div class="wrap svc__grid">
  <div class="svc__copy">
   {km(6, 'Guma Servis', light=True)}
   <h2 id="svc-t" class="d2" data-split>Kupite gume. Mi ih montiramo.</h2>
   <p class="svc__lede">Servis u Ulici {BIZ['service_address']} u Čačku: montaža, balansiranje, reglaža, vulkanizerske usluge i brzi servis.</p>
   <ul class="svc__list" data-svc-list>{items}</ul>
   <div class="svc__cta">
    <a class="btn btn--go" href="servis.html"><span>Ceo cenovnik</span>{icon('arrow')}</a>
    <a class="btn btn--line-light" href="tel:{BIZ['phone_href']}">{icon('phone')}<span>{BIZ['phone']} · opcija 3</span></a>
   </div>
   <p class="svc__hours">{icon('clock')}Radnim danima 08–18h · Subotom 08–16h</p>
  </div>
  <div class="svc__visual">{media}</div>
 </div>
</div></section>'''


def hotel_stack():
    tires = []
    for i in range(4):
        y = 40 + i * 74
        grooves = ''.join(f'<path d="M{x} {y + 6}l8 14-8 14 8 14-8 14"/>' for x in range(52, 330, 26))
        tires.append(f'<g class="st-tyre" style="--i:{3 - i}"><rect x="30" y="{y}" width="320" height="68" rx="26" class="st-body"/>'
                     f'<g class="st-groove">{grooves}</g>'
                     f'<rect x="30" y="{y}" width="320" height="68" rx="26" class="st-edge"/></g>')
    return f'''<svg class="stack" viewBox="0 0 440 380" role="img" aria-label="Četiri složene gume sa hotelskom privezicom">
 <ellipse cx="190" cy="352" rx="190" ry="12" class="st-shadow"/>
 {''.join(tires)}
 <g class="st-tag" transform="translate(330 70) rotate(14)">
  <path d="M0 0h86l18 22-18 22H0z" class="st-tag__card"/>
  <circle cx="84" cy="22" r="5" class="st-tag__hole"/>
  <text x="12" y="19" class="st-tag__k">HOTEL</text><text x="12" y="35" class="st-tag__v">1 SEZONA</text>
 </g>
 <path d="M414 92c14-24 6-44-14-46" class="st-string"/>
</svg>'''


def hotel():
    return f'''
<section class="sec hotel" aria-labelledby="hotel-t"><div class="wrap hotel__grid">
 <div class="hotel__visual" data-stack>{hotel_stack()}</div>
 <div class="hotel__copy">
  {km(7, 'Hotel za gume')}
  <h2 id="hotel-t" class="d2" data-split>Drugi komplet prezimljuje kod nas.</h2>
  <p>Čuvamo gume svih vrsta i veličina u magacinu zaštićenom od ekstremnih temperatura i sunčeve svetlosti. Uz zamenu sezone radimo montažu i balansiranje.</p>
  <dl class="kv">
   <div><dt>Cena</dt><dd><b>{fmt(600)}</b> po komadu, jedna sezona</dd></div>
   <div><dt>Preuzimanje</dt><dd>Najavite 3 dana unapred</dd></div>
   <div><dt>Potvrda</dt><dd>Obavezna pri preuzimanju</dd></div>
  </dl>
  <a class="btn btn--ink" href="hotel-za-gume.html"><span>Prijavite gume za čuvanje</span>{icon('arrow')}</a>
 </div>
</div></section>'''


def story():
    return f'''
<section class="story" aria-labelledby="story-t"><div class="wrap story__grid">
 <div class="story__year" aria-hidden="true"><span data-year>1992</span></div>
 <div class="story__copy">
  {km(8, 'Naša priča')}
  <h2 id="story-t" class="d2" data-split>Uvoznik pneumatika iz Čačka.</h2>
  <p class="big">Preduzeće „Čajka – M” osnovano je 1992. godine. Od tada beležimo stalni rast obima prodaje, poslovanja i broja kupaca — na domaćem tržištu i u regionu.</p>
  <ul class="story__facts">
   <li data-reveal><b>1992.</b><span>godina osnivanja</span></li>
   <li data-reveal><b>ISO 9001</b><span>upravljanje kvalitetom</span></li>
   <li data-reveal><b>ISO 14001</b><span>zaštita životne sredine</span></li>
   <li data-reveal><b>Kama · Voltyre</b><span>ovlašćeni uvoznik</span></li>
  </ul>
  <div class="story__cta"><a class="more" href="o-nama.html">Naša priča {icon('arrow')}</a>
  <a class="more" href="{BIZ['b2b']}" rel="noopener">B2B portal za partnere {icon('arrow-ne')}</a></div>
 </div>
</div></section>'''


def guides():
    p = POSTS[:4]
    return f'''
<section class="sec sec--paper" aria-labelledby="blog-t"><div class="wrap">
 <div class="sec__head">{km(9, 'Saveti')}<h2 id="blog-t" class="d2" data-split>Pre nego što kupite</h2><a class="more" href="blog.html">Svi saveti {icon('arrow')}</a></div>
 <div class="guides">{post_card(p[0], big=True)}<div class="guides__side">{''.join(post_card(x) for x in p[1:4])}</div></div>
</div></section>'''


def visit():
    loc = lambda t, a, c, hrs, maps, note: f'''<article class="visit__loc" data-reveal>
 <h3>{t}</h3><p>{a}<br>{c}</p>
 <ul class="hours">{''.join(f'<li><span>{d}</span><b>{h}</b></li>' for d, h in hrs)}</ul>
 <p class="fine">{note}</p>
 <a class="more" href="{maps}" rel="noopener">Putanja {icon('arrow-ne')}</a></article>'''  # noqa: E731
    return f'''
<section class="visit" aria-labelledby="visit-t"><div class="wrap visit__grid">
 <div class="visit__call">
  {km(10, 'Kontakt')}
  <h2 id="visit-t" class="d2" data-split>Niste sigurni koja guma? Pozovite.</h2>
  <a class="visit__phone" href="tel:{BIZ['phone_href']}">{BIZ['phone']}</a>
  <p>Prodaja: <a href="tel:{BIZ['sales_href']}">{BIZ['sales']}</a> · <a href="mailto:prodaja@cajkam.rs">prodaja@cajkam.rs</a></p>
 </div>
 {loc('Čajka M — prodaja', BIZ['address'], BIZ['city'], BIZ['hours'], BIZ['maps_hq'], 'Ovde je i servis za teretna vozila.')}
 {loc('Guma Servis', BIZ['service_address'], BIZ['service_city'], BIZ['service_hours'], BIZ['maps_service'], 'Montaža, balansiranje, reglaža i hotel za gume.')}
</div></section>'''


def home():
    body = hero() + categories() + tread_section() + offers() + brands() + service() + hotel() + story() + guides() + visit() + explainer()
    return page('index.html', 'Čajka M — Online prodaja guma | Čačak', body, scripts=('home',), cls='home')
