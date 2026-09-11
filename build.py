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
    ("index.html", "Home"),
    ("for-business.html", "For business"),
    ("for-engineers.html", "For engineers"),
    ("how-it-works.html", "How it works"),
    ("evidence.html", "Evidence"),
]
CHILDREN = [
    ("governance.html", "Business governance"),
    ("commons-for-business.html", "Commons for business"),
    ("commons-for-engineers.html", "Commons for engineers"),
]
LISTED = NAV + CHILDREN
REDIRECTS = {"for-organizations.html": "for-business.html", "commons.html": "commons-for-business.html"}
AUDIENCES = {
    "business": [("for-business.html", "Overview"), ("governance.html", "Governance"), ("commons-for-business.html", "Commons")],
    "engineers": [("for-engineers.html", "Overview"), ("for-engineers.html#sdk", "SDK"), ("commons-for-engineers.html", "Commons"), ("https://doublegate-io.github.io/doublegate-sdk/", "Technical docs")],
}


def audience_for(page: str) -> str | None:
    return next((name for name, links in AUDIENCES.items() if page in dict(links)), None)


def subnav_html(page: str) -> str:
    audience = audience_for(page)
    if not audience:
        return ""
    links = "".join(f'<a href="{href}"' + (' aria-current="page"' if href == page else '') + f'>{label}</a>' for href, label in AUDIENCES[audience])
    return f'<div class="audience-nav"><div class="wrap"><span>For {audience}</span><nav aria-label="For {audience}">{links}</nav></div></div>'


# Scripts a page loads, by page. The shell carries none: the site is static
# and this is the one page that draws in the browser. Listed here rather than
# in the fragment so the <script> tags land after the footer, where a slow
# load cannot hold up the copy, and so check.py can verify each file exists.
SCRIPTS = {
    "index.html": ["assets/sky-data.js", "assets/sky.js"],
}

# Rendered and reachable by URL, but out of the nav, the footer and the sitemap,
# and marked noindex. Pricing is unlisted until the tiers carry numbers: a
# pricing page with no prices invites the one conversation the site cannot
# yet finish. The fragment stays current so re-listing is a one-line change.
UNLISTED = [
    ("pricing.html", "Pricing"),
]

# Adoption release (release 2) timing. One constant so every page
# quotes the same date; change it here, rebuild, and nothing drifts.
FIRST_RELEASE = "Q2 2027"

TITLES = {
    "index.html": (
        "doublegate — governed organizational knowledge",
        "Governed organizational knowledge for humans, agents and applications. "
        "Explore admission, authority and permitted projection through an illustrative "
        "knowledge review, published interfaces and the release roadmap.",
    ),
    "how-it-works.html": (
        "How doublegate works — a correction becomes shared knowledge",
        "Follow a proposed correction through evidence, assessment, an authorized decision "
        "and eligible shared use. An illustration of the planned review and publication lifecycle.",
    ),
    "for-business.html": (
        "For business — evaluate governed team knowledge",
        "Retain corrections, conventions and skills across your teams. "
        "Explore doublegate's deployment model, review controls and business case "
        "for shared agent knowledge.",
    ),
    "for-engineers.html": (
        "For engineers — build with reviewed knowledge",
        "Start with offline SDK checks, inspect development interface snapshots and plan "
        "the memory-provider integration. Operating costs, acceptance tests and the release sequence.",
    ),
    "governance.html": (
        "Business governance — decisions, provenance and source authority",
        "Planned connectors and shared review controls for agent knowledge: "
        "scoped approval, contributor accountability and provenance. References to the ECB RDARR Guide, "
        "EU AI Act Article 12, GDPR and BCBS 239 — quoted, not paraphrased.",
    ),
    "commons-for-business.html": (
        "Commons for business — publishing rights and reviewed reuse",
        "Decide what your organization can contribute to the planned Commons, what reuse costs, "
        "and which licensing, privacy and accountability decisions remain yours.",
    ),
    "commons-for-engineers.html": (
        "Commons for engineers — artifacts, attribution and integration",
        "Prepare versioned artifacts and review evidence with the offline SDK. Inspect current "
        "formats and interface snapshots separately from the planned release-5 Commons service.",
    ),
    "pricing.html": (
        "Pricing — Solo, Team, Organization",
        "Solo use is free. The organization gate is private and proprietary. Team adds the "
        "shared gate. Organization adds a second independent authority.",
    ),
    "evidence.html": (
        "Evidence — every claim, with its source",
        "The research behind the pitch: the 66-firm field experiment, Meta's in-house "
        "build, the provider survey, and the skill security data. Each one linked to "
        "its primary source.",
    ),
}

