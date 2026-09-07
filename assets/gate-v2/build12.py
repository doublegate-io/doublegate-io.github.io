#!/usr/bin/env python3
"""Round 12 — the portrait mark, deeper overlap, visible on both grounds.

Run:      python3 assets/gate-v2/build12.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure12.js
Audit:    node assets/gate-v2/audit-geometry.js assets/gate-v2/round12/logo-*.svg
Read:     python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
            assets/gate-v2/round12/one-*.png

THE REQUEST, AND THE WALL IN IT
-------------------------------
Asked for: the r-3x2-vert portrait mark, in similar colours, MORE VISIBLE on both
dark and light grounds, with a little MORE OVERLAP.

The visibility half of that request runs into a wall that is worth stating with
numbers rather than working around silently. A colour clears 3:1 (WCAG 1.4.11) on
BOTH grounds only if its luminance sits in the band

    dark #08090c  ->  L >= 3*(Lbg + .05) - .05  =  0.108
    white         ->  L <= 1.05/3 - .05         =  0.300

Inside that band, the MAXIMUM possible ratio between two colours is
(0.300+.05)/(0.108+.05) = 2.21:1 — under the 3:1 the ink-vs-ink gate requires. So
no two fixed colours can both be visible on both grounds where their strokes
touch. One of the two has to give.

The honest version of "similar colours, visible on both" is therefore:

    ONE CONSTANT + a partner per ground.

    #2563eb  blue 600   THE CONSTANT — the only value in the family that clears
                        3:1 on all four counts at once:
                        on dark 3.85:1 · on white 5.17:1
                        vs granat 3.14:1 · vs ink 4.25:1
    paper    granat #0A1F44 rear + blue 600 front
    dark     blue 600 rear + ink #e6e9ef front

Blue 600 is what makes the identity read as the same brand on both grounds: it is
present in every render, and only its ROLE changes — the same trick round 10
found, now with the deepest blue that still separates.

MORE OVERLAP, AND WHAT IT IS EXPECTED TO COST
--------------------------------------------
Deeper overlap means a SMALLER offset (the offset is the gap between the two
rects' origins). Round 10 measured that shrinking the offset 8 -> 6 on the square
mark cost ink 0.336 -> 0.531 — more stroke sits inside the crossing region. So
the ladder below is built at offsets 8, 7, 6, 5, 4 and measured rather than
assumed; if "a little more" has a price, the price is printed.

One thing deeper overlap may BUY, and it is the reason the portrait was risky in
round 11: the 8px-offset portrait read back as "stacked PHONES OR TABLETS" — a
device affordance. A phone-stack icon needs clear air between the two devices;
deeper overlap makes the pair read as one layered object instead. The vision reads
on this ladder test that directly.

GEOMETRY HELD FROM ROUND 11
---------------------------
Portrait 13x20, rx2, <rect> never <path> (miter joins add paint: 0.406 vs 0.336 on
the identical box), whole-pixel coordinates, spans asserted inside the 2px reserved
margin.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

# ---- the palette, every value measured before use
GRANAT = "#0A1F44"        # 16.25:1 on white. Cannot sit on dark (1.23:1).
NAVY2 = "#2563eb"         # blue 600 — THE CONSTANT. Clears 3:1 on all four counts.
INK_D = "#e6e9ef"         # 16.37:1 on dark, 1.22:1 on white — dark ground only.
PAPER = "#ffffff"
BG_D = "#08090c"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round12")
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

def _origin(w, h, off_x, off_y):
    """Centre the pair, clamp to the 2px reserved margin, assert it fits.

    Round 11's first pass centred wide variants straight into the margin (a 22px
    rect + 8px offset spans 30px, so the origin lands at x=1). Centre, clamp,
    assert — the assert caught three silent overflows the same day it was added.
    """
    span_x, span_y = w + off_x, h + off_y
    assert span_x <= 28 and span_y <= 28, (
        f"pair spans {span_x}x{span_y}, will not fit inside the 2px reserved margin")
    x0 = max(2, round((32 - span_x) / 2))
    y0 = max(2, round((32 - span_y) / 2))
    return x0, y0


def _portrait(off, rx, rear, front):
    """13x20 portrait pair at the given offset. Static colours."""
    x0, y0 = _origin(13, 20, off, off)

    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="{x0}" y="{y0}" width="13" height="20" rx="{rx}"'
            f' fill="none" stroke="{rear}" stroke-width="{W}"/>',
            f'<rect x="{x0 + off}" y="{y0 + off}" width="13" height="20" rx="{rx}"'
            f' fill="none" stroke="{front}" stroke-width="{W}"/>',
        ])
    return g


def _portrait_themed(off, rx):
    """The shippable one-file build. Classes resolve per ground via the style block:
    paper granat rear + blue 600 front; dark blue 600 rear + ink front."""
    x0, y0 = _origin(13, 20, off, off)

    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="{x0}" y="{y0}" width="13" height="20" rx="{rx}"'
            f' fill="none" class="rear" stroke-width="{W}"/>',
            f'<rect x="{x0 + off}" y="{y0 + off}" width="13" height="20" rx="{rx}"'
            f' fill="none" class="front" stroke-width="{W}"/>',
        ])
    return g


RIVALS = {
    # ---- the overlap ladder, on paper. offset 8 = round 11's r-3x2-vert.
    "v-8": (_portrait(8, 2, GRANAT, NAVY2),
            "PAPER · offset 8 — round 11's portrait, rebuilt with the correct pair"),
    "v-7": (_portrait(7, 2, GRANAT, NAVY2),
            "PAPER · offset 7 — the first step deeper"),
    "v-6": (_portrait(6, 2, GRANAT, NAVY2),
            "PAPER · offset 6 — the expected pick: 'a little more' overlap"),
    "v-5": (_portrait(5, 2, GRANAT, NAVY2),
            "PAPER · offset 5 — deep, watch for fusion"),
    "v-4": (_portrait(4, 2, GRANAT, NAVY2),
            "PAPER · offset 4 — very deep, expected to fuse or go muddy"),
    # ---- taste variant at the expected pick
    "v-6-rx4": (_portrait(6, 4, GRANAT, NAVY2),
                "PAPER · offset 6 with rx4 — softer corners, same overlap"),
    # ---- the dark branch, and the shippable file
    "dark-v-6": (_portrait(6, 2, NAVY2, INK_D),
                 "DARK · offset 6 — blue 600 rear, ink front (the constant + partner)"),
    "themed-v-6": (_portrait_themed(6, 2),
                   "THEMED · one file: granat+blue600 on paper, blue600+ink on dark"),
}
THEMES = {RIVALS["themed-v-6"][0]: (NAVY2, INK_D, GRANAT, NAVY2)}

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
    """One ink — embossing, engraving, a partner's monochrome footer."""
    g = geom("  ")
    for c in (GRANAT, NAVY2, INK_D):
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
    defaults to light, so a dark pane relying on the query renders wrong."""
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
        head = ("DARK — blue 600 constant, ink partner"
                if dark_pane else "PAPER — granat + blue 600 (the constant)")
        return (f'<section style="background:{bg};color:{fg}">'
                f'<h2>{head}</h2>' + "".join(out) + "</section>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>doublegate — portrait, deeper overlap</title>
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
    print("the wall, with numbers: a colour visible on BOTH grounds must sit in the")
    print("luminance band [0.108, 0.300]. Two colours inside that band are at most")
    print("2.21:1 apart — under the 3:1 ink-vs-ink gate. So no two FIXED colours can")
    print("be fully visible on both grounds where they touch. The build is therefore")
    print("one constant + a partner per ground:\n")
    print(f"  CONSTANT {NAVY2} blue 600 — on dark {contrast(NAVY2, BG_D):.2f}:1,"
          f" on white {contrast(NAVY2, PAPER):.2f}:1,"
          f" vs granat {contrast(GRANAT, NAVY2):.2f}:1, vs ink {contrast(INK_D, NAVY2):.2f}:1")
    print(f"  paper branch: granat {GRANAT} + {NAVY2}")
    print(f"  dark  branch: {NAVY2} + ink {INK_D}\n")
    print("overlap ladder — watch ink climb as the offset shrinks (more stroke inside")
    print("the crossing region). Round 10 saw 8->6 cost ink 0.336->0.531 on the square.")
    print("also watch the reads: does deeper overlap kill the 'stacked phones' affordance?")


if __name__ == "__main__":
    main()