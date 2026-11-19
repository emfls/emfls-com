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
        a = dict(attrs)
        if t == "h1":
            self.h1 += 1
        elif t == "h2":
            self.h2 += 1
        elif t == "svg":
            self.svg += 1
            self._skip = True
        elif t == "table":
            self.table += 1
        elif t == "ins":
            self.ins += 1
        elif t == "a" and a.get("href"):
            self.links.append(str(a["href"]))
        elif t == "link" and a.get("href") and a.get("rel") == "stylesheet":
            self.links.append(str(a["href"]))
        elif t == "script":
            if a.get("type") == "application/ld+json":
                self._in_ld = True
                self._ld_buf = []
            elif a.get("src") and not str(a["src"]).startswith("http"):
                self.links.append(str(a["src"]))
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
        # Only allowed on 404.html where dynamic_nav rewrites data-nav-rel
        return source_file.name == "404.html"
    clean = unquote(href.split("#", 1)[0].split("?", 1)[0])
    target = (source_file.parent / clean).resolve()
    if clean.endswith("/") or target.is_dir():
        return (target / "index.html").is_file()
    return target.is_file()


def main() -> int:
    for req in (".nojekyll", "ads.txt", "robots.txt", "sitemap.xml", "search-index.json", "404.html"):
        assert (ROOT / req).is_file(), f"Missing required root file: {req}"
    assert "pub-8830524482034754" in (ROOT / "ads.txt").read_text(encoding="utf-8")
    assert not (ROOT / "CNAME").exists(), "CNAME must not exist during staging preview before Gabia DNS change"

    sm_root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    sm_locs = [el.text or "" for el in sm_root.iter() if el.tag.endswith("loc")]
    assert len(sm_locs) == 27, f"Expected 27 sitemap URLs, got {len(sm_locs)}"

    html_files = sorted(ROOT.rglob("*.html"))
    assert len(html_files) == 28, f"Expected 28 HTML files (27 canonical + 404.html), got {len(html_files)}"

    article_count = 0
    for f in html_files:
        raw = f.read_text(encoding="utf-8")
        assert f'<meta name="google-adsense-account" content="{ADSENSE_PUB}">' in raw, f"Missing AdSense meta in {f}"
        assert f"pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB}" in raw, f"Missing AdSense loader in {f}"

        p = PageInspector()
        p.feed(raw)
        assert p.h1 == 1, f"{f}: h1 count {p.h1} != 1"
        assert p.ins == 0, f"{f}: expected 0 <ins> tags during review, got {p.ins}"
        for ld_raw in p.json_ld:
            json.loads(ld_raw)
        for href in p.links:
            assert check_relative_target(f, href), f"{f}: broken relative link '{href}'"

        rel = f.relative_to(ROOT)
        if len(rel.parts) == 3 and rel.parts[0] in ("lighting", "design", "studio") and rel.name == "index.html":
            article_count += 1
            assert p.visible_words >= 1100, f"{rel}: visible_words={p.visible_words} < 1100"
            assert p.svg >= 1, f"{rel}: missing inline <svg>"
            assert p.table >= 1, f"{rel}: missing <table>"
            assert p.h2 >= 4, f"{rel}: h2={p.h2} < 4"
            assert len(p.json_ld) == 2, f"{rel}: expected Article + BreadcrumbList JSON-LD"
            low = raw.lower()
            for token in FORBIDDEN:
                assert token not in low, f"{rel}: forbidden token '{token}'"

    assert article_count == 18, f"Expected 18 article pages, audited {article_count}"
    print(f"QA_SITE_PASS: {len(html_files)} HTML pages ({article_count} deep articles, 27 sitemap URLs), 0 errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
