"""Bundle the generated site into ONE self-contained HTML file.

    python tools/build_standalone.py            -> dist/IMS_Website.html

Every page becomes a hidden section; a tiny router shows one at a time from the
URL hash, so links, the services menu and prev/next keep working offline.
CSS and JS are inlined; every image is embedded once as a data URI and assigned
to <img> tags at load time (so repeated icons do not bloat the file).
"""
import base64
import html as html_mod
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "dist")
OUT = os.path.join(OUT_DIR, "IMS_Website.html")
os.makedirs(OUT_DIR, exist_ok=True)

with open(os.path.join(ROOT, "content.json"), encoding="utf-8") as f:
    C = json.load(f)
SITE = C["site"]

PAGES = [("home", "index.html"), ("services", "services/index.html")]
PAGES += [(f"svc-{s['slug']}", f"services/{s['slug']}.html") for s in C["services"]]
PAGES += [("contact", "contact.html")]


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def link_to_hash(href, page_dir):
    """Map a relative site link to an in-file hash."""
    h = href.strip()
    if h.startswith(("http", "mailto:", "tel:", "#")):
        return h if not h.startswith("#") else ("#about" if h == "#about" else "#home")
    anchor = ""
    if "#" in h:
        h, anchor = h.split("#", 1)
    h = h.replace("../", "")
    if page_dir == "services" and not h.startswith("services/") and h not in ("index.html", "contact.html", ""):
        h = "services/" + h  # sibling service page referenced without folder
    if h in ("", "index.html"):
        return "#about" if anchor == "about" else "#home"
    if h == "contact.html":
        return "#contact"
    if h == "services/index.html":
        return "#services"
    m = re.match(r"services/([a-z0-9-]+)\.html$", h)
    if m:
        return f"#svc-{m.group(1)}"
    return "#home"


IMG = {}   # relative asset path -> data URI


def data_uri(rel):
    rel = rel.replace("../", "")
    if rel not in IMG:
        p = os.path.join(ROOT, rel)
        ext = os.path.splitext(p)[1].lower()
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".svg": "image/svg+xml"}[ext]
        with open(p, "rb") as f:
            IMG[rel] = f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")
    return rel


def rewrite(html, page_dir):
    html = re.sub(r'href="([^"]+)"', lambda m: f'href="{link_to_hash(m.group(1), page_dir)}"', html)
    html = re.sub(r'src="([^"]*assets/[^"]+)"', lambda m: f'src="" data-img="{data_uri(m.group(1))}"', html)
    html = re.sub(r"style=\"background-image:url\('([^']*assets/[^']+)'\)\"", lambda m: f'data-bg="{data_uri(m.group(1))}"', html)
    return html


def between(s, start, end):
    i = s.index(start)
    j = s.index(end, i) + len(end)
    return s[i:j]


home = read("index.html")
header = between(home, '<header class="site-header">', "</header>")
footer = between(home, '<footer class="site-footer">', "</footer>")
header = rewrite(header, "")
footer = rewrite(footer, "")
css = read("assets/css/site.css")
titles = {}
sections = []
for pid, path in PAGES:
    src = read(path)
    titles[pid] = html_mod.unescape(re.search(r"<title>(.*?)</title>", src, re.S).group(1))
    main = between(src, '<main id="main">', "</main>")
    main = main[len('<main id="main">'):-len("</main>")]
    page_dir = "services" if path.startswith("services/") else ""
    sections.append(f'<section class="page" id="page-{pid}" hidden>{rewrite(main, page_dir)}</section>')

site_js = read("assets/js/site.js")
router_js = """
(function(){
  var IMG = window.__IMG__;
  document.querySelectorAll('img[data-img]').forEach(function(i){ i.src = IMG[i.getAttribute('data-img')] || ''; });
  document.querySelectorAll('[data-bg]').forEach(function(e){ e.style.backgroundImage = 'url(' + IMG[e.getAttribute('data-bg')] + ')'; });
  var titles = window.__TITLES__;
  function show(){
    var h = (location.hash || '#home').slice(1);
    var target = h === 'about' ? 'home' : h;
    var el = document.getElementById('page-' + target) ? target : 'home';
    document.querySelectorAll('.page').forEach(function(p){ p.hidden = (p.id !== 'page-' + el); });
    document.title = titles[el] || document.title;
    document.querySelectorAll('.nav > ul > li > a').forEach(function(a){
      var href = a.getAttribute('href');
      a.classList.toggle('active', href === '#' + el || (el.indexOf('svc-') === 0 && href === '#services'));
    });
    var nav = document.getElementById('nav'); if (nav) nav.classList.remove('open');
    var sub = document.querySelector('.has-sub'); if (sub) sub.classList.remove('open');
    if (h === 'about') { var ab = document.getElementById('about'); if (ab) window.scrollTo(0, ab.getBoundingClientRect().top + window.scrollY - 84); }
    else window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', show);
  show();
})();
"""

doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_mod.escape(titles['home'])}</title>
<meta name="description" content="{SITE['description']}">
<link rel="icon" href="{{FAVICON}}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
{css}
.page[hidden] {{ display: none; }}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{header}
<main id="main">
{''.join(sections)}
</main>
{footer}
<script>window.__TITLES__ = {json.dumps(titles)};</script>
<script>window.__IMG__ = {json.dumps(IMG)};</script>
<script>{site_js}</script>
<script>{router_js}</script>
</body>
</html>
"""
data_uri("assets/brand/favicon-32.png")
doc = doc.replace("{FAVICON}", IMG["assets/brand/favicon-32.png"])
# the favicon call above added it to IMG after the map was serialised; re-serialise
doc = doc.replace(f"<script>window.__IMG__ = {json.dumps({k: v for k, v in IMG.items() if k != 'assets/brand/favicon-32.png'})};</script>",
                  f"<script>window.__IMG__ = {json.dumps(IMG)};</script>")
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(doc)
print("wrote", OUT, f"{os.path.getsize(OUT)/1e6:.1f} MB", "| pages:", len(PAGES), "| images embedded:", len(IMG))
