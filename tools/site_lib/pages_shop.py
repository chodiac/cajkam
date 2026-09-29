"""Catalogue, product, cart, checkout, compare and account pages."""
from .base import (R, BIZ, ON_SALE, MAX_DISCOUNT, TIRES, n, fmt, icon, page, page_head, crumbs, explainer, todo, km, rail)


def catalog(path, title, preset='', lede='', active='gume', label='Katalog', no=1):
    body = f'''{page_head(title, lede, label=label, no=no)}
<section class="catp" data-catalog data-preset="{preset}">
 <div class="wrap">
  <form class="sizebar" data-sizebar aria-label="Dimenzija i sezona" onsubmit="return false">
   <p class="sizebar__l">Dimenzija</p>
   <div class="sizebar__fields">
    <label class="bigsel"><span class="sr">Širina</span><select data-f="sirina"><option value="">Širina</option></select><small>širina</small></label>
    <span class="bigsel__sep" aria-hidden="true">/</span>
    <label class="bigsel"><span class="sr">Visina</span><select data-f="visina"><option value="">Visina</option></select><small>visina</small></label>
    <span class="bigsel__sep" aria-hidden="true">R</span>
    <label class="bigsel"><span class="sr">Prečnik</span><select data-f="precnik"><option value="">Prečnik</option></select><small>prečnik</small></label>
   </div>
   <div class="sizebar__seasons seg seg--dark" role="group" aria-label="Sezona" data-seasonbar></div>
   <button type="button" class="linkbtn linkbtn--light" data-explain>{icon('info')}Gde piše dimenzija?</button>
  </form>
  <div class="catp__layout">
   <aside class="filters" id="filters" data-filters aria-label="Filteri">
    <div class="filters__head"><h2>Filteri</h2><button class="icon-btn" data-filters-close aria-label="Zatvori filtere">{icon('close')}</button></div>
    <div class="filters__body" data-facets><p class="skeleton">Učitavanje filtera…</p></div>
    <div class="filters__foot"><button class="btn btn--line" type="button" data-clear><span>Obriši sve</span></button><button class="btn btn--go" type="button" data-filters-apply>Prikaži rezultate</button></div>
   </aside>
   <div class="results">
    <div class="toolbar">
     <button class="btn btn--ink btn--sm toolbar__filters" data-filters-open aria-controls="filters">{icon('filter')}<span>Filteri</span> <b data-active-count></b></button>
     <p class="toolbar__count" aria-live="polite" data-count>Učitavanje…</p>
     <label class="toolbar__sort"><span>Sortiraj</span><select data-sort>
      <option value="rec">Preporučeno</option><option value="price-asc">Cena: od najniže</option>
      <option value="price-desc">Cena: od najviše</option><option value="new">Najnovije</option>
      <option value="brand">Proizvođač A–Ž</option><option value="size">Dimenzija</option></select></label>
     <div class="toolbar__view" role="group" aria-label="Prikaz">
      <button class="icon-btn" data-view="grid" aria-pressed="true" aria-label="Mreža">{icon('grid')}</button>
      <button class="icon-btn" data-view="list" aria-pressed="false" aria-label="Lista">{icon('list')}</button>
     </div>
    </div>
    <div class="chips" data-chips></div>
    <div class="grid grid--3 results__grid" data-grid aria-busy="true"></div>
    <div class="results__more"><button class="btn btn--line" data-more hidden></button><p class="fine" data-shown></p></div>
   </div>
  </div>
 </div>
 <a class="cmpbar" href="uporedi.html" data-cmpbar hidden>{icon('compare')}<span data-cmpbar-t></span><b>Uporedi {icon('arrow')}</b></a>
</section>
{explainer()}'''
    return page(path, f'{title} — Čajka M', body, active=active, scripts=('catalog',), cls='is-shop')


