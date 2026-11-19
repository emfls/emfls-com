#!/usr/bin/env python3
"""Static compiler for EMFLS Studio Journal (clean-slate AdSense-ready static site)."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
SITE_ORIGIN = "https://www.emfls.com"
PUB_DATE = "2026-11-19"
PUB_LABEL = "November 19, 2026"
ADSENSE_PUB = "ca-pub-8830524482034754"

CATEGORIES = {
    "lighting": {
        "label": "Lighting & Optics",
        "eyebrow": "Photography Lighting & Exposure",
        "description": "How to measure window-light ratios, balance Kelvin color, predict focal compression, and check dynamic range in a studio setup.",
    },
    "design": {
        "label": "Design & Color",
        "eyebrow": "Typography, Color Spaces & Vector Craft",
        "description": "Readable modular type scales, accessible WCAG luminance pairs, structured SVG technical diagrams, and wide-gamut display proofing.",
    },
    "studio": {
        "label": "Studio Workflow",
        "eyebrow": "Acoustics, Calibration & Asset Architecture",
        "description": "First-reflection acoustic placement, monitor bias-light calibration, desk ergonomics, and durable plain-text project archiving.",
    },
}

TRUST_LINKS = (
    ("about/", "About"),
    ("editorial-policy/", "Editorial Policy"),
    ("privacy-policy/", "Privacy Policy"),
    ("terms/", "Terms"),
    ("contact/", "Contact"),
)


def rel_prefix(depth: int) -> str:
    return "" if depth == 0 else "../" * depth


def head_block(
    *,
    title: str,
    description: str,
    canonical_path: str,
    depth: int,
    og_type: str = "website",
    extra_style: str = "",
    json_ld: list[dict] | None = None,
    noindex: bool = False,
    include_adsense: bool = True,
) -> str:
    prefix = rel_prefix(depth)
    canon_url = f"{SITE_ORIGIN}/{canonical_path}"
    robots = "noindex, follow" if noindex else "index, follow"
    ld_tags = ""
    if json_ld:
        ld_tags = "\n".join(
            f'  <script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'
            for obj in json_ld
        )
    css_link = f'  <link rel="stylesheet" href="{prefix}assets/style.css">' if not extra_style else f'  <style>{extra_style}</style>'
    adsense_meta = (
        f'\n  <meta name="google-adsense-account" content="{ADSENSE_PUB}">'
        if include_adsense
        else ""
    )
    adsense_script = (
        f'\n  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB}" crossorigin="anonymous"></script>'
        if include_adsense
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="robots" content="{robots}">{adsense_meta}
  <link rel="canonical" href="{html.escape(canon_url)}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="EMFLS Studio Journal">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{html.escape(canon_url)}">
{css_link}
{ld_tags}{adsense_script}
</head>"""


def header_html(depth: int, active_rel: str = "", dynamic_nav: bool = False) -> str:
    prefix = rel_prefix(depth)
    nav_items = [
        ("", "Home"),
        ("lighting/", "Lighting"),
        ("design/", "Design"),
        ("studio/", "Studio"),
        ("about/", "About"),
        ("contact/", "Contact"),
    ]

    def mk_link(rel: str, label: str) -> str:
        cur = ' aria-current="page"' if rel == active_rel and not dynamic_nav else ""
        if dynamic_nav:
            return f'<a href="/{rel}" data-nav-rel="{html.escape(rel)}">{html.escape(label)}</a>'
        href = f"{prefix}{rel}" if rel else (prefix or "./")
        return f'<a href="{html.escape(href)}"{cur}>{html.escape(label)}</a>'

    brand_href = '"/" data-nav-rel=""' if dynamic_nav else f'"{html.escape(prefix or "./")}"'
    links = "\n        ".join(mk_link(r, l) for r, l in nav_items)
    return f"""  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href={brand_href}>
        <span class="brand-mark">EMFLS Studio Journal</span>
        <span class="brand-sub">Field Craft &amp; Reference</span>
      </a>
      <nav class="main-nav" aria-label="Primary Navigation">
        {links}
      </nav>
    </div>
  </header>"""


