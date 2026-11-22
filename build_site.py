#!/usr/bin/env python3
"""Static compiler for EMFLS Studio Journal (AdSense-ready daily editorial static site)."""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
SITE_ORIGIN = "https://www.emfls.com"
DEFAULT_PUB_DATE = "2026-11-19"
ADSENSE_PUB = "ca-pub-8830524482034754"
CONTACT_EMAIL = "emfls24777@daum.net"

CATEGORIES = {
    "lighting": {
        "label": "Lighting & Optics",
        "eyebrow": "Photography Lighting & Exposure",
        "description": "How to measure window-light ratios, control softbox falloff, balance Kelvin color, predict focal compression, and check dynamic range in a studio setup.",
        "og_image": "assets/images/og-lighting.webp",
    },
    "design": {
        "label": "Design & Color",
        "eyebrow": "Typography, Color Spaces & Vector Craft",
        "description": "Readable modular type scales, accessible WCAG luminance pairs, structured SVG technical diagrams, and wide-gamut display proofing.",
        "og_image": "assets/images/og-design.webp",
    },
    "studio": {
        "label": "Studio Workflow",
        "eyebrow": "Acoustics, Calibration & Asset Architecture",
        "description": "First-reflection acoustic placement, monitor bias-light calibration, desk ergonomics, and durable plain-text project archiving.",
        "og_image": "assets/images/og-studio.webp",
    },
}

TRUST_LINKS = (
    ("about/", "About"),
    ("editorial-policy/", "Editorial Policy"),
    ("privacy-policy/", "Privacy Policy"),
    ("terms/", "Terms"),
    ("contact/", "Contact"),
    ("rss.xml", "RSS Feed"),
)


def rel_prefix(depth: int) -> str:
    return "" if depth == 0 else "../" * depth


def format_date_label(iso_date: str) -> str:
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    return dt.strftime("%B %-d, %Y")


