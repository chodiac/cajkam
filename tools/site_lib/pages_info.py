"""Service, hotel, brands, blog, about, contact and policy pages."""
import re

from .base import (R, BIZ, BRANDS, POSTS, PAGES, POLICY, SERVICES, SERVICE_PRICES, UPLOADS, CAT_COUNT,
                   esc, fmt, n, icon, km, page, page_head, crumbs, media_slot, post_card, relink, date_sr, todo)
from .pages_home import hotel_stack


def slug(g):
    return re.sub(r'[^a-z]+', '-', g.lower().replace('ž', 'z').replace('š', 's').replace('č', 'c').replace('ć', 'c')).strip('-')


def service_page():
    tables = ''.join(f'''<section class="pricelist" id="{slug(g)}" data-reveal><h3 class="d4">{g}</h3>
<table><thead><tr><th scope="col">Usluga</th><th scope="col">Cena</th></tr></thead><tbody>
{''.join(f'<tr><td>{a}</td><td>{fmt(b) if not isinstance(b, str) else b}</td></tr>' for a, b in rows)}
</tbody></table></section>''' for g, rows in SERVICE_PRICES)
    items = ''.join(f'''<article class="svcrow" data-reveal>
 <div class="svcrow__media">{media_slot(ph, "4/3", "slot--dark", ico)}</div>
 <div class="svcrow__copy"><p class="svcrow__no">0{i + 1}</p><h2 class="d3">{t}</h2><p>{d}</p><p class="svcrow__price">{pr}</p></div>
</article>''' for i, (k, t, pr, d, ph, ico) in enumerate(SERVICES))
    hours = ''.join(f'<li><span>{d}</span><b>{h}</b></li>' for d, h in BIZ['service_hours'])
    body = f'''{page_head('Guma Servis', 'Vulkanizerske usluge u Čačku — savremena oprema, širok asortiman i zaposleni kojima je zadovoljstvo klijenata na prvom mestu.', label='Servis', dark=True)}
<section class="sec sec--tight"><div class="wrap svcpage">
 <div class="svcpage__main">
  <div class="svcrows">{items}</div>
  <div class="sec__head">{km(2, 'Cenovnik')}<h2 class="d2" id="cenovnik">Cenovnik usluga</h2></div>
  <nav class="jump" aria-label="Grupe usluga">{''.join(f'<a href="#{slug(g)}">{g}</a>' for g, _ in SERVICE_PRICES)}</nav>
  <div class="pricelists">{tables}</div>
  <p class="fine">Cene su u dinarima, prema cenovniku objavljenom na cajkam.rs.</p>
 </div>
 <aside class="svcpage__side">
  <div class="box box--ink sticky">
   <p class="label label--light">Guma Servis</p>
   <p class="big">{BIZ['service_address']}<br>{BIZ['service_city']}</p>
   <ul class="hours hours--light">{hours}</ul>
   <a class="btn btn--go btn--block" href="tel:{BIZ['phone_href']}">{icon('phone')}<span>Pozovite — opcija 3</span></a>
   <a class="btn btn--line-light btn--block" href="{BIZ['maps_service']}" rel="noopener">{icon('pin')}<span>Putanja do servisa</span></a>
   <p class="fine">Servis za teretna vozila: {BIZ['address']}, radnim danima 08–16h, subotom 08–14h.</p>
  </div>
 </aside>
</div></section>'''
    return page('servis.html', 'Guma Servis — vulkanizerske usluge i reglaža trapa u Čačku | Čajka M', body, active='servis')


