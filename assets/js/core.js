// Shared runtime: paths, formatting, cart/compare store, header, cards, motion.
const doc = document.documentElement;
export const ROOT = doc.dataset.root || '';
export const VER = doc.dataset.v || '';
export const CALM = doc.classList.contains('calm');
export const UPLOADS = 'https://cajkam.rs/wp-content/uploads/';
export const url = (p) => ROOT + p;
export const $ = (s, el = document) => el.querySelector(s);
export const $$ = (s, el = document) => [...el.querySelectorAll(s)];
export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const nf0 = new Intl.NumberFormat('sr-Latn-RS', { maximumFractionDigits: 0 });
const nf2 = new Intl.NumberFormat('sr-Latn-RS', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const num = (v) => nf0.format(v);
export const rsd = (v) => (Number.isInteger(v) ? nf0 : nf2).format(v) + ' RSD';
export const SEASON = { letnja: 'Letnja', zimska: 'Zimska', sve: 'Sve sezone' };
export const SEASONS_PL = { letnja: 'Letnje', zimska: 'Zimske', sve: 'Sve sezone' };
export const CATS = { putnicke: 'Putničke', poluteretne: 'Poluteretne', teretne: 'Teretne', industrijske: 'Industrijske', poljoprivredne: 'Poljoprivredne', ostalo: 'Ostalo' };
export const img = (p, full) => (p.i ? UPLOADS + (full ? p.i.replace(/-\d+x\d+(\.\w+)$/, '$1') : p.i) : '');
export const onSale = (p) => !p.np && p.r && p.p > 0 && p.p < p.r;
export const pct = (p) => Math.round((1 - p.p / p.r) * 100);
// Serbian count forms: 1 guma · 2–4 gume · 5+ guma; accusative 1 gumu ("Prikaži 1 gumu").
export function gume(n, acc = false) {
  const d = n % 10, h = n % 100;
  if (d === 1 && h !== 11) return acc ? 'gumu' : 'guma';
  return d >= 2 && d <= 4 && (h < 12 || h > 14) ? 'gume' : 'guma';
}
export const icon = (n, c = 'i') => `<svg class="${c}" aria-hidden="true"><use href="#i-${n}"/></svg>`;

// ---------------------------------------------------------------- data
let productsP, sizesP;
export function loadProducts() {
  productsP ||= fetch(url(`data/web/products.json?v=${VER}`)).then((r) => r.json()).then((list) => {
    const byId = new Map(list.map((p) => [p.id, p]));
    const bySlug = new Map(list.map((p) => [p.s, p]));
    return { list, byId, bySlug };
  });
  return productsP;
}
export function loadSizes() {
  sizesP ||= fetch(url(`data/web/sizes.json?v=${VER}`)).then((r) => r.json());
  return sizesP;
}

// ---------------------------------------------------------------- store
// Lines keep a small snapshot so the cart renders without the 2 MB catalogue.
const read = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
const write = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } };
export const snap = (p) => ({ id: p.id, s: p.s, sz: p.sz, b: p.b, m: p.m, p: p.p, r: p.r, i: p.i, st: p.st, z: p.z, li: p.li, si: p.si });

