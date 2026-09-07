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

So this draws the five hundred, in three states. Siloed: every agent taught
separately, the same lesson bought over and over. Pooled: taught once and
inherited by all -- which is what every memory provider already sells, and the
panel shows what comes with it, because a write that is readable immediately
spreads a wrong memory exactly as fast as a right one. Gated: taught once,
reviewed by someone who did not write it, signed, and only then inherited.

The middle panel is the point of the figure. Without it the argument is "pool your
knowledge", which needs no product. With it the argument is the site's own: the
risk of pooling is what doublegate removes, and removing it is what makes the
knowledge worth collecting.

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
# THREE panels, not two. Two panels argued for pooling, and pooling is what every
# memory provider already sells -- a reader who knows the category saw panel 2
# ("one writes, everyone inherits") and thought "so, mem0". The figure has to earn
# the product, which means showing the naive fix failing. The middle panel is the
# objection the site's own copy raises and answers: "one wrong memory would reach
# everyone, and nobody could say who vouched for it."
W = 1080
PAD = 24
GUT = 40
NPANEL = 3
COLW = (W - 2 * PAD - GUT * (NPANEL - 1)) / NPANEL
PX = [PAD + (COLW + GUT) * i for i in range(NPANEL)]
LX, MX, RX = PX             # siloed, pooled, gated

# ── the population ──────────────────────────────────────────────────────────
# 500 agents, drawn as a 25x20 field. Not "about five hundred": exactly the
# number the headline says, because a reader who counts the columns and finds
# 500 has just verified the claim themselves.
# 20x25 in a 317px column instead of 25x20 in a 488px one: still exactly 500, and
# still countable. Not "about five hundred" -- a reader who counts a row and a
# column has verified the headline's number themselves.
COLS, ROWS = 20, 25
TOTAL = COLS * ROWS
assert TOTAL == 500, TOTAL

DOT_R = 2.9
FIELD_TOP = 150

# In the pooled panel the wrong memory travels at the speed of the right one --
# that is the whole objection. A share of the field carries it, seeded so the
# spread is identical every run. 1 in 7 is illustrative of contagion, not a
# measured rate, and the caption says "the mistake too" rather than a number, so
# the picture never asserts a statistic the evidence page cannot support.
TAINT_EVERY = 7
CELL_W = COLW / COLS
# 8.6 not 7.4: at 25 rows in a 317px column the dots merged into vertical stripes
# and the field read as 20 bars rather than 500 individuals, which is the whole
# unit of the argument.
CELL_H = 8.6
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

