#!/usr/bin/env python3
"""Improving the live doublegate mark — rivals that carry SEQUENCE.

Run from the repo root:  python3 assets/gate-v2/build.py
Then measure:            CHROME_PATH=... node assets/gate-v2/measure.js

WHY THIS EXISTS
---------------
The live mark (assets/logo.svg, commit 0d0acd3) won its round honestly and its
case study left exactly two defects on the record rather than dressing them up:

  1. "The mark says 'two gates' but not 'sequence.'" The product model is
     admission THEN ratification — ordered. The live `wide` variant is
     symmetric and carries no order. The `offset` variant ranked equally on the
     two-gates question and would have carried it; `wide` was chosen on 16px
     robustness alone. That was a real trade, not a win.
  2. "Red/green reads fail/pass." Both gates are legitimate sequential stages,
     not a bad one and a good one. Kept for palette consistency, mismatch named.

Both are now the brief. Every rival here must keep the two properties the live
mark already earned — reads as a GATE (not a toggle/circuit), reads as TWO
objects (not a lowercase m) — while adding order.

THE 6PX GAP IS LOAD-BEARING. Between x=13 and x=19 on the live mark. Anyone
tightening it for elegance reintroduces the lowercase m. Rivals may move the
gates but may not close that daylight.

PALETTE
-------
Red/green is dropped. The two gates are stages of one passage, so they get one
hue at two depths: dim slate for the first gate (passed, behind you) and full
green for the second (the one that admits). Depth-not-hue also survives
greyscale, which red/green does not — a favicon in a monochrome tab strip keeps
its order.

Amber stays available for the in-flight artifact, consistent with the naming-set
palette decision: amber = present but not yet admitted, green = admitted.

Rules carried over rather than rediscovered (../knowledgegate/README.md,
../naming-options/README.md):
  - ink fills must flip through prefers-color-scheme or they vanish on a light tab
  - an arch whose span matches the object beneath it reads as a lowercase "n"
  - two strokes meeting at a low vertex read as a tick, whatever the directions
  - a distinguishing element must differ in KIND, not degree
  - three thin parallel lines fill solid at 16px; two heavier ones survive
  - font-family in an *attribute* cannot contain quotes or the SVG will not parse
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

GRN = "#34d399"          # the gate that admits
SLATE = "#64748b"        # the gate already passed — same passage, less depth
AMB = "#fbbf24"          # in flight: present, not yet admitted
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

ARCH_L = "M 2 27 V 15.5 A 5.5 5.5 0 0 1 13 15.5 V 27"
ARCH_R = "M 19 27 V 15.5 A 5.5 5.5 0 0 1 30 15.5 V 27"


# ------------------------------------------------------------------ geometry

def g_live(i="  "):
    """CONTROL: the live mark exactly as shipped, red/green and all.

    Carried in unchanged so the improvements are measured against what is
    actually on the site rather than against a memory of it.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="{ARCH_L}" fill="none" stroke="#fb7185" stroke-width="3.5"'
        ' stroke-linecap="round"/>',
        f'<path d="{ARCH_R}" fill="none" stroke="#34d399" stroke-width="3.5"'
        ' stroke-linecap="round"/>',
    ])


def g_depth(i="  "):
    """Minimal change: same geometry, sequence carried by depth instead of hue.

    The cheapest possible fix and therefore the one to beat. Identical paths to
    the live mark — so the 16px robustness that won round 3 is preserved exactly
    — with the first gate dropped to slate and the second at full green. Order
    now reads as near-then-far rather than bad-then-good, and it survives
    greyscale.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="{ARCH_L}" fill="none" stroke="{SLATE}" stroke-width="3.5"'
        ' stroke-linecap="round"/>',
        f'<path d="{ARCH_R}" fill="none" stroke="{GRN}" stroke-width="3.5"'
        ' stroke-linecap="round"/>',
    ])


def g_step(i="  "):
    """Sequence by height: the second gate stands taller than the first.

    This is the `offset` idea from round 3, which ranked equally on the
    two-gates question and was dropped only on 16px robustness. Made explicit:
    unequal heights read as a progression, and the taller second gate says the
    ratification gate is the higher bar.

    Heights differ by 4px, not 1. A 1px difference reads as a drawing error;
    4px reads as intent, and survives downscaling to 16px where 1px is gone.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M 2 27 V 18 A 5.5 5.5 0 0 1 13 18 V 27" fill="none" stroke="{SLATE}"'
        ' stroke-width="3.5" stroke-linecap="round"/>',
        f'<path d="M 19 27 V 13.5 A 5.5 5.5 0 0 1 30 13.5 V 27" fill="none" stroke="{GRN}"'
        ' stroke-width="3.5" stroke-linecap="round"/>',
    ])