def footer_html(depth: int, dynamic_nav: bool = False) -> str:
    prefix = rel_prefix(depth)
    links = []
    for rel, label in TRUST_LINKS:
        if dynamic_nav:
            links.append(f'<a href="/{rel}" data-nav-rel="{html.escape(rel)}">{html.escape(label)}</a>')
        else:
            links.append(f'<a href="{html.escape(prefix + rel)}">{html.escape(label)}</a>')
    links_html = "\n        ".join(links)
    return f"""  <footer class="site-footer">
    <div class="container footer-grid">
      <div>
        <strong>EMFLS Studio Journal</strong> · Independent reference notes on lighting, design systems, and studio workflow.
      </div>
      <nav class="footer-links" aria-label="Editorial &amp; Legal Links">
        {links_html}
      </nav>
    </div>
  </footer>"""


def wrap_page(
    *,
    title: str,
    description: str,
    canonical_path: str,
    depth: int,
    body_html: str,
    active_rel: str = "",
    og_type: str = "website",
    json_ld: list[dict] | None = None,
    include_search_js: bool = False,
    dynamic_nav: bool = False,
    extra_style: str = "",
    noindex: bool = False,
    include_adsense: bool = True,
) -> str:
    prefix = rel_prefix(depth)
    data_attr = "" if dynamic_nav else f' data-root="{html.escape(prefix)}"'
    script_tag = (
        f'\n  <script src="{"/" if dynamic_nav else prefix}assets/search.js" defer></script>'
        if include_search_js
        else ""
    )
    if dynamic_nav and include_search_js:
        # Resolve search.js cleanly at both root and /emfls-com/ staging subpath
        script_tag = (
            '\n  <script>(function(){var p=window.location.pathname||"/";'
            'var b=(p==="/emfls-com"||p.indexOf("/emfls-com/")===0)?"/emfls-com/":"/";'
            'var s=document.createElement("script");s.src=b+"assets/search.js";s.defer=true;'
            'document.head.appendChild(s);})();</script>'
        )
    return (
        head_block(
            title=title,
            description=description,
            canonical_path=canonical_path,
            depth=depth,
            og_type=og_type,
            json_ld=json_ld,
            extra_style=extra_style,
            noindex=noindex,
            include_adsense=include_adsense,
        )
        + f"\n<body{data_attr}>\n"
        + '  <a class="skip-link" href="#main-content">Skip to main content</a>\n'
        + header_html(depth, active_rel=active_rel, dynamic_nav=dynamic_nav)
        + f'\n  <main id="main-content" tabindex="-1">\n    <div class="container">\n{body_html}\n    </div>\n  </main>\n'
        + footer_html(depth, dynamic_nav=dynamic_nav)
        + script_tag
        + "\n</body>\n</html>\n"
    )


def load_articles() -> list[dict]:
    files = sorted(CONTENT_DIR.glob("*__*.json"))
    if len(files) != 18:
        raise RuntimeError(f"Expected 18 article JSON files in {CONTENT_DIR}, found {len(files)}")
    items = [json.loads(p.read_text(encoding="utf-8")) for p in files]
    cat_order = {"lighting": 0, "design": 1, "studio": 2}
    items.sort(key=lambda a: (cat_order.get(a["category"], 99), a["slug"]))
    return items


