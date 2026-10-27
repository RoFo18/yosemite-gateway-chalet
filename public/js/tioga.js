/* Tioga Road opening dates vs. April 1 snowpack. Draws every [data-tioga] block from #tioga-data. */
(() => {
  const src = document.getElementById('tioga-data');
  if (!src) return;
  const NS = 'http://www.w3.org/2000/svg';
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const CUM = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
  const doy = s => { const [m, d] = s.split(' '); return CUM[MON.indexOf(m)] + +d; };
  const dstr = n => { n = Math.round(n); let i = 11; while (CUM[i] >= n) i--; return `${['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][i]} ${n - CUM[i]}`; };
  const short = n => { n = Math.round(n); let i = 11; while (CUM[i] >= n) i--; return `${MON[i]} ${n - CUM[i]}`; };

  const all = JSON.parse(src.textContent).map(r => ({ ...r, od: doy(r.open) })).sort((a, b) => a.y - b.y);
  const fit = all.filter(r => r.snow != null);
  const mx = fit.reduce((s, r) => s + r.snow, 0) / fit.length, my = fit.reduce((s, r) => s + r.od, 0) / fit.length;
  const slope = fit.reduce((s, r) => s + (r.snow - mx) * (r.od - my), 0) / fit.reduce((s, r) => s + (r.snow - mx) ** 2, 0);
  const icpt = my - slope * mx;
  const pred = s => icpt + slope * s;
  fit.forEach(r => { r.p = pred(r.snow); r.gap = r.od - r.p; });
  const recent = fit.filter(r => r.y >= 2020);
  const recentGap = recent.reduce((s, r) => s + r.gap, 0) / recent.length;
  const era = y => (y >= 2020 ? 'new' : y >= 1980 ? 'old' : 'early');
  const signed = g => `${g >= 0 ? '+' : '−'}${Math.abs(Math.round(g))}`;

  const el = (tag, attrs = {}, parent) => {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  };
  const txt = (parent, x, y, s, cls, anchor = 'start') => { const t = el('text', { x, y, class: cls, 'text-anchor': anchor }, parent); t.textContent = s; return t; };

  function tooltip(host) {
    const t = document.createElement('div');
    t.className = 'tg-tip'; t.hidden = true; host.appendChild(t);
    return {
      show(html, x, y) {
        t.innerHTML = html; t.hidden = false;
        const w = t.offsetWidth, h = t.offsetHeight, W = host.clientWidth;
        let left = x + 14; if (left + w > W - 4) left = x - w - 14; if (left < 4) left = 4;
        let top = y - h - 12; if (top < 0) top = y + 16;
        t.style.left = left + 'px'; t.style.top = top + 'px';
      },
      hide() { t.hidden = true; }
    };
  }
  const tipFor = r => `<strong>${r.y}</strong><span>Opened ${dstr(r.od)}</span>` +
    (r.snow != null ? `<span>Snowpack ${r.snow}% of average</span><span>Snow predicts ${dstr(r.p)}, so ${Math.abs(Math.round(r.gap))} days ${r.gap >= 0 ? 'late' : 'early'}</span>` : '<span>No snowpack on record</span>') +
    (r.note ? `<em>${r.note}</em>` : '');

  function nearest(svg, items, ev, max = 26) {
    const b = svg.getBoundingClientRect();
    const px = ev.clientX - b.left, py = ev.clientY - b.top;
    let best = null, bd = max * max;
    for (const it of items) { const d = (it.cx - px) ** 2 + (it.cy - py) ** 2; if (d < bd) { bd = d; best = it; } }
    return [best, px, py];
  }

  /* ------------------------------------------------------------ scatter */
  function scatter(host) {
    host.innerHTML = '';
    const W = host.clientWidth, H = Math.max(340, Math.min(560, W * 0.56));
    const m = { t: 18, r: 18, b: 46, l: 62 };
    const X = s => m.l + (s / 260) * (W - m.l - m.r);
    const Y = d => m.t + (1 - (d - 105) / (215 - 105)) * (H - m.t - m.b);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: 'tg-svg' }, host);
    const g = el('g', {}, svg);
    [[121, 'May 1'], [152, 'Jun 1'], [182, 'Jul 1'], [213, 'Aug 1']].forEach(([d, l]) => {
      el('line', { x1: m.l, x2: W - m.r, y1: Y(d), y2: Y(d), class: 'tg-grid' }, g);
      txt(g, m.l - 10, Y(d) + 4, l, 'tg-tick', 'end');
    });
    [0, 50, 100, 150, 200, 250].forEach(s => txt(g, X(s), H - m.b + 22, s + '%', 'tg-tick', 'middle'));
    txt(g, (m.l + W - m.r) / 2, H - 6, 'April 1 snowpack, percent of average', 'tg-axis', 'middle');
    el('line', { x1: X(100), x2: X(100), y1: m.t, y2: H - m.b, class: 'tg-avg' }, g);
    txt(g, X(100) + 6, m.t + 12, 'Average snow', 'tg-note');
    el('line', { x1: X(0), y1: Y(pred(0)), x2: X(255), y2: Y(pred(255)), class: 'tg-fit' }, g);
    const items = [];
    fit.forEach(r => {
      const cx = X(r.snow), cy = Y(r.od);
      el('circle', { cx, cy, r: W < 520 ? 4.5 : 5.5, class: `tg-dot tg-${era(r.y)}` }, g);
      items.push({ r, cx, cy });
    });
    const lab = W < 520 ? [2023, 2020, 2015, 2026] : [2023, 2020, 2015, 2026, 1983, 2024, 2022];
    lab.forEach(y => {
      const it = items.find(i => i.r.y === y); if (!it) return;
      const right = it.cx < W * 0.72;
      txt(g, it.cx + (right ? 10 : -10), it.cy + 4, String(y), 'tg-lab', right ? 'start' : 'end');
    });
    const ring = el('circle', { r: 9, class: 'tg-ring', visibility: 'hidden' }, svg);
    const tip = tooltip(host);
    const move = ev => {
      const [best] = nearest(svg, items, ev);
      if (!best) { tip.hide(); ring.setAttribute('visibility', 'hidden'); return; }
      ring.setAttribute('cx', best.cx); ring.setAttribute('cy', best.cy); ring.setAttribute('visibility', 'visible');
      tip.show(tipFor(best.r), best.cx, best.cy);
    };
    svg.addEventListener('pointermove', move);
    svg.addEventListener('pointerdown', move);
    svg.addEventListener('pointerleave', () => { tip.hide(); ring.setAttribute('visibility', 'hidden'); });
  }

  /* ------------------------------------------------------------ residual bars */
  function residuals(host) {
    host.innerHTML = '';
    const W = host.clientWidth, H = Math.max(280, Math.min(400, W * 0.42));
    const m = { t: 30, r: 10, b: 52, l: 46 };
    const yrs = fit.map(r => r.y);
    const n = yrs[yrs.length - 1] - yrs[0] + 1, bw = (W - m.l - m.r) / n;
    const X = y => m.l + (y - yrs[0]) * bw;
    const Y = v => m.t + (1 - (v + 25) / 60) * (H - m.t - m.b);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: 'tg-svg' }, host);
    [-20, -10, 10, 20, 30].forEach(v => {
      el('line', { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), class: 'tg-grid' }, svg);
      txt(svg, m.l - 8, Y(v) + 4, (v > 0 ? '+' : '−') + Math.abs(v), 'tg-tick', 'end');
    });
    txt(svg, m.l - 8, Y(0) + 4, '0', 'tg-tick', 'end');
    txt(svg, m.l, 14, 'Days late (up) or early (down) against the snow prediction', 'tg-axis');
    const items = [];
    fit.forEach(r => {
      const v = Math.max(-25, Math.min(35, r.gap));
      const y0 = Y(0), y1 = Y(v), w = Math.max(2, bw - 2);
      const top = Math.min(y0, y1), h = Math.max(1.5, Math.abs(y1 - y0));
      el('rect', { x: X(r.y) + 1, y: top, width: w, height: h, rx: Math.min(2, w / 2), class: `tg-bar ${r.gap >= 0 ? 'tg-late' : 'tg-early'}` }, svg);
      items.push({ r, cx: X(r.y) + bw / 2, cy: y1, x0: X(r.y), x1: X(r.y) + bw });
    });
    el('line', { x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0), class: 'tg-zero' }, svg);
    [[1980, 1989], [1990, 1999], [2000, 2009], [2010, 2019], [2020, 2026]].forEach(([a, b]) => {
      const rs = fit.filter(r => r.y >= a && r.y <= b), mean = rs.reduce((s, r) => s + r.gap, 0) / rs.length;
      el('line', { x1: X(a) + 1, x2: X(b) + bw - 1, y1: Y(mean), y2: Y(mean), class: 'tg-mean' }, svg);
      const cx = (X(a) + X(b) + bw) / 2, rm = Math.round(mean);
      txt(svg, cx, H - m.b + 20, `${a}s`, 'tg-tick', 'middle');
      txt(svg, cx, H - m.b + 38, rm === 0 ? 'on the line' : `${Math.abs(rm)} days ${rm > 0 ? 'late' : 'early'}`, 'tg-meanlab', 'middle');
    });
    const tip = tooltip(host);
    const move = ev => {
      const b = svg.getBoundingClientRect(), px = ev.clientX - b.left;
      const it = items.find(i => px >= i.x0 && px < i.x1);
      if (!it) return tip.hide();
      tip.show(tipFor(it.r), it.cx, Math.min(it.cy, Y(0)));
    };
    svg.addEventListener('pointermove', move);
    svg.addEventListener('pointerdown', move);
    svg.addEventListener('pointerleave', () => tip.hide());
  }

  /* ------------------------------------------------------------ eras */
  function eras(host) {
    host.innerHTML = '';
    const W = host.clientWidth, H = Math.max(260, Math.min(360, W * 0.38));
    const m = { t: 48, r: 12, b: 32, l: 58 };
    const y0 = 1956, y1 = 2027;
    const X = y => m.l + ((y - y0) / (y1 - y0)) * (W - m.l - m.r);
    const Y = d => m.t + (1 - (d - 92) / (210 - 92)) * (H - m.t - m.b);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: 'tg-svg' }, host);
    [[91, 'Apr 1'], [121, 'May 1'], [152, 'Jun 1'], [182, 'Jul 1']].forEach(([d, l]) => {
      el('line', { x1: m.l, x2: W - m.r, y1: Y(d), y2: Y(d), class: 'tg-grid' }, svg);
      txt(svg, m.l - 10, Y(d) + 4, l, 'tg-tick', 'end');
    });
    [1960, 1970, 1980, 1990, 2000, 2010, 2020].forEach(y => txt(svg, X(y), H - 10, y, 'tg-tick', 'middle'));
    [[1957, 1979, 'early'], [1980, 2019, 'old'], [2020, 2026, 'new']].forEach(([a, b, c]) => {
      const rs = all.filter(r => r.y >= a && r.y <= b), mean = rs.reduce((s, r) => s + r.od, 0) / rs.length;
      el('line', { x1: X(a) - 4, x2: X(b) + 4, y1: Y(mean), y2: Y(mean), class: `tg-eramean tg-${c}` }, svg);
      const lx = c === 'new' ? X(b) + 4 : X(a) - 4, an = c === 'new' ? 'end' : 'start';
      txt(svg, lx, 14, c === 'new' ? '2020s' : `${a} to ${String(b).slice(2)}`, 'tg-tick', an);
      txt(svg, lx, 32, `avg ${short(mean)}`, 'tg-meanlab', an);
      el('line', { x1: lx, x2: lx, y1: 38, y2: Y(mean), class: 'tg-grid' }, svg);
    });
    const items = [];
    all.forEach(r => {
      const cx = X(r.y), cy = Y(r.od);
      el('circle', { cx, cy, r: W < 520 ? 3.5 : 4.5, class: `tg-dot tg-${era(r.y)}` }, svg);
      items.push({ r: r.snow != null ? fit.find(f => f.y === r.y) : r, cx, cy });
    });
    const tip = tooltip(host);
    const move = ev => { const [best] = nearest(svg, items, ev, 20); if (!best) return tip.hide(); tip.show(tipFor(best.r), best.cx, best.cy); };
    svg.addEventListener('pointermove', move);
    svg.addEventListener('pointerdown', move);
    svg.addEventListener('pointerleave', () => tip.hide());
  }

  /* ------------------------------------------------------------ predictor */
  function predictor(host) {
    host.innerHTML = `
      <div class="tg-pred">
        <label for="tg-snow" class="tg-pred-l">April 1 snowpack <output id="tg-snow-out">100%</output> of average</label>
        <input id="tg-snow" type="range" min="0" max="250" step="1" value="100">
        <div class="tg-pred-out" aria-live="polite">
          <div><span class="tg-pred-k">The snow says</span><span class="tg-pred-v" data-p="fit"></span><span class="tg-pred-s" data-p="band"></span></div>
          <div><span class="tg-pred-k">At the 2020s pace</span><span class="tg-pred-v" data-p="recent"></span><span class="tg-pred-s">${Math.round(recentGap)} days later, as every spring since 2020 has run</span></div>
          <div><span class="tg-pred-k">Springs most like it</span><span class="tg-pred-s tg-pred-near" data-p="near"></span></div>
        </div>
      </div>`;
    const inp = host.querySelector('input'), out = host.querySelector('output');
    const q = k => host.querySelector(`[data-p="${k}"]`);
    const upd = () => {
      const s = +inp.value, p = pred(s);
      out.textContent = s + '%';
      q('fit').textContent = dstr(p);
      q('band').textContent = `Half of all springs land between ${short(p - 7)} and ${short(p + 7)}`;
      q('recent').textContent = dstr(p + recentGap);
      q('near').textContent = [...fit].sort((a, b) => Math.abs(a.snow - s) - Math.abs(b.snow - s)).slice(0, 3)
        .sort((a, b) => b.y - a.y).map(r => `${r.y}: ${r.snow}%, opened ${short(r.od)}`).join('. ');
    };
    inp.addEventListener('input', upd);
    upd();
  }

  /* ------------------------------------------------------------ table */
  function table(host) {
    const rows = [...all].reverse().map(r => {
      const f = fit.find(x => x.y === r.y);
      return `<tr><th scope="row">${r.y}</th><td>${r.snow != null ? r.snow + '%' : ''}</td><td>${short(r.od)}</td><td>${r.close || ''}</td><td>${f ? short(f.p) : ''}</td><td>${f ? signed(f.gap) : ''}</td></tr>`;
    }).join('');
    host.innerHTML = `<details class="tg-table"><summary>See every year in a table</summary><div class="tg-table-scroll"><table>
      <thead><tr><th scope="col">Year</th><th scope="col">April 1 snow</th><th scope="col">Opened</th><th scope="col">Closed</th><th scope="col">Snow predicts</th><th scope="col">Days late</th></tr></thead>
      <tbody>${rows}</tbody></table></div></details>`;
  }

  const draw = { scatter, residuals, eras, predictor, table };
  const blocks = [...document.querySelectorAll('[data-tioga]')];
  const render = () => blocks.forEach(b => { const k = b.dataset.tioga; if (k !== 'predictor' && k !== 'table') draw[k](b); });
  blocks.forEach(b => { const k = b.dataset.tioga; if (k === 'predictor' || k === 'table') draw[k](b); });
  render();
  let w = innerWidth, t;
  addEventListener('resize', () => { if (innerWidth === w) return; w = innerWidth; clearTimeout(t); t = setTimeout(render, 150); });
})();
