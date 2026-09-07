#!/usr/bin/env python3
"""Round 8 — develop `offset`: fix the overlap, then study colour with numbers.

Run:      python3 assets/gate-v2/build8.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure8.js
Audit:    node assets/gate-v2/audit-geometry.js assets/gate-v2/round8/logo-*.svg
Read:     python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
            assets/gate-v2/round8/one-*.png

WHY offset EARNED THIS
---------------------
Best-measuring mark of 59: separable at 16px with 23 separating scanlines, ink
0.406, and the only mark in eight rounds to pass the IBM 32px-grid audit
untouched. Reads back as "two overlapping squares forming a window-like frame" —
no letter, no chart, no pin, no person.

THE ONE REAL DEFECT, AND IT IS NOT COSMETIC
-------------------------------------------
Where the two outlines cross there are four line-crossings and a small closed
cell. Nothing states which square is in front. That matters twice over:

  - Semantically. Two squares that merely intersect are peers. Two squares where
    one passes clearly IN FRONT are ordered — and order (admission, then
    ratification) is the property four rounds tried and failed to carry.
  - Optically. At 16px, four crossings inside a 5x5 pixel region is where a mark
    turns to mud. The 23 scanlines are measured on the whole glyph; the crossing
    region is the part that will not survive a favicon.

Three ways to resolve a crossing, all tested here rather than argued:
  knockout  — the front square carries a background-coloured gap, so the rear
              outline visibly stops. Classic, and it is how a real overlap looks.
  weave     — front over at one crossing, under at the other. Interlocked rather
              than stacked, which reads as custody: neither link opens alone.
  fill      — the front square is solid, so occlusion is automatic and total.

KNOCKOUT HAS A TRAP THIS PROJECT HAS ALREADY HIT
------------------------------------------------
A gap painted in the background colour is correct on dark and a visible dark bar
on white. That exact bug shipped once here (the `spine-book` notch). So the
knockout gap must theme through prefers-color-scheme like every other ink, and
`audit-geometry.js` now has a check for a themed class with no media query.

COLOUR: MEASURED, NOT PREFERRED
-------------------------------
The site palette is fixed (assets/style.css :root) and every option below is drawn
from it, so nothing invents a new brand colour:
    --grn #34d399   --cyn #22d3ee   --amb #fbbf24   --vio #a78bfa   --red #fb7185
    --ink #e6e9ef   --ink-dim #97a1b2   on --bg #08090c / white

This file computes WCAG contrast for every accent against BOTH backgrounds and
prints it. A mark is not shippable if its accent fails on white, because a favicon
cannot control the tab colour. 3:1 is the graphical-object threshold (WCAG 1.4.11);
below that the stroke disappears.

Red is excluded on meaning, not on contrast: red/green reads fail/pass, and the two
squares are sequential stages rather than a bad one and a good one.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

INK_D, INK_L = "#e6e9ef", "#10131a"
BG_D, BG_L = "#08090c", "#ffffff"
GRN, CYN, AMB, VIO, DIM = "#34d399", "#22d3ee", "#fbbf24", "#a78bfa", "#97a1b2"

# The accent problem, and the two candidate fixes.
#
# Every accent in :root is tuned for the dark site and every one of them fails the
# 3:1 graphical-object threshold on white — grn 1.92:1, cyn 1.81:1, amb 1.67:1. The
# ink already themes through prefers-color-scheme; the accent never did, because
# until now it only ever appeared on the dark page. A favicon cannot choose the tab
# colour, so this is a real defect rather than a nicety.
#
# ONE-SHADE fix: move down the same hue ramp until one value clears 3:1 on both
# grounds. #059669 (emerald 600) gives 5.28:1 dark / 3.77:1 white. One hex
# everywhere, nothing to theme, and it cannot drift — but it is visibly duller than
# the site's #34d399 and would not match the accent used elsewhere on the page.
#
# THEMED fix: keep #34d399 on dark, swap to #059669 on light, exactly as .ink
# already flips. Same hue, correct weight on each ground, and the mark keeps the
# site's own green where the site is actually dark. Costs one media-query line.
GRN_L = "#059669"   # emerald 600 — 3.77:1 on white
CYN_L = "#0891b2"
AMB_L = "#d97706"
VIO_L = "#8b5cf6"
ACCENT_LIGHT = {GRN: GRN_L, CYN: CYN_L, AMB: AMB_L, VIO: VIO_L, DIM: "#55606f"}
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round8")
SANS_ATTR = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"

# .cut is the knockout gap: it must flip with the theme or it is a dark bar on
# white. This project has shipped that bug before.
INK_STYLE = f"""  <style>
    .ink {{ fill: {INK_D}; }}
    .ink-s {{ stroke: {INK_D}; }}
    .cut {{ stroke: {BG_D}; }}
    .acc {{ stroke: {GRN}; }}
    @media (prefers-color-scheme: light) {{
      .ink {{ fill: {INK_L}; }}
      .ink-s {{ stroke: {INK_L}; }}
      .cut {{ stroke: {BG_L}; }}
      .acc {{ stroke: {GRN_L}; }}
    }}
  </style>"""

W = 2.5          # stroke weight, one value everywhere (IBM: no mixed weights)


# ------------------------------------------------------- contrast, measured

def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ------------------------------------------------------------------ geometry
# Baseline for reference:
#   rect 3,3  18x18 rx2 stroke GRN
#   rect 11,11 18x18 rx2 stroke ink
# Every variant keeps two elements and whole-number coordinates.

def g_baseline(i="  "):
    """The round-4 mark exactly as measured, carried in as the control.

    Two identical outlined squares, offset 8px on both axes, strokes simply
    crossing. Nothing states which is in front.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{GRN}"'
        f' stroke-width="{W}"/>',
        f'<rect x="11" y="11" width="18" height="18" rx="2" fill="none" class="ink-s"'
        f' stroke-width="{W}"/>',
    ])


