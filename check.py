#!/usr/bin/env python3
"""Gate checks for the static site. Every check here exists because the error
happened once already.

Run:  python3 site/check.py
Exit non-zero on any failure, so it can be wired into CI as-is.
"""
from __future__ import annotations

import html as H
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT  # the site IS the repo root here

# internal vocabulary that must never reach a visitor-facing surface
LEAKS = {
    "component ID": r"\bC(?:1[01]|[1-9])\s*·",
    "tracker ID": r"\bFR-\d+",
    "store filename": r"\b(?:limbo|active|record|ledger|derivation)\.db\b",
    "invariant ID": r"\bI[1-7]\b(?!\w)",
    "ADR reference": r"ADR-\d{4}",
    "milestone code": r"\bM[0-5]\b(?!\w)",
    "trust class": r"\bT-[0-4]\b",
    "sub-level": r"\bL[0-3]b?\b(?!\w)",
    "jargon": r"\b(?:quorum|limbo|k-of-n|MCP|MemoryService|hybrid retrieval|FTS|rerank)\b",
}

fails: list[str] = []


def fail(msg: str) -> None:
    fails.append(msg)


def visible(markup: str) -> str:
    """Visible copy only: no script/style, no tags, no link targets."""
    out = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", markup)
    out = re.sub(r'\b(?:href|src|alt|content)="[^"]*"', " ", out)
    return H.unescape(re.sub(r"(?s)<[^>]+>", " ", out))


# scratch files (.tmp_*) are probes, not pages — scanning them produced 14
# bogus failures once, and worse, they got committed. Ignore them here and in
# .gitignore so neither can happen again.
pages = sorted(p for p in ROOT.glob("*.html") if not p.name.startswith(".tmp"))
if not pages:
    fail("no built pages — run python3 site/build.py")

for page in pages:
    markup = page.read_text()
    name = page.name

    # 1. tag balance. An unclosed <div> silently swallows the rest of a page.
    for tag in ("section", "div", "pre", "ul", "ol", "li", "p", "article", "table"):
        opened = len(re.findall(rf"<{tag}[\s>]", markup))
        closed = len(re.findall(rf"</{tag}>", markup))
        if opened != closed:
            fail(f"{name}: <{tag}> {opened} open vs {closed} closed")

    # 2. in-page anchors resolve.
    ids = set(re.findall(r'id="([^"]+)"', markup))
    for target in re.findall(r'href="#([^"]+)"', markup):
        if target not in ids and target != "top":
            fail(f"{name}: dead anchor #{target}")

    # 3. internal page links resolve. Six pages cross-link heavily; a renamed
    #    file used to break silently because nothing checked across pages.
    for href in re.findall(r'href="([^"#:]+\.html)(?:#[^"]*)?"', markup):
        if not (ROOT / href).exists():
            fail(f"{name}: link to missing page {href}")

    # 4. referenced assets exist.
    for src in re.findall(r'(?:src|href)="(assets/[^"]+)"', markup):
        if not (ROOT / src).exists():
            fail(f"{name}: missing asset {src}")

    # 5. no internal vocabulary in visible copy.
    body = visible(markup)
    for label, pattern in LEAKS.items():
        hits = set(re.findall(pattern, body, re.I))
        if hits:
            fail(f"{name}: {label} leak -> {sorted(hits)}")

    # 6. nav label must match the heading of the page it lands on. Four of six
    #    labels once disagreed with their target; free disorientation.
    title = re.search(r"<title>(.*?)</title>", markup, re.S)
    if not title:
        fail(f"{name}: no <title>")
    desc = re.search(r'<meta name="description" content="([^"]+)"', markup)
    if not desc or len(desc.group(1)) < 60:
        fail(f"{name}: missing or too-short meta description")

    # 7. every page must offer a way onward. A dead-end page is a lost reader.
    if name != "index.html" and 'class="btn' not in markup:
        fail(f"{name}: no call to action")

    # 8. images need real alt text — the diagram carries the whole argument.
    #    Exception: an image that merely repeats adjacent text (the brand mark
    #    beside the word "doublegate") is decorative, and the correct answer is
    #    aria-hidden + empty alt, not an invented description a screen reader
    #    would read out twice.
    for img in re.findall(r"<img[^>]*>", markup):
        if 'aria-hidden="true"' in img:
            if not re.search(r'alt=""', img):
                fail(f"{name}: aria-hidden img must have alt=\"\"")
            continue
        alt = re.search(r'alt="([^"]*)"', img)
        if not alt or len(alt.group(1)) < 25:
            fail(f"{name}: img without meaningful alt text")