def product_page():
    body = f'''
<section class="pdp" data-pdp><div class="wrap">
 <nav class="crumbs" aria-label="Putanja"><ol data-crumbs><li><a href="index.html">Početna</a></li><li><a href="gume.html">Gume</a></li></ol></nav>
 <div class="pdp__grid">
  <div class="pdp__gallery">
   <div class="pdp__stage" data-stage>
    <figure class="pdp__view is-on" data-view-i="0"><div class="pdp__zoom" data-zoom><img data-pdp-img alt="" width="600" height="600"></div></figure>
    <figure class="pdp__view" data-view-i="1"><div class="pdp__code-art" data-pdp-art></div><figcaption class="fine">Ilustracija: gde se oznaka nalazi na bočnici.</figcaption></figure>
    <span class="card__sale" data-pdp-sale hidden></span>
    <span class="pdp__zhint" aria-hidden="true">{icon('search')}Pređite mišem preko slike za uveličanje</span>
   </div>
   <div class="pdp__thumbs" role="tablist" aria-label="Prikaz">
    <button role="tab" aria-selected="true" data-thumb="0"><img data-pdp-thumb alt=""><span>Fotografija</span></button>
    <button role="tab" aria-selected="false" data-thumb="1"><span class="pdp__thumb-code" data-pdp-thumbcode></span><span>Oznaka na bočnici</span></button>
   </div>
   <p class="fine">Fotografija je ilustrativna; izgled šare odgovara modelu, ne nužno i dimenziji.</p>
  </div>
  <div class="pdp__info">
   <p class="pdp__brand" data-pdp-brand></p>
   <h1 class="pdp__t"><span class="sz sz--xl" data-pdp-size></span><span class="pdp__model" data-pdp-model></span></h1>
   <ul class="pdp__tags" data-pdp-tags></ul>
   <div class="pdp__buy">
    <div class="pdp__price" data-pdp-price></div>
    <p class="stock" data-pdp-stock></p>
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
   <ul class="pdp__assure">
    <li>{icon('shield')}<span>Garancija 24 meseca</span></li><li>{icon('truck')}<span>Dostava 1–3 radna dana</span></li>
    <li>{icon('cash')}<span>Plaćanje pouzećem</span></li><li>{icon('wrench')}<span><a href="servis.html">Montaža od {fmt(400)}</a>, plaća se posebno</span></li>
   </ul>
  </div>
 </div>

 <div class="pdp__lower">
  <section class="pdp__specs" aria-labelledby="specs-t">
   {km(1, 'Specifikacija')}
   <h2 id="specs-t" class="d3">Tehnički podaci</h2>
   <dl class="specs" data-pdp-specs></dl>
   <p class="fine" data-pdp-specnote></p>
  </section>
  <section class="pdp__read" aria-labelledby="read-t">
   {km(2, 'Oznaka')}
   <h2 id="read-t" class="d3">Kako čitati ovu oznaku</h2>
   <div class="pdp__code" data-pdp-code></div>
   <p class="fine">Proverite da se oznaka poklapa sa bočnicom gume na vašem vozilu ili sa saobraćajnom dozvolom.</p>
  </section>
 </div>

 <section class="pdp__rel" aria-labelledby="same-t">
  <div class="sec__head">{km(3, 'Ista dimenzija')}<h2 id="same-t" class="d2" data-same-title>Druge gume iste dimenzije</h2><a class="more" data-same-link href="gume.html">Sve u ovoj dimenziji {icon('arrow')}</a></div>
  {rail('', 'Gume iste dimenzije').replace('class="rail__track"', 'class="rail__track" data-same')}
 </section>
 <section class="pdp__rel" aria-labelledby="model-t" data-model-sec hidden>
  <div class="sec__head">{km(4, 'Isti model')}<h2 id="model-t" class="d2">Druge dimenzije ovog modela</h2></div>
  <div class="sizes-list" data-model></div>
 </section>
</div>
<div class="buybar" data-buybar hidden><div class="wrap buybar__in"><div><b class="sz" data-bb-size></b><span data-bb-price></span></div><button class="btn btn--go" data-bb-add>{icon('cart')}<span>U korpu</span></button></div></div>
</section>'''
    return page('guma.html', 'Guma — Čajka M', body, active='gume', scripts=('product',), cls='is-shop')


ASSURE = f'''<ul class="assure"><li>{icon('shield')}Garancija 24 meseca</li><li>{icon('truck')}Dostava 1–3 radna dana</li><li>{icon('cash')}Plaćanje pouzećem</li></ul>'''


def cart_page():
    body = f'''{page_head('Korpa', label='Kupovina')}
<section class="sec sec--tight"><div class="wrap cart-layout" data-cartpage>
 <div class="cart-lines" data-lines><p class="skeleton">Učitavanje korpe…</p></div>
 <aside class="summary" aria-labelledby="sum-t">
  <h2 id="sum-t" class="d3">Pregled</h2>
  <div class="sumrow"><span>Gume</span><b data-sum-items>0 RSD</b></div>
  <div class="sumrow"><span>Dostava</span><span>Obračunava se pri poručivanju</span></div>
  <div class="sumrow sumrow--total"><span>Ukupno sa PDV-om</span><b data-sum-total>0 RSD</b></div>
  <p class="fine">PDV je uračunat u cenu. Cena ne uključuje montažu — <a href="servis.html">cenovnik servisa</a>.</p>
  <a class="btn btn--go btn--block btn--lg" href="kasa.html" data-checkout><span>Nastavi na poručivanje</span>{icon('arrow')}</a>
  {ASSURE}
 </aside>
</div></section>'''
    return page('korpa.html', 'Korpa — Čajka M', body, scripts=('cart',), cls='is-shop')