def g_knockout(i="  "):
    """The rear square visibly stops where the front one passes over it.

    Two short strokes in the background colour, laid over the rear outline along
    the front square's two leading edges. The rear square now reads as behind
    rather than merely intersecting, so the pair is ordered.

    The gap strokes are heavier than the outline (4 vs 2.5) so the break survives
    downscaling — a background gap the same width as the line it interrupts closes
    up under anti-aliasing.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{GRN}"'
        f' stroke-width="{W}"/>',
        f'<path d="M11 13 v8 h8" fill="none" class="cut" stroke-width="4.5"'
        f' stroke-linecap="butt"/>'
        f'\n{i}<rect x="11" y="11" width="18" height="18" rx="2" fill="none"'
        f' class="ink-s" stroke-width="{W}"/>',
    ])


def g_weave(i="  "):
    """Interlocked: front at one crossing, behind at the other.

    A woven overlap says neither square is simply on top — they are linked, and
    neither comes apart without the other. That is chain of custody rather than
    hierarchy, and it is the more accurate relationship for a record and its
    countersignature.

    Two knockout segments, one on each outline, at opposite crossings.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 3 h18 v18 h-18 z" fill="none" stroke="{GRN}"'
        f' stroke-width="{W}" stroke-linejoin="round"/>'
        f'\n{i}<path d="M13 21 h8" fill="none" class="cut" stroke-width="4.5"/>',
        f'<path d="M11 11 h18 v18 h-18 z" fill="none" class="ink-s"'
        f' stroke-width="{W}" stroke-linejoin="round"/>'
        f'\n{i}<path d="M11 13 v8" fill="none" class="cut" stroke-width="4.5"/>',
    ])


def g_solidfront(i="  "):
    """The front square solid, the rear one outlined. Occlusion is total.

    The heaviest statement of order available: what is admitted is filled in, what
    is still outside is only drawn. Also the simplest to read at 16px, because a
    solid mass needs no interpretation.

    Risk: ink climbs, and a solid square with an outline behind it edges toward the
    copy/duplicate affordance that is already the open question on this mark.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{GRN}"'
        f' stroke-width="{W}"/>',
        '<rect x="11" y="11" width="18" height="18" rx="2" class="ink"/>',
    ])


def g_tight(i="  "):
    """Knockout, with the offset reduced 8px -> 6px and radius dropped to 0.

    Two things at once, both about optical weight. A smaller offset makes the pair
    read as one object rather than two loose squares; square corners make it read
    as a record or a plate rather than a UI card, which is the affordance risk.

    Sharper corners also survive 16px better than a 2px radius, which rounds away
    to mush at that size.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M4 4 h18 v18 h-18 z" fill="none" stroke="{GRN}"'
        f' stroke-width="{W}" stroke-linejoin="miter"/>',
        f'<path d="M10 12 v10 h10" fill="none" class="cut" stroke-width="4.5"/>'
        f'\n{i}<path d="M10 10 h18 v18 h-18 z" fill="none" class="ink-s"'
        f' stroke-width="{W}" stroke-linejoin="miter"/>',
    ])


