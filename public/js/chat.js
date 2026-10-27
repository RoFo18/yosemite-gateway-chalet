/* The chalet's chat. Loaded on demand by site.js the first time someone reaches for the Ask button.
   Talks to /api/chat (a Netlify function), streams the answer in, and keeps the conversation
   in this browser tab only (sessionStorage) so it survives moving between pages. */
(function () {
  if (window.YGCChat) return;
  var KEY = 'ygc-chat', OPEN = 'ygc-chat-open';
  var GREETING = "Ask me about the place, the canyon, or what's open. Got dates in mind? I'll check the calendar and hand you the form.";
  var CHIPS = ['Is it open over Christmas?', 'Skiing with kids?', 'Can we bring the dog?', 'How far to Yosemite?'];
  var store = {
    get: function (k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  };
  var history = [];
  try { history = JSON.parse(store.get(KEY) || '[]'); } catch (e) { history = []; }
  var mobile = function () { return window.matchMedia('(max-width: 760px)').matches; };
  var lastFocus = null, busy = false;

  // ---------- tiny, safe markdown: escape first, then links, bold and lists
  function esc(s) { return s.replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function md(text) {
    var out = [], list = null;
    esc(text).split(/\n+/).forEach(function (line) {
      line = line.replace(/\[([^\]]+)\]\(((?:\/|https:\/\/)[^)\s]*)\)/g, function (_, t, u) {
        var ext = /^https:/.test(u) && !/^https:\/\/(www\.)?yosemitechalet\.us/.test(u);
        var cta = /^\/inquire\//.test(u) ? ' class="yc-cta"' : '';
        return '<a href="' + u + '"' + cta + (ext ? ' target="_blank" rel="noopener"' : '') + '>' + t + '</a>';
      }).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      var li = /^\s*[-*]\s+(.*)/.exec(line);
      if (li) { if (!list) { list = []; out.push(list); } list.push('<li>' + li[1] + '</li>'); }
      else if (line.trim()) { list = null; out.push('<p>' + line + '</p>'); }
    });
    return out.map(function (x) { return Array.isArray(x) ? '<ul>' + x.join('') + '</ul>' : x; }).join('');
  }

  // ---------- build the panel once
  var el = document.createElement('section');
  el.className = 'ygc-chat'; el.hidden = true;
  el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'false'); el.setAttribute('aria-labelledby', 'yc-title');
  el.innerHTML =
    '<header class="yc-head"><div><p class="yc-title" id="yc-title">Ask about the chalet</p><p class="yc-sub">The house, the canyon, your dates</p></div>' +
    '<button class="yc-x" type="button" aria-label="Close chat"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg></button></header>' +
    '<div class="yc-log" aria-live="polite"></div>' +
    '<div class="yc-chips"></div>' +
    '<form class="yc-form"><label class="sr-only" for="yc-in">Your question</label><textarea class="yc-in" id="yc-in" rows="1" maxlength="600" placeholder="Ask anything about your stay"></textarea>' +
    '<button class="yc-send" type="submit" aria-label="Send"><svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button></form>' +
    '<p class="yc-foot">Answers come from the chalet’s own pages. Only the owners confirm a booking.</p>';
  document.body.appendChild(el);
  var log = el.querySelector('.yc-log'), chips = el.querySelector('.yc-chips'), form = el.querySelector('.yc-form'),
      input = el.querySelector('.yc-in'), send = el.querySelector('.yc-send');

  function bubble(role, html) {
    var d = document.createElement('div');
    d.className = 'yc-msg ' + (role === 'user' ? 'yc-me' : 'yc-bot');
    d.innerHTML = html; log.appendChild(d); log.scrollTop = log.scrollHeight; return d;
  }
  function render() {
    log.innerHTML = '';
    bubble('assistant', md(GREETING));
    history.forEach(function (m) { bubble(m.role, m.role === 'user' ? '<p>' + esc(m.content) + '</p>' : md(m.content)); });
    chips.innerHTML = '';
    if (!history.length) CHIPS.forEach(function (c) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'yc-chip'; b.textContent = c;
      b.addEventListener('click', function () { ask(c); }); chips.appendChild(b);
    });
  }
  function save() { store.set(KEY, JSON.stringify(history.slice(-16))); }

  // ---------- talk to the function, stream the answer in
  function ask(q) {
    q = (q || '').trim().slice(0, 600);
    if (!q || busy) return;
    busy = true; send.disabled = true; chips.innerHTML = '';
    history.push({ role: 'user', content: q }); save();
    bubble('user', '<p>' + esc(q) + '</p>');
    var out = bubble('assistant', '<span class="yc-typing" aria-label="Thinking"><i></i><i></i><i></i></span>'), text = '';
    var done = function (fallback) {
      if (!text) text = fallback || "Line's down for a minute. The [inquiry form](/inquire/) still works, and the owners answer within a day.";
      out.innerHTML = md(text);
      history.push({ role: 'assistant', content: text }); save();
      busy = false; send.disabled = false; log.scrollTop = log.scrollHeight;
    };
    fetch('/api/chat', {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ messages: history.slice(-12), page: location.pathname })
    }).then(function (r) {
      if (!r.ok || !r.body) {
        return r.json().catch(function () { return {}; }).then(function (j) { done(j && j.message); });
      }
      var reader = r.body.getReader(), dec = new TextDecoder(), buf = '';
      function pump() {
        return reader.read().then(function (res) {
          if (res.done) return done();
          buf += dec.decode(res.value, { stream: true });
          var parts = buf.split('\n\n'); buf = parts.pop();
          parts.forEach(function (p) {
            var line = p.replace(/^data: /, '');
            try { var j = JSON.parse(line); if (j.t) { text += j.t; out.innerHTML = md(text); log.scrollTop = log.scrollHeight; } } catch (e) {}
          });
          return pump();
        });
      }
      return pump();
    }).catch(function () { done(); });
  }

  form.addEventListener('submit', function (e) { e.preventDefault(); var v = input.value; input.value = ''; input.style.height = ''; ask(v); });
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit')); } });
  input.addEventListener('input', function () { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 120) + 'px'; });
  el.querySelector('.yc-x').addEventListener('click', close);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !el.hidden) close(); });
  // On a phone the chat covers the page, so step aside when a link inside it is followed
  log.addEventListener('click', function (e) { var a = e.target.closest('a'); if (a && mobile() && !a.target) store.set(OPEN, '0'); });

  function open(restoring) {
    if (!el.hidden) return;
    if (restoring && mobile()) return;
    lastFocus = document.activeElement;
    render(); el.hidden = false;
    document.documentElement.classList.add('chat-open');
    requestAnimationFrame(function () { el.classList.add('on'); });
    store.set(OPEN, '1');
    if (!restoring && !mobile()) input.focus();
  }
  function close() {
    el.classList.remove('on'); document.documentElement.classList.remove('chat-open');
    store.set(OPEN, '0');
    setTimeout(function () { el.hidden = true; }, 250);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  window.YGCChat = { open: open, close: close };
})();
