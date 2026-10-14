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

import json
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
]
LISTED = NAV + CHILDREN
# Retired pages redirect so an old bookmark still lands somewhere that answers it.
# The two Commons pages described a public library the 2026-10-04 feature review
# declined; their readers land on the audience overview instead.
REDIRECTS = {
    "for-organizations.html": "for-business.html",
    "commons.html": "for-business.html",
    "commons-for-business.html": "for-business.html",
    "commons-for-engineers.html": "for-engineers.html",
}
AUDIENCES = {
    "business": [("for-business.html", "Overview"), ("governance.html", "Governance")],
    "engineers": [("for-engineers.html", "Overview"), ("for-engineers.html#sdk", "SDK"), ("for-engineers.html#plugin", "Plugin"), ("https://about.doublegate.io/doublegate-sdk/", "Technical docs")],
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

# What ships next, in the order it ships. One constant so every page names the
# same next steps; the Solo release is dated when its exit list is green, and
# until then no page carries a date.
# Every use reads "Next: {next_steps}.", so the constant holds two whole
# sentences: the Solo release, then Team.
NEXT_STEPS = ("the Solo release of today's gate, installable, backed up and restorable, with "
              "rotating signing keys and erasable content. Then Team, one gate a group shares "
              "over the network, under one review policy")
AVAILABILITY = ('<p class="availability"><b>Available today:</b> the gate, its console, a Claude Code '
                'plugin and the offline SDK. '
                f'<b>Next:</b> {NEXT_STEPS}.</p>')

TITLES = {
    "index.html": (
        "doublegate — reviewed memory for AI agents",
        "What an AI agent writes is held and scanned, and other agents recall it only after a "
        "reviewer other than its author signs it. The gate, its console and a Claude Code "
        "plugin are available today.",
    ),
    "how-it-works.html": (
        "How doublegate works — a correction becomes shared knowledge",
        "Follow one correction from the moment an agent writes it to the moment another agent "
        "recalls it. See each stage, from the work area to recall, and what happens when a step "
        "refuses it.",
    ),
    "for-business.html": (
        "For business — keep what a company's agents learn",
        "Keep the corrections, conventions and skills a company's agents learn as reviewed claims "
        "that any agent on the gate can find. Who runs it, what it costs, and what a group "
        "gets next.",
    ),
    "for-engineers.html": (
        "For engineers — build with reviewed knowledge",
        "Run the gate, connect Claude Code through its plugin, review in the "
        "console, and check files offline with the SDK. Interfaces, running costs and the "
        "release sequence.",
    ),
    "governance.html": (
        "Business governance — decisions, provenance and a signed record",
        "Who wrote each claim, who reviewed it and why, in a signed journal an auditor can verify. "
        "Quoted references to the ECB RDARR Guide, EU AI Act Article 12, GDPR and BCBS 239.",
    ),
    "pricing.html": (
        "Pricing — Solo and Team",
        "Solo is free and self-hosted on one machine. Team, on the roadmap, adds one gate a "
        "group shares over the network, under one review policy.",
    ),
    "evidence.html": (
        "Evidence — every finding, with its source",
        # Ends at the rules while #against and #measured are hidden; once
        # #against renders, the description adds ", and the findings that cut
        # against us".
        "The research behind the problem, and the rules the gate enforces and how to "
        "check each.",
    ),
}

# The role table (for-engineers #agents, evidence #rules) and the count of
# methods an agent key reaches are counted from the site's own snapshot of the
# method catalog, api/daemon-rpc.json, so the page cannot drift from the file
# published beside it. Nothing outside this directory is read. The visible
# cells carry role names, counts and act words only; a method this map does not
# name is counted, not listed. The build refuses a snapshot that contradicts the
# copy built on it: an act reachable by an agent key, a method that deletes, or
# an act the map names that the catalog no longer has.
#
# ROLES is the ranked ladder, each reaching every method of those before it.
# UNRANKED names each role off that ladder and the ladder roles whose methods it
# also reaches: a runner key answers as agent for every other method and alone
# reaches its own, adds no act, and reaches nothing of reviewer or admin
# (ADR-0140 d1; 17 — Crews §12). Its row is counted from those, never cumulated.
ROLES = ("reader", "agent", "reviewer", "admin")
UNRANKED = {"runner": ("reader", "agent")}
ACT_WORDS = {"dg.promote": "promote", "dg.sign": "sign", "dg.reject": "reject",
             "dg.demote": "demote", "dg.hide": "hide", "dg.ban": "ban"}


def role_reach() -> tuple[str, str]:
    """(the role table's markup, "<methods an agent key reaches> of <all methods>")."""
    verbs = json.loads((ROOT / "api" / "daemon-rpc.json").read_text(encoding="utf-8"))["verbs"]
    by_role = {role: {v["name"] for v in verbs if v["role"] == role}
               for role in (*ROLES, *UNRANKED)}
    problems = [f"a method needs a role the table does not know: {v['name']} ({v['role']})"
                for v in verbs if v["role"] not in by_role]
    problems += [f"{name} is not in the catalog" for name in ACT_WORDS
                 if not any(name in names for names in by_role.values())]
    problems += [f"an agent key reaches {name}" for name in ACT_WORDS
                 if name in by_role["reader"] | by_role["agent"]]
    problems += [f"a {role} key reaches {name}" for role, below in UNRANKED.items()
                 for name in ACT_WORDS
                 if name in by_role[role].union(*(by_role[r] for r in below))]
    problems += [f"{v['name']} deletes" for v in verbs if "delete" in v["name"]]
    if problems:
        raise SystemExit("build.py: api/daemon-rpc.json contradicts the role table's copy: "
                         + "; ".join(problems))
    total, reached, rows, agent_reach = len(verbs), 0, [], ""
    for role in ROLES:
        reached += len(by_role[role])
        acts = ", ".join(word for name, word in ACT_WORDS.items() if name in by_role[role])
        rows.append(f"<tr><td>{role}</td><td>{reached} of {total}</td><td>{acts or '—'}</td></tr>")
        if role == "agent":
            agent_reach = f"{reached} of {total}"
    for role, below in UNRANKED.items():
        own = len(by_role[role]) + sum(len(by_role[r]) for r in below)
        rows.append(f"<tr><td>{role}</td><td>{own} of {total}</td><td>—</td></tr>")
    table = ('<table class="cmp role-table">'
             "<caption>Each role up to admin reaches every method of the roles listed before it. "
             "A runner is the API key of a machine that starts a crew's agents. It reaches the reader's "
             "and the agent's methods and its own, and adds no act. No method deletes.</caption>"
             "<thead><tr><th>Role</th><th>Methods it reaches</th><th>Acts it adds</th></tr></thead>"
             f"<tbody>{''.join(rows)}</tbody></table>")
    return table, agent_reach


ROLE_TABLE, AGENT_REACH = role_reach()

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
EMAIL = "eugene@doublegate.io"
MAILTO = f"mailto:{EMAIL}"
SITE = "https://about.doublegate.io/"

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
<meta property="og:image" content="https://about.doublegate.io/assets/social-card.svg">
<meta property="og:url" content="{canonical}">
<link rel="canonical" href="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="assets/institutional.css">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>

<header class="nav">
  <div class="nav-inner">
    <a class="brand" href="index.html"><span class="dg-wordmark" aria-label="doublegate">DOUBLE<span class="dg-mark" aria-hidden="true"></span>GATE</span></a>
    <nav class="desktop-nav" aria-label="Main navigation">{nav}<a class="ghost" href="{org}">GitHub</a></nav>
    <details class="mobile-menu"><summary>Menu</summary><nav aria-label="Mobile navigation">{nav}<a class="ghost" href="{org}">GitHub</a></nav></details>
  </div>
</header>

{subnav}
{body}

<footer>
  <div class="wrap">
    <span class="gate-rail dg-boundary-mark foot-rail" aria-hidden="true"><i></i><i></i></span>
    <div class="foot">
      <div>
        <b>doublegate</b> · <a href="index.html#implementation">Availability and roadmap</a> · <a href="evidence.html">Research and evaluation sources</a>
        <p class="dim"><a href="for-business.html#offering">Solo use is free and stays that way</a>.
        <a href="{contact}">Questions, objections and corrections go here</a>, a report that
        the site is wrong included.</p>
      </div>
      <div class="foot-links">
        <a href="how-it-works.html">How it works</a>
        <a href="for-business.html">For business</a>
        <a href="for-engineers.html">For engineers</a>
        <a href="governance.html">Governance</a>
        <a href="evidence.html">Evidence</a>
        <a href="{org}">GitHub</a>
        <a href="{contact}">Ask a question</a>
        <a href="{mailto}">Email</a>
      </div>
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
# Each entry is (label, headline, complement, status). A status may carry
# {next_steps} or {availability}; render() substitutes both after the hero is in.
HEROES = {'for-business.html': ('For business',
                       'Make what agents learn reusable.',
                       '<p class="hero-proposition">Keep each correction with its evidence, who '
                       'wrote it and who signed it.</p><p>The organization chooses who reviews: a '
                       'person, a grading model or both, and which kinds of content need '
                       'a person.</p><div class="cta-row"><a class="btn" '
                       'href="#group">What a group gets next</a></div>',
                       '<p class="availability"><b>Available today,</b> where every '
                       'agent shares one gate. Review costs model usage and someone’s time. '
                       '<b>Next:</b> Team, one gate a group shares over the network.</p>'),
 'for-engineers.html': ('For engineers',
                        'Build with reviewed knowledge.',
                        '<p class="hero-proposition">Run the gate. Connect Claude '
                        'Code. Review in the console.</p><p>The SDK checks files offline, '
                        'without a gate.</p><div class="cta-row"><a class="btn primary" '
                        'href="#plugin">Connect Claude Code</a><a class="btn" '
                        'href="#agents">Inspect the API artifacts</a></div>',
                        '{availability}'),
 'governance.html': ('For business / Governance',
                     'Know who approved what. And why.',
                     '<p class="hero-proposition">Every decision is signed into a record an auditor '
                     'can verify.</p><p>Every claim carries its author and every '
                     'grade and signature on it. The identity that wrote a claim can never '
                     'approve it.</p><a href="#how">Follow a claim from its author</a>',
                     '<p class="availability"><b>Runs today:</b> a signed journal anyone holding '
                     'it can verify, with the reviewer named on each decision. <b>Next:</b> '
                     '{next_steps}.</p>'),
 'how-it-works.html': ('How it works',
                       'A correction becomes shared knowledge.',
                       '<p class="hero-proposition">One claim, from the agent that writes it to '
                       'the agent that finds it.</p><p>Follow one correction: the '
                       'payments sandbox rate-limits per API key, not per account. Each stage '
                       'below changes who may read it.</p><a '
                       'href="#diagram">Follow the review lifecycle</a>',
                       '<p class="availability">Every stage here is available today. '
                       'Sharing a gate across a group comes with Team.</p>'),
 'evidence.html': ('Evidence',
                   'Every finding, with its source.',
                   '<p class="hero-proposition">Read the finding. Check what it actually '
                   'supports.</p><p>Published research documents the problem. Anyone can check the '
                   'gate’s rules against what we publish, on their own gate.</p><a href="#findings">Read the primary '
                   'sources</a>',
                   ''),
 'index.html': ('doublegate / Agent memory',
                'Check what agents learn. Then reuse it.',
                '\n'
                '        <p class="hero-proposition">A company&rsquo;s agents relearn the same lessons. '
                'Keep the ones a reviewer checked.</p>\n'
                '        <p>doublegate holds what an agent writes until a person or model other '
                'than its author signs it. Other agents can then find it if they search every work '
                'area. By default an agent searches its own area and those above it.</p>\n'
                '        <div class="cta-row"><a class="btn primary" href="#cost">See a reviewed '
                'example</a><a class="btn" href="how-it-works.html">How it works</a></div>',
                '<p class="availability"><b>Available today:</b> the gate, its '
                'console, a Claude Code plugin and the offline SDK.</p>')}

def hero_html(page: str) -> str:
    label, headline, complement, status = HEROES[page]
    return (ROOT / "templates/hero.html").read_text().format(label=label, headline=headline, complement=complement, status=status)

def render_redirect(target: str) -> str:
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><link rel="canonical" href="{SITE}{target}"><title>Page moved — doublegate</title><script>location.replace("{target}" + location.search + location.hash);</script></head><body><p>This page has moved to <a href="{target}">{dict(LISTED)[target]}</a>.</p></body></html>
'''

def render(page: str) -> str:
    title, desc = TITLES[page]
    body = anchor_headings((PAGES / page).read_text().strip().replace("{hero}", hero_html(page) if page in HEROES else "").replace("{next_steps}", NEXT_STEPS).replace("{availability}", AVAILABILITY).replace("{role_table}", ROLE_TABLE).replace("{agent_reach}", AGENT_REACH))
    if not body.startswith("<main"):
        body = f'<main class="audience-page">{body}</main>'
    # index.html is served at the domain root, so its canonical is the bare
    # domain — not "/index.html", which would be a second URL for one page.
    canonical = SITE if page == "index.html" else SITE + page
    markup = SHELL.format(
        title=title, desc=desc, nav=nav_html(page), subnav=subnav_html(page), body=body, gh=GH, org=ORG,
        contact=CONTACT, mailto=MAILTO, email=EMAIL, canonical=canonical,
        scripts=scripts_html(page),
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
    "> doublegate is gated memory for AI agents. What an agent writes goes into a named work "
    "area, where it is held and scanned. No other agent's recall returns it until an identity "
    "that did not write it has reviewed and signed it. "
    "Every promotion is that gate's own and is marked provisional. Recall with no scope "
    "searches the caller's work area, then each parent, and stops at the first level that "
    "answers. Ask with scope `space` to search the whole space. By default a grading model "
    "reads each held claim twice, for and against, and those two readings can promote it with "
    "no person. An operator can require a person for any kind of content. Next: {next_steps}."
)

# The descriptions of the api/ files say the same thing api-sync.py's manifest
# says about them.
LLMS_API = [
    ("api/mcp-tools.json", "the tool schemas of the gate's built-in plugin, which is being retired, as its `tools/list` answers them; the Claude Code plugin's tools are not in this file"),
    ("api/daemon-rpc.json", "every verb on a gate's local socket — parameters, which role serves it, the proof each needs; a running gate answers the same to `dg.describe`"),
    ("api/openapi.json", "OpenAPI for the gate's HTTP surface on this machine; it answers on loopback only, with a sign-in or an API key"),
    ("api/note.schema.json", "JSON Schema of a published note's `data`: the closed field set a subscriber may rely on — which claim, what happened, what kind; never the text"),
    ("api/index.json", "which commit of which repository each document was rendered from"),
]

# Rule 1's eight tool names are typed here, not read from doublegate-agent
# (build.py reads nothing outside this directory); compare them by hand with
# doublegate-agent/src/doublegate_agent/mcp.py TOOLS when either changes.
LLMS_RULES = [
    "Claude Code: the `doublegate-agent` plugin gives an agent thirteen tools: remember, record, recall, context, workarea, lineage, workarea_relate, complete, status, ask, cancel_question, questions_from_crews and answer_question. It offers no act above an agent's. Over the gate's local socket, a process running as the gate's operating-system user is the gate's administrator, so the gate itself holds an agent to these acts only when the agent runs under another operating-system user.",
    "The gate's built-in plugin, which is being retired, namespaces its tools `doublegate.*` — `doublegate.remember`, not `remember`. Launch it with `doublegate-client mcp` (this machine's gate) over stdio and call `tools/list`.",
    "Every write names a work area. `remember` returns a handle, never a promise of promotion; nothing you remember is readable to anyone else through `recall` until a reviewer other than its author has promoted it. Your own held claims come back to you marked `held`.",
    "Never send `writer_identity` or `deployment_id`; identity is derived from the connection and a request carrying it is refused.",
    "There is no promote, sign, demote, delete or trust-class tool on any tier. The thing being gated does not operate the gate; a person, or a reviewer who is not the author, does that on the gate's own socket or in its console.",
    "Every hit carries `provisional`: true while no second authority has countersigned, which on one gate is every hit. The flag is shown and never changes the order of hits.",
]


def render_llms() -> str:
    pages = "\n".join(f"- [{label}]({SITE if p == 'index.html' else SITE + p}): {TITLES[p][1]}" for p, label in LISTED)
    api = "\n".join(f"- [{path}]({SITE}{path}): {about}" for path, about in LLMS_API)
    rules = "\n".join(f"- {r}" for r in LLMS_RULES)
    return (
        "# doublegate\n\n"
        + LLMS_INTRO.format(next_steps=NEXT_STEPS) + "\n\n"
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
      The link is wrong, or it pointed at something that moved. Nothing on the visitor's side is broken.
    </p>
    <div class="cta-row">
      <a class="btn primary" href="index.html">Start at the overview</a>
      <a class="btn" href="how-it-works.html">See how it works</a>
    </div>
    <p class="micro">
      A broken link on this site is our bug —
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