export const cart = {
  lines: () => read('cm.cart', []),
  save(lines) { write('cm.cart', lines); emit(); },
  add(p, q = 1) {
    const lines = this.lines();
    const l = lines.find((x) => x.id === p.id);
    if (l) l.q = Math.min(99, l.q + q); else lines.push({ ...snap(p), q });
    this.save(lines);
  },
  set(id, q) { this.save(this.lines().map((l) => (l.id === id ? { ...l, q: Math.max(1, Math.min(99, q)) } : l))); },
  remove(id) { this.save(this.lines().filter((l) => l.id !== id)); },
  clear() { this.save([]); },
  count() { return this.lines().reduce((a, l) => a + l.q, 0); },
  total() { return this.lines().reduce((a, l) => a + l.q * l.p, 0); },
};
export const compare = {
  items: () => read('cm.compare', []),
  has(id) { return this.items().some((x) => x.id === id); },
  toggle(p) {
    let it = this.items();
    if (it.some((x) => x.id === p.id)) it = it.filter((x) => x.id !== p.id);
    else { if (it.length >= 4) { toast('Možete uporediti najviše 4 gume.', 'Uporedi', 'uporedi.html'); return false; } it.push(snap(p)); }
    write('cm.compare', it); emit(); return true;
  },
  remove(id) { write('cm.compare', this.items().filter((x) => x.id !== id)); emit(); },
};
const subs = new Set();
export const onChange = (fn) => subs.add(fn);
function emit() { subs.forEach((f) => f()); paintCounts(); }
addEventListener('storage', (e) => { if (e.key?.startsWith('cm.')) emit(); });

function paintCounts() {
  const n = cart.count();
  $$('[data-cart-count]').forEach((b) => { const was = b.textContent; b.textContent = n; b.hidden = !n; if (String(n) !== was && n) { b.classList.remove('bump'); void b.offsetWidth; b.classList.add('bump'); } });
  $$('[data-cart-total]').forEach((t) => { t.textContent = n ? rsd(cart.total()) : 'Korpa'; });
  const c = compare.items().length;
  $$('[data-compare-count]').forEach((b) => { b.textContent = c; b.hidden = !c; });
  const ids = new Set(compare.items().map((x) => x.id));
  $$('[data-compare]').forEach((b) => b.setAttribute('aria-pressed', ids.has(+b.dataset.compare)));
  paintDrawer();
}

// ---------------------------------------------------------------- cards
export function cardHTML(p, k = 0) {
  const sale = onSale(p);
  const idx = p.li ? `<span class="tag tag--idx">${p.li}${p.si}</span>` : '';
  const flags = (p.f || []).filter((f) => f === 'XL' || f === 'RunFlat').map((f) => `<span class="tag">${f}</span>`).join('');
  const pos = p.pos ? `<span class="tag">${esc(p.pos)}</span>` : '';
  const price = p.np ? '<p class="price price--ask">Cena na upit</p>'
    : `<p class="price">${sale ? `<s>${rsd(p.r)}</s>` : ''}<b>${rsd(p.p)}</b><small>sa PDV-om</small></p>`;
  const stock = p.st ? '<p class="stock stock--ok"><i></i>Na stanju</p>' : '<p class="stock stock--no"><i></i>Nije na stanju</p>';
  const href = url(`guma.html?p=${encodeURIComponent(p.s)}`);
  return `<article class="card" data-id="${p.id}" style="--k:${k}" data-snap='${esc(JSON.stringify(snap(p)))}'>
 <a class="card__media" href="${href}" tabindex="-1" aria-hidden="true"><img src="${img(p)}" alt="" loading="lazy" decoding="async" width="300" height="300">${sale ? `<span class="card__sale">−${pct(p)} %</span>` : ''}${p.z ? `<span class="season" data-s="${p.z}"><i></i>${SEASON[p.z]}</span>` : ''}</a>
 <div class="card__body">
  <p class="card__brand">${esc(p.b) || '&nbsp;'}</p>
  <h3 class="card__title"><a href="${href}"><span class="sz">${esc(p.sz || p.n)}</span><span class="card__model">${esc(p.m)}</span></a></h3>
  <p class="card__meta">${idx}${flags}${pos}</p>
  <div class="card__foot">${price}${stock}</div>
 </div>
 <div class="card__act">
  <button class="btn btn--go btn--sm" data-add="${p.id}"${!p.st || p.np ? ' disabled' : ''}>${icon('cart')}<span>U korpu</span></button>
  <button class="icon-btn icon-btn--line" data-compare="${p.id}" aria-pressed="${compare.has(p.id)}" aria-label="Dodaj u poređenje">${icon('compare')}</button>
 </div>
</article>`;
}
const cardSnap = (el) => { try { return JSON.parse(el.closest('[data-snap]').dataset.snap); } catch { return null; } };

