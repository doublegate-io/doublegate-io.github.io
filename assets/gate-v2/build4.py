#!/usr/bin/env python3
"""Round 4 — stop drawing the mechanism. Draw a mark.

Run:      python3 assets/gate-v2/build4.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure4.js
Read:     python3 .tmp/ask_open.py assets/gate-v2/round4/one-*.png

THE DIAGNOSIS, WHICH IS NOT ABOUT ARCHES
----------------------------------------
Eighteen rivals over three rounds were rejected. I kept treating that as a
shape problem — the arch reads as an "n", so drop the arch; the bars read as a
chart, so drop the bars. Wrong level. Every one of those marks was a small
DIAGRAM: three or four elements, arranged to explain that a thing passes one
authority and then a second one.

Paul Rand, who did IBM, UPS, ABC and NeXT, settled this in 1947:

    "A logo does not need to explain the business. It needs to be distinctive,
     memorable, and simple enough to work everywhere ... A logo derives meaning
     from the quality of the thing it stands for, not the other way around.
     The mark does not create the reputation. It stores it."

Sagi Haviv (Chermayeff & Geismar) states the test as a checklist: a mark must be
APPROPRIATE to its subject, DISTINCTIVE enough to hold meaning, and SIMPLE ENOUGH
TO BE DRAWN FROM MEMORY.

That last clause is the one that fails us. Nobody can draw a tablet with two
lozenge seals struck at different depths from memory. They can draw Vercel's
triangle, Apple's bitten circle, the Chase hexagon of four rotated shapes.

Count the elements in what we shipped and proposed:

    live mark      2 arches                        -> reads "nn"
    twoseals       tablet + 2 lozenges = 3         -> reads "a document icon"
    relay          2 diagonals + block + rule = 4  -> reads "a pen, a checkmark"
    turnstile      4 elements                      -> reads "a person"

Compare: Vercel = ONE triangle. Rand's ABC = three circles with letters.

So the brief for this round is a hard constraint, not a preference:

    ONE OR TWO ELEMENTS. NO MORE. If a viewer cannot redraw it from memory
    after five seconds, it is out — regardless of what it measures.

Meaning is allowed to be *hidden* rather than *shown*. FedEx puts an arrow in
the gap between E and x, and most people never consciously see it; it works
anyway. Amazon's curve is a-to-z and a smile in one line. That is the register to
aim at: one shape that happens to contain the second idea, not two shapes
demonstrating a process.

WHAT SURVIVES FROM THE EARLIER ROUNDS
-------------------------------------
The four failure classes still apply, and they are cheap to check against:
  A round top + descending legs -> n / u / horseshoe / E
  B stacked horizontal bars     -> bar chart / hamburger menu
  C circle with a tail          -> Q / question mark / map pin
  D narrow centred column       -> a person
Plus: an X reads as reject; two strokes meeting at a low vertex read as a tick.

Palette narrows too. Rand's WWF panda is black and white so it prints anywhere,
and "the restraint is the meaning". A two-colour mark cannot be drawn from
memory in one colour, so these are ONE ink plus at most one accent, and each is
checked in flat monochrome as well.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

GRN = "#34d399"
INK_D, INK_L = "#e6e9ef", "#10131a"
BG_D, BG_L = "#08090c", "#ffffff"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round4")
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
# Every function below emits ONE or TWO drawn elements. That is the whole point
# of the round; a third element is a bug, not a refinement.

def g_seam(i="  "):
    """ONE square, cut once, the halves offset along the cut.

    The single idea: a thing that has been through a check does not come out
    identical — it comes out registered, shifted into line. One diagonal cut
    through a solid square, upper half nudged, is a shape a person can redraw
    from memory in five seconds with two strokes.

    The gate is the cut. Nothing depicts a gate; the cut IS one, the way the
    FedEx arrow is the gap rather than a drawn arrow.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M4 4 h24 v10 l-24 4 z" class="ink"/>',
        '<path d="M4 20 l24 -4 v12 h-24 z" class="ink"/>',
    ])