def format_rfc822(iso_date: str) -> str:
    dt = datetime.strptime(iso_date, "%Y-%m-%d").replace(hour=12, tzinfo=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def article_image_rel(article: dict) -> str:
    return f"assets/images/{article['category']}-{article['slug']}.webp"


def head_block(
    *,
    title: str,
    description: str,
    canonical_path: str,
    depth: int,
    og_type: str = "website",
    og_image_rel: str = "assets/images/og-home.webp",
    og_image_alt: str = "EMFLS Studio Journal workspace with calibrated photography, design, and studio instruments",
    extra_style: str = "",
    json_ld: list[dict] | None = None,
    noindex: bool = False,
    include_adsense: bool = True,
) -> str:
    prefix = rel_prefix(depth)
    canon_url = f"{SITE_ORIGIN}/{canonical_path}"
    og_image_url = f"{SITE_ORIGIN}/{og_image_rel}"
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
  <link rel="alternate" type="application/rss+xml" title="EMFLS Studio Journal RSS" href="{SITE_ORIGIN}/rss.xml">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="EMFLS Studio Journal">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{html.escape(canon_url)}">
  <meta property="og:image" content="{html.escape(og_image_url)}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="800">
  <meta property="og:image:alt" content="{html.escape(og_image_alt)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(description)}">
  <meta name="twitter:image" content="{html.escape(og_image_url)}">
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
    og_image_rel: str = "assets/images/og-home.webp",
    og_image_alt: str = "EMFLS Studio Journal workspace with calibrated photography, design, and studio instruments",
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
            og_image_rel=og_image_rel,
            og_image_alt=og_image_alt,
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
    if len(files) < 18:
        raise RuntimeError(f"Expected at least 18 article JSON files in {CONTENT_DIR}, found {len(files)}")
    items = []
    for p in files:
        data = json.loads(p.read_text(encoding="utf-8"))
        data.setdefault("published_date", DEFAULT_PUB_DATE)
        data.setdefault("updated_date", data["published_date"])
        items.append(data)
    cat_order = {"lighting": 0, "design": 1, "studio": 2}
    items.sort(key=lambda a: (cat_order.get(a["category"], 99), a["slug"]))
    return items


def build_home(articles: list[dict], latest_date: str) -> str:
    cat_counts = {c: sum(1 for a in articles if a["category"] == c) for c in CATEGORIES}
    cat_cards = "\n".join(
        f"""        <article class="card">
          <div>
            <a class="card-thumb-link" href="{c}/">
              <img class="card-thumb" src="{info['og_image']}" alt="{html.escape(info['label'])} studio photography reference" width="1200" height="800" loading="lazy" decoding="async">
            </a>
            <div class="card-meta">{html.escape(info['eyebrow'])} · {cat_counts[c]} guides</div>
            <h2><a href="{c}/">{html.escape(info['label'])}</a></h2>
          </div>
          <p>{html.escape(info['description'])}</p>
        </article>"""
        for c, info in CATEGORIES.items()
    )

    newest_first = sorted(articles, key=lambda a: (a["published_date"], a["slug"]), reverse=True)
    featured_picks: list[dict] = []
    seen_slugs: set[str] = set()
    # Always lead with the newest published articles first, then fill evenly across all 3 categories (9 cards total)
    for a in newest_first[:3]:
        featured_picks.append(a)
        seen_slugs.add(a["slug"])
    for c in ("lighting", "design", "studio"):
        for a in [x for x in newest_first if x["category"] == c]:
            if a["slug"] not in seen_slugs and len(featured_picks) < 9:
                featured_picks.append(a)
                seen_slugs.add(a["slug"])
                if sum(1 for p in featured_picks if p["category"] == c) >= 3:
                    break

    featured_cards = []
    for a in featured_picks:
        c = a["category"]
        rel = f"{c}/{a['slug']}/"
        img_rel = article_image_rel(a)
        alt_txt = a.get("hero_alt") or f"Editorial studio photograph illustrating {a['title']}"
        featured_cards.append(
            f"""        <article class="card">
          <div>
            <a class="card-thumb-link" href="{html.escape(rel)}">
              <img class="card-thumb" src="{html.escape(img_rel)}" alt="{html.escape(alt_txt)}" width="1200" height="800" loading="lazy" decoding="async">
            </a>
            <div class="card-meta">{html.escape(CATEGORIES[c]['label'])} · {format_date_label(a['published_date'])} · {a['reading_minutes']} min read</div>
            <h3><a href="{html.escape(rel)}">{html.escape(a['title'])}</a></h3>
          </div>
          <p>{html.escape(a['lead_summary'])}</p>
        </article>"""
        )

    body = f"""      <section class="hero">
        <p class="eyebrow">Independent Technical Reference · Updated {format_date_label(latest_date)}</p>
        <h1>EMFLS Studio Journal</h1>
        <p class="lead">Practical field guides on photography lighting, accessible typography and color systems, and small-room studio acoustics. Each guide pairs studio photography, a measured schematic, worked numerical examples, and a reproducible verification checklist.</p>
        <form id="studio-search-form" class="search-box" role="search">
          <input id="studio-search-input" type="search" aria-label="Search field guides" placeholder="Try softbox, WCAG, or acoustic">
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
        <h2 id="featured-title">Latest &amp; Featured Studio Field Guides</h2>
        <div class="grid-3">
{chr(10).join(featured_cards)}
        </div>
      </section>

      <section class="trust-strip" aria-labelledby="standards-title">
        <h2 id="standards-title" style="margin-top:0">Editorial Verification &amp; Independence</h2>
        <p>Check light levels, calculate contrast ratios, or measure room geometry with the reproducible steps in each guide. Read our <a href="about/">About page</a>, inspect our <a href="editorial-policy/">Editorial Policy</a>, or <a href="contact/">contact the editorial desk</a> directly with corrections.</p>
      </section>"""

    ld = [
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "EMFLS Studio Journal",
            "url": f"{SITE_ORIGIN}/",
            "email": CONTACT_EMAIL,
            "logo": f"{SITE_ORIGIN}/assets/images/og-home.webp",
        },
        {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "EMFLS Studio Journal",
            "url": f"{SITE_ORIGIN}/",
            "description": "Independent field guides covering photography lighting, editorial design systems, and studio workflow craft.",
        },
    ]
    return wrap_page(
        title="EMFLS Studio Journal — Lighting, Design & Studio Craft Field Guides",
        description="Practical field guides with studio photographs, worked examples, schematics, and checks for photography lighting, accessible design, and small-room acoustics.",
        canonical_path="",
        depth=0,
        body_html=body,
        active_rel="",
        og_image_rel="assets/images/og-home.webp",
        json_ld=ld,
        include_search_js=True,
    )


def build_category_page(cat: str, info: dict, articles: list[dict]) -> str:
    subset = sorted(
        [a for a in articles if a["category"] == cat],
        key=lambda a: (a["published_date"], a["slug"]),
        reverse=True,
    )
    card_list = []
    for a in subset:
        alt_txt = a.get("hero_alt") or f"Editorial studio photograph for {a['title']}"
        card_list.append(
            f"""        <article class="card">
          <div>
            <a class="card-thumb-link" href="{html.escape(a['slug'])}/">
              <img class="card-thumb" src="../{html.escape(article_image_rel(a))}" alt="{html.escape(alt_txt)}" width="1200" height="800" loading="lazy" decoding="async">
            </a>
            <div class="card-meta">{html.escape(info['label'])} · {format_date_label(a['published_date'])} · {a['reading_minutes']} min read</div>
            <h2><a href="{html.escape(a['slug'])}/">{html.escape(a['title'])}</a></h2>
          </div>
          <p>{html.escape(a['lead_summary'])}</p>
        </article>"""
        )
    cards = "\n".join(card_list)
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
        og_image_rel=info["og_image"],
        og_image_alt=f"{info['label']} editorial cover photograph for EMFLS Studio Journal",
        json_ld=ld,
    )