// ---------------------------------------------------------------- toast
let toastT;
export function toast(msg, linkText, href) {
  const t = $('[data-toast]');
  if (!t) return;
  t.innerHTML = `<span>${esc(msg)}</span>${linkText ? `<a href="${url(href)}">${esc(linkText)}</a>` : ''}`;
  t.hidden = false; t.style.animation = 'none'; void t.offsetWidth; t.style.animation = '';
  clearTimeout(toastT); toastT = setTimeout(() => { t.hidden = true; }, 3600);
}

// ---------------------------------------------------------------- overlays
function overlay(el, open, opener) {
  el.hidden = !open;
  document.body.style.overflow = open ? 'hidden' : '';
  if (open) { el._opener = opener || document.activeElement; ($('input, button, a', el.firstElementChild) || el).focus(); }
  else el._opener?.focus?.();
}
function paintDrawer() {
  const box = $('[data-cart-lines]');
  if (!box) return;
  const lines = cart.lines();
  box.innerHTML = lines.length ? lines.map((l) => `<div class="mline"><img src="${img(l)}" alt="" loading="lazy">
   <div><span class="sz">${esc(l.sz)}</span><small>${esc(l.b)} ${esc(l.m)}</small><small>${l.q} × ${rsd(l.p)}</small></div>
   <button class="icon-btn" data-rm="${l.id}" aria-label="Ukloni ${esc(l.sz)}">${icon('trash')}</button></div>`).join('')
    : `<div class="empty"><p>Korpa je prazna.</p><a class="btn btn--go" href="${url('gume.html')}"><span>Pronađite gume</span></a></div>`;
  const s = $('[data-cart-sum]'); if (s) s.textContent = rsd(cart.total());
}

// ---------------------------------------------------------------- header
function initHeader() {
  const drawer = $('[data-drawer]');
  const burger = $('[data-menu-open]');
  burger?.addEventListener('click', () => { overlay(drawer, true, burger); burger.setAttribute('aria-expanded', 'true'); });
  drawer?.addEventListener('click', (e) => { if (e.target === drawer || e.target.closest('[data-menu-close]')) { overlay(drawer, false); burger.setAttribute('aria-expanded', 'false'); } });

  const cd = $('[data-cartdrawer]');
  cd?.addEventListener('click', (e) => {
    if (e.target === cd || e.target.closest('[data-cart-close]')) overlay(cd, false);
    const rm = e.target.closest('[data-rm]'); if (rm) cart.remove(+rm.dataset.rm);
  });
  addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      [drawer, cd].forEach((o) => { if (o && !o.hidden) overlay(o, false); });
      closeMega();
    }
    // "/" jumps to search, like most shops people already know
    if (e.key === '/' && !e.target.closest('input, textarea, select, [contenteditable]')) { e.preventDefault(); $('#q')?.focus(); }
  });

  // mega menu
  const mega = $('#mega'), mt = $('.mega-toggle'), li = $('.has-mega');
  let hoverT;
  const openMega = () => { clearTimeout(hoverT); if (!mega.hidden) return; mega.hidden = false; mt.setAttribute('aria-expanded', 'true'); };
  function closeMega() { if (!mega) return; mega.hidden = true; mt?.setAttribute('aria-expanded', 'false'); }
  if (mega) {
    mt.addEventListener('click', () => { $$('img', mega).forEach((i) => { i.loading = 'eager'; }); if (mega.hidden) openMega(); else closeMega(); });
    if (matchMedia('(hover:hover)').matches) {
      // Entering either the nav item or the panel must cancel a pending close,
      // otherwise moving the pointer down into the menu closes it 200 ms later.
      // warm the menu photos as soon as the pointer heads for "Gume", so the panel never opens empty
      li.addEventListener('pointerenter', () => $$('img', mega).forEach((i) => { i.loading = 'eager'; }), { once: true });
      [li, mega].forEach((el) => {
        el.addEventListener('mouseenter', () => { clearTimeout(hoverT); if (mega.hidden) hoverT = setTimeout(openMega, 90); });
        el.addEventListener('mouseleave', () => { clearTimeout(hoverT); hoverT = setTimeout(closeMega, 200); });
      });
    }
    document.addEventListener('click', (e) => { if (!e.target.closest('.hdr')) closeMega(); });
  }

  // hide on the way down, return on the way up; road rail follows the scroll
  const hdr = $('[data-hdr]');
  const rail = $('.roadrail');
  let lastY = scrollY, ticking = false;
  const onScroll = () => {
    const y = scrollY;
    hdr.classList.toggle('is-scrolled', y > 8);
    if (!CALM && mega?.hidden && !document.activeElement?.closest?.('.hdr')) hdr.classList.toggle('is-hidden', y > 320 && y > lastY + 2);
    if (y < lastY - 2) hdr.classList.remove('is-hidden');
    lastY = y;
    const max = document.documentElement.scrollHeight - innerHeight;
    rail?.style.setProperty('--p', max > 0 ? (y / max).toFixed(4) : 0);
    ticking = false;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();
  initSearch();
}

