"""Static site builder for the IMS website.

    python build.py

Reads content.json and writes index.html, services/*.html, contact.html,
404.html, sitemap.xml and robots.txt next to this file. No dependencies.
"""
import html
import json
import os
import re
import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT, "content.json"), encoding="utf-8") as f:
    C = json.load(f)
SITE = C["site"]
SERVICES = C["services"]
YEAR = datetime.date.today().year


# ----------------------------------------------------------------- helpers
def esc(s):
    return html.escape(s, quote=True)


def md(s):
    """Escape then turn **x** into <strong>x</strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(s))


def plain(s):
    return s.replace("**", "")


CHEVRON_SVG = (
    '<svg class="chev" viewBox="0 0 60 40" aria-hidden="true">'
    '<path d="M0 0h14l16 20-16 20H0l16-20z" fill="#1CB5F4"/>'
    '<path d="M22 0h14l16 20-16 20H22l16-20z" fill="#A7ADB4"/></svg>'
)
ARROW = '<span class="arr" aria-hidden="true">&rsaquo;&rsaquo;</span>'


def icon(h, tone, rel, alt=""):
    return f'<img class="ico ico-{tone}" src="{rel}assets/icons/{h}-{tone}.png" alt="{esc(alt)}" loading="lazy" width="64" height="64">'


def head(title, desc, rel, path, og_img=None):
    canonical = SITE["domain"].rstrip("/") + "/" + path
    og_img = og_img or "assets/brand/ims-logo.png"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE['full_name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE['domain']}/{og_img}">
<meta name="theme-color" content="#003E7E">
<link rel="icon" type="image/png" sizes="32x32" href="{rel}assets/brand/favicon-32.png">
<link rel="icon" type="image/png" sizes="64x64" href="{rel}assets/brand/favicon-64.png">
<link rel="apple-touch-icon" href="{rel}assets/brand/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(rel, active):
    items = "".join(
        f'<li><a href="{rel}services/{s["slug"]}.html"><span class="n">{s["num"]:02d}</span>{esc(s["short"])}</a></li>'
        for s in SERVICES
    )

    def cls(name):
        return ' class="active"' if name == active else ""

    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{rel}index.html" aria-label="{esc(SITE['full_name'])} home">
      <img src="{rel}assets/brand/ims-lockup.png" alt="{esc(SITE['full_name'])}" width="1255" height="456">
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav" aria-label="Menu"><span></span><span></span><span></span></button>
    <nav id="nav" class="nav">
      <ul>
        <li><a href="{rel}index.html"{cls('home')}>Home</a></li>
        <li class="has-sub"><a href="{rel}services/index.html"{cls('services')} aria-haspopup="true">Services</a>
          <ul class="sub">{items}<li class="all"><a href="{rel}services/index.html">All services {ARROW}</a></li></ul>
        </li>
        <li><a href="{rel}index.html#about"{cls('about')}>About</a></li>
        <li class="cta"><a class="btn btn-primary" href="{rel}contact.html">Contact us {ARROW}</a></li>
      </ul>
    </nav>
  </div>
</header>
<main id="main">
"""


