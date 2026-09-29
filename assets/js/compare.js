// Side-by-side comparison of up to four tyres, from stored snapshots,
// enriched with full data once the catalogue loads.
import { $, esc, rsd, img, url, compare, cart, onChange, toast, loadProducts, SEASON, CATS, icon } from './core.js';

const box = $('[data-cmp]');
const diff = $('[data-diff]');
let full = new Map();

const ROWS = [
  ['Cena', (p) => (p.np ? 'Na upit' : `<b>${rsd(p.p)}</b>${p.r && p.p < p.r ? `<br><s class="fine">${rsd(p.r)}</s>` : ''}`)],
  ['Dostupnost', (p) => (p.st ? '<span class="stock stock--ok"><i></i>Na stanju</span>' : '<span class="stock stock--no"><i></i>Nije na stanju</span>')],
  ['Proizvođač', (p) => esc(p.b)],
  ['Model', (p) => esc(p.m)],
  ['Sezona', (p) => SEASON[p.z] || '—'],
  ['Tip gume', (p) => CATS[p.c] || '—'],
  ['Širina', (p) => p.w || '—'],
  ['Visina', (p) => p.h || '—'],
  ['Prečnik', (p) => (p.d ? `${p.d}"` : '—')],
  ['Indeks nosivosti', (p) => p.li || '—'],
  ['Indeks brzine', (p) => p.si || '—'],
  ['Karakteristike', (p) => (p.f || []).join(', ') || '—'],
];

function render() {
  const items = compare.items().map((s) => full.get(s.id) || s);
  const toggle = diff.closest('label');
  if (!items.length) {
    box.innerHTML = `<div class="empty"><h2 class="d3">Još niste izabrali gume za poređenje</h2><p>U katalogu kliknite ikonicu poređenja na kartici gume. Možete uporediti do 4 gume.</p><a class="btn btn--go" href="${url('gume.html')}">Otvori katalog</a></div>`;
    toggle.hidden = true;
    return;
  }
  toggle.hidden = false;
  const head = `<tr><th></th>${items.map((p) => `<td><a href="${url(`guma.html?p=${encodeURIComponent(p.s)}`)}"><img src="${img(p)}" alt=""></a><span class="sz">${esc(p.sz)}</span>${esc(p.b)} ${esc(p.m)}
    <div style="display:flex;gap:6px;margin-top:10px"><button class="btn btn--go btn--sm" data-buy="${p.id}"${!p.st || p.np ? ' disabled' : ''}>${icon('cart')}U korpu</button><button class="icon-btn icon-btn--line cmp__rm" data-out="${p.id}" aria-label="Ukloni iz poređenja">${icon('close')}</button></div></td>`).join('')}</tr>`;
  const body = ROWS.map(([k, f]) => {
    const vals = items.map(f);
    const same = items.length > 1 && vals.every((v) => v === vals[0]);
    return `<tr class="${same ? 'is-same' : 'is-diff'}${same && diff.checked ? ' hide' : ''}"><th scope="row">${k}</th>${vals.map((v) => `<td>${v}</td>`).join('')}</tr>`;
  }).join('');
  box.innerHTML = `<table><thead>${head}</thead><tbody>${body}</tbody></table>`;
}

box.addEventListener('click', (e) => {
  const out = e.target.closest('[data-out]');
  if (out) { compare.remove(+out.dataset.out); return; }
  const buy = e.target.closest('[data-buy]');
  if (buy) {
    const p = compare.items().find((x) => x.id === +buy.dataset.buy);
    cart.add(full.get(p.id) || p, 1);
    toast(`${p.sz} dodata u korpu.`, 'Otvori korpu', 'korpa.html');
  }
});
diff.addEventListener('change', render);
onChange(render);
render();
loadProducts().then(({ byId }) => { full = byId; render(); });