// Suggestions come from the small sizes index, not the full catalogue.
const SIZE_RX = /^\s*(\d{3})\s*[/ ,.-]?\s*(\d{2})\s*[/ ,.-]?\s*(?:z?r)?\s*(\d{2})\b/i;
export function parseSize(q) {
  const m = SIZE_RX.exec(q || '');
  return m ? { w: m[1], h: m[2], d: m[3] } : null;
}
function initSearch() {
  const form = $('[data-search]');
  if (!form) return;
  const input = $('input', form), box = $('#suggest');
  let sel = -1;
  const close = () => { box.hidden = true; sel = -1; input.setAttribute('aria-expanded', 'false'); };
  $$('form[role="search"]').forEach((f) => f.addEventListener('submit', (e) => {
    const s = parseSize($('input', f).value);
    if (s) { e.preventDefault(); location.href = url(`gume.html?sirina=${s.w}&visina=${s.h}&precnik=${s.d}`); }
  }));
  input.addEventListener('input', async () => {
    const q = input.value.trim().toLowerCase();
    if (q.length < 2) return close();
    const { rows, brands } = await loadSizes();
    const digits = q.replace(/\D/g, '');
    const agg = new Map();
    for (const [, , w, h, d, n] of rows) {
      if (!h) continue;
      const key = `${w}/${h} R${d}`;
      if (digits.length >= 3 && `${w}${h}${d}`.toLowerCase().startsWith(digits)) agg.set(key, (agg.get(key) || 0) + n);
    }
    const sizes = [...agg].sort((a, b) => b[1] - a[1]).slice(0, 6);
    const br = brands.filter(([b]) => b && b.toLowerCase().includes(q)).slice(0, 4);
    let html = '';
    if (sizes.length) html += '<p class="suggest__h">Dimenzije</p>' + sizes.map(([k, n]) => {
      const [w, h, d] = k.split(/[/ R]+/);
      return `<a role="option" href="${url(`gume.html?sirina=${w}&visina=${h}&precnik=${d}`)}"><span class="sz">${k}</span><small>${num(n)} ${gume(n)}</small></a>`;
    }).join('');
    if (br.length) html += '<p class="suggest__h">Proizvođači</p>' + br.map(([b, n]) => `<a role="option" href="${url(`gume.html?brend=${encodeURIComponent(b)}`)}"><b>${esc(b)}</b><small>${num(n)} ${gume(n)}</small></a>`).join('');
    html += `<p class="suggest__h">Pretraga</p><a role="option" href="${url(`gume.html?q=${encodeURIComponent(input.value.trim())}`)}">Sve gume za „${esc(input.value.trim())}”<small>${icon('arrow')}</small></a>`;
    box.innerHTML = html; box.hidden = false; sel = -1; input.setAttribute('aria-expanded', 'true');
  });
  input.addEventListener('keydown', (e) => {
    const opts = $$('a', box);
    if (box.hidden || !opts.length) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + opts.length) % opts.length;
      opts.forEach((o, i) => o.setAttribute('aria-selected', i === sel));
    } else if (e.key === 'Enter' && sel >= 0) { e.preventDefault(); location.href = opts[sel].href; } else if (e.key === 'Escape') { close(); input.blur(); }
  });
  document.addEventListener('click', (e) => { if (!form.contains(e.target)) close(); });
}

