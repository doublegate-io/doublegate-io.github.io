#!/usr/bin/env python3
"""Generate hero-flow layout variants from ONE geometry source.

Why this exists
---------------
The shipped figure was patched three times in a row -- reroute a connector away
from a box, then re-centre a callout, then jog the connector to reach it -- and
the patches composed into something absurd: the author fast lane left the
GRADED & SIGNED box, curved right, climbed, ran back left and re-entered the
same box it started from. Each edit was locally correct. The route was wrong
because the LAYOUT was wrong: a single horizontal rail with three different
kinds of branch hanging off it gives a branch nowhere to go but around, and
"around" means curves, and curves collide with labels.

So stop hand-editing paths. Declare the content once, declare a layout
strategy, and let each strategy compute its own coordinates. Then look at them
side by side and pick.

Two rules every variant obeys, because breaking them is what produced the mess:

  1. A branch leaves and enters at a JUNCTION -- the dot under a stage, on the
     stage's centre line. Never at an arbitrary x inside a box.
  2. Connectors are orthogonal. Horizontal, vertical, and a small corner
     radius. No quadratics threading between labels: a diagonal or a long
     curve is exactly what has to dodge text, and dodging text is what looked
     amateur.

Reserved bands keep text out of the way of lines by construction -- a label
never occupies a band a connector uses.

Run:  python3 hero-variants.py           # writes .tmp/variants/*.svg + index.html
"""
from __future__ import annotations

import json
import subprocess
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / ".tmp" / "variants"
CHROME = os.environ.get("CHROME_PATH", "")

FONT = ("ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Inter, sans-serif")

# ── content: the argument, independent of any layout ────────────────────────
STAGES = [
    dict(key="write", accent=None,      grad=None,    st=None,
         nm=["an agent", "writes it"], sb=None),
    dict(key="held",  accent="#fb7185", grad="gHold", st="HELD",
         nm=["a separate store"], sb="no read path to it"),
    dict(key="scan",  accent="#fbbf24", grad="gChk",  st="SCANNED",
         nm=["injection · secrets"], sb="executable payloads"),
    dict(key="sign",  accent="#34d399", grad="gOk",   st="GRADED & SIGNED",
         nm=["by a reviewer who", "did not write it"], sb=None),
    dict(key="gate2", accent="#a78bfa", grad="gLed",  st="SECOND GATE",
         nm=["reviewed again,"], sb="on its own authority"),
    dict(key="read",  accent="#22d3ee", grad="gCyn",  st="READABLE",
         nm=["company-wide,", "pre-approved"], sb=None),
]

FAST_LINES = ["visible to you straight away",
              "others wait for the signature, you do not"]
REJECT_LINE = ("a failed verdict sends it back to holding, with its reasons"
               " — it can be re-earned")
RECORD_LINES = ["transcripts · tool output · logs — straight through, never held",
                "they record what happened; they do not claim anything is true"]
PUNCHLINE = "All the checking happens on the way in — nothing sits in the read path."

DEFS = """  <linearGradient id="gHold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4c0519" stop-opacity=".6"/><stop offset="1" stop-color="#4c0519" stop-opacity=".15"/>
  </linearGradient>
  <linearGradient id="gChk" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#78350f" stop-opacity=".6"/><stop offset="1" stop-color="#78350f" stop-opacity=".15"/>
  </linearGradient>
  <linearGradient id="gOk" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#064e3b" stop-opacity=".65"/><stop offset="1" stop-color="#064e3b" stop-opacity=".18"/>
  </linearGradient>
  <linearGradient id="gLed" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#4c1d95" stop-opacity=".65"/><stop offset="1" stop-color="#4c1d95" stop-opacity=".18"/>
  </linearGradient>
  <linearGradient id="gCyn" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#0e7490" stop-opacity=".5"/><stop offset="1" stop-color="#0e7490" stop-opacity=".14"/>
  </linearGradient>
  <linearGradient id="rail" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fb7185" stop-opacity=".55"/>
    <stop offset=".3" stop-color="#fbbf24" stop-opacity=".55"/>
    <stop offset=".55" stop-color="#34d399" stop-opacity=".55"/>
    <stop offset=".78" stop-color="#a78bfa" stop-opacity=".55"/>
    <stop offset="1" stop-color="#22d3ee" stop-opacity=".55"/>
  </linearGradient>
  <linearGradient id="railV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fb7185" stop-opacity=".55"/>
    <stop offset=".3" stop-color="#fbbf24" stop-opacity=".55"/>
    <stop offset=".55" stop-color="#34d399" stop-opacity=".55"/>
    <stop offset=".78" stop-color="#a78bfa" stop-opacity=".55"/>
    <stop offset="1" stop-color="#22d3ee" stop-opacity=".55"/>
  </linearGradient>
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="4.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>"""

