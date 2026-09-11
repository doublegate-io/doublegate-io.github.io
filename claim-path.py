#!/usr/bin/env python3
"""Generate claim-path.svg -- a new claim travelling the plumbing, and the loop.

What this figure is for
-----------------------
Three figures now sit on the site and each answers a different question:

  artifact-flow.svg   WHO decides. Five numbered stages, the authority chain,
                      who may read it and when. 44 labels.
  hero-field.svg      WHAT comes back. Five verdicts over sixty submissions.
  this one            WHERE it goes. The path one claim takes through the pipe,
                      and what happens when it meets a claim already there.

The thing neither of the other two shows is the loop. A reader who has seen
"MERGED: several beliefs reconciled into one" reasonably assumes the store edits
something. It does not. Consolidation emits a NEW candidate with derives_from
edges to its parents, and that candidate makes a second full trip through the
same gate, graded by an identity that is not the consolidator. The parents are
superseded on promotion -- never edited, never deleted -- and if the merge is
refused, both parents simply stay ACTIVE and the store stays contradictory.

That loop is the whole argument for why a merge cannot launder anything, and it
is invisible on a straight left-to-right pipeline. So the figure draws the pipe
once and sends two things down it: the arriving claim, and the merge candidate
its arrival provoked.

Grounding (every element traces to the design repo)
---------------------------------------------------
  ADR-0001   limbo.db and active.db are physically separate SQLite databases,
             so the two stores are drawn as two containers, not two zones of one
  ADR-0008   the write path is gated, not the read path -- one chokepoint
  ADR-0016   consolidation is a proposer, never a decider: it emits a candidate
             with derives_from edges, has no authority to promote/edit/delete,
             the candidate is gated like any other artifact by a non-C13
             identity, parents are superseded on promotion never edited or
             deleted, and a REJECTED merge leaves both parents ACTIVE
  ADR-0016 §6 C13 never proposes across trust classes
  capture §4 derives_from: "one parent for extraction, two or more when it is a
             consolidation candidate" -- this is why one-parent and many-parent
             are different marks, not a stylistic choice
  release    the integrator is the ONLY writer to a consumer surface, and only
             materializes with a quorum-satisfied promotion record
  retrieval  C15 holds a connection to active.db and no handle that resolves to
             limbo.db -- the reason the read arrow touches only one container

Honesty
-------
No counts, rates or timings appear here. This is a mechanism diagram in a design
phase, so it claims only structure: what connects to what, in what order, and
who is forbidden from doing what. Nothing on the figure asserts a measurement.

Deterministic: computed geometry, no randomness, byte-identical every run.

Run:  CHROME_PATH=... python3 claim-path.py
"""
from __future__ import annotations

import json
import os
import subprocess
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

CYN = "#22d3ee"     # the arriving claim
VIO = "#a78bfa"     # the merge candidate the arrival provoked
GRN = "#34d399"     # promoted / readable
AMB = "#fbbf24"     # refused merge: both parents stay live
ROSE = "#fb7185"    # never readable

# ── the pipe: the stages a candidate passes, in order ───────────────────────
# Names are the components' own. Every one of these is on the write path; there
# is exactly one writer to a consumer surface at the end of it.
BLU = "#60a5fa"     # ratify

STAGES = [
    ("ADMIT", "class, and edges\nto any parent", AMB),
    ("SCAN", "injection, keys,\nscripts", ROSE),
    ("ASSESS", "AI trust\n0–100", CYN),
    ("DECIDE", "approve or\nreject", BLU),
    ("RECORD", "a signed event\nin the ledger", GRN),
]

EYEBROW = "ONE CLAIM ARRIVES \u2014 WHERE IT GOES, AND WHAT HAPPENS IF SOMETHING LIKE IT IS ALREADY THERE"

FOOT = ("A merge is not an edit. Consolidation proposes a new claim and sends it back "
        "through the gate, judged by someone else.")
CAVEAT = ("Mechanism only \u2014 what connects to what, and who may not act. No rates, volumes or "
          "timings are claimed.")
LOOP_NOTE = "a second trip through the same gate \u2014 nothing is edited in place"
LOOP_RULE = "graded by an identity that did not propose it"

