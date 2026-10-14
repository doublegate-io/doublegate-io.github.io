#!/usr/bin/env python3
"""Generate claim-path.svg -- a new claim travelling the path, and the loop.

What this figure is for
-----------------------
Three figures now sit on the site and each answers a different question:

  the lifecycle flow  WHO decides. Five stages and the exits from them, drawn as
                      HTML markup on how-it-works #diagram (artifact-flow.svg,
                      which drew this as an image, left the site 2026-10-06).
  hero-field.svg      WHAT comes back. Five verdicts over sixty claims.
  this one            WHERE it goes. The path one claim takes through the gate,
                      and what happens when it meets a claim already there.

The thing neither of the other two shows is the loop. A reader who has seen
"MERGED" reasonably assumes the store edits something. It does not. A
correction is a new claim linked to the one it replaces: it is written, held,
scanned, graded and signed like any other, and the claim it supersedes is kept.
Merges and splits are a reviewer's act, and the reviewer who starts one cannot
commit it. Nothing is edited in place and nothing is deleted.

So the figure draws the path once and sends two things down it: the arriving
claim, and the correction that arrives when it meets one already there.

Words and colours (redrawn 2026-10-06 in the decided words, ADR-0104 d8)
------------------------------------------------------------------------
  stages     WRITE (held in quarantine) -> SCAN -> GRADE (two readings; a person
             when policy asks) -> SIGN (a reviewer who is not the author) ->
             PROMOTE (a signed journal event, marked provisional, ADR-0108 d2)
  colours    the site's grammar for the stages: rose held, amber scanned, green
             signed, violet the journal. GRADE is neutral, because a grade is
             neither a signature nor a state, and a claim in transit is ink.
  outcomes   PROMOTED / SUPERSEDED (old kept) / MERGED (parents kept) /
             REJECTED (kept, reason recorded), in the homepage verdict figure's
             glyphs and colours (hero-field.py), so the two teach one language
  stores     quarantine (no other agent's recall returns what is held there)
             and promoted claims (what recall finds), drawn as two containers
  not drawn  automatic consolidation (planned, as a peer that proposes and a
             reviewer decides) and a second, countersigning gate (planned)

Honesty
-------
No counts, rates or timings appear here. It claims only structure: what
connects to what, in what order, and who may not do what. Nothing on the
figure asserts a measurement.

Deterministic: computed geometry, no randomness, byte-identical every run.

Run:    CHROME_PATH=... python3 claim-path.py
Check:  CHROME_PATH=... python3 claim-path.py --check   (exit 1 when the SVG is stale)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "claim-path.svg"
CHROME = os.environ.get("CHROME_PATH", "")

FONT = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Inter, sans-serif"

# The site renders .diagram.wide img at exactly 1000px (assets/style.css), so the
# canvas is authored at 1000: declared type size then equals rendered type size
# and nothing is silently shrunk by a 0.92 scale factor.
W = 1000
PAD = 24

INK = "#e6e9ef"
DIM = "#8d97a9"
FAINT = "#6b7484"
LINE = "#232b39"
BG = "#08090c"

CYN = "#22d3ee"     # readable: the promoted claims recall finds; PROMOTED
VIO = "#a78bfa"     # the journal; MERGED, as on the verdict figure
GRN = "#34d399"     # signed; SUPERSEDED (a revision), as on the verdict figure
AMB = "#fbbf24"     # scanned
ROSE = "#fb7185"    # held, never readable; REJECTED
SLATE = "#cbd5e1"   # graded: neither a signature nor a state

# ── the path: the stages a claim passes, in order ───────────────────────────
STAGES = [
    ("WRITE", "held in\nquarantine", ROSE),
    ("SCAN", "injection,\nsecrets, scripts", AMB),
    ("GRADE", "two readings; a\nperson when\npolicy asks", SLATE),
    ("SIGN", "a reviewer who\nis not the\nauthor", GRN),
    ("PROMOTE", "a signed journal\nevent, marked\nprovisional", VIO),
]

EYEBROW = "ONE CLAIM ARRIVES — WHERE IT GOES, AND WHAT HAPPENS IF SOMETHING LIKE IT IS ALREADY THERE"

FOOT = ("Nothing is edited in place. A correction is a new claim that takes the same "
        "path, and the claim it replaces is kept.")
CAVEAT = ("Mechanism only — what connects to what, and who may not act. No rates, volumes or "
          "timings are claimed.")
ARRIVES, ARRIVES_SUB = "A CLAIM ARRIVES", "an agent wrote something down"
LOOP_HEAD = ("IT MATCHES", "SOMETHING")
LOOP_NOTE = "a correction is a new claim on the same path"
LOOP_RULE = "graded and signed again, by a reviewer who is not its author"

# The two stores' lines; each is measured and checked against its box below.
HELD_TITLE = "quarantine"
HELD_LINES = ("held here while", "it is reviewed")
HELD_NO = ("no other agent's", "recall returns it")
LIVE_TITLE = "promoted claims"
LIVE_LINES = ("what recall finds,", "each one marked", "provisional")

OUTS = [
    (CYN, "plain", "PROMOTED", "a new claim; recall finds it once it is signed"),
    (GRN, "one", "SUPERSEDED", "a correction is served; the old version is kept"),
    (VIO, "many", "MERGED", "by reviewers only; the parents are kept"),
    (ROSE, "hollow", "REJECTED", "kept, with the reason recorded; never recalled"),
]

# ── geometry ────────────────────────────────────────────────────────────────
# Two containers: quarantine on the left of the path (no other agent's recall
# reaches it), promoted claims on the right (recall reads them). The path runs
# between them, so the figure's left-to-right axis IS the boundary being
# crossed -- that is the one thing the reader must take away.
STAGE_W = 112
STAGE_H = 76                       # three lines of sub-text under the stage name
STAGE_GAP = 9
PIPE_Y = 190                       # centre line of the stage row
STORE_W = 140
PIPE_X0 = PAD + STORE_W + 20       # immediately after the quarantine container
LOOP_Y = 300                       # the correction's return path
COL2 = PAD + 470                   # second column of outcomes

STYLE = """    .eyebrow { font-size:11.5px; font-weight:700; letter-spacing:.09em; fill:#8d97a9; }
    .stage   { font-size:12.5px; font-weight:700; letter-spacing:.05em; }
    .sub     { font-size:11px; fill:#7c8698; }
    .store   { font-size:12.5px; font-weight:700; letter-spacing:.05em; }
    .storesub{ font-size:11px; fill:#7c8698; }
    .lane    { font-size:11.5px; font-weight:700; letter-spacing:.04em; fill:#e6e9ef; }
    .lanesub { font-size:11.5px; fill:#8d97a9; }
    .rule    { font-size:11px; font-weight:600; fill:#e6e9ef; }
    .out     { font-size:11.5px; font-weight:600; }
    .outsub  { font-size:11px; fill:#7c8698; }
    .foot    { font-size:13px; font-weight:600; fill:#e6e9ef; }
    .cav     { font-size:11px; fill:#6b7484; }
    .no      { font-size:11px; font-weight:600; fill:#fb7185; }

    /* The only motion is two dots tracing the two journeys. A reader who asks
       the OS for less motion gets the same figure standing still -- the paths,
       the marks and every label are static. */
    @media (prefers-reduced-motion: reduce) { .mover { display:none; } }"""


def defs():
    marks = [("ar", DIM)] + [(f"ar{i}", STAGES[i][2]) for i in range(1, len(STAGES))]
    out = ["""  <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1e2430" stop-opacity="0"/>
    <stop offset=".07" stop-color="{LINE}"/>
    <stop offset=".93" stop-color="{LINE}"/>
    <stop offset="1" stop-color="#1e2430" stop-opacity="0"/>
  </linearGradient>""".replace("{LINE}", LINE)]
    for mid, colour in marks:
        out.append(f"""  <marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5"
          markerHeight="5.5" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{colour}"/>
  </marker>""")
    return "\n".join(out)


def measure(pairs):
    """Rendered width of each (class, text) at the class it will use."""
    if not CHROME:
        raise SystemExit("set CHROME_PATH")
    tmp = ROOT / ".tmp" / "_cp.svg"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    rows, y = [], 30
    for cls, txt in pairs:
        esc = txt.replace("&", "&amp;").replace("<", "&lt;")
        rows.append(f'<text class="{cls}" x="10" y="{y}">{esc}</text>')
        y += 34
    tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" '
                   f'height="{y + 20}" font-family="{FONT}">'
                   f'<style>{STYLE}</style>' + "\n".join(rows) + "</svg>")
    js = ROOT / ".tmp" / "_cp.js"
    js.write_text("""
const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME_PATH,args:['--no-sandbox']});
const p=await b.newPage();await p.goto('file://'+process.argv[2]);
const o=await p.evaluate(()=>{const r={};document.querySelectorAll('text')
.forEach(t=>r[t.textContent]=+t.getBBox().width.toFixed(1));return r;});
console.log(JSON.stringify(o));await b.close();})();""")
    r = subprocess.run(["node", str(js), str(tmp)], cwd=ROOT, capture_output=True,
                       text=True, env={**os.environ, "CHROME_PATH": CHROME})
    if r.returncode:
        raise SystemExit(r.stderr[-700:])
    return json.loads(r.stdout)


def stage_x(i):
    return PIPE_X0 + i * (STAGE_W + STAGE_GAP)


def build(Wd):
    o = []
    n = len(STAGES)
    pipe_x1 = stage_x(n - 1) + STAGE_W

    o.append(f'<text class="eyebrow" x="{PAD}" y="34">{EYEBROW}</text>')
    o.append(f'<path d="M {PAD} 48 L {W - PAD} 48" stroke="url(#rule)" fill="none"/>')

    # ── the two stores, as two containers ───────────────────────────────────
    # Separate boxes with no shared edge: a single box with a dividing line
    # would read as one store with a filter.
    lx, ly = PAD, PIPE_Y - 46
    o.append(f'<rect x="{lx}" y="{ly}" width="{STORE_W}" height="92" rx="7" '
             f'fill="#0d1017" stroke="{LINE}" stroke-width="1.5"/>')
    o.append(f'<text class="store" x="{lx + 14}" y="{ly + 26}" fill="{ROSE}">{HELD_TITLE}</text>')
    for k, ln in enumerate(HELD_LINES):
        o.append(f'<text class="storesub" x="{lx + 14}" y="{ly + 44 + k * 14}">{ln}</text>')
    # Two lines: one line overflowed the box. The box width is set by the path
    # fitting on the canvas, so the text wraps rather than the box growing.
    for k, ln in enumerate(HELD_NO):
        o.append(f'<text class="no" x="{lx + 14}" y="{ly + 76 + k * 12}">{ln}</text>')

    rx = pipe_x1 + 34
    o.append(f'<rect x="{rx}" y="{ly}" width="{W - PAD - rx}" height="92" rx="7" '
             f'fill="#0d1017" stroke="{LINE}" stroke-width="1.5"/>')
    o.append(f'<text class="store" x="{rx + 14}" y="{ly + 26}" fill="{CYN}">{LIVE_TITLE}</text>')
    for k, ln in enumerate(LIVE_LINES):
        o.append(f'<text class="storesub" x="{rx + 14}" y="{ly + 45 + k * 15}">{ln}</text>')

    # ── the path: five stages, one row ─────────────────────────────────────
    top = PIPE_Y - STAGE_H / 2
    for i, (name, sub, col) in enumerate(STAGES):
        x = stage_x(i)
        # A tinted border and a colour-matched title, on the same dark fill: the
        # box stays a container, the colour tells you which kind of stop it is.
        o.append(f'<rect x="{x}" y="{top:g}" width="{STAGE_W}" '
                 f'height="{STAGE_H}" rx="6" fill="#10141d" stroke="{col}" '
                 f'stroke-width="1.5" stroke-opacity=".5"/>')
        # a 3px cap on the left edge, so the colour survives at small scale
        o.append(f'<path d="M {x + 1.5} {top + 6:g} '
                 f'L {x + 1.5} {top + STAGE_H - 6:g}" stroke="{col}" '
                 f'stroke-width="3" stroke-linecap="round" fill="none"/>')
        o.append(f'<text class="stage" x="{x + 11}" y="{PIPE_Y - 20:g}" fill="{col}">{name}</text>')
        for k, ln in enumerate(sub.split("\n")):
            o.append(f'<text class="sub" x="{x + 11}" y="{PIPE_Y - 3 + k * 13:g}">{ln}</text>')
        if i:
            o.append(f'<path d="M {x - STAGE_GAP + 2} {PIPE_Y} L {x - 4} {PIPE_Y}" '
                     f'stroke="{col}" stroke-width="1.5" stroke-opacity=".7" '
                     f'fill="none" marker-end="url(#ar{i})"/>')

    # quarantine -> path, and path -> promoted claims. The second arrow is the
    # only one in the figure that enters the promoted store.
    o.append(f'<path d="M {lx + STORE_W + 3} {PIPE_Y} L {PIPE_X0 - 4} {PIPE_Y}" '
             f'stroke="{DIM}" stroke-width="1.4" fill="none" marker-end="url(#ar)"/>')
    o.append(f'<path d="M {pipe_x1 + 3} {PIPE_Y} L {rx - 4} {PIPE_Y}" '
             f'stroke="{CYN}" stroke-width="1.8" fill="none" marker-end="url(#ar)"/>')

    return o, pipe_x1, lx, rx, ly


def journeys(o, pipe_x1, lx, rx, ly, Wd):
    """The two trips down the path.

    Trip 1 is the arriving claim. Trip 2 is the correction that arrives when it
    meets one already there -- a separate claim, on the same path, graded and
    signed by a reviewer who is not its author. Drawing trip 2 as a return path
    under the stages is the only honest shape: an arrow from the promoted store
    straight back into it would say "edit", which is the thing that never
    happens.
    """
    # ── trip 1: the claim that just arrived ─────────────────────────────────
    y1 = ly - 30
    o.append(f'<text class="lane" x="{PAD}" y="{y1}">{ARRIVES}</text>')
    kx = PAD + Wd[ARRIVES] + 12
    o.append(f'<circle cx="{kx + 5:g}" cy="{y1 - 4:g}" r="5" fill="{INK}" fill-opacity=".9"/>')
    o.append(f'<text class="lanesub" x="{kx + 17:g}" y="{y1}">{ARRIVES_SUB}</text>')

    # the moving dot for trip 1: quarantine, through every stage, into the store
    o.append(f'<circle class="mover" r="4.4" fill="{INK}">'
             f'<animateMotion dur="7s" repeatCount="indefinite" keyPoints="0;1" '
             f'keyTimes="0;1" calcMode="linear" '
             f'path="M {lx + STORE_W + 6} {PIPE_Y} L {rx + 60} {PIPE_Y}"/>'
             f'<animate attributeName="fill-opacity" dur="7s" repeatCount="indefinite" '
             f'values="0;.95;.95;0" keyTimes="0;.06;.9;1"/></circle>')

    # ── the fork: does anything like it already exist? ──────────────────────
    # It sits after PROMOTE, where the claim is a signed claim and not a guess.
    fx = pipe_x1 + 17
    loop_left = PIPE_X0 + STAGE_W / 2

    # ── trip 2: the correction ──────────────────────────────────────────────
    # ONE path with ONE arrowhead, so it reads as one journey back to the front.
    LOOP_PATH = (f"M {fx} {PIPE_Y + STAGE_H / 2 + 8:g} "
                 f"L {fx} {LOOP_Y - 14} "
                 f"Q {fx} {LOOP_Y} {fx - 16} {LOOP_Y} "
                 f"L {loop_left + 40} {LOOP_Y} "
                 f"Q {loop_left} {LOOP_Y} {loop_left} {LOOP_Y - 22} "
                 f"L {loop_left} {PIPE_Y + STAGE_H / 2 + 7:g}")
    o.append(f'<path d="{LOOP_PATH}" stroke="{DIM}" stroke-width="1.7" fill="none" '
             f'stroke-dasharray="5 4" marker-end="url(#ar)"/>')

    # The loop's label sits to the LEFT of the return path, in the gutter under
    # the quarantine box, one line each.
    o.append(f'<text class="lane" x="{PAD}" y="{LOOP_Y - 6:g}">{LOOP_HEAD[0]}</text>')
    o.append(f'<text class="lane" x="{PAD}" y="{LOOP_Y + 10:g}">{LOOP_HEAD[1]}</text>')

    # the mark: a new claim with its retained parent behind it -- the verdict
    # figure's REVISED glyph, so the two figures teach one language.
    mx, my = PAD + 6, LOOP_Y + 32
    o.append(f'<circle cx="{mx - 4.6:g}" cy="{my + 3.6:g}" r="3.2" fill="{GRN}" fill-opacity=".34"/>')
    o.append(f'<circle cx="{mx:g}" cy="{my:g}" r="5" fill="{GRN}" fill-opacity=".95"/>')
    o.append(f'<text class="lanesub" x="{mx + 14:g}" y="{my + 4:g}">{LOOP_NOTE}</text>')

    # the rule that makes the loop trustworthy, stated beside the return line
    o.append(f'<text class="rule" x="{loop_left + 70:g}" y="{LOOP_Y + 19:g}">{LOOP_RULE}</text>')

    # the moving dot for trip 2
    o.append(f'<circle class="mover" r="4.2" fill="{INK}">'
             f'<animateMotion dur="7s" begin="2.2s" repeatCount="indefinite" '
             f'calcMode="linear" keyPoints="0;1" keyTimes="0;1" '
             f'path="{LOOP_PATH}"/>'
             f'<animate attributeName="fill-opacity" dur="7s" begin="2.2s" '
             f'repeatCount="indefinite" values="0;.95;.95;0" keyTimes="0;.08;.85;1"/></circle>')

    return o


def outcomes(o):
    """The four ways it can end: two rows of two, each one kept in the journal."""
    oy = LOOP_Y + 96
    # 22px above the first row: at 16 the rule sat 5px off the cap-height of the
    # first-row labels and the clearance gate wants 6.
    o.append(f'<path d="M {PAD} {oy - 22:g} L {W - PAD} {oy - 22:g}" stroke="url(#rule)" '
             f'fill="none"/>')
    for idx, (colour, glyph, name, sub) in enumerate(OUTS):
        x = (PAD, COL2)[idx % 2]
        oy_row = oy + (idx // 2) * 40
        gx, gy = x + 5, oy_row - 4
        if glyph == "plain":
            o.append(f'<circle cx="{gx}" cy="{gy}" r="4.8" fill="{colour}" fill-opacity=".9"/>')
        elif glyph == "one":
            o.append(f'<circle cx="{gx - 4.4:g}" cy="{gy + 3.6:g}" r="3.1" fill="{colour}" fill-opacity=".34"/>')
            o.append(f'<circle cx="{gx}" cy="{gy}" r="4.8" fill="{colour}" fill-opacity=".9"/>')
        elif glyph == "many":
            o.append(f'<circle cx="{gx - 4.6:g}" cy="{gy + 3.2:g}" r="3.1" fill="{colour}" fill-opacity=".34"/>')
            o.append(f'<circle cx="{gx + 1.1:g}" cy="{gy + 4.1:g}" r="3.1" fill="{colour}" fill-opacity=".34"/>')
            o.append(f'<circle cx="{gx}" cy="{gy}" r="4.8" fill="{colour}" fill-opacity=".9"/>')
        else:
            # hollow: kept in the journal, never readable
            o.append(f'<circle cx="{gx}" cy="{gy}" r="4.2" fill="none" stroke="{colour}" '
                     f'stroke-width="1.5" stroke-opacity=".8"/>')
        o.append(f'<text class="out" x="{x + 16}" y="{oy_row:g}" fill="{colour}">{name}</text>')
        o.append(f'<text class="outsub" x="{x + 16}" y="{oy_row + 16:g}">{sub}</text>')
    return o, oy + 40


def render():
    pairs = [("eyebrow", EYEBROW), ("foot", FOOT), ("cav", CAVEAT),
             ("lane", ARRIVES), ("lanesub", ARRIVES_SUB),
             ("store", HELD_TITLE), ("store", LIVE_TITLE),
             ("rule", LOOP_RULE), ("lanesub", LOOP_NOTE)]
    pairs += [("lane", t) for t in LOOP_HEAD]
    pairs += [("storesub", t) for t in HELD_LINES + LIVE_LINES]
    pairs += [("no", t) for t in HELD_NO]
    for name, sub, _ in STAGES:
        pairs.append(("stage", name))
        pairs += [("sub", ln) for ln in sub.split("\n")]
    for _, _, a, b in OUTS:
        pairs += [("out", a), ("outsub", b)]
    Wd = measure(pairs)

    body, pipe_x1, lx, rx, ly = build(Wd)
    body = journeys(body, pipe_x1, lx, rx, ly, Wd)
    body, oy = outcomes(body)

    base = oy + 34
    body.append(f'<path d="M {PAD} {base:g} L {W - PAD} {base:g}" stroke="url(#rule)" fill="none"/>')
    body.append(f'<text class="foot" x="{PAD}" y="{base + 26:g}">{FOOT}</text>')
    body.append(f'<text class="cav" x="{PAD}" y="{base + 45:g}">{CAVEAT}</text>')
    height = int(base + 64)

    # ── layout pre-flight, before writing ──────────────────────────────────
    problems = []
    if pipe_x1 + 34 + 150 > W - PAD:
        problems.append(f"path ends at {pipe_x1}, the promoted store will not fit")
    for cls, t in (("foot", FOOT), ("cav", CAVEAT), ("eyebrow", EYEBROW)):
        if PAD + Wd[t] > W - PAD:
            problems.append(f"{cls} overruns by {PAD + Wd[t] - (W - PAD):.0f}px")
    for i, (_, _, a, b) in enumerate(OUTS):
        end = (PAD, COL2)[i % 2] + 16 + max(Wd[a], Wd[b])
        limit = COL2 - 20 if i % 2 == 0 else W - PAD
        if end > limit:
            problems.append(f'outcome "{a}" overruns its column by {end - limit:.0f}px')
    for name, sub, _ in STAGES:
        for ln in [name] + sub.split("\n"):
            if Wd[ln] > STAGE_W - 20:
                problems.append(f'stage text "{ln}" is {Wd[ln]:.0f}px > {STAGE_W - 20}px')
    if PIPE_X0 + 8 + 70 + Wd[LOOP_RULE] > W - PAD:
        problems.append(f"loop rule overruns by "
                        f"{PIPE_X0 + 8 + 70 + Wd[LOOP_RULE] - (W - PAD):.0f}px")
    if PAD + 20 + Wd[LOOP_NOTE] > W - PAD:
        problems.append(f"loop note overruns by {PAD + 20 + Wd[LOOP_NOTE] - (W - PAD):.0f}px")
    for t in (HELD_TITLE,) + HELD_LINES + HELD_NO:
        if Wd[t] > STORE_W - 28:
            problems.append(f'quarantine text "{t}" is {Wd[t]:.0f}px > {STORE_W - 28}px')
    # the promoted store is whatever is left between the path and the margin
    live_w = W - PAD - rx
    for t in (LIVE_TITLE,) + LIVE_LINES:
        if Wd[t] > live_w - 28:
            problems.append(f'promoted-store text "{t}" is {Wd[t]:.0f}px > {live_w - 28:.0f}px')
    if problems:
        for p in problems:
            print("  " + p)
        raise SystemExit("layout does not fit -- shorten copy, do not widen the canvas")

    desc = (
        "A claim arriving at the gate, and the loop that runs when it meets one already "
        "there. On the left, the quarantine: the claim is held here while it is reviewed, "
        "and no other agent's recall returns it. It passes five stages in order — "
        "WRITE, held in quarantine; SCAN, for injection, secrets and scripts; GRADE, two "
        "readings, and a person when policy asks; SIGN, by a reviewer who is not the "
        "author; and PROMOTE, a signed journal event marked provisional. Only then does a "
        "single arrow cross into the promoted claims, which recall finds. Below the path, "
        "one dashed arrow shows what happens when a claim meets one already there: a "
        "correction is a new claim that takes the same path, graded and signed again by a "
        "reviewer who is not its author. Nothing is edited in place. Four endings are "
        "possible: PROMOTED, a new claim recall finds once it is signed; SUPERSEDED, where "
        "the correction is served and the old version is kept; MERGED, by reviewers only, "
        "with the parents kept; and REJECTED, kept with the reason recorded and never "
        "recalled. The figure shows mechanism only — what connects to what and who may "
        "not act — and claims no rates, volumes or timings.")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}"
     role="img" aria-labelledby="t d" font-family="{FONT}">
<title id="t">Where an arriving claim goes, and the loop that runs when it meets one already there</title>
<desc id="d">{desc}</desc>
<defs>
  <style><![CDATA[
{STYLE}
  ]]></style>
{defs()}
</defs>
<rect width="{W}" height="{height}" fill="{BG}"/>
{chr(10).join(body)}
</svg>
""", height


def main():
    svg, height = render()
    if "--check" in sys.argv[1:]:
        if not OUT.exists() or OUT.read_text() != svg:
            raise SystemExit(f"{OUT.relative_to(ROOT)} is stale: run python3 claim-path.py")
        print(f"{OUT.relative_to(ROOT)} up to date")
        return
    OUT.write_text(svg)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(svg)} bytes, {len(STAGES)} stages, "
          f"path {PIPE_X0}→{stage_x(len(STAGES) - 1) + STAGE_W}, height {height})")


if __name__ == "__main__":
    main()