def checkout_page():
    body = f'''{page_head('Poručivanje', 'Registracija nije neophodna. Potvrdu porudžbine šaljemo na vaš e-mail.', label='Kupovina', trail=[('korpa.html', 'Korpa')])}
<section class="sec sec--tight"><div class="wrap cart-layout">
 <form class="checkout" data-checkout-form novalidate>
  <ol class="steps-line" aria-hidden="true"><li class="is-on">Kupac</li><li>Dostava</li><li>Plaćanje</li></ol>
  <fieldset class="box"><legend class="d4">1. Kupujete kao</legend>
   <div class="seg seg--wide">
    <label><input type="radio" name="kupac" value="fizicko" checked><span>Fizičko lice</span></label>
    <label><input type="radio" name="kupac" value="pravno"><span>Pravno lice</span></label>
   </div>
   <div class="fields" data-company hidden>
    <label class="field field--full"><span>Naziv pravnog lica *</span><input name="firma" autocomplete="organization"></label>
    <label class="field"><span>PIB *</span><input name="pib" inputmode="numeric" pattern="[0-9]{{9}}" maxlength="9"></label>
    <label class="field"><span>Matični broj *</span><input name="mb" inputmode="numeric" pattern="[0-9]{{8}}" maxlength="8"></label>
   </div>
  </fieldset>
  <fieldset class="box"><legend class="d4">2. Podaci za dostavu</legend>
   <div class="fields">
    <label class="field"><span>Ime *</span><input name="ime" required autocomplete="given-name"></label>
    <label class="field"><span>Prezime *</span><input name="prezime" required autocomplete="family-name"></label>
    <label class="field"><span>Telefon *</span><input name="tel" type="tel" required autocomplete="tel" placeholder="06x xxx xxxx"></label>
    <label class="field"><span>E-mail *</span><input name="email" type="email" required autocomplete="email"></label>
    <label class="field field--full"><span>Ulica i broj *</span><input name="adresa" required autocomplete="street-address"></label>
    <label class="field"><span>Mesto *</span><input name="mesto" required autocomplete="address-level2"></label>
    <label class="field"><span>Poštanski broj *</span><input name="pb" required inputmode="numeric" autocomplete="postal-code"></label>
    <label class="field field--full"><span>Napomena</span><textarea name="napomena" rows="3" placeholder="Npr. dostava na adresu vulkanizera"></textarea></label>
   </div>
  </fieldset>
  <fieldset class="box"><legend class="d4">3. Plaćanje</legend>
   <label class="opt"><input type="radio" name="placanje" value="pouzecem" checked><span><b>Pouzećem</b><small>Gotovinom kuriru prilikom preuzimanja.</small></span></label>
   <label class="opt"><input type="radio" name="placanje" value="predracun"><span><b>Uplata po predračunu</b><small>Predračun šaljemo e-mailom; gume rezervišemo 24 časa. Kod avansnog plaćanja dostava je 0 dinara.</small></span></label>
  </fieldset>
  <label class="check"><input type="checkbox" required name="uslovi"><span>Pročitao/la sam i prihvatam <a href="uslovi-koriscenja.html">Uslove korišćenja i prodaje</a>. *</span></label>
  <p class="form-err" data-err hidden></p>
  <button class="btn btn--go btn--lg btn--block" type="submit"><span>Potvrdi porudžbinu</span>{icon('arrow')}</button>
  <p class="fine">Naloge za isporuku pouzećem dajemo do 12 časova. Isporuke se ne vrše vikendom i državnim praznicima.</p>
  <p class="todo-note">{todo('Nije povezano')} Porudžbina se još ne šalje u WooCommerce prodavnicu — ovaj korak čeka povezivanje sa postojećim backendom.</p>
 </form>
 <aside class="summary" aria-labelledby="sum-t"><h2 id="sum-t" class="d3">Vaša porudžbina</h2><div data-mini-lines></div>
  <div class="sumrow"><span>Dostava</span><span>{todo('Tarifa kurirske službe')}</span></div>
  <div class="sumrow sumrow--total"><span>Ukupno sa PDV-om</span><b data-sum-total>0 RSD</b></div>{ASSURE}</aside>
</div>
<div class="wrap done" data-done hidden>
 <div class="done__mark">{icon('check')}</div>
 <h2 class="d2">Porudžbina je zabeležena</h2>
 <p>Potvrda bi stigla na <b data-done-email></b>. Ako neka guma nije raspoloživa kod dobavljača, prodaja vas poziva da dogovorite rok ili zamenu.</p>
 <p class="todo-note">{todo('Prototip')} Ovaj sajt još nije povezan sa WooCommerce prodavnicom — porudžbina nije poslata i korpa nije naplaćena.</p>
 <a class="btn btn--ink" href="gume.html"><span>Nazad na gume</span></a>
</div></section>'''
    return page('kasa.html', 'Poručivanje — Čajka M', body, scripts=('checkout',), cls='is-shop')


