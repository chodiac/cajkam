// Homepage: tyre finder, hero film, the "Gazeći sloj" tread section, brand belt, service list.
import { $, $$, CALM, loadSizes, num, url, icon, gume } from './core.js';

const numSort = (a, b) => (parseFloat(a) || 9e9) - (parseFloat(b) || 9e9) || String(a).localeCompare(b);
const lerp = (a, b, t) => a + (b - a) * t;
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));

// ------------------------------------------------------------ finder
// Options depend on each other and come from the real size index, so every
// combination offered leads to at least one tyre.
(async function finder() {
  const form = $('[data-finder]');
  if (!form) return;
  const tip = $('[data-f-tip]', form);
  const sel = { w: $('[data-dim="w"]', form), h: $('[data-dim="h"]', form), d: $('[data-dim="d"]', form) };
  const label = $('[data-finder-label]', form);
  const { rows } = await loadSizes();
  const season = () => form.querySelector('input[name="sezona"]:checked')?.value || '';
  // row: [cat, season, w, h, d, count, inStock]
  const base = () => rows.filter((r) => (!tip.value || r[0] === tip.value) && (!season() || r[1] === season()));
  const fill = (s, vals, blank) => {
    const was = s.value;
    s.innerHTML = `<option value="">${blank}</option>` + vals.map((v) => `<option value="${v}">${v || 'bez oznake'}</option>`).join('');
    if (vals.includes(was)) s.value = was;
    else if (was) { s.closest('.ff').classList.remove('is-flash'); void s.offsetWidth; s.closest('.ff').classList.add('is-flash'); }
    s.disabled = !vals.length;
  };
  const uniq = (list, i) => [...new Set(list.map((r) => r[i]))].sort(numSort);
  function update() {
    let list = base();
    fill(sel.w, uniq(list, 2), '—');
    if (sel.w.value) list = list.filter((r) => r[2] === sel.w.value);
    const hs = uniq(list, 3).filter(Boolean);
    fill(sel.h, sel.w.value ? hs : [], '—');
    if (sel.h.value) list = list.filter((r) => r[3] === sel.h.value);
    fill(sel.d, sel.w.value ? uniq(list, 4) : [], '—');
    if (sel.d.value) list = list.filter((r) => r[4] === sel.d.value);
    const n = list.reduce((a, r) => a + r[5], 0);
    const any = sel.w.value || season() || tip.value !== 'putnicke';
    label.textContent = !any ? 'Pronađi gume' : n ? `Prikaži ${num(n)} ${gume(n, true)}` : 'Nema — prikaži slične';
  }
  form.addEventListener('change', (e) => {
    if (e.target === tip || e.target.name === 'sezona') update();
    if (e.target === sel.w) { sel.h.value = ''; sel.d.value = ''; update(); if (!sel.h.disabled) sel.h.focus(); else sel.d.focus(); }
    if (e.target === sel.h) { sel.d.value = ''; update(); sel.d.focus(); }
    if (e.target === sel.d) update();
  });
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const q = new URLSearchParams();
    if (tip.value) q.set('tip', tip.value);
    if (season()) q.set('sezona', season());
    if (sel.w.value) q.set('sirina', sel.w.value);
    if (sel.h.value) q.set('visina', sel.h.value);
    if (sel.d.value) q.set('precnik', sel.d.value);
    location.href = url(`gume.html?${q}`);
  });
  update();
})();

