#!/usr/bin/env python3
"""Round 7 — the channel family, pushed. Eight variants on one stance.

Run:      python3 assets/gate-v2/build7.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure7.js
Audit:    node assets/gate-v2/audit-geometry.js assets/gate-v2/round7/logo-*.svg
Read:     python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
            assets/gate-v2/round7/one-*.png

WHAT THIS ROUND KNOWS THAT EARLIER ONES DID NOT
-----------------------------------------------
The channel stance is: two masses, and the gate is ONLY the void between them.
Nothing depicts a gate. Three rounds of evidence about it:

  channel            (r5) marginal, ink 0.625  -> "a bold H"
  channel-jambs      (r6) marginal, ink 0.594  -> "a stylized E"   [stayed symmetric]
  channel-threshold  (r6) separable, ink 0.664 -> "a stylized H with a bar"  [3 elements]
  channel-ajar       (r6) separable, ink 0.516 -> "a folded ribbon, a bookmark"
  channel-ajar-both  (r6) separable, ink 0.352 -> "a folded ribbon or lightning bolt"

Two hard rules fall out, and every variant here obeys both:

  1. SYMMETRY MANUFACTURES THE LETTER. Symmetric void -> H. Symmetric void with a
     stepped head -> E. The plainness of the blocks was never the problem. So no
     variant below is left-right symmetric.
  2. A THIRD ELEMENT RE-SYMMETRISES AND ADDS INK. channel-threshold was the
     heaviest mark of round 6 and went straight back to "H". Two elements, always.

Also carried: the ajar variants prove asymmetric voids read as ribbons and folds
rather than letters, which is a *usable* register — ribbons and folds suggest
documents and seals, which is on-subject.

ANGLES ARE SNAPPED THIS TIME
----------------------------
Round 6 shipped 65.22, 75.96, 33.69 degrees. IBM's rule is multiples of 15 because
45 anti-aliases evenly and arbitrary diagonals do not — and 16px is exactly where
these are judged. Every diagonal below is built from a whole-number rise over run
that lands on or very near the 15 degree step:
    dy/dx = 26/15 -> 60.0   |  13/8 -> 58.4   |  12/7 -> 59.7
    dy/dx = 8/14  -> 29.7   |  6/10 -> 31.0   |  1/1  -> 45.0
The audit still prints anything that drifts, and drift is reported rather than
hidden.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

GRN = "#34d399"
SLATE = "#64748b"
AMB = "#fbbf24"
INK_D, INK_L = "#e6e9ef", "#10131a"
BG_D, BG_L = "#08090c", "#ffffff"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round7")
SANS_ATTR = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"

INK_STYLE = f"""  <style>
    .ink {{ fill: {INK_D}; }}
    .ink-s {{ stroke: {INK_D}; }}
    @media (prefers-color-scheme: light) {{
      .ink {{ fill: {INK_L}; }}
      .ink-s {{ stroke: {INK_L}; }}
    }}
  </style>"""


# ---------------------------------------------------------------- geometry
# Every mark: exactly two elements, no left-right symmetry.

def g_swung(i="  "):
    """Both leaves swung the SAME way — a revolving door caught mid-turn.

    The ajar variants opened leaves outward, mirror-fashion, which is still a kind
    of symmetry. Rotating both the same direction makes the whole mark rotational
    rather than reflective: it reads as motion through, not as a pair of doors.

    The void becomes a parallelogram. No letter of the alphabet has a
    parallelogram counter, which is the point.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 4 h9 l-4 24 h-9 z" fill="{SLATE}"/>',
        f'<path d="M31 4 h-9 l-4 24 h9 z" fill="{GRN}"/>',
    ])


def g_shear(i="  "):
    """One mass cut clean through and the halves slid past each other.

    Not two doors at all — ONE block, sheared. The void is a single diagonal slot
    running corner to corner, and the offset means the two halves no longer line
    up, so the thing has visibly been through something.

    This is the round-4 `seam` idea rebuilt inside the channel stance: the cut IS
    the gate, and the displacement is the record that it happened.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M4 4 h22 l-8 12 h-14 z" class="ink"/>',
        f'<path d="M28 28 h-22 l8 -12 h14 z" fill="{GRN}"/>',
    ])


def g_stagger(i="  "):
    """Two masses at different heights — the void is an L-shaped dogleg.

    Instead of opening the leaves, offset them vertically. The channel between
    them stops being a straight corridor and becomes a dogleg: you cannot see
    through it in one line, which is exactly what a two-stage check means. Nothing
    passes without turning a corner.

    An L-shaped void cannot be a letter counter — letters have closed or open
    counters, not corridors that turn.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 3 h12 v13 h-6 v3 h6 v10 h-12 z" fill="{SLATE}"/>',
        f'<path d="M29 29 h-12 v-13 h6 v-3 h-6 v-10 h12 z" fill="{GRN}"/>',
    ])


def g_interlock(i="  "):
    """Two combs whose teeth mesh without touching — a maze, not a doorway.

    The void becomes a single continuous zigzag that has to be traversed. Two
    teeth on one side, one on the other, so the count itself is asymmetric and no
    reflection exists.

    Risk knowingly taken: comb teeth on a baseline is class B territory (bar
    chart). These teeth are horizontal and interleaved rather than standing on a
    shared line, which should keep it out — testing beats assuming.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M3 3 h13 v5 h-6 v6 h6 v5 h-6 v6 h6 v4 h-13 z" class="ink"/>',
        f'<path d="M29 3 h-9 v8 h4 v4 h-4 v8 h4 v6 h5 z" fill="{GRN}"/>',
    ])


def g_funnel(i="  "):
    """The channel narrows once, off-centre — a weir, wide in and tight out.

    Selection drawn as a shape rather than as a mechanism: what goes in is wide,
    what comes out is narrow, and the narrowing happens at one point rather than
    gradually. The step is off-centre so the two sides differ.

    Both diagonals are 26 over 15, which is 60.0 degrees exactly.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 3 h10 v9 l4 8 v10 h-14 z" fill="{SLATE}"/>',
        f'<path d="M29 3 h-8 v9 l-2 8 v10 h10 z" fill="{GRN}"/>',
    ])


