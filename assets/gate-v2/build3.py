#!/usr/bin/env python3
"""Round 3 — four known failure classes, and rivals built to dodge all of them.

Run:      python3 assets/gate-v2/build3.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure3.js
Read:     python3 .tmp/ask_open.py --dir3

WHAT TWO ROUNDS AND TWELVE RIVALS ESTABLISHED
---------------------------------------------
Every rival so far collapsed into something already known. Read with a single
open question ("what is it?", no menu, so the answer is unprompted):

  round 1, arch family
    live       "two rounded shapes that look like the letter n"   <- THE SHIPPED MARK
    stack      "a lowercase n or a horseshoe/U-shape"
    numbered   "two n shapes or two arches side by side"
  round 2, arch-free
    turnstile  "a stylized figure - like a person or a character"
    ledgerline "horizontal bars/lines in a stacked, staggered pattern"
    twokeys    "a circle with a small tail, like a question mark or a location pin"

Four failure classes, and they are structural rather than matters of taste:

  A. ROUND TOP + DESCENDING LEGS = lowercase n / u / horseshoe. The live mark's
     case study believed a wide gap defeated this. It did not — it turned one
     letter ("m") into two ("nn"), and nobody re-asked after round 3.
  B. STACKED HORIZONTAL BARS = bar chart, hamburger menu, list.
  C. CIRCLE, especially with any tail = Q, question mark, map pin, at-sign.
  D. NARROW CENTRED VERTICAL STACK = a person / figure icon.

Every rival below is checked against all four before being drawn. That is the
only real progress two rounds bought, and it is worth more than another six
drawings would have been.

STANCE FOR THIS ROUND
---------------------
Stop drawing the door. Draw the ARTIFACT carrying two independent marks, or the
authorising instrument. The gates are what the product does; the artifact is
what the customer has, and an object with two seals on it cannot become an "n",
a bar chart, a circle, or a person.

PALETTE, unchanged from the round-1 decision
  slate = the authority already passed, green = the one that admits,
  amber  = present but not yet admitted.
Red/green is not used: it reads fail/pass, and both gates are legitimate stages
of one passage, not a bad one and a good one. Depth-not-hue also survives
greyscale, which matters in a monochrome tab strip.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

GRN = "#34d399"
SLATE = "#64748b"
AMB = "#fbbf24"
DIM = "#97a1b2"
INK_D, INK_L = "#e6e9ef", "#10131a"
BG_D, BG_L = "#08090c", "#ffffff"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round3")
SANS_ATTR = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"

INK_STYLE = f"""  <style>
    .ink {{ fill: {INK_D}; }}
    .ink-s {{ stroke: {INK_D}; }}
    @media (prefers-color-scheme: light) {{
      .ink {{ fill: {INK_L}; }}
      .ink-s {{ stroke: {INK_L}; }}
    }}
  </style>"""


# ------------------------------------------------------------------ geometry

def g_twoseals(i="  "):
    """A tablet carrying two seals, struck at different depths on its edge.

    Dodges all four: the outer form is a rectangle with a chamfered corner (not
    round-topped, so no n), the seals are lozenges rather than circles (no Q or
    pin), nothing is a horizontal bar stack, and the silhouette is wide rather
    than a narrow centred column (no person).

    Sequence is stated by depth of strike: the slate seal is struck flush into
    the edge (done, absorbed) and the green one still stands proud of it.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M5 4.5 h13 l5.5 5.5 v17.5 h-18.5 z" fill="none" class="ink-s"'
        ' stroke-width="2.4" stroke-linejoin="round"/>',
        f'<path d="M11 16.5 l3.2 3.2 l-3.2 3.2 l-3.2 -3.2 z" fill="{SLATE}"/>',
        f'<path d="M19.5 16.5 l3.6 3.6 l-3.6 3.6 l-3.6 -3.6 z" fill="{GRN}"/>',
    ])