def footer(rel):
    svc = "".join(f'<li><a href="{rel}services/{s["slug"]}.html">{esc(s["short"])}</a></li>' for s in SERVICES)
    addr = "<br>".join(esc(a) for a in SITE["address_lines"])
    phone = f'<li><a href="tel:{esc(SITE["phone"])}">{esc(SITE["phone"])}</a></li>' if SITE.get("phone") else ""
    person_li = ""
    return f"""</main>
<footer class="site-footer">
  <div class="wrap grid-4">
    <div class="f-brand">
      <img src="{rel}assets/brand/ims-logo-white.png" alt="{esc(SITE['full_name'])} — {esc(SITE['slogan'])}" width="220" height="100">
      <p class="tag">{esc(SITE['taglines']['people'])}</p>
    </div>
    <div>
      <h4>Services</h4>
      <ul class="f-links">{svc}</ul>
    </div>
    <div>
      <h4>Company</h4>
      <ul class="f-links">
        <li><a href="{rel}index.html#about">About IMS</a></li>
        <li><a href="{rel}services/index.html">Advanced Engineering Services</a></li>
        <li><a href="{rel}contact.html">Contact us</a></li>
      </ul>
    </div>
    <div>
      <h4>Contact</h4>
      <ul class="f-links">
        {person_li}
        <li><a href="mailto:{esc(SITE['email'])}">{esc(SITE['email'])}</a></li>
        {phone}
        <li>{addr}</li>
      </ul>
    </div>
  </div>
  <div class="wrap f-bottom">
    <span>{esc(SITE['taglines']['footer'])}</span>
    <span>&copy; {YEAR} {esc(SITE['full_name'])}. All rights reserved.</span>
  </div>
</footer>
<script src="{rel}assets/js/site.js"></script>
</body>
</html>
"""


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("wrote", path)


def kicker(text):
    return f'<p class="kicker">{esc(text)}</p>'


def service_card(s, rel):
    return f"""<a class="card svc" href="{rel}services/{s['slug']}.html">
  <div class="card-top"><span class="num">{s['num']:02d}</span>{icon(s['card_icon'], 'n', rel)}</div>
  <h3>{esc(s['title'])}</h3>
  <p>{esc(s['blurb'])}</p>
  <span class="more">Learn more {ARROW}</span>
</a>"""



CHIP_ICONS = {
    "gear": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>',
    "cube": '<svg viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7l7 4a2 2 0 0 0 2 0l7-4a2 2 0 0 0 1-1.7z"/><path d="M3.3 7 12 12l8.7-5M12 22V12"/></svg>',
    "bars": '<svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
    "monitor": '<svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4M7 12l3-3 3 2 4-4"/></svg>',
    "person": '<svg viewBox="0 0 24 24"><circle cx="12" cy="7" r="4"/><path d="M5.5 21a6.5 6.5 0 0 1 13 0"/></svg>',
    "nodes": '<svg viewBox="0 0 24 24"><circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="19" r="2.5"/><circle cx="19" cy="19" r="2.5"/><path d="M12 7.5v5M12 12.5 6.5 17M12 12.5l5.5 4.5"/></svg>',
    "layers": '<svg viewBox="0 0 24 24"><path d="m12 3 9 5-9 5-9-5 9-5z"/><path d="m3 13 9 5 9-5M3 18l9 5 9-5"/></svg>',
    "pin": '<svg viewBox="0 0 24 24"><path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "target": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/></svg>',
}
HERO_CHIPS = [
    ("gear", "Design", "services/advanced-manufacturing-engineering.html"),
    ("cube", "Simulate", "services/throughput-buffer-optimization.html"),
    ("bars", "Optimize", "services/continuous-improvement-processing.html"),
    ("monitor", "Digital twin", "services/machine-transfer-optimization-virtual-twin.html"),
    ("person", "Ergonomics", "services/ergonomics-simulation-human-factors.html"),
    ("nodes", "Process engineering", "services/advanced-manufacturing-engineering.html"),
]
HERO_TRUST = [
    ("layers", "7 core services", "End-to-end manufacturing expertise"),
    ("pin", "Saudi-based", "Proudly supporting Vision 2030"),
    ("target", "Concept to execution", "From idea to real-world impact"),
]


def hero_chips(rel):
    return "".join(f'<li><a href="{rel}{href}">{CHIP_ICONS[ico]}{esc(label)}</a></li>' for ico, label, href in HERO_CHIPS)


def hero_trust():
    return "".join(f'<li>{CHIP_ICONS[ico]}<div><strong>{esc(t)}</strong><span>{esc(d)}</span></div></li>' for ico, t, d in HERO_TRUST)