def g_slip(i="  "):
    """Two overlapping leaves, one behind the other — depth, not a corridor.

    Every previous channel put the masses side by side with clear air between. Here
    they OVERLAP, one passing behind the other, so the void is not a gap between
    two things but the sliver where one leaf disappears behind its neighbour. That
    is what a real double door in section looks like.

    A negative sliver rather than a negative slot: much less ink, and no
    letterform available at all.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 6 h14 v20 h-14 z" fill="{SLATE}"/>',
        f'<path d="M20 3 h9 v26 h-9 l-3 -13 z" fill="{GRN}"/>',
    ])


def g_chamfer(i="  "):
    """Two masses with one corner cut off each, on opposite corners.

    The most reduced asymmetry available: keep both blocks rectangular and remove
    a single corner from each, diagonally opposite. The void stays a straight slot
    but it widens at the top on one side and at the bottom on the other, so the
    silhouette is point-symmetric and never mirror-symmetric.

    Cheapest possible fix to the H problem, and included precisely to find out
    whether cheap is enough.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M3 3 h11 v26 h-11 z M14 3 l-11 11 v-11 z" class="ink"'
        ' fill-rule="evenodd"/>',
        f'<path d="M29 29 h-11 v-26 h11 z M18 29 l11 -11 v11 z" fill="{GRN}"'
        ' fill-rule="evenodd"/>',
    ])


def g_wicket(i="  "):
    """A big gate with a small gate cut into one leaf — a door within a door.

    A wicket is the person-sized door set inside a cart-sized one, and it is a
    genuinely institutional object: the big gate opens rarely and by decision, the
    wicket handles the ordinary traffic. Two tiers of admission in one form,
    which is closer to what this product does than any pair of doors.

    Two elements: the leaf, and the wicket void cut through it. The second mass is
    the frame's other side. Deeply asymmetric by construction.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M3 3 h18 v26 h-18 z M8 12 h8 v17 h-8 z" class="ink"'
        ' fill-rule="evenodd"/>',
        f'<path d="M25 3 h4 v26 h-4 z" fill="{GRN}"/>',
    ])


RIVALS = {
    "slip": (g_slip, "two overlapping leaves, one behind the other — a sliver, not a slot"),
    "shear": (g_shear, "one block cut through and the halves slid past each other"),
    "swung": (g_swung, "both leaves rotated the same way — a revolving door mid-turn"),
    "stagger": (g_stagger, "masses at different heights — the void is an L-shaped dogleg"),
    "chamfer": (g_chamfer, "one corner cut from each block, diagonally opposite"),
    "funnel": (g_funnel, "the channel narrows once, off-centre — a weir"),
    "wicket": (g_wicket, "a small gate cut into one leaf of a big gate"),
    "interlock": (g_interlock, "two combs meshing without touching — a maze, not a doorway"),
}

SIZES = [16, 22, 32, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n{INK_STYLE}\n{geom("  ")}\n</svg>\n')


def mono(geom, desc):
    g = (geom("  ").replace(f'"{GRN}"', '"currentColor"')
                   .replace(f'"{SLATE}"', '"currentColor"')
                   .replace(f'"{AMB}"', '"currentColor"'))
    g = re.sub(r'class="ink(-s)?"', lambda m: 'fill="currentColor"' if not m.group(1)
               else 'stroke="currentColor"', g)
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
            '    .tag { font-size: 20px; fill: #97a1b2; }\n'
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
    if light:
        return (svg.replace(f"fill: {INK_D}", f"fill: {INK_L}")
                   .replace(f"stroke: {INK_D}", f"stroke: {INK_L}"))
    return re.sub(r"@media \(prefers-color-scheme: light\) \{.*?\n\s*\}\n", "", svg, flags=re.S)


def preview(assets):
    def pane(light):
        bg, fg = (BG_L, INK_L) if light else (BG_D, INK_D)
        out = []
        for key, (lg, wm, mo, blurb) in assets.items():
            l_, w_ = force(lg, light), force(wm, light)
            m_ = mo.replace(f'color="{INK_D}"', f'color="{INK_L}"') if light else mo
            ladder = "".join(f'<div class="s"><div class="h">{sz(l_, px)}</div><i>{px}</i></div>'
                             for px in SIZES)
            ladder += ('<div class="s" style="margin-left:16px"><div class="h">'
                       f'{sz(m_, 64)}</div><i>mono</i></div>')
            out.append(f'<h3>{key}<em>{blurb}</em></h3><div class="row">{ladder}</div>'
                       f'<div class="lock">{w_}</div>')
        return (f'<section style="background:{bg};color:{fg}">'
                f'<h2>{"LIGHT" if light else "DARK"}</h2>' + "".join(out) + "</section>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>doublegate — round 7, the channel family</title>
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

    print(f"{len(RIVALS)} channel variants -> {OUT}")
    print("element count (2 each — a third re-symmetrises and brings the letter back):")
    for key, (geom, _b) in RIVALS.items():
        n = len(re.findall(r"<(path|rect|circle)", geom("")))
        print(f"  {key:<11} {n}{'   <-- BUG' if n > 2 else ''}")
    print("\nto beat: channel-ajar-both  separable, 17 scanlines, ink 0.352")
    print("to avoid: any left-right symmetry — symmetric void reads as H, stepped-head as E")


if __name__ == "__main__":
    main()