def build_home(articles: list[dict]) -> str:
    cat_counts = {c: sum(1 for a in articles if a["category"] == c) for c in CATEGORIES}
    cat_cards = "\n".join(
        f"""        <article class="card">
          <div>
            <div class="card-meta">{html.escape(info['eyebrow'])} · {cat_counts[c]} guides</div>
            <h2><a href="{c}/">{html.escape(info['label'])}</a></h2>
          </div>
          <p>{html.escape(info['description'])}</p>
        </article>"""
        for c, info in CATEGORIES.items()
    )

    featured_cards = []
    # 2 featured guides from each category (6 featured total on Home + full archive in categories)
    for c in ("lighting", "design", "studio"):
        subset = [a for a in articles if a["category"] == c][:3]
        for a in subset:
            rel = f"{a['category']}/{a['slug']}/"
            featured_cards.append(
                f"""        <article class="card">
          <div>
            <div class="card-meta">{html.escape(CATEGORIES[c]['label'])} · {a['reading_minutes']} min read</div>
            <h3><a href="{html.escape(rel)}">{html.escape(a['title'])}</a></h3>
          </div>
          <p>{html.escape(a['lead_summary'])}</p>
        </article>"""
            )

    body = f"""      <section class="hero">
        <p class="eyebrow">Independent Technical Reference · Updated {PUB_LABEL}</p>
        <h1>EMFLS Studio Journal</h1>
        <p class="lead">Practical field guides on lighting, accessible typography and color, and studio acoustics. Each guide uses a schematic, worked examples, and a checklist to help you apply and verify the technique in your own setup.</p>
        <form id="studio-search-form" class="search-box" role="search">
          <input id="studio-search-input" type="search" aria-label="Search field guides" placeholder="Try WCAG or acoustic">
          <button type="submit">Search</button>
        </form>
        <div id="studio-search-results" class="search-results" role="region" aria-live="polite" aria-label="Search results"></div>
      </section>

      <section aria-labelledby="sections-title">
        <h2 id="sections-title">Core Editorial Sections</h2>
        <div class="grid-3">
{cat_cards}
        </div>
      </section>

      <section aria-labelledby="featured-title">
        <h2 id="featured-title">Featured Studio Field Guides</h2>
        <div class="grid-3">
{chr(10).join(featured_cards)}
        </div>
      </section>

      <section class="trust-strip" aria-labelledby="standards-title">
        <h2 id="standards-title" style="margin-top:0">Editorial Verification &amp; Independence</h2>
        <p>Check light levels, calculate contrast ratios, or measure room geometry with the steps in each guide. Read our <a href="editorial-policy/">Editorial Policy</a> or <a href="contact/">report a technical issue</a>.</p>
      </section>"""

    ld = [
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "EMFLS Studio Journal",
            "url": f"{SITE_ORIGIN}/",
            "description": "Independent field guides covering photography lighting, editorial design systems, and studio workflow craft.",
        }
    ]
    return wrap_page(
        title="EMFLS Studio Journal — Lighting, Design & Studio Craft Field Guides",
        description="Practical field guides with worked examples, diagrams, and checks for photography lighting, accessible design, and small-room acoustics.",
        canonical_path="",
        depth=0,
        body_html=body,
        active_rel="",
        json_ld=ld,
        include_search_js=True,
    )


def build_category_page(cat: str, info: dict, articles: list[dict]) -> str:
    subset = [a for a in articles if a["category"] == cat]
    cards = "\n".join(
        f"""        <article class="card">
          <div>
            <div class="card-meta">{html.escape(info['label'])} · {a['reading_minutes']} min read</div>
            <h2><a href="{html.escape(a['slug'])}/">{html.escape(a['title'])}</a></h2>
          </div>
          <p>{html.escape(a['lead_summary'])}</p>
        </article>"""
        for a in subset
    )
    body = f"""      <nav class="breadcrumbs" aria-label="Breadcrumb">
        <a href="../">Home</a> / <span aria-current="page">{html.escape(info['label'])}</span>
      </nav>
      <section class="hero">
        <p class="eyebrow">{html.escape(info['eyebrow'])}</p>
        <h1>{html.escape(info['label'])} Field Guides</h1>
        <p class="lead">{html.escape(info['description'])}</p>
      </section>
      <div class="grid-2">
{cards}
      </div>"""
    ld = [
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_ORIGIN}/"},
                {"@type": "ListItem", "position": 2, "name": info["label"], "item": f"{SITE_ORIGIN}/{cat}/"},
            ],
        }
    ]
    return wrap_page(
        title=f"{info['label']} Field Guides — EMFLS Studio Journal",
        description=info["description"],
        canonical_path=f"{cat}/",
        depth=1,
        body_html=body,
        active_rel=f"{cat}/",
        json_ld=ld,
    )