def hotel_page():
    body = f'''{page_head('Hotel za gume', 'Bezbedno čuvanje guma svih vrsta i veličina tokom sezone — u magacinu zaštićenom od ekstremnih temperatura i sunčeve svetlosti.', label='Usluge')}
<section class="sec sec--tight"><div class="wrap hotelpage">
 <div class="hotelpage__copy">
  <div class="hotel__visual hotel__visual--sm" data-stack>{hotel_stack()}</div>
  <dl class="kv kv--big"><div><dt>Cena</dt><dd>{fmt(600)} po komadu</dd></div><div><dt>Period</dt><dd>Jedna sezona</dd></div></dl>
  <h2 class="d3">Kako funkcioniše</h2>
  <ol class="steps">
   <li data-reveal><b>Donesete gume</b><span>Uz zamenu sezone u Guma Servisu radimo montažu i balansiranje.</span></li>
   <li data-reveal><b>Dobijate potvrdu</b><span>Upisujemo proizvođača, dimenziju, DOT, broj komada i registarsku oznaku vozila.</span></li>
   <li data-reveal><b>Najavite preuzimanje</b><span>Najmanje 3 dana unapred. Pri preuzimanju obavezno pokažite potvrdu.</span></li>
  </ol>
  <p class="svc-call"><a class="btn btn--line" href="tel:{BIZ['phone_href']}">{icon('phone')}<span>{BIZ['phone']} · opcija 3</span></a></p>
 </div>
 <form class="box hotel-form" data-demo-form data-success="Zahtev je zabeležen. Za termin pozovite servis ili sačekajte naš poziv.">
  <h2 class="d3">Prijava guma za čuvanje</h2>
  <p class="fine">Popunite podatke — potvrdu dobijate prilikom predaje guma.</p>
  <div class="fields">
   <label class="field field--full"><span>Naziv kompanije</span><input name="firma" autocomplete="organization"></label>
   <label class="field field--full"><span>Ime i prezime <small>(ako je klijent fizičko lice)</small></span><input name="ime" autocomplete="name"></label>
   <label class="field"><span>Telefon *</span><input name="tel" type="tel" required autocomplete="tel"></label>
   <label class="field"><span>Registarska oznaka vozila *</span><input name="reg" required placeholder="ČA 123-AB"></label>
   <label class="field"><span>Proizvođač pneumatika</span><input name="brend"></label>
   <label class="field"><span>Dimenzija pneumatika</span><input name="dim" placeholder="205/55 R16"></label>
   <label class="field"><span>DOT pneumatika</span><input name="dot" placeholder="npr. 2423"></label>
   <label class="field"><span>Broj komada *</span><input name="kom" type="number" min="1" max="12" value="4" required></label>
   <label class="field"><span>Datum predaje na čuvanje</span><input name="datum" type="date"></label>
   <label class="field field--full"><span>Napomene o čuvanju</span><textarea name="nap" rows="3"></textarea></label>
  </div>
  <button class="btn btn--go btn--block" type="submit"><span>Pošalji zahtev</span>{icon('arrow')}</button>
 </form>
</div></section>'''
    return page('hotel-za-gume.html', 'Hotel za gume — čuvanje guma u Čačku | Čajka M', body, active='hotel')


def brands_page():
    counts = dict(BRANDS['counts'])
    logos = {lg['brand'] or lg['name']: lg for lg in BRANDS['logos']}
    names = sorted(set([b for b in counts if b]) | set(logos), key=str.lower)
    tiles = []
    letters = []
    for b in names:
        lg = logos.get(b)
        c = counts.get(b, 0)
        art = (f'<img src="{UPLOADS}{lg["logo"]}" alt="" loading="lazy" decoding="async">' if lg else
               f'<span class="brand__word">{esc(b)}</span>')
        meta = f'{n(c)} guma' if c else 'Na upit'
        href = f'gume.html?brend={b}' if c else 'kontakt.html'
        L = b[0].upper()
        anchor = '' if L in letters else f' id="b-{L}"'
        letters.append(L)
        tiles.append(f'<a class="brand{" brand--ask" if not c else ""}" href="{href}"{anchor} data-reveal>{art}<span class="brand__n"><b>{esc(b)}</b><small>{meta}</small></span></a>')
    az = ''.join(f'<a href="#b-{L}">{L}</a>' for L in dict.fromkeys(letters))
    body = f'''{page_head('Brendovi', 'Sarađujemo sa svetski priznatim proizvođačima. Ovlašćeni smo uvoznik brendova Kama i Voltyre.', label='Proizvođači')}
<section class="sec sec--tight"><div class="wrap">
 <nav class="az" aria-label="Po slovu">{az}</nav>
 <div class="brands-grid">{''.join(tiles)}</div>
 <p class="fine">Brendovi bez guma u online katalogu dostupni su na upit — pozovite {BIZ['phone']}.</p>
</div></section>'''
    return page('brendovi.html', 'Brendovi guma — Čajka M', body, active='brendovi')