// ------------------------------------------------------------ hero film
// A coded stand-in for the hero footage: macro side view of a wheel rolling
// across dry asphalt, a wet road and snow. When media/hero.mp4 exists the
// build hides this canvas and the <video> plays instead.
const COND = [
  { key: 'dry', label: 'Suv asfalt', icon: 'sun', sky: ['#E9B26A', '#7C5A3A', '#211C19'], road: ['#4A4643', '#2A2725'], tint: 'rgba(255,190,120,.10)' },
  { key: 'wet', label: 'Mokar kolovoz', icon: 'drop', sky: ['#7F98A6', '#34454F', '#12181C'], road: ['#2C3439', '#12171A'], tint: 'rgba(120,170,210,.10)' },
  { key: 'snow', label: 'Sneg', icon: 'snow', sky: ['#DDE6EC', '#8FA2AF', '#3A4A55'], road: ['#E9EEF1', '#B8C4CB'], tint: 'rgba(210,230,245,.12)' },
];
const PHASE = 6.5; // seconds per condition

(function film() {
  const cv = $('[data-film]');
  const vid = $('[data-hero-video]');
  if (vid) { // real footage: the same button pauses it; calm mode keeps the poster
    const b = $('[data-film-ctl]');
    if (CALM) { vid.removeAttribute('autoplay'); vid.pause(); }
    b?.addEventListener('click', () => { if (vid.paused) vid.play(); else vid.pause(); b.innerHTML = icon(vid.paused ? 'play' : 'pause'); b.setAttribute('aria-label', vid.paused ? 'Pusti video' : 'Pauziraj video'); });
  }
  if (!cv || cv.hidden) return;
  const hero = $('[data-hero]');
  const ctx = cv.getContext('2d', { alpha: false });
  const ctl = $('[data-film-ctl]');
  const lab = $('[data-cond-label]'), ico = $('[data-cond-icon]');
  let W = 0, H = 0, t = 0, last = 0, playing = !CALM, visible = true, raf = 0, curCond = -1;

  // grain + asphalt textures are made once
  const noise = (w, h, a, blurX = 0) => {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'); const id = g.createImageData(w, h);
    for (let i = 0; i < id.data.length; i += 4) { const v = Math.random() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = a; }
    g.putImageData(id, 0, 0);
    if (blurX) { g.filter = `blur(${blurX}px)`; g.drawImage(c, 0, 0); g.filter = 'none'; }
    return c;
  };
  const grain = noise(256, 256, 22);
  const asphalt = (() => {
    const c = document.createElement('canvas'); c.width = 512; c.height = 128; const g = c.getContext('2d');
    for (let i = 0; i < 2600; i++) { const v = 90 + Math.random() * 120; g.fillStyle = `rgba(${v},${v},${v},${Math.random() * .5})`; g.fillRect(Math.random() * 512, Math.random() * 128, 1 + Math.random() * 3, 1 + Math.random() * 2); }
    const s = document.createElement('canvas'); s.width = 512; s.height = 128; const sg = s.getContext('2d');
    sg.filter = 'blur(0px)';
    for (let k = 0; k < 10; k++) { sg.globalAlpha = .14; sg.drawImage(c, k * 3, 0); sg.drawImage(c, k * 3 - 512, 0); } // motion streak
    return s;
  })();

  const parts = []; // spray / snow powder / dust
  const flakes = Array.from({ length: 160 }, () => ({ x: Math.random(), y: Math.random(), s: .5 + Math.random() * 1.8, v: .3 + Math.random() }));
  const lights = Array.from({ length: 14 }, () => ({ x: Math.random(), y: .3 + Math.random() * .22, r: 6 + Math.random() * 22, a: .15 + Math.random() * .35 }));

  function size() {
    const r = cv.getBoundingClientRect();
    const scale = Math.min(1, 1280 / r.width) * Math.min(devicePixelRatio || 1, 1.5);
    W = cv.width = Math.round(r.width * scale); H = cv.height = Math.round(r.height * scale);
  }
  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const mix = (a, b, k) => { const A = hex(a), B = hex(b); return `rgb(${A.map((v, i) => Math.round(lerp(v, B[i], k))).join(',')})`; };

  function weights(time) {
    const cyc = (time / PHASE) % 3;
    const i = Math.floor(cyc), f = cyc - i;
    const blend = clamp((f - .82) / .18); // last 18 % of a phase crossfades into the next
    return { a: i, b: (i + 1) % 3, k: blend * blend * (3 - 2 * blend) };
  }

  function draw(dt) {
    if (!W || !H) return;
    const { a, b, k } = weights(t);
    const A = COND[a], B = COND[b];
    const main = k < .5 ? a : b;
    if (main !== curCond) { curCond = main; lab.textContent = COND[main].label; ico.innerHTML = icon(COND[main].icon); }
    const wet = (a === 1 ? 1 - k : 0) + (b === 1 ? k : 0);
    const snow = (a === 2 ? 1 - k : 0) + (b === 2 ? k : 0);
    const dry = 1 - wet - snow;

    const narrow = W < H * 1.1;
    const horizon = H * (narrow ? .52 : .56);
    const ground = H * (narrow ? .82 : .9);
    const R = Math.min(H * (narrow ? .27 : .43), W * (narrow ? .38 : .34));
    const cx = W * (narrow ? .62 : .74), cy = ground - R;
    const speed = W * .9; // px per second at the contact line
    const off = t * speed;

    // sky
    let g = ctx.createLinearGradient(0, 0, 0, horizon);
    g.addColorStop(0, mix(A.sky[2], B.sky[2], k)); g.addColorStop(.55, mix(A.sky[1], B.sky[1], k)); g.addColorStop(1, mix(A.sky[0], B.sky[0], k));
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, horizon + 1);
    // low sun / sky glow behind the wheel
    g = ctx.createRadialGradient(W * .82, horizon * .92, 0, W * .82, horizon * .92, W * .6);
    g.addColorStop(0, `rgba(255,${Math.round(lerp(200, 240, snow))},${Math.round(lerp(140, 250, snow + wet))},${.55 * dry + .25 * snow + .15 * wet})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, horizon);
    // distant lights, parallax
    for (const L of lights) {
      const x = ((L.x * W * 1.4 - off * .04) % (W * 1.4) + W * 1.4) % (W * 1.4) - W * .2, y = horizon * (L.y + .5);
      const rg = ctx.createRadialGradient(x, y, 0, x, y, L.r * (W / 1280));
      rg.addColorStop(0, `rgba(255,${wet > .5 ? 220 : 200},160,${L.a * (1 - snow * .6)})`); rg.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = rg; ctx.fillRect(x - 60, y - 60, 120, 120);
    }

    // road with perspective strips
    g = ctx.createLinearGradient(0, horizon, 0, H);
    g.addColorStop(0, mix(A.road[1], B.road[1], k)); g.addColorStop(1, mix(A.road[0], B.road[0], k));
    ctx.fillStyle = g; ctx.fillRect(0, horizon, W, H - horizon);
    const strips = 42;
    ctx.globalAlpha = .55 - snow * .35;
    for (let i = 0; i < strips; i++) {
      const y0 = horizon + (H - horizon) * (i / strips) ** 1.6, y1 = horizon + (H - horizon) * ((i + 1) / strips) ** 1.6;
      const depth = (y0 - horizon) / (ground - horizon + 1); // 0 far .. 1 at contact
      const sx = ((off * depth * .5) % 512 + 512) % 512;
      ctx.drawImage(asphalt, sx, (i * 7) % 100, 256, 8, 0, y0, W, Math.max(1, y1 - y0 + 1));
    }
    ctx.globalAlpha = 1;
    // wet sheen: sky reflected in the road
    if (wet > .01) {
      g = ctx.createLinearGradient(0, horizon, 0, H);
      g.addColorStop(0, `rgba(170,200,220,${.35 * wet})`); g.addColorStop(.6, `rgba(90,120,140,${.12 * wet})`); g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g; ctx.fillRect(0, horizon, W, H - horizon);
      for (const L of lights) {
        const x = ((L.x * W * 1.4 - off * .04) % (W * 1.4) + W * 1.4) % (W * 1.4) - W * .2;
        ctx.fillStyle = `rgba(255,210,150,${L.a * .35 * wet})`; ctx.fillRect(x - 2, horizon + 4, 4, (H - horizon) * .5);
      }
    }
    // haze where road meets sky, so the horizon never reads as a hard edge
    g = ctx.createLinearGradient(0, horizon - H * .08, 0, horizon + H * .06);
    const hz = mix(A.sky[0], B.sky[0], k).replace('rgb', 'rgba').replace(')', ',');
    g.addColorStop(0, hz + '0)'); g.addColorStop(.55, hz + '.55)'); g.addColorStop(1, hz + '0)');
    ctx.fillStyle = g; ctx.fillRect(0, horizon - H * .08, W, H * .14);
    // lane marking (runs parallel to travel) + snow ruts
    const laneY = lerp(horizon, ground, .38);
    const dash = W * .16, gap = W * .12;
    ctx.fillStyle = `rgba(245,240,225,${.75 * (1 - snow * .85)})`;
    for (let x = -((off * .38) % (dash + gap)); x < W; x += dash + gap) ctx.fillRect(x, laneY, dash, Math.max(2, H * .006));
    if (snow > .01) {
      ctx.fillStyle = `rgba(120,135,145,${.35 * snow})`;
      ctx.fillRect(0, ground - H * .012, W, H * .018);
      ctx.fillRect(0, lerp(horizon, ground, .6), W, H * .01);
    }

    // contact shadow
    g = ctx.createRadialGradient(cx, ground, 0, cx, ground, R * 1.3);
    g.addColorStop(0, `rgba(0,0,0,${.75 - snow * .25})`); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.save(); ctx.translate(cx, ground); ctx.scale(1, .12); ctx.translate(-cx, -ground);
    ctx.fillStyle = g; ctx.fillRect(cx - R * 1.4, ground - R * 1.4, R * 2.8, R * 2.8); ctx.restore();

    // the wheel
    const ang = off / R; // rolls without slipping
    ctx.save(); ctx.translate(cx, cy);
    ctx.fillStyle = '#0B0D0E'; ctx.beginPath(); ctx.arc(0, 0, R, 0, Math.PI * 2); ctx.fill();
    // tread blocks on the circumference (motion-blurred by drawing a few ghosts)
    const N = 44;
    for (let ghost = 0; ghost < 3; ghost++) {
      ctx.globalAlpha = ghost ? .25 : .9;
      ctx.fillStyle = '#1E2327';
      for (let i = 0; i < N; i++) {
        const a0 = ang + ghost * .012 + (i / N) * Math.PI * 2;
        ctx.save(); ctx.rotate(a0); ctx.fillRect(R * .93, -R * .045, R * .07, R * .09); ctx.restore();
      }
    }
    ctx.globalAlpha = 1;
    // sidewall
    g = ctx.createRadialGradient(0, 0, R * .6, 0, 0, R * .93);
    g.addColorStop(0, '#15191C'); g.addColorStop(.7, '#22282C'); g.addColorStop(1, '#101315');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, R * .92, 0, Math.PI * 2); ctx.fill();
    // rim: bright barrel + blurred spokes
    g = ctx.createRadialGradient(-R * .15, -R * .2, 0, 0, 0, R * .62);
    g.addColorStop(0, '#E4E8EA'); g.addColorStop(.7, '#8F999F'); g.addColorStop(1, '#4A5358');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, R * .62, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#262C30'; ctx.beginPath(); ctx.arc(0, 0, R * .56, 0, Math.PI * 2); ctx.fill();
    for (let ghost = 0; ghost < 6; ghost++) {
      ctx.globalAlpha = .22;
      ctx.fillStyle = '#B9C2C7';
      for (let s = 0; s < 5; s++) {
        ctx.save(); ctx.rotate(ang + s * Math.PI * 2 / 5 + ghost * .05);
        ctx.beginPath(); ctx.moveTo(-R * .05, -R * .12); ctx.lineTo(-R * .08, -R * .55); ctx.lineTo(R * .08, -R * .55); ctx.lineTo(R * .05, -R * .12); ctx.fill(); ctx.restore();
      }
    }
    ctx.globalAlpha = 1;
    ctx.fillStyle = '#9BA5AA'; ctx.beginPath(); ctx.arc(0, 0, R * .12, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#F2B51C'; ctx.beginPath(); ctx.arc(0, 0, R * .035, 0, Math.PI * 2); ctx.fill();
    // back light rimming the tyre
    ctx.strokeStyle = `rgba(255,${Math.round(lerp(200, 245, snow))},${Math.round(lerp(150, 255, snow + wet))},${.5 * dry + .35 * snow + .3 * wet})`;
    ctx.lineWidth = R * .025; ctx.beginPath(); ctx.arc(0, 0, R * .985, -Math.PI * .95, -Math.PI * .15); ctx.stroke();
    ctx.restore();

    // particles thrown back from the contact patch
    const emit = wet * 6 + snow * 5 + dry * 1.2;
    for (let i = 0; i < emit * dt * 60; i++) {
      const type = Math.random() < wet / (wet + snow + dry * .2 + 1e-6) ? 'w' : Math.random() < snow / (snow + dry * .2 + 1e-6) ? 's' : 'd';
      parts.push({ x: cx - R * .2 - Math.random() * R * .2, y: ground - 2, vx: -(.5 + Math.random()) * speed * .45, vy: -(.3 + Math.random() * .8) * H * .5, life: 0, max: .5 + Math.random() * .6, type, r: 1 + Math.random() * 2.5 });
    }
    for (let i = parts.length - 1; i >= 0; i--) {
      const p = parts[i];
      p.life += dt; p.x += p.vx * dt; p.y += p.vy * dt; p.vy += H * 1.6 * dt;
      if (p.life > p.max || p.y > ground + 4) { parts.splice(i, 1); continue; }
      const al = 1 - p.life / p.max;
      ctx.fillStyle = p.type === 'w' ? `rgba(200,225,240,${.5 * al})` : p.type === 's' ? `rgba(250,252,255,${.8 * al})` : `rgba(200,170,130,${.35 * al})`;
      if (p.type === 'w') ctx.fillRect(p.x, p.y, p.r * 5 * (W / 1280), p.r * .8);
      else { ctx.beginPath(); ctx.arc(p.x, p.y, p.r * (W / 1280) * (p.type === 's' ? 1.6 : 1), 0, 7); ctx.fill(); }
    }
    if (parts.length > 900) parts.splice(0, parts.length - 900);

    // weather in the air
    if (wet > .01) {
      ctx.strokeStyle = `rgba(200,220,235,${.35 * wet})`; ctx.lineWidth = 1;
      ctx.beginPath();
      for (const f of flakes) {
        const x = ((f.x * W - t * W * .6 * f.v) % W + W) % W, y = ((f.y * H + t * H * 2.2 * f.v) % H);
        ctx.moveTo(x, y); ctx.lineTo(x - W * .012, y + H * .05);
      }
      ctx.stroke();
    }
    if (snow > .01) {
      ctx.fillStyle = `rgba(255,255,255,${.85 * snow})`;
      for (const f of flakes) {
        const x = ((f.x * W - t * W * .35 * f.v) % W + W) % W, y = ((f.y * H + t * H * .16 * f.v + Math.sin(t * 2 + f.x * 20) * 6) % H);
        ctx.beginPath(); ctx.arc(x, y, f.s * (W / 1280) * 1.6, 0, 7); ctx.fill();
      }
    }

    // grade: tint, vignette, grain
    ctx.fillStyle = k < .5 ? A.tint : B.tint; ctx.fillRect(0, 0, W, H);
    g = ctx.createRadialGradient(W * .6, H * .5, H * .3, W * .5, H * .5, W * .8);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.6)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'overlay';
    const pat = ctx.createPattern(grain, 'repeat');
    ctx.save(); ctx.translate(Math.random() * 256, Math.random() * 256); ctx.fillStyle = pat; ctx.fillRect(-256, -256, W + 512, H + 512); ctx.restore();
    ctx.globalCompositeOperation = 'source-over';
  }

  function frame(now) {
    raf = 0;
    const dt = Math.min(.05, (now - (last || now)) / 1000); last = now;
    if (playing && visible && !document.hidden) { t += dt; draw(dt); }
    if (playing && visible) raf = requestAnimationFrame(frame);
  }
  const kick = () => { if (!raf && playing && visible) { last = 0; raf = requestAnimationFrame(frame); } };
  function setPlaying(p) {
    playing = p;
    ctl.innerHTML = icon(p ? 'pause' : 'play');
    ctl.setAttribute('aria-label', p ? 'Pauziraj video' : 'Pusti video');
    kick();
  }

  size(); t = 1.6; draw(0); cv.classList.add('is-on');
  new ResizeObserver(() => { size(); draw(0); }).observe(cv);
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; kick(); }).observe(hero);
  document.addEventListener('visibilitychange', kick);
  ctl?.addEventListener('click', () => setPlaying(!playing));
  if (!CALM) kick();
  window.__film = { draw: (time) => { t = time; draw(0); }, canvas: cv };
})();

// ------------------------------------------------------------ tread (signature)
// The tread band is sticky while the three season steps scroll past it. The
// page scroll literally rolls the tyre (background offset) and the step in the
// middle of the screen decides the road surface.
(function tread() {
  const sec = $('[data-tread]');
  if (!sec) return;
  const tv = $('.tv', sec);
  const steps = $$('[data-tstep]', sec);
  const lbl = $('[data-tv-label]', sec), temp = $('[data-tv-temp]', sec);
  const META = { letnja: ['Suv asfalt', 'Iznad 7 °C'], sve: ['Mokar kolovoz', 'Blage zime'], zimska: ['Sneg i led', 'Ispod 7 °C'] };
  const mq = matchMedia('(min-width: 900px)');
  let cond = 'letnja', inView = false;

  function setCond(c) {
    if (c === cond) return;
    cond = c; sec.dataset.cond = c;
    lbl.textContent = META[c][0]; temp.textContent = META[c][1];
  }
  function onScroll() {
    if (!mq.matches) return;
    const r = sec.getBoundingClientRect();
    const p = clamp(-r.top / (r.height - innerHeight));
    if (!CALM) tv.style.setProperty('--roll', `${(p * 3600).toFixed(1)}px`);
    const mid = innerHeight * .55;
    let best = steps[0], bd = 1e9;
    steps.forEach((s) => { const b = s.getBoundingClientRect(); const d = Math.abs((b.top + b.bottom) / 2 - mid); if (d < bd) { bd = d; best = s; } });
    steps.forEach((s) => s.classList.toggle('is-on', s === best));
    setCond(r.top > innerHeight * .1 && best === steps[0] ? 'letnja' : best.dataset.tstep);
  }
  addEventListener('scroll', () => requestAnimationFrame(onScroll), { passive: true });
  addEventListener('resize', onScroll);
  onScroll();

  // particles for the current surface: warm dust, rain, snow
  const cv = $('[data-tread-fx]', sec);
  if (!cv || CALM) return;
  const ctx = cv.getContext('2d');
  const P = Array.from({ length: 140 }, () => ({ x: Math.random(), y: Math.random(), v: .4 + Math.random(), s: .6 + Math.random() * 1.6 }));
  let raf = 0, t = 0, last = 0;
  const size = () => { cv.width = cv.clientWidth; cv.height = cv.clientHeight; };
  function frame(now) {
    const dt = Math.min(.05, (now - (last || now)) / 1000); last = now; t += dt;
    const W = cv.width, H = cv.height;
    ctx.clearRect(0, 0, W, H);
    if (cond === 'sve') {
      ctx.strokeStyle = 'rgba(190,215,235,.35)'; ctx.lineWidth = 1; ctx.beginPath();
      for (const p of P) { const x = ((p.x * W - t * 60 * p.v) % W + W) % W, y = (p.y * H + t * 900 * p.v) % H; ctx.moveTo(x, y); ctx.lineTo(x - 6, y + 26); }
      ctx.stroke();
    } else if (cond === 'zimska') {
      ctx.fillStyle = 'rgba(255,255,255,.85)';
      for (const p of P) { const x = ((p.x * W + Math.sin(t + p.y * 9) * 30) % W + W) % W, y = (p.y * H + t * 50 * p.v) % H; ctx.beginPath(); ctx.arc(x, y, p.s * 1.6, 0, 7); ctx.fill(); }
    } else {
      for (const p of P.slice(0, 60)) { const x = (p.x * W + Math.sin(t * .3 + p.y * 7) * 40) % W, y = ((p.y * H - t * 12 * p.v) % H + H) % H; ctx.fillStyle = `rgba(255,210,150,${.25 * p.s / 2.2})`; ctx.beginPath(); ctx.arc(x, y, p.s, 0, 7); ctx.fill(); }
    }
    raf = inView ? requestAnimationFrame(frame) : 0;
  }
  size(); addEventListener('resize', size);
  new IntersectionObserver(([e]) => { inView = e.isIntersecting && mq.matches; if (inView && !raf) { last = 0; raf = requestAnimationFrame(frame); } }).observe(sec);
})();

// ------------------------------------------------------------ brand belt
// Drifts on its own and picks up speed with the scroll, like passing traffic.
(function belt() {
  const b = $('[data-belt]');
  if (!b || CALM) return;
  let x = 0, v = 0, lastY = scrollY, hover = false, on = false, raf = 0, last = 0;
  b.addEventListener('mouseenter', () => { hover = true; });
  b.addEventListener('mouseleave', () => { hover = false; });
  b.addEventListener('focusin', () => { hover = true; });
  b.addEventListener('focusout', () => { hover = false; });
  addEventListener('scroll', () => { v += Math.abs(scrollY - lastY) * .6; lastY = scrollY; }, { passive: true });
  const half = () => b.firstElementChild.offsetWidth;
  function frame(now) {
    const dt = Math.min(.05, (now - (last || now)) / 1000); last = now;
    v *= .92;
    x -= (hover ? 0 : 40 + v * 6) * dt;
    const w = half(); if (-x > w) x += w;
    b.style.transform = `translate3d(${x.toFixed(1)}px,0,0)`;
    raf = on ? requestAnimationFrame(frame) : 0;
  }
  new IntersectionObserver(([e]) => { on = e.isIntersecting; if (on && !raf) { last = 0; raf = requestAnimationFrame(frame); } }).observe(b);
})();

// ------------------------------------------------------------ service list
(function service() {
  const list = $('[data-svc-list]');
  if (!list) return;
  const items = $$('.svc__item', list);
  const fine = matchMedia('(hover: hover) and (min-width: 901px)').matches;
  function activate(it) {
    if (it.hasAttribute('data-on')) return;
    items.forEach((x) => { const on = x === it; x.toggleAttribute('data-on', on); $('.svc__btn', x).setAttribute('aria-expanded', on); });
    $$('[data-svc-media]').forEach((m) => { m.hidden = m.dataset.svcMedia !== it.dataset.svc; });
  }
  items.forEach((it) => {
    $('.svc__btn', it).addEventListener('click', () => activate(it));
    if (fine) it.addEventListener('mouseenter', () => activate(it));
  });
})();