STYLE = """    .zn   { font-size:11.5px; font-weight:700; letter-spacing:.1em; fill:#8d97a9; }
    .st   { font-size:12px; font-weight:700; letter-spacing:.07em; }
    .nm   { font-size:14px; font-weight:600; fill:#e6e9ef; }
    .sb   { font-size:12.5px; fill:#97a1b2; }
    .panel{ fill:#0e1118; stroke:#1e2430; stroke-width:1.4; }
    @media (prefers-reduced-motion: reduce) { .mover { display: none; } }"""


# ── text measurement: real rendered widths, never estimated ─────────────────
def measure(strings: list[str]) -> dict[str, float]:
    """Rendered width of each string at the class it will actually use."""
    if not CHROME:
        raise SystemExit("set CHROME_PATH")
    tmp = ROOT / ".tmp" / "_m.svg"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    y = 20
    for cls, txt in strings:
        rows.append(f'<text class="{cls}" x="10" y="{y}">'
                    f'{txt.replace("&", "&amp;")}</text>')
        y += 24
    tmp.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{y+20}" '
        f'font-family="{FONT}"><style>{STYLE}</style>' + "\n".join(rows) + "</svg>")
    js = ROOT / ".tmp" / "_m.js"
    js.write_text("""
const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME_PATH,args:['--no-sandbox']});
const p=await b.newPage();await p.goto('file://'+process.argv[2]);
const o=await p.evaluate(()=>{const r={};document.querySelectorAll('text')
.forEach(t=>r[t.textContent]=+t.getBBox().width.toFixed(1));return r;});
console.log(JSON.stringify(o));await b.close();})();""")
    r = subprocess.run(["node", str(js), str(tmp)], cwd=ROOT,
                       capture_output=True, text=True,
                       env={**os.environ, "CHROME_PATH": CHROME})
    if r.returncode:
        raise SystemExit(r.stderr[-500:])
    return json.loads(r.stdout)


def stage_strings():
    out = []
    for s in STAGES:
        if s["st"]:
            out.append(("st", s["st"]))
        for n in s["nm"]:
            out.append(("nm", n))
        if s["sb"]:
            out.append(("sb", s["sb"]))
    for f in FAST_LINES:
        out.append(("nm" if f is FAST_LINES[0] else "sb", f))
    out.append(("sb", REJECT_LINE))
    out.append(("nm", RECORD_LINES[0]))
    out.append(("sb", RECORD_LINES[1]))
    return out


def widest(s, W, pad):
    strings = ([s["st"]] if s["st"] else []) + s["nm"] + ([s["sb"]] if s["sb"] else [])
    return max(W[t] for t in strings) + 2 * pad


# ── drawing primitives shared by every variant ──────────────────────────────
def elbow(x1, y1, x2, y2, r=10, first="v"):
    """Orthogonal 2-segment connector with a rounded corner.

    No diagonals and no long quadratics: those are the shapes that have to
    weave between labels, and weaving is what read as unprofessional. `first`
    picks which axis moves before the corner.
    """
    if abs(x1 - x2) < 0.5:
        return f"M {x1:g} {y1:g} L {x2:g} {y2:g}"
    if abs(y1 - y2) < 0.5:
        return f"M {x1:g} {y1:g} L {x2:g} {y2:g}"
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    if first == "v":
        return (f"M {x1:g} {y1:g} L {x1:g} {y2 - sy*r:g} "
                f"Q {x1:g} {y2:g} {x1 + sx*r:g} {y2:g} L {x2:g} {y2:g}")
    return (f"M {x1:g} {y1:g} L {x2 - sx*r:g} {y1:g} "
            f"Q {x2:g} {y1:g} {x2:g} {y1 + sy*r:g} L {x2:g} {y2:g}")


def bracket(x1, x2, y_from, y_to, r=10):
    """A -| |- return path: down/up out of one point, across, back into another.
    Three straight runs and two corners. This is how a rejection loop should
    look -- the old one used two quadratics and visibly wobbled."""
    sy = 1 if y_to > y_from else -1
    return (f"M {x1:g} {y_from:g} L {x1:g} {y_to - sy*r:g} "
            f"Q {x1:g} {y_to:g} {x1 - r:g} {y_to:g} "
            f"L {x2 + r:g} {y_to:g} "
            f"Q {x2:g} {y_to:g} {x2:g} {y_to - sy*r:g} L {x2:g} {y_from:g}")


