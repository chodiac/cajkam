// Catalogue: every filter lives in the URL, so results are shareable and the
// back button works. Facet counts always reflect the other active filters.
import { $, $$, esc, num, rsd, icon, gume, cardHTML, loadProducts, parseSize, reveal, CATS, SEASONS_PL, onSale, compare, onChange } from './core.js';

const root = $('[data-catalog]');
const grid = $('[data-grid]', root);
const facetsBox = $('[data-facets]', root);
const chipsBox = $('[data-chips]', root);
const countEl = $('[data-count]', root);
const moreBtn = $('[data-more]', root);
const shownEl = $('[data-shown]', root);
const sortSel = $('[data-sort]', root);
const sizeSel = { sirina: $('[data-f="sirina"]', root), visina: $('[data-f="visina"]', root), precnik: $('[data-f="precnik"]', root) };
const seasonBar = $('[data-seasonbar]', root);
const filtersEl = $('[data-filters]', root);
const PAGE = 24;
const preset = new URLSearchParams(root.dataset.preset || '');
const LIST_KEYS = ['tip', 'sezona', 'brend', 'pozicija', 'osobine'];
const SCALAR = ['sirina', 'visina', 'precnik', 'cmin', 'cmax', 'stanje', 'akcija', 'q', 'sort', 'prikaz'];

let ALL = [];
let state = {};
let shown = PAGE;
const numSort = (a, b) => (parseFloat(a) || 9e9) - (parseFloat(b) || 9e9) || String(a).localeCompare(b);

// ------------------------------------------------------------ state <-> URL
function readURL() {
  const u = new URLSearchParams(location.search);
  preset.forEach((v, k) => u.set(k, v));
  const s = {};
  LIST_KEYS.forEach((k) => { s[k] = (u.get(k) || '').split(',').filter(Boolean); });
  SCALAR.forEach((k) => { s[k] = u.get(k) || ''; });
  const sz = parseSize(s.q);
  if (sz) { Object.assign(s, { sirina: sz.w, visina: sz.h, precnik: sz.d }); s.q = ''; }
  return s;
}
function writeURL() {
  const u = new URLSearchParams();
  LIST_KEYS.forEach((k) => { if (state[k].length) u.set(k, state[k].join(',')); });
  SCALAR.forEach((k) => { if (state[k] && !(k === 'sort' && state[k] === 'rec') && !preset.has(k)) u.set(k, state[k]); });
  preset.forEach((_, k) => u.delete(k));
  history.replaceState(null, '', `${location.pathname}${u.size ? `?${u}` : ''}`);
}

// ------------------------------------------------------------ filtering
const TESTS = {
  tip: (p, v) => v.includes(p.c),
  sezona: (p, v) => v.includes(p.z),
  brend: (p, v) => v.includes(p.b),
  pozicija: (p, v) => v.some((x) => (p.pos || '').includes(x)),
  osobine: (p, v) => v.every((x) => (p.f || []).includes(x)),
  sirina: (p, v) => p.w === v,
  visina: (p, v) => p.h === v,
  precnik: (p, v) => p.d === v,
  cmin: (p, v) => !p.np && p.p >= +v,
  cmax: (p, v) => !p.np && p.p <= +v,
  stanje: (p) => p.st === 1,
  akcija: (p) => onSale(p),
  q: (p, v) => v.toLowerCase().split(/\s+/).every((t) => p._h.includes(t)),
};
function active(s, except = []) {
  return Object.keys(TESTS).filter((k) => !except.includes(k) && (Array.isArray(s[k]) ? s[k].length : s[k]));
}
function filter(s, except = []) {
  const keys = active(s, except);
  return ALL.filter((p) => keys.every((k) => TESTS[k](p, s[k])));
}
const SORTS = {
  rec: (a, b) => b.st - a.st || (onSale(b) ? 1 : 0) - (onSale(a) ? 1 : 0) || (a.np || 0) - (b.np || 0) || b.id - a.id,
  'price-asc': (a, b) => (a.np || 0) - (b.np || 0) || a.p - b.p,
  'price-desc': (a, b) => (a.np || 0) - (b.np || 0) || b.p - a.p,
  new: (a, b) => b.id - a.id,
  brand: (a, b) => a.b.localeCompare(b.b) || a.p - b.p,
  size: (a, b) => numSort(a.w, b.w) || numSort(a.h, b.h) || numSort(a.d, b.d) || a.p - b.p,
};

