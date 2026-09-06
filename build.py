#!/usr/bin/env python3
"""Assemble the site from a shared shell + per-page fragments.

Why a build step for a static site: the nav, footer and head metadata must be
identical on every page, and hand-copying them across six pages is how a nav
label ends up disagreeing with the page it points at. Fragments live in
site/pages/*.html and carry only their own <section> content.

Run:  python3 site/build.py        (writes site/*.html)
      python3 site/build.py --check  (fails if output is stale — for CI)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "pages"

# ---------------------------------------------------------------- site map
# order matters: this drives the nav
NAV = [
    ("index.html", "Overview"),
    ("how-it-works.html", "How it works"),
    ("for-organizations.html", "For organizations"),
    ("for-engineers.html", "For engineers"),
    ("governance.html", "Governance"),
    ("commons.html", "Commons"),
    ("pricing.html", "Pricing"),
    ("evidence.html", "Evidence"),
]

TITLES = {
    "index.html": (
        "doublegate — your organization's AI knowledge, reviewed and shared",
        "Your engineers teach their agents every day and none of it is shared. "
        "doublegate reviews what an agent learns, signs it, and makes it an asset "
        "the whole organization inherits.",
    ),
    "how-it-works.html": (
        "How doublegate works — one memory's journey",
        "Follow a single memory from the moment an agent writes it, through holding, "
        "scanning, independent review and signing, to the point every other machine "
        "can read it.",
    ),
    "for-organizations.html": (
        "For organizations — stop paying for the same lesson twice",
        "A study across 66 firms found individual AI tools produced individual time "
        "savings and no shift in how the organization works. This is the page about "
        "why, and what it costs you.",
    ),
    "for-engineers.html": (
        "For engineers — what it is, what it costs, what breaks",
        "doublegate replaces your memory provider. Read path is unchanged, checking "
        "happens on the way in. Latency, token cost, failure modes and the things "
        "that are not built yet.",
    ),
    "governance.html": (
        "Governance — connectors, provenance, and what regulators ask for",
        "Let your existing systems propose what agents should know, with every belief "
        "audited, traceable, versioned and discoverable. Mapped to the ECB RDARR Guide, "
        "EU AI Act Article 12, GDPR and BCBS 239 — quoted, not paraphrased.",
    ),
    "commons.html": (
        "The Commons — a reviewed public library of agent knowledge",
        "Skills, memories and knowledge artifacts anyone can draw on, held and signed by a "
        "reviewer that did not write them. Free to read, free to contribute, every verdict "
        "published — including the rejections.",
    ),
    "pricing.html": (
        "Pricing — Solo, Team, Organization",
        "The same open-source engine at every tier. Solo is free. Team adds the "
        "shared gate. Organization adds a second independent authority.",
    ),
    "evidence.html": (
        "Evidence — every claim, with its source",
        "The research behind the pitch: the 66-firm field experiment, Meta's in-house "
        "build, the provider survey, and the skill security data. Each one linked to "
        "its primary source.",
    ),
}

GH = "https://github.com/doublegate-io/doublegate-io.github.io"
DOCS = f"{GH}/blob/main/docs"

SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" type="image/svg+xml" href="assets/logo.svg">
<meta property="og:image" content="https://doublegate-io.github.io/assets/social-card.svg">
<meta property="og:url" content="https://doublegate-io.github.io/">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<header class="nav">
  <div class="nav-inner">
    <a class="brand" href="index.html"><img class="brand-mark" src="assets/logo.svg" width="22" height="22" alt="" aria-hidden="true"> doublegate</a>
    <nav>{nav}<a class="ghost" href="{gh}">GitHub</a></nav>
  </div>
</header>

{body}

<footer>
  <div class="wrap foot">
    <div>
      <b>doublegate</b> · design phase · every claim traces to cited research
      <p class="dim">Open source. Solo use is free and stays that way.</p>
    </div>
    <div class="foot-links">
      <a href="how-it-works.html">How it works</a>
      <a href="for-organizations.html">For organizations</a>
      <a href="for-engineers.html">For engineers</a>
      <a href="pricing.html">Pricing</a>
      <a href="evidence.html">Evidence</a>
      <a href="{gh}">GitHub</a>
    </div>
  </div>
</footer>

</body>
</html>
"""


def nav_html(current: str) -> str:
    out = []
    for href, label in NAV:
        if href == "index.html":
            continue  # the brand mark is the home link
        cls = ' class="here"' if href == current else ""
        out.append(f'<a href="{href}"{cls}>{label}</a>')
    return "".join(out)


def render(page: str) -> str:
    title, desc = TITLES[page]
    body = (PAGES / page).read_text().strip()
    return SHELL.format(
        title=title, desc=desc, nav=nav_html(page), body=body, gh=GH
    )


def main() -> int:
    check = "--check" in sys.argv
    stale, written = [], []
    for page, _ in NAV:
        want = render(page)
        out = ROOT / page
        if check:
            if not out.exists() or out.read_text() != want:
                stale.append(page)
        else:
            out.write_text(want)
            written.append(page)
    if check:
        if stale:
            print("STALE (run python3 site/build.py):", ", ".join(stale))
            return 1
        print(f"all {len(NAV)} pages up to date")
        return 0
    print(f"wrote {len(written)} pages: {', '.join(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