def box_svg(s, x, y, w, h, cx):
    tall = s["key"] == "sign"
    o = []
    if s["grad"]:
        o.append(f'  <rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
                 f'rx="{14 if tall else 13}" fill="url(#{s["grad"]})" '
                 f'stroke="{s["accent"]}" stroke-width="{2 if tall else 1.6}"'
                 + (' filter="url(#glow)"' if tall else '') + '/>')
    else:
        o.append(f'  <rect class="panel" x="{x:g}" y="{y:g}" width="{w:g}" '
                 f'height="{h:g}" rx="12"/>')
    ty = y + 26
    if s["st"]:
        o.append(f'  <text class="st" x="{cx:g}" y="{ty:g}" text-anchor="middle" '
                 f'fill="{s["accent"]}">{s["st"].replace("&", "&amp;")}</text>')
        ty += 22
    for n in s["nm"]:
        o.append(f'  <text class="nm" x="{cx:g}" y="{ty:g}" text-anchor="middle">{n}</text>')
        ty += 18
    if s["sb"]:
        o.append(f'  <text class="sb" x="{cx:g}" y="{y+h-12:g}" text-anchor="middle">{s["sb"]}</text>')
    return "\n".join(o)


def dot(cx, cy, s, r=None, junction=True):
    col = s["accent"] or "#8d97a9"
    fill = "#08090c" if s["accent"] else "#0e1118"
    rr = r or (5 if s["key"] == "sign" else (4 if not s["accent"] else 4.5))
    sw = 2.2 if s["key"] == "sign" else (1.5 if not s["accent"] else 2)
    return (f'  <circle cx="{cx:g}" cy="{cy:g}" r="{rr}" fill="{fill}" '
            f'stroke="{col}" stroke-width="{sw}"/>')