// ---------------------------------------------------------------- global delegation
function initActions() {
  document.addEventListener('click', (e) => {
    const add = e.target.closest('[data-add]');
    if (add) {
      const p = cardSnap(add) || window.__products?.get(+add.dataset.add);
      if (!p) return;
      cart.add(p, 1);
      const c = add.closest('.card'); c?.classList.remove('is-added'); void c?.offsetWidth; c?.classList.add('is-added');
      toast(`${p.sz} dodata u korpu.`, 'Otvori korpu', 'korpa.html');
      return;
    }
    const cmp = e.target.closest('[data-compare]');
    if (cmp) {
      const p = cardSnap(cmp) || window.__products?.get(+cmp.dataset.compare);
      if (p && compare.toggle(p) && compare.has(p.id)) toast(`${p.sz} je u poređenju (${compare.items().length}/4).`, 'Uporedi', 'uporedi.html');
      return;
    }
    const open = e.target.closest('[data-cart-open]');
    if (open && cart.count() && !location.pathname.endsWith('korpa.html') && matchMedia('(min-width: 768px)').matches) {
      e.preventDefault(); overlay($('[data-cartdrawer]'), true, open);
      return;
    }
    // the tyre photo morphs into the product page (cross-document view transition)
    const toPdp = e.target.closest('.card a[href*="guma.html"]');
    if (toPdp && 'onpagereveal' in window) {
      $$('.card__media img').forEach((i) => { i.style.viewTransitionName = ''; });
      const im = $('.card__media img', toPdp.closest('.card'));
      if (im) im.style.viewTransitionName = 'tyre';
    }
  });

  initRails();

  // explainer
  const dlg = $('[data-xp-dialog]');
  if (dlg) {
    $$('[data-explain]').forEach((b) => b.addEventListener('click', () => dlg.showModal()));
    dlg.addEventListener('click', (e) => {
      if (e.target === dlg || e.target.closest('[data-xp-close]')) dlg.close();
      const seg = e.target.closest('[data-xp]');
      if (seg) {
        $$('[data-xp]', dlg).forEach((s) => s.setAttribute('aria-pressed', s === seg));
        $$('[data-xp-info]', dlg).forEach((i) => { i.hidden = i.dataset.xpInfo !== seg.dataset.xp; });
      }
    });
  }

  // forms that have no backend yet: validate, then say honestly that nothing was sent
  $$('[data-demo-form]').forEach((f) => f.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!f.reportValidity()) return;
    f.innerHTML = `<div class="done" style="padding:24px 0"><div class="done__mark">${icon('check')}</div><p class="big">${esc(f.dataset.success)}</p>
      <p class="todo-note"><span class="todo">${icon('info')}Nije povezano</span>Forma još nije povezana sa serverom — ništa nije poslato. Za hitne stvari pozovite +381 32 5461 011.</p></div>`;
  }));
}