// ------------------------------------------------------------ render: facets
const count = (list, key) => list.reduce((m, p) => { const v = key(p); if (v != null && v !== '') m.set(v, (m.get(v) || 0) + 1); return m; }, new Map());

function group(id, title, body, open = true) {
  return `<details class="fgroup" data-group="${id}"${open ? ' open' : ''}><summary>${title}${icon('down')}</summary><div class="fgroup__body">${body}</div></details>`;
}
function options(key, entries, labels = {}, dots = false) {
  return entries.map(([v, n]) => {
    const on = state[key].includes(v);
    return `<label class="fopt${n || on ? '' : ' is-zero'}"><input type="checkbox" data-k="${key}" value="${esc(v)}"${on ? ' checked' : ''}>
      ${dots ? `<i data-s="${esc(v)}"></i>` : ''}<span>${esc(labels[v] || v)}</span><small>${num(n)}</small></label>`;
  }).join('');
}
let brandQuery = '';
let brandAll = false;
function renderFacets() {
  const tipC = count(filter(state, ['tip']), (p) => p.c);
  const tipE = Object.keys(CATS).filter((c) => c !== 'ostalo').map((c) => [c, tipC.get(c) || 0]);
  const brC = count(filter(state, ['brend']), (p) => p.b);
  let brE = [...new Set([...brC.keys(), ...state.brend])].map((b) => [b, brC.get(b) || 0]).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  if (brandQuery) brE = brE.filter(([b]) => b.toLowerCase().includes(brandQuery));
  const brShown = brandAll || brandQuery ? brE : brE.slice(0, 8);
  const posC = count(filter(state, ['pozicija']), (p) => p.pos);
  const posE = ['Vodeća', 'Pogonska', 'Prikolica'].map((k) => [k, [...posC].filter(([v]) => v.includes(k)).reduce((a, [, n]) => a + n, 0)]).filter(([, n]) => n || state.pozicija.length);
  const osC = filter(state, ['osobine']);
  const osE = [['XL', osC.filter((p) => p.f?.includes('XL')).length], ['RunFlat', osC.filter((p) => p.f?.includes('RunFlat')).length]];
  const base = filter(state, ['cmin', 'cmax']).filter((p) => !p.np);
  const lo = base.length ? Math.floor(Math.min(...base.map((p) => p.p))) : 0;
  const hi = base.length ? Math.ceil(Math.max(...base.map((p) => p.p))) : 0;
  const stN = filter(state, ['stanje']).filter((p) => p.st).length;
  const akN = filter(state, ['akcija']).filter(onSale).length;

  const openState = Object.fromEntries($$('.fgroup', facetsBox).map((g) => [g.dataset.group, g.open]));
  facetsBox.innerHTML = [
    group('dost', 'Dostupnost', `<label class="switch"><span>Samo na stanju <small class="fine">(${num(stN)})</small></span><input type="checkbox" data-k="stanje"${state.stanje ? ' checked' : ''}></label>
      ${preset.has('akcija') ? '' : `<label class="switch"><span>Samo na akciji <small class="fine">(${num(akN)})</small></span><input type="checkbox" data-k="akcija"${state.akcija ? ' checked' : ''}></label>`}`),
    group('tip', 'Tip gume', options('tip', tipE, CATS)),
    group('brend', 'Proizvođač', `<input class="fgroup__search" type="search" placeholder="Pronađi proizvođača" aria-label="Pronađi proizvođača" data-brand-q value="${esc(brandQuery)}">
      ${options('brend', brShown)}${!brandQuery && brE.length > 8 ? `<button type="button" class="fgroup__more" data-brand-all>${brandAll ? 'Prikaži manje' : `Prikaži sve (${brE.length})`}</button>` : ''}`),
    group('cena', 'Cena po komadu (RSD)', `<div class="frange"><input type="number" inputmode="numeric" data-k="cmin" placeholder="${num(lo)}" value="${state.cmin}" aria-label="Najniža cena"><span>–</span><input type="number" inputmode="numeric" data-k="cmax" placeholder="${num(hi)}" value="${state.cmax}" aria-label="Najviša cena"></div>`),
    posE.length ? group('poz', 'Pozicija (teretne)', options('pozicija', posE)) : '',
    group('os', 'Karakteristike', options('osobine', osE, { XL: 'Ojačane (XL)', RunFlat: 'Run Flat' }), false),
  ].join('');
  $$('.fgroup', facetsBox).forEach((g) => { if (g.dataset.group in openState) g.open = openState[g.dataset.group]; });
}