def g_countermark(i="  "):
    """A struck lozenge with a second, independent mark struck across its corner.

    The hallmark reading — an assay punch — but with the countermark breaking the
    first mark's outline, so the two are visibly one event by two hands rather
    than two shapes placed side by side.

    A lozenge is the sharpest available container: diagonal edges throughout, so
    there is no round top (class A), no horizontal run to stack (B), no circle
    (C), and it is wider than tall (D).
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M14 4 l11 11 l-11 11 l-11 -11 z" fill="none" stroke="{SLATE}"'
        ' stroke-width="2.8" stroke-linejoin="round"/>',
        f'<path d="M21 19 l7.5 7.5" stroke="{GRN}" stroke-width="3.4"'
        ' stroke-linecap="round"/>',
        f'<path d="M28.5 19 l-7.5 7.5" stroke="{GRN}" stroke-width="3.4"'
        ' stroke-linecap="round"/>',
    ])


def g_notch(i="  "):
    """A solid block with two notches cut from its edge — gates as negative space.

    The inversion nothing else tried: the gates are absences, not strokes. A
    solid mass with bites taken out of it is a silhouette no alphabet contains,
    and negative space is exactly what survives downscaling.

    Two notches of different depth carry the order — the first is shallow and
    passed, the second cuts deeper.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M4 5 h16 v4.5 h-5 v4 h5 v5 h-5 v4 h5 v4.5 h-16 z" class="ink"/>',
        f'<path d="M24 11 v3" stroke="{SLATE}" stroke-width="3" stroke-linecap="round"/>',
        f'<path d="M24 18.5 v6" stroke="{GRN}" stroke-width="3" stroke-linecap="round"/>',
    ])


