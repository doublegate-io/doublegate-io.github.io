#!/usr/bin/env python3
"""Generate hero-field.svg -- the index figure as a POPULATION, not a pipeline.

Why a different figure at all
-----------------------------
The index headline argues a population problem: "Your company is paying to teach
five hundred private AI agents." The figure under it drew a pipeline -- the
sequence one claim passes through -- which is the same thing artifact-flow.svg
already draws in full on how-it-works, with 44 labels to this one's 25. Two
figures, one idea, and the smaller one was the site's front door. Redrawing the
rail four different ways never fixed that, because the staleness was the choice
of subject, not the routing of its connectors.

So this draws the five hundred. Left: every agent taught separately, the same
lesson bought over and over, nothing shared. Right: taught once, reviewed once,
signed once, and every agent inherits it. The count IS the argument, so the count
is what the reader sees.

Why it is also structurally safer
---------------------------------
A field of dots needs almost no connectors. The last three commits were all
connector defects -- a lane through a box, a lane that re-entered the box it left,
a caption 2px under a bracket -- and every one of them was possible only because
the layout demanded a branch weave between labels. This figure has exactly two
strokes in the body. There is nearly nothing to route, so there is nearly nothing
to route wrongly.

Deterministic by construction: the dot grid is computed, the jitter is seeded, and
every label is placed relative to a measured column. Same output every run.

Run:  CHROME_PATH=... python3 hero-field.py
"""
from __future__ import annotations

import json
import math
import os
import random
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "hero-field.svg"
CHROME = os.environ.get("CHROME_PATH", "")

FONT = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Inter, sans-serif"

# ── canvas ──────────────────────────────────────────────────────────────────
W = 1080
PAD = 24
GUT = 56                      # the divide between the two halves
COLW = (W - 2 * PAD - GUT) / 2
LX = PAD                      # left column origin
RX = PAD + COLW + GUT         # right column origin

# ── the population ──────────────────────────────────────────────────────────
# 500 agents, drawn as a 25x20 field. Not "about five hundred": exactly the
# number the headline says, because a reader who counts the columns and finds
# 500 has just verified the claim themselves.
COLS, ROWS = 25, 20
TOTAL = COLS * ROWS
assert TOTAL == 500, TOTAL

DOT_R = 3.0
FIELD_TOP = 150
CELL_W = COLW / COLS
CELL_H = 7.4
JITTER = 0.55                 # a hand-placed feel without breaking the grid
SEED = 20260907               # fixed: the figure must be byte-identical each run

STYLE = """    .zn  { font-size:11.5px; font-weight:700; letter-spacing:.1em; fill:#8d97a9; }
    .hd  { font-size:15px; font-weight:700; fill:#e6e9ef; }
    .big { font-size:38px; font-weight:700; letter-spacing:-.01em; }
    .nm  { font-size:13.5px; font-weight:600; fill:#e6e9ef; }
    .sb  { font-size:12.5px; fill:#97a1b2; }
    .tiny{ font-size:11.5px; fill:#8d97a9; }
    .panel { fill:#0e1118; stroke:#1e2430; stroke-width:1.4; }

    /* A reader who asks the OS for less motion gets the static figure. The
       animation only re-states what the layout already shows. */
    @media (prefers-reduced-motion: reduce) { .mover { display:none; } }"""

DEFS = """  <linearGradient id="fAlone" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fb7185" stop-opacity=".85"/>
    <stop offset="1" stop-color="#fb7185" stop-opacity=".38"/>
  </linearGradient>
  <linearGradient id="fShared" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#22d3ee" stop-opacity=".9"/>
    <stop offset="1" stop-color="#34d399" stop-opacity=".55"/>
  </linearGradient>
  <linearGradient id="seam" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1e2430" stop-opacity="0"/>
    <stop offset=".18" stop-color="#2a3342" stop-opacity="1"/>
    <stop offset=".82" stop-color="#2a3342" stop-opacity="1"/>
    <stop offset="1" stop-color="#1e2430" stop-opacity="0"/>
  </linearGradient>
  <filter id="soft" x="-70%" y="-70%" width="240%" height="240%">
    <feGaussianBlur stdDeviation="3.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>"""


def measure(pairs):
    """Rendered width of each (class, string) at the class it will actually use."""
    if not CHROME:
        raise SystemExit("set CHROME_PATH")
    tmp = ROOT / ".tmp" / "_hf.svg"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    rows, y = [], 24
    for cls, txt in pairs:
        rows.append(f'<text class="{cls}" x="10" y="{y}">'
                    f'{txt.replace("&", "&amp;")}</text>')
        y += 30
    tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" '
                   f'height="{y + 20}" font-family="{FONT}">'
                   f'<style>{STYLE}</style>' + "\n".join(rows) + "</svg>")
    js = ROOT / ".tmp" / "_hf.js"
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
        raise SystemExit(r.stderr[-600:])
    return json.loads(r.stdout)


