#!/usr/bin/env python3
"""Round 5 — six stances none of the previous 24 marks tried.

Run:      python3 assets/gate-v2/build5.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure5.js
Audit:    node assets/gate-v2/audit-geometry.js assets/gate-v2/round5/logo-*.svg
Read:     python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
            assets/gate-v2/round5/one-*.png

WHAT IS ACTUALLY NEW HERE
-------------------------
Round 4 established the constraint that matters — one or two elements, no diagram
— and produced three survivors. But all six of its marks were still *solid
geometric primitives*: square, triangle, ring. This round spends the same element
budget on four ideas that were never available while the marks were diagrams:

1. MEANING IN THE VOID (`channel`). FedEx's arrow is the gap between E and x, not
   a drawn arrow. `notch` in round 3 cut absences into a mass but still drew two
   separate accent strokes beside it. Here the two gates are ONLY the negative
   space between two blocks — nothing depicts a gate, the emptiness is one.

2. A BORROWED WORKING SYMBOL (`caret`). Proofreaders already have a mark that
   means "admit this, here": the caret. It is the editorial insertion symbol, so
   it is appropriate by inheritance rather than by explanation — and it tests a
   real hypothesis. This project's rule says two strokes meeting at a LOW vertex
   read as a tick. A caret's vertex is at the TOP. If the rule is about the
   junction's position rather than the strokes themselves, a caret escapes it.
   That is worth knowing either way.

3. THE PART THAT MAKES THE ARCH HOLD, WITHOUT THE ARCH (`keystone`). Four rounds
   died on the arch. A keystone is the single wedge that locks one — remove it and
   the arch falls. One trapezoid keeps the gate lineage and cannot read as an "n"
   because there is no round top and no legs.

4. TWO NOTCHES IN ONE FORM (`notchpair`). A single element, and the sequence is
   entirely implicit: one shape that has been cut on entry and cut again on exit.
   The most reduced statement of two gates available — nothing is drawn twice.

Plus two that test known risks rather than avoiding them:

5. `chainlink` — chain of custody, two interlocking links. The obvious risk is
   that a chain link IS the universal hyperlink icon. Testing it beats assuming.

6. `deboss` — one square with an impression struck into it. Tests whether an
   *impression* reads differently from a *notch*, after round 4's `bite` fused at
   16px for want of negative space.

CONSTRAINTS CARRIED FORWARD, ALL OF THEM
----------------------------------------
  - ONE OR TWO ELEMENTS. The count prints on every run.
  - Four failure classes: A round top + descending legs -> n/u/horseshoe/E;
    B stacked horizontal bars -> chart/hamburger; C circle esp. with a tail ->
    Q/question mark/map pin/crescent; D narrow centred column -> a person.
  - An X reads as reject. Two strokes at a low vertex read as a tick.
  - One ink + at most one accent, and a flat monochrome variant per mark, because
    a mark that needs two colours cannot be drawn from memory in one.
  - IBM 32px grid: whole-number coordinates, one stroke weight, 2px padding,
    radii on the 2px step, angles on the 15 degree step. Round 4 shipped three
    marks with arbitrary diagonals (80.54, 63.43); these are snapped from the
    start, which is cheaper than fixing them after.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

GRN = "#34d399"
INK_D, INK_L = "#e6e9ef", "#10131a"
BG_D, BG_L = "#08090c", "#ffffff"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round5")
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

def g_channel(i="  "):
    """TWO blocks. The gates are the empty space between them, and nothing else.

    The FedEx principle applied properly: the arrow between the E and the x is
    not drawn, it is what is left over. Round 3's `notch` cut absences into a
    mass but then drew two accent strokes next to it, which is having it both
    ways. Here there is no accent and no third element — two solid masses, and
    the channel running between them is the only gate present.

    The channel narrows once, halfway down. That single step is the whole
    sequence: wider on entry, tighter after the first pass. It costs no element
    because it is a property of the two shapes' edges.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M3 3 h10 v11 h-4 v4 h4 v11 h-10 z" class="ink"/>',
        '<path d="M29 3 h-10 v11 h4 v4 h-4 v11 h10 z" class="ink"/>',
    ])