def g_transit(i="  "):
    """Sequence by an artifact between the gates, mid-passage.

    Order is stated by *position* rather than by styling the gates: the thing
    being admitted sits between gate one and gate two, so it has visibly passed
    the first and not the second. Direction of travel becomes unambiguous.

    Costs the mark its emptiness — a third element inside 256 pixels is what
    pushed AgentLibrarian to weakest-of-six in the naming set. The block is kept
    small and low so it cannot bridge the load-bearing gap.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="{ARCH_L}" fill="none" stroke="{SLATE}" stroke-width="3.2"'
        ' stroke-linecap="round"/>',
        f'<path d="{ARCH_R}" fill="none" stroke="{GRN}" stroke-width="3.2"'
        ' stroke-linecap="round"/>',
        f'<rect x="14.2" y="21" width="3.6" height="6" rx="1" fill="{AMB}"/>',
    ])


def g_stack(i="  "):
    """Sequence as two gates in DEPTH — one behind the other, not side by side.

    The stance the live mark cannot take: side-by-side is inherently symmetric,
    so no styling fully fixes order. Two gates on the same axis, the near one
    lower and offset, read as a corridor you go through one after the other.

    Risk being tested: overlapping arches are exactly how the lowercase-m trap
    was born. The offset here is diagonal rather than horizontal, so the two
    crowns never share a baseline and there is no centre post to fuse.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M 13 12 V 6.5 A 5 5 0 0 1 28 6.5 V 12" fill="none" stroke="{SLATE}"'
        ' stroke-width="3" stroke-linecap="round"/>',
        f'<path d="M 3 28 V 19 A 6 6 0 0 1 21 19 V 28" fill="none" stroke="{GRN}"'
        ' stroke-width="3.4" stroke-linecap="round"/>',
    ])