def build_article_page(article: dict, all_articles: list[dict]) -> str:
    cat = article["category"]
    slug = article["slug"]
    cat_label = CATEGORIES[cat]["label"]
    siblings = [a for a in all_articles if a["category"] == cat and a["slug"] != slug][:3]
    sections = article["sections_html"].replace(
        '<div class="table-wrap">',
        '<div class="table-wrap" role="region" aria-label="Comparison table" tabindex="0">',
    )
    related_cards = "\n".join(
        f"""          <article class="card">
            <div>
              <div class="card-meta">{html.escape(cat_label)} · {s['reading_minutes']} min read</div>
              <h3><a href="../{html.escape(s['slug'])}/">{html.escape(s['title'])}</a></h3>
            </div>
            <p>{html.escape(s['lead_summary'])}</p>
          </article>"""
        for s in siblings
    )

    body = f"""      <nav class="breadcrumbs" aria-label="Breadcrumb">
        <a href="../../">Home</a> / <a href="../">{html.escape(cat_label)}</a> / <span aria-current="page">{html.escape(article['title'])}</span>
      </nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">{html.escape(CATEGORIES[cat]['eyebrow'])}</p>
          <h1>{html.escape(article['title'])}</h1>
          <div class="byline">By <strong>EMFLS Editorial Desk</strong> · Published {PUB_LABEL} · {article['reading_minutes']} min read ({article['word_count']:,} words)</div>
          <p class="lead-callout">{html.escape(article['lead_summary'])}</p>
          <figure class="diagram-figure">
            <input type="checkbox" id="diagram-full-size" aria-describedby="diagram-scroll-hint">
            <label for="diagram-full-size">Show full-size diagram</label>
            <p id="diagram-scroll-hint">Scroll horizontally or focus the diagram and use the arrow keys to see all labels.</p>
            <div class="diagram-view" role="region" aria-label="Diagram" tabindex="0">
              {article['svg_diagram']}
            </div>
            <figcaption>{html.escape(article['svg_caption'])}</figcaption>
          </figure>
          {sections}
        </div>
        <aside class="related-panel" aria-labelledby="related-heading">
          <h2 id="related-heading" style="margin-top:0">Related {html.escape(cat_label)} Guides</h2>
          <div class="grid-3">
{related_cards}
          </div>
        </aside>
      </article>"""

    canon = f"{SITE_ORIGIN}/{cat}/{slug}/"
    ld = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article["title"],
            "description": article["meta_description"],
            "datePublished": PUB_DATE,
            "dateModified": PUB_DATE,
            "author": {"@type": "Organization", "name": "EMFLS Editorial Desk"},
            "publisher": {"@type": "Organization", "name": "EMFLS Studio Journal"},
            "mainEntityOfPage": canon,
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_ORIGIN}/"},
                {"@type": "ListItem", "position": 2, "name": cat_label, "item": f"{SITE_ORIGIN}/{cat}/"},
                {"@type": "ListItem", "position": 3, "name": article["title"], "item": canon},
            ],
        },
    ]
    return wrap_page(
        title=f"{article['title']} — EMFLS Studio Journal",
        description=article["meta_description"],
        canonical_path=f"{cat}/{slug}/",
        depth=2,
        body_html=body,
        active_rel=f"{cat}/",
        og_type="article",
        json_ld=ld,
    )