# ── geometry ────────────────────────────────────────────────────────────────
# Two containers because ADR-0001 makes them two databases. Limbo on the left of
# the pipe (nothing reads it), active on the right (everything reads it). The
# pipe runs between them, so the figure's left-to-right axis IS the admission
# boundary being crossed -- that is the one thing the reader must take away.
STAGE_W = 112
STAGE_H = 58
STAGE_GAP = 9
PIPE_Y = 190                       # centre line of the stage row
STORE_W = 140                      # sized to hold "memory limbo" at 12.5px
PIPE_X0 = PAD + STORE_W + 20       # immediately after the limbo container
LOOP_Y = 300                       # the consolidation return path

STYLE = """    .eyebrow { font-size:11.5px; font-weight:700; letter-spacing:.09em; fill:#8d97a9; }
    .stage   { font-size:12.5px; font-weight:700; letter-spacing:.05em; fill:#e6e9ef; }
    .sub     { font-size:11px; fill:#7c8698; }
    .store   { font-size:12.5px; font-weight:700; letter-spacing:.05em; }
    .storesub{ font-size:11px; fill:#7c8698; }
    .lane    { font-size:11.5px; font-weight:700; letter-spacing:.04em; }
    .lanesub { font-size:11.5px; fill:#8d97a9; }
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
    S1, S2, S3, S4 = (STAGES[i][2] for i in range(1, 5))
    return f"""  <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1e2430" stop-opacity="0"/>
    <stop offset=".07" stop-color="{LINE}"/>
    <stop offset=".93" stop-color="{LINE}"/>
    <stop offset="1" stop-color="#1e2430" stop-opacity="0"/>
  </linearGradient>
  <marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5"
          markerHeight="5.5" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{DIM}"/>
  </marker>
  <marker id="ar1" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5"
          markerHeight="5.5" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{S1}"/>
  </marker>
  <marker id="ar2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5"
          markerHeight="5.5" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{S2}"/>
  </marker>
  <marker id="ar3" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5"
          markerHeight="5.5" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{S3}"/>
  </marker>
  <marker id="ar4" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5"
          markerHeight="5.5" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{S4}"/>
  </marker>
  <marker id="arc" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5"
          markerHeight="5.5" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{CYN}"/>
  </marker>
  <marker id="arv" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5.5"
          markerHeight="5.5" orient="auto-start-reverse">
    <path d="M 0 1 L 9 5 L 0 9 z" fill="{VIO}"/>
  </marker>"""


def measure(pairs):
    """Rendered width/height of each (class, text) at the class it will use."""
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
    # Drawn as separate boxes with no shared edge, because they are separate
    # databases. A single box with a dividing line would be the wrong picture:
    # it would imply one store with a filter, which is exactly the design that
    # ADR-0001 rejects.
    lx, ly = PAD, PIPE_Y - 46
    o.append(f'<rect x="{lx}" y="{ly}" width="{STORE_W}" height="92" rx="7" '
             f'fill="#0d1017" stroke="{LINE}" stroke-width="1.5"/>')
    o.append(f'<text class="store" x="{lx + 14}" y="{ly + 26}" fill="{AMB}">memory limbo</text>')
    o.append(f'<text class="storesub" x="{lx + 14}" y="{ly + 44}">held here while</text>')
    o.append(f'<text class="storesub" x="{lx + 14}" y="{ly + 58}">it is judged</text>')
    # Two lines: one line overflowed the box by 40px. The box width is set by the
    # pipe fitting on the canvas, so the text wraps rather than the box growing.
    o.append(f'<text class="no" x="{lx + 14}" y="{ly + 76}">no read path</text>')
    o.append(f'<text class="no" x="{lx + 14}" y="{ly + 88}">reaches this</text>')

    rx = pipe_x1 + 34
    o.append(f'<rect x="{rx}" y="{ly}" width="{W - PAD - rx}" height="92" rx="7" '
             f'fill="#0d1017" stroke="{LINE}" stroke-width="1.5"/>')
    o.append(f'<text class="store" x="{rx + 14}" y="{ly + 26}" fill="{GRN}">active memory</text>')
    o.append(f'<text class="storesub" x="{rx + 14}" y="{ly + 45}">eligible claims</text>')
    o.append(f'<text class="storesub" x="{rx + 14}" y="{ly + 60}">current access</text>')
    o.append(f'<text class="storesub" x="{rx + 14}" y="{ly + 80}">one writer, ever</text>')

    # ── the pipe: five stages, one row ─────────────────────────────────────
    for i, (name, sub, col) in enumerate(STAGES):
        x = stage_x(i)
        # A tinted border and a colour-matched title, on the same dark fill: the
        # box stays a container, the colour tells you which kind of stop it is.
        o.append(f'<rect x="{x}" y="{PIPE_Y - STAGE_H / 2:g}" width="{STAGE_W}" '
                 f'height="{STAGE_H}" rx="6" fill="#10141d" stroke="{col}" '
                 f'stroke-width="1.5" stroke-opacity=".5"/>')
        # a 3px cap on the left edge, so the colour survives at small scale
        o.append(f'<path d="M {x + 1.5} {PIPE_Y - STAGE_H / 2 + 6:g} '
                 f'L {x + 1.5} {PIPE_Y + STAGE_H / 2 - 6:g}" stroke="{col}" '
                 f'stroke-width="3" stroke-linecap="round" fill="none"/>')
        o.append(f'<text class="stage" x="{x + 11}" y="{PIPE_Y - 13:g}" fill="{col}">{name}</text>')
        for k, ln in enumerate(sub.split("\n")):
            o.append(f'<text class="sub" x="{x + 11}" y="{PIPE_Y + 2 + k * 13:g}">{ln}</text>')
        if i:
            o.append(f'<path d="M {x - STAGE_GAP + 2} {PIPE_Y} L {x - 4} {PIPE_Y}" '
                     f'stroke="{col}" stroke-width="1.5" stroke-opacity=".7" '
                     f'fill="none" marker-end="url(#ar{i})"/>')

    # limbo -> pipe, and pipe -> active. The second arrow is the chokepoint: it
    # is the only arrow in the figure that enters active.db.
    o.append(f'<path d="M {lx + STORE_W + 3} {PIPE_Y} L {PIPE_X0 - 4} {PIPE_Y}" '
             f'stroke="{DIM}" stroke-width="1.4" fill="none" marker-end="url(#ar)"/>')
    o.append(f'<path d="M {pipe_x1 + 3} {PIPE_Y} L {rx - 4} {PIPE_Y}" '
             f'stroke="{GRN}" stroke-width="1.8" fill="none" marker-end="url(#ar)"/>')

    return o, pipe_x1, lx, rx, ly


def journeys(o, pipe_x1, lx, rx, ly, Wd):
    """The two trips down the pipe, and the three ways they can end.

    Trip 1 is the arriving claim. Trip 2 is the merge candidate its arrival
    provoked -- a separate artifact, on the same pipe, judged by someone else.
    Drawing trip 2 as a return path under the pipe is the only honest shape:
    a curved arrow back into ADMIT says "second full trip", where an arrow from
    MERGED straight into active.db would say "edit", which is the claim ADR-0016
    exists to refuse.
    """
    n = len(STAGES)
    a_in = PIPE_X0
    a_out = pipe_x1

    # ── trip 1: the claim that just arrived ─────────────────────────────────
    y1 = ly - 30
    o.append(f'<text class="lane" x="{PAD}" y="{y1}" fill="{CYN}">A CLAIM ARRIVES</text>')
    kx = PAD + Wd["A CLAIM ARRIVES"] + 12
    o.append(f'<circle cx="{kx + 5:g}" cy="{y1 - 4:g}" r="5" fill="{CYN}" fill-opacity=".9"/>')
    o.append(f'<text class="lanesub" x="{kx + 17:g}" y="{y1}">an agent wrote something down</text>')

    # the moving dot for trip 1: limbo, through every stage, into active
    o.append(f'<circle class="mover" r="4.4" fill="{CYN}">'
             f'<animateMotion dur="7s" repeatCount="indefinite" keyPoints="0;1" '
             f'keyTimes="0;1" calcMode="linear" '
             f'path="M {lx + STORE_W + 6} {PIPE_Y} L {rx + 60} {PIPE_Y}"/>'
             f'<animate attributeName="fill-opacity" dur="7s" repeatCount="indefinite" '
             f'values="0;.95;.95;0" keyTimes="0;.06;.9;1"/></circle>')

    # ── the fork: does anything like it already exist? ──────────────────────
    # This is the question the figure is built to answer, so it sits on the pipe
    # at the point where it is actually asked -- after RECORD, when the claim is
    # a real artifact with a signature, not before, when it is still a guess.
    fx = a_out + 17
    loop_left = PIPE_X0 + STAGE_W / 2

    # ── trip 2: the merge candidate ────────────────────────────────────────
    # ONE path with ONE arrowhead. It was two -- a vertical drop with its own
    # marker, then the return leg with another -- which read as two separate hops
    # instead of one journey back to the front of the pipe.
    LOOP_PATH = (f"M {fx} {PIPE_Y + STAGE_H / 2 + 8:g} "
                 f"L {fx} {LOOP_Y - 14} "
                 f"Q {fx} {LOOP_Y} {fx - 16} {LOOP_Y} "
                 f"L {loop_left + 40} {LOOP_Y} "
                 f"Q {loop_left} {LOOP_Y} {loop_left} {LOOP_Y - 22} "
                 f"L {loop_left} {PIPE_Y + STAGE_H / 2 + 7:g}")
    o.append(f'<path d="{LOOP_PATH}" stroke="{VIO}" stroke-width="1.7" fill="none" '
             f'stroke-dasharray="5 4" marker-end="url(#arv)"/>')

    # The loop's label sits to the LEFT of the return path, in the gutter under
    # the limbo box, on one line each -- stacking three lines under the path put
    # them through the footer.
    o.append(f'<text class="lane" x="{PAD}" y="{LOOP_Y - 6:g}" fill="{VIO}">IT MATCHES</text>')
    o.append(f'<text class="lane" x="{PAD}" y="{LOOP_Y + 10:g}" fill="{VIO}">SOMETHING</text>')

    # the mark: a new claim with two retained parents behind it -- the same
    # glyph vocabulary as hero-field.svg, so the two figures teach one language.
    mx, my = PAD + 6, LOOP_Y + 32
    o.append(f'<circle cx="{mx - 5:g}" cy="{my + 3.4:g}" r="3.2" fill="{VIO}" fill-opacity=".34"/>')
    o.append(f'<circle cx="{mx + 1.2:g}" cy="{my + 4.4:g}" r="3.2" fill="{VIO}" fill-opacity=".34"/>')
    o.append(f'<circle cx="{mx:g}" cy="{my:g}" r="5" fill="{VIO}" fill-opacity=".95"/>')
    o.append(f'<text class="lanesub" x="{mx + 14:g}" y="{my + 4:g}">'
             f'{LOOP_NOTE}</text>')

    # the constraint that makes the loop trustworthy, stated ON the loop path,
    # above it, where there is clear space between the pipe and the return line
    o.append(f'<text class="no" x="{loop_left + 70:g}" y="{LOOP_Y + 19:g}">'
             f'{LOOP_RULE}</text>')

    # the moving dot for trip 2
    o.append(f'<circle class="mover" r="4.2" fill="{VIO}">'
             f'<animateMotion dur="7s" begin="2.2s" repeatCount="indefinite" '
             f'calcMode="linear" keyPoints="0;1" keyTimes="0;1" '
             f'path="{LOOP_PATH}"/>'
             f'<animate attributeName="fill-opacity" dur="7s" begin="2.2s" '
             f'repeatCount="indefinite" values="0;.95;.95;0" keyTimes="0;.08;.85;1"/></circle>')

    return o


def outcomes(o, rx, ly, Wd):
    """The three ways it can end, on the right, against active.db.

    All three are listed because the two that products usually hide are the two
    that matter here: a refused merge leaves the store contradictory on purpose,
    and a refused claim stays in the ledger with its reasons.
    """
    # Derived from the loop band, not from the store box: the outcomes sit below
    # everything the loop drew, so the two cannot collide as copy changes.
    oy = LOOP_Y + 96
    # 22px, not 16: at 16 the rule sat 5px off the cap-height of the first-row
    # labels and the clearance gate wants 6.
    o.append(f'<path d="M {PAD} {oy - 22:g} L {W - PAD} {oy - 22:g}" stroke="url(#rule)" '
             f'fill="none"/>')

    items = [
        (GRN, "plain", "PROMOTED",
         "a new claim, published within scope"),
        (VIO, "many", "MERGE ACCEPTED",
         "parents superseded, both kept, never deleted"),
        (AMB, "pair", "MERGE REFUSED",
         "both parents stay live \u2014 the store stays contradictory, on purpose"),
        (ROSE, "hollow", "REFUSED",
         "held from shared retrieval; reasons recorded"),
    ]
    # Two rows of two: acceptances on the first, refusals on the second. Four on
    # one line overran the canvas by 224px, and the pairing is the better read
    # anyway -- the two refusals are the cases the product is built around.
    col_x = [PAD, PAD + 470]
    x = PAD
    for idx, (colour, glyph, name, sub) in enumerate(items):
        x = col_x[idx % 2]
        oy_row = oy + (idx // 2) * 40
        # glyph, in the same vocabulary as the verdicts figure
        gx, gy = x + 5, oy_row - 4
        if glyph == "plain":
            o.append(f'<circle cx="{gx}" cy="{gy}" r="4.8" fill="{colour}" fill-opacity=".9"/>')
        elif glyph == "many":
            o.append(f'<circle cx="{gx - 4.6:g}" cy="{gy + 3.2:g}" r="3.1" fill="{colour}" fill-opacity=".34"/>')
            o.append(f'<circle cx="{gx + 1.1:g}" cy="{gy + 4.1:g}" r="3.1" fill="{colour}" fill-opacity=".34"/>')
            o.append(f'<circle cx="{gx}" cy="{gy}" r="4.8" fill="{colour}" fill-opacity=".9"/>')
        elif glyph == "pair":
            o.append(f'<circle cx="{gx - 3.3:g}" cy="{gy}" r="3.2" fill="{colour}" fill-opacity=".9"/>')
            o.append(f'<circle cx="{gx + 3.3:g}" cy="{gy}" r="3.2" fill="{colour}" fill-opacity=".9"/>')
        else:
            o.append(f'<circle cx="{gx}" cy="{gy}" r="4.2" fill="none" stroke="{colour}" '
                     f'stroke-width="1.5" stroke-opacity=".8"/>')
        o.append(f'<text class="out" x="{x + 16}" y="{oy_row:g}" fill="{colour}">{name}</text>')
        o.append(f'<text class="outsub" x="{x + 16}" y="{oy_row + 16:g}">{sub}</text>')

    return o, oy + 40


def main():
    pairs = [("eyebrow", EYEBROW), ("foot", FOOT), ("cav", CAVEAT),
             ("lane", "A CLAIM ARRIVES"),
             ("lanesub", "an agent wrote something down"),
             ("no", "no read path"), ("no", "reaches this"),
             ("store", "memory limbo"), ("storesub", "held here while"),
             ("storesub", "it is judged"), ("store", "active memory"),
             ("storesub", "eligible claims"), ("storesub", "current access"),
             ("storesub", "one writer, ever"),
             ("no", LOOP_RULE), ("lanesub", LOOP_NOTE),
             ("lane", "IT MATCHES"), ("lane", "SOMETHING")]
    for name, sub, _ in STAGES:
        pairs.append(("stage", name))
        pairs += [("sub", ln) for ln in sub.split("\n")]
    OUTS = [("PROMOTED", "a new claim, published within scope"),
            ("MERGE ACCEPTED", "parents superseded, both kept, never deleted"),
            ("MERGE REFUSED", "both parents stay live \u2014 the store stays contradictory, on purpose"),
            ("REFUSED", "held from shared retrieval; reasons recorded")]
    for a, b in OUTS:
        pairs += [("out", a), ("outsub", b)]
    Wd = measure(pairs)

    body, pipe_x1, lx, rx, ly = build(Wd)
    body = journeys(body, pipe_x1, lx, rx, ly, Wd)
    body, oy = outcomes(body, rx, ly, Wd)

    base = oy + 34
    body.append(f'<path d="M {PAD} {base:g} L {W - PAD} {base:g}" stroke="url(#rule)" fill="none"/>')
    body.append(f'<text class="foot" x="{PAD}" y="{base + 26:g}">{FOOT}</text>')
    body.append(f'<text class="cav" x="{PAD}" y="{base + 45:g}">{CAVEAT}</text>')
    height = int(base + 64)

    # ── layout pre-flight, before writing ──────────────────────────────────
    problems = []
    if pipe_x1 + 34 + 150 > W - PAD:
        problems.append(f"pipe ends at {pipe_x1}, active.db box will not fit")
    for cls, t in (("foot", FOOT), ("cav", CAVEAT), ("eyebrow", EYEBROW)):
        if PAD + Wd[t] > W - PAD:
            problems.append(f"{cls} overruns by {PAD + Wd[t] - (W - PAD):.0f}px")
    for i, (a, b) in enumerate(OUTS):
        end = (PAD if i % 2 == 0 else PAD + 470) + 16 + max(Wd[a], Wd[b])
        limit = PAD + 470 - 20 if i % 2 == 0 else W - PAD
        if end > limit:
            problems.append(f'outcome "{a}" overruns its column by {end - limit:.0f}px')
    for name, sub, _ in STAGES:
        for ln in [name] + sub.split("\n"):
            if Wd[ln] > STAGE_W - 20:
                problems.append(f'stage text "{ln}" is {Wd[ln]:.0f}px > {STAGE_W - 20}px')
    if PIPE_X0 + 8 + 70 + Wd[LOOP_RULE] > W - PAD:
        problems.append(f"loop rule overruns by "
                        f"{PIPE_X0 + 8 + 70 + Wd[LOOP_RULE] - (W - PAD):.0f}px")
    if PAD + 6 + 14 + Wd[LOOP_NOTE] > W - PAD:
        problems.append(f"loop note overruns by {PAD + 20 + Wd[LOOP_NOTE] - (W - PAD):.0f}px")
    for t in ("no read path", "reaches this", "memory limbo",
              "held here while", "it is judged"):
        if Wd[t] > STORE_W - 28:
            problems.append(f'limbo text "{t}" is {Wd[t]:.0f}px > {STORE_W - 28}px')
    # the active box is whatever is left between the pipe and the margin
    active_w = W - PAD - (stage_x(len(STAGES) - 1) + STAGE_W + 34)
    for t in ("active memory", "eligible claims", "current access", "one writer, ever"):
        if Wd[t] > active_w - 28:
            problems.append(f'active text "{t}" is {Wd[t]:.0f}px > {active_w - 28:.0f}px')
    if problems:
        for p in problems:
            print("  " + p)
        raise SystemExit("layout does not fit -- shorten copy, do not widen the canvas")

    desc = (
        "A claim arriving at the gate, and the loop that runs when it matches something "
        "already held. On the left, memory limbo: the claim is held here while it is judged, "
        "and no consumer read path reaches this store. It passes through five stages in order "
        "\u2014 ADMIT, which records the envelope, trust class and any derives_from edges; SCAN, "
        "for injection, keys and scripts; ASSESS, an AI trust score from 0–100; DECIDE, "
        "a distinct authorized non-author AI or human approves or rejects; and RECORD, a signed "
        "event in the ledger. Only then does a single arrow cross into active memory, the "
        "only store current access, and one component is its only writer. Below the pipe, one "
        "dashed arrow shows what happens when the arriving claim matches one already held: "
        "consolidation proposes a new claim carrying edges to every parent, and that candidate "
        "takes a second full trip through the same gate, graded by an identity that did not "
        "propose it. Nothing is edited in place. Four endings are possible: PROMOTED, a new "
        "claim readable once signed; MERGE ACCEPTED, with the parents superseded and kept, "
        "never deleted; MERGE REFUSED, where both parents stay live and the store stays "
        "contradictory on purpose; and REFUSED, which stays in the ledger with its reasons and "
        "is excluded from shared retrieval. The figure shows mechanism only \u2014 what connects to what and "
        "who may not act \u2014 and claims no rates, volumes or timings.")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}"
     role="img" aria-labelledby="t d" font-family="{FONT}">
<title id="t">Where an arriving claim goes, and the loop that runs when it matches one already held</title>
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
"""
    OUT.write_text(svg)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(svg)} bytes, {len(STAGES)} stages, "
          f"pipe {PIPE_X0}\u2192{pipe_x1}, height {height})")


if __name__ == "__main__":
    main()
