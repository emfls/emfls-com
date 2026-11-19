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
        "description": "Measured window-light ratios, Kelvin color balance, focal compression geometry, and dynamic-range workflows for practical studio shooting.",
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
        + header_html(depth, active_rel=active_rel, dynamic_nav=dynamic_nav)
        + f"\n  <main>\n    <div class=\"container\">\n{body_html}\n    </div>\n  </main>\n"
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
        <p class="lead">Clear, measurement-backed field guides on natural and artificial lighting, accessible design typography and color spaces, and quiet workspace acoustics. Every guide pairs real distances, ratios, and verification checklists with custom schematic diagrams.</p>
        <form id="studio-search-form" class="search-box" role="search">
          <input id="studio-search-input" type="search" aria-label="Search field guides" placeholder="Search guides (e.g., kelvin, histogram, wcag, acoustic, svg)...">
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
        <p>Every guide in EMFLS Studio Journal is structured around repeatable desk checks—spectrometer and incident light readings, contrast ratio math, and physical room geometry—rather than sponsored product roundups. Read our <a href="editorial-policy/">Editorial Policy</a> or <a href="contact/">submit a technical correction</a>.</p>
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
        description="Practical measurement-backed field guides on photography lighting, accessible design typography, SVG diagrams, and small-room studio acoustics.",
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
            {article['svg_diagram']}
            <figcaption>{html.escape(article['svg_caption'])}</figcaption>
          </figure>
          {article['sections_html']}
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
        "Learn about the mission, documentation focus, and independent studio testing principles behind EMFLS Studio Journal.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">About</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Publication Profile</p>
          <h1>About EMFLS Studio Journal</h1>
          <p class="lead-callout">EMFLS Studio Journal is an independent technical publication dedicated to practical photography lighting geometry, accessible digital typography and vector diagramming, and ergonomic desk studio engineering.</p>
          <h2>Why We Focus on Physical &amp; Visual Fundamentals</h2>
          <p>Modern creative workspaces sit at the intersection of light, color perception, typography, and acoustics. Too often, creators run into subtle technical obstacles—clipped highlights in window portraits, muddy print exports, vibrating low-end voice recordings, or low-contrast web diagrams—that can be resolved quickly with clear numbers and first-principles diagrams.</p>
          <p>Rather than publishing product roundups or speculative industry commentary, our editors maintain focused reference guides tested against repeatable measurements: incident light meter checks, WCAG luminance ratios, sRGB and Display P3 color boundaries, and calibrated room geometry.</p>
          <h2>Core Sections Maintained Here</h2>
          <ul>
            <li><a href="../lighting/">Lighting &amp; Optics</a>: Directional window diffusion, Kelvin color reconciliation, perspective compression, histogram reading, and RAW headroom.</li>
            <li><a href="../design/">Design &amp; Color</a>: Modular typographic hierarchies, WCAG palette math, crisp SVG schematic rules, and responsive CSS grids.</li>
            <li><a href="../studio/">Studio Workflow</a>: First-reflection acoustic treatment, microphone proximity control, bias lighting calibration, and long-term plain-text archiving.</li>
          </ul>
          <h2>Publisher Information</h2>
          <p>EMFLS Studio Journal is independently published by the EMFLS Editorial Desk in Seoul. Questions, technical feedback, and errata notices can be sent to <a href="mailto:contact@emfls.com">contact@emfls.com</a> or submitted through our <a href="../contact/">Contact page</a>.</p>
        </div>
      </article>""",
    )

    pages["editorial-policy"] = (
        "Editorial Policy & Verification Standards",
        "How EMFLS Studio Journal researches, diagrams, verifies, and updates every technical guide prior to publication.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Editorial Policy</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Standards &amp; Accountability</p>
          <h1>Editorial Policy</h1>
          <p class="lead-callout">Every reference guide on EMFLS Studio Journal follows a structured verification standard designed to prioritize clarity, safety, reproducibility, and zero promotional bias.</p>
          <h2>1. Measurement &amp; Technical Accuracy</h2>
          <p>Angles, contrast ratios, luminance levels, acoustic absorption thicknesses, and file-handling recommendations are stated with explicit ranges and boundary assumptions. Whenever different hardware environments yield different tolerances, our reference tables document those margins directly.</p>
          <h2>2. Independence &amp; Conflict Prevention</h2>
          <p>EMFLS Studio Journal accepts no paid placement, undisclosed sponsorships, or commercial review exchanges. Product categories and tools mentioned in our lighting or studio setup notes serve purely as technical examples illustrating physics, optics, or software behavior.</p>
          <h2>3. Original Technical Diagrams</h2>
          <p>Inline vector diagrams are drawn natively as scalable SVG figures to ensure sharp legibility across desktop displays and narrow mobile viewports without external image compression artifacts.</p>
          <h2>4. Corrections &amp; Revision Logging</h2>
          <p>If a reader identifies a broken calculation, unclear diagram label, or outdated technical standard, please notify us via <a href="mailto:contact@emfls.com">contact@emfls.com</a>. Verified corrections are applied promptly to the affected article with an updated publication date.</p>
        </div>
      </article>""",
    )

    pages["privacy-policy"] = (
        "Privacy Policy",
        "How EMFLS Studio Journal handles server logs, cookies, third-party Google AdSense advertising cookies, and user opt-out rights.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Privacy Policy</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Effective Date: {PUB_LABEL}</p>
          <h1>Privacy Policy</h1>
          <p class="lead-callout">Your privacy matters to EMFLS Studio Journal. This document explains what limited technical data is collected when you visit www.emfls.com, how cookies and Google AdSense operate, and how you can manage or opt out of personalized advertising.</p>
          <h2>1. Log Files &amp; Technical Requests</h2>
          <p>EMFLS Studio Journal is served as a static website. Like standard web hosting providers, our static hosting infrastructure may temporarily log non-identifying request headers such as browser type, referring URL, requested path, timestamp, and Internet Protocol (IP) address solely to maintain uptime, diagnose routing issues, and prevent abuse.</p>
          <h2>2. Cookies &amp; Web Beacons</h2>
          <p>This website itself does not set account logins or proprietary tracking databases. Static client-side features such as in-page article search execute locally within your browser without uploading personal profiles.</p>
          <h2>3. Google AdSense &amp; Third-Party Advertising Cookies</h2>
          <p>EMFLS Studio Journal participates in <strong>Google AdSense</strong> to support ongoing independent editorial documentation. Third-party vendors, including Google, use cookies—including the <strong>DoubleClick / Google advertising (DART) cookie</strong>—to serve ads based on a user's prior visits to this website or other websites across the Internet.</p>
          <ul>
            <li>Google's use of advertising cookies enables it and its partners to serve advertisements to visitors based on their visit to www.emfls.com and other sites on the web.</li>
            <li>You may opt out of personalized advertising at any time by visiting <a href="https://www.google.com/settings/ads" rel="noopener noreferrer" target="_blank">Google Ads Settings</a>.</li>
            <li>You can review how Google uses information from sites that use its services at <a href="https://policies.google.com/technologies/ads" rel="noopener noreferrer" target="_blank">Google Advertising Policies &amp; Technologies</a>.</li>
            <li>Alternatively, users can opt out of a third-party vendor's use of cookies for personalized advertising by visiting <a href="https://www.aboutads.info/choices/" rel="noopener noreferrer" target="_blank">aboutads.info</a>.</li>
          </ul>
          <h2>4. Children's Information</h2>
          <p>EMFLS Studio Journal is a general technical reference resource intended for creative practitioners and does not knowingly collect personally identifiable information from children under the age of 13.</p>
          <h2>5. Consent &amp; Contact</h2>
          <p>By using www.emfls.com, you acknowledge the practices described in this Privacy Policy. If you have privacy questions or requests regarding data handling, contact <a href="mailto:contact@emfls.com">contact@emfls.com</a>.</p>
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
          <p>Questions about permissions, citations, or these Terms of Use may be directed to <a href="mailto:contact@emfls.com">contact@emfls.com</a>.</p>
        </div>
      </article>""",
    )

    pages["contact"] = (
        "Contact EMFLS Editorial Desk",
        "Reach EMFLS Studio Journal for technical corrections, accessibility feedback, privacy inquiries, or editorial questions.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Contact</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Reader Support &amp; Corrections</p>
          <h1>Contact Us</h1>
          <p class="lead-callout">We welcome technical corrections, diagram accessibility suggestions, broken-link reports, and reader questions regarding any guide published on EMFLS Studio Journal.</p>
          <h2>Direct Editorial Email</h2>
          <p>Please write to our editorial inbox at <a href="mailto:contact@emfls.com">contact@emfls.com</a>. Including the exact page URL and a short note on your hardware setup or browser viewport helps us reproduce and verify any issue quickly.</p>
          <h2>Response Guidelines</h2>
          <ul>
            <li><strong>Technical Errata &amp; Diagram Fixes:</strong> Reviewed within 2 business days.</li>
            <li><strong>Privacy &amp; Legal Inquiries:</strong> Addressed within 3 business days.</li>
            <li><strong>Policy Links:</strong> You can also review our <a href="../privacy-policy/">Privacy Policy</a>, <a href="../editorial-policy/">Editorial Policy</a>, and <a href="../terms/">Terms of Use</a>.</li>
          </ul>
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
          <input id="studio-search-input" type="search" aria-label="Search current field guides" placeholder="Search current guides (e.g., lighting, color, desk, contrast, raw)...">
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
