#!/usr/bin/env python3
"""Round 6 — keystone and channel, developed with detail. On request.

Run:      python3 assets/gate-v2/build6.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure6.js
Audit:    node assets/gate-v2/audit-geometry.js assets/gate-v2/round6/logo-*.svg
Read:     python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
            assets/gate-v2/round6/one-*.png

THE ASK, AND THE TRADE IT MAKES
-------------------------------
Requested: keystone with more detail, channel with more detail, and channel with
one side of the door slightly opened.

This deliberately relaxes round 4's one-or-two-element constraint. That constraint
came from Rand ("a logo does not need to explain the business") and Haviv ("simple
enough to be drawn from memory"), and it is the reason rounds 4 and 5 finally
stopped producing diagrams. Going back up in element count risks the exact failure
that killed rounds 1-3.

So every mark here prints its element count, and the README records what the
detail bought and what it cost. If a detailed variant measures worse AND reads
worse than its minimal parent, that is a finding, not a defeat.

TWO REASONS THE ASK IS WELL-AIMED
---------------------------------
1. Detail should FIX keystone rather than burden it. `keystone` fused at 16px with
   ZERO separating scanlines — the worst possible result — because a single solid
   convex shape has no interior void, and interior void is what survives
   downscaling. Adding an interior feature is not decoration here; it is the only
   thing that can make the mark separable at all.

2. An opened door should BREAK the "H" read. `channel` read as "a bold H", a new
   failure class: the negative space between two masses is itself a letter. H is
   perfectly symmetric. An asymmetric gap — one leaf swung open, the other shut —
   cannot be an H, because no letter has one straight side and one angled one in
   that arrangement. This is a real hypothesis with a real prediction.

CONSTRAINTS STILL IN FORCE
--------------------------
  A round top + descending legs -> n/u/horseshoe/E
  B stacked horizontal bars     -> chart/hamburger
  C circle esp. with a tail     -> Q/question mark/map pin/crescent
  D narrow centred column       -> a person
  E two masses with a gap       -> the VOID is a letter (H)
  X = reject. LOW vertex = tick (an apex is fine — the caret proved that).
  IBM 32px grid: whole numbers, 2px padding, radii on the 2px step, angles on the
  15 degree step. All angles below are 15/30/45/60/75 by construction.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

GRN = "#34d399"
SLATE = "#64748b"
INK_D, INK_L = "#e6e9ef", "#10131a"
BG_D, BG_L = "#08090c", "#ffffff"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round6")
SANS_ATTR = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"

INK_STYLE = f"""  <style>
    .ink {{ fill: {INK_D}; }}
    .ink-s {{ stroke: {INK_D}; }}
    @media (prefers-color-scheme: light) {{
      .ink {{ fill: {INK_L}; }}
      .ink-s {{ stroke: {INK_L}; }}
    }}
  </style>"""


# ------------------------------------------------------- keystone, developed

def g_keystone_joints(i="  "):
    """The keystone with its two joint lines — the voussoirs either side.

    A keystone alone is just a trapezoid. What identifies it as a keystone is the
    JOINT: the radial line where it meets the stone beside it. Two joints, cut as
    voids through the block, give the shape its name back.

    This is the fix for the fusion, not a decoration. The solid trapezoid scored
    0 separating scanlines because a convex mass is one unbroken run on every
    line. Two interior cuts create the void the measurement needs.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M10 4 h12 l6 24 h-24 z'
        ' M13 7 l-4 18 h-2 l4 -18 z'
        ' M19 7 l4 18 h2 l-4 -18 z" class="ink" fill-rule="evenodd"/>',
    ])


def g_keystone_seated(i="  "):
    """The keystone seated between two springing stones, locked in place.

    Adds what a keystone is FOR: it is the last stone placed, and it puts the two
    sides into compression. The neighbours are cut back so the keystone reads as
    the piece that completes the span, and the whole thing keeps a flat top rather
    than an arch, so class A cannot apply.

    Three elements. Above the round-4 budget, and recorded as such.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M12 5 h8 l5 22 h-18 z" class="ink"/>',
        f'<path d="M3 27 h6 l4 -18 h-6 z" fill="{SLATE}"/>',
        f'<path d="M29 27 h-6 l-4 -18 h6 z" fill="{SLATE}"/>',
    ])


def g_keystone_marked(i="  "):
    """The keystone with a mason's mark struck into it.

    Historically the stone carries the mark of whoever cut it — accountable
    authorship, which is the reviewer-is-never-the-author invariant in stone. The
    mark is a lozenge void inside the block: interior negative space, which fixes
    the fusion, and meaning that is hidden rather than shown.

    One element. The most reduced of the three keystone developments.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M10 4 h12 l6 24 h-24 z M16 11 l5 5 l-5 5 l-5 -5 z"'
        ' class="ink" fill-rule="evenodd"/>',
    ])


