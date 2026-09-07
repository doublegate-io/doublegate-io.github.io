#!/usr/bin/env python3
"""Round 10 — `ink-square` in granat (navy) and its partners.

Run:      python3 assets/gate-v2/build10.py
Measure:  CHROME_PATH=... node assets/gate-v2/measure10.js
Audit:    node assets/gate-v2/audit-geometry.js assets/gate-v2/round10/logo-*.svg
Read:     python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
            assets/gate-v2/round10/one-*.png

GRANAT BEHAVES BETTER THAN GARNET, AND FOR A STRUCTURAL REASON
--------------------------------------------------------------
Garnet failed because a dark red must brighten into a pink before it clears 3:1 on
black, so the colour could not survive the trip. Navy has an escape garnet did not:
a navy and a mid blue are the SAME hue at two values, so the pair can swap roles
between grounds and the identity still reads as blue in both places.

Navy alone cannot sit on the dark site — measured on #08090c:

    #0F172E near-black 1.12:1   #1D3461 muted      1.63:1
    #0A1F44 granat     1.23:1   #1B2F6B royal      1.58:1
    #172554 blue 950   1.35:1   #1E3A8A blue 800   1.92:1
    #12275C brighter   1.39:1   #1E40AF blue 700   2.28:1

All fail, exactly as the garnets did. But on white #0A1F44 measures 16.25:1, which
is better than any garnet managed, and navy-on-paper is the more established
institutional pairing anyway — ledger covers, passport boards, bank cheques, court
bindings.

THE PAIR THAT SURVIVES BOTH GROUNDS
-----------------------------------
Of every lighter blue tested, exactly one clears 3:1 on BOTH grounds:

    #3b82f6  blue 500   dark 5.41:1   white 3.68:1   <- the only one
    #60a5fa  blue 400   dark 7.83:1   white 2.54:1
    #0ea5e9  sky 500    dark 7.18:1   white 2.77:1
    #38bdf8  sky 400    dark 9.29:1   white 2.14:1
    #22d3ee  cyan 400   dark 11.02:1  white 1.81:1
    #818cf8  indigo 400 dark 6.67:1   white 2.98:1   (misses by 0.02)

So #3b82f6 is load-bearing: it is the one blue that can appear unchanged wherever the
mark goes, which means the ROLE swap can carry the theme instead of a colour swap.
    on paper  navy #0A1F44 rear, blue #3b82f6 front   — navy is the weight
    on dark   blue #3b82f6 rear, ink #e6e9ef front    — navy drops out, blue stays

That is materially better than round 9's garnet plan, where the brand colour itself
had to change between grounds.

THE TWO INKS ALSO HAVE TO SEPARATE FROM EACH OTHER
--------------------------------------------------
The squares cross, so the two strokes touch. Contrast against the ground is not
enough; they need contrast against one another or the crossing greys out.

    navy vs #3b82f6   4.42:1        navy vs #38bdf8   7.59:1
    navy vs #0ea5e9   5.86:1        navy vs #22d3ee   8.99:1
    navy vs #60a5fa   6.39:1

4.42:1 is comfortable — well past the 1.5:1 floor for adjacent graphical elements
and past 3:1 too. Same-hue pairs are the risk case here and this one clears it.

A SECOND HUE, BECAUSE NAVY + BLUE IS ONE SIGNAL
-----------------------------------------------
Two values of one hue read as one thing in two states, which is arguably right for
two gates. But it gives up the chance to say the two gates are DIFFERENT KINDS of
check. Warm counterpoints that clear 3:1 on both grounds and 3:1 against navy:

    #B45F06 copper      dark 4.34:1  white 4.58:1  vs-navy 3.54:1
    #ea580c orange 600  dark 5.59:1  white 3.56:1  vs-navy 4.57:1
    #d97706 amber 600   dark 6.25:1  white 3.19:1  vs-navy 5.10:1
    #b45309 amber 700   dark 3.96:1  white 5.02:1  vs-navy 3.24:1

Copper is the pick to test: navy and copper is a real institutional pairing (ledger
board with copper foil, naval instruments, bank fittings) rather than a UI accent,
and it is the most balanced of the four across both grounds.

Excluded on meaning, not contrast: emerald #059669 passes everything (5.28/3.77,
vs-navy 4.31) but green next to blue reads pass/info, and these two squares are
sequential stages rather than a state and its status.

GEOMETRY IS FIXED AT ink-square
-------------------------------
Round 9's winner and the best-measured mark of 81: baseline geometry with SQUARE
corners, 24 separating scanlines at ink 0.336. Square corners are why it reads as a
plate or a seal instead of a UI card. Nothing about the shape changes here — this
round is colour only, so the comparison is clean.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

# ---- the palette, all values measured before use
NAVY = "#0A1F44"          # granat. 16.25:1 on white. Cannot sit on the dark ground.
NAVY_SOFT = "#12275C"     # 14.28:1 on white — for the two-value navy pair
BLUE = "#3b82f6"          # blue 500. THE load-bearing value: 5.41:1 dark, 3.68:1 white
COPPER = "#B45F06"        # 4.34:1 dark, 4.58:1 white, 3.54:1 against navy
INK_D = "#e6e9ef"
PAPER = "#ffffff"
BG_D = "#08090c"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "round10")
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
# ink-square, held constant. Square corners, no rx. Colour is the only variable.

def _pair(rear_col, front_col):
    """ink-square with an explicit rear and front colour.

    Two traps hit while drawing this, both caught by measuring against round 9
    rather than trusting the eye:

    OFFSET. Coordinates must be 3,3 and 11,11 — an 8px offset on both axes. Drew it
    at 4,4 / 10,10 first, a 6px offset borrowed from round 6's `tight`, and it went
    to ink 0.531 with 20 scanlines. A tighter overlap puts more stroke inside the
    crossing region and costs both numbers.

    PRIMITIVE. Must be <rect>, not <path> with stroke-linejoin="miter". Identical
    box, identical stroke width, and the path version measured ink 0.406 against
    rect's 0.336 — the miter joins project past the corner and add paint that a
    rect's own corners do not. Round 9's ink-square is a rect; a faithful rebuild
    has to be one too.

    No knockout gap: round 9 established that two different ink colours state which
    square is in front on their own, at lower ink and with nothing to keep themed.
    """
    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="3" y="3" width="18" height="18" fill="none"'
            f' stroke="{rear_col}" stroke-width="{W}"/>',
            f'<rect x="11" y="11" width="18" height="18" fill="none"'
            f' stroke="{front_col}" stroke-width="{W}"/>',
        ])
    return g


def _themed_pair(rear_d, front_d, rear_l, front_l):
    """The role-swap build: one file, correct on both grounds.

    This is what granat makes possible and garnet did not. On paper navy carries the
    weight with blue in front; on dark navy drops out entirely and blue takes the
    rear with ink in front. The brand still reads as blue in both places because
    #3b82f6 is present either way — only its ROLE changes.
    """
    def g(i="  "):
        return "\n".join(f"{i}{ln}" for ln in [
            f'<rect x="3" y="3" width="18" height="18" fill="none" class="rear"'
            f' stroke-width="{W}"/>',
            f'<rect x="11" y="11" width="18" height="18" fill="none" class="front"'
            f' stroke-width="{W}"/>',
        ])
    return g, (rear_d, front_d, rear_l, front_l)


RIVALS = {
    # ---- paper: granat's home ground
    "ink-navy-blue": (_pair(NAVY, BLUE),
                      "PAPER · granat #0A1F44 rear, blue #3b82f6 front — the pair"),
    "ink-blue-navy": (_pair(BLUE, NAVY),
                      "PAPER · blue rear, granat front — granat is the newer mark"),
    "ink-navy-copper": (_pair(NAVY, COPPER),
                        "PAPER · granat + COPPER #B45F06 — two hues, two kinds of check"),
    "ink-copper-navy": (_pair(COPPER, NAVY),
                        "PAPER · copper rear, granat front"),
    # Kept as evidence, not as a candidate. The two navies are 1.14:1 against EACH
    # OTHER, so where the strokes cross they merge into one shape. Both clear the
    # ground easily (16.25:1 and 14.28:1) — proving ground contrast alone is not
    # enough for a mark whose elements touch.
    "ink-two-navy": (_pair(NAVY, NAVY_SOFT),
                     "PAPER · two navies at 1.14:1 INK-VS-INK — merges, shown as proof"),
    "ink-navy-only": (_pair(NAVY, NAVY),
                      "PAPER · granat alone, the control — does the 2nd colour earn it?"),
    # ---- dark: navy cannot come, so blue takes over
    "dark-blue-ink": (_pair(BLUE, INK_D),
                      "DARK · blue #3b82f6 rear, ink front — the role swap"),
    "dark-ink-blue": (_pair(INK_D, BLUE),
                      "DARK · ink rear, blue front"),
    "dark-navy-proof": (_pair(NAVY, BLUE),
                        "DARK · granat on black at 1.23:1 — FAILS WCAG, shown as proof"),
    "dark-blue-copper": (_pair(BLUE, COPPER),
                         "DARK · blue + copper, both clear 3:1 here"),
    # ---- the shippable one file
    "themed": (_themed_pair(BLUE, INK_D, NAVY, BLUE)[0],
               "THEMED · one file: navy+blue on paper, blue+ink on dark"),
}
# Register the themed variant's four colours. Kept in a module dict rather than as an
# attribute on the function so the type checker can see it.
THEMES = {RIVALS["themed"][0]: (BLUE, INK_D, NAVY, BLUE)}

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
    engraving, a partner's monochrome footer, a fax."""
    g = geom("  ")
    for c in (NAVY, NAVY_SOFT, BLUE, COPPER, INK_D):
        g = g.replace(f'"{c}"', '"currentColor"')
    g = re.sub(r'class="(rear|front)"', 'stroke="currentColor"', g)
    col = INK_D if dark else NAVY
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32"'
            f' height="32" role="img" aria-label="{NAME}" color="{col}">\n'
            f'  <title>{NAME}</title>\n  <desc>{desc} Monochrome.</desc>\n{g}\n</svg>\n')