function renderSizebar() {
  const fill = (sel, list, key, v) => {
    const vals = [...new Set(list.map((p) => p[key]).filter(Boolean))].sort(numSort);
    if (v && !vals.includes(v)) vals.push(v);
    sel.innerHTML = `<option value="">${key === 'd' ? 'Svi' : 'Sve'}</option>` + vals.map((x) => `<option${x === v ? ' selected' : ''}>${esc(x)}</option>`).join('');
    sel.classList.toggle('is-set', !!v);
  };
  fill(sizeSel.sirina, filter(state, ['sirina', 'visina', 'precnik']), 'w', state.sirina);
  fill(sizeSel.visina, filter(state, ['visina', 'precnik']), 'h', state.visina);
  fill(sizeSel.precnik, filter(state, ['precnik']), 'd', state.precnik);
  const zc = count(filter(state, ['sezona']), (p) => p.z);
  const all = [...zc.values()].reduce((a, b) => a + b, 0);
  seasonBar.innerHTML = `<button type="button" data-season="" aria-pressed="${!state.sezona.length}">Sve <small>${num(all)}</small></button>` +
    ['letnja', 'zimska', 'sve'].map((z) => `<button type="button" data-season="${z}" aria-pressed="${state.sezona.includes(z)}"><i data-s="${z}"></i>${SEASONS_PL[z]} <small>${num(zc.get(z) || 0)}</small></button>`).join('');
  seasonBar.hidden = !all;
}

function chipList() {
  const out = [];
  const size = [state.sirina, state.visina && `/${state.visina}`, state.precnik && ` R${state.precnik}`].filter(Boolean).join('');
  if (size) out.push(['size', '', `Dimenzija ${size}`]);
  LIST_KEYS.forEach((k) => state[k].forEach((v) => { if (!preset.has(k)) out.push([k, v, k === 'tip' ? CATS[v] : k === 'sezona' ? SEASONS_PL[v] : v]); }));
  if (state.cmin || state.cmax) out.push(['cena', '', `${state.cmin ? rsd(+state.cmin) : '0'} – ${state.cmax ? rsd(+state.cmax) : '…'}`]);
  if (state.stanje) out.push(['stanje', '', 'Na stanju']);
  if (state.akcija && !preset.has('akcija')) out.push(['akcija', '', 'Na akciji']);
  if (state.q) out.push(['q', '', `„${state.q}”`]);
  return out;
}
function renderChips() {
  const c = chipList();
  chipsBox.innerHTML = c.map(([k, v, l]) => `<button type="button" data-rm-k="${k}" data-rm-v="${esc(v)}" aria-label="Ukloni filter ${esc(l)}">${esc(l)}${icon('close')}</button>`).join('') +
    (c.length > 1 ? '<button type="button" class="chips__clear" data-clear>Obriši sve</button>' : '');
  const n = c.length;
  $$('[data-active-count]').forEach((b) => { b.textContent = n || ''; });
}