# ORG is where the nav's "GitHub" goes: the organization profile makes the case
# for the project and lists every repo. GH is this site's own repo, which is what
# issues and docs links need — a visitor who clicks "GitHub" and lands on the
# source of the page they were just reading has learned nothing.
ORG = "https://github.com/doublegate-io"
GH = f"{ORG}/doublegate-io.github.io"
DOCS = f"{GH}/blob/main/docs"
# Two contact surfaces, because they answer different questions and one of them
# has to be public.
#
# CONTACT (issues) is for anything the answer belongs in public: a question about
# the mechanism, an objection, a correction to a cited claim. A site that stakes
# its identity on "every claim traces to cited research" should take its
# corrections where everyone can see both the correction and the reply.
#
# Private email is available only through the footer Email link.
CONTACT = f"{GH}/issues"
EMAIL = "eugene.korniichuk@gmail.com"
MAILTO = f"mailto:{EMAIL}"
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
<link rel="stylesheet" href="assets/institutional.css">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<header class="nav">
  <div class="nav-inner">
    <a class="brand" href="index.html"><span class="dg-wordmark" aria-label="DoubleGate">DOUBLE<span class="dg-mark" aria-hidden="true"></span>GATE</span></a>
    <nav class="desktop-nav" aria-label="Main navigation">{nav}<a class="ghost" href="{org}">GitHub</a></nav>
    <details class="mobile-menu"><summary>Menu</summary><nav aria-label="Mobile navigation">{nav}<a class="ghost" href="{org}">GitHub</a></nav></details>
  </div>
</header>

{subnav}
{body}

<footer>
  <div class="wrap foot">
    <div>
      <b>doublegate</b> · <a href="index.html#implementation">Release roadmap</a> · research and evaluation sources
      <p class="dim">Solo use is free and stays that way. The organization gate is private and proprietary.
      <a href="{contact}">Questions, objections and corrections go here</a> — including
      "you got this wrong".</p>
    </div>
    <div class="foot-links">
      <a href="how-it-works.html">How it works</a>
      <a href="for-business.html">For business</a>
      <a href="for-engineers.html">For engineers</a>
      <a href="governance.html">Governance</a>
      <a href="commons-for-business.html">Commons for business</a>
      <a href="commons-for-engineers.html">Commons for engineers</a>
      <a href="evidence.html">Evidence</a>
      <a href="{org}">GitHub</a>
      <a href="{contact}">Ask a question</a>
      <a href="{mailto}">Email</a>
    </div>
  </div>