def build_article_page(article: dict, all_articles: list[dict]) -> str:
    cat = article["category"]
    slug = article["slug"]
    cat_label = CATEGORIES[cat]["label"]
    pub_date = article["published_date"]
    upd_date = article["updated_date"]
    img_rel = article_image_rel(article)
    hero_alt = article.get("hero_alt") or f"Editorial studio photograph illustrating {article['title']}"
    hero_caption = article.get("hero_caption") or f"Editorial visual reference for {article['title']}. Technical floor geometry and worked values appear in the schematic and tables below."

    siblings = sorted(
        [a for a in all_articles if a["category"] == cat and a["slug"] != slug],
        key=lambda a: (a["published_date"], a["slug"]),
        reverse=True,
    )[:3]
    sections = article["sections_html"].replace(
        '<div class="table-wrap">',
        '<div class="table-wrap" role="region" aria-label="Comparison table" tabindex="0">',
    )

    faq_html = ""
    faqs = article.get("faqs") or []
    if faqs:
        items_html = "\n".join(
            f"""            <div class="faq-item">
              <h3>{html.escape(item['question'])}</h3>
              <p>{html.escape(item['answer'])}</p>
            </div>"""
            for item in faqs
        )
        faq_html = f"""
          <section class="faq-section" aria-labelledby="faq-heading">
            <h2 id="faq-heading">Frequently Asked Questions</h2>
{items_html}
          </section>"""

    rel_list = []
    for s in siblings:
        s_alt = s.get("hero_alt") or f"Editorial photograph for {s['title']}"
        rel_list.append(
            f"""          <article class="card">
            <div>
              <a class="card-thumb-link" href="../{html.escape(s['slug'])}/">
                <img class="card-thumb" src="../../{html.escape(article_image_rel(s))}" alt="{html.escape(s_alt)}" width="1200" height="800" loading="lazy" decoding="async">
              </a>
              <div class="card-meta">{html.escape(cat_label)} · {s['reading_minutes']} min read</div>
              <h3><a href="../{html.escape(s['slug'])}/">{html.escape(s['title'])}</a></h3>
            </div>
            <p>{html.escape(s['lead_summary'])}</p>
          </article>"""
        )
    related_cards = "\n".join(rel_list)

    body = f"""      <nav class="breadcrumbs" aria-label="Breadcrumb">
        <a href="../../">Home</a> / <a href="../">{html.escape(cat_label)}</a> / <span aria-current="page">{html.escape(article['title'])}</span>
      </nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">{html.escape(CATEGORIES[cat]['eyebrow'])}</p>
          <h1>{html.escape(article['title'])}</h1>
          <div class="byline">By <strong>EMFLS Editorial Desk</strong> · Published <time datetime="{pub_date}">{format_date_label(pub_date)}</time> · {article['reading_minutes']} min read ({article['word_count']:,} words)</div>
          <figure class="hero-photo">
            <img src="../../{html.escape(img_rel)}" alt="{html.escape(hero_alt)}" width="1200" height="800" loading="eager" decoding="async">
            <figcaption>{html.escape(hero_caption)}</figcaption>
          </figure>
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
          {sections}{faq_html}
        </div>
        <aside class="related-panel" aria-labelledby="related-heading">
          <h2 id="related-heading" style="margin-top:0">Related {html.escape(cat_label)} Guides</h2>
          <div class="grid-3">
{related_cards}
          </div>
        </aside>
      </article>"""

    canon = f"{SITE_ORIGIN}/{cat}/{slug}/"
    ld: list[dict] = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article["title"],
            "description": article["meta_description"],
            "image": f"{SITE_ORIGIN}/{img_rel}",
            "datePublished": pub_date,
            "dateModified": upd_date,
            "author": {"@type": "Organization", "name": "EMFLS Editorial Desk", "url": f"{SITE_ORIGIN}/about/"},
            "publisher": {"@type": "Organization", "name": "EMFLS Studio Journal", "url": f"{SITE_ORIGIN}/"},
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
    if faqs:
        ld.append(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": item["question"],
                        "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
                    }
                    for item in faqs
                ],
            }
        )
    return wrap_page(
        title=f"{article['title']} — EMFLS Studio Journal",
        description=article["meta_description"],
        canonical_path=f"{cat}/{slug}/",
        depth=2,
        body_html=body,
        active_rel=f"{cat}/",
        og_type="article",
        og_image_rel=img_rel,
        og_image_alt=hero_alt,
        json_ld=ld,
    )