// ------------------------------------------------------------ render: results
let results = [];
function renderResults(reset = true) {
  if (reset) shown = PAGE;
  results = filter(state).sort(SORTS[state.sort] || SORTS.rec);
  const inStock = results.filter((p) => p.st).length;
  countEl.innerHTML = `<b>${num(results.length)}</b> ${gume(results.length)}${results.length ? ` · ${num(inStock)} na stanju` : ''}`;
  $('[data-filters-apply]', root).textContent = results.length ? `Prikaži ${num(results.length)} ${gume(results.length, true)}` : 'Nema rezultata';
  grid.classList.toggle('is-list', state.prikaz === 'list');
  $$('[data-view]', root).forEach((b) => b.setAttribute('aria-pressed', b.dataset.view === (state.prikaz || 'grid')));
  if (!results.length) { grid.innerHTML = emptyState(); moreBtn.hidden = true; shownEl.textContent = ''; return; }
  grid.innerHTML = results.slice(0, shown).map(cardHTML).join('');
  moreBtn.hidden = shown >= results.length;
  moreBtn.textContent = `Prikaži još ${num(Math.min(PAGE, results.length - shown))}`;
  shownEl.textContent = `Prikazano ${num(Math.min(shown, results.length))} od ${num(results.length)}`;
  grid.setAttribute('aria-busy', 'false');
}
function emptyState() {
  // offer the single most useful way out: drop one filter, with the count it would give
  const ways = chipList().map(([k, v, l]) => {
    const s = clone(state);
    drop(s, k, v);
    return [k, v, l, filter(s).length];
  }).filter((w) => w[3]).sort((a, b) => a[3] - b[3]).slice(0, 3);
  const size = [state.sirina, state.visina && `/${state.visina}`, state.precnik && ` R${state.precnik}`].filter(Boolean).join('');
  return `<div class="empty">${size ? `<p class="sz">${esc(size)}</p>` : ''}<h2 class="d3">Nema guma za ove filtere</h2>
   <p>Pokušajte bez jednog od filtera ili nas pozovite — ako gume nema u online ponudi, proverićemo kod dobavljača.</p>
   <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center">${ways.map(([k, v, l, n]) => `<button class="btn btn--line btn--sm" data-rm-k="${k}" data-rm-v="${esc(v)}">Bez „${esc(l)}” · ${num(n)}</button>`).join('')}
   <a class="btn btn--go btn--sm" href="tel:+381325461011">${icon('phone')}+381 32 5461 011</a></div></div>`;
}

// ------------------------------------------------------------ mutations
const clone = (s) => JSON.parse(JSON.stringify(s));
function drop(s, k, v) {
  if (k === 'size') { s.sirina = s.visina = s.precnik = ''; return; }
  if (k === 'cena') { s.cmin = s.cmax = ''; return; }
  if (LIST_KEYS.includes(k)) s[k] = s[k].filter((x) => x !== v); else s[k] = '';
}
function update({ facets = true } = {}) {
  writeURL();
  renderSizebar();
  if (facets) renderFacets();
  renderChips();
  renderResults();
  retitle();
}
function retitle() {
  const h = $('.phead__t');
  if (!h || preset.has('akcija')) return;
  const tip = state.tip.length === 1 ? CATS[state.tip[0]] : '';
  const z = state.sezona.length === 1 ? state.sezona[0] : '';
  const words = [tip, z && z !== 'sve' ? SEASONS_PL[z].toLowerCase() : '', 'gume', z === 'sve' ? 'za sve sezone' : ''].filter(Boolean).join(' ');
  const t = words[0].toUpperCase() + words.slice(1);
  if (h.getAttribute('aria-label') === t) return;
  h.textContent = t; h.setAttribute('aria-label', t);
  document.title = `${h.textContent} — Čajka M`;
}