</footer>
{scripts}
</body>
</html>
"""


def nav_html(current: str) -> str:
    out = []
    for href, label in NAV:
        parent = {"business": "for-business.html", "engineers": "for-engineers.html"}.get(audience_for(current), current)
        cls = ' class="here" aria-current="page"' if href == parent else ""
        out.append(f'<a href="{href}"{cls}>{label}</a>')
    return "".join(out)


def scripts_html(page: str) -> str:
    tags = "".join(f'<script src="{src}" defer></script>\n' for src in SCRIPTS.get(page, []))
    return ("\n" + tags) if tags else ""


# Each <section id="..."> is a chapter, and a reader who wants to send a
# colleague one chapter should not have to read the markup to find its name.
# The build stamps a link to the section's own id onto that section's heading:
# invisible until the heading is hovered or the link is focused, so the page
# reads unchanged, and copyable from the address bar once clicked.
#
# Done here rather than in the fragments for the reason the shell is: an anchor
# hand-written into a fragment can disagree with the section it sits in, and
# nothing would catch it. Generated from the id itself, it cannot.
_SECTION = re.compile(r'(<section id="([^"]+)"[^>]*>)(.*?)(</section>)', re.S)
_FIRST_H2 = re.compile(r"(<h2[^>]*>)(.*?)(</h2>)", re.S)


def anchor_headings(body: str) -> str:
    """Give every chapter heading a link to its own section.

    One <h2> per section is the convention; only the first is stamped, and a
    section without one (a hero, a bare diagram) is left alone — it is still
    addressable by URL, it just has no heading to hang the affordance on.
    """
    def stamp(m: re.Match[str]) -> str:
        open_tag, sid, inner, close_tag = m.groups()
        link = (
            f'<a class="h-anchor" href="#{sid}" aria-label="Link to this section">'
            "<span aria-hidden=\"true\">#</span></a>"
        )
        inner = _FIRST_H2.sub(
            lambda h: f"{h.group(1)}{h.group(2)}{link}{h.group(3)}", inner, count=1
        )
        return f"{open_tag}{inner}{close_tag}"

    return _SECTION.sub(stamp, body)



# Editorial hero content is rendered through one static template.
HEROES = {'for-business.html': ('For business',
                       'Make team knowledge reusable.',
                       '<p class="hero-proposition">Keep the correction, its evidence and who '
                       'stands behind it.</p><p>Give one team a governed path from agent '
                       'corrections to reusable knowledge. Your organization defines the criteria, '
                       'ownership and access.</p><div class="cta-row"><a class="btn" '
                       'href="#honest">Plan a team evaluation</a></div>',
                       '<p class="availability">Shared-team controls are planned for release 4. '
                       'Review consumes inference and operating effort; compare results with your '
                       'existing workflow.</p>'),
 'for-engineers.html': ('For engineers',
                        'Build with reviewed knowledge.',
                        '<p class="hero-proposition">Start offline. Inspect the result before '
                        'wiring a consumer.</p><p>The Python SDK checks declarative artifacts. '
                        'Provider interfaces describe the next integration boundary; installing '
                        'the SDK does not start a gate.</p><div class="cta-row"><a class="btn '
                        'primary" href="#sdk">Run the SDK example</a><a class="btn" '
                        'href="#agents">Inspect the API artifacts</a></div>',
                        '{availability}'),
 'governance.html': ('For business / Governance',
                     'Know who approved what. And why.',
                     '<p class="hero-proposition">Governance begins with a scoped decision and a '
                     'record you can inspect.</p><p>Connect proposed knowledge to its source, '
                     'reviewer and permitted use. Source-system credentials confer no approval '
                     'authority.</p><a href="#how">Follow a system contribution</a>',
                     '<p class="availability">Signed decisions and keyed reads exist in the '
                     'development surface. Two-stage review and shared-team controls are planned '
                     'for releases 3 and 4; connectors have separate acceptance checks.</p>'),
 'how-it-works.html': ('How it works',
                       'A correction becomes shared knowledge.',
                       '<p class="hero-proposition">One revision. Evidence, a decision and a '
                       'permitted use.</p><p>Follow an illustrative correction: the payments '
                       'sandbox rate-limits per API key, not per account. Each stage below changes '
                       'what others may do with that revision.</p><a href="#diagram">Follow the '
                       'review lifecycle</a>',
                       '<p class="availability">The journey illustrates the planned release-3 '
                       'review and release-4 sharing workflow.</p>'),
 'evidence.html': ('Evidence',
                   'Every claim, with its source.',
                   '<p class="hero-proposition">Read the finding. Check what it actually '
                   'supports.</p><p>Published research supports the problem and approach. '
                   'DoubleGate’s planned evaluations must establish its own outcomes; the internal '
                   'provider survey is available on request.</p><a href="#findings">Read the '
                   'primary sources</a>',
                   ''),
 'commons-for-business.html': ('For business / Commons',
                               'Share what you have the rights to share.',
                               '<p class="hero-proposition">A reviewed supply of knowledge, with '
                               'explicit costs and publishing choices.</p><p>Choose what leaves '
                               'your organization. Assess the rights, evidence and maintenance '
                               'work before contributing or reusing an artifact.</p><a '
                               'href="#why-contribute">Evaluate contribution</a>',
                               '<p class="availability">The public Commons is planned for release '
                               '5. Reading is free; reuse follows each artifact’s published '
                               'terms.</p>'),
 'commons-for-engineers.html': ('For engineers / Commons',
                                'Carry the evidence with the artifact.',
                                '<p class="hero-proposition">Version the content. Preserve '
                                'attribution. Check eligible use.</p><p>Prepare artifacts with the '
                                'offline SDK and inspect the published schemas. SDK findings '
                                'inform review; they grant no publication or execution '
                                'authority.</p><a href="#formats">Inspect the current formats</a>',
                                '<p class="availability">SDK development artifacts are available '
                                'now. Commons publication and public operation remain release-5 '
                                'work.</p>'),
 'index.html': ('DoubleGate / Agent memory',
                'Memory and knowledge for AI agents.',
                '\n'
                '        <p class="hero-proposition">Reuse what agents learn.<br>Keep the evidence '
                'and the review.</p>\n'
                '        <p>DoubleGate is building a memory provider for reviewed claims, team '
                'conventions and reusable skills — instead of letting each session start from '
                'private, unversioned corrections.</p>\n'
                '        <div class="cta-row"><a class="btn primary" href="#cost">See a reviewed '
                'example</a><a class="btn" href="for-engineers.html#sdk">Build with the '
                'SDK</a></div>',
                '{availability}')}

def hero_html(page: str) -> str:
    label, headline, complement, status = HEROES[page]
    return (ROOT / "templates/hero.html").read_text().format(label=label, headline=headline, complement=complement, status=status)

def render_redirect(target: str) -> str:
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><link rel="canonical" href="{SITE}{target}"><title>Page moved — doublegate</title><script>location.replace("{target}" + location.search + location.hash);</script></head><body><p>This page has moved to <a href="{target}">{dict(LISTED)[target]}</a>.</p></body></html>
'''

def render(page: str) -> str:
    title, desc = TITLES[page]
    body = anchor_headings((PAGES / page).read_text().strip().replace("{hero}", hero_html(page) if page in HEROES else "").replace("{first_release}", FIRST_RELEASE).replace("{availability}", f'<p class="availability"><b>Available now:</b> offline SDK and development API artifacts. <b>Planned:</b> provider adoption in {FIRST_RELEASE}; review and organizational sharing follow in later releases.</p>'))
    if not body.startswith("<main"):
        body = f'<main class="audience-page">{body}</main>'
    # index.html is served at the domain root, so its canonical is the bare
    # domain — not "/index.html", which would be a second URL for one page.
    canonical = SITE if page == "index.html" else SITE + page
    markup = SHELL.format(
        title=title, desc=desc, nav=nav_html(page), subnav=subnav_html(page), body=body, gh=GH, org=ORG,
        contact=CONTACT, mailto=MAILTO, email=EMAIL, canonical=canonical,
        first_release=FIRST_RELEASE, scripts=scripts_html(page),
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
        for p, _ in LISTED
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n"
    )


def render_robots() -> str:
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\nLLMs: {SITE}llms.txt\n"


# The front door for a program (llmstxt.org): what the thing is, in one paragraph,
# then the machine-readable documents, then the pages. Generated here so it quotes
# the same release date as every page and cannot name a page that does not exist.
LLMS_INTRO = (
    "> doublegate is memory and knowledge-sharing software for AI agents. "
    "Contributions are held for review; signed decisions establish scoped publication. "
    "The release-3 workflow uses an AI trust assessment from 0–100, then a distinct "
    "authorized AI or human APPROVE or REJECT decision without a second score. "
    "Approval means production-ready for the declared scope, version and use; current "
    "access and applicability govern retrieval. Release 4 adds shared team attribution "
    "and publication over authenticated HTTP. The organization gate remains private and proprietary. Adoption release · {first_release}."
)

LLMS_API = [
    ("api/mcp-tools.json", "the tool schemas each tier serves over the agent-tool protocol (exactly what `tools/list` answers), and the `instructions` paragraph the handshake carries"),
    ("api/daemon-rpc.json", "every verb on a gate's local socket — parameters, which role serves it, the proof each needs; a running gate answers the same to `dg.describe`"),
    ("api/note.schema.json", "JSON Schema of a published note's `data`: the closed field set a subscriber or a knowledge map may rely on — which claim, what happened, what kind; never the text"),
    ("api/openapi.json", "OpenAPI 3.1 for the organization gate's keyed HTTP surface — submissions in, signed outcomes out, the ratified collection for read keys; a running gate serves it at `GET /openapi.json` to any valid key"),
    ("api/index.json", "which commit of which repository each document was rendered from"),
]

LLMS_RULES = [
    "Tools are namespaced `doublegate.*` — `doublegate.remember`, not `remember`. Launch the plugin tier (`doublegate-plugin mcp`, works with no gate running) or the client tier (`doublegate-client mcp`, this machine's gate) over stdio and call `tools/list`.",
    "`remember` returns a handle, never a promise of admission: `local:` when no gate was reachable, `sha256:` once a gate stamped it. Nothing is readable through `recall` until a reviewer that did not write it promoted it.",
    "Never send `writer_identity` or `deployment_id`; identity is derived from the connection and a request carrying it is refused.",
    "There is no promote, sign, delete or trust-class tool on any tier. The thing being gated does not operate the gate; a person, or a quorum that excludes the writer, does that on the gate's own socket.",
    "The organization gate is not where memory lives. Client gates submit to it (`PUT /submissions/{id}`), and the verdict never rides the request — poll `GET /outcomes?since=<position>` with the same key.",
]


def render_llms() -> str:
    pages = "\n".join(f"- [{label}]({SITE if p == 'index.html' else SITE + p}): {TITLES[p][1]}" for p, label in LISTED)
    api = "\n".join(f"- [{path}]({SITE}{path}): {about}" for path, about in LLMS_API)
    rules = "\n".join(f"- {r}" for r in LLMS_RULES)
    return (
        "# doublegate\n\n"
        + LLMS_INTRO.format(first_release=FIRST_RELEASE) + "\n\n"
        "## The API, as data\n\n"
        "Rendered from the code that serves it and checked against it in the code repositories' continuous "
        "integration; published here as a snapshot stamped with the commit.\n\n"
        + api + "\n\n"
        "## If you are an agent wiring yourself in\n\n"
        + rules + "\n\n"
        "## Pages\n\n"
        + pages + "\n\n"
        "## Optional\n\n"
        f"- [Site source]({GH}): how these pages are built and the checks they pass\n"
        f"- [Questions, objections and corrections]({CONTACT})\n"
    )


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
        nav=nav_html("404.html"), subnav="",
        body=NOT_FOUND_BODY.format(contact=CONTACT),
        gh=GH,
        org=ORG,
        contact=CONTACT,
        mailto=MAILTO,
        email=EMAIL,
        canonical=SITE,
        first_release=FIRST_RELEASE,
        scripts="",
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
    for page, _ in LISTED + UNLISTED:
        markup = markup.replace(f'href="{page}"', f'href="/{page}"')
    return markup


def main() -> int:
    check = "--check" in sys.argv
    stale, written = [], []

    # (path, content) for everything generated, pages and crawler files alike,
    # so --check covers all of it and a drifted sitemap fails CI like a
    # drifted page does.
    targets = [(page, render(page)) for page, _ in LISTED + UNLISTED]
    targets.extend((old, render_redirect(target)) for old, target in REDIRECTS.items())
    targets.append(("sitemap.xml", render_sitemap()))
    targets.append(("robots.txt", render_robots()))
    targets.append(("llms.txt", render_llms()))
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