# ----------------------------------------------------------------- pages
def build_home():
    rel = ""
    T = SITE["taglines"]
    A = C["about"]
    chips = hero_chips(rel)
    trust = hero_trust()
    cards = "".join(service_card(s, rel) for s in SERVICES)
    about_ps = "".join(f"<p>{md(p)}</p>" for p in A["paragraphs"])
    body = f"""
<section class="hero hero-split">
  <div class="wrap hero-grid">
    <div class="hero-text">
      {kicker(T['hero_kicker'])}
      <h1>{T['hero_title_html']}</h1>
      <p class="lead">{esc(T['hero_lead'])}</p>
      <div class="actions">
        <a class="btn btn-primary" href="services/index.html">Explore services {ARROW}</a>
        <a class="btn btn-ghost" href="contact.html">Request consultation</a>
      </div>
      <ul class="chips" aria-label="Capabilities">{chips}</ul>
      <ul class="trust">{trust}</ul>
      <p class="think">{esc(SITE['slogan'])}</p>
    </div>
    <div class="hero-visual">
      <picture>
        <source srcset="assets/img/hero-composite.webp" type="image/webp">
        <img src="assets/img/hero-composite.jpg" alt="Robotic assembly cell with a production performance dashboard: design, simulate, optimize" width="1254" height="1254" fetchpriority="high">
      </picture>
    </div>
  </div>
</section>

<section id="about" class="about">
  <div class="wrap grid-2">
    <div>
      {kicker(A['kicker'])}
      <h2>{esc(A['heading'])}</h2>
      <p class="lead">{md(A['intro'])}</p>
      {about_ps}
    </div>
    <div class="about-media panel">
      <div class="chev-bg small" aria-hidden="true"><i class="b1"></i><i class="b2"></i></div>
      <img src="assets/img/ame-cell-3d.png" alt="3D model of a robotic assembly cell" width="640" height="470" loading="lazy">
    </div>
  </div>
</section>

<section id="services" class="services">
  <div class="wrap">
    <div class="sec-head">
      {kicker('Services')}
      <h2>{esc(A['services_heading'])}</h2>
      <p class="lead">{esc(A['services_lead'])}</p>
    </div>
    <div class="grid-3">{cards}</div>
  </div>
</section>

<section class="band band-navy">
  <div class="wrap grid-2 v-center">
    <div>
      <p class="kicker light">{esc(T['people'])}</p>
      <h2>Engineer the decision. De-risk the capital.</h2>
      <p class="lead">Every recommendation we make is validated in simulation before a single piece of equipment is ordered.</p>
    </div>
    <div class="band-cta">
      <a class="btn btn-light" href="contact.html">Start a conversation {ARROW}</a>
    </div>
  </div>
</section>
"""
    title = f"{SITE['full_name']} (IMS) — Advanced Manufacturing Engineering, Simulation & Optimization"
    write("index.html", head(title, SITE["description"], rel, "", "assets/img/hero-robot-arm.png") + header(rel, "home") + body + footer(rel))


def build_services_index():
    rel = "../"
    rows = "".join(
        f"""<a class="svc-row" href="{s['slug']}.html">
  <span class="num">{s['num']:02d}</span>
  {icon(s['card_icon'], 'n', rel)}
  <div><h3>{esc(s['title'])}</h3><p>{esc(s['blurb'])}</p></div>
  <span class="more">{ARROW}</span>
</a>"""
        for s in SERVICES
    )
    A = C["about"]
    body = f"""
<section class="hero page-hero">
  <div class="chev-bg" aria-hidden="true"><i class="b1"></i><i class="b2"></i></div>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{rel}index.html">Home</a><span>/</span><span>Services</span></nav>
    {kicker('Advanced Engineering Services')}
    <h1>{esc(A['services_heading'])}</h1>
    <p class="lead">{esc(A['services_lead'])}</p>
  </div>
</section>
<section class="svc-list">
  <div class="wrap">{rows}</div>
</section>
"""
    title = f"Services — {SITE['full_name']}"
    desc = "Seven advanced engineering services: manufacturing engineering, logistics and material flow, throughput and buffer optimization, ergonomics simulation, continuous improvement, press transfer digital twins and special projects."
    write("services/index.html", head(title, desc, rel, "services/index.html") + header(rel, "services") + body + footer(rel))