function bind() {
  Object.entries(sizeSel).forEach(([k, sel]) => sel.addEventListener('change', () => {
    state[k] = sel.value;
    if (k === 'sirina') { state.visina = ''; state.precnik = ''; }
    if (k === 'visina') state.precnik = '';
    const bar = $('[data-sizebar]'); bar.classList.remove('is-flash'); void bar.offsetWidth; bar.classList.add('is-flash');
    update();
  }));
  seasonBar.addEventListener('click', (e) => {
    const b = e.target.closest('[data-season]'); if (!b) return;
    const z = b.dataset.season;
    state.sezona = !z ? [] : state.sezona.includes(z) ? state.sezona.filter((x) => x !== z) : [z];
    update();
  });
  facetsBox.addEventListener('change', (e) => {
    const t = e.target, k = t.dataset.k;
    if (!k) return;
    if (LIST_KEYS.includes(k)) state[k] = t.checked ? [...state[k], t.value] : state[k].filter((x) => x !== t.value);
    else if (k === 'cmin' || k === 'cmax') state[k] = t.value ? String(Math.max(0, +t.value)) : '';
    else state[k] = t.checked ? '1' : '';
    update();
  });
  facetsBox.addEventListener('input', (e) => {
    if (!e.target.matches('[data-brand-q]')) return;
    brandQuery = e.target.value.trim().toLowerCase();
    renderFacets();
    const q = $('[data-brand-q]', facetsBox); q.focus(); q.setSelectionRange(q.value.length, q.value.length);
  });
  facetsBox.addEventListener('click', (e) => { if (e.target.closest('[data-brand-all]')) { brandAll = !brandAll; renderFacets(); } });
  root.addEventListener('click', (e) => {
    const rm = e.target.closest('[data-rm-k]');
    if (rm) { drop(state, rm.dataset.rmK, rm.dataset.rmV); update(); return; }
    if (e.target.closest('[data-clear]')) {
      LIST_KEYS.forEach((k) => { if (!preset.has(k)) state[k] = []; });
      ['sirina', 'visina', 'precnik', 'cmin', 'cmax', 'stanje', 'q'].forEach((k) => { state[k] = ''; });
      if (!preset.has('akcija')) state.akcija = '';
      update(); return;
    }
    const v = e.target.closest('[data-view]');
    if (v) { state.prikaz = v.dataset.view === 'list' ? 'list' : ''; writeURL(); renderResults(false); }
  });
  sortSel.addEventListener('change', () => { state.sort = sortSel.value; writeURL(); renderResults(); });
  moreBtn.addEventListener('click', () => {
    const from = shown;
    shown += PAGE;
    grid.insertAdjacentHTML('beforeend', results.slice(from, shown).map((p, i) => cardHTML(p, i)).join(''));
    moreBtn.hidden = shown >= results.length;
    moreBtn.textContent = `Prikaži još ${num(Math.min(PAGE, results.length - shown))}`;
    shownEl.textContent = `Prikazano ${num(Math.min(shown, results.length))} od ${num(results.length)}`;
    grid.children[from]?.querySelector('a:not([tabindex])')?.focus({ preventScroll: true });
  });

  // mobile sheet
  let scrim;
  const open = () => {
    filtersEl.classList.add('is-open');
    scrim = Object.assign(document.createElement('div'), { className: 'filters-scrim' });
    scrim.addEventListener('click', close);
    document.body.append(scrim); document.body.style.overflow = 'hidden';
    $('[data-filters-close]', filtersEl).focus();
  };
  function close() { filtersEl.classList.remove('is-open'); scrim?.remove(); document.body.style.overflow = ''; $('[data-filters-open]', root).focus(); }
  $('[data-filters-open]', root).addEventListener('click', open);
  $('[data-filters-close]', root).addEventListener('click', close);
  $('[data-filters-apply]', root).addEventListener('click', () => { close(); root.scrollIntoView({ behavior: 'smooth' }); });
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && filtersEl.classList.contains('is-open')) close(); });
}

// ------------------------------------------------------------ compare bar
const cmpbar = $('[data-cmpbar]');
function paintCmp() {
  const n = compare.items().length;
  cmpbar.hidden = !n;
  $('[data-cmpbar-t]', cmpbar).textContent = n === 1 ? '1 guma u poređenju — dodajte još jednu' : `${n} gume u poređenju`;
}
onChange(paintCmp);
paintCmp();

// ------------------------------------------------------------ boot
(async () => {
  grid.innerHTML = '<p class="skeleton">Učitavanje guma…</p>';
  const { list, byId } = await loadProducts();
  window.__products = byId;
  ALL = list.filter((p) => p.c !== 'ostalo' || preset.has('akcija'));
  ALL.forEach((p) => { p._h = `${p.n} ${p.b} ${p.m} ${p.sz}`.toLowerCase(); });
  state = readURL();
  sortSel.value = state.sort || 'rec';
  bind();
  update();
  reveal();
})();