def field(x0, cols, rows, seed, taught_idx=None):
    """The dot field. Returns (svg, positions). Seeded, so output is stable."""
    rnd = random.Random(seed)
    out, pos = [], []
    for r in range(rows):
        for c in range(cols):
            cx = x0 + CELL_W * (c + 0.5) + rnd.uniform(-JITTER, JITTER)
            cy = FIELD_TOP + CELL_H * (r + 0.5) + rnd.uniform(-JITTER, JITTER)
            pos.append((cx, cy))
    return out, pos


# ── copy: the argument, stated once ─────────────────────────────────────────
# The numeral must count THE SAME THING the field counts, or the reader has to
# work out mid-glance that the dots are agents while the big number is lessons.
# The first draft did exactly that -- 500 dots meaning agents beside a 500 meaning
# lessons bought -- and the unit only resolved from the footer. Both numerals now
# count LIT DOTS, so the claim is verifiable by looking at the picture.
L_HEAD   = "every one taught separately"
L_BIG    = "500"
L_BIGSUB = "agents taught"
L_LINES  = [
    ("nm", "Every correction lands in one agent and stops."),
    ("sb", "The next engineer hits the same wrong assumption"),
    ("sb", "and pays to correct it again. Nobody can say"),
    ("sb", "who decided what, or on what basis."),
]
R_HEAD   = "the rest inherit it"
R_BIG    = "1"
R_BIGSUB = "agent taught"
R_LINES  = [
    ("nm", "One writes it. A reviewer that did not write it"),
    ("sb", "grades and signs it. The other 499 inherit it"),
    ("sb", "already approved, and the signature travels"),
    ("sb", "with it \u2014 who trusted it, when, on what basis."),
]
FOOT = ("Same five hundred agents. Same correction. The difference is whether the "
        "company keeps it.")
ZONE_L = "WITHOUT A SHARED GATE"
ZONE_R = "WITH DOUBLEGATE"


