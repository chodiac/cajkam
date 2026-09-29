// Product detail. The shop's API has no descriptions, so the page is built
// from the specification itself: size, indices, season, stock, price.
import { $, $$, esc, num, gume, rsd, icon, img, url, cardHTML, loadProducts, cart, compare, onSale, pct, toast, SEASON, CATS, reveal } from './core.js';

// Standard ETRTO tables (general reference, not shop data).
const LOAD = { 70: 335, 71: 345, 72: 355, 73: 365, 74: 375, 75: 387, 76: 400, 77: 412, 78: 425, 79: 437, 80: 450, 81: 462, 82: 475, 83: 487, 84: 500, 85: 515, 86: 530, 87: 545, 88: 560, 89: 580, 90: 600, 91: 615, 92: 630, 93: 650, 94: 670, 95: 690, 96: 710, 97: 730, 98: 750, 99: 775, 100: 800, 101: 825, 102: 850, 103: 875, 104: 900, 105: 925, 106: 950, 107: 975, 108: 1000, 109: 1030, 110: 1060, 111: 1090, 112: 1120, 113: 1150, 114: 1180, 115: 1215, 116: 1250, 117: 1285, 118: 1320, 119: 1360, 120: 1400, 121: 1450, 122: 1500, 123: 1550, 124: 1600, 125: 1650, 126: 1700, 127: 1750, 128: 1800, 129: 1850, 130: 1900, 131: 1950, 132: 2000, 133: 2060, 134: 2120, 135: 2180, 136: 2240, 137: 2300, 138: 2360, 139: 2430, 140: 2500, 141: 2575, 142: 2650, 143: 2725, 144: 2800, 145: 2900, 146: 3000, 147: 3075, 148: 3150, 149: 3250, 150: 3350, 151: 3450, 152: 3550, 153: 3650, 154: 3750, 155: 3875, 156: 4000, 157: 4125, 158: 4250, 159: 4375, 160: 4500 };
const SPEED = { J: 100, K: 110, L: 120, M: 130, N: 140, P: 150, Q: 160, R: 170, S: 180, T: 190, U: 200, H: 210, V: 240, W: 270, Y: 300 };
const OUT_OF_STOCK = 'Proizvod trenutno nije na zalihama. Molimo vas da nas pozovete za više informacija na broj: 032/546-10-11';

const pdp = $('[data-pdp]');
const slug = new URLSearchParams(location.search).get('p');

(async () => {
  const { list, bySlug, byId } = await loadProducts();
  window.__products = byId;
  const p = bySlug.get(slug);
  if (!p) return missing();
  render(p, list);
  reveal();
})();

function missing() {
  $('.pdp__grid', pdp).innerHTML = `<div class="empty"><p class="sz">?</p><h1 class="d3">Ova guma više nije u ponudi</h1><p>Moguće je da je model povučen ili da je link zastareo.</p><a class="btn btn--go" href="${url('gume.html')}">Pretraži gume</a></div>`;
  $('.pdp__lower', pdp).hidden = true;
  $$('.pdp__rel', pdp).forEach((s) => { s.hidden = true; });
}