def build_trust_pages() -> dict[str, tuple[str, str, str]]:
    pages = {}

    pages["about"] = (
        "About EMFLS Studio Journal",
        "Learn who publishes EMFLS Studio Journal and how to use its photography, design, and studio reference guides.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">About</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Publication Profile</p>
          <h1>About EMFLS Studio Journal</h1>
          <p class="lead-callout">EMFLS Studio Journal is an independent technical publication dedicated to practical photography lighting geometry, accessible digital typography and vector diagramming, and ergonomic desk studio engineering.</p>
          <h2>Why We Focus on Physical &amp; Visual Fundamentals</h2>
          <p>Modern creative workspaces sit at the intersection of light, color perception, typography, and acoustics. Too often, creators run into subtle technical obstacles—clipped highlights in window portraits, muddy print exports, vibrating low-end voice recordings, or low-contrast web diagrams—that can be resolved quickly with clear numbers and first-principles diagrams.</p>
          <p>Our guides explain how to check incident light with a meter, calculate WCAG contrast ratios, compare sRGB and Display P3, and measure a room or desk layout. Worked examples show how to apply each method. Use your own equipment and conditions to verify the result.</p>
          <h2>Core Sections Maintained Here</h2>
          <ul>
            <li><a href="../lighting/">Lighting &amp; Optics</a>: Directional window diffusion, Kelvin color reconciliation, perspective compression, histogram reading, and RAW headroom.</li>
            <li><a href="../design/">Design &amp; Color</a>: Modular typographic hierarchies, WCAG palette math, crisp SVG schematic rules, and responsive CSS grids.</li>
            <li><a href="../studio/">Studio Workflow</a>: First-reflection acoustic treatment, microphone proximity control, bias lighting calibration, and long-term plain-text archiving.</li>
          </ul>
          <h2>Publisher Information</h2>
          <p>The EMFLS Editorial Desk independently publishes EMFLS Studio Journal. See the <a href="../contact/">Contact page</a> for technical corrections and accessibility feedback.</p>
        </div>
      </article>""",
    )

    pages["editorial-policy"] = (
        "Editorial Policy & Verification Standards",
        "How EMFLS Studio Journal presents worked examples, technical diagrams, and reader corrections.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Editorial Policy</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Standards &amp; Accountability</p>
          <h1>Editorial Policy</h1>
          <p class="lead-callout">Our reference guides explain how to check a calculation or technique so readers can reproduce it in their own setup.</p>
          <h2>1. Measurement &amp; Technical Accuracy</h2>
          <p>Worked examples illustrate calculations and measurement procedures. Results depend on the equipment, room, and settings used. Check the assumptions in each example before using its numbers as a target.</p>
          <h2>2. Independence &amp; Conflict Prevention</h2>
          <p>EMFLS Studio Journal accepts no paid placement, undisclosed sponsorships, or commercial review exchanges. Product categories and tools mentioned in our lighting or studio setup notes serve purely as technical examples illustrating physics, optics, or software behavior.</p>
          <h2>3. Original Technical Diagrams</h2>
          <p>Article figures use scalable SVGs and text captions. Choose “Show full-size diagram” when labels are too small in the preview.</p>
          <h2>4. Corrections</h2>
          <p>See the <a href="../contact/">Contact page</a> to report a calculation error, unclear diagram label, or outdated reference. Include the article URL and the specific passage or label.</p>
        </div>
      </article>""",
    )

    pages["privacy-policy"] = (
        "Privacy Policy",
        "What GitHub Pages and Google AdSense collect when you visit EMFLS Studio Journal and where to manage ad personalization.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Privacy Policy</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Effective Date: {PUB_LABEL}</p>
          <h1>Privacy Policy</h1>
          <p class="lead-callout">This policy explains how our host and advertising providers process data when you visit www.emfls.com.</p>
          <h2>1. Hosting &amp; Site Search</h2>
          <p>GitHub Pages hosts this static site. GitHub logs and stores visitors’ Internet Protocol (IP) addresses for security, including visits by people who are signed out of GitHub. See <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection">GitHub Pages data collection</a> and the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub Privacy Statement</a>.</p>
          <p>Reading the site requires no account. The site search downloads an article index and matches your search terms in your browser.</p>
          <h2>2. Google AdSense &amp; Third-Party Advertising</h2>
          <p>This site loads <strong>Google AdSense</strong>. Your browser shares information with Google when its advertising services load, including the page URL and your IP address. Third parties, including Google, can place or read cookies in your browser and use web beacons, IP addresses, or other identifiers to collect information as a result of serving ads.</p>
          <p>Google uses this information to deliver ads, measure performance, and prevent fraud or abuse. Depending on your settings, Google and its partners may use information about previous visits to this site and other sites to personalize ads. Read <a href="https://policies.google.com/technologies/partner-sites">how Google uses data from sites and apps that use its services</a>.</p>
          <h2>3. Advertising Choices</h2>
          <ul>
            <li>Manage Google ad personalization in <a href="https://adssettings.google.com/">Google Ad Settings</a>.</li>
            <li>Manage personalized advertising from participating vendors through <a href="https://www.aboutads.info/choices/">YourAdChoices</a>.</li>
          </ul>
          <h2>4. Children's Information</h2>
          <p>EMFLS Studio Journal is a general technical reference resource intended for creative practitioners and does not knowingly collect personally identifiable information from children under the age of 13.</p>
          <h2>5. Privacy Requests</h2>
          <p>For data handled by our host or ad provider, see the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub Privacy Statement</a> or <a href="https://policies.google.com/privacy">Google Privacy Policy</a>. This site does not currently offer a private contact channel. Keep personal information out of the public technical issue tracker linked on the <a href="../contact/">Contact page</a>.</p>
        </div>
      </article>""",
    )

    pages["terms"] = (
        "Terms of Use & Reference Disclaimer",
        "Terms governing your access to EMFLS Studio Journal guides, vector diagrams, and educational technical examples.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Terms of Use</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Last Updated: {PUB_LABEL}</p>
          <h1>Terms of Use</h1>
          <p class="lead-callout">By reading or referencing materials on EMFLS Studio Journal (www.emfls.com), you agree to the educational usage terms and disclaimers summarized below.</p>
          <h2>1. Educational &amp; Informational Purpose</h2>
          <p>All articles, exposure charts, color contrast guidelines, acoustic placement steps, and ergonomic geometry ranges published on this website are provided strictly for general educational reference. Workspace safety, electrical rigging for studio lights, and personal physical comfort should always be verified against equipment manufacturer safety manuals and qualified local professionals where applicable.</p>
          <h2>2. Intellectual Property</h2>
          <p>Original article text, layout styles, and scalable vector diagrams created for EMFLS Studio Journal remain the intellectual property of EMFLS Studio Journal unless otherwise noted. Brief excerpts or links for non-commercial citation are welcome with clear attribution back to the canonical URL.</p>
          <h2>3. External Links</h2>
          <p>Links to external reference standards or privacy settings pages are provided for reader convenience. We do not control or assume responsibility for the ongoing availability or content of third-party websites.</p>
          <h2>4. Contact Regarding Terms</h2>
          <p>The <a href="../contact/">Contact page</a> lists the public route for technical issues. A private channel for permissions requests is currently unavailable.</p>
        </div>
      </article>""",
    )

    pages["contact"] = (
        "Contact EMFLS Editorial Desk",
        "Report technical corrections, diagram accessibility problems, or broken links for EMFLS Studio Journal.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Contact</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Reader Support &amp; Corrections</p>
          <h1>Contact Us</h1>
          <p class="lead-callout">Report a technical correction, inaccessible diagram, or broken link in the <a href="https://github.com/emfls/emfls-com/issues">public EMFLS Studio Journal GitHub issue tracker</a>. Posting requires a GitHub account.</p>
          <h2>What to Include</h2>
          <p>Include the article URL, the relevant passage or diagram label, and what you expected to see. For a layout problem, include your browser and approximate screen width.</p>
          <h2>Private Inquiries</h2>
          <p>GitHub issues are public. Keep personal information, privacy requests, and other confidential matters out of the tracker. A private contact channel is currently unavailable. See our <a href="../privacy-policy/">Privacy Policy</a> for information on how GitHub and Google handle data.</p>
        </div>
      </article>""",
    )
    return pages


def build_404(style_text: str) -> str:
    body = """      <section class="hero">
        <p class="eyebrow">Page Not Found (404)</p>
        <h1>This URL has moved or been retired</h1>
        <p class="lead">EMFLS Studio Journal was rebuilt from the ground up with organized technical guides covering Lighting &amp; Optics, Design &amp; Color, and Studio Workflow. Use the search below or browse any section directly.</p>
        <form id="studio-search-form" class="search-box" role="search">
          <input id="studio-search-input" type="search" aria-label="Search current field guides" placeholder="Try lighting or contrast">
          <button type="submit">Search</button>
        </form>
        <div id="studio-search-results" class="search-results" role="region" aria-live="polite" aria-label="Search results"></div>
      </section>
      <section aria-labelledby="recover-title">
        <h2 id="recover-title">Browse Current Sections</h2>
        <div class="grid-3">
          <article class="card">
            <div><div class="card-meta">6 Guides</div><h3><a href="/lighting/" data-nav-rel="lighting/">Lighting &amp; Optics</a></h3></div>
            <p>Window diffusion angles, Kelvin balance, focal length geometry, and RAW dynamic range.</p>
          </article>
          <article class="card">
            <div><div class="card-meta">6 Guides</div><h3><a href="/design/" data-nav-rel="design/">Design &amp; Color</a></h3></div>
            <p>Modular type scales, WCAG contrast pairs, clean SVG diagramming, and responsive CSS grids.</p>
          </article>
          <article class="card">
            <div><div class="card-meta">6 Guides</div><h3><a href="/studio/" data-nav-rel="studio/">Studio Workflow</a></h3></div>
            <p>Room acoustic treatment, mic placement, bias lighting, plain-text archiving, and ergonomics.</p>
          </article>
        </div>
      </section>"""
    return wrap_page(
        title="Page Not Found — EMFLS Studio Journal",
        description="Explore current EMFLS Studio Journal guides on lighting, design, and studio workflow.",
        canonical_path="404.html",
        depth=0,
        body_html=body,
        include_search_js=True,
        dynamic_nav=True,
        extra_style=style_text,
        noindex=True,
        include_adsense=False,
    )


def main() -> int:
    articles = load_articles()
    style_text = (ROOT / "assets/style.css").read_text(encoding="utf-8")

    # Clean stale category HTML directories before writing
    for cat in CATEGORIES:
        cat_dir = ROOT / cat
        cat_dir.mkdir(parents=True, exist_ok=True)
        (cat_dir / "index.html").write_text(build_category_page(cat, CATEGORIES[cat], articles), encoding="utf-8")

    # Home
    (ROOT / "index.html").write_text(build_home(articles), encoding="utf-8")

    # 18 Articles
    for article in articles:
        art_dir = ROOT / article["category"] / article["slug"]
        art_dir.mkdir(parents=True, exist_ok=True)
        (art_dir / "index.html").write_text(build_article_page(article, articles), encoding="utf-8")

    # 5 Trust Pages
    trust = build_trust_pages()
    for slug, (title, desc, body) in trust.items():
        t_dir = ROOT / slug
        t_dir.mkdir(parents=True, exist_ok=True)
        html_doc = wrap_page(
            title=f"{title} — EMFLS Studio Journal",
            description=desc,
            canonical_path=f"{slug}/",
            depth=1,
            body_html=body,
            active_rel=f"{slug}/",
        )
        (t_dir / "index.html").write_text(html_doc, encoding="utf-8")

    # Custom 404.html
    (ROOT / "404.html").write_text(build_404(style_text), encoding="utf-8")

    # Root support files
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    (ROOT / "ads.txt").write_text("google.com, pub-8830524482034754, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_ORIGIN}/sitemap.xml\n",
        encoding="utf-8",
    )

    search_index = [
        {
            "path": f"{a['category']}/{a['slug']}/",
            "title": a["title"],
            "category": a["category"],
            "category_label": CATEGORIES[a["category"]]["label"],
            "reading_minutes": a["reading_minutes"],
            "summary": a["lead_summary"],
            "description": a["meta_description"],
        }
        for a in articles
    ]
    (ROOT / "search-index.json").write_text(json.dumps(search_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Sitemap (27 canonical URLs)
    urls = [""] + [f"{c}/" for c in CATEGORIES] + [f"{a['category']}/{a['slug']}/" for a in articles] + [f"{s}/" for s in trust]
    url_blocks = "\n".join(
        f"  <url><loc>{SITE_ORIGIN}/{u}</loc><lastmod>{PUB_DATE}</lastmod></url>" for u in urls
    )
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_blocks}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    (ROOT / "README.md").write_text(
        "# EMFLS Studio Journal\n\nStatic reference publication covering photography lighting, editorial design systems, and studio workflow craft.\n",
        encoding="utf-8",
    )
    print(f"BUILT: 1 home + 3 categories + {len(articles)} articles + {len(trust)} trust pages = {len(urls)} canonical URLs (+ 404.html)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