def g_axis(i="  "):
    """Knockout, offset on ONE axis only — displaced sideways, not diagonally.

    A diagonal offset is the copy/duplicate icon's exact gesture. A purely
    horizontal displacement is not: it reads as one thing having moved along a
    line, which is what passing through a gate is.

    Tests whether the UI-affordance risk lives in the overlap or in the diagonal.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 7 h17 v18 h-17 z" fill="none" stroke="{GRN}"'
        f' stroke-width="{W}" stroke-linejoin="round"/>',
        f'<path d="M12 7 v18" fill="none" class="cut" stroke-width="4.5"/>'
        f'\n{i}<path d="M12 7 h17 v18 h-17 z" fill="none" class="ink-s"'
        f' stroke-width="{W}" stroke-linejoin="round"/>',
    ])


# Colour study: identical geometry (the knockout), one accent swapped, so the
# comparison is colour and nothing else.
def _knockout_with(accent):
    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{accent}"'
            f' stroke-width="{W}"/>',
            f'<path d="M11 13 v8 h8" fill="none" class="cut" stroke-width="4.5"/>'
            f'\n{i}<rect x="11" y="11" width="18" height="18" rx="2" fill="none"'
            f' class="ink-s" stroke-width="{W}"/>',
        ])
    return g


ACCENTS = {"grn": GRN, "cyn": CYN, "amb": AMB, "vio": VIO, "dim": DIM}


def g_fix_oneshade(i="  "):
    """Knockout with the accent moved down its own ramp to #059669.

    One hex on both grounds — 5.28:1 dark, 3.77:1 white — so nothing themes and
    nothing can drift out of step. The cost is that it is duller than the site's
    #34d399, and on the dark page it will not match the green used elsewhere.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{GRN_L}"'
        f' stroke-width="{W}"/>',
        f'<path d="M11 13 v8 h8" fill="none" class="cut" stroke-width="4.5"/>'
        f'\n{i}<rect x="11" y="11" width="18" height="18" rx="2" fill="none"'
        f' class="ink-s" stroke-width="{W}"/>',
    ])