def g_numbered(i="  "):
    """Sequence by a tally: gate one carries one stroke, gate two carries two.

    Order stated as a count rather than as a style — the second gate is the one
    with two marks under it. Unambiguous and language-free.

    The strokes sit BELOW the crowns and outside them, so they cannot be read as
    a tick (no vertex) and cannot fuse with the arch at 16px.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M 2 22 V 13 A 5.5 5.5 0 0 1 13 13 V 22" fill="none" stroke="{SLATE}"'
        ' stroke-width="3.2" stroke-linecap="round"/>',
        f'<path d="M 19 22 V 13 A 5.5 5.5 0 0 1 30 13 V 22" fill="none" stroke="{GRN}"'
        ' stroke-width="3.2" stroke-linecap="round"/>',
        f'<path d="M 7.5 27 v3" stroke="{SLATE}" stroke-width="2.6" stroke-linecap="round"/>',
        f'<path d="M 22 27 v3" stroke="{GRN}" stroke-width="2.6" stroke-linecap="round"/>',
        f'<path d="M 27 27 v3" stroke="{GRN}" stroke-width="2.6" stroke-linecap="round"/>',
    ])


RIVALS = {
    "live": (g_live, "control — the shipped mark, red/green, symmetric"),
    "depth": (g_depth, "same paths, order by depth not hue"),
    "step": (g_step, "order by height — the second gate is the higher bar"),
    "transit": (g_transit, "order by position — the artifact is between the gates"),
    "stack": (g_stack, "order in depth — a corridor, not a pair"),
    "numbered": (g_numbered, "order by tally — one stroke, then two"),
}

SIZES = [16, 22, 32, 48, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


# -------------------------------------------------------------------- assets

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


def social(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200"'
            f' height="630" role="img" aria-label="{NAME} — {TAG}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n'
            '  <style>\n'
            f'    .wm {{ font-family: {SANS_ATTR}; }}\n'
            f'    .name {{ font-size: 104px; font-weight: 680; letter-spacing: -3px;'
            f' fill: {INK_D}; }}\n'
            '    .tag { font-size: 38px; fill: #b6bfcd; }\n'
            f'    .dom {{ font-size: 27px; fill: {DIM}; letter-spacing: 0.5px; }}\n'
            f'    .ink {{ fill: {INK_D}; }}\n'
            f'    .ink-s {{ stroke: {INK_D}; }}\n'
            '  </style>\n'
            f'  <rect width="1200" height="630" fill="{BG_D}"/>\n'
            f'  <rect x="0" y="0" width="1200" height="5" fill="{GRN}"/>\n'
            '  <g transform="translate(96 150) scale(4.1)">\n'
            f'{geom("    ")}\n'
            '  </g>\n'
            f'  <text class="wm name" x="96" y="360">{NAME}</text>\n'
            f'  <text class="wm tag"  x="100" y="424">{TAG}</text>\n'
            '  <text class="wm dom"  x="100" y="530">doublegate.io</text>\n'
            '</svg>\n')


def sz(svg, px):
    return re.sub(r'width="32" height="32"', f'width="{px}" height="{px}"', svg, count=1)


def force(svg, light):
    """Resolve prefers-color-scheme by hand, in BOTH directions.

    Headless Chrome defaults to LIGHT, so a dark pane relying on the media query
    renders dark ink on dark ground and a vision read honestly reports elements
    as missing. That has happened twice in this project.
    """
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
<html lang="en"><head><meta charset="utf-8"><title>doublegate — mark v2</title>
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
    assets = {}
    for key, (geom, blurb) in RIVALS.items():
        desc = f"{NAME} — {blurb}."
        lg, wm = logo(geom, desc), wordmark(geom, desc)
        for svg in (lg, wm, social(geom, desc)):
            ET.fromstring(svg)          # gate: never write unparseable markup
        open(os.path.join(HERE, f"logo-{key}.svg"), "w").write(lg)
        open(os.path.join(HERE, f"wordmark-{key}.svg"), "w").write(wm)
        open(os.path.join(HERE, f"social-{key}.svg"), "w").write(social(geom, desc))
        assets[key] = (lg, wm, blurb)

    open(os.path.join(HERE, "preview.html"), "w").write(preview(assets))

    # One tight PNG per rival, dark only, for the semantic read. A 900x3000 sheet
    # makes a vision model summarise instead of answering per-mark.
    chrome = os.path.expanduser(
        "~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome")
    if os.path.exists(chrome):
        h = 120 + len(RIVALS) * 260 * 2      # derived, never hardcoded
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                        f' --virtual-time-budget=4000 --screenshot={HERE}/preview.png'
                        f' --window-size=900,{h} {HERE}/preview.html 2>/dev/null'], check=False)
        for key, (lg, _wm, _b) in assets.items():
            d = force(lg, light=False)
            cells = "".join('<div style="display:flex;align-items:center;justify-content:center;'
                            f'width:150px;height:150px">{sz(d, px)}</div>' for px in (16, 32, 128))
            p = os.path.join(HERE, f".one-{key}.html")
            open(p, "w").write(f'<!doctype html><body style="margin:0;background:{BG_D};'
                               f'display:flex">{cells}</body>')
            subprocess.run(["bash", "-c",
                            f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                            f' --virtual-time-budget=2500 --screenshot={HERE}/one-{key}.png'
                            f' --window-size=460,155 {p} 2>/dev/null'], check=False)
            os.remove(p)

    print(f"{len(RIVALS)} rival marks for {NAME} -> {HERE}")
    print("brief: carry SEQUENCE (admission then ratification), drop red/green fail/pass")
    print("next: CHROME_PATH=... node assets/gate-v2/measure.js")
    print("      python3 .tmp/ask_vision.py  (ollama :11435, ornith-1.5:9b)")


if __name__ == "__main__":
    main()
