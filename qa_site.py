#!/usr/bin/env python3
"""Static site QA validator for EMFLS Studio Journal."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
ADSENSE_PUB = "ca-pub-8830524482034754"
CONTACT_EMAIL = "emfls24777@daum.net"
FORBIDDEN = (
    "lorem",
    "coming soon",
    "as an ai",
    "chatgpt",
    "openai",
    "claude",
    "/users/",
    "obsidian",
    "**",
)


class PageInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.h1 = 0
        self.h2 = 0
        self.svg = 0
        self.imgs: list[dict[str, str]] = []
        self.table = 0
        self.ins = 0
        self.links: list[str] = []
        self.json_ld: list[str] = []
        self._in_ld = False
        self._ld_buf: list[str] = []
        self._skip = False
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        a = {k: (v or "") for k, v in attrs}
        if t == "h1":
            self.h1 += 1
        elif t == "h2":
            self.h2 += 1
        elif t == "svg":
            self.svg += 1
            self._skip = True
        elif t == "img":
            self.imgs.append(a)
            if a.get("src"):
                self.links.append(a["src"])
        elif t == "table":
            self.table += 1
        elif t == "ins":
            self.ins += 1
        elif t == "a" and a.get("href"):
            self.links.append(a["href"])
        elif t == "link" and a.get("href") and a.get("rel") == "stylesheet":
            self.links.append(a["href"])
        elif t == "script":
            if a.get("type") == "application/ld+json":
                self._in_ld = True
                self._ld_buf = []
            elif a.get("src") and not a["src"].startswith("http"):
                self.links.append(a["src"])
            self._skip = True
        elif t == "style":
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t == "script":
            if self._in_ld:
                self.json_ld.append("".join(self._ld_buf))
                self._in_ld = False
            self._skip = False
        elif t in ("svg", "style"):
            self._skip = False

    def handle_data(self, data: str) -> None:
        if self._in_ld:
            self._ld_buf.append(data)
        elif not self._skip:
            self._text.append(data)

    @property
    def visible_words(self) -> int:
        return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.-]*", " ".join(self._text)))


def check_relative_target(source_file: Path, href: str) -> bool:
    if href.startswith(("http://", "https://", "mailto:", "#", "tel:")):
        return True
    if href.startswith("/"):
        return source_file.name == "404.html"
    clean = unquote(href.split("#", 1)[0].split("?", 1)[0])
    target = (source_file.parent / clean).resolve()
    if clean.endswith("/") or target.is_dir():
        return (target / "index.html").is_file()
    return target.is_file()


def main() -> int:
    for req in (".nojekyll", "ads.txt", "robots.txt", "sitemap.xml", "rss.xml", "search-index.json", "404.html"):
        assert (ROOT / req).is_file(), f"Missing required root file: {req}"
    assert "pub-8830524482034754" in (ROOT / "ads.txt").read_text(encoding="utf-8")
    assert (ROOT / "CNAME").is_file(), "Missing CNAME for www.emfls.com production binding"
    assert (ROOT / "CNAME").read_text(encoding="utf-8").strip() == "www.emfls.com", "Unexpected CNAME content"

    content_files = sorted((ROOT / "content").glob("*__*.json"))
    expected_articles = len(content_files)
    assert expected_articles >= 19, f"Expected >= 19 articles, found {expected_articles}"
    expected_sitemap = 1 + 3 + expected_articles + 5

    sm_root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    sm_locs = [el.text or "" for el in sm_root.iter() if el.tag.endswith("loc")]
    assert len(sm_locs) == expected_sitemap, f"Expected {expected_sitemap} sitemap URLs, got {len(sm_locs)}"

    rss_root = ET.fromstring((ROOT / "rss.xml").read_text(encoding="utf-8"))
    rss_items = [el for el in rss_root.iter() if el.tag.endswith("item")]
    assert len(rss_items) == expected_articles, f"Expected {expected_articles} RSS items, got {len(rss_items)}"

    html_files = sorted(ROOT.rglob("*.html"))
    assert len(html_files) == expected_sitemap + 1, f"Expected {expected_sitemap + 1} HTML files, got {len(html_files)}"

    article_count = 0
    for f in html_files:
        raw = f.read_text(encoding="utf-8")
        if f.name == "404.html":
            assert "adsbygoogle.js" not in raw, f"Forbidden adsbygoogle.js runtime in {f}"
            assert "pagead2.googlesyndication.com" not in raw, f"Forbidden pagead runtime host in {f}"
            assert "google-adsense-account" not in raw, f"Forbidden AdSense meta in {f}"
        else:
            assert f'<meta name="google-adsense-account" content="{ADSENSE_PUB}">' in raw, f"Missing AdSense meta in {f}"
            assert f"pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB}" in raw, f"Missing AdSense loader in {f}"
            assert '<meta property="og:image" content="https://www.emfls.com/assets/images/' in raw, f"Missing og:image in {f}"
            assert '<meta name="twitter:card" content="summary_large_image">' in raw, f"Missing twitter:card in {f}"

        p = PageInspector()
        p.feed(raw)
        assert p.h1 == 1, f"{f}: h1 count {p.h1} != 1"
        assert p.ins == 0, f"{f}: expected 0 <ins> tags during review, got {p.ins}"
        for ld_raw in p.json_ld:
            json.loads(ld_raw)
        for img in p.imgs:
            assert img.get("alt"), f"{f}: image missing alt text"
            assert img.get("width") and img.get("height"), f"{f}: image missing explicit width/height"
        for href in p.links:
            assert check_relative_target(f, href), f"{f}: broken relative link/asset '{href}'"

        rel = f.relative_to(ROOT)
        if len(rel.parts) == 3 and rel.parts[0] in ("lighting", "design", "studio") and rel.name == "index.html":
            article_count += 1
            assert p.visible_words >= 1100, f"{rel}: visible_words={p.visible_words} < 1100"
            assert len(p.imgs) >= 1, f"{rel}: missing bespoke editorial hero photograph <img>"
            assert p.svg >= 1, f"{rel}: missing inline <svg>"
            assert '<input type="checkbox" id="diagram-full-size"' in raw, f"{rel}: missing diagram size control"
            assert '<label for="diagram-full-size">' in raw, f"{rel}: missing label for diagram size control"
            assert '<div class="diagram-view" role="region" aria-label="Diagram" tabindex="0">' in raw, f"{rel}: missing keyboard-scrollable diagram"
            assert 'viewBox="0 0 720 320"' in raw, f"{rel}: diagram size differs from the full-size display"
            assert '<figcaption>' in raw, f"{rel}: missing readable diagram caption"
            assert p.table >= 1, f"{rel}: missing <table>"
            assert p.h2 >= 4, f"{rel}: h2={p.h2} < 4"
            assert len(p.json_ld) >= 2, f"{rel}: expected >= 2 JSON-LD blocks (Article + BreadcrumbList)"
            low = raw.lower()
            for token in FORBIDDEN:
                assert token not in low, f"{rel}: forbidden token '{token}'"

    assert article_count == expected_articles, f"Expected {expected_articles} article pages, audited {article_count}"
    about_p = PageInspector()
    about_p.feed((ROOT / "about/index.html").read_text(encoding="utf-8"))
    assert about_p.visible_words >= 500, f"About page too thin: {about_p.visible_words}"
    ed_p = PageInspector()
    ed_p.feed((ROOT / "editorial-policy/index.html").read_text(encoding="utf-8"))
    assert ed_p.visible_words >= 450, f"Editorial policy page too thin: {ed_p.visible_words}"
    privacy = (ROOT / "privacy-policy/index.html").read_text(encoding="utf-8")
    assert 'href="https://policies.google.com/technologies/partner-sites"' in privacy, "Missing Google partner data disclosure link"
    assert 'href="https://adssettings.google.com/"' in privacy, "Missing Google Ad Settings link"
    contact = (ROOT / "contact/index.html").read_text(encoding="utf-8")
    assert 'href="https://github.com/emfls/emfls-com/issues"' in contact, "Missing public corrections link"
    assert f'mailto:{CONTACT_EMAIL}' in contact, "Missing direct private email on Contact page"
    print(f"QA_SITE_PASS: {len(html_files)} HTML pages ({article_count} illustrated deep articles, {expected_sitemap} sitemap URLs, RSS valid, about={about_p.visible_words}w, editorial={ed_p.visible_words}w), 0 errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