def blog_pages():
    body = f'''{page_head('Saveti', 'Izbor, održavanje i čuvanje guma — ukratko i jasno.', label='Blog')}
<section class="sec sec--tight"><div class="wrap"><div class="guides guides--all">{post_card(POSTS[0], big=True)}<div class="blog-grid">{''.join(post_card(p) for p in POSTS[1:])}</div></div></div></section>'''
    page('blog.html', 'Saveti o gumama — blog | Čajka M', body, active='blog')
    for p in POSTS:
        others = [q for q in POSTS if q['slug'] != p['slug']][:3]
        hero = f'<figure class="article__img" data-reveal="wipe"><img src="{p["img"]}" alt="" decoding="async"></figure>' if p['img'] else ''
        cat = {'Uncategorized': 'Saveti'}.get(p['cat'], p['cat'] or 'Saveti')
        body = f'''
<article class="article"><div class="wrap wrap--text">
 {crumbs([('index.html', 'Početna'), ('blog.html', 'Saveti'), (None, esc(p['title']))])}
 <p class="post__meta"><span>{cat}</span><time datetime="{p['date']}">{date_sr(p['date'])}</time><span>{p['min']} min čitanja</span></p>
 <h1 class="article__t" data-split>{esc(p['title'])}</h1>
</div>
<div class="wrap wrap--wide">{hero}</div>
<div class="wrap wrap--text">
 <div class="prose">{relink(p['html'])}</div>
 <aside class="article__cta"><div><p class="label label--light">Znate dimenziju?</p><p class="d3">Pronađite gume za vaše vozilo.</p></div><a class="btn btn--go" href="{R}gume.html"><span>Pretraži gume</span>{icon('arrow')}</a></aside>
</div></article>
<section class="sec sec--paper"><div class="wrap"><div class="sec__head"><h2 class="d2">Pročitajte još</h2><a class="more" href="{R}blog.html">Svi saveti {icon('arrow')}</a></div>
<div class="grid grid--3">{''.join(post_card(q) for q in others)}</div></div></section>'''
        page(f'blog/{p["slug"]}.html', f'{p["title"]} — Čajka M', body, active='blog', desc=p['excerpt'][:155], cls='is-article')


def about_page():
    body = f'''{page_head('O nama', 'Preduzeće „Čajka – M” osnovano je 1992. godine. Osnovna delatnost je uvoz i prodaja pneumatika na domaćem tržištu i u regionu.', label='Čajka M · od 1992.', dark=True)}
<section class="sec sec--tight"><div class="wrap about">
 <div class="about__lead">
  <p class="about__year" aria-hidden="true"><span data-year>1992</span></p>
  <p class="big">Od trenutka osnivanja do danas beležimo stalni rast obima prodaje, obima poslovanja i broja naših kupaca.</p>
 </div>
 <div class="about__cols">
  <section data-reveal>{km(1, 'Tržište')}<h2 class="d3">Pratimo potrebe kupaca</h2><p>Dugi niz godina uspešnog poslovanja u uslovima turbulentnog tržišta naučio nas je da pratimo potrebe naših kupaca i usavršavamo poslovanje kako bismo odgovorili zahtevima tržišta.</p></section>
  <section data-reveal>{km(2, 'Principi')}<h2 class="d3">Osnovni principi poslovanja</h2><ul class="ticks"><li>Uvažavanje i stalno prilagođavanje zahtevima tržišta i kupaca</li><li>Visok kvalitet proizvoda i usluga u svim segmentima</li><li>Partnerski odnosi sa svim učesnicima u razmeni i sa finalnim potrošačima</li></ul></section>
  <section data-reveal>{km(3, 'Sertifikati')}<h2 class="d3">Kvalitet i životna sredina</h2><p>Čajka M je nosilac sertifikata <b>SRPS ISO 9001:2015</b> i <b>SRPS ISO 14001:2015</b>, koji potvrđuju posvećenost kvalitetu i zaštiti životne sredine.</p></section>
 </div>
 {media_slot('Magacin i tim Čajka M, Bulevar oslobodilaca Čačka 84', '21/9', 'slot--wide', 'hotel')}
 <div class="about__offer">
  <div>{km(4, 'Ponuda')}<h2 class="d2">Ovlašćeni uvoznik Kama i Voltyre</h2><p>U ponudi su i Sava, Tigar, Michelin, Goodyear, Dunlop, Nokian i drugi proizvođači — za putnička, poluteretna, teretna, industrijska i poljoprivredna vozila.</p>
  <div class="about__links"><a class="btn btn--ink" href="{R}brendovi.html"><span>Brendovi</span>{icon('arrow')}</a><a class="btn btn--line" href="{BIZ['b2b']}" rel="noopener"><span>B2B portal za partnere</span>{icon('arrow-ne')}</a></div></div>
  <ul class="about__nums">{''.join(f'<li data-reveal><b data-countup>{n(CAT_COUNT[c])}</b><span>{t}</span></li>' for c, t in (('putnicke', 'putničkih'), ('poluteretne', 'poluteretnih'), ('teretne', 'teretnih'), ('poljoprivredne', 'poljoprivrednih')))}</ul>
 </div>
 <blockquote class="about__quote" data-reveal>Svim našim partnerima i budućim kupcima zahvaljujemo na podršci. Nastavićemo da radimo sa istim entuzijazmom i strašću — hvala što ste deo naše priče!</blockquote>
</div></section>'''
    return page('o-nama.html', 'O nama — Čajka M Čačak', body, active='o-nama')


