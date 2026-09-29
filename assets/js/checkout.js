// Checkout: validates like the real thing, then states plainly that this
// prototype is not connected to the WooCommerce shop yet.
import { $, $$, esc, rsd, img, cart } from './core.js';

const form = $('[data-checkout-form]');
const mini = $('[data-mini-lines]');
const total = $('[data-sum-total]');
const lines = cart.lines();
mini.innerHTML = lines.length
  ? lines.map((l) => `<div class="mline"><img src="${img(l)}" alt=""><div><span class="sz">${esc(l.sz)}</span><small>${esc(l.b)} ${esc(l.m)}</small><small>${l.q} × ${rsd(l.p)}</small></div><b>${rsd(l.q * l.p)}</b></div>`).join('')
  : '<p class="fine">Korpa je prazna.</p>';
total.textContent = rsd(cart.total());

const company = $('[data-company]');
$$('[name="kupac"]', form).forEach((r) => r.addEventListener('change', () => {
  const on = form.kupac.value === 'pravno';
  company.hidden = !on;
  $$('input', company).forEach((i) => { i.required = on; });
}));

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const err = $('[data-err]', form);
  if (!lines.length) {
    err.textContent = 'Korpa je prazna — dodajte gume pre poručivanja.';
    err.hidden = false;
    return;
  }
  if (!form.checkValidity()) {
    const bad = $$(':invalid', form).filter((i) => i.matches('input, textarea'));
    err.textContent = `Proverite označena polja (${bad.length}).`;
    err.hidden = false;
    form.reportValidity();
    return;
  }
  err.hidden = true;
  $('[data-done-email]').textContent = form.email.value;
  form.closest('.cart-layout').hidden = true;
  $('[data-done]').hidden = false;
  scrollTo({ top: 0 });
  cart.clear();
});