def g_bite(i="  "):
    """ONE solid square with a single notch bitten out of the right edge.

    Rand's Apple principle, applied directly: Janoff put the bite in so the
    apple could not be mistaken for a cherry at small size, and it happened to
    pun on "byte". One deliberate flaw does the identifying work.

    Here the bite is the aperture — the only way in or out of a closed
    collection. One element, one absence, drawable from memory instantly.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M4 4 h24 v9 l-7 3 l7 3 v9 h-24 z" class="ink"/>',
    ])


def g_offset(i="  "):
    """TWO identical squares, one offset diagonally, overlapping.

    The Chase Manhattan move — 1960, one of the first purely abstract marks a
    major company adopted: four identical rotated shapes, meaning nothing
    literal, memorable forever. Two identical forms in a deliberate relationship
    read as *a pair in sequence* without drawing a sequence.

    Copy and countersigned copy. Original and record. The viewer supplies the
    meaning; the mark just holds the shape.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="{GRN}"'
        ' stroke-width="2.5"/>',
        '<rect x="11" y="11" width="18" height="18" rx="2" fill="none" class="ink-s"'
        ' stroke-width="2.5"/>',
    ])


def g_wedge(i="  "):
    """ONE arrow-like wedge with a slot cut across it.

    Vercel is a triangle and nothing else. This is the nearest honest equivalent
    that is not that triangle: a wedge pointing up (admitted, promoted) with a
    single horizontal slot cut through it — a thing on its way, stopped once.

    Deliberately NOT the diode from the naming set: no separate bar, no leads.
    One silhouette, one absence in it.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M16 3 l13 26 h-26 z M9 20 h14 l-2 -4 h-10 z" class="ink"'
        ' fill-rule="evenodd"/>',
    ])


def g_halfring(i="  "):
    """ONE heavy ring, broken once, with the break offset from centre.

    A seal is a ring. A ring that has been broken and re-closed carries custody:
    it was opened by someone with authority to open it. One stroke, one gap —
    the simplest closed form there is, and the gap does the talking.

    Class C says a circle with a tail reads as Q or a map pin. There is no tail
    here, and the break is on the side rather than the bottom, so there is
    nothing to read as a stem.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M16 4 a12 12 0 1 1 -8.5 20.5" fill="none" class="ink-s"'
        ' stroke-width="4.5" stroke-linecap="round"/>',
        f'<path d="M16 28 a12 12 0 0 0 8.5 -3.5" fill="none" stroke="{GRN}"'
        ' stroke-width="4.5" stroke-linecap="round"/>',
    ])


def g_dg(i="  "):
    """A monogram: d and g sharing one stem.

    The control for this round, and the option every one of these rounds has
    avoided. Supabase, Stripe, Linear all lean on the name rather than the
    mechanism. A monogram is automatically appropriate and automatically
    drawable; the risk is that it is not distinctive.

    Two counters over one stem. Included precisely because "it reads as a
    letter" is a *feature* here, and it makes the other five earn their place.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M15 4 v24" stroke="{GRN}" stroke-width="3" stroke-linecap="round"/>',
        '<path d="M15 10 h-6 a5 5 0 0 0 0 12 h6 M15 22 h6 a5 5 0 0 1 0 6 h-4"'
        ' fill="none" class="ink-s" stroke-width="3" stroke-linejoin="round"'
        ' stroke-linecap="round"/>',
    ])


RIVALS = {
    "seam": (g_seam, "one square cut once, halves offset along the cut"),
    "bite": (g_bite, "one square, one notch bitten from the edge"),
    "offset": (g_offset, "two identical squares, one offset"),
    "wedge": (g_wedge, "one wedge with a slot cut through it"),
    "halfring": (g_halfring, "one heavy ring, broken once"),
    "dg": (g_dg, "control — a d/g monogram on a shared stem"),
}

SIZES = [16, 22, 32, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n{INK_STYLE}\n{geom("  ")}\n</svg>\n')


def mono(geom, desc):
    """Flat monochrome variant. Rand's WWF panda is black and white so it prints
    anywhere, and the restraint IS the meaning. A mark that only works in two
    colours cannot be drawn from memory in one."""
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
<html lang="en"><head><meta charset="utf-8"><title>doublegate — round 4, one or two elements</title>
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
        h = 120 + len(RIVALS) * 260 * 2
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

    counts = {k: len(re.findall(r"<(path|rect|circle)", v(""))) for k, (v, _) in RIVALS.items()}
    print(f"{len(RIVALS)} rivals -> {OUT}")
    print("element count (the hard constraint — 1 or 2, a third is a bug):")
    for k, n in sorted(counts.items(), key=lambda x: x[1]):
        flag = "" if n <= 2 else "   <-- TOO MANY"
        print(f"  {k:<10} {n}{flag}")


if __name__ == "__main__":
    main()