def build_service(s, i):
    rel = "../"
    prev_s = SERVICES[i - 1] if i > 0 else None
    next_s = SERVICES[i + 1] if i < len(SERVICES) - 1 else None
    crumbs = f'<nav class="crumbs" aria-label="Breadcrumb"><a href="{rel}index.html">Home</a><span>/</span><a href="index.html">Services</a><span>/</span><span>{esc(s["short"])}</span></nav>'
    hero = f"""
<section class="hero svc-hero">
  <div class="chev-bg" aria-hidden="true"><i class="b1"></i><i class="b2"></i><i class="b3"></i></div>
  <div class="wrap grid-2">
    <div class="hero-text">
      {crumbs}
      <div class="num-title"><span class="big-num">{s['num']}</span><h1>{esc(s['title'])}</h1></div>
      <p class="lead">{esc(s['subtitle'])}</p>
    </div>
    <div class="hero-media"><img src="{rel}assets/img/{s['hero_img']}" alt="{esc(s['hero_alt'])}" width="640" height="560" fetchpriority="high"></div>
  </div>
</section>
"""
    if s.get("special"):
        samples = "".join(
            f'<div class="sample"><span class="num">{n}</span><h3>{esc(x["title"])}</h3><p>{esc(x["desc"])}</p></div>'
            for n, x in enumerate(s["samples"], 1)
        )
        body = hero + f"""
<section class="intro">
  <div class="wrap grid-2 v-center">
    <p class="lead big">{esc(s['intro'])}</p>
    <div class="pillar-row right">{CHEVRON_SVG}<div class="pillar-words">{''.join(f'<span>{esc(p)}</span>' for p in SITE['taglines']['pillars'])}</div></div>
  </div>
</section>
<section class="samples">
  <div class="wrap">
    <div class="sec-head">{kicker('Track record')}<h2>{esc(s['samples_heading'])}</h2></div>
    <div class="grid-2 gap">{samples}</div>
  </div>
</section>
"""
    else:
        pains = "".join(f"<li>{md(p)}</li>" for p in s["pains"])
        scope = "".join(f"<li>{esc(p)}</li>" for p in s["scope"])
        inputs = "".join(
            f"""<div class="input-card">
  <div class="input-head"><span class="num">{n}</span><h3>{esc(x['title'])}</h3></div>
  <div class="input-body"><p>{esc(x['desc'])}</p>{icon(x['icon'], 'w', rel)}</div>
</div>"""
            for n, x in enumerate(s["inputs"], 1)
        )
        delivs = "".join(
            f'<div class="deliv">{icon(x["icon"], "n", rel)}<div><h3>{esc(x["title"])}</h3><p>{md(x["desc"])}</p></div></div>'
            for x in s["deliverables"]
        )
        extra = ""
        if s.get("case"):
            steps = "".join(
                f"""<figure class="step">
  <img src="{rel}assets/img/{st['src']}" alt="{esc(st['label'])}: {esc(st['desc'])}" loading="lazy">
  <figcaption><span class="lbl">{esc(st['label'])}</span><span class="tag {st['tag_class']}">{esc(st['tag'])}</span><p>{esc(st['desc'])}</p></figcaption>
</figure>"""
                for st in s["case"]["steps"]
            )
            extra += f"""
<section class="case">
  <div class="wrap">
    <div class="sec-head">{kicker('Worked example')}<h2>{esc(s['case']['heading'])}</h2></div>
    <div class="steps">{steps}</div>
  </div>
</section>"""
        if s.get("compare"):
            cp = s["compare"]
            extra += f"""
<section class="compare">
  <div class="wrap">
    <div class="sec-head">{kicker('Before and after')}<h2>{esc(cp['heading'])}</h2></div>
    <div class="grid-2 gap">
      <figure class="cmp">
        <div class="cmp-img"><img src="{rel}assets/img/{cp['before']['src']}" alt="Layout before optimization: {esc(cp['before']['label'])}" loading="lazy"></div>
        <figcaption><span class="tag red">Before</span> {esc(cp['before']['label'])}</figcaption>
      </figure>
      <figure class="cmp">
        <div class="cmp-img"><img src="{rel}assets/img/{cp['after']['src']}" alt="Layout after optimization: {esc(cp['after']['label'])}" loading="lazy"></div>
        <figcaption><span class="tag green">After</span> {esc(cp['after']['label'])}</figcaption>
      </figure>
    </div>
  </div>
</section>"""
        if s.get("gallery"):
            figs = "".join(
                f'<figure class="{"wide" if g.get("wide") else ""}"><img src="{rel}assets/img/{g["src"]}" alt="{esc(g["caption"])}" loading="lazy"><figcaption>{esc(g["caption"])}</figcaption></figure>'
                for g in s["gallery"]
            )
            extra += f"""
<section class="gallery">
  <div class="wrap">
    <div class="sec-head">{kicker('In practice')}<h2>Simulation and analysis outputs</h2></div>
    <div class="gal">{figs}</div>
  </div>
</section>"""
        body = hero + f"""
<section class="question">
  <div class="wrap"><span class="qmark" aria-hidden="true">?</span><h2>{esc(s['question'])}</h2></div>
</section>

<section class="pains">
  <div class="wrap grid-2 gap">
    <div>
      {kicker('The challenge')}
      <h2>Typical issues we see</h2>
      <ul class="chev-list">{pains}</ul>
    </div>
    <aside class="panel scope">
      <h3>{esc(s['scope_heading'])}</h3>
      <ul class="tick-list">{scope}</ul>
    </aside>
  </div>
</section>

<section class="inputs">
  <div class="wrap">
    <div class="sec-head with-chev">{CHEVRON_SVG}<h2>{md(s['inputs_heading'])}</h2></div>
    <div class="input-grid">{inputs}</div>
  </div>
</section>

<section class="deliverables">
  <div class="wrap">
    <div class="sec-head with-chev">{CHEVRON_SVG}<h2>{md(s['deliverables_heading'])}</h2></div>
    <div class="grid-2 gap deliv-grid">{delivs}</div>
  </div>
</section>
{extra}
"""
    nav = f"""
<section class="cta-close">
  <div class="chev-bg" aria-hidden="true"><i class="b1"></i><i class="b2"></i></div>
  <div class="wrap cta-inner">
    <div class="cta-copy">
      <p class="kicker light">Next step</p>
      <h2>{esc(s['closing'])}</h2>
      <p>Tell us about your line, your targets and your constraints. We come back with a scoped proposal, not a sales call.</p>
    </div>
    <div class="cta-actions">
      <a class="btn btn-light" href="{rel}contact.html?service={s['slug']}">Request a scoped proposal {ARROW}</a>
      <a class="cta-alt" href="mailto:{esc(SITE['email'])}?subject={esc('IMS enquiry: ' + plain(s['title']))}">or e-mail {esc(SITE['email'])}</a>
    </div>
  </div>
</section>
<nav class="pager wrap" aria-label="Other services">
  {f'<a class="prev" href="{prev_s["slug"]}.html"><small>Previous</small><span>{prev_s["num"]:02d} {esc(prev_s["short"])}</span></a>' if prev_s else '<span></span>'}
  <a class="all" href="index.html">All services</a>
  {f'<a class="next" href="{next_s["slug"]}.html"><small>Next</small><span>{next_s["num"]:02d} {esc(next_s["short"])}</span></a>' if next_s else '<span></span>'}
</nav>
"""
    title = f"{s['title']} — {SITE['full_name']}"
    desc = plain(s["blurb"])
    write(f"services/{s['slug']}.html", head(title, desc, rel, f"services/{s['slug']}.html", f"assets/img/{s['hero_img']}") + header(rel, "services") + body + nav + footer(rel))