export function initRails(root = document) {
  $$('[data-rail]', root).forEach((r) => {
    if (r._rail) return; r._rail = 1;
    const t = $('.rail__track', r);
    const bar = $('[data-rail-progress]', r);
    const step = () => t.clientWidth * 0.9;
    $('[data-rail-prev]', r)?.addEventListener('click', () => t.scrollBy({ left: -step(), behavior: CALM ? 'auto' : 'smooth' }));
    $('[data-rail-next]', r)?.addEventListener('click', () => t.scrollBy({ left: step(), behavior: CALM ? 'auto' : 'smooth' }));
    const paint = () => { const max = t.scrollWidth - t.clientWidth; const vis = t.clientWidth / (t.scrollWidth || 1); bar?.style.setProperty('--rp', Math.min(1, vis + (max > 0 ? (t.scrollLeft / max) * (1 - vis) : 1)).toFixed(3)); };
    t.addEventListener('scroll', paint, { passive: true });
    new ResizeObserver(paint).observe(t);
  });
}

// ---------------------------------------------------------------- motion
// Headings rise word by word from their own baseline.
function splitHeadings() {
  $$('[data-split]').forEach((h) => {
    if (h.dataset.splitDone) return;
    h.dataset.splitDone = 1;
    const label = h.textContent;
    let i = 0;
    const walk = (node) => {
      [...node.childNodes].forEach((c) => {
        if (c.nodeType === 3) {
          const frag = document.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach((part) => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.append(' '); return; }
            const w = document.createElement('span'); w.className = 'w'; w.setAttribute('aria-hidden', 'true');
            const s = document.createElement('span'); s.textContent = part; s.style.setProperty('--wi', i++);
            w.append(s); frag.append(w);
          });
          c.replaceWith(frag);
        } else if (c.nodeType === 1) walk(c);
      });
    };
    walk(h);
    h.setAttribute('aria-label', label.trim());
  });
}

export function reveal(root = document) {
  const els = $$('[data-reveal]:not(.is-in), [data-split]:not(.is-in), [data-stack]:not(.is-in), [data-countup]:not(.is-in), [data-year]:not(.is-in)', root);
  if (CALM || !('IntersectionObserver' in window)) return els.forEach((e) => e.classList.add('is-in'));
  const io = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (!en.isIntersecting) return;
    const el = en.target;
    if (el.matches('[data-reveal]') && !el.style.getPropertyValue('--i')) {
      const sibs = [...el.parentElement.children].filter((x) => x.matches('[data-reveal]'));
      el.style.transitionDelay = `${Math.min(sibs.indexOf(el), 5) * 70}ms`;
    }
    if (el.matches('[data-countup]')) countUp(el);
    if (el.matches('[data-year]')) countYear(el);
    el.classList.add('is-in'); io.unobserve(el);
  }), { rootMargin: '0px 0px -10% 0px' });
  els.forEach((e) => io.observe(e));
}
function countUp(el) {
  const target = parseInt(el.textContent.replace(/\D/g, ''), 10);
  if (!target) return;
  const t0 = performance.now(), dur = 1100;
  const f = (now) => { const t = Math.min(1, (now - t0) / dur); el.textContent = num(Math.round(target * (1 - (1 - t) ** 3))); if (t < 1) requestAnimationFrame(f); };
  requestAnimationFrame(f);
}
function countYear(el) {
  // the odometer runs from today back to the founding year
  const end = +el.textContent, start = new Date().getFullYear();
  const t0 = performance.now(), dur = 1400;
  const f = (now) => { const t = Math.min(1, (now - t0) / dur); el.textContent = Math.round(start + (end - start) * (1 - (1 - t) ** 4)); if (t < 1) requestAnimationFrame(f); };
  requestAnimationFrame(f);
}

// Footer sign-off drifts with the scroll, like a sign passing by.
function initBye() {
  const p = $('[data-bye]');
  if (!p || CALM) return;
  const io = new IntersectionObserver(([e]) => { p._on = e.isIntersecting; });
  io.observe(p);
  addEventListener('scroll', () => {
    if (!p._on) return;
    const r = p.getBoundingClientRect();
    const t = 1 - Math.min(1, Math.max(0, r.top / innerHeight));
    p.style.setProperty('--bye', `${(-t * 8).toFixed(2)}%`);
  }, { passive: true });
}

initHeader();
initActions();
paintCounts();
splitHeadings();
reveal();
initBye();