def build(Wd):
    _, lpos = field(LX, COLS, ROWS, SEED)
    _, rpos = field(RX, COLS, ROWS, SEED + 1)
    field_bot = FIELD_TOP + CELL_H * ROWS

    o = []

    # ── the seam. One stroke, vertical, in a gutter that holds no text. It is
    #    the only line in the upper half, so there is nothing for it to cross.
    o.append(f'<path d="M {LX+COLW+GUT/2:g} 96 L {LX+COLW+GUT/2:g} {field_bot+34:g}" '
             f'stroke="url(#seam)" stroke-width="1.4" fill="none"/>')

    # ── zone labels
    o.append(f'<text class="zn" x="{LX}" y="52" fill="#fb7185" fill-opacity=".75">{ZONE_L}</text>')
    o.append(f'<text class="zn" x="{RX}" y="52" fill="#22d3ee" fill-opacity=".8">{ZONE_R}</text>')

    # ── the counters. This is the whole argument in two numerals: 500 against 1.
    o.append(f'<text class="big" x="{LX}" y="98" fill="url(#fAlone)">{L_BIG}</text>')
    o.append(f'<text class="tiny" x="{LX + Wd[L_BIG] + 10:g}" y="98" fill="#fb7185" '
             f'fill-opacity=".8">{L_BIGSUB}</text>')
    o.append(f'<text class="hd" x="{LX}" y="124">{L_HEAD}</text>')

    o.append(f'<text class="big" x="{RX}" y="98" fill="url(#fShared)" filter="url(#soft)">{R_BIG}</text>')
    o.append(f'<text class="tiny" x="{RX + Wd[R_BIG] + 10:g}" y="98" fill="#22d3ee" '
             f'fill-opacity=".85">{R_BIGSUB}</text>')
    o.append(f'<text class="hd" x="{RX}" y="124">{R_HEAD}</text>')

    # ── LEFT FIELD: every dot lit its own colour, none connected to any other.
    #    Each is a separate purchase of the same lesson. The visual fact that
    #    there are no lines here IS the point: nothing is shared.
    o.append('<!-- 500 agents, each taught separately. No connectors, by argument:\n'
             '     nothing passes between them, which is the problem being shown. -->')
    o.append('<g fill="url(#fAlone)">')
    for cx, cy in lpos:
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R}"/>')
    o.append("</g>")

    # ── RIGHT FIELD: one dot is the author (bright, ringed); the rest inherit.
    #    Drawn dimmer and filled, so the eye reads "same population, one source".
    # The author sits on the field's BOTTOM-left corner. Mid-grid it was
    # unfindable at r=3.6 among 500 identical dots -- and if the numeral beside
    # this field says "1", this dot IS the subject and must read first. Top-left
    # was the obvious corner but it sits directly under the column heading, so
    # any label there collides with it (svg-geometry.js measured 5px of overlap
    # and svg-clearance.js caught the leader 1px off the same heading). The band
    # below the field is clear for 34px, so the label goes there instead.
    author = (ROWS - 1) * COLS
    o.append('<!-- the same 500. One is the author; the rest inherit what it wrote,\n'
             '     already signed. Again no connectors: inheritance is a state, not\n'
             '     a journey, and the journey is what how-it-works.html draws. -->')
    o.append('<g fill="url(#fShared)" fill-opacity=".46">')
    for i, (cx, cy) in enumerate(rpos):
        if i == author:
            continue
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R}"/>')
    o.append("</g>")
    acx, acy = rpos[author]
    AR = DOT_R + 2.2                      # materially larger than an inheritor
    o.append(f'<circle class="mover" cx="{acx:.1f}" cy="{acy:.1f}" r="{AR:g}" '
             f'fill="none" stroke="#34d399" stroke-width="1.6">'
             f'<animate attributeName="r" dur="4s" repeatCount="indefinite" '
             f'values="{AR:g};{AR+9:g};{AR:g}" keyTimes="0;0.5;1"/>'
             f'<animate attributeName="stroke-opacity" dur="4s" repeatCount="indefinite" '
             f'values=".9;0;.9" keyTimes="0;0.5;1"/></circle>')
    o.append(f'<circle cx="{acx:.1f}" cy="{acy:.1f}" r="{AR:g}" fill="#34d399" '
             f'filter="url(#soft)"/>')
    # The label goes in the clear band ABOVE the field, never inside it. Placed
    # beside the dot it sat on top of 14 inheritors -- measured, after a first
    # collision detector wrongly reported zero. One short vertical leader connects
    # them; it is the only connector in the body of the figure.
    lab_y = field_bot + 17
    o.append(f'<path d="M {acx:.1f} {acy + AR + 2:.1f} L {acx:.1f} {lab_y - 11:.1f}" '
             f'stroke="#34d399" stroke-opacity=".5" stroke-width="1.3" fill="none"/>')
    o.append(f'<text class="nm" x="{acx:.1f}" y="{lab_y:.1f}" fill="#6ee7b7">'
             f'this one writes it</text>')

    # ── prose columns, each under its own field, inside its own column width
    y = field_bot + 34
    for cls, line in L_LINES:
        o.append(f'<text class="{cls}" x="{LX}" y="{y}">{line}</text>')
        y += 19
    y2 = field_bot + 34
    for cls, line in R_LINES:
        o.append(f'<text class="{cls}" x="{RX}" y="{y2}">{line}</text>')
        y2 += 19

    base = max(y, y2) + 16
    o.append(f'<line x1="{PAD}" y1="{base:g}" x2="{W-PAD}" y2="{base:g}" '
             f'stroke="#1b212c" stroke-width="1"/>')
    o.append(f'<text x="{W/2:g}" y="{base+30:g}" text-anchor="middle" font-size="14.5" '
             f'font-weight="600" fill="#e6e9ef">{FOOT}</text>')

    height = int(base + 54)
    desc = ("Two fields of five hundred dots each, one dot per AI agent. On the left, "
            "without a shared gate, every dot is lit separately: each agent is taught "
            "the same lesson on its own, five hundred lessons bought for one lesson "
            "learned, with no record of who decided what. On the right, with "
            "doublegate, a single bright agent writes the lesson, a reviewer that did "
            "not write it grades and signs it, and every remaining agent inherits it "
            "already approved with the signature travelling with it: one lesson, "
            "signed. The same five hundred agents and the same correction in both "
            "halves; the difference is whether the company keeps it.")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}"
     role="img" aria-labelledby="t d" font-family="{FONT}">
<title id="t">Five hundred agents taught separately, against one signed lesson inherited by all</title>
<desc id="d">{desc}</desc>
<defs>
  <style><![CDATA[
{STYLE}
  ]]></style>
{DEFS}
</defs>
<rect width="{W}" height="{height}" fill="#08090c"/>
{chr(10).join(o)}
</svg>
"""


def main():
    Wd = measure([("big", L_BIG), ("big", R_BIG), ("hd", L_HEAD), ("hd", R_HEAD),
                  ("tiny", L_BIGSUB), ("tiny", R_BIGSUB),
                  *L_LINES, *R_LINES, ("nm", FOOT),
                  ("zn", ZONE_L), ("zn", ZONE_R), ("tiny", "one agent writes it")])

    # every prose line must fit its own column, or the two halves collide
    overflow = [(t, Wd[t]) for _, t in L_LINES + R_LINES if Wd[t] > COLW]
    if overflow:
        for t, w in overflow:
            print(f"  OVERFLOW {w:.0f}px > column {COLW:.0f}px: {t}")
        raise SystemExit("prose does not fit its column -- shorten it, do not widen the canvas")

    svg = build(Wd)
    OUT.write_text(svg)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(svg)} bytes, {TOTAL} agents per side, "
          f"column {COLW:.0f}px)")


if __name__ == "__main__":
    main()
