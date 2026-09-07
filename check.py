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

# 404.html is a page in every respect except addressing. GitHub Pages serves it
# for an unmatched path at ANY depth, so its links and assets must be
# root-absolute ("/assets/style.css") where every other page is relative. That
# makes it exempt from two checks below — link resolution reads the leading
# slash off first, and nav parity ignores it — and from the current-page marker,
# since no nav entry is ever "here" on a 404.
NOT_FOUND = "404.html"


def resolve(href: str) -> str:
    """Strip the leading slash so a root-absolute href resolves on disk."""
    return href[1:] if href.startswith("/") else href

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
        if not (ROOT / resolve(href)).exists():
            fail(f"{name}: link to missing page {href}")

    # 4. referenced assets exist.
    for src in re.findall(r'(?:src|href)="/?(assets/[^"]+)"', markup):
        if not (ROOT / src).exists():
            fail(f"{name}: missing asset {src}")

    # 5. no internal vocabulary in visible copy.
    body = visible(markup)
    for label, pattern in LEAKS.items():
        hits = set(re.findall(pattern, body, re.I))
        if hits:
            fail(f"{name}: {label} leak -> {sorted(hits)}")

    # 6. head metadata present. Without a distinct title + description of real
    #    length, two pages share a link preview and neither is findable.
    #    (Nav-label/heading agreement is check 9; this comment used to claim
    #    that by mistake after an edit moved the nav logic.)
    title = re.search(r"<title>(.*?)</title>", markup, re.S)
    if not title:
        fail(f"{name}: no <title>")
    desc = re.search(r'<meta name="description" content="([^"]+)"', markup)
    if not desc or len(desc.group(1)) < 60:
        fail(f"{name}: missing or too-short meta description")

    # 7. every page must offer a way onward. A dead-end page is a lost reader.
    if name != "index.html" and 'class="btn' not in markup:
        fail(f"{name}: no call to action")

    # 7b. a button label names the destination; it does not argue for clicking.
    #     The landing page shipped "Why this costs you money" as its primary CTA —
    #     it scolds the reader and promises a cost as the reward for the click. Two
    #     other pages pointed at the same destination under two more editorial
    #     labels ("Why it is worth running", "What this means for your company"),
    #     so the same page had three names and none of them was its name.
    #     A label may say what a thing is. It may not say whether it is worth it,
    #     what it costs the reader, or why they are wrong.
    for label in re.findall(r'<a class="btn[^"]*"[^>]*>([^<]+)</a>', markup):
        flat = re.sub(r"\s+", " ", label).strip()
        if re.match(r"(?i)^(why|what this means|whether)\b", flat):
            fail(f"{name}: CTA argues instead of naming a destination -> {flat!r}")
        if re.search(r"(?i)\bcosts? you\b|\bworth (?:it|running)\b", flat):
            fail(f"{name}: CTA editorializes -> {flat!r}")

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
#     Old names stay in the pattern: GitHub keeps redirecting them forever, so a
#     stale link still resolves to the private repo and still 404s the visitor.
PRIVATE_REPO = re.compile(
    r"github\.com/(?:e8kor/doublegate|doublegate-io/(?:design|doublegate-design))(?:[/#?]|$)")
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
    navs[page.name] = [resolve(h) for h in links]
    here = re.findall(r'class="here"', block.group(1))
    if page.name not in ("index.html", NOT_FOUND) and len(here) != 1:
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

# 14. NO ORPHANED SENTENCE FRAGMENTS IN VISIBLE COPY.
#     Stripping the links to the private design repo left two captions behind as
#     fragments — "…you do not own." followed by "a deliberate decision, not an
#     oversight" — which read as broken English and shipped that way, because
#     nothing checked prose shape. A sentence that starts lowercase after a full
#     stop, or a paragraph that never terminates, is the signature of that edit.
SENTENCE_START = re.compile(r"[.!?]\s+([a-z])")
for page in pages:
    for attrs, para in re.findall(r"(?s)<p([^>]*)>(.*?)</p>", page.read_text()):
        text = re.sub(r"\s+", " ", visible(para)).strip()
        if not text:
            continue
        # a lowercase word opening a new sentence
        for m in SENTENCE_START.finditer(text):
            frag = text[max(0, m.start() - 40): m.start() + 40]
            # tolerate deliberate lowercase: the product name, and file/URL-ish tokens
            word = re.match(r"[a-z][\w-]*", text[m.start(1):])
            if word and word.group(0) in ("doublegate", "mem0", "arxiv"):
                continue
            fail(f"{page.name}: sentence starts lowercase -> …{frag}…")
        # a visible paragraph that never terminates: the fragment's other shape.
        # Eyebrow labels and "→" link captions are deliberately unpunctuated, so
        # only prose is held to this — a paragraph with a sentence in it.
        is_label = "→" in text or "eyebrow" in attrs
        if len(text) > 40 and not is_label and text[-1] not in ".!?:;”\"')»…—":
            fail(f"{page.name}: paragraph does not end in punctuation -> …{text[-50:]}")