def build_trust_pages(latest_date: str, article_count: int) -> dict[str, tuple[str, str, str, list[dict]]]:
    latest_label = format_date_label(latest_date)
    pages: dict[str, tuple[str, str, str, list[dict]]] = {}

    pages["about"] = (
        "About EMFLS Studio Journal",
        "Learn who publishes EMFLS Studio Journal, our studio bench verification process, and how our lighting, design, and studio reference guides are built.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">About</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Publication Profile · {article_count} Reference Guides</p>
          <h1>About EMFLS Studio Journal</h1>
          <figure class="hero-photo">
            <img src="../assets/images/og-home.webp" alt="EMFLS Studio Journal minimalist workbench with calibrated camera body, gray card, brass ruler, and linen sketchbook" width="1200" height="800" loading="eager" decoding="async">
            <figcaption>EMFLS Studio Journal publishes reproducible field guides built around physical measurements, clean schematics, and small-room constraints.</figcaption>
          </figure>
          <p class="lead-callout">EMFLS Studio Journal is an independent technical publication dedicated to practical photography lighting geometry, accessible digital typography and color systems, and small-room studio ergonomics and acoustics.</p>
          <h2>Why We Focus on Physical &amp; Visual Fundamentals</h2>
          <p>Independent photographers, designers, educators, and solo studio creators work in real rooms—often spare bedrooms, shared offices, or compact desks under three by four metres—rather than commercial soundstages with unlimited rigging space. Many frustrating creative issues stem from a handful of measurable physical factors: window light falling off too steeply across a portrait, clipped skin highlights under mixed Kelvin fixtures, muddy print proofs exported from wide-gamut displays, resonant bass reflections in untreated corners, or web diagrams whose color contrast fails WCAG legibility thresholds.</p>
          <p>Instead of repeating vague gear opinions or affiliate product roundups, every EMFLS Studio Journal article breaks a recurring studio problem down to repeatable numbers, plain floor geometry, and step-by-step verification checks. Our guides explain how to meter incident light loss in photographic stops, compute WCAG relative luminance contrast ratios, compare sRGB and Display P3 color boundaries, position first-reflection broadband acoustic panels using a hand mirror, and establish durable plain-text project archives.</p>
          <h2>How Each Field Guide Is Structured &amp; Verified</h2>
          <p>Before a guide enters our main archive, the EMFLS Editorial Desk follows a consistent four-part format designed so any reader can reproduce and audit the result with ordinary tools:</p>
          <ol>
            <li><strong>Defined room or digital baseline:</strong> Every article states the working assumptions—room dimensions, modifier size, color space, viewing distance, or microphone capsule pattern—up front so numbers are never presented out of context.</li>
            <li><strong>Scaled schematic &amp; visual reference:</strong> Each guide pairs an editorial studio visual with an accessible inline SVG technical schematic (expandable to full 720-pixel width with keyboard scrolling) so spatial relationships are immediately clear on both phones and desktop monitors.</li>
            <li><strong>Worked numerical table:</strong> Real ratios—such as stop falloff by distance, Kelvin shift steps, typographic modular scales, or microphone proximity bass boost—are laid out in scannable reference tables.</li>
            <li><strong>Reproducible field checklist:</strong> Every article closes with concrete inspection steps so you can test the method on your own camera, display, or room acoustics rather than taking any number on faith.</li>
          </ol>
          <h2>Core Editorial Sections</h2>
          <ul>
            <li><a href="../lighting/"><strong>Lighting &amp; Optics</strong></a>: Directional window diffusion, softbox inverse-square falloff, tabletop product shadow control, Kelvin color reconciliation, focal-length perspective compression, histogram reading, and RAW highlight headroom.</li>
            <li><a href="../design/"><strong>Design &amp; Color</strong></a>: Modular typographic scales, WCAG luminance contrast palettes, clear SVG diagramming rules, print versus screen color spaces, responsive editorial CSS grids, and deliberate whitespace hierarchy.</li>
            <li><a href="../studio/"><strong>Studio Workflow</strong></a>: Small-room first-reflection acoustic treatment, microphone distance and proximity control, monitor bias-lighting calibration, ergonomic desk geometry, non-destructive media file naming, and plain-text archiving.</li>
          </ul>
          <h2>Editorial Team, Cadence &amp; Accountability</h2>
          <p>EMFLS Studio Journal is independently published and maintained by the <strong>EMFLS Editorial Desk</strong> as an ad-supported educational publication. We publish new original field guides on an ongoing schedule and periodically revise existing articles when technical standards (such as WCAG specifications, color profile workflows, or display calibration practices) evolve. All substantial technical revisions update the visible publication record and sitemap modification date.</p>
          <p>Have a calculation correction, accessibility issue, or topic suggestion? Reach our editors directly via email at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> or review our full channels on the <a href="../contact/">Contact page</a> and <a href="../editorial-policy/">Editorial Policy</a>.</p>
        </div>
      </article>""",
        [
            {
                "@context": "https://schema.org",
                "@type": "AboutPage",
                "name": "About EMFLS Studio Journal",
                "url": f"{SITE_ORIGIN}/about/",
                "mainEntity": {
                    "@type": "Organization",
                    "name": "EMFLS Studio Journal",
                    "url": f"{SITE_ORIGIN}/",
                    "email": CONTACT_EMAIL,
                },
            }
        ],
    )

    pages["editorial-policy"] = (
        "Editorial Policy & Verification Standards",
        "How EMFLS Studio Journal verifies lighting math, color contrast tables, original diagrams, editorial independence, and reader corrections.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Editorial Policy</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Standards &amp; Accountability · Updated {latest_label}</p>
          <h1>Editorial Policy</h1>
          <p class="lead-callout">Every reference guide on EMFLS Studio Journal is written so a practitioner can reproduce the geometry, check the underlying math, and verify the visual or acoustic outcome in their own workspace.</p>
          <h2>1. Measurement Transparency &amp; Worked Examples</h2>
          <p>Worked tables and stop calculations across our Lighting, Design, and Studio sections illustrate optical, acoustic, or mathematical relationships under stated baseline assumptions—for instance, a fixed 1.20 m backdrop distance, a standard 6500 K viewing white point, or WCAG 2.x relative luminance formulas. Real studio outcomes always depend on wall paint reflectance, window orientation, lens transmission, display gamut, and room dimensions. We clearly label baseline assumptions and encourage readers to confirm target values with their own light meter, colorimeter, or reference test chart.</p>
          <h2>2. Editorial Independence &amp; Advertising Separation</h2>
          <p>EMFLS Studio Journal is reader-first and maintains a strict firewall between editorial content and display advertising. We do not accept paid article placements, undisclosed sponsorships, paid link insertions, or free-hardware review exchanges. Whenever a camera format, color space, modifier shape, or file convention is named in a guide, it appears purely to illustrate a physical, optical, or workflow principle—never as a paid endorsement.</p>
          <p>Advertising revenue from Google AdSense helps support ongoing research, writing, and hosting. Advertisers have zero influence over topic selection, conclusions, diagrams, or corrections.</p>
          <h2>3. Original Photography, Schematics &amp; Accessibility</h2>
          <p>Each guide pairs high-resolution visual references with custom scalable vector schematics (`720 × 320` viewBox) accompanied by descriptive alternative text and readable captions. Every schematic includes a “Show full-size diagram” toggle and keyboard-scrollable viewport so mobile readers and assistive-technology users can inspect small angle markers and meter values without clipping or zooming glitches.</p>
          <h2>4. Fact-Checking, Updates &amp; Substantive Revisions</h2>
          <p>Before publication, every article passes automated structural, HTML, link-integrity, schema, and reading-clarity checks in addition to editorial review of equations, units, and standards citations (including W3C WCAG specifications, IEC sRGB / Display P3 definitions, and standard photographic exposure formulas).</p>
          <ul>
            <li><strong>Substantive corrections or updates:</strong> When a formula, threshold, or technical standard changes, we update the text, recalculate affected tables, and refresh the guide's visible modification date.</li>
            <li><strong>Minor maintenance edits:</strong> Typographical fixes, spacing improvements, or broken-link repairs are deployed promptly without inflating publication dates.</li>
          </ul>
          <h2>5. Reader Corrections &amp; Feedback Process</h2>
          <p>We welcome technical scrutiny from working photographers, designers, and engineers. If you spot a calculation slip, ambiguous diagram label, broken internal link, or accessibility barrier, email us directly at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> or open a public report on our <a href="../contact/">Contact page</a>. Include the article URL and the specific table row or schematic label; we review and respond to actionable technical reports within 2 to 4 business days.</p>
        </div>
      </article>""",
        [
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": "Editorial Policy — EMFLS Studio Journal",
                "url": f"{SITE_ORIGIN}/editorial-policy/",
            }
        ],
    )

    pages["privacy-policy"] = (
        "Privacy Policy",
        "What GitHub Pages and Google AdSense collect when you visit EMFLS Studio Journal and how to manage ad personalization or contact us privately.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Privacy Policy</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Effective Date: {latest_label}</p>
          <h1>Privacy Policy</h1>
          <p class="lead-callout">This policy explains how our host, advertising partners, and editorial email channel process data when you visit www.emfls.com.</p>
          <h2>1. Hosting &amp; Static Site Search</h2>
          <p>GitHub Pages hosts this static site. GitHub logs and stores visitors’ Internet Protocol (IP) addresses for security and reliability, including visits by people who are signed out of GitHub. See <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection">GitHub Pages data collection</a> and the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub Privacy Statement</a>.</p>
          <p>Reading the site requires no account, login, or newsletter signup. On-site search downloads a static article index JSON file and filters your search query locally inside your browser without transmitting search terms to an external database.</p>
          <h2>2. Google AdSense &amp; Third-Party Advertising Cookies</h2>
          <p>This site integrates <strong>Google AdSense</strong> to support independent publishing. When advertising services load, your browser shares standard technical information with Google, including the page URL and IP address. Third-party vendors, including Google, use cookies, web beacons, or similar identifiers to serve ads based on a user’s prior visits to this website or other websites.</p>
          <p>Google’s use of advertising cookies enables Google and its partners to serve ads based on your visits to this site and/or other sites on the internet, measure ad performance, and help prevent fraud or invalid traffic. Read <a href="https://policies.google.com/technologies/partner-sites">how Google uses data from sites and apps that use its services</a>.</p>
          <h2>3. Your Advertising &amp; Cookie Choices</h2>
          <ul>
            <li>Opt out of personalized advertising from Google via <a href="https://adssettings.google.com/">Google Ad Settings</a>.</li>
            <li>Opt out of third-party vendor personalized advertising cookies via <a href="https://www.aboutads.info/choices/">YourAdChoices (aboutads.info)</a>.</li>
            <li>Clear or block cookies at any time through your browser privacy controls.</li>
          </ul>
          <h2>4. Direct Email Correspondence</h2>
          <p>If you email the EMFLS Editorial Desk at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>, your email provider and ours process your address and message content solely to read and reply to your inquiry. We do not sell, rent, or add reader email addresses to marketing lists. Please do not include sensitive financial, medical, or account credentials in email correspondence.</p>
          <h2>5. Children's Information</h2>
          <p>EMFLS Studio Journal is a general technical reference resource intended for creative practitioners and does not knowingly collect personally identifiable information from children under the age of 13.</p>
          <h2>6. Privacy Requests &amp; Policy Updates</h2>
          <p>For data handled by our host or advertising provider, see the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub Privacy Statement</a> or <a href="https://policies.google.com/privacy">Google Privacy Policy</a>. For site-specific privacy questions or removal of email correspondence, write directly to <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> or review the <a href="../contact/">Contact page</a>.</p>
        </div>
      </article>""",
        [
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": "Privacy Policy — EMFLS Studio Journal",
                "url": f"{SITE_ORIGIN}/privacy-policy/",
            }
        ],
    )

    pages["terms"] = (
        "Terms of Use & Reference Disclaimer",
        "Terms governing your access to EMFLS Studio Journal guides, studio photographs, vector schematics, and educational technical examples.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Terms of Use</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Last Updated: {latest_label}</p>
          <h1>Terms of Use</h1>
          <p class="lead-callout">By reading or referencing materials on EMFLS Studio Journal (www.emfls.com), you agree to the educational usage terms and disclaimers summarized below.</p>
          <h2>1. Educational &amp; Informational Purpose</h2>
          <p>All articles, exposure charts, color contrast guidelines, acoustic placement steps, and ergonomic geometry ranges published on this website are provided strictly for general educational reference. Workspace safety, overhead electrical rigging for studio lights, acoustic wall mounting hardware, and personal physical comfort should always be verified against equipment manufacturer safety manuals and qualified local professionals where applicable.</p>
          <h2>2. Intellectual Property &amp; Fair Citation</h2>
          <p>Original article text, layout styles, studio photographs, and scalable vector diagrams created for EMFLS Studio Journal remain the intellectual property of EMFLS Studio Journal unless otherwise noted. Brief excerpts or links for non-commercial educational citation are welcome with clear attribution back to the canonical URL. Republishing complete guides, tables, or image sets without written permission is prohibited.</p>
          <h2>3. External Reference Links</h2>
          <p>Links to external reference standards (such as W3C WCAG documentation, optical photometry specifications, or browser privacy settings pages) are provided strictly for reader convenience and independent verification. We do not control, endorse, or assume responsibility for the ongoing availability, accuracy, or privacy policies of third-party websites.</p>
          <h2>4. Editorial Updates, Revisions &amp; Correction Policy</h2>
          <p>Technical standards, browser rendering engines, and LED measurement benchmarks evolve over time. Every field guide displays both its original publication date and its most recent substantive review date. When readers or internal checks surface an arithmetic typo, broken anchor, or outdated browser behavior, we correct the affected guide directly and update its revision timestamp rather than silently deleting reference pages.</p>
          <h2>5. Availability &amp; Limitation of Liability</h2>
          <p>EMFLS Studio Journal is published as a free static reference library on an &ldquo;as-is&rdquo; basis without warranties of uninterrupted uptime or fitness for a specific commercial installation. Neither EMFLS Studio Journal nor its contributors shall be liable for indirect damages, equipment misuse, or production losses arising from applying general workshop examples without local testing.</p>
          <h2>6. Permissions &amp; Contact Regarding Terms</h2>
          <p>For permissions inquiries, copyright notices, or questions regarding these terms, write directly to <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> or visit our <a href="../contact/">Contact page</a>.</p>
        </div>
      </article>""",
        [
            {
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": "Terms of Use — EMFLS Studio Journal",
                "url": f"{SITE_ORIGIN}/terms/",
            }
        ],
    )

    pages["contact"] = (
        "Contact EMFLS Editorial Desk",
        "Reach the EMFLS Studio Journal editorial desk by direct email or public GitHub issue for corrections, accessibility reports, or inquiries.",
        f"""      <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../">Home</a> / <span aria-current="page">Contact</span></nav>
      <article class="article-shell">
        <div class="article-body">
          <p class="eyebrow">Reader Support &amp; Corrections</p>
          <h1>Contact Us</h1>
          <p class="lead-callout">Have a technical correction, accessibility report, diagram question, or privacy request? Contact the EMFLS Editorial Desk directly by email at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> or log a reproducible technical issue on GitHub.</p>
          <h2>Direct Editorial Email (Private Channel)</h2>
          <p>For editorial questions, privacy inquiries, copyright notices, or feedback you prefer to keep private, email <a href="mailto:{CONTACT_EMAIL}"><strong>{CONTACT_EMAIL}</strong></a>. We review incoming messages regularly and aim to respond to actionable editorial and privacy inquiries within <strong>2 to 4 business days</strong>.</p>
          <h2>Public Technical Correction Tracker</h2>
          <p>For open technical corrections—such as an equation check, broken link, table typo, or mobile layout defect—you can also open an issue in the <a href="https://github.com/emfls/emfls-com/issues">public EMFLS Studio Journal GitHub issue tracker</a> so fixes remain publicly auditable. Posting on GitHub requires a free GitHub account; existing reports remain publicly readable without signing in.</p>
          <h2>Choose the Best Channel</h2>
          <div class="table-wrap" role="region" aria-label="Contact channel routing" tabindex="0">
            <table>
              <thead>
                <tr><th scope="col">Inquiry Type</th><th scope="col">Recommended Channel</th><th scope="col">Target Review Window</th></tr>
              </thead>
              <tbody>
                <tr><th scope="row">Calculation or technical standard correction</th><td>Direct email or GitHub issue</td><td>2–4 business days</td></tr>
                <tr><th scope="row">Diagram accessibility or mobile layout defect</th><td>GitHub issue or direct email</td><td>2–4 business days</td></tr>
                <tr><th scope="row">Privacy, copyright, or permissions request</th><td>Direct email (<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>)</td><td>2–4 business days</td></tr>
                <tr><th scope="row">New studio guide topic suggestion</th><td>Direct email or GitHub issue</td><td>Reviewed monthly during editorial planning</td></tr>
              </tbody>
            </table>
          </div>
          <h2>Helpful Details to Include</h2>
          <ul>
            <li>The full article URL on <code>www.emfls.com</code>.</li>
            <li>The exact heading, table row, or diagram label you are referencing.</li>
            <li>For layout or accessibility bugs, your browser name and approximate viewport width (for example, mobile 375 px or desktop 1440 px).</li>
          </ul>
          <h2>How Editorial Corrections Are Verified &amp; Logged</h2>
          <p>When you flag a technical discrepancy—such as a lighting falloff calculation, contrast ratio, or CSS layout rule—our editorial desk reproduces the exact conditions on calibrated test fixtures or browser viewports before editing the source file. Confirmed fixes are rebuilt across the static site, validated against automated accessibility and broken-link checks, and reflected in the article&rsquo;s updated revision date.</p>
          <p>Please note that we do not accept paid guest posts, sponsored product placements, or paid link exchanges. Keep confidential passwords or sensitive personal documents out of both email and public GitHub reports. See our <a href="../privacy-policy/">Privacy Policy</a> and <a href="../editorial-policy/">Editorial Policy</a> for full details.</p>
        </div>
      </article>""",
        [
            {
                "@context": "https://schema.org",
                "@type": "ContactPage",
                "name": "Contact EMFLS Studio Journal",
                "url": f"{SITE_ORIGIN}/contact/",
                "mainEntity": {
                    "@type": "Organization",
                    "name": "EMFLS Studio Journal",
                    "email": CONTACT_EMAIL,
                    "url": f"{SITE_ORIGIN}/",
                },
            }
        ],
    )
    return pages


