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
#    Unlisted pages (build.py UNLISTED) are rendered and reachable but have no
#    nav entry, so no marker is correct for them — the same exemption the 404
#    page gets, for the same reason.
build_src_nav = (ROOT / "build.py").read_text()
unlisted = set(re.findall(r'^\s*\("([^"]+\.html)",\s*"[^"]*"\),\s*$',
                          build_src_nav.split("UNLISTED = [", 1)[1].split("]", 1)[0], re.M)) \
    if "UNLISTED = [" in build_src_nav else set()
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
    if page.name not in ("index.html", NOT_FOUND) and page.name not in unlisted and len(here) != 1:
        fail(f"{page.name}: expected exactly 1 current-page marker, found {len(here)}")
    if page.name in unlisted:
        if here:
            fail(f"{page.name}: unlisted page must not mark itself current in the nav")
        if page.name in navs[page.name]:
            fail(f"{page.name}: unlisted page appears in the nav")
        if '<meta name="robots" content="noindex">' not in markup:
            fail(f"{page.name}: unlisted page must carry noindex")
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

# 17. THE SITE SELLS THE PRODUCT; IT NEVER ANNOUNCES ITS ABSENCE.
#     On 2026-09-07 an "offering audit" carried the design repo's engineering-tier
#     honesty list onto three pages as copy — "read permissions have no design
#     yet — scheduled, not drawn", "designed, not shipped" — and every gate here
#     stayed green, because none had an opinion on phase language. Three commits
#     to unwind. The rule (site AGENTS.md rule 1): the phase is stated once, as a
#     dated release (build.py FIRST_RELEASE); every limit is a dated roadmap item;
#     nothing on a visitor-facing page says what does not exist. Same for the
#     older class of defensive framing ("we are not claiming", "not just another")
#     and negative-chapter headings ("What we will not tell you").
#
#     Visible copy only — link targets, alt text and the design repo's own words
#     inside a quotation are not the page's voice. Phrases the site deliberately
#     uses ("no built-in ranking" quoting the MCP registry; "not comparable")
#     are not in the list, and adding one means checking every page still passes.
PHASE_LANGUAGE = re.compile(
    r"design[- ]phase"
    r"|\bnot (?:yet )?(?:shipped|built|running|implemented)\b"
    r"|\bno (?:design|code|dates?)\b(?! path)"
    r"|\bnothing (?:is |here is )?(?:built|shipped|scheduled)\b"
    r"|\bdesigned(?:,)? (?:rather than|but not|not) (?:shipped|built|running)\b"
    r"|\bdoes not exist yet\b|\bnot (?:yet )?scheduled\b|\bscheduled, not drawn\b"
    r"|\bplanned, not\b|\bnot a product yet\b|\bunbuilt\b",
    re.I)
DEFENSIVE_FRAMING = re.compile(
    r"not just another|we (?:are|'re) not claiming|we (?:do not|don't) claim"
    r"|to be clear|let'?s be clear|silver bullet|\bwe refuse\b|\bwe will not (?:tell|claim)\b",
    re.I)
NEGATIVE_HEADING = re.compile(
    r"(?i)^what (?:we|this|it) (?:are|is|will|do|does|can)(?:n'?t| not) ",
)
for page in pages:
    markup = page.read_text()
    # drop quotations: the words inside <q> and <blockquote> belong to the source
    quoted = re.sub(r"(?is)<(q|blockquote)[^>]*>.*?</\1>", " ", markup)
    body = re.sub(r"\s+", " ", visible(quoted))
    for m in PHASE_LANGUAGE.finditer(body):
        fail(f"{page.name}: phase language in visible copy -> "
             f"…{body[max(0, m.start() - 45): m.end() + 30]}…")
    for m in DEFENSIVE_FRAMING.finditer(body):
        fail(f"{page.name}: defensive framing in visible copy -> "
             f"…{body[max(0, m.start() - 45): m.end() + 30]}…")
    for h in re.findall(r"(?s)<h[1-3][^>]*>(.*?)</h[1-3]>", markup):
        text = re.sub(r"\s+", " ", visible(h)).strip()
        if NEGATIVE_HEADING.match(text):
            fail(f"{page.name}: heading frames a disclaimer, not guidance -> {text!r}")

# 18. THE KNOWLEDGE MAP'S CLAIMS ARE COPY, AND ITS DATA IS FRESH.
#     The map on the front page is the first JavaScript on the site, and it reads
#     eight hundred claims from a generated file. Three ways that goes wrong that
#     nothing above would see: (a) a script the page loads does not exist, and the
#     section renders as an empty box; (b) sky-claims.txt is edited and the
#     generated file is not, so the site ships yesterday's claims; (c) a claim
#     carries internal vocabulary or phase language — every gate here scans
#     visible copy, and a claim in a tooltip is visible copy that lives in a .js
#     file where check 5 does not look. sky-data.py --check owns (b) and (c);
#     this runs it, and does (a) itself.
for page in pages:
    markup = page.read_text()
    for src in re.findall(r'<script src="([^"]+)"', markup):
        if not (ROOT / resolve(src)).exists():
            fail(f"{page.name}: script {src} does not exist")
        if not src.startswith(("assets/", "/assets/")):
            fail(f"{page.name}: script {src} is loaded from outside assets/ — the site ships no third-party code")