# 15. EVERY EVIDENCE CLAIM CARRIES A RESOLVABLE SOURCE.
#     The evidence page promises "if a claim cannot be sourced, it is marked as
#     unverified or it is not here", then shipped an <article> whose source line
#     read "Our summary, with the citation above" pointing at nothing. On the one
#     page whose entire job is citation integrity, an uncited claim is the worst
#     possible defect, so it is now an assertion.
ev = ROOT / "evidence.html"
if ev.exists():
    for art in re.findall(r"(?s)<article[^>]*>(.*?)</article>", ev.read_text()):
        heading = re.search(r"(?s)<h3[^>]*>(.*?)</h3>", art)
        label = re.sub(r"\s+", " ", visible(heading.group(1))).strip() if heading else "?"
        linked = re.search(r'<a class="src" href="(https?://[^"]+)"', art)
        if linked:
            continue
        # an unlinked source is allowed ONLY when it says so in plain words
        span = re.search(r"(?s)<span class=\"src\">(.*?)</span>", art)
        claim = re.sub(r"\s+", " ", visible(span.group(1))).lower() if span else ""
        if not any(w in claim for w in ("our survey", "our own", "unverified", "on request")):
            fail(f"evidence.html: claim without a resolvable source -> {label!r}")

# 16. THERE IS EXACTLY ONE CONTACT ADDRESS, AND EVERY PAGE HAS A WAY TO REACH IT.
#     The readiness review found no contact path anywhere on the site: no mailto,
#     no form, no signup. A product site with no way to reach anyone is a
#     brochure. Two failure modes are checked here.
#
#     (a) Drift. build.py owns EMAIL/MAILTO and injects them into the footer, but
#         pricing.html hardcodes the same address in its own CTA, because page
#         bodies are read raw and are not .format()ed — a placeholder there would
#         ship as literal "{mailto}". A second literal address is how a typo'd or
#         stale address survives a rename, so the two must agree byte for byte.
#     (b) Absence. If a page loses its footer, it loses its only contact path
#         silently. Assert every page carries the address.
build_src = (ROOT / "build.py").read_text()
declared = re.search(r'^EMAIL = "([^"]+)"', build_src, re.M)
if not declared:
    fail("build.py: no EMAIL declared — the footer contact path has no source")
else:
    addr = declared.group(1)
    if "@" not in addr or "." not in addr.split("@")[-1]:
        fail(f"build.py: EMAIL is not an address -> {addr!r}")
    for page in pages:
        markup = page.read_text()
        # <wbr> is a legal break opportunity inside a rendered address (the pricing
        # CTA uses one after the @ so a 320px screen folds it as
        # "eugene.korniichuk@ / gmail.com" instead of "…gmail.co / m"). It splits
        # the literal in the SOURCE, so strip it before matching — otherwise this
        # check silently stops protecting any page whose only copy is the split
        # one, which is exactly how a typo would slip through unnoticed.
        flat = markup.replace("<wbr>", "").replace("&shy;", "")
        if addr not in flat:
            fail(f"{page.name}: no contact address — the page is a dead end")
        # any mailto: on any page must point at the one declared address
        for got in re.findall(r'href="mailto:([^"?]+)', flat):
            if got != addr:
                fail(f"{page.name}: mailto {got!r} disagrees with build.py EMAIL {addr!r}")
        # a visible address must not be broken anywhere except immediately after
        # the @ — a fold inside the TLD renders as a typo.
        for vis in re.findall(r'>([^<>]*@[^<>]*)<wbr>([^<>]*)<', markup):
            if not vis[0].rstrip().endswith("@"):
                fail(f"{page.name}: <wbr> splits an address somewhere other than "
                     f"after the @ -> {vis[0]!r}|{vis[1]!r}")

# ---------------------------------------------------------------- report
if fails:
    print(f"FAIL — {len(fails)} problem(s):")
    for f in fails:
        print(f"  · {f}")
    sys.exit(1)

print(f"PASS — {len(pages)} pages: " + ", ".join(p.name for p in pages))
print("  tag balance · anchors · cross-page links · assets · vocabulary")
print("  metadata · calls to action · alt text · nav parity · svg motion paths")
print("  README inline HTML integrity · one contact address, reachable everywhere")