def build_404(style_text: str, articles: list[dict]) -> str:
    cat_counts = {c: sum(1 for a in articles if a["category"] == c) for c in CATEGORIES}
    body = f"""      <section class="hero">
        <p class="eyebrow">Page Not Found (404)</p>
        <h1>This URL has moved or been retired</h1>
        <p class="lead">EMFLS Studio Journal is organized into field guides covering Lighting &amp; Optics, Design &amp; Color, and Studio Workflow. Use the search below or browse any section directly.</p>
        <form id="studio-search-form" class="search-box" role="search">
          <input id="studio-search-input" type="search" aria-label="Search current field guides" placeholder="Try softbox, lighting, or contrast">
          <button type="submit">Search</button>
        </form>
        <div id="studio-search-results" class="search-results" role="region" aria-live="polite" aria-label="Search results"></div>
      </section>
      <section aria-labelledby="recover-title">
        <h2 id="recover-title">Browse Current Sections</h2>
        <div class="grid-3">
          <article class="card">
            <div><div class="card-meta">{cat_counts['lighting']} Guides</div><h3><a href="/lighting/" data-nav-rel="lighting/">Lighting &amp; Optics</a></h3></div>
            <p>Window diffusion angles, softbox falloff math, Kelvin balance, focal length geometry, and RAW dynamic range.</p>
          </article>
          <article class="card">
            <div><div class="card-meta">{cat_counts['design']} Guides</div><h3><a href="/design/" data-nav-rel="design/">Design &amp; Color</a></h3></div>
            <p>Modular type scales, WCAG contrast pairs, clean SVG diagramming, and responsive CSS grids.</p>
          </article>
          <article class="card">
            <div><div class="card-meta">{cat_counts['studio']} Guides</div><h3><a href="/studio/" data-nav-rel="studio/">Studio Workflow</a></h3></div>
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


def build_rss(articles: list[dict], latest_date: str) -> str:
    ordered = sorted(articles, key=lambda a: (a["updated_date"], a["published_date"], a["slug"]), reverse=True)
    items = []
    for a in ordered:
        link = f"{SITE_ORIGIN}/{a['category']}/{a['slug']}/"
        items.append(
            f"""    <item>
      <title>{html.escape(a['title'])}</title>
      <link>{html.escape(link)}</link>
      <guid isPermaLink="true">{html.escape(link)}</guid>
      <pubDate>{format_rfc822(a['published_date'])}</pubDate>
      <description>{html.escape(a['meta_description'])}</description>
    </item>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>EMFLS Studio Journal</title>
    <link>{SITE_ORIGIN}/</link>
    <description>Independent field guides covering photography lighting, editorial design systems, and studio workflow craft.</description>
    <language>en-us</language>
    <lastBuildDate>{format_rfc822(latest_date)}</lastBuildDate>
    <atom:link href="{SITE_ORIGIN}/rss.xml" rel="self" type="application/rss+xml" />
{chr(10).join(items)}
  </channel>