def compare_page():
    body = f'''{page_head('Uporedite gume', 'Dodajte do 4 gume iz kataloga i uporedite ih jednu pored druge.', label='Poređenje')}
<section class="sec sec--tight"><div class="wrap" data-comparepage>
 <label class="check check--inline"><input type="checkbox" data-diff><span>Prikaži samo razlike</span></label>
 <div class="cmp" data-cmp><p class="skeleton">Učitavanje…</p></div>
</div></section>'''
    return page('uporedi.html', 'Uporedite gume — Čajka M', body, scripts=('compare',), cls='is-shop')


def account_page():
    body = f'''{page_head('Moj nalog', label='Nalog')}
<section class="sec sec--tight"><div class="wrap acct" data-account>
 <div class="acct__forms" data-acct-guest>
  <div class="tabs" role="tablist">
   <button role="tab" aria-selected="true" aria-controls="t-login" id="tab-login">Prijava</button>
   <button role="tab" aria-selected="false" aria-controls="t-reg" id="tab-reg">Registracija</button>
  </div>
  <form class="box" id="t-login" role="tabpanel" aria-labelledby="tab-login" data-login>
   <label class="field field--full"><span>Korisničko ime ili e-mail *</span><input required autocomplete="username"></label>
   <label class="field field--full"><span>Lozinka *</span><input type="password" required autocomplete="current-password"></label>
   <label class="check"><input type="checkbox"><span>Zapamti me</span></label>
   <button class="btn btn--ink btn--block" type="submit"><span>Prijavi se</span></button>
   <a class="linkbtn" href="#" data-lost>Zaboravili ste lozinku?</a>
  </form>
  <form class="box" id="t-reg" role="tabpanel" aria-labelledby="tab-reg" hidden data-register>
   <p>Registrujte se i kupujte sa popustom.</p>
   <label class="field field--full"><span>E-mail *</span><input type="email" required autocomplete="email"></label>
   <label class="field field--full"><span>Lozinka *</span><input type="password" required minlength="8" autocomplete="new-password"></label>
   <button class="btn btn--go btn--block" type="submit"><span>Napravi nalog</span></button>
   <p class="fine">{todo('Iznos popusta za registrovane kupce')}</p>
  </form>
  <p class="todo-note">{todo('Nije povezano')} Prijava i registracija rade samo lokalno u ovom pregledaču; povezivanje sa WooCommerce nalozima je sledeći korak.</p>
 </div>
 <aside class="acct__side">
  <div class="box box--paper"><h2 class="d4">Kupovina bez naloga</h2><p>Registracija nije neophodna da biste naručili gume. Nalog čuva adrese i istoriju porudžbina.</p><a class="more" href="gume.html">Nastavi kupovinu {icon('arrow')}</a></div>
  <div class="box box--ink"><h2 class="d4">Partneri i pravna lica</h2><p>Veleprodajne cene i porudžbine za servise i firme idu preko posebnog B2B portala — nije deo ove kupovine.</p><a class="btn btn--go" href="{BIZ['b2b']}" rel="noopener"><span>B2B portal</span>{icon('arrow-ne')}</a></div>
 </aside>
 <div class="acct__dash" data-acct-user hidden>
  <nav class="acct__nav" aria-label="Nalog"><button aria-current="true">Porudžbine</button><button data-logout>Odjava</button></nav>
  <div class="box"><h2 class="d4">Porudžbine</h2><div class="empty"><p>Još nemate porudžbina.</p><a class="btn btn--go" href="gume.html"><span>Pronađite gume</span>{icon('arrow')}</a></div>
   <p class="todo-note">{todo('Prototip')} Nalog radi lokalno u pregledaču; istorija porudžbina dolazi iz WooCommerce-a nakon povezivanja.</p></div>
 </div>
</div></section>'''
    return page('nalog.html', 'Moj nalog — Čajka M', body, scripts=('account',), cls='is-shop')


def all_pages():
    return [catalog('gume.html', 'Gume', lede=f'{n(len(TIRES))} guma za putnička, poluteretna, teretna, industrijska i poljoprivredna vozila.'),
            catalog('akcije.html', 'Akcije', preset='akcija=1', active='akcije', label='Na popustu', no=3,
                    lede=f'{len(ON_SALE)} modela na popustu — sniženja do {MAX_DISCOUNT} %. Cene su po komadu, sa PDV-om.'),
            product_page(), cart_page(), checkout_page(), compare_page(), account_page()]