function render(p, list) {
  const title = `${p.sz} ${p.b} ${p.m}`.trim();
  document.title = `${title} — Čajka M`;
  $('meta[name="description"]').content = `${title}${p.z ? `, ${SEASON[p.z].toLowerCase()} guma` : ''}. ${p.np ? 'Cena na upit' : `${rsd(p.p)} sa PDV-om`}. ${p.st ? 'Na stanju.' : ''}`;
  $('[data-crumbs]', pdp).insertAdjacentHTML('beforeend',
    `<li><a href="${url(`gume.html?tip=${p.c}`)}">${CATS[p.c]}</a></li><li aria-current="page">${esc(p.sz)}</li>`);

  const im = $('[data-pdp-img]', pdp);
  im.src = img(p, true); im.alt = title;
  im.onerror = () => { im.onerror = null; im.src = img(p); };
  const th = $('[data-pdp-thumb]', pdp); th.src = img(p);
  $('[data-pdp-thumbcode]', pdp).textContent = p.sz ? p.sz.split(' ')[0] : '—';
  $('[data-pdp-art]', pdp).innerHTML = sidewall(p);
  gallery();
  if (onSale(p)) { const s = $('[data-pdp-sale]', pdp); s.textContent = `−${pct(p)} %`; s.hidden = false; }

  $('[data-pdp-brand]', pdp).innerHTML = `${esc(p.b)}${p.z ? `<span class="season" data-s="${p.z}"><i></i>${SEASON[p.z]}</span>` : ''}`;
  $('[data-pdp-size]', pdp).textContent = p.sz || p.n;
  $('[data-pdp-model]', pdp).textContent = p.m || p.n;

  const tags = [];
  if (p.z) tags.push(`<li data-s="${p.z}"><i></i>${SEASON[p.z]}</li>`);
  tags.push(`<li>${CATS[p.c]}</li>`);
  if (p.li) tags.push(`<li>${p.li}${p.si} · ${LOAD[+p.li.split('/')[0]] ? `do ${num(LOAD[+p.li.split('/')[0]])} kg` : ''}${SPEED[p.si] ? `, ${SPEED[p.si]} km/h` : ''}</li>`);
  (p.f || []).forEach((f) => tags.push(`<li>${{ XL: 'Ojačana (XL)', RunFlat: 'Run Flat', FR: 'Zaštita felne (FR)', 'M+S': 'M+S' }[f] || f}</li>`));
  if (p.pos) tags.push(`<li>${esc(p.pos)}</li>`);
  $('[data-pdp-tags]', pdp).innerHTML = tags.join('');

  // price + stock
  const priceBox = $('[data-pdp-price]', pdp);
  priceBox.innerHTML = p.np ? '<p class="price price--ask">Cena na upit</p>'
    : `<p class="price">${onSale(p) ? `<s>${rsd(p.r)}</s>` : ''}<b>${rsd(p.p)}</b><small>po komadu, sa PDV-om</small></p>${onSale(p) ? `<span class="save">Ušteda ${rsd(p.r - p.p)} po gumi</span>` : ''}`;
  const stock = $('[data-pdp-stock]', pdp);
  stock.className = `stock ${p.st ? 'stock--ok' : 'stock--no'}`;
  stock.innerHTML = p.st ? '<i></i>Na stanju — isporuka 1–3 radna dana' : `<i></i>${OUT_OF_STOCK}`;

  // quantity
  const qIn = $('[data-q-input]', pdp);
  const total = $('[data-pdp-total]', pdp);
  const setQ = (q) => {
    q = Math.max(1, Math.min(99, q | 0 || 1));
    qIn.value = q;
    $$('[data-qp]', pdp).forEach((b) => b.setAttribute('aria-pressed', +b.dataset.qp === q));
    total.innerHTML = p.np ? '' : `${q} × ${rsd(p.p)} = <b>${rsd(q * p.p)}</b>`;
    total.classList.remove('is-tick'); void total.offsetWidth; total.classList.add('is-tick');
  };
  $$('[data-q]', pdp).forEach((b) => b.addEventListener('click', () => setQ(+qIn.value + +b.dataset.q)));
  $$('[data-qp]', pdp).forEach((b) => b.addEventListener('click', () => setQ(+b.dataset.qp)));
  qIn.addEventListener('change', () => setQ(+qIn.value));
  setQ(p.c === 'putnicke' || p.c === 'poluteretne' ? 4 : 1);

  const add = $('[data-pdp-add]', pdp);
  const canBuy = p.st && !p.np;
  add.disabled = !canBuy;
  if (!canBuy) { add.innerHTML = `${icon('phone')}Pozovite za dostupnost`; add.disabled = false; add.onclick = () => { location.href = 'tel:+381325461011'; }; $('.qty-row', pdp).hidden = true; }
  else add.addEventListener('click', () => { cart.add(p, +qIn.value); toast(`${qIn.value} × ${p.sz} u korpi.`, 'Otvori korpu', 'korpa.html'); });
  const cmpBtn = $('[data-pdp-compare]', pdp);
  const paintCmp = () => cmpBtn.setAttribute('aria-pressed', compare.has(p.id));
  cmpBtn.addEventListener('click', () => { compare.toggle(p); paintCmp(); if (compare.has(p.id)) toast('Dodata u poređenje.', 'Uporedi', 'uporedi.html'); });
  paintCmp();

  // specs
  const li1 = p.li ? +p.li.split('/')[0] : 0;
  const rows = [
    ['Proizvođač', esc(p.b)], ['Model', esc(p.m)], ['Dimenzija', `<span class="sz">${esc(p.sz)}</span>`],
    ['Širina', p.w && `${p.w}${/^\d{3}$/.test(p.w) ? ' mm' : ''}`], ['Visina (profil)', p.h && `${p.h}${/^\d{2}$/.test(p.h) ? ' %' : ''}`], ['Prečnik felne', p.d && `${p.d}"`],
    ['Sezona', p.z && SEASON[p.z]], ['Tip gume', CATS[p.c]],
    ['Indeks nosivosti', p.li && `${p.li}${LOAD[li1] ? ` — do ${num(LOAD[li1])} kg po gumi` : ''}`],
    ['Indeks brzine', p.si && `${p.si}${SPEED[p.si] ? ` — do ${SPEED[p.si]} km/h` : ''}`],
    ['Pozicija', p.pos && esc(p.pos)], ['Karakteristike', (p.f || []).join(', ')],
    ['Zemlja porekla', `<span class="todo">${icon('info')}Podatak za dopunu</span>`],
    ['Šifra', String(p.id)],
  ].filter(([, v]) => v);
  $('[data-pdp-specs]', pdp).innerHTML = rows.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('');
  $('[data-pdp-specnote]', pdp).textContent = `Indeksi nosivosti i brzine preuzeti su iz naziva proizvoda${p.ci ? '; tip gume određen je prema dimenziji' : ''}. Kilogrami i km/h su standardne vrednosti za dati indeks.`;

  // "how to read"
  const parts = [[p.w, 'Širina', /^\d{3}$/.test(p.w) ? 'mm' : ''], [p.h, 'Visina', /^\d{2}$/.test(p.h) ? '% širine' : ''], [p.d && `R${p.d}`, 'Prečnik', 'cola'],
    [p.li, 'Nosivost', LOAD[li1] ? `${num(LOAD[li1])} kg` : ''], [p.si, 'Brzina', SPEED[p.si] ? `${SPEED[p.si]} km/h` : '']].filter(([v]) => v);
  $('[data-pdp-code]', pdp).innerHTML = parts.map(([v, k, u]) => `<div><b>${esc(v)}</b><span>${k}${u ? `<br>${u}` : ''}</span></div>`).join('');

  // same size, other brands: the real decision aid
  const same = list.filter((x) => x.id !== p.id && x.w === p.w && x.h === p.h && x.d === p.d && x.c === p.c)
    .sort((a, b) => b.st - a.st || (a.z === p.z ? -1 : 0) - (b.z === p.z ? -1 : 0) || a.p - b.p);
  const sameBox = $('[data-same]', pdp);
  if (same.length) {
    sameBox.innerHTML = same.slice(0, 12).map(cardHTML).join('');
    $('[data-same-title]', pdp).innerHTML = `Još ${num(same.length)} ${gume(same.length)} u dimenziji <span class="sz">${esc(p.sz)}</span>`;
    $('[data-same-link]', pdp).href = url(`gume.html?sirina=${p.w}${p.h ? `&visina=${p.h}` : ''}&precnik=${p.d}&tip=${p.c}`);
  } else sameBox.closest('.pdp__rel').hidden = true;

  // same model, other sizes
  const model = list.filter((x) => x.id !== p.id && x.b === p.b && x.m === p.m && x.m).sort((a, b) => parseFloat(a.d) - parseFloat(b.d) || parseFloat(a.w) - parseFloat(b.w));
  if (model.length) {
    $('[data-model-sec]', pdp).hidden = false;
    $('[data-model]', pdp).innerHTML = model.slice(0, 24).map((x) => `<a href="${url(`guma.html?p=${encodeURIComponent(x.s)}`)}"><span class="sz">${esc(x.sz)}</span><small>${x.np ? 'Cena na upit' : rsd(x.p)} · ${x.st ? 'na stanju' : 'nije na stanju'}</small></a>`).join('');
  }

  // sticky buy bar on phones once the main button scrolls away
  const bar = $('[data-buybar]', pdp);
  if (canBuy) {
    $('[data-bb-size]', pdp).textContent = p.sz;
    $('[data-bb-price]', pdp).textContent = rsd(p.p);
    $('[data-bb-add]', pdp).addEventListener('click', () => add.click());
    const mq = matchMedia('(max-width: 767px)');
    new IntersectionObserver(([e]) => { bar.hidden = !mq.matches || e.isIntersecting || e.boundingClientRect.top > 0; }).observe(add);
  }
}

