(function () {
  var root = document.documentElement, body = document.body;

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
    if (a && d) a.addEventListener('change', function () { if (a.value) d.min = a.value; });
    form.addEventListener('submit', function (e) {
      if (a && d && a.value && d.value && d.value <= a.value) {
        e.preventDefault();
        msg.hidden = false;
        d.focus();
      } else if (msg) { msg.hidden = true; }
    });
  }
})();