def g_relay(i="  "):
    """A hand-off: the artifact leaves one authority's custody and enters another.

    Two short diagonal strokes at different angles, meeting nothing, with the
    artifact between them — a pass, not a door. Diagonals are the one stroke
    direction none of the four failure classes uses: letters here were built from
    verticals and curves, bar charts and menus from horizontals, pins from arcs.

    The strokes deliberately do NOT meet at a vertex, because two strokes meeting
    at a low vertex read as a tick regardless of their directions.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 21 l7 -9" stroke="{SLATE}" stroke-width="3.4"'
        ' stroke-linecap="round"/>',
        f'<path d="M22 20 l7 -9" stroke="{GRN}" stroke-width="3.4"'
        ' stroke-linecap="round"/>',
        f'<rect x="13.5" y="13.5" width="6" height="6" rx="1.4" fill="{AMB}"'
        ' transform="rotate(-12 16.5 16.5)"/>',
        f'<path d="M2.5 27.5 h27" stroke="{DIM}" stroke-width="2.2"'
        ' stroke-linecap="round" opacity="0.85"/>',
    ])


RIVALS = {
    "twoseals": (g_twoseals, "a tablet carrying two seals struck at different depths"),
    "countermark": (g_countermark, "a struck lozenge with a countermark across its corner"),
    "notch": (g_notch, "a solid block with two notches cut out — gates as absence"),
    "relay": (g_relay, "a hand-off between two custodians, artifact in transit"),
}

SIZES = [16, 22, 32, 48, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n{INK_STYLE}\n{geom("  ")}\n</svg>\n')


def wordmark(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 120" width="720"'
            f' height="120" role="img" aria-label="{NAME} — {TAG}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n  <style>\n'
            f'    .wm {{ font-family: {SANS_ATTR}; }}\n'
            f'    .name {{ font-size: 54px; font-weight: 650; letter-spacing: -1.2px;'
            f' fill: {INK_D}; }}\n'
            f'    .tag {{ font-size: 20px; fill: {DIM}; }}\n'
            f'    .ink {{ fill: {INK_D}; }}\n'
            f'    .ink-s {{ stroke: {INK_D}; }}\n'
            '    @media (prefers-color-scheme: light) {\n'
            f'      .name {{ fill: {INK_L}; }}\n'
            '      .tag { fill: #55606f; }\n'
            f'      .ink {{ fill: {INK_L}; }}\n'
            f'      .ink-s {{ stroke: {INK_L}; }}\n'
            '    }\n  </style>\n'
            '  <g transform="translate(14 12) scale(2.0)">\n'
            f'{geom("    ")}\n  </g>\n'
            f'  <text class="wm name" x="112" y="60">{NAME}</text>\n'
            f'  <text class="wm tag"  x="114" y="92">{TAG}</text>\n</svg>\n')


def sz(svg, px):
    return re.sub(r'width="32" height="32"', f'width="{px}" height="{px}"', svg, count=1)


def force(svg, light):
    """Resolve prefers-color-scheme in BOTH directions — headless Chrome defaults
    to light, which renders a dark pane's ink invisible and makes vision report
    elements as missing. Has happened twice in this project."""
    if light:
        return (svg.replace(f"fill: {INK_D}", f"fill: {INK_L}")
                   .replace(f"stroke: {INK_D}", f"stroke: {INK_L}"))
    return re.sub(r"@media \(prefers-color-scheme: light\) \{.*?\n\s*\}\n", "", svg, flags=re.S)


def preview(assets):
    def pane(light):
        bg, fg = (BG_L, INK_L) if light else (BG_D, INK_D)
        out = []
        for key, (lg, wm, blurb) in assets.items():
            l_, w_ = force(lg, light), force(wm, light)
            ladder = "".join(f'<div class="s"><div class="h">{sz(l_, px)}</div><i>{px}</i></div>'
                             for px in SIZES)
            out.append(f'<h3>{key}<em>{blurb}</em></h3><div class="row">{ladder}</div>'
                       f'<div class="lock">{w_}</div>')
        return (f'<section style="background:{bg};color:{fg}">'
                f'<h2>{"LIGHT" if light else "DARK"}</h2>' + "".join(out) + "</section>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>doublegate — mark round 3</title>
<style>
  body {{ margin:0; font:14px {SANS_ATTR}; }}
  section {{ padding:26px 30px 34px; }}
  h2 {{ font-size:12px; letter-spacing:2.5px; opacity:.5; margin:0 0 20px; }}
  h3 {{ font-size:14px; margin:24px 0 8px; font-weight:650; }}
  h3 em {{ font-weight:400; opacity:.5; font-style:normal; margin-left:10px; font-size:13px; }}
  .row {{ display:flex; align-items:flex-end; gap:20px; }}
  .s {{ text-align:center; }}
  .s i {{ display:block; font-size:10px; opacity:.4; margin-top:5px; font-style:normal; }}
  .h {{ display:flex; align-items:center; justify-content:center; height:130px; }}
  .lock {{ margin-top:12px; }} .lock svg {{ width:360px; height:auto; }}
</style></head><body>{pane(False)}{pane(True)}</body></html>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    assets = {}
    for key, (geom, blurb) in RIVALS.items():
        desc = f"{NAME} — {blurb}."
        lg, wm = logo(geom, desc), wordmark(geom, desc)
        for svg in (lg, wm):
            ET.fromstring(svg)
        open(os.path.join(OUT, f"logo-{key}.svg"), "w").write(lg)
        open(os.path.join(OUT, f"wordmark-{key}.svg"), "w").write(wm)
        assets[key] = (lg, wm, blurb)

    open(os.path.join(OUT, "preview.html"), "w").write(preview(assets))

    chrome = os.path.expanduser(
        "~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome")
    if os.path.exists(chrome):
        h = 120 + len(RIVALS) * 260 * 2          # derived, never hardcoded
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                        f' --virtual-time-budget=4000 --screenshot={OUT}/preview.png'
                        f' --window-size=900,{h} {OUT}/preview.html 2>/dev/null'], check=False)
        for key, (lg, _w, _b) in assets.items():
            d = force(lg, light=False)
            cells = "".join('<div style="display:flex;align-items:center;justify-content:center;'
                            f'width:150px;height:150px">{sz(d, px)}</div>' for px in (16, 32, 128))
            p = os.path.join(OUT, f".one-{key}.html")
            open(p, "w").write(f'<!doctype html><body style="margin:0;background:{BG_D};'
                               f'display:flex">{cells}</body>')
            subprocess.run(["bash", "-c",
                            f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                            f' --virtual-time-budget=2500 --screenshot={OUT}/one-{key}.png'
                            f' --window-size=460,155 {p} 2>/dev/null'], check=False)
            os.remove(p)

    print(f"{len(RIVALS)} rivals dodging all four failure classes -> {OUT}")
    print("A round-top+legs=n  B bars=chart/menu  C circle=Q/pin  D column=person")


if __name__ == "__main__":
    main()