def wrap(body, w, h, extra_defs="", movers=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"
     role="img" aria-labelledby="t d" font-family="{FONT}">
<title id="t">How knowledge moves through doublegate</title>
<desc id="d">An agent writes a claim. It is held in a separate store nothing can read, scanned for
injection and secrets, graded and signed by a reviewer that did not write it, reviewed again by a
second gate on its own authority, and only then readable company-wide. Once signed it is visible to
the author's own agents immediately, while others wait for that signature. Rejected content returns
to holding with its reasons. Records such as transcripts and logs bypass review entirely.</desc>
<defs>
  <style><![CDATA[
{STYLE}
  ]]></style>
{DEFS}
{extra_defs}
</defs>
<rect width="{w}" height="{h}" fill="#08090c"/>
{body}
{movers}
</svg>
"""


def mover_rail(railL, railR, RAIL, sg, hg, geo, RY, REJ_Y, CALL_Y):
    """Animation block shared by the variants. Every track is a line-only band."""
    out = ['<!-- dots ride the rail; every track is a line-only band -->']
    for begin in ["", ' begin="2.7s"', ' begin="5.4s"']:
        out.append(f"""<g class="mover" fill="#fb7185"><circle r="5.5">
  <animateMotion dur="8s"{begin} repeatCount="indefinite" calcMode="linear"><mpath href="#mRail"/></animateMotion>
  <animate attributeName="fill" dur="8s"{begin} repeatCount="indefinite"
    values="#8d97a9;#fb7185;#fbbf24;#34d399;#a78bfa;#22d3ee;#22d3ee"
    keyTimes="0;0.15;0.32;0.5;0.68;0.88;1"/>
  <animate attributeName="opacity" dur="8s"{begin} repeatCount="indefinite" values="0;1;1;1;0" keyTimes="0;0.04;0.5;0.94;1"/>
  <animate attributeName="r" dur="8s"{begin} repeatCount="indefinite" values="5.5;5.5;7;5.5;5.5" keyTimes="0;0.46;0.5;0.56;1"/>
</circle></g>""")
    out.append("""<g class="mover" fill="#34d399"><circle r="4.5">
  <animateMotion dur="8s" begin="4.1s" repeatCount="indefinite" calcMode="linear"><mpath href="#mMine"/></animateMotion>
  <animate attributeName="opacity" dur="8s" begin="4.1s" repeatCount="indefinite" values="0;1;1;0;0" keyTimes="0;0.06;0.3;0.42;1"/>
</circle></g>""")
    out.append("""<g class="mover" fill="#fb7185"><circle r="4.5">
  <animateMotion dur="16s" begin="3.6s" repeatCount="indefinite" calcMode="linear"><mpath href="#mRej"/></animateMotion>
  <animate attributeName="opacity" dur="16s" begin="3.6s" repeatCount="indefinite" values="0;1;1;0;0" keyTimes="0;0.02;0.2;0.27;1"/>
</circle></g>""")
    for begin in ["", ' begin="1.5s"', ' begin="2.9s"']:
        out.append(f"""<g class="mover" fill="#60a5fa"><circle r="4">
  <animateMotion dur="4.4s"{begin} repeatCount="indefinite" calcMode="linear"><mpath href="#mRec"/></animateMotion>
  <animate attributeName="opacity" dur="4.4s"{begin} repeatCount="indefinite" values="0;1;1;0" keyTimes="0;0.05;0.9;1"/>
</circle></g>""")
    out.append(f"""<rect class="mover" x="{sg['x']:g}" y="{sg['y']:g}" width="{sg['w']:g}" height="{sg['h']:g}" rx="14" fill="none" stroke="#34d399" stroke-width="2">
  <animate attributeName="stroke-opacity" dur="8s" repeatCount="indefinite" values="0;0;.85;0;0" keyTimes="0;0.44;0.5;0.6;1"/>
  <animate attributeName="stroke-width" dur="8s" repeatCount="indefinite" values="2;2;4.5;2;2" keyTimes="0;0.44;0.5;0.6;1"/>
</rect>""")
    return "\n".join(out)


def zone(label, x, y):
    return f'<text class="zn" x="{x}" y="{y}">{label}</text>'


def records_band(L, R, RY, railL, railR, caps=True):
    mid = (L + R) / 2
    o = [f'<line x1="{L}" y1="{RY-40}" x2="{R}" y2="{RY-40}" stroke="#1b212c" stroke-width="1"/>',
         zone("RECORDS \u2014 WHAT ACTUALLY HAPPENED", L, RY - 18),
         f'<path d="M {railL:g} {RY:g} L {railR:g} {RY:g}" stroke="#1e3a5f" stroke-width="2" stroke-dasharray="6 5" fill="none"/>']
    if caps:
        o.append(f'<circle cx="{railL-14:g}" cy="{RY:g}" r="4" fill="#0e1118" stroke="#60a5fa" stroke-width="1.5"/>')
        o.append(f'<circle cx="{railR+14:g}" cy="{RY:g}" r="4" fill="#0e1118" stroke="#60a5fa" stroke-width="1.5"/>')
    o.append(f'<text class="nm" x="{mid:g}" y="{RY+24:g}" text-anchor="middle" fill="#93c5fd">{RECORD_LINES[0]}</text>')
    o.append(f'<text class="sb" x="{mid:g}" y="{RY+42:g}" text-anchor="middle">{RECORD_LINES[1]}</text>')
    o.append(f'<text x="{mid:g}" y="{RY+70:g}" text-anchor="middle" font-size="14.5" font-weight="600" fill="#e6e9ef">{PUNCHLINE}</text>')
    return o


def row_widths(W, pad, gap, L, R):
    """Content-derived widths, leftover slack spread evenly so the row spans L..R."""
    ws = [round(widest(s, W, pad)) for s in STAGES]
    slack = (R - L) - (sum(ws) + gap * (len(ws) - 1))
    if slack < 0:
        raise SystemExit(f"row overflows by {-slack}px at gap={gap}")
    add = slack // len(ws)
    ws = [w + add + (1 if i < slack - add * len(ws) else 0) for i, w in enumerate(ws)]
    xs, x = [], L
    for w in ws:
        xs.append(x)
        x += w + gap
    return xs, ws


# ============================================================================
#  VARIANT A - "banded rail"
#  Keeps the horizontal rail but gives every branch its OWN reserved band, and
#  both branches leave from a real junction. The fast lane is a single straight
#  vertical up from the signing junction; the rejection is a bracket below the
#  rail. Neither passes a label, because the bands they use contain no text.
# ============================================================================
def variant_banded(W):
    PAD, GAP, L, R = 13, 24, 24, 1056
    CALL_Y, BOX_TOP, RAIL, REJ_Y, CAP_Y = 58, 128, 240, 270, 294
    xs, ws = row_widths(W, PAD, GAP, L, R)
    geo = {}
    for s, x0, w in zip(STAGES, xs, ws):
        h = 88 if s["key"] == "sign" else (62 if s["key"] == "write" else 78)
        geo[s["key"]] = dict(x=x0, w=w, y=BOX_TOP + (88 - h), h=h,
                             cx=x0 + w / 2, bot=BOX_TOP + 88)
    o = [zone("CLAIMS \u2014 WHAT THE AGENT ASSERTS AS TRUE", L, 30)]
    railL, railR = geo["write"]["cx"], geo["read"]["cx"]
    o.append(f'<path d="M {railL:g} {RAIL} L {railR:g} {RAIL}" stroke="url(#rail)" stroke-width="2.5" fill="none"/>')
    for s in STAGES:
        g = geo[s["key"]]
        col = s["accent"] or "#8d97a9"
        o.append("<g>")
        o.append(box_svg(s, g["x"], g["y"], g["w"], g["h"], g["cx"]))
        o.append(f'  <line x1="{g["cx"]:g}" y1="{g["y"]+g["h"]:g}" x2="{g["cx"]:g}" y2="{RAIL}" '
                 f'stroke="{"#232b39" if not s["accent"] else col+"66"}" stroke-width="1.5"/>')
        o.append(dot(g["cx"], RAIL, s))
        o.append("</g>")

    sg, hg = geo["sign"], geo["held"]
    cw = round(max(W[f] for f in FAST_LINES) + 2 * PAD)
    # The fast lane cannot climb the signing box's own centre line: the box is
    # directly above the junction, so a straight vertical spends its whole length
    # inside it (measured: 63.6%). Leave from the box's TOP edge instead of the
    # rail junction -- same centre line, still one straight vertical, but it starts
    # where the box ends. The claim being made is about the signing stage, so
    # departing from the stage itself is also the truer reading.
    o.append('<!-- author fast lane: ONE straight vertical from the top edge of the signing\n'
             '     box to its callout, on the box centre line. Nothing to route around, and\n'
             '     no part of it crosses a box interior. -->')
    o.append(f'<path d="M {sg["cx"]:g} {sg["y"]:g} L {sg["cx"]:g} {CALL_Y+50}" stroke="#34d399" '
             f'stroke-opacity=".5" stroke-width="1.6" stroke-dasharray="4 4" fill="none"/>')
    o.append(f'<g>\n  <rect class="panel" x="{round(sg["cx"]-cw/2)}" y="{CALL_Y}" width="{cw}" '
             f'height="46" rx="11" stroke="#34d399" stroke-opacity=".45"/>')
    o.append(f'  <text class="nm" x="{sg["cx"]:g}" y="{CALL_Y+20}" text-anchor="middle">{FAST_LINES[0]}</text>')
    o.append(f'  <text class="sb" x="{sg["cx"]:g}" y="{CALL_Y+37}" text-anchor="middle">{FAST_LINES[1]}</text>\n</g>')

    o.append('<!-- rejection: junction to junction, three straight runs, own band -->')
    o.append(f'<path d="{bracket(sg["cx"], hg["cx"], RAIL, REJ_Y)}" stroke="#fb7185" '
             f'stroke-opacity=".45" stroke-width="1.6" stroke-dasharray="4 4" fill="none"/>')
    o.append(f'<text class="sb" x="{L}" y="{CAP_Y}" fill="#fb7185" fill-opacity=".85">{REJECT_LINE}</text>')

    RY = 352
    o += records_band(L, R, RY, railL, railR)
    defs = (f'  <path id="mRail" d="M {railL:g} {RAIL} L {railR:g} {RAIL}" fill="none"/>\n'
            f'  <path id="mMine" d="M {sg["cx"]:g} {sg["y"]:g} L {sg["cx"]:g} {CALL_Y+50}" fill="none"/>\n'
            f'  <path id="mRej" d="{bracket(sg["cx"], hg["cx"], RAIL, REJ_Y)}" fill="none"/>\n'
            f'  <path id="mRec" d="M {railL:g} {RY} L {railR:g} {RY}" fill="none"/>')
    return wrap("\n".join(o), 1080, RY + 84, defs,
                mover_rail(railL, railR, RAIL, sg, hg, geo, RY, REJ_Y, CALL_Y))


# ============================================================================
#  VARIANT B - "two columns, gutter"
#  Stages run DOWN the left; branches and captions live in the right gutter. A
#  vertical spine makes every branch naturally HORIZONTAL, so the fast lane is
#  a single straight run with no elbow at all. It also kills the width problem:
#  long copy has the whole gutter, so nothing gets shortened to fit a box.
# ============================================================================
def variant_columns(W):
    PAD, LEFT, SPINE, GUT, R = 13, 68, 300, 340, 1056
    TOP, VGAP = 58, 20
    boxw = max(round(widest(s, W, PAD)) for s in STAGES)
    geo, y = {}, TOP
    for s in STAGES:
        n = (1 if s["st"] else 0) + len(s["nm"]) + (1 if s["sb"] else 0)
        h = 28 + n * 19
        geo[s["key"]] = dict(x=LEFT, y=y, w=boxw, h=h, cx=LEFT + boxw / 2, cy=y + h / 2)
        y += h + VGAP
    bottom = y - VGAP
    o = [zone("CLAIMS \u2014 WHAT THE AGENT ASSERTS AS TRUE", 24, 30)]
    o.append(f'<path d="M {SPINE} {TOP+14} L {SPINE} {bottom-14}" stroke="url(#railV)" stroke-width="2.5" fill="none"/>')
    for s in STAGES:
        g = geo[s["key"]]
        col = s["accent"] or "#8d97a9"
        o.append("<g>")
        o.append(box_svg(s, g["x"], g["y"], g["w"], g["h"], g["cx"]))
        o.append(f'  <line x1="{g["x"]+g["w"]:g}" y1="{g["cy"]:g}" x2="{SPINE}" y2="{g["cy"]:g}" '
                 f'stroke="{"#232b39" if not s["accent"] else col+"66"}" stroke-width="1.5"/>')
        o.append(dot(SPINE, g["cy"], s))
        o.append("</g>")

    sg, hg = geo["sign"], geo["held"]
    cw = round(max(W[f] for f in FAST_LINES) + 2 * PAD)
    o.append('<!-- fast lane: one horizontal run into the gutter. A vertical spine means a\n'
             '     branch is already perpendicular to the flow, so no elbow is needed. -->')
    o.append(f'<path d="M {SPINE} {sg["cy"]:g} L {GUT} {sg["cy"]:g}" stroke="#34d399" '
             f'stroke-opacity=".5" stroke-width="1.6" stroke-dasharray="4 4" fill="none"/>')
    o.append(f'<g>\n  <rect class="panel" x="{GUT}" y="{sg["cy"]-24:g}" width="{cw}" height="48" '
             f'rx="11" stroke="#34d399" stroke-opacity=".45"/>')
    o.append(f'  <text class="nm" x="{GUT+cw/2:g}" y="{sg["cy"]-3:g}" text-anchor="middle">{FAST_LINES[0]}</text>')
    o.append(f'  <text class="sb" x="{GUT+cw/2:g}" y="{sg["cy"]+15:g}" text-anchor="middle">{FAST_LINES[1]}</text>\n</g>')

    BX = LEFT - 26
    o.append('<!-- rejection: a bracket to the LEFT of the column, junction to junction -->')
    o.append(f'<path d="M {LEFT:g} {sg["cy"]:g} L {BX+10:g} {sg["cy"]:g} '
             f'Q {BX:g} {sg["cy"]:g} {BX:g} {sg["cy"]-10:g} '
             f'L {BX:g} {hg["cy"]+10:g} Q {BX:g} {hg["cy"]:g} {BX+10:g} {hg["cy"]:g} '
             f'L {LEFT:g} {hg["cy"]:g}" stroke="#fb7185" stroke-opacity=".45" '
             f'stroke-width="1.6" stroke-dasharray="4 4" fill="none"/>')
    o.append(f'<text class="sb" x="{GUT}" y="{hg["cy"]+5:g}" fill="#fb7185" fill-opacity=".85">{REJECT_LINE}</text>')

    RY = bottom + 62
    o += records_band(24, R, RY, 24 + 52, R - 52, caps=False)
    defs = (f'  <path id="mRail" d="M {SPINE} {TOP+14} L {SPINE} {bottom-14}" fill="none"/>\n'
            f'  <path id="mMine" d="M {SPINE} {sg["cy"]:g} L {GUT} {sg["cy"]:g}" fill="none"/>\n'
            f'  <path id="mRej" d="M {LEFT:g} {sg["cy"]:g} L {BX:g} {sg["cy"]:g} L {BX:g} {hg["cy"]:g} L {LEFT:g} {hg["cy"]:g}" fill="none"/>\n'
            f'  <path id="mRec" d="M {24+52} {RY} L {R-52} {RY}" fill="none"/>')
    return wrap("\n".join(o), 1080, RY + 84, defs,
                mover_rail(SPINE, SPINE, TOP, sg, hg, geo, RY, 0, 0))


# ============================================================================
#  VARIANT C - "three lanes, no branches"
#  The branch problem disappears if you stop drawing branches. Each outcome is
#  its own lane, all flowing left to right, so the figure has zero return paths
#  and zero verticals crossing anything. Reading order carries what connectors
#  were straining to carry.
# ============================================================================
def variant_lanes(W):
    PAD, GAP, L, R = 13, 24, 24, 1056
    xs, ws = row_widths(W, PAD, GAP, L, R)
    BOX_TOP, RAIL, LANE_A, LANE_R = 88, 200, 248, 296
    geo = {}
    for s, x0, w in zip(STAGES, xs, ws):
        h = 88 if s["key"] == "sign" else (62 if s["key"] == "write" else 78)
        geo[s["key"]] = dict(x=x0, w=w, y=BOX_TOP + (88 - h), h=h,
                             cx=x0 + w / 2, bot=BOX_TOP + 88)
    o = [zone("CLAIMS \u2014 WHAT THE AGENT ASSERTS AS TRUE", L, 30)]
    railL, railR = geo["write"]["cx"], geo["read"]["cx"]
    o.append(f'<path d="M {railL:g} {RAIL} L {railR:g} {RAIL}" stroke="url(#rail)" stroke-width="2.5" fill="none"/>')
    for s in STAGES:
        g = geo[s["key"]]
        col = s["accent"] or "#8d97a9"
        o.append("<g>")
        o.append(box_svg(s, g["x"], g["y"], g["w"], g["h"], g["cx"]))
        o.append(f'  <line x1="{g["cx"]:g}" y1="{g["y"]+g["h"]:g}" x2="{g["cx"]:g}" y2="{RAIL}" '
                 f'stroke="{"#232b39" if not s["accent"] else col+"66"}" stroke-width="1.5"/>')
        o.append(dot(g["cx"], RAIL, s))
        o.append("</g>")

    sg, hg = geo["sign"], geo["held"]
    o.append('<!-- author lane: starts under signing and runs FORWARD. Not a branch off the\n'
             '     rail but a lane of its own, so there is no vertical to route and no label\n'
             '     to dodge. The lane starting late IS the argument. -->')
    o.append(f'<path d="M {sg["cx"]:g} {LANE_A} L {railR:g} {LANE_A}" stroke="#34d399" '
             f'stroke-opacity=".45" stroke-width="1.8" stroke-dasharray="5 4" fill="none"/>')
    o.append(f'<circle cx="{sg["cx"]:g}" cy="{LANE_A}" r="4" fill="#08090c" stroke="#34d399" stroke-width="2"/>')
    # Captions are centred on the LANE they describe, not left-anchored at its start:
    # a left-anchored caption on a lane that begins two thirds of the way across runs
    # off the canvas (svg-bounds.js caught exactly that).
    amid = (sg["cx"] + railR) / 2
    o.append(f'<text class="nm" x="{amid:g}" y="{LANE_A-11}" text-anchor="middle" fill="#6ee7b7">{FAST_LINES[0]}</text>')
    o.append(f'<text class="sb" x="{amid:g}" y="{LANE_A+19}" text-anchor="middle">{FAST_LINES[1]}</text>')

    o.append('<!-- rejection lane: right to left in its own row, so a return reads as a return -->')
    o.append(f'<path d="M {sg["cx"]:g} {LANE_R} L {hg["cx"]+11:g} {LANE_R}" stroke="#fb7185" '
             f'stroke-opacity=".45" stroke-width="1.8" stroke-dasharray="5 4" fill="none"/>')
    o.append(f'<path d="M {hg["cx"]+11:g} {LANE_R-5} L {hg["cx"]+2:g} {LANE_R} L {hg["cx"]+11:g} {LANE_R+5}" '
             f'stroke="#fb7185" stroke-opacity=".75" stroke-width="1.6" fill="none"/>')
    o.append(f'<text class="sb" x="{(sg["cx"]+hg["cx"])/2:g}" y="{LANE_R+21}" text-anchor="middle" '
             f'fill="#fb7185" fill-opacity=".85">{REJECT_LINE}</text>')

    RY = 358
    o += records_band(L, R, RY, railL, railR)
    defs = (f'  <path id="mRail" d="M {railL:g} {RAIL} L {railR:g} {RAIL}" fill="none"/>\n'
            f'  <path id="mMine" d="M {sg["cx"]:g} {LANE_A} L {railR:g} {LANE_A}" fill="none"/>\n'
            f'  <path id="mRej" d="M {sg["cx"]:g} {LANE_R} L {hg["cx"]+2:g} {LANE_R}" fill="none"/>\n'
            f'  <path id="mRec" d="M {railL:g} {RY} L {railR:g} {RY}" fill="none"/>')
    return wrap("\n".join(o), 1080, RY + 84, defs,
                mover_rail(railL, railR, RAIL, sg, hg, geo, RY, LANE_R, 0))


# ============================================================================
#  VARIANT D - "gated chain, no rail"
#  Drop the rail. Boxes connect directly edge to edge with short arrows: the
#  shortest possible connectors, so none of them can pass near a label. The
#  author note becomes a plain aside above the signing box rather than a
#  balloon on a wire, and the rejection is one full bracket below the row.
# ============================================================================
def variant_chain(W):
    # 40px gaps would overflow by 56px (row_widths says so rather than guessing);
    # 28px is the widest gap this copy affords while still spanning L..R.
    PAD, GAP, L, R = 13, 28, 24, 1056
    xs, ws = row_widths(W, PAD, GAP, L, R)
    TOP = 86
    geo = {}
    for s, x0, w in zip(STAGES, xs, ws):
        n = (1 if s["st"] else 0) + len(s["nm"]) + (1 if s["sb"] else 0)
        geo[s["key"]] = dict(x=x0, w=w, h=28 + n * 19, cx=x0 + w / 2)
    maxh = max(g["h"] for g in geo.values())
    for g in geo.values():
        g["y"] = TOP + (maxh - g["h"]) / 2
        g["cy"] = g["y"] + g["h"] / 2
    MIDY = TOP + maxh / 2
    o = [zone("CLAIMS \u2014 WHAT THE AGENT ASSERTS AS TRUE", L, 30)]
    keys = [s["key"] for s in STAGES]
    for i, s in enumerate(STAGES):
        g = geo[s["key"]]
        o.append("<g>" + box_svg(s, g["x"], g["y"], g["w"], g["h"], g["cx"]) + "</g>")
        if i + 1 < len(keys):
            n = geo[keys[i + 1]]
            col = STAGES[i + 1]["accent"] or "#8d97a9"
            x1, x2 = g["x"] + g["w"] + 5, n["x"] - 5
            o.append(f'<path d="M {x1:g} {MIDY:g} L {x2-5:g} {MIDY:g}" stroke="{col}" '
                     f'stroke-opacity=".6" stroke-width="1.8" fill="none"/>')
            o.append(f'<path d="M {x2-6:g} {MIDY-4.5:g} L {x2:g} {MIDY:g} L {x2-6:g} {MIDY+4.5:g}" '
                     f'stroke="{col}" stroke-opacity=".85" stroke-width="1.6" fill="none"/>')

    sg, rg = geo["sign"], geo["read"]
    o.append('<!-- the author note is an aside, not a balloon on a wire: no connector at all -->')
    o.append(f'<text class="nm" x="{sg["cx"]:g}" y="{TOP-30}" text-anchor="middle" fill="#6ee7b7">{FAST_LINES[0]}</text>')
    o.append(f'<text class="sb" x="{sg["cx"]:g}" y="{TOP-16}" text-anchor="middle">{FAST_LINES[1]}</text>')
    # the stub needs real air under the caption: at TOP-6 it cleared the descenders
    # by 3px, which is the "line standing in the text's way" complaint in miniature
    o.append(f'<path d="M {sg["cx"]:g} {TOP-8} L {sg["cx"]:g} {TOP+(maxh-sg["h"])/2:g}" '
             f'stroke="#34d399" stroke-opacity=".35" stroke-width="1.4" stroke-dasharray="3 4" fill="none"/>')

    REJ_Y = TOP + maxh + 46
    o.append('<!-- one bracket, three straight runs, well clear of every box -->')
    o.append(f'<path d="{bracket(sg["cx"], geo["held"]["cx"], TOP+maxh+2, REJ_Y)}" stroke="#fb7185" '
             f'stroke-opacity=".45" stroke-width="1.6" stroke-dasharray="4 4" fill="none"/>')
    o.append(f'<text class="sb" x="{(sg["cx"]+geo["held"]["cx"])/2:g}" y="{REJ_Y+21}" '
             f'text-anchor="middle" fill="#fb7185" fill-opacity=".85">{REJECT_LINE}</text>')

    RY = REJ_Y + 96
    o += records_band(L, R, RY, L + 52, R - 52, caps=False)
    defs = (f'  <path id="mRail" d="M {geo["write"]["cx"]:g} {MIDY:g} L {rg["cx"]:g} {MIDY:g}" fill="none"/>\n'
            f'  <path id="mMine" d="M {sg["cx"]:g} {TOP-8} L {sg["cx"]:g} {TOP+(maxh-sg["h"])/2:g}" fill="none"/>\n'
            f'  <path id="mRej" d="{bracket(sg["cx"], geo["held"]["cx"], TOP+maxh+2, REJ_Y)}" fill="none"/>\n'
            f'  <path id="mRec" d="M {L+52} {RY} L {R-52} {RY}" fill="none"/>')
    return wrap("\n".join(o), 1080, RY + 84, defs,
                mover_rail(L, R, MIDY, sg, geo["held"], geo, RY, REJ_Y, 0))


VARIANTS = {
    "a-banded":  ("Banded rail: reserved bands, both branches leave from junctions", variant_banded),
    "b-columns": ("Two columns: vertical spine, every branch is horizontal", variant_columns),
    "c-lanes":   ("Three lanes: no branches at all, each outcome gets a row", variant_lanes),
    "d-chain":   ("Gated chain: no rail, boxes connect edge to edge", variant_chain),
}

_CSS = """
  body { margin:0; background:#08090c; color:#e6e9ef; padding:32px 24px 80px; }
  h1 { font-size:20px; margin:0 0 6px; }
  p.note { color:#97a1b2; font-size:13px; max-width:900px; margin:0 0 26px;
           line-height:1.5; }
  h2 { font-size:13.5px; font-weight:600; color:#8d97a9; margin:34px 0 10px; }
  .fig { border:1px solid #1b212c; border-radius:11px; background:#05060a;
         padding:14px; overflow-x:auto; }
  .fig img { display:block; width:1080px; }
"""


def main():
    W = measure(stage_strings())
    OUT.mkdir(parents=True, exist_ok=True)
    cards = []
    for key, (label, fn) in VARIANTS.items():
        (OUT / f"{key}.svg").write_text(fn(W))
        cards.append(f'<section><h2>{key} &mdash; {label}</h2>'
                     f'<div class="fig"><img src="{key}.svg" alt="{label}"></div></section>')
    head = ('<!doctype html><meta charset="utf-8"><title>hero-flow layout variants</title>'
            f'<style>body{{font-family:{FONT};}}{_CSS}</style>')
    note = ('Same content, four layout strategies. Every variant obeys two rules that the '
            'shipped figure broke: a branch leaves and enters at a junction (the dot on a '
            'stage centre line, never an arbitrary point inside a box), and connectors are '
            'orthogonal with rounded corners, never quadratics threading between labels. '
            'Text and lines occupy separate reserved bands.')
    (OUT / "index.html").write_text(
        f'{head}<h1>hero-flow \u2014 layout variants</h1><p class="note">{note}</p>'
        + "".join(cards))
    print(f"wrote {len(VARIANTS)} variants + index.html to {OUT}")


if __name__ == "__main__":
    main()