def g_fix_themed(i="  "):
    """Knockout with the accent themed: #34d399 on dark, #059669 on light.

    Same hue on both grounds, correct optical weight on each, and the dark page
    keeps the exact green the rest of the site uses. Costs one media-query line,
    which .ink and .cut already pay.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<rect x="3" y="3" width="18" height="18" rx="2" fill="none" class="acc"'
        f' stroke-width="{W}"/>',
        f'<path d="M11 13 v8 h8" fill="none" class="cut" stroke-width="4.5"/>'
        f'\n{i}<rect x="11" y="11" width="18" height="18" rx="2" fill="none"'
        f' class="ink-s" stroke-width="{W}"/>',
    ])


RIVALS = {
    "baseline": (g_baseline, "round-4 control — strokes simply cross, nothing in front"),
    "knockout": (g_knockout, "rear outline stops where the front square passes over"),
    "weave": (g_weave, "interlocked — front at one crossing, behind at the other"),
    "solidfront": (g_solidfront, "front square solid: occlusion total, order unmistakable"),
    "tight": (g_tight, "knockout, offset 8->6px, square corners"),
    "axis": (g_axis, "knockout, displaced sideways only — not the duplicate-icon diagonal"),
    "fix-oneshade": (g_fix_oneshade, "ACCENT FIX A — one shade #059669, passes 3:1 on both"),
    "fix-themed": (g_fix_themed, "ACCENT FIX B — #34d399 dark / #059669 light, themed"),
}
RIVALS.update({f"colour-{k}": (_knockout_with(v), f"knockout with the {k} accent ({v})")
               for k, v in ACCENTS.items()})

SIZES = [16, 22, 32, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n{INK_STYLE}\n{geom("  ")}\n</svg>\n')


def mono(geom, desc):
    """Flat monochrome. A mark that only works in two colours cannot be drawn from
    memory in one, and a favicon may be rendered on any ground."""
    g = geom("  ")
    for c in (GRN, CYN, AMB, VIO, DIM):
        g = g.replace(f'"{c}"', '"currentColor"')
    g = re.sub(r'class="acc"', 'stroke="currentColor"', g)
    g = re.sub(r'class="ink-s"', 'stroke="currentColor"', g)
    g = re.sub(r'class="ink"', 'fill="currentColor"', g)
    g = re.sub(r'class="cut"', f'stroke="{BG_D}"', g)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}" color="{INK_D}">\n'
            f'  <title>{NAME}</title>\n  <desc>{desc} Monochrome.</desc>\n{g}\n</svg>\n')


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
            f'    .cut {{ stroke: {BG_D}; }}\n'
            f'    .acc {{ stroke: {GRN}; }}\n'
            '    @media (prefers-color-scheme: light) {\n'
            f'      .name {{ fill: {INK_L}; }}\n'
            '      .tag { fill: #55606f; }\n'
            f'      .ink {{ fill: {INK_L}; }}\n'
            f'      .ink-s {{ stroke: {INK_L}; }}\n'
            f'      .cut {{ stroke: {BG_L}; }}\n'
            f'      .acc {{ stroke: {GRN_L}; }}\n'
            '    }\n  </style>\n'
            '  <g transform="translate(14 12) scale(2.0)">\n'
            f'{geom("    ")}\n  </g>\n'
            f'  <text class="wm name" x="112" y="60">{NAME}</text>\n'
            f'  <text class="wm tag"  x="114" y="92">{TAG}</text>\n</svg>\n')


def sz(svg, px):
    return re.sub(r'width="32" height="32"', f'width="{px}" height="{px}"', svg, count=1)


def force(svg, light):
    """Resolve prefers-color-scheme in code, BOTH directions. Headless Chrome
    defaults to light, so a dark pane relying on the query renders dark on dark
    and a vision read honestly reports missing elements."""
    if light:
        return (svg.replace(f"fill: {INK_D}", f"fill: {INK_L}")
                   .replace(f"stroke: {INK_D}", f"stroke: {INK_L}")
                   .replace(f"stroke: {BG_D}", f"stroke: {BG_L}")
                   .replace(f"stroke: {GRN};", f"stroke: {GRN_L};"))
    return re.sub(r"@media \(prefers-color-scheme: light\) \{.*?\n\s*\}\n", "", svg, flags=re.S)


def preview(assets):
    def pane(light):
        bg, fg = (BG_L, INK_L) if light else (BG_D, INK_D)
        out = []
        for key, (lg, wm, mo, blurb) in assets.items():
            l_, w_ = force(lg, light), force(wm, light)
            m_ = mo.replace(f'color="{INK_D}"', f'color="{INK_L}"') if light else mo
            if light:
                m_ = m_.replace(f'stroke="{BG_D}"', f'stroke="{BG_L}"')
            ladder = "".join(f'<div class="s"><div class="h">{sz(l_, px)}</div><i>{px}</i></div>'
                             for px in SIZES)
            ladder += ('<div class="s" style="margin-left:16px"><div class="h">'
                       f'{sz(m_, 64)}</div><i>mono</i></div>')
            out.append(f'<h3>{key}<em>{blurb}</em></h3><div class="row">{ladder}</div>'
                       f'<div class="lock">{w_}</div>')
        return (f'<section style="background:{bg};color:{fg}">'
                f'<h2>{"LIGHT" if light else "DARK"}</h2>' + "".join(out) + "</section>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>doublegate — offset, developed</title>
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
        lg, wm, mo = logo(geom, desc), wordmark(geom, desc), mono(geom, desc)
        for svg in (lg, wm, mo):
            ET.fromstring(svg)
        open(os.path.join(OUT, f"logo-{key}.svg"), "w").write(lg)
        open(os.path.join(OUT, f"wordmark-{key}.svg"), "w").write(wm)
        open(os.path.join(OUT, f"mono-{key}.svg"), "w").write(mo)
        assets[key] = (lg, wm, mo, blurb)

    open(os.path.join(OUT, "preview.html"), "w").write(preview(assets))

    chrome = os.path.expanduser(
        "~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome")
    if os.path.exists(chrome):
        h = 120 + len(RIVALS) * 260 * 2          # derived from the rival count
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                        f' --virtual-time-budget=4000 --screenshot={OUT}/preview.png'
                        f' --window-size=1000,{h} {OUT}/preview.html 2>/dev/null'], check=False)
        for key, (lg, _w, _m, _b) in assets.items():
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

    print(f"{len(RIVALS)} variants -> {OUT}\n")
    print("WCAG contrast of each accent, on BOTH grounds. 3:1 is the graphical-object")
    print("threshold (1.4.11); a favicon cannot choose the tab colour, so white matters.")
    print(f"  {'accent':<8} {'hex':<9} {'on #08090c':>11} {'on white':>9}   verdict")
    for k, v in list(ACCENTS.items()) + [("ink", INK_D)]:
        cd, cl = contrast(v, BG_D), contrast(v, BG_L)
        ok = "PASS both" if min(cd, cl) >= 3 else (
            f"FAILS on {'white' if cl < 3 else 'dark'} ({min(cd, cl):.2f}:1)")
        print(f"  {k:<8} {v:<9} {cd:>10.2f}:1 {cl:>8.2f}:1   {ok}")
    print("\nred #fb7185 excluded on MEANING not contrast: red/green reads fail/pass,")
    print("and the two squares are sequential stages, not a bad one and a good one.")


if __name__ == "__main__":
    main()
