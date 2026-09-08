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
    ("evidence.html", "Evidence"),
]

# Rendered and reachable by URL, but out of the nav, the footer and the sitemap,
# and marked noindex. Pricing is unlisted until the tiers carry numbers: a
# pricing page with no prices invites the one conversation the site cannot
# yet finish. The fragment stays current so re-listing is a one-line change.
UNLISTED = [
    ("pricing.html", "Pricing"),
]

# What the first release is called, and when. One constant so every page
# quotes the same date; change it here, rebuild, and nothing drifts.
FIRST_RELEASE = "Q2 2027"

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
        "For engineers — what it is, what it costs, when it ships",
        "doublegate replaces your memory provider. Read path is unchanged, checking "
        "happens on the way in. Latency, token cost, the four tools your agent gains, "
        "and the release roadmap.",
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
# Two contact surfaces, because they answer different questions and one of them
# has to be public.
#
# CONTACT (issues) is for anything the answer belongs in public: a question about
# the mechanism, an objection, a correction to a cited claim. A site that stakes
# its identity on "every claim traces to cited research" should take its
# corrections where everyone can see both the correction and the reply.
#
# EMAIL is for the conversation that cannot happen in an issue tracker: what a
# deployment would cost, whether the boundary fits an org, when a tier lands.
# Nobody files a public issue to ask about their own company.
CONTACT = f"{GH}/issues"
EMAIL = "eugene.korniichuk@gmail.com"
# A subject line, so a cold mail arrives already sorted. "Deployment" rather
# than "sales": the conversation on offer is where a gate fits an organization
# and what it would cost there, ahead of the first release.
MAILTO = f"mailto:{EMAIL}?subject=doublegate%20%E2%80%94%20deployment%20and%20pricing"
SITE = "https://doublegate-io.github.io/"

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
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="apple-touch-icon" sizes="180x180" href="assets/apple-touch-icon.png">
<meta property="og:image" content="https://doublegate-io.github.io/assets/social-card.svg">
<meta property="og:url" content="{canonical}">
<link rel="canonical" href="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<header class="nav">
  <div class="nav-inner">
    <a class="brand" href="index.html"><img class="brand-mark" src="assets/logo-dark.svg" width="22" height="22" alt="" aria-hidden="true"> doublegate</a>
    <nav>{nav}<a class="ghost" href="{gh}">GitHub</a></nav>
  </div>
</header>

{body}

<footer>
  <div class="wrap foot">
    <div>
      <b>doublegate</b> · open source · first release {first_release} · every claim traces to cited research
      <p class="dim">Solo use is free and stays that way.
      <a href="{contact}">Questions, objections and corrections go here</a> — including
      "you got this wrong". Ask about deployment or pricing at
      <a href="{mailto}">{email}</a>.</p>
    </div>
    <div class="foot-links">
      <a href="how-it-works.html">How it works</a>
      <a href="for-organizations.html">For organizations</a>
      <a href="for-engineers.html">For engineers</a>
      <a href="governance.html">Governance</a>
      <a href="evidence.html">Evidence</a>
      <a href="{gh}">GitHub</a>
      <a href="{contact}">Ask a question</a>
      <a href="{mailto}">Email</a>
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
    # index.html is served at the domain root, so its canonical is the bare
    # domain — not "/index.html", which would be a second URL for one page.
    canonical = SITE if page == "index.html" else SITE + page
    markup = SHELL.format(
        title=title, desc=desc, nav=nav_html(page), body=body, gh=GH,
        contact=CONTACT, mailto=MAILTO, email=EMAIL, canonical=canonical,
        first_release=FIRST_RELEASE,
    )
    if page in dict(UNLISTED):
        # Reachable, not advertised: no canonical to claim a place in the
        # index, and an explicit noindex so a crawler that finds the URL
        # anyway leaves it out.
        markup = markup.replace(
            f'<link rel="canonical" href="{canonical}">\n',
            '<meta name="robots" content="noindex">\n',
        )
    return markup


def render_sitemap() -> str:
    """Generated from NAV so a new page cannot be missing from the sitemap."""
    urls = "\n".join(
        f"  <url><loc>{SITE if p == 'index.html' else SITE + p}</loc></url>"
        for p, _ in NAV
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n"
    )


def render_robots() -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n"


# GitHub Pages serves /404.html for any unmatched path. It goes through the same
# shell as every page so a lost reader still gets the nav, the footer and a way
# on -- a bare "not found" is a dead end, which is the one thing check 7 forbids
# everywhere else.
NOT_FOUND_BODY = """<section id="top">
  <div class="wrap hero narrow">
    <p class="eyebrow">404</p>
    <h1>That page <span class="grad">is not here</span></h1>
    <p class="lede">
      The link is wrong, or it pointed at something that moved. Nothing is broken on your side.
    </p>
    <div class="cta-row">
      <a class="btn primary" href="index.html">Start at the overview</a>
      <a class="btn" href="how-it-works.html">See how it works</a>
    </div>
    <p class="micro">
      If a link on this site brought you here, that is our bug —
      <a href="{contact}">tell us where it was</a>.
    </p>
  </div>
</section>"""


def render_404() -> str:
    # Absolute asset and link paths: /404.html can be served from any depth, and
    # a relative "assets/style.css" would 404 alongside it.
    markup = SHELL.format(
        title="Not found — doublegate",
        desc=(
            "That page is not here. The link is wrong or it pointed at something that "
            "moved — start from the overview, or tell us which link was broken."
        ),
        nav=nav_html("404.html"),
        body=NOT_FOUND_BODY.format(contact=CONTACT),
        gh=GH,
        contact=CONTACT,
        mailto=MAILTO,
        email=EMAIL,
        canonical=SITE,
        first_release=FIRST_RELEASE,
    )
    # An error page must not invite indexing, and must not claim to BE the home
    # page it points at: drop the canonical, keep og:url pointing at the root so
    # a shared 404 previews as the site rather than as nothing.
    markup = markup.replace(
        f'<link rel="canonical" href="{SITE}">\n',
        '<meta name="robots" content="noindex">\n',
    )
    markup = markup.replace('href="assets/', 'href="/assets/')
    markup = markup.replace('src="assets/', 'src="/assets/')
    for page, _ in NAV + UNLISTED:
        markup = markup.replace(f'href="{page}"', f'href="/{page}"')
    return markup


def main() -> int:
    check = "--check" in sys.argv
    stale, written = [], []

    # (path, content) for everything generated, pages and crawler files alike,
    # so --check covers all of it and a drifted sitemap fails CI like a
    # drifted page does.
    targets = [(page, render(page)) for page, _ in NAV + UNLISTED]
    targets.append(("sitemap.xml", render_sitemap()))
    targets.append(("robots.txt", render_robots()))
    targets.append(("404.html", render_404()))

    for name, want in targets:
        out = ROOT / name
        if check:
            if not out.exists() or out.read_text() != want:
                stale.append(name)
        else:
            out.write_text(want)
            written.append(name)
    if check:
        if stale:
            print("STALE (run python3 site/build.py):", ", ".join(stale))
            return 1
        print(f"all {len(targets)} files up to date")
        return 0
    print(f"wrote {len(written)} files: {', '.join(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