if (ROOT / "sky-data.py").exists():
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "sky-data.py"), "--check"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        fail("sky-data.py --check: " + (r.stdout + r.stderr).strip().replace("\n", " | ")[:400])
    # the page that loads the data must carry the map, and the map must carry the
    # elements sky.js writes to — a renamed id fails silently in a browser
    for page in pages:
        markup = page.read_text()
        if "sky-data.js" not in markup:
            continue
        for el_id in ("sky", "sky-feed", "sky-count", "sky-tip", "sky-pause",
                      "sky-n-new", "sky-n-sharp", "sky-n-merge", "sky-n-held", "sky-n-refused"):
            if f'id="{el_id}"' not in markup:
                fail(f"{page.name}: loads sky.js but has no #{el_id}")

# 18b. THE MAP CAN BE DRAWN FROM A REAL FEED, AND A REAL FEED LEAKS NOTHING.
#     tests/fixtures/org-feed.jsonl is an organization gate's published notes,
#     captured from the real daemons (six claims countersigned, one refused for
#     a credential, two relations). sky-data.py --feed must render it, the
#     output must carry only labels — no claim text, no ids, no signer — and
#     the shipped sky must still be the authored one. This is the site's half
#     of the gate's own feed test; if the gate's field set ever grows a content
#     field, this is where the page would have shown it.
if (ROOT / "sky-data.py").exists() and (ROOT / "tests" / "fixtures" / "org-feed.jsonl").exists():
    import subprocess, tempfile
    fx = ROOT / "tests" / "fixtures" / "org-feed.jsonl"
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "sky-data.feed.js"
        r = subprocess.run([sys.executable, str(ROOT / "sky-data.py"), "--feed", str(fx), "--out", str(out)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            fail("sky-data.py --feed on the fixture: " + (r.stdout + r.stderr).strip().replace("\n", " | ")[:400])
        else:
            rendered = out.read_text()
            feed_text = fx.read_text()
            import json as _json
            subjects = {_json.loads(l).get("subject", "") for l in feed_text.splitlines() if l.strip()}
            for needle in ("hunter2", "AKIA", "refunds", "idempotency", "agent://", "uid:", "urn:doublegate", "sha256"):
                if needle in rendered:
                    fail(f"sky-data.py --feed: {needle!r} reached the rendered map — the map is labels only")
            for sid in subjects:
                if sid and sid in rendered:
                    fail("sky-data.py --feed: an artifact id reached the rendered map")
            if "spaces" not in rendered.splitlines()[1]:
                fail("sky-data.py --feed: the header does not say it was drawn from a feed")
    if "window.SKY_DATA" in (ROOT / "assets" / "sky-data.js").read_text() and \
            "--feed" in (ROOT / "assets" / "sky-data.js").read_text().splitlines()[0]:
        fail("assets/sky-data.js was rendered from a feed; the shipped sky is the authored one until a real org gate is public")

# 19. A FIGURE MADE OF WORDS IS MARKUP, NOT AN IMAGE.
#     scope-flow.svg and record-fields.svg were tables of prose and quoted
#     regulation shipped as 1040px images. Three costs, none of which any gate
#     above could see: the text was not selectable, not findable by search, and
#     not reachable by a screen reader beyond one alt attribute; and because a
#     1040px image cannot reflow, style.css had to pin it to its natural width
#     below the breakpoint and let a phone scroll sideways — at 390px the figure
#     rendered its 11.5px labels at 3.8px. As markup they reflow and the type can
#     grow instead of shrink.
#
#     The regression this guards is re-adding a text-heavy figure as an <img>.
#     The test is the figure's own words: the pages must carry them as copy, so
#     that check 5 (vocabulary), check 14 (sentence shape) and check 17 (phase
#     language) all reach them — which is the second reason markup beats an
#     image, and the reason a returning SVG must not pass silently.
FIGURE_COPY = {
    "commons.html": ("ladder", [
        "Four scopes — one mechanism, a wider audience each time",
        "you, on your own machine",
        "a group sharing one gate",
        "many teams, one authority",
        "anyone, outside your company",
        "Same write path at every scope — only the signing authority changes",
    ]),
    "governance.html": ("record", [
        "One signed record — what it holds, and what each field is for",
        "The requirement it answers",
        "reviewer identity — never the author",
        "over every field above — verifiable without asking us",
        "change any field and the signature stops verifying",
    ]),
}
for name, (container, phrases) in FIGURE_COPY.items():
    page = ROOT / name
    if not page.exists():
        continue
    markup = page.read_text()
    if f'class="{container}"' not in markup:
        fail(f"{name}: .{container} is gone — the figure it replaced was an image "
             f"of text, and must not come back as one")
        continue
    body = re.sub(r"\s+", " ", visible(markup))
    for phrase in phrases:
        if re.sub(r"\s+", " ", phrase) not in body:
            fail(f"{name}: figure copy missing from visible text -> {phrase!r}")
for page in pages:
    for src in re.findall(r'<img[^>]*src="/?assets/([^"]+)"', page.read_text()):
        if src in ("scope-flow.svg", "record-fields.svg"):
            fail(f"{page.name}: {src} is back as an image — it is a table of words; "
                 f"keep it as markup so it reflows and the copy gates reach it")

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
print("  no phase language · knowledge-map scripts, data freshness and claim copy · the map from a real feed, labels only")
print("  text figures are markup, not images")