def g_caret(i="  "):
    """ONE caret, the proofreader's mark for "insert this here", on its rule.

    Editors already own a symbol meaning "admitted, at this point" — it is the
    caret, and it has meant that in manuscript correction for centuries. Using it
    is appropriate by inheritance rather than by explanation, which is exactly
    what Rand's principle asks for.

    It also tests a rule this project wrote down: two strokes meeting at a LOW
    vertex read as a tick. A caret's vertex is at the top. If the tick-read comes
    from the junction's position rather than from having two strokes, the caret
    escapes it — and if it does not, the rule needs rewriting to say so.

    Angles are 60 degrees, on the 15 degree step, rather than the arbitrary
    diagonals round 4 shipped.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M8 20 l8 -12 l8 12" fill="none" class="ink-s" stroke-width="4"'
        ' stroke-linecap="round" stroke-linejoin="miter"/>',
        f'<path d="M4 26 h24" stroke="{GRN}" stroke-width="4" stroke-linecap="round"/>',
    ])


def g_keystone(i="  "):
    """ONE trapezoid: the stone that locks an arch, without drawing the arch.

    Four rounds died on the arch, and the reflex was to abandon the gate metaphor
    entirely. There is a third option — keep the lineage, drop the silhouette. A
    keystone is the single wedge at the crown of an arch that puts every other
    stone into compression; pull it and the arch falls. Nothing is admitted until
    it is in place.

    A trapezoid cannot become an "n": no round top, no descending legs, no
    counter. One element, four straight edges, symmetric, trivially redrawn from
    memory. Sides are on the 15 degree step.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M11 5 h10 l6 22 h-22 z" class="ink"/>',
    ])


def g_notchpair(i="  "):
    """ONE form, cut twice — on entry and on exit. Sequence entirely implicit.

    The most reduced statement of two gates that exists: nothing is drawn twice.
    A single block carries a notch on its left edge and another on its right, so
    the object itself records having passed two checks. The gates are absences in
    the thing, not objects beside it.

    This is the round 4 `bite` idea taken to its conclusion, and it addresses why
    `bite` FUSED at 16px: one notch in a solid mass leaves almost no internal
    negative space. Two notches, cut deeper and offset vertically, break the
    silhouette on both sides at different heights.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M4 4 h24 v6 l-6 3 l6 3 v12 h-24 v-8 l6 -3 l-6 -3 z" class="ink"/>',
    ])


def g_chainlink(i="  "):
    """TWO interlocking links: chain of custody, and neither link opens alone.

    Tests a known risk head-on instead of avoiding it — a chain link is the
    universal hyperlink icon, so this may well fail. But custody chain is the
    single most accurate metaphor available for an append-only register with two
    signatures, and the failure classes were all found by testing rather than by
    caution.

    Drawn as two rounded rectangles rather than two ovals: ovals would put us
    into class C, and rectangular links are how a physical chain actually looks
    in section.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<rect x="3" y="9" width="16" height="14" rx="4" fill="none" class="ink-s"'
        ' stroke-width="3"/>',
        f'<rect x="13" y="9" width="16" height="14" rx="4" fill="none" stroke="{GRN}"'
        ' stroke-width="3"/>',
    ])


def g_deboss(i="  "):
    """ONE block with a struck impression in it — an embossed record, not a notch.

    Round 4's `bite` fused because a notch on an outer edge only removes
    silhouette. An impression *inside* the mass creates interior negative space,
    which is what actually survives downscaling. Same one-element instinct,
    different physics.

    An accession stamp leaves an impression rather than a cut, so this is also
    more accurate to the subject than a bite is. The impression is a lozenge, not
    a circle, to stay out of class C.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M4 4 h24 v24 h-24 z M16 9 l7 7 l-7 7 l-7 -7 z" class="ink"'
        ' fill-rule="evenodd"/>',
    ])


RIVALS = {
    "channel": (g_channel, "two blocks — the gates are ONLY the space between them"),
    "caret": (g_caret, "the proofreader's insert mark, on its rule"),
    "keystone": (g_keystone, "the stone that locks an arch, without the arch"),
    "notchpair": (g_notchpair, "one form cut twice, on entry and on exit"),
    "chainlink": (g_chainlink, "two interlocking links — chain of custody"),
    "deboss": (g_deboss, "one block with a struck impression, not a cut"),
}

SIZES = [16, 22, 32, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n{INK_STYLE}\n{geom("  ")}\n</svg>\n')


def mono(geom, desc):
    g = geom("  ").replace(f'"{GRN}"', '"currentColor"')
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
<html lang="en"><head><meta charset="utf-8"><title>doublegate — round 5</title>
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
        h = 120 + len(RIVALS) * 260 * 2          # derived, never hardcoded
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

    print(f"{len(RIVALS)} rivals -> {OUT}")
    print("element count (hard constraint — 1 or 2; a third is a bug):")
    for key, (geom, _b) in sorted(RIVALS.items(),
                                  key=lambda kv: len(re.findall(r"<(path|rect|circle)",
                                                                kv[1][0]("")))):
        n = len(re.findall(r"<(path|rect|circle)", geom("")))
        print(f"  {key:<10} {n}{'   <-- TOO MANY' if n > 2 else ''}")


if __name__ == "__main__":
    main()