def wordmark(geom, desc, dark):
    name_c = INK_D if dark else NAVY
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
        fg = INK_D if dark_pane else NAVY
        out = []
        for key, (lg, wm, mo, blurb) in assets.items():
            is_dark = key.startswith("dark-")
            if key == "themed":
                pass                        # themed appears in both panes
            elif is_dark != dark_pane:
                continue
            l_ = force(lg, light=not dark_pane)
            w_ = force(wm, light=not dark_pane)
            m_ = mo.replace(f'color="{NAVY}"', f'color="{INK_D}"') if dark_pane else mo
            ladder = "".join(f'<div class="s"><div class="h">{sz(l_, px)}</div><i>{px}</i></div>'
                             for px in SIZES)
            ladder += ('<div class="s" style="margin-left:16px"><div class="h">'
                       f'{sz(m_, 64)}</div><i>1 ink</i></div>')
            out.append(f'<h3>{key}<em>{blurb}</em></h3><div class="row">{ladder}</div>'
                       f'<div class="lock">{w_}</div>')
        head = ("DARK — granat drops out, blue #3b82f6 carries it"
                if dark_pane else "PAPER — granat's home ground")
        return (f'<section style="background:{bg};color:{fg}">'
                f'<h2>{head}</h2>' + "".join(out) + "</section>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>doublegate — granat and blue</title>
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
            dark_g = key.startswith("dark-") or key == "themed"
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
    print("granat (navy) on the two grounds — same story as garnet, all fail on black:")
    for h, n in [("#0F172E", "near-black"), (NAVY, "GRANAT — chosen"),
                 (NAVY_SOFT, "granat brighter"), ("#1B2F6B", "royal-leaning"),
                 ("#1E3A8A", "blue 800"), ("#1E40AF", "blue 700")]:
        cd, cl = contrast(h, BG_D), contrast(h, PAPER)
        print(f"  {h}  dark {cd:5.2f}:1  white {cl:5.2f}:1  "
              f"{'PASS both' if min(cd, cl) >= 3 else 'fails dark'}  {n}")

    print("\nbut navy has an escape garnet did not — ONE lighter blue clears both grounds,")
    print("so the ROLE swaps between themes while the colour itself stays put:")
    for h, n in [(BLUE, "BLUE 500 — load-bearing"), ("#60a5fa", "blue 400"),
                 ("#0ea5e9", "sky 500"), ("#38bdf8", "sky 400"), ("#22d3ee", "cyan 400"),
                 ("#818cf8", "indigo 400, misses by 0.02")]:
        cd, cl = contrast(h, BG_D), contrast(h, PAPER)
        print(f"  {h}  dark {cd:5.2f}:1  white {cl:5.2f}:1  "
              f"{'PASS both' if min(cd, cl) >= 3 else 'fails white'}  {n}")

    print("\nthe two inks TOUCH at the crossing, so they need separation from each other")
    print("as well as from the ground (1.5:1 floor for adjacent elements, 3:1 comfortable):")
    for h, n in [(BLUE, "blue 500"), (COPPER, "copper"), (NAVY_SOFT, "the softer navy")]:
        print(f"  granat vs {h}  {contrast(NAVY, h):5.2f}:1  {n}")

    print(f"\ncopper {COPPER} as a second HUE: dark {contrast(COPPER, BG_D):.2f}:1, "
          f"white {contrast(COPPER, PAPER):.2f}:1, vs-navy {contrast(COPPER, NAVY):.2f}:1")
    print("emerald #059669 passes every number but is excluded on MEANING: green beside")
    print("blue reads pass/info, and these squares are sequential stages not a status.")


if __name__ == "__main__":
    main()