</rss>
"""


def main() -> int:
    articles = load_articles()
    latest_date = max(a["updated_date"] for a in articles)
    style_text = (ROOT / "assets/style.css").read_text(encoding="utf-8")

    for cat in CATEGORIES:
        cat_dir = ROOT / cat
        cat_dir.mkdir(parents=True, exist_ok=True)
        (cat_dir / "index.html").write_text(build_category_page(cat, CATEGORIES[cat], articles), encoding="utf-8")

    (ROOT / "index.html").write_text(build_home(articles, latest_date), encoding="utf-8")

    for article in articles:
        art_dir = ROOT / article["category"] / article["slug"]
        art_dir.mkdir(parents=True, exist_ok=True)
        (art_dir / "index.html").write_text(build_article_page(article, articles), encoding="utf-8")

    trust = build_trust_pages(latest_date, len(articles))
    for slug, (title, desc, body, ld) in trust.items():
        t_dir = ROOT / slug
        t_dir.mkdir(parents=True, exist_ok=True)
        html_doc = wrap_page(
            title=f"{title} — EMFLS Studio Journal",
            description=desc,
            canonical_path=f"{slug}/",
            depth=1,
            body_html=body,
            active_rel=f"{slug}/",
            og_image_rel="assets/images/og-home.webp",
            json_ld=ld,
        )
        (t_dir / "index.html").write_text(html_doc, encoding="utf-8")

    (ROOT / "404.html").write_text(build_404(style_text, articles), encoding="utf-8")
    (ROOT / "rss.xml").write_text(build_rss(articles, latest_date), encoding="utf-8")

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
            "published_date": a["published_date"],
            "summary": a["lead_summary"],
            "description": a["meta_description"],
        }
        for a in sorted(articles, key=lambda x: (x["published_date"], x["slug"]), reverse=True)
    ]
    (ROOT / "search-index.json").write_text(json.dumps(search_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    url_entries: list[tuple[str, str]] = [("", latest_date)]
    for c in CATEGORIES:
        cat_latest = max(a["updated_date"] for a in articles if a["category"] == c)
        url_entries.append((f"{c}/", cat_latest))
    for a in articles:
        url_entries.append((f"{a['category']}/{a['slug']}/", a["updated_date"]))
    for s in trust:
        url_entries.append((f"{s}/", latest_date))

    url_blocks = "\n".join(
        f"  <url><loc>{SITE_ORIGIN}/{u}</loc><lastmod>{lm}</lastmod></url>" for u, lm in url_entries
    )
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{url_blocks}
</urlset>
"""
    (ROOT / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")
    (ROOT / "README.md").write_text(
        "# EMFLS Studio Journal\n\nIndependent static reference publication covering photography lighting, editorial design systems, and studio workflow craft.\n",
        encoding="utf-8",
    )
    print(f"BUILT: 1 home + 3 categories + {len(articles)} articles + {len(trust)} trust pages = {len(url_entries)} canonical URLs (+ 404.html & rss.xml)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