// Two views: the photo (with a pointer-following zoom) and an illustration of
// where the size code sits on the sidewall.
function gallery() {
  const stage = $('[data-stage]', pdp);
  const views = $$('[data-view-i]', stage);
  const thumbs = $$('[data-thumb]', pdp);
  thumbs.forEach((t) => t.addEventListener('click', () => {
    thumbs.forEach((x) => x.setAttribute('aria-selected', x === t));
    views.forEach((v) => v.classList.toggle('is-on', v.dataset.viewI === t.dataset.thumb));
    stage.classList.toggle('is-art', t.dataset.thumb === '1');
  }));
  const z = $('[data-zoom]', stage);
  const im = $('img', z);
  const move = (e) => {
    const r = z.getBoundingClientRect();
    im.style.transformOrigin = `${((e.clientX - r.left) / r.width) * 100}% ${((e.clientY - r.top) / r.height) * 100}%`;
  };
  if (matchMedia('(hover: hover)').matches) {
    z.addEventListener('mouseenter', (e) => { move(e); z.classList.add('is-zoom'); });
    z.addEventListener('mousemove', move);
    z.addEventListener('mouseleave', () => z.classList.remove('is-zoom'));
  } else {
    z.addEventListener('click', (e) => { move(e); z.classList.toggle('is-zoom'); });
  }
}

