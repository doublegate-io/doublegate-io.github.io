#!/usr/bin/env python3
"""Round 9 — `baseline` in garnet and black, on paper.

Run:      python3 assets/gate-v2/build9.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure9.js
Audit:    node assets/gate-v2/audit-geometry.js assets/gate-v2/round9/logo-*.svg
Read:     python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
            assets/gate-v2/round9/one-*.png

THE CONSTRAINT DECIDED THE GROUND, SO SAY SO UP FRONT
-----------------------------------------------------
Garnet is a DARK red. Measured against WCAG 1.4.11's 3:1 threshold for graphical
objects, on the site's near-black #08090c:

    #5C0A18  very deep   1.43:1     #9B2242  raspberry   2.56:1
    #6E1423  deep        1.69:1     #A52A45  light       2.86:1
    #7B1E3C  wine        1.98:1     #733635  gemstone    2.19:1
    #8B1A2B  brighter    2.16:1

Every one fails. Nothing that still reads as garnet clears 3:1 on black — by the
time it does (#B03A52 at 3.39:1, #C2334D at 3.67:1) it has become a pink or a
crimson, and the name no longer describes it.

So garnet-and-black is not a dark-site palette. It is a PAPER palette: garnet ink
and black ink on white, which is exactly where the colour comes from historically —
seals, ledger rules, law-book spine stamping, university crests. On white, garnet
measures 9-14:1 and is genuinely excellent.

That is a real fork rather than a detail, and it is stated in the README instead of
being buried: choosing garnet means the identity's home ground becomes light, and
the dark site becomes the inversion. The alternative is to keep black as the home
ground and accept a pink.

Both are built here so the choice is made by looking:
    ink-*      garnet + black on white       <- the honest garnet
    dark-*     the same marks inverted       <- garnet swapped for its passing shade

WHY BASELINE, NOT KNOCKOUT
--------------------------
Requested explicitly. Baseline is the round-4 mark: two outlined squares, strokes
simply crossing, nothing stating which is in front. It reads as "a set of
overlapping squares" where knockout reads as "interlocking".

Two colours change that calculus, though, and this is the round's actual argument.
Knockout needed a background-coloured gap to say which square was in front. With
two DIFFERENT ink colours, the front square is stated by colour alone — garnet
crosses black, and the eye resolves the order without any gap being cut. The
crossing stops being mud because the two lines are no longer the same colour.

So baseline-in-two-colours may get knockout's ordering for free, at baseline's
lower ink. Tested rather than assumed.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

# ---- the palette
# Garnet on white, measured. #7B1E3C is the wine-leaning garnet: 10.03:1 on white,
# unmistakably garnet rather than a bright red, and it holds its hue when printed.
GARNET = "#7B1E3C"
GARNET_DEEP = "#5C0A18"       # 13.89:1 on white — nearly black-red, for the ink pair
BLACK = "#10131a"             # the site's own --panel, not pure #000: pure black on
                              # white is harsher than any print ink and reads cheap
PAPER = "#ffffff"
# For the dark inversion, garnet cannot come along. #C2334D is the shade that clears
# 3:1 on black (3.67:1) while staying in the garnet family as far as it can.
GARNET_ON_DARK = "#C2334D"
INK_ON_DARK = "#e6e9ef"
BG_D = "#08090c"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round9")
SANS_ATTR = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"
W = 2.5

# Both grounds are explicit per-variant rather than themed, because this round is a
# comparison OF grounds. The chosen mark gets a themed build in the next round.


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
# baseline geometry, held constant. Only colour and colour ORDER change.
#   rear  rect 3,3   18x18 rx2
#   front rect 11,11 18x18 rx2

def _pair(rear_col, front_col, rx=2, radius_attr=True):
    """The baseline mark with an explicit rear and front colour.

    No knockout gap anywhere in this round. The claim under test is that two
    different ink colours state the order by themselves, which is what a real
    two-colour print does — the second pass sits visibly on the first.
    """
    r = f' rx="{rx}"' if radius_attr else ""

    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="3" y="3" width="18" height="18"{r} fill="none"'
            f' stroke="{rear_col}" stroke-width="{W}"/>',
            f'<rect x="11" y="11" width="18" height="18"{r} fill="none"'
            f' stroke="{front_col}" stroke-width="{W}"/>',
        ])
    return g


def _pair_solid(rear_col, front_col, front_fill):
    """Rear outlined, front outlined AND filled with paper.

    The cheapest possible occlusion: the front square carries an opaque paper fill,
    so it covers the rear outline wherever they meet. No knockout stroke to keep in
    sync with the theme, no mixed weights, and the crossing region disappears
    entirely. This is how a two-colour print actually behaves — the second plate is
    opaque.
    """
    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="3" y="3" width="18" height="18" rx="2" fill="none"'
            f' stroke="{rear_col}" stroke-width="{W}"/>',
            f'<rect x="11" y="11" width="18" height="18" rx="2" fill="{front_fill}"'
            f' stroke="{front_col}" stroke-width="{W}"/>',
        ])
    return g


RIVALS = {
    # ---- garnet + black on paper: the honest garnet
    "ink-garnet-front": (_pair(BLACK, GARNET),
                         "PAPER · black rear, GARNET front — garnet is the newer mark"),
    "ink-garnet-rear": (_pair(GARNET, BLACK),
                        "PAPER · garnet rear, black front — black is the newer mark"),
    "ink-occluded": (_pair_solid(BLACK, GARNET, PAPER),
                     "PAPER · garnet front OPAQUE — order total, crossing gone"),
    "ink-occluded-rev": (_pair_solid(GARNET, BLACK, PAPER),
                         "PAPER · black front opaque over garnet"),
    "ink-square": (_pair(BLACK, GARNET, rx=0, radius_attr=False),
                   "PAPER · square corners — a plate or a seal, not a UI card"),
    "ink-deep": (_pair(GARNET_DEEP, GARNET, rx=2),
                 "PAPER · two garnets, deep rear + garnet front — one hue, two values"),
    "ink-mono-black": (_pair(BLACK, BLACK),
                       "PAPER · black only — the control, is garnet earning anything?"),
    # ---- the dark inversion: garnet cannot come, so this is its passing shade
    "dark-garnet-front": (_pair(INK_ON_DARK, GARNET_ON_DARK),
                          "DARK · ink rear, #C2334D front — garnet pushed to clear 3:1"),
    "dark-garnet-rear": (_pair(GARNET_ON_DARK, INK_ON_DARK),
                         "DARK · #C2334D rear, ink front"),
    "dark-true-garnet": (_pair(INK_ON_DARK, GARNET),
                         "DARK · TRUE garnet #7B1E3C on black — 1.98:1, FAILS, shown as proof"),
}

SIZES = [16, 22, 32, 64, 128]
NAME = "doublegate"
TAG = "reviewed before it is remembered"


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n{geom("  ")}\n</svg>\n')


def mono(geom, desc):
    """One-colour fallback. A two-colour mark must still work in a single ink —
    fax, embossing, laser engraving, a partner's monochrome footer."""
    g = geom("  ")
    for c in (GARNET, GARNET_DEEP, GARNET_ON_DARK, BLACK, INK_ON_DARK):
        g = g.replace(f'"{c}"', '"currentColor"')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}" color="{BLACK}">\n'
            f'  <title>{NAME}</title>\n  <desc>{desc} Monochrome.</desc>\n{g}\n</svg>\n')