# 8a. og:image and og:url MUST be absolute. Crawlers do not resolve relative
#     Open Graph URLs, so a relative one yields a link preview with no image --
#     silently, since the page itself renders fine.
for page in pages:
    markup = page.read_text()
    for prop in ("og:image", "og:url"):
        m = re.search(rf'property="{prop}" content="([^"]+)"', markup)
        if not m:
            fail(f"{page.name}: missing {prop}")
        elif not m.group(1).startswith("https://"):
            fail(f"{page.name}: {prop} must be absolute -> {m.group(1)}")

# 8b. THE SITE MUST NOT LINK INTO THE PRIVATE DESIGN REPO.
#     The site is public; the design package is not. A deep link into it renders
#     as a 404 for every visitor, and the visitor cannot tell a broken link from
#     evidence that does not exist. Primary sources are cited directly instead.
PRIVATE_REPO = re.compile(r"github\.com/(?:e8kor/doublegate|doublegate-io/doublegate-design)")
for page in pages:
    for url in re.findall(r'(?:href|src)="([^"]+)"', page.read_text()):
        if PRIVATE_REPO.search(url):
            fail(f"{page.name}: links into the private design repo -> {url}")

# 9. nav is identical on every page, and marks the current one exactly once.
navs = {}
for page in pages:
    markup = page.read_text()
    block = re.search(r"<nav>(.*?)</nav>", markup, re.S)
    if not block:
        fail(f"{page.name}: no nav")
        continue
    links = re.findall(r'href="([^"]+)"', block.group(1))
    navs[page.name] = links
    here = re.findall(r'class="here"', block.group(1))
    if page.name != "index.html" and len(here) != 1:
        fail(f"{page.name}: expected exactly 1 current-page marker, found {len(here)}")
if len({tuple(v) for v in navs.values()}) > 1:
    fail(f"nav differs between pages: {navs}")

# 10. the SVG's motion paths must resolve, or artifacts animate to nowhere.
svg_path = ROOT / "assets" / "artifact-flow.svg"
if svg_path.exists():
    svg = svg_path.read_text()
    svg_ids = set(re.findall(r'id="([^"]+)"', svg))
    for ref in re.findall(r'<mpath[^>]*(?:xlink:)?href="#([^"]+)"', svg):
        if ref not in svg_ids:
            fail(f"artifact-flow.svg: mpath -> missing #{ref}")
else:
    fail("artifact-flow.svg missing")


# 11. the repo README's inline HTML must stay well-formed. A string replacement
#     once dropped the opening <img ...> and left a bare alt= line behind, which
#     GitHub renders as literal text — invisible in a diff review.
readme = REPO / "README.md"
if readme.exists():
    text = readme.read_text()
    stray = [
        ln.strip()[:60]
        for ln in text.splitlines()
        if re.match(r'^\s*(?:alt|src|width|height)=', ln)
    ]
    if stray:
        fail(f"README.md: orphaned HTML attribute line(s) -> {stray}")
    for tag in ("p", "img"):
        if tag == "img":
            # void element: every occurrence must be a complete tag
            if text.count("<img") != len(re.findall(r"<img\b[^>]*>", text)):
                fail("README.md: unterminated <img> tag")
        else:
            o, c = len(re.findall(rf"<{tag}[\s>]", text)), len(re.findall(rf"</{tag}>", text))
            if o != c:
                fail(f"README.md: <{tag}> {o} open vs {c} closed")
    for src in re.findall(r'<img[^>]*src="(site/[^"]+)"', text):
        if not (REPO / src.removeprefix("site/")).exists():
            fail(f"README.md: missing asset {src}")

# ---------------------------------------------------------------- report
if fails:
    print(f"FAIL — {len(fails)} problem(s):")
    for f in fails:
        print(f"  · {f}")
    sys.exit(1)

print(f"PASS — {len(pages)} pages: " + ", ".join(p.name for p in pages))
print("  tag balance · anchors · cross-page links · assets · vocabulary")
print("  metadata · calls to action · alt text · nav parity · svg motion paths")
print("  README inline HTML integrity")