# Panel 1 is SLATE, not red. Nothing is wrong in the siloed panel -- its cost is
# waste and isolation, not error -- and using red there while panel 2 uses red for
# "carrying the wrong memory" gave one colour two meanings side by side. Red now
# appears exactly once, where the argument needs alarm, which also makes its
# ABSENCE in panel 3 legible as "the red is gone".
DEFS = """  <linearGradient id="fAlone" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#94a3b8" stop-opacity=".72"/>
    <stop offset="1" stop-color="#64748b" stop-opacity=".38"/>
  </linearGradient>
  <linearGradient id="fPool" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fbbf24" stop-opacity=".8"/>
    <stop offset="1" stop-color="#fbbf24" stop-opacity=".42"/>
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


# ── copy: three panels, one argument ────────────────────────────────────────
# Each panel is (zone, numeral, unit, head, prose lines). The numeral counts LIT
# dots in that panel, so every number is verifiable by looking -- the first draft
# paired a 500 meaning "lessons bought" with 500 dots meaning "agents", and the
# unit only resolved from the footer.
PANELS = [
    dict(
        key="silo", x=None, zone="SILOED \u2014 TODAY", zc="#94a3b8",
        big="500", unit="taught separately", head="Every correction stops",
        head2="where it was made.",
        lines=[("sb", "The next engineer hits the"),
               ("sb", "same wall and pays again."),
               ("sb", "No record of who decided"),
               ("sb", "what, or on what basis.")],
    ),
    dict(
        key="pool", x=None, zone="POOLED \u2014 MEMORY TOOLS", zc="#fbbf24",
        big="1", unit="taught, 499 inherit", head="One writes, all read",
        head2="\u2014 the mistake too.",
        lines=[("sb", "Across fourteen providers a"),
               ("sb", "write is readable at once."),
               ("sb", "Scores change ranking,"),
               ("sb", "never visibility.")],
    ),
    dict(
        key="gate", x=None, zone="GATED \u2014 DOUBLEGATE", zc="#22d3ee",
        big="1", unit="taught, 499 inherit", head="Reviewed first, then",
        head2="inherited by all.",
        lines=[("sb", "A reviewer that did not write"),
               ("sb", "it grades and signs it."),
               ("sb", "Nothing unsigned is ever"),
               ("sb", "readable by anyone.")],
    ),
]
for _p, _x in zip(PANELS, PX):
    _p["x"] = _x

FOOT3 = ("Same five hundred agents, same correction. Pooling moves it faster; the gate "
         "decides whether what moves is worth having.")


# ── legacy two-panel copy, kept for reference ───────────────────────────────
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
    field_bot = FIELD_TOP + CELL_H * ROWS
    o = []

    # ── two seams, in gutters that hold no text. The only strokes in the upper
    #    half, so there is nothing for them to cross.
    for gx in (PX[1] - GUT / 2, PX[2] - GUT / 2):
        o.append(f'<path d="M {gx:g} 96 L {gx:g} {field_bot + 30:g}" '
                 f'stroke="url(#seam)" stroke-width="1.4" fill="none"/>')

    author_label = None

    for p in PANELS:
        x0 = p["x"]
        _, pos = field(x0, COLS, ROWS, SEED + PANELS.index(p))

        # zone, numeral, unit, heading
        o.append(f'<text class="zn" x="{x0}" y="52" fill="{p["zc"]}" '
                 f'fill-opacity=".8">{p["zone"]}</text>')
        grad = {"silo": "fAlone", "pool": "fPool", "gate": "fShared"}[p["key"]]
        soft = ' filter="url(#soft)"' if p["key"] == "gate" else ""
        o.append(f'<text class="big" x="{x0}" y="98" fill="url(#{grad})"{soft}>{p["big"]}</text>')
        o.append(f'<text class="tiny" x="{x0 + Wd[p["big"]] + 9:g}" y="98" fill="{p["zc"]}" '
                 f'fill-opacity=".85">{p["unit"]}</text>')
        # 18px of leading, not 16: at 15px type the ascender of the second line
        # met the descender of the first and svg-geometry.js measured 2px of
        # overlap on all three panels at once.
        o.append(f'<text class="hd" x="{x0}" y="122">{p["head"]}</text>')
        o.append(f'<text class="hd" x="{x0}" y="140">{p["head2"]}</text>')

        # ── the field itself. No connectors anywhere: what each panel shows is a
        #    STATE of the population, and colour carries it.
        if p["key"] == "silo":
            # every dot lit on its own. The absence of any shared marking IS the
            # problem being shown: 500 separate purchases of one lesson.
            o.append('<g fill="url(#fAlone)">')
            for cx, cy in pos:
                o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R}"/>')
            o.append("</g>")

        elif p["key"] == "pool":
            # one author, everyone inherits -- and so does the wrong memory. The
            # tainted share is seeded, and deliberately scattered rather than
            # clustered: a bad memory does not spread by adjacency, it spreads by
            # retrieval, so it surfaces anywhere someone asks the same question.
            o.append('<g fill="url(#fPool)" fill-opacity=".5">')
            for i, (cx, cy) in enumerate(pos):
                if i % TAINT_EVERY == 3:
                    continue
                o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R}"/>')
            o.append("</g>")
            o.append('<g fill="#fb7185" fill-opacity=".92">')
            for i, (cx, cy) in enumerate(pos):
                if i % TAINT_EVERY == 3:
                    o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R + 0.5:g}"/>')
            o.append("</g>")

        else:
            # gated: the same inheritance, with the wrong memory held back. The
            # author is marked because the numeral beside this panel says 1, so
            # that dot is the subject and has to read first.
            author = (ROWS - 1) * COLS
            o.append('<g fill="url(#fShared)" fill-opacity=".5">')
            for i, (cx, cy) in enumerate(pos):
                if i == author:
                    continue
                o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R}"/>')
            o.append("</g>")
            acx, acy = pos[author]
            AR = DOT_R + 2.2
            o.append(f'<circle class="mover" cx="{acx:.1f}" cy="{acy:.1f}" r="{AR:g}" '
                     f'fill="none" stroke="#34d399" stroke-width="1.6">'
                     f'<animate attributeName="r" dur="4s" repeatCount="indefinite" '
                     f'values="{AR:g};{AR + 9:g};{AR:g}" keyTimes="0;0.5;1"/>'
                     f'<animate attributeName="stroke-opacity" dur="4s" '
                     f'repeatCount="indefinite" values=".9;0;.9" keyTimes="0;0.5;1"/></circle>')
            o.append(f'<circle cx="{acx:.1f}" cy="{acy:.1f}" r="{AR:g}" fill="#34d399" '
                     f'filter="url(#soft)"/>')
            author_label = (acx, acy, AR)

        # prose under the field, inside this panel's own column width
        y = field_bot + 34
        for cls, line in p["lines"]:
            o.append(f'<text class="{cls}" x="{x0}" y="{y}">{line}</text>')
            y += 18

    # the author's leader, drawn last so it sits above the field. One short
    # vertical into the clear band below; the only connector in the body.
    acx, acy, AR = author_label
    lab_y = field_bot + 17
    o.append(f'<path d="M {acx:.1f} {acy + AR + 2:.1f} L {acx:.1f} {lab_y - 11:.1f}" '
             f'stroke="#34d399" stroke-opacity=".5" stroke-width="1.3" fill="none"/>')
    o.append(f'<text class="nm" x="{acx:.1f}" y="{lab_y:.1f}" fill="#6ee7b7">'
             f'this one writes it</text>')

    base = field_bot + 34 + 18 * max(len(p["lines"]) for p in PANELS) + 4
    o.append(f'<line x1="{PAD}" y1="{base:g}" x2="{W - PAD}" y2="{base:g}" '
             f'stroke="#1b212c" stroke-width="1"/>')
    o.append(f'<text x="{W / 2:g}" y="{base + 30:g}" text-anchor="middle" '
             f'font-size="14.5" font-weight="600" fill="#e6e9ef">{FOOT3}</text>')

    height = int(base + 54)
    desc = ("Three fields of five hundred dots each, one dot per AI agent, showing the "
            "same population in three states. Siloed, as things are today: every dot "
            "is lit separately, five hundred agents taught the same lesson one at a "
            "time, and no record of who decided what. Pooled, as memory tools do it: "
            "one agent is taught and the other four hundred and ninety-nine inherit "
            "it, but scattered red dots show that the wrong memory travels with the "
            "right one, because across fourteen surveyed providers a write is readable "
            "immediately and confidence scores change ranking rather than visibility. "
            "Gated, with doublegate: the same one-taught, four-hundred-and-ninety-nine-"
            "inherit spread, with one bright agent marked as the one that writes it, a "
            "reviewer that did not write it grading and signing it, and nothing "
            "unsigned readable by anyone, so no red dots remain. Same five hundred "
            "agents and the same correction throughout; pooling moves it faster, and "
            "the gate decides whether what moves is worth having.")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}"
     role="img" aria-labelledby="t d" font-family="{FONT}">
<title id="t">Five hundred agents siloed, pooled, and gated</title>
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
    pairs = [("nm", FOOT3), ("nm", "this one writes it")]
    for p in PANELS:
        pairs += [("big", p["big"]), ("tiny", p["unit"]), ("zn", p["zone"]),
                  ("hd", p["head"]), ("hd", p["head2"]), *p["lines"]]
    Wd = measure(pairs)

    # Every label must fit the panel that holds it, numerals and units included --
    # a numeral plus its unit sit side by side, so their combined width is what has
    # to clear the column, not either one alone.
    bad = []
    for p in PANELS:
        for _, t in p["lines"]:
            if Wd[t] > COLW:
                bad.append((p["key"], t, Wd[t]))
        for t in (p["head"], p["head2"], p["zone"]):
            if Wd[t] > COLW:
                bad.append((p["key"], t, Wd[t]))
        pair_w = Wd[p["big"]] + 9 + Wd[p["unit"]]
        if pair_w > COLW:
            bad.append((p["key"], f'{p["big"]} + {p["unit"]}', pair_w))
    if bad:
        for k, t, w in bad:
            print(f"  OVERFLOW [{k}] {w:.0f}px > column {COLW:.0f}px: {t}")
        raise SystemExit("copy does not fit its panel -- shorten it, do not widen the canvas")

    svg = build(Wd)
    OUT.write_text(svg)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(svg)} bytes, {NPANEL} panels x {TOTAL} "
          f"agents, column {COLW:.0f}px)")


if __name__ == "__main__":
    main()
