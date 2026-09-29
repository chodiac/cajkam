// Full cart page.
import { $, esc, rsd, icon, img, url, cart, onChange } from './core.js';

const box = $('[data-lines]');
const sumItems = $('[data-sum-items]');
const sumTotal = $('[data-sum-total]');
const go = $('[data-checkout]');

function render() {
  const lines = cart.lines();
  if (!lines.length) {
    box.innerHTML = `<div class="empty"><p class="sz">0 guma</p><h2 class="d3">Korpa je prazna</h2>
      <p>Izaberite dimenziju i pronađite gume za vaše vozilo.</p><a class="btn btn--go" href="${url('gume.html')}">Pretraži gume ${icon('arrow')}</a></div>`;
    go.setAttribute('aria-disabled', 'true');
    go.style.pointerEvents = 'none';
    go.style.opacity = '.45';
  } else {
    box.innerHTML = lines.map((l) => {
      const href = url(`guma.html?p=${encodeURIComponent(l.s)}`);
      return `<article class="cline" data-id="${l.id}">
      <a href="${href}" tabindex="-1" aria-hidden="true"><img src="${img(l)}" alt="" loading="lazy"></a>
      <div><a href="${href}" style="text-decoration:none"><span class="sz">${esc(l.sz)}</span></a>
       <p class="cline__m">${esc(l.b)} ${esc(l.m)}</p>
       <p class="cline__u">${rsd(l.p)} po komadu${l.r && l.p < l.r ? ` · umesto ${rsd(l.r)}` : ''}</p>
       <button class="linkbtn cline__rm" data-rm="${l.id}">${icon('trash')}Ukloni</button></div>
      <div class="qty"><button class="icon-btn" data-d="-1" aria-label="Manje">${icon('minus')}</button><input type="number" min="1" max="99" value="${l.q}" aria-label="Količina za ${esc(l.sz)}" data-qin><button class="icon-btn" data-d="1" aria-label="Više">${icon('plus')}</button></div>
      <p class="cline__sum">${rsd(l.q * l.p)}</p></article>`;
    }).join('');
    go.removeAttribute('aria-disabled');
    go.style.pointerEvents = '';
    go.style.opacity = '';
  }
  sumItems.textContent = rsd(cart.total());
  sumTotal.textContent = rsd(cart.total());
}

box.addEventListener('click', (e) => {
  const line = e.target.closest('.cline');
  if (!line) return;
  const id = +line.dataset.id;
  if (e.target.closest('[data-rm]')) { cart.remove(id); return; }
  const d = e.target.closest('[data-d]');
  if (d) cart.set(id, +line.querySelector('[data-qin]').value + +d.dataset.d);
});
box.addEventListener('change', (e) => {
  const line = e.target.closest('.cline');
  if (line && e.target.matches('[data-qin]')) cart.set(+line.dataset.id, +e.target.value);
});
onChange(render);
render();
