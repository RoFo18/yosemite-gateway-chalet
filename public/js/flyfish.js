/* Where to fish today: map, live June Lake weather, month hatches, two choices, one answer. */
(() => {
  const src = document.getElementById('ff-data');
  if (!src) return;
  const D = JSON.parse(src.textContent);
  const root = document.querySelector('.fft');
  const out = root.querySelector('.fft-out');
  const now = { t: null, w: null, c: null, p: null };
  const month = new Date().getMonth();
  const season = [2, 3, 4].includes(month) ? 'spring' : [5, 6, 7].includes(month) ? 'summer' : [8, 9, 10].includes(month) ? 'fall' : 'winter';
  const LV = { beginner: 0, intermediate: 1, advanced: 2 };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // style fit by water kind: how naturally each style suits it
  const FIT = {
    spring: { dry: 3, nymph: 3, streamer: 0 }, meadow: { dry: 2, nymph: 2, streamer: 3 },
    stillwater: { dry: 0, nymph: 3, streamer: 3 }, freestone: { dry: 3, nymph: 2, streamer: 0 },
    tailwater: { dry: 1, nymph: 3, streamer: 3 }, alpine: { dry: 3, nymph: 1, streamer: 0 }
  };

  function score(w, style, skill) {
    const m = w.months[month];
    if (!m) return null;
    const f = w.flies[season] || {};
    if (style !== 'best' && !(f[style] || []).length) return null;
    let s = m * 10;
    const gap = LV[w.skill] - LV[skill];
    if (gap > 0) s -= gap * 5;            // technical water punishes beginners
    if (gap < -1) s -= 2;                 // easy water bores experts, a little
    if (style !== 'best') s += FIT[w.kind][style] * 2;
    if (now.w != null) {
      if (now.w > 25) s -= 8;
      else if (now.w > 15) s -= (w.kind === 'stillwater' || w.kind === 'alpine' || style === 'dry') ? 5 : 2;
    }
    if (now.c != null && style === 'dry' && now.c > 60) s += 3;   // overcast is mayfly weather
    if (now.t != null && now.t > 85 && (w.kind === 'meadow' || w.kind === 'tailwater')) s -= 3;
    return s;
  }

  function flies(w, style) {
    const f = w.flies[season] || {};
    if (style !== 'best') return (f[style] || []).slice(0, 3);
    const order = Object.entries(FIT[w.kind]).sort((a, b) => b[1] - a[1]).map(x => x[0]);
    const pick = [];
    order.forEach(k => (f[k] || []).forEach(x => pick.length < 3 && pick.push(x)));
    return pick;
  }

  const LEADS = ['Go here first.', 'Then, if that fails, here.'];
  function recommend(e) {
    if (e) e.preventDefault();
    const fd = new FormData(root.querySelector('form'));
    const style = fd.get('style'), skill = fd.get('skill');
    const ranked = D.waters.map(w => ({ w, s: score(w, style, skill) })).filter(x => x.s != null).sort((a, b) => b.s - a.s).slice(0, 2);
    if (!ranked.length) {
      out.innerHTML = '<p class="fft-none">Nothing nearby fishes that way this month. Change the style, or come back in the spring and we will talk.</p>';
      return;
    }
    out.innerHTML = ranked.map((r, i) => `<article class="fft-rec">
        <p class="fft-lead">${LEADS[i]}</p>
        <h3><a href="${r.w.url}">${esc(r.w.name)}</a></h3>
        <p class="fft-where">${esc(r.w.note)}</p>
        <p class="fft-flies"><span>Flies</span>${flies(r.w, style).map(esc).join(' &middot; ')}</p>
        <p class="fft-how"><span>The one thing</span>${esc(r.w.presentation)}</p>
      </article>`).join('');
    highlight(ranked.map(r => r.w.id));
  }

  // weather
  const fmt = { t: v => Math.round(v) + '°F', w: v => Math.round(v) + ' mph', c: v => Math.round(v) + '%', p: v => Math.round(v) + ' hPa' };
  fetch(`https://api.open-meteo.com/v1/forecast?latitude=${D.home.lat}&longitude=${D.home.lng}&current=temperature_2m,wind_speed_10m,cloud_cover,pressure_msl&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=America%2FLos_Angeles`)
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(j => {
      const c = j.current || {};
      now.t = c.temperature_2m; now.w = c.wind_speed_10m; now.c = c.cloud_cover; now.p = c.pressure_msl;
      for (const k in fmt) if (now[k] != null) root.querySelector(`[data-now="${k}"]`).textContent = fmt[k](now[k]);
    })
    .catch(() => { root.querySelector('.fft-now').insertAdjacentHTML('afterend', '<p class="fft-note">Live weather is unavailable right now, so this is based on the month alone.</p>'); })
    .finally(() => recommend());

  root.querySelector('form').addEventListener('submit', recommend);

  // map
  let markers = {};
  function highlight(ids) {
    Object.entries(markers).forEach(([id, m]) => m.setStyle(ids.includes(id) ? { radius: 9, fillOpacity: 1, weight: 2 } : { radius: 6, fillOpacity: .75, weight: 1.5 }));
  }
  function initMap() {
    const el = document.getElementById('fft-map');
    if (!window.L || !el) { if (el) el.innerHTML = '<ul class="fft-list">' + D.waters.map(w => `<li><a href="${w.url}">${esc(w.name)}</a></li>`).join('') + '</ul>'; return; }
    const map = L.map(el, { scrollWheelZoom: false, zoomControl: true, attributionControl: true }).setView([D.home.lat - 0.12, D.home.lng + 0.12], 9);
    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 13, className: 'fft-relief', attribution: 'Relief &copy; Esri; labels &copy; Esri, HERE, Garmin, OpenStreetMap contributors'
    }).addTo(map);
    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', { maxZoom: 13, opacity: .8 }).addTo(map);
    L.circle([D.home.lat, D.home.lng], { radius: 96560, color: '#d9b27a', weight: 1, opacity: .45, fill: false, dashArray: '2 6', interactive: false }).addTo(map);
    L.circleMarker([D.home.lat, D.home.lng], { radius: 5, color: '#f1efe8', fillColor: '#f1efe8', fillOpacity: 1, weight: 0 })
      .addTo(map).bindTooltip('The chalet', { direction: 'top', className: 'fft-tip' });
    D.waters.forEach(w => {
      const m = L.circleMarker([w.lat, w.lng], { radius: 6, color: '#18241d', weight: 1.5, fillColor: '#d9b27a', fillOpacity: .75 })
        .addTo(map).bindTooltip(w.name, { direction: 'top', className: 'fft-tip' });
      m.on('click', () => { location.href = w.url; });
      markers[w.id] = m;
    });
    map.fitBounds(L.latLngBounds(D.waters.map(w => [w.lat, w.lng]).concat([[D.home.lat, D.home.lng]])).pad(0.08), { maxZoom: 9 });
  }
  if (window.L) initMap(); else window.addEventListener('load', initMap);
})();
