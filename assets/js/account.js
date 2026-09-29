// Account screens. Works locally only; a real login needs the WooCommerce backend.
import { $, $$ } from './core.js';

const guest = $('[data-acct-guest]');
const user = $('[data-acct-user]');
const side = $('.acct__side');
const tabs = $$('[role="tab"]');

tabs.forEach((t) => t.addEventListener('click', () => {
  tabs.forEach((x) => x.setAttribute('aria-selected', x === t));
  $$('[role="tabpanel"]').forEach((p) => { p.hidden = p.id !== t.getAttribute('aria-controls'); });
}));
if (location.hash === '#registracija') tabs[1].click();

const show = (logged) => { guest.hidden = logged; side.hidden = logged; user.hidden = !logged; };
const signIn = (e) => {
  e.preventDefault();
  if (!e.target.reportValidity()) return;
  try { sessionStorage.setItem('cm.user', '1'); } catch { /* private mode */ }
  show(true);
};
$('[data-login]').addEventListener('submit', signIn);
$('[data-register]').addEventListener('submit', signIn);
$('[data-logout]').addEventListener('click', () => {
  try { sessionStorage.removeItem('cm.user'); } catch { /* private mode */ }
  show(false);
});
$('[data-lost]').addEventListener('click', (e) => {
  e.preventDefault();
  e.target.textContent = 'Link za novu lozinku stiže na e-mail kada sajt bude povezan sa prodavnicom.';
});
try { show(sessionStorage.getItem('cm.user') === '1'); } catch { show(false); }
