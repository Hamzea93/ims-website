(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  // On touch / narrow screens the Services item opens its sub-menu on first tap.
  var sub = document.querySelector('.has-sub');
  if (sub) {
    var link = sub.querySelector(':scope > a');
    link.addEventListener('click', function (e) {
      if (window.matchMedia('(max-width: 820px)').matches && !sub.classList.contains('open')) {
        e.preventDefault();
        sub.classList.add('open');
      }
    });
    sub.addEventListener('keydown', function (e) { if (e.key === 'Escape') sub.classList.remove('open'); });
  }
})();

// Contact page: a service page's call-to-action passes ?service=<slug>; label the enquiry and pre-fill the e-mail subject.
(function () {
  var topic = document.getElementById('enquiry-topic');
  var titles = window.__SERVICE_TITLES__;
  if (!topic || !titles) return;
  var slug = new URLSearchParams(location.search).get('service');
  var title = slug && titles[slug];
  if (!title) return;
  topic.querySelector('strong').textContent = title;
  topic.hidden = false;
  document.querySelectorAll('a[href^="mailto:"]').forEach(function (a) {
    var href = a.getAttribute('href').split('?')[0];
    a.setAttribute('href', href + '?subject=' + encodeURIComponent('IMS enquiry: ' + title));
  });
})();
