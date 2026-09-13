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
