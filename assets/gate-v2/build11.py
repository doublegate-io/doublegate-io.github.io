#!/usr/bin/env python3
"""Round 11 — two navies, rounded corners, stretched to rectangles.

Run:      python3 assets/gate-v2/build11.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure11.js
Audit:    node assets/gate-v2/audit-geometry.js assets/gate-v2/round11/logo-*.svg
Read:     python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
            assets/gate-v2/round11/one-*.png

THREE CHANGES REQUESTED, AND ONE OF THEM NEEDED A CORRECTION FIRST
------------------------------------------------------------------
Asked for: ink-two-navy, rounded corners instead of square, and rectangles stretched
instead of squares. Two of the three are straightforward. The two-navy pair is not,
and the reason is measured rather than aesthetic.

ink-two-navy was #0A1F44 + #12275C, and those two are 1.14:1 AGAINST EACH OTHER.
Round 10's vision read on that exact file came back as "a cluster of THREE
overlapping squares" — where the strokes crossed they merged and manufactured a
square that was never drawn. Both inks are excellent against paper (16.25:1 and
14.28:1); it is the pair that fails.

So: how far up the same-hue ramp must the partner go before two navies read as two?

    #12275C  1.14:1 vs granat   MERGES   (the one that failed)
    #173371  1.35:1             MERGES
    #1B3A80  1.52:1             MERGES
    #1E3A8A  1.57:1             MERGES   (blue 800)
    #1E40AF  1.86:1             MERGES   (blue 700)
    #2148A0  1.93:1             MERGES
    #2657B8  2.43:1             marginal
    #2563eb  3.14:1             PASS     (blue 600)
    #3b82f6  4.42:1             PASS     (blue 500)

The answer is that a true navy-on-navy pair cannot be done — the partner has to
travel all the way to blue 600 before the two separate. So this round uses
#0A1F44 + #2563eb: the DEEPEST possible partner that still reads as two elements.
That is the two-navy idea honoured as closely as the physics allows, and it comes
with a bonus the brighter pick did not have — #2563eb clears 3:1 on all three
grounds at once (3.85:1 dark, 5.17:1 white, 3.14:1 against granat), so it is usable
in every position without a second value.

STRETCHING CHANGES WHAT THE MARK CAN BE MISTAKEN FOR
----------------------------------------------------
Two overlapping SQUARES is the copy/duplicate icon's exact gesture, and that
affordance risk has been open on this shape since round 4. A stretched rectangle is
not that icon. It is a card, a plate, a label, a ledger line, a nameplate — all of
which are closer to a register entry than a UI clipboard is.

But stretching costs something specific and it has to be watched: a wide rectangle
has less HEIGHT for horizontal scanlines to separate, and gapRows is where the
16px verdict comes from. Several ratios are built so the cost is visible rather
than assumed.

ROUNDED CORNERS, ON THE 2px STEP
--------------------------------
audit-geometry.js requires corner radii to be multiples of 2px on a 32px grid (IBM's
rule), so rx is 2 or 4 and never 3 or 5. Round 9 found square corners read as "a
plate or a seal" rather than a UI card, which was the point of going square — so
rounding is a deliberate walk-back toward warmth, and the audit's 2px step is what
keeps it from drifting into a soft app-icon look.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

# ---- the palette, every value measured before use
GRANAT = "#0A1F44"        # 16.25:1 white. Cannot sit on a dark ground (1.23:1).
NAVY2 = "#2563eb"         # blue 600. 3.14:1 vs granat, 5.17:1 white, 3.85:1 dark —
                          # the deepest partner that still separates from granat.
BLUE = "#3b82f6"          # blue 500, round 10's constant, kept for the dark build
INK_D = "#e6e9ef"
PAPER = "#ffffff"
BG_D = "#08090c"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round11")
SANS_ATTR = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"
W = 2.5


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
#
# <rect>, never <path> with miter joins: round 10 measured the path version of the
# identical box at ink 0.406 against rect's 0.336, because miter joins project past
# the corner and add paint a rect's own corners do not.
#
# Coordinates stay inside the 2px reserved edge (so 2..30) and land on whole pixels.

def _origin(w, h, off_x, off_y):
    """Top-left of the REAR rect so the pair is centred and stays inside the margin.

    Centring the combined bounding box in the 32px grid is the obvious move and it is
    what pushed the wide variants into the reserved 2px edge: at 22px wide with an
    8px offset the pair spans 30px, so a centred origin lands at x=1. IBM reserves
    2..30 on a 32px grid, and artwork in the margin is what gets clipped by a
    platform that adds its own mask.

    So centre, then clamp to 2, and if the pair is too wide to fit inside the margin
    at all the caller must reduce the offset or the width rather than have this
    silently overflow. Asserted rather than trusted.
    """
    span_x, span_y = w + off_x, h + off_y
    assert span_x <= 28 and span_y <= 28, (
        f"pair spans {span_x}x{span_y}, will not fit inside the 2px reserved margin")
    x0 = max(2, round((32 - span_x) / 2))
    y0 = max(2, round((32 - span_y) / 2))
    return x0, y0


def _rects(w, h, off_x, off_y, rx, rear, front):
    """Two stretched rectangles, offset, rear then front."""
    x0, y0 = _origin(w, h, off_x, off_y)

    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{rx}"'
            f' fill="none" stroke="{rear}" stroke-width="{W}"/>',
            f'<rect x="{x0 + off_x}" y="{y0 + off_y}" width="{w}" height="{h}" rx="{rx}"'
            f' fill="none" stroke="{front}" stroke-width="{W}"/>',
        ])
    return g


def _themed(w, h, off_x, off_y, rx):
    """The shippable one-file build.

    On paper the two navies do the work. On dark granat is invisible (1.23:1), so it
    drops out and the pair becomes blue 500 rear with ink in front — round 10's role
    swap, which keeps a blue present on both grounds so the brand colour never
    changes.
    """
    x0, y0 = _origin(w, h, off_x, off_y)

    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{rx}"'
            f' fill="none" class="rear" stroke-width="{W}"/>',
            f'<rect x="{x0 + off_x}" y="{y0 + off_y}" width="{w}" height="{h}" rx="{rx}"'
            f' fill="none" class="front" stroke-width="{W}"/>',
        ])
    return g


# Ratios, from nearly-square to a hard letterbox. Offsets are 8px where the geometry
# allows it, because round 10 measured that a 6px offset cost ink 0.531 vs 0.336 —
# a tighter overlap puts more stroke inside the crossing region.
RIVALS = {
    "r-4x3": (_rects(20, 15, 8, 8, 2, GRANAT, NAVY2),
              "PAPER · 4:3, rx2 — the gentlest stretch"),
    "r-3x2": (_rects(20, 13, 8, 8, 2, GRANAT, NAVY2),
              "PAPER · 3:2, rx2 — classic card proportion"),
    "r-16x9": (_rects(20, 11, 8, 8, 2, GRANAT, NAVY2),
               "PAPER · 16:9, rx2 — a plate or a nameplate"),
    "r-2x1": (_rects(20, 10, 8, 8, 2, GRANAT, NAVY2),
              "PAPER · 2:1, rx2 — a label or a ledger line"),
    "r-5x2": (_rects(20, 8, 8, 6, 2, GRANAT, NAVY2),
              "PAPER · 5:2, rx2 — hard letterbox, offset dropped to fit"),
    "r-3x2-rx4": (_rects(20, 13, 8, 8, 4, GRANAT, NAVY2),
                  "PAPER · 3:2 with rx4 — softer, testing the radius step"),
    "r-3x2-vert": (_rects(13, 20, 8, 8, 2, GRANAT, NAVY2),
                   "PAPER · 3:2 PORTRAIT — a page or a card stood upright"),
    "r-3x2-shift": (_rects(18, 12, 10, 5, 2, GRANAT, NAVY2),
                    "PAPER · 3:2, offset mostly sideways — reads as displacement"),
    # ---- the old pair, kept as evidence
    "r-3x2-failed-pair": (_rects(20, 13, 8, 8, 2, GRANAT, "#12275C"),
                          "PAPER · the ORIGINAL two-navy pair at 1.14:1 — merges, proof"),
    # ---- dark ground
    "dark-3x2": (_rects(20, 13, 8, 8, 2, BLUE, INK_D),
                 "DARK · blue 500 rear, ink front — the role swap"),
    "dark-3x2-navy2": (_rects(20, 13, 8, 8, 2, NAVY2, INK_D),
                       "DARK · blue 600 rear at 3.85:1, ink front — one colour both grounds"),
    # ---- the shippable file
    "themed-3x2": (_themed(20, 13, 8, 8, 2),
                   "THEMED · one file: two navies on paper, blue+ink on dark"),
}
THEMES = {RIVALS["themed-3x2"][0]: (BLUE, INK_D, GRANAT, NAVY2)}

SIZES = [16, 22, 32, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


def _theme_style(geom):
    if geom not in THEMES:
        return ""
    rd, fd, rl, fl = THEMES[geom]
    return f"""  <style>
    .rear {{ stroke: {rd}; }}
    .front {{ stroke: {fd}; }}
    @media (prefers-color-scheme: light) {{
      .rear {{ stroke: {rl}; }}
      .front {{ stroke: {fl}; }}
    }}
  </style>
