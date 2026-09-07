#!/usr/bin/env python3
"""Round 2 — the arch is the problem, so stop drawing arches.

Run from the repo root:  python3 assets/gate-v2/build2.py
Measure:                 CHROME_PATH=... node assets/gate-v2/measure2.js
Read:                    python3 .tmp/ask_gate.py --dir2 <keys>

THE FINDING THAT FORCED THIS FILE
---------------------------------
Round 1 put six rivals through a local vision model one at a time, asking what
each reads as. All six came back as letterforms:

  live      "two rounded n shapes ... it reads as nn or uu"
  depth     "the letter n or m"
  step      "two n shapes, or a pair of arches"   + ORDER: NO
  transit   "it looks like nn or m"                + ORDER: NO
  stack     "a horseshoe, a U, or an upside-down n"
  numbered  "it reads like two n's or u's"

The live mark's case study recorded that the wide gap defeated the lowercase-m
trap. It did not. It converted a one-letter read into a two-letter read — "nn"
instead of "m" — and nobody asked the question again after round 3, because the
semantic question was considered closed. It was not.

The root cause is structural and no amount of spacing, colour or height fixes
it: a round-topped shape with two descending legs IS a lowercase n. Every rival
that keeps that silhouette inherits the read.

So round 2 abandons the bare arch. Every rival here must state a gate WITHOUT
drawing an n — and must still carry sequence, which round 1 also failed
(`step`'s 4px height difference and `transit`'s in-flight block both scored
ORDER: NO).

WHAT SURVIVES FROM ROUND 1
--------------------------
  - the palette decision: depth not hue (slate = passed, green = admits),
    because red/green reads fail/pass and both gates are legitimate stages
  - amber = present but not yet admitted
  - measurement before opinion; semantic read one mark at a time
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

def g_turnstile(i="  "):
    """Two horizontal barriers across a vertical channel — a turnstile in section.

    Kills the n by rotating the whole idea 90 degrees: the gates become
    horizontal bars, and a horizontal bar has no descenders, so there is no
    letter to find. The channel is implied by the bars' alignment rather than
    drawn, which keeps the ink low.

    Sequence is inherent: the artifact is above both bars, so it must cross the
    slate one and then the green one. Travel is top-to-bottom, which is how a
    queue reads.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<rect x="13" y="2.5" width="6" height="5" rx="1.3" fill="{AMB}"/>',
        f'<path d="M4 13 h24" stroke="{SLATE}" stroke-width="3.4" stroke-linecap="round"/>',
        f'<path d="M4 22 h24" stroke="{GRN}" stroke-width="3.4" stroke-linecap="round"/>',
        '<rect x="14.2" y="27" width="3.6" height="3.6" rx="1" class="ink"/>',
    ])


def g_airlock(i="  "):
    """Two shutters closing from opposite sides, offset along the channel.

    An airlock: never both open. Each gate is a bracket entering from one edge
    and stopping short, so neither is a closed round form. The two are offset
    along the horizontal axis, which states order by position on the path
    rather than by decoration.

    No round top anywhere — every stroke is a right angle, which is the property
    the arch family could not have.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M2 8 h8 v16" fill="none" stroke="{SLATE}" stroke-width="3.2"'
        ' stroke-linejoin="round" stroke-linecap="round"/>',
        f'<path d="M30 24 h-8 v-16" fill="none" stroke="{GRN}" stroke-width="3.2"'
        ' stroke-linejoin="round" stroke-linecap="round"/>',
        f'<rect x="13.5" y="13.5" width="5" height="5" rx="1.2" fill="{AMB}"/>',
    ])


def g_ratchet(i="  "):
    """Two steps up a stair, the artifact standing on the lower one.

    A stair is inherently ordered — you cannot read a step as simultaneous with
    the one above it — and it contains no closed or round form at all. The
    slate tread is the admission gate, the green tread is ratification, and the
    amber block sits on the first, having passed one and not the other.

    Ink stays low because the treads are strokes, not filled boxes.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M2.5 26 h13" stroke="{SLATE}" stroke-width="3.4" stroke-linecap="round"/>',
        f'<path d="M15.5 26 v-9" stroke="{SLATE}" stroke-width="3.4" stroke-linecap="round"/>',
        f'<path d="M15.5 16 h14" stroke="{GRN}" stroke-width="3.4" stroke-linecap="round"/>',
        f'<rect x="5" y="18.5" width="5.5" height="5.5" rx="1.3" fill="{AMB}"/>',
    ])