function sidewall(p) {
  const code = `${p.sz || p.n}${p.li ? ` ${p.li}${p.si}` : ''}`;
  return `<svg class="sidewall" viewBox="-300 -300 600 600" role="img" aria-label="Oznaka ${esc(code)} na bočnici gume">
  <defs><path id="swarc" d="M-222 0 A222 222 0 1 1 222 0"/></defs>
  <circle r="290" class="sw-rubber"/><circle r="286" fill="none" stroke="#2A3035" stroke-width="2"/>
  <circle r="252" fill="none" stroke="#2A3035" stroke-width="1.5"/>
  <circle r="185" class="sw-rim"/><circle r="165" class="sw-rim2"/><circle r="150" fill="#2A3035"/>
  ${[0, 72, 144, 216, 288].map((a) => `<path transform="rotate(${a})" d="M-14 -40 L-9 -150 L9 -150 L14 -40Z" fill="#C9CFD2"/>`).join('')}
  <circle r="40" class="sw-rim"/>
  <text text-anchor="middle"><textPath href="#swarc" startOffset="50%">${esc(code)}</textPath></text>
  <path d="M-150 -262 A300 300 0 0 1 150 -262" fill="none" stroke="#F2B51C" stroke-width="4" stroke-dasharray="10 8" transform="scale(.95)"/>
</svg>`;
}