"""


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n{_theme_style(geom)}{geom("  ")}\n</svg>\n')


def mono(geom, desc, dark):
    """One ink. A two-colour mark must still work in a single colour — embossing,
    engraving, a partner's monochrome footer."""
    g = geom("  ")
    for c in (GRANAT, NAVY2, BLUE, INK_D, "#12275C"):
        g = g.replace(f'"{c}"', '"currentColor"')
    g = re.sub(r'class="(rear|front)"', 'stroke="currentColor"', g)
    col = INK_D if dark else GRANAT
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}" color="{col}">\n'
            f'  <title>{NAME}</title>\n  <desc>{desc} Monochrome.</desc>\n{g}\n</svg>\n')


def wordmark(geom, desc, dark):
    name_c = INK_D if dark else GRANAT
    tag_c = "#97a1b2" if dark else "#55606f"
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 120" width="720"'
            f' height="120" role="img" aria-label="{NAME} — {TAG}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n  <style>\n'
            f'    .wm {{ font-family: {SANS_ATTR}; }}\n'
            f'    .name {{ font-size: 54px; font-weight: 650; letter-spacing: -1.2px;'
            f' fill: {name_c}; }}\n'
            f'    .tag {{ font-size: 20px; fill: {tag_c}; }}\n'
            '  </style>\n'
            f'{_theme_style(geom)}'
            '  <g transform="translate(14 12) scale(2.0)">\n'
            f'{geom("    ")}\n  </g>\n'
            f'  <text class="wm name" x="112" y="60">{NAME}</text>\n'
            f'  <text class="wm tag"  x="114" y="92">{TAG}</text>\n</svg>\n')