def g_sluice(i="  "):
    """Two vertical shutters on one horizontal run, raised to different heights.

    The canal-lock reading the PoundLock mark measured well on, rebuilt to state
    order: the first shutter is raised (passed, open) and the second is down
    (still to clear). Nothing is round, and the shared baseline makes the run a
    path rather than two objects standing about.

    The differ-in-kind rule: the two shutters are distinguished by how far they
    cross the run, not by weight or hue alone.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M2 25.5 h28" stroke="{DIM}" stroke-width="2.6" stroke-linecap="round"/>',
        f'<path d="M10 25.5 v-8" stroke="{SLATE}" stroke-width="3.4" stroke-linecap="round"/>',
        f'<path d="M22 25.5 v-19" stroke="{GRN}" stroke-width="3.4" stroke-linecap="round"/>',
        f'<rect x="13.5" y="19.5" width="5" height="5" rx="1.2" fill="{AMB}"/>',
    ])


def g_twokeys(i="  "):
    """Two keyholes, and the second one is the one that turns.

    Two-man rule stated as hardware: neither key alone opens it. Circles are
    risky (an 8 or infinity at 16px), so these are notched rings on separate
    baselines, never side by side on the same axis, with the green one carrying
    the turn stroke.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<circle cx="9.5" cy="10" r="5" fill="none" stroke="{SLATE}" stroke-width="3"/>',
        f'<circle cx="22" cy="22" r="5" fill="none" stroke="{GRN}" stroke-width="3"/>',
        f'<path d="M22 27.5 v3" stroke="{GRN}" stroke-width="2.8" stroke-linecap="round"/>',
    ])


def g_ledgerline(i="  "):
    """Two entries struck onto a register line, the second countersigning it.

    The one rival whose subject is the record instead of the door — ADR-0005 is
    a ledger. A short slate stroke is the first signature, a longer green stroke
    beneath it is the countersignature, both on the same rule.

    The strokes are stacked on separate baselines rather than crossing, because
    two strokes meeting at a low vertex read as a tick regardless of direction.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 9 h11" stroke="{SLATE}" stroke-width="3.2" stroke-linecap="round"/>',
        f'<path d="M3 18 h19" stroke="{GRN}" stroke-width="3.2" stroke-linecap="round"/>',
        f'<path d="M2.5 27 h27" stroke="{DIM}" stroke-width="2.4" stroke-linecap="round"/>',
        f'<rect x="24.5" y="14.5" width="5" height="5" rx="1.2" fill="{AMB}"/>',
    ])


RIVALS = {
    "turnstile": (g_turnstile, "two barriers across a channel, travel top to bottom"),
    "airlock": (g_airlock, "two shutters from opposite edges, offset along the path"),
    "ratchet": (g_ratchet, "two steps of a stair, artifact standing on the first"),
    "sluice": (g_sluice, "two shutters on one run, first raised and second down"),
    "twokeys": (g_twokeys, "two keyholes, the second one turns"),
    "ledgerline": (g_ledgerline, "signature then countersignature on a register rule"),
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
            f'  <desc>{desc}</desc>\n'
            '  <style>\n'
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
            '    }\n'
            '  </style>\n'
            '  <g transform="translate(14 12) scale(2.0)">\n'
            f'{geom("    ")}\n'
            '  </g>\n'
            f'  <text class="wm name" x="112" y="60">{NAME}</text>\n'
            f'  <text class="wm tag"  x="114" y="92">{TAG}</text>\n'
            '</svg>\n')


def sz(svg, px):
    return re.sub(r'width="32" height="32"', f'width="{px}" height="{px}"', svg, count=1)


def force(svg, light):
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
<html lang="en"><head><meta charset="utf-8"><title>doublegate — mark v2 round 2</title>
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
  .lock {{ margin-top:12px; }}
  .lock svg {{ width:360px; height:auto; }}
</style></head><body>{pane(False)}{pane(True)}</body></html>
"""


def main():
    d2 = os.path.join(HERE, "round2")
    os.makedirs(d2, exist_ok=True)
    assets = {}
    for key, (geom, blurb) in RIVALS.items():
        desc = f"{NAME} — {blurb}."
        lg, wm = logo(geom, desc), wordmark(geom, desc)
        for svg in (lg, wm):
            ET.fromstring(svg)
        open(os.path.join(d2, f"logo-{key}.svg"), "w").write(lg)
        open(os.path.join(d2, f"wordmark-{key}.svg"), "w").write(wm)
        assets[key] = (lg, wm, blurb)

    open(os.path.join(d2, "preview.html"), "w").write(preview(assets))

    chrome = os.path.expanduser(
        "~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome")
    if os.path.exists(chrome):
        h = 120 + len(RIVALS) * 260 * 2
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                        f' --virtual-time-budget=4000 --screenshot={d2}/preview.png'
                        f' --window-size=900,{h} {d2}/preview.html 2>/dev/null'], check=False)
        for key, (lg, _w, _b) in assets.items():
            d = force(lg, light=False)
            cells = "".join('<div style="display:flex;align-items:center;justify-content:center;'
                            f'width:150px;height:150px">{sz(d, px)}</div>' for px in (16, 32, 128))
            p = os.path.join(d2, f".one-{key}.html")
            open(p, "w").write(f'<!doctype html><body style="margin:0;background:{BG_D};'
                               f'display:flex">{cells}</body>')
            subprocess.run(["bash", "-c",
                            f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                            f' --virtual-time-budget=2500 --screenshot={d2}/one-{key}.png'
                            f' --window-size=460,155 {p} 2>/dev/null'], check=False)
            os.remove(p)

    print(f"{len(RIVALS)} arch-free rivals -> {d2}")
    print("brief: state a gate WITHOUT drawing a lowercase n, and carry sequence")


if __name__ == "__main__":
    main()