def contact_page():
    emails = ''.join(f'<li><a href="mailto:{e}">{e}</a><small>{l}</small></li>' for e, l in BIZ['emails'])

    def loc(t, a, c, hrs, maps, emb, note=''):
        return f'''<article class="loc" data-reveal>
 <div class="loc__map"><iframe src="{emb}" title="Mapa: {t}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
 <div class="loc__body"><h3 class="d3">{t}</h3><p>{a}<br>{c}</p>
 <ul class="hours">{''.join(f'<li><span>{d}</span><b>{h}</b></li>' for d, h in hrs)}</ul>{note}
 <a class="btn btn--line btn--sm" href="{maps}" rel="noopener">{icon('pin')}<span>Putanja</span></a></div></article>'''
    body = f'''{page_head('Kontakt', 'Pozovite nas, pišite nam ili dođite — kolege iz maloprodaje će vas uslužiti.', label='Kontakt')}
<section class="sec sec--tight"><div class="wrap contact">
 <div class="contact__cards">
  <div class="box box--ink"><p class="label label--light">Telefoni</p>
   <ul class="clist clist--light"><li><a href="tel:{BIZ['phone_href']}">{BIZ['phone']}</a><small>Centrala</small></li><li><a href="tel:{BIZ['sales_href']}">{BIZ['sales']}</a><small>Prodaja</small></li><li><a href="tel:{BIZ['phone_href']}">{BIZ['phone']}</a><small>Servis — opcija 3</small></li></ul></div>
  <div class="box"><p class="label">E-mail</p><ul class="clist">{emails}</ul></div>
  <form class="box contact__form" data-demo-form data-success="Poruka je zabeležena. Odgovaramo radnim danima 08–16h.">
   <h2 class="d3">Pišite nam</h2>
   <div class="fields">
    <label class="field"><span>Ime i prezime *</span><input required autocomplete="name"></label>
    <label class="field"><span>E-mail *</span><input type="email" required autocomplete="email"></label>
    <label class="field field--full"><span>Naslov *</span><input required></label>
    <label class="field field--full"><span>Tekst poruke</span><textarea rows="4"></textarea></label>
   </div>
   <button class="btn btn--go" type="submit"><span>Pošalji poruku</span>{icon('arrow')}</button>
  </form>
 </div>
 <div class="sec__head" id="kako-do-nas">{km(2, 'Lokacije')}<h2 class="d2">Kako do nas</h2></div>
 <div class="locs">
  {loc('Čajka M — prodaja', BIZ['address'] + ',', BIZ['city'], BIZ['hours'], BIZ['maps_hq'], BIZ['embed_hq'], '<p class="fine">Ovde je i servis za teretna vozila.</p>')}
  {loc('Guma Servis', BIZ['service_address'] + ',', BIZ['service_city'], BIZ['service_hours'], BIZ['maps_service'], BIZ['embed_service'])}
 </div>
</div></section>'''
    return page('kontakt.html', 'Kontakt i kako do nas — Čajka M Čačak', body, active='kontakt')


def policy_nav(cur):
    return '<nav class="policy__nav" aria-label="Korisnički servis"><ul>' + ''.join(
        f'<li><a href="{R}{h}"{" aria-current=page" if h == cur else ""}>{l}</a></li>' for h, l in POLICY) + '</ul></nav>'


def faq_page():
    f = PAGES['najcesce-postavljana-pitanja']['html']
    pairs = re.findall(r'([^<>]+\?)\s*((?:<p>.*?</p>\s*)+)', f, re.S)
    items = ''.join(f'<details class="faq"><summary>{esc(re.sub(r" +\?", "?", q.strip()))}{icon("plus")}</summary><div class="prose">{relink(a)}</div></details>'
                    for q, a in pairs)
    body = f'''{page_head('Česta pitanja', 'Poručivanje, isporuka, plaćanje i garancija — ukratko.', label='Korisnički servis')}
<section class="sec sec--tight"><div class="wrap policy">{policy_nav('cesta-pitanja.html')}<div class="faqs">{items}</div></div></section>'''
    return page('cesta-pitanja.html', 'Česta pitanja — Čajka M', body)