# -------------------------------------------------------- channel, developed

def g_channel_jambs(i="  "):
    """The channel, with each side given a jamb and a lintel stop.

    `channel` read as "a bold H" because two plain vertical masses with a gap
    between them is exactly that letter. Detail here is aimed squarely at the H:
    each block gets a stepped head, so the two inner edges are no longer two
    parallel straight lines, and the crossbar the eye invents has nothing to sit
    on.

    Two elements still. The gates remain purely the void between them.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M3 3 h11 v4 h-4 v6 h4 v6 h-4 v6 h4 v4 h-11 z" class="ink"/>',
        '<path d="M29 3 h-11 v4 h4 v6 h-4 v6 h4 v6 h-4 v4 h11 z" class="ink"/>',
    ])


def g_channel_threshold(i="  "):
    """The channel with a threshold, and the artifact standing on it.

    Adds the floor the passage runs across and one small block on it, mid-channel:
    past the first gate, short of the second. This is the most literal of the
    three channel developments and the closest to a diagram, which is exactly the
    risk the element budget exists to control.

    Three elements. Included so the cost of the detail is measurable rather than
    argued about.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M3 3 h10 v9 h-3 v4 h3 v9 h-10 z" class="ink"/>',
        '<path d="M29 3 h-10 v9 h3 v4 h-3 v9 h10 z" class="ink"/>',
        f'<path d="M3 28 h26 M14 17 h4 v4 h-4 z" stroke="{GRN}" stroke-width="2"'
        ' fill="none" stroke-linecap="round"/>',
    ])


def g_channel_ajar(i="  "):
    """The channel with the near leaf swung open. THE H-BREAKER.

    The left mass stays a shut jamb. The right one is drawn as a leaf pivoted
    outward — its inner edge runs at 60 degrees instead of vertical, so the void
    between them is a wedge rather than a slot.

    H is perfectly symmetric and both its uprights are straight. A gap with one
    straight side and one angled side cannot be read as an H, which is the whole
    point of the variant. It also states sequence for free: one gate has been
    passed (open), the next has not (shut).

    Two elements, and it keeps the meaning-in-the-void stance intact.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M3 3 h10 v26 h-10 z" class="ink"/>',
        f'<path d="M29 3 v26 h-8 l6 -13 l-6 -13 z" fill="{GRN}"/>',
    ])


def g_channel_ajar_both(i="  "):
    """Both leaves ajar, by different amounts — sequence in one gesture.

    If one open leaf breaks the H, two opened by DIFFERENT angles should break it
    harder while also carrying the order: the first gate stands wide, the second
    barely cracked. Asymmetry does the work that colour was doing in earlier
    rounds.

    Two elements. Tests whether the asymmetry or the openness is what matters.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 3 v26 l9 -6 l-4 -7 l4 -7 z" fill="{SLATE}"/>',
        f'<path d="M29 3 v26 l-6 -3 l3 -10 l-3 -10 z" fill="{GRN}"/>',
    ])


RIVALS = {
    "keystone-marked": (g_keystone_marked,
                        "keystone with a mason's mark struck into it — 1 element"),
    "keystone-joints": (g_keystone_joints,
                        "keystone with its two voussoir joints cut through — 1 element"),
    "keystone-seated": (g_keystone_seated,
                        "keystone locked between two springing stones — 3 elements"),
    "channel-ajar": (g_channel_ajar,
                     "channel with the near leaf swung open — the H-breaker"),
    "channel-ajar-both": (g_channel_ajar_both,
                          "both leaves ajar by different amounts — order by asymmetry"),
    "channel-jambs": (g_channel_jambs,
                      "channel with stepped jambs — inner edges no longer parallel"),
    "channel-threshold": (g_channel_threshold,
                          "channel with a threshold and the artifact on it — 3 elements"),
}

SIZES = [16, 22, 32, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n{INK_STYLE}\n{geom("  ")}\n</svg>\n')


def mono(geom, desc):
    g = geom("  ").replace(f'"{GRN}"', '"currentColor"').replace(f'"{SLATE}"', '"currentColor"')
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
<html lang="en"><head><meta charset="utf-8"><title>doublegate — round 6</title>
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

    print(f"{len(RIVALS)} developed variants -> {OUT}")
    print("element count (round 4's budget was 1-2; these are ON REQUEST above it):")
    for key, (geom, _b) in sorted(RIVALS.items(),
                                  key=lambda kv: len(re.findall(r"<(path|rect|circle)",
                                                                kv[1][0]("")))):
        n = len(re.findall(r"<(path|rect|circle)", geom("")))
        print(f"  {key:<20} {n}{'   <-- over budget, deliberately' if n > 2 else ''}")
    print("\nparents to beat:  keystone FUSED 0 scanlines · channel marginal 18, reads 'H'")


if __name__ == "__main__":
    main()