def wordmark(geom, desc, dark):
    name_c = INK_ON_DARK if dark else BLACK
    tag_c = "#97a1b2" if dark else "#55606f"
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 120" width="720"'
            f' height="120" role="img" aria-label="{NAME} — {TAG}">\n  <title>{NAME}</title>\n'
            f'  <desc>{desc}</desc>\n  <style>\n'
            f'    .wm {{ font-family: {SANS_ATTR}; }}\n'
            f'    .name {{ font-size: 54px; font-weight: 650; letter-spacing: -1.2px;'
            f' fill: {name_c}; }}\n'
            f'    .tag {{ font-size: 20px; fill: {tag_c}; }}\n'
            '  </style>\n'
            '  <g transform="translate(14 12) scale(2.0)">\n'
            f'{geom("    ")}\n  </g>\n'
            f'  <text class="wm name" x="112" y="60">{NAME}</text>\n'
            f'  <text class="wm tag"  x="114" y="92">{TAG}</text>\n</svg>\n')


def sz(svg, px):
    return re.sub(r'width="32" height="32"', f'width="{px}" height="{px}"', svg, count=1)


def preview(assets):
    def pane(dark_pane):
        bg = BG_D if dark_pane else PAPER
        fg = INK_ON_DARK if dark_pane else BLACK
        out = []
        for key, (lg, wm, mo, blurb) in assets.items():
            if key.startswith("dark-") != dark_pane:
                continue
            m_ = mo.replace(f'color="{BLACK}"', f'color="{INK_ON_DARK}"') if dark_pane else mo
            ladder = "".join(f'<div class="s"><div class="h">{sz(lg, px)}</div><i>{px}</i></div>'
                             for px in SIZES)
            ladder += ('<div class="s" style="margin-left:16px"><div class="h">'
                       f'{sz(m_, 64)}</div><i>1 ink</i></div>')
            out.append(f'<h3>{key}<em>{blurb}</em></h3><div class="row">{ladder}</div>'
                       f'<div class="lock">{wm}</div>')
        head = "DARK — the inversion (true garnet cannot come)" if dark_pane \
            else "PAPER — garnet's real home ground"
        return (f'<section style="background:{bg};color:{fg}">'
                f'<h2>{head}</h2>' + "".join(out) + "</section>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>doublegate — baseline in garnet and black</title>
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
        lg, wm, mo = logo(geom, desc), wordmark(geom, desc, dark), mono(geom, desc)
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
        h = 140 + len(RIVALS) * 300      # derived from the rival count, never hardcoded
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                        f' --virtual-time-budget=4000 --screenshot={OUT}/preview.png'
                        f' --window-size=1000,{h} {OUT}/preview.html 2>/dev/null'], check=False)
        for key, (lg, _w, _m, _b) in assets.items():
            ground = BG_D if key.startswith("dark-") else PAPER
            cells = "".join('<div style="display:flex;align-items:center;justify-content:center;'
                            f'width:150px;height:150px">{sz(lg, px)}</div>' for px in (16, 32, 128))
            p = os.path.join(OUT, f".one-{key}.html")
            open(p, "w").write(f'<!doctype html><body style="margin:0;background:{ground};'
                               f'display:flex">{cells}</body>')
            subprocess.run(["bash", "-c",
                            f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars'
                            f' --virtual-time-budget=2500 --screenshot={OUT}/one-{key}.png'
                            f' --window-size=460,155 {p} 2>/dev/null'], check=False)
            os.remove(p)

    print(f"{len(RIVALS)} variants -> {OUT}\n")
    print("why this round is on PAPER: garnet is a dark red and 3:1 (WCAG 1.4.11) is")
    print("the threshold for a graphical object. Nothing that still reads as garnet")
    print("clears it on #08090c.\n")
    print(f"  {'hex':<10}{'on #08090c':>11}{'on white':>10}   {'':<12} note")
    rows = [(GARNET_DEEP, "very deep garnet"), (GARNET, "GARNET — chosen for paper"),
            ("#8B1A2B", "brighter garnet"), ("#9B2242", "raspberry garnet"),
            ("#A52A45", "light garnet"), (GARNET_ON_DARK, "pushed to clear 3:1 on black"),
            (BLACK, "BLACK — the site's --panel"), (INK_ON_DARK, "ink on dark")]
    for h, note in rows:
        cd, cl = contrast(h, BG_D), contrast(h, PAPER)
        v = "PASS both" if min(cd, cl) >= 3 else (
            f"fails dark" if cd < 3 else "fails white")
        print(f"  {h:<10}{cd:>10.2f}:1{cl:>9.2f}:1   {v:<12} {note}")
    print("\nthe fork, stated rather than buried: choosing garnet makes the identity's")
    print("home ground LIGHT and the dark site its inversion. Keeping black as home")
    print("means accepting a pink (#C2334D) instead of a garnet.")
    print("\nno knockout gaps in this round — the claim under test is that two different")
    print("ink colours state which square is in front on their own.")


if __name__ == "__main__":
    main()