def reklamacija_form():
    pos = ''.join(f'<label><input type="radio" name="poz" value="{p}"><span>{p}</span></label>'
                  for p in ('Prednja leva', 'Prednja desna', 'Zadnja leva', 'Zadnja desna'))
    return f'''<form class="box rek-form" id="obrazac" data-demo-form data-success="Zahtev za reklamaciju je zabeležen.">
 <h2 class="d3">Obrazac za reklamaciju</h2>
 <div class="fields">
  <label class="field field--full"><span>Naziv (komercijalni naziv) gume *</span><input required></label>
  <label class="field"><span>Guma je kupljena kod prodavca</span><input></label>
  <label class="field"><span>Dimenzija pneumatika *</span><input required placeholder="205/55 R16"></label>
  <label class="field"><span>Model (sa unutrašnjom / tubeless)</span><input></label>
  <label class="field"><span>Datum proizvodnje</span><input></label>
  <label class="field"><span>Serijski broj</span><input></label>
  <label class="field"><span>Pređena kilometraža (km)</span><input inputmode="numeric"></label>
  <label class="field field--full"><span>Opis nastanka defekta i razlog reklamacije *</span><textarea rows="3" required></textarea></label>
  <label class="field"><span>Pritisak vazduha u eksploataciji</span><input></label>
  <label class="field"><span>Opterećenje pri uočavanju defekta</span><input></label>
  <label class="field"><span>Mašina na kojoj je montiran pneumatik</span><input></label>
  <label class="field"><span>Vozilo (brend/model)</span><input></label>
 </div>
 <fieldset class="field field--full"><legend>Pozicija pneumatika na vozilu</legend><div class="seg seg--wrap">{pos}</div></fieldset>
 <label class="field field--full"><span>Fotografije: oštećenja (3), DOT (1), serijski broj (1), izmerena dubina šare (1)</span><input type="file" accept="image/*" multiple></label>
 <label class="check"><input type="checkbox"><span>Saglasni smo da se koriste destruktivne metode ispitivanja.</span></label>
 <div class="fields">
  <label class="field"><span>Ime i prezime *</span><input required autocomplete="name"></label>
  <label class="field"><span>Datum</span><input type="date"></label>
  <label class="field"><span>E-mail *</span><input type="email" required autocomplete="email"></label>
  <label class="field"><span>Telefon *</span><input type="tel" required autocomplete="tel"></label>
 </div>
 <button class="btn btn--go" type="submit"><span>Pošalji reklamaciju</span>{icon('arrow')}</button>
</form>'''


def policy_page(path, key, title):
    h = relink(PAGES[key]['html'])
    if key == 'reklamacije':
        h = h.split('Naziv (komercijalni naziv)')[0]
        h = re.sub(r'<p>[^<]*$', '', h.strip())
    extra = reklamacija_form() if key == 'reklamacije' else ''
    body = f'''{page_head(title, label='Korisnički servis')}
<section class="sec sec--tight"><div class="wrap policy">{policy_nav(path)}<div><div class="prose">{h}</div>{extra}</div></div></section>'''
    return page(path, f'{title} — Čajka M', body)


def not_found():
    body = f'''<section class="nf"><div class="wrap nf__in">
 <p class="nf__code" aria-hidden="true">404</p>{km(404 % 100, 'Kraj puta')}<h1 class="d2">Ova stranica je sišla sa puta.</h1>
 <p>Adresa ne postoji ili je stranica premeštena.</p>
 <div class="nf__cta"><a class="btn btn--go" href="{R}gume.html"><span>Pretraži gume</span>{icon('arrow')}</a><a class="btn btn--line" href="{R}index.html"><span>Početna</span></a></div>
</div></section>'''
    return page('404.html', 'Stranica nije pronađena — Čajka M', body)


def all_pages():
    out = [service_page(), hotel_page(), brands_page(), about_page(), contact_page(), faq_page(),
           policy_page('reklamacije.html', 'reklamacije', 'Reklamacije'),
           policy_page('uslovi-isporuke.html', 'uslovi-isporuke', 'Uslovi isporuke'),
           policy_page('zastita-potrosaca.html', 'zastita-potrosaca', 'Zaštita potrošača'),
           policy_page('uslovi-koriscenja.html', 'uslovi-koriscenja', 'Uslovi korišćenja i prodaje'),
           policy_page('politika-privatnosti.html', 'politika-privatnosti', 'Politika privatnosti'),
           not_found(), 'blog.html']
    blog_pages()
    return out