def build_contact():
    rel = ""
    addr = "<br>".join(esc(a) for a in SITE["address_lines"])
    phone = f'<div class="c-item"><h3>Phone</h3><p><a href="tel:{esc(SITE["phone"])}">{esc(SITE["phone"])}</a></p></div>' if SITE.get("phone") else ""
    svc_opts = "".join(f'<li><a href="services/{s["slug"]}.html">{esc(s["short"])}</a></li>' for s in SERVICES)
    topics = json.dumps({x["slug"]: x["title"] for x in SERVICES})
    team = SITE.get("contact_team")
    person_block = f'<div class="c-item"><h3>{esc(team["label"])}</h3><p class="team-desc">{esc(team["desc"])}</p></div>' if team else ""
    body = f"""
<section class="hero page-hero">
  <div class="chev-bg" aria-hidden="true"><i class="b1"></i><i class="b2"></i></div>
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><span>Contact</span></nav>
    {kicker('Contact us')}
    <h1>Let&rsquo;s talk about your next program</h1>
    <p class="lead">Tell us about your line, your targets and your constraints. We will come back with a scoped proposal.</p>
  </div>
</section>
<section class="contact">
  <div class="wrap grid-2 gap">
    <div class="panel c-card">
      <p id="enquiry-topic" class="topic" hidden>Enquiry about: <strong></strong></p>
      {person_block}
      <div class="c-item"><h3>E-mail</h3><p><a class="mail" href="mailto:{esc(SITE['email'])}">{esc(SITE['email'])}</a></p></div>
      {phone}
      <div class="c-item"><h3>Office</h3><p>{addr}</p></div>
      <a class="btn btn-primary" href="mailto:{esc(SITE['email'])}?subject=IMS%20enquiry">Send us an e-mail {ARROW}</a>
    </div>
    <div>
      <h2>What to include</h2>
      <ul class="chev-list">
        <li>The <strong>service</strong> you are interested in, or the problem you are trying to solve</li>
        <li>Your <strong>plant, line or program</strong> and where it is in its life cycle (concept, launch, running)</li>
        <li>Rough <strong>volumes, cycle-time targets</strong> and any hard constraints (space, capital, timing)</li>
        <li>The <strong>data</strong> you already have: layouts, cycle time charts, PFEP, 3D models</li>
      </ul>
      <h3 class="mt">Services</h3>
      <ul class="tick-list two-col">{svc_opts}</ul>
    </div>
  </div>
</section>
<script>window.__SERVICE_TITLES__ = {topics};</script>
"""
    title = f"Contact — {SITE['full_name']}"
    write("contact.html", head(title, "Contact Integrated Manufacturing Systems (IMS) in Saudi Arabia for advanced manufacturing engineering, simulation and optimization services.", rel, "contact.html") + header(rel, "contact") + body + footer(rel))


def build_404():
    rel = "/"
    body = f"""
<section class="hero page-hero">
  <div class="wrap">
    {kicker('404')}
    <h1>Page not found</h1>
    <p class="lead">The page you asked for is not here. Try the <a href="/index.html">home page</a> or <a href="/services/index.html">our services</a>.</p>
  </div>
</section>
"""
    write("404.html", head("Page not found — IMS", "Page not found", rel, "404.html") + header(rel, "") + body + footer(rel))


def build_meta():
    urls = ["", "services/index.html", "contact.html"] + [f"services/{s['slug']}.html" for s in SERVICES]
    today = datetime.date.today().isoformat()
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sm += f"  <url><loc>{SITE['domain']}/{u}</loc><lastmod>{today}</lastmod></url>\n"
    sm += "</urlset>\n"
    write("sitemap.xml", sm)
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")


if __name__ == "__main__":
    build_home()
    build_services_index()
    for i, s in enumerate(SERVICES):
        build_service(s, i)
    build_contact()
    build_404()
    build_meta()