def sz(svg, px):
    return re.sub(r'width="32" height="32"', f'width="{px}" height="{px}"', svg, count=1)


def force(svg, light):
    """Resolve prefers-color-scheme in code, both directions — headless Chrome
    defaults to light, so a dark pane relying on the query renders wrong and a
    vision read then honestly reports missing elements."""
    if light:
        m = re.search(r"@media \(prefers-color-scheme: light\) \{(.*?)\n\s*\}\n", svg, re.S)
        if m:
            for cls, col in re.findall(r"\.(\w[\w-]*) \{ stroke: (#[0-9a-fA-F]{6}); \}",
                                       m.group(1)):
                svg = re.sub(rf"\.{cls} \{{ stroke: #[0-9a-fA-F]{{6}}; \}}(?![\s\S]*?@media)",
                             f".{cls} {{ stroke: {col}; }}", svg, count=1)
        return svg
    return re.sub(r"@media \(prefers-color-scheme: light\) \{.*?\n\s*\}\n", "", svg, flags=re.S)


def preview(assets):
    def pane(dark_pane):
        bg = BG_D if dark_pane else PAPER
        fg = INK_D if dark_pane else GRANAT
        out = []
        for key, (lg, wm, mo, blurb) in assets.items():
            is_dark = key.startswith("dark-")
            if key.startswith("themed"):
                pass                        # themed appears in both panes
            elif is_dark != dark_pane:
                continue
            l_ = force(lg, light=not dark_pane)
            w_ = force(wm, light=not dark_pane)
            m_ = mo.replace(f'color="{GRANAT}"', f'color="{INK_D}"') if dark_pane else mo
            ladder = "".join(f'<div class="s"><div class="h">{sz(l_, px)}</div><i>{px}</i></div>'
                             for px in SIZES)
            ladder += ('<div class="s" style="margin-left:16px"><div class="h">'
                       f'{sz(m_, 64)}</div><i>1 ink</i></div>')
            out.append(f'<h3>{key}<em>{blurb}</em></h3><div class="row">{ladder}</div>'
                       f'<div class="lock">{w_}</div>')
        head = ("DARK — granat drops out at 1.23:1, blue carries it"
                if dark_pane else "PAPER — two navies, granat's home ground")
        return (f'<section style="background:{bg};color:{fg}">'
                f'<h2>{head}</h2>' + "".join(out) + "</section>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>doublegate — stretched, two navies</title>
<style>
  body {{ margin:0; font:14px {SANS_ATTR}; }}
  section {{ padding:26px 30px 34px; }}
  h2 {{ font-size:12px; letter-spacing:2.5px; opacity:.55; margin:0 0 20px; }}
  h3 {{ font-size:14px; margin:24px 0 8px; font-weight:650; }}
  h3 em {{ font-weight:400; opacity:.55; font-style:normal; margin-left:10px; font-size:13px; }}
  .row {{ display:flex; align-items:flex-end; gap:20px; }}
  .s {{ text-align:center; }}
  .s i {{ display:block; font-size:10px; opacity:.45; margin-top:5px; font-style:normal; }}
  .h {{ display:flex; align-items:center; justify-content:center; height:130px; }}
  .lock {{ margin-top:12px; }} .lock svg {{ width:360px; height:auto; }}
</style></head><body>{pane(False)}{pane(True)}</body></html>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    assets = {}
    for key, (geom, blurb) in RIVALS.items():
        desc = f"{NAME} — {blurb}."
        dark = key.startswith("dark-")
        lg, wm, mo = logo(geom, desc), wordmark(geom, desc, dark), mono(geom, desc, dark)
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
        h = 140 + len(RIVALS) * 300          # derived from the rival count
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                        f' --virtual-time-budget=4000 --screenshot={OUT}/preview.png'
                        f' --window-size=1000,{h} {OUT}/preview.html 2>/dev/null'], check=False)
        for key, (lg, _w, _m, _b) in assets.items():
            dark_g = key.startswith("dark-")
            ground = BG_D if dark_g else PAPER
            d = force(lg, light=not dark_g)
            cells = "".join('<div style="display:flex;align-items:center;justify-content:center;'
                            f'width:150px;height:150px">{sz(d, px)}</div>' for px in (16, 32, 128))
            p = os.path.join(OUT, f".one-{key}.html")
            open(p, "w").write(f'<!doctype html><body style="margin:0;background:{ground};'
                               f'display:flex">{cells}</body>')
            subprocess.run(["bash", "-c",
                            f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                            f' --virtual-time-budget=2500 --screenshot={OUT}/one-{key}.png'
                            f' --window-size=460,155 {p} 2>/dev/null'], check=False)
            os.remove(p)

    print(f"{len(RIVALS)} variants -> {OUT}\n")
    print("a true two-navy pair cannot be done — the partner must travel to blue 600")
    print("before the two read as two. Ink-vs-ink against granat #0A1F44:")
    for h, n in [("#12275C", "the original pair — MERGES"), ("#173371", "navy lifted"),
                 ("#1B3A80", "navy lifted more"), ("#1E3A8A", "blue 800"),
                 ("#1E40AF", "blue 700"), ("#2657B8", "marginal"),
                 (NAVY2, "BLUE 600 — chosen, deepest that separates"),
                 (BLUE, "blue 500")]:
        v = contrast(GRANAT, h)
        verdict = "PASS" if v >= 3 else ("marginal" if v >= 2 else "MERGES")
        print(f"  {h}  {v:5.2f}:1  {verdict:<9} {n}")
    print(f"\nand {NAVY2} clears every ground at once, which the brighter pick did not need to:")
    print(f"  vs granat {contrast(GRANAT, NAVY2):.2f}:1   "
          f"on white {contrast(NAVY2, PAPER):.2f}:1   on dark {contrast(NAVY2, BG_D):.2f}:1")
    print("\nwatch gapRows as the stretch increases — a wide rectangle has less height")
    print("for horizontal scanlines to separate, and that is where the 16px verdict comes from.")


if __name__ == "__main__":
    main()
