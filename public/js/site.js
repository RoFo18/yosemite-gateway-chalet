(function () {
  var root = document.documentElement, body = document.body;

  // Chat: nothing loads until someone reaches for it
  var chatReady = null;
  function loadChat() {
    if (chatReady) return chatReady;
    var v = (document.querySelector('[data-chat-open][data-v]') || {}).getAttribute ? document.querySelector('[data-chat-open][data-v]').getAttribute('data-v') : '';
    chatReady = new Promise(function (res, rej) {
      var l = document.createElement('link'); l.rel = 'stylesheet'; l.href = '/css/chat.css?v=' + v; document.head.appendChild(l);
      var s = document.createElement('script'); s.src = '/js/chat.js?v=' + v; s.onload = res; s.onerror = rej; document.head.appendChild(s);
    });
    return chatReady;
  }
  document.querySelectorAll('[data-chat-open]').forEach(function (b) {
    b.addEventListener('pointerenter', loadChat, { once: true });
    b.addEventListener('touchstart', loadChat, { once: true, passive: true });
    b.addEventListener('click', function () { loadChat().then(function () { window.YGCChat && window.YGCChat.open(); }); });
  });
  try { if (sessionStorage.getItem('ygc-chat-open') === '1') loadChat().then(function () { window.YGCChat && window.YGCChat.open(true); }); } catch (e) {}

  // Inquiry form: accept dates and guests from a link (the chat builds these)
  (function () {
    var f = document.querySelector('form.inquiry'); if (!f) return;
    var q = new URLSearchParams(location.search), set = function (id, v) { var el = f.querySelector(id); if (el && v) { el.value = v; el.dispatchEvent(new Event('change', { bubbles: true })); } };
    if (/^\d{4}-\d{2}-\d{2}$/.test(q.get('arrival') || '')) set('#arrival', q.get('arrival'));
    if (/^\d{4}-\d{2}-\d{2}$/.test(q.get('departure') || '')) set('#departure', q.get('departure'));
    if (/^[1-8]$/.test(q.get('guests') || '')) set('#guests', q.get('guests'));
    if (q.get('message')) set('#message', q.get('message').slice(0, 600));
    if (q.get('arrival')) { var h = document.getElementById('inquiry-form'); if (h) setTimeout(function () { h.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 300); }
  })();

  // Share and copy buttons (thank-you page)
  document.querySelectorAll('[data-share]').forEach(function (b) {
    if (!navigator.share) { b.hidden = true; return; }
    b.addEventListener('click', function () {
      navigator.share({ title: 'Yosemite Gateway Chalet', text: b.getAttribute('data-share-text'), url: b.getAttribute('data-share-url') }).catch(function () {});
    });
  });
  document.querySelectorAll('[data-copy]').forEach(function (b) {
    b.addEventListener('click', function () {
      var url = b.getAttribute('data-copy'), label = b.textContent;
      var done = function () { b.textContent = 'Link copied'; setTimeout(function () { b.textContent = label; }, 2200); };
      if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, function () { window.prompt('Copy this link', url); });
      else window.prompt('Copy this link', url);
    });
  });

  // Masthead turns solid once the hero scrolls away
  var mast = document.querySelector('[data-masthead]');
  var bar = document.querySelector('.mobile-bar');
  function onScroll() {
    var y = window.scrollY || 0;
    if (mast && body.classList.contains('has-hero')) mast.classList.toggle('solid', y > 80);
    if (bar) bar.classList.toggle('show', y > 520);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Full-screen menu
  var toggle = document.querySelector('.menu-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = body.classList.toggle('menu-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.querySelector('.mt-label').textContent = open ? 'Close' : 'Menu';
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && body.classList.contains('menu-open')) toggle.click();
    });
  }

  // Film bands: load the Vimeo player only when someone presses play
  document.querySelectorAll('.film-frame[data-vimeo], .film-frame[data-youtube]').forEach(function (b) {
    b.addEventListener('click', function () {
      if (b.classList.contains('playing')) return;
      var f = document.createElement('iframe');
      var yt = b.getAttribute('data-youtube');
      f.src = yt ? 'https://www.youtube-nocookie.com/embed/' + yt + '?autoplay=1&rel=0&modestbranding=1'
                 : 'https://player.vimeo.com/video/' + b.getAttribute('data-vimeo') + '?autoplay=1&dnt=1&byline=0&portrait=0&title=0';
      f.title = b.getAttribute('aria-label').replace(/^Play /, '');
      f.allow = 'autoplay; fullscreen; picture-in-picture';
      f.allowFullscreen = true;
      b.classList.add('playing');
      b.removeAttribute('aria-label');
      b.innerHTML = '';
      b.appendChild(f);
    });
  });

  // Living header: a silent loop behind the title, on screens wide enough, when motion and data are welcome
  document.querySelectorAll('.ph-video[data-src]').forEach(function (v) {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var save = navigator.connection && navigator.connection.saveData;
    if (reduce || save || !window.matchMedia('(min-width: 760px)').matches) return;
    v.src = v.getAttribute('data-src');
    v.addEventListener('playing', function () { v.classList.add('on'); }, { once: true });
    var p = v.play(); if (p && p.catch) p.catch(function () {});
  });

  // The film: plays in a dialog with sound, and ends on a way to book
  var dlg = document.querySelector('.film-dlg'), fb = document.querySelector('.ph-film');
  if (dlg && fb && dlg.showModal) {
    var fv = dlg.querySelector('.fd-video'), end = dlg.querySelector('.fd-end');
    var shut = function () { fv.pause(); dlg.close(); };
    fb.addEventListener('click', function () {
      if (!fv.src) fv.src = fb.getAttribute('data-film');
      end.hidden = true; dlg.showModal(); fv.currentTime = 0;
      var p = fv.play(); if (p && p.catch) p.catch(function () {});
    });
    fv.addEventListener('ended', function () { end.hidden = false; });
    dlg.querySelector('.fd-again').addEventListener('click', function () { end.hidden = true; fv.currentTime = 0; fv.play(); });
    dlg.querySelector('.fd-x').addEventListener('click', shut);
    dlg.addEventListener('click', function (e) { if (e.target === dlg) shut(); });
    dlg.addEventListener('cancel', function () { fv.pause(); });
  }

  // Carousels
  document.querySelectorAll('[data-carousel]').forEach(function (c) {
    var track = c.querySelector('[data-track]'), slides = track.children, n = slides.length;
    var prev = c.querySelector('[data-prev]'), next = c.querySelector('[data-next]'), idxEl = c.querySelector('[data-idx]');
    var thumbs = c.querySelectorAll('.car-thumb'), tabs = c.querySelectorAll('.st-tab'), cur = 0;
    var lock = 0;
    function go(i) { i = Math.max(0, Math.min(n - 1, i)); lock = Date.now() + 700; mark(i); track.scrollTo({ left: slides[i].offsetLeft - track.offsetLeft, behavior: 'smooth' }); }
    function mark(i) {
      cur = i; if (idxEl) idxEl.textContent = i + 1;
      if (prev) prev.disabled = i === 0; if (next) next.disabled = i === n - 1;
      thumbs.forEach(function (t, k) { t.classList.toggle('is-on', k === i); if (k === i) { t.setAttribute('aria-current', 'true'); if (t.parentNode.scrollWidth > t.parentNode.clientWidth) t.parentNode.scrollTo({ left: t.offsetLeft - t.parentNode.clientWidth / 2 + t.clientWidth / 2, behavior: 'smooth' }); } else t.removeAttribute('aria-current'); });
      var ch = slides[i] && slides[i].getAttribute('data-chapter');
      tabs.forEach(function (t) { var on = t.textContent === ch; t.classList.toggle('is-on', on); if (on) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current'); });
    }
    var tick;
    track.addEventListener('scroll', function () {
      clearTimeout(tick);
      tick = setTimeout(function () { if (Date.now() > lock) mark(Math.round(track.scrollLeft / track.clientWidth)); }, 80);
    }, { passive: true });
    if (prev) prev.addEventListener('click', function () { go(cur - 1); });
    if (next) next.addEventListener('click', function () { go(cur + 1); });
    thumbs.forEach(function (t) { t.addEventListener('click', function () { go(+t.getAttribute('data-go')); }); });
    tabs.forEach(function (t) { t.addEventListener('click', function () { go(+t.getAttribute('data-go')); }); });
    c.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1); }
    });
    mark(0);
  });

  // Lightbox for galleries
  var lb = document.getElementById('lightbox');
  if (lb && lb.showModal) {
    var im = lb.querySelector('img');
    document.querySelectorAll('[data-lightbox]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        im.src = a.getAttribute('href');
        var i = a.querySelector('img');
        im.alt = i ? i.alt : '';
        lb.showModal();
      });
    });
    lb.querySelector('.lb-close').addEventListener('click', function () { lb.close(); });
    lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });
  }

  // Gentle reveal on scroll. Content stays visible without JS or with reduced motion.
  var motionOK = window.matchMedia && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (motionOK && 'IntersectionObserver' in window) {
    var targets = document.querySelectorAll('.feature, .suite, .season, .glist li, .rel-card, .statement, .spec');
    targets.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top > window.innerHeight) el.setAttribute('data-reveal', '');
    });
    root.classList.add('reveal-ready');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('[data-reveal]').forEach(function (el) { io.observe(el); });
  }

  // Inquiry form: dates must make sense before Netlify receives it
  var form = document.querySelector('form.inquiry');
  if (form) {
    var a = form.querySelector('#arrival'), d = form.querySelector('#departure'), msg = form.querySelector('#date-error');
    var today = new Date(); today.setHours(0, 0, 0, 0);
    var iso = today.toISOString().slice(0, 10);
    if (a) a.min = iso;
    if (d) d.min = iso;
    if (a && d) a.addEventListener('change', function () {
      if (!a.value) return;
      d.min = a.value;
      if (!d.value || d.value <= a.value) {
        var w = new Date(a.value + 'T12:00:00'); w.setDate(w.getDate() + 7);
        d.value = w.toISOString().slice(0, 10);
      }
    });
    form.addEventListener('submit', function (e) {
      if (a && d && a.value && d.value && d.value <= a.value) {
        e.preventDefault();
        msg.hidden = false;
        d.focus();
      } else if (msg) { msg.hidden = true; }
    });
  }

  // Live availability calendar (Inquire page). Booked nights come from /api/availability,
  // which merges the chalet's Airbnb and VRBO calendars.
  var cal = document.querySelector('[data-cal]');
  if (cal) (function () {
    var monthsEl = cal.querySelector('[data-cal-months]');
    var statusEl = document.querySelector('[data-cal-status]');
    var sumEl = document.querySelector('[data-cal-summary] .cs-value');
    var goBtn = document.querySelector('[data-cal-go]');
    var clearBtn = document.querySelector('[data-cal-clear]');
    var booked = {};               // 'YYYY-MM-DD' -> true when that night is taken
    var start = null, end = null, hover = null;
    var MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
    var DAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    var LONG_DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

    function pad(n) { return (n < 10 ? '0' : '') + n; }
    function key(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
    function parse(k) { var p = k.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
    function addDays(k, n) { var d = parse(k); d.setDate(d.getDate() + n); return key(d); }
    function nightsBetween(a, b) { return Math.round((parse(b) - parse(a)) / 864e5); }
    function pretty(k) { var d = parse(k); return LONG_DAYS[d.getDay()].slice(0, 3) + ', ' + MONTHS[d.getMonth()].slice(0, 3) + ' ' + d.getDate(); }
    var todayD = new Date(); todayD.setHours(0, 0, 0, 0);
    var today = key(todayD);
    var view = new Date(todayD.getFullYear(), todayD.getMonth(), 1);
    var lastMonth = new Date(todayD.getFullYear(), todayD.getMonth() + 18, 1);

    function rangeClear(a, b) {       // every night from a up to (not including) b is open
      for (var k = a; k < b; k = addDays(k, 1)) if (booked[k]) return false;
      return true;
    }
    function perView() { return window.matchMedia('(min-width: 760px)').matches ? 2 : 1; }

    function render() {
      var n = perView(), html = '';
      for (var m = 0; m < n; m++) {
        var first = new Date(view.getFullYear(), view.getMonth() + m, 1);
        var days = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate();
        html += '<div class="cal-month"><p class="cal-title">' + MONTHS[first.getMonth()] + ' <span>' + first.getFullYear() + '</span></p>';
        html += '<div class="cal-grid" role="grid">';
        for (var w = 0; w < 7; w++) html += '<span class="cal-dow" aria-hidden="true">' + DAYS[w].slice(0, 2) + '</span>';
        for (var b = 0; b < first.getDay(); b++) html += '<span class="cal-pad"></span>';
        for (var d = 1; d <= days; d++) {
          var k = key(new Date(first.getFullYear(), first.getMonth(), d));
          var cls = ['cal-day'], label = LONG_DAYS[parse(k).getDay()] + ', ' + MONTHS[first.getMonth()] + ' ' + d;
          var past = k < today, taken = !!booked[k], disabled = past;
          var canCheckout = start && !end && k > start && rangeClear(start, k);
          if (taken) { cls.push('is-booked'); label += ', booked'; if (!canCheckout) disabled = true; else label += ', available for departure'; }
          else if (!past) label += ', open';
          if (past) cls.push('is-past');
          if (k === today) cls.push('is-today');
          var rangeEnd = end || (start && hover && hover > start && rangeClear(start, hover) ? hover : null);
          if (start && k === start) cls.push('is-start');
          if (rangeEnd && k === rangeEnd) cls.push('is-end');
          if (start && rangeEnd && k > start && k < rangeEnd) cls.push('in-range');
          if (start && !end && k > start && !canCheckout) cls.push('is-blocked');
          html += '<button type="button" class="' + cls.join(' ') + '" data-day="' + k + '"' + (disabled ? ' disabled' : '') +
                  ' aria-label="' + label + '"' + (k === start || k === end ? ' aria-pressed="true"' : '') + '>' + d + '</button>';
        }
        html += '</div></div>';
      }
      monthsEl.innerHTML = html;
      cal.querySelector('[data-cal-prev]').disabled = view <= new Date(todayD.getFullYear(), todayD.getMonth(), 1);
      cal.querySelector('[data-cal-next]').disabled = new Date(view.getFullYear(), view.getMonth() + n, 1) > lastMonth;
      summary();
    }

    function summary() {
      if (start && end) {
        var n = nightsBetween(start, end);
        sumEl.textContent = pretty(start) + '  to  ' + pretty(end) + '  ·  ' + n + (n === 1 ? ' night' : ' nights');
      } else if (start) sumEl.textContent = 'Arrive ' + pretty(start) + '. Now choose a departure day.';
      else sumEl.textContent = 'Choose an arrival day';
      goBtn.disabled = !(start && end);
      clearBtn.hidden = !start;
    }

    monthsEl.addEventListener('click', function (e) {
      var b = e.target.closest('[data-day]'); if (!b || b.disabled) return;
      var k = b.getAttribute('data-day');
      if (!start || end || k <= start) { if (booked[k]) return; start = k; end = null; }
      else if (rangeClear(start, k)) end = k;
      else if (!booked[k]) { start = k; end = null; }
      render();
      var again = monthsEl.querySelector('[data-day="' + k + '"]'); if (again) again.focus();
    });
    monthsEl.addEventListener('mouseover', function (e) {
      var b = e.target.closest('[data-day]');
      if (!start || end || !b) return;
      var k = b.getAttribute('data-day');
      if (k !== hover) { hover = k; render(); }
    });
    cal.querySelector('[data-cal-prev]').addEventListener('click', function () { view = new Date(view.getFullYear(), view.getMonth() - 1, 1); render(); });
    cal.querySelector('[data-cal-next]').addEventListener('click', function () { view = new Date(view.getFullYear(), view.getMonth() + 1, 1); render(); });
    clearBtn.addEventListener('click', function () { start = end = hover = null; render(); });
    goBtn.addEventListener('click', function () {
      var a = document.getElementById('arrival'), d = document.getElementById('departure');
      if (a && d) {
        a.value = start; d.value = end;
        a.dispatchEvent(new Event('change', { bubbles: true }));
        d.dispatchEvent(new Event('change', { bubbles: true }));
      }
      var h = document.getElementById('inquiry-form');
      if (h) h.scrollIntoView({ behavior: 'smooth', block: 'start' });
      var f = document.getElementById('first');
      if (f) setTimeout(function () { f.focus({ preventScroll: true }); }, 450);
    });
    var lastN = perView();
    window.addEventListener('resize', function () { if (perView() !== lastN) { lastN = perView(); render(); } });

    render();
    fetch('/api/availability', { headers: { accept: 'application/json' } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) {
        (data.booked || []).forEach(function (r) { for (var k = r[0]; k < r[1]; k = addDays(k, 1)) booked[k] = true; });
        if (start && booked[start]) start = end = null;
        if (start && end && !rangeClear(start, end)) end = null;
        render();
        var mins = Math.max(0, Math.round((Date.now() - new Date(data.updated)) / 60000));
        statusEl.textContent = 'Synced with our VRBO and Airbnb calendars ' + (mins < 2 ? 'just now' : mins + ' minutes ago') +
          '. A very recent booking can take a little while to appear, so we confirm every date in our reply.';
        statusEl.classList.add('ok');
      })
      .catch(function () {
        statusEl.textContent = 'Live availability is not loading right now. Choose your dates anyway and we will confirm them within a day.';
      });
  })();
})();
