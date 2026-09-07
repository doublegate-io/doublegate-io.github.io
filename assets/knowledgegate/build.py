#!/usr/bin/env python3
"""KnowledgeGate mark candidates — one geometry source, four variants, full preview.

Run from the repo root:  python3 assets/knowledgegate/build.py
Writes logo/wordmark/social-card per variant plus preview.html covering every
size on both themes.

Variants, and the stance each takes:

  arch-book   The live two-arch gate, one arch, with an open book passing under it.
              Closest to the existing mark; the book is what the rename adds.
  posts-book  Two posts (first gate, second gate) holding a closed book.
              Keeps "two of something" countable, which the single arch loses.
  spine-book  The book IS the gate: red spine to pass, first line inside signed.
              Most literal about a library, least about admission.
  arches      Two arches, no book. The incumbent geometry under the new name,
              for the case where the book is judged too literal.

What the size ladder decided, so nobody re-litigates it from taste:
  - An arch with visible legs plus a book beneath reads as a lowercase "n" at
    16-22px. Fixed by making the book narrower than the arch span and leaving
    daylight between them, so the eye sees an object under a canopy.
  - Page fills used --ink (#e6e9ef), which is invisible on a light browser tab.
    Every ink element flips through prefers-color-scheme; that is the only theme
    mechanism that works inside a favicon SVG.
  - A book below ~22px survives only as a silhouette. Page lines are dropped
    from the small-size read rather than being drawn finer.
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

RED, GRN, DIM = "#fb7185", "#34d399", "#97a1b2"
INK_D, INK_L = "#e6e9ef", "#10131a"
BG_D, BG_L = "#08090c", "#ffffff"
HERE = os.path.dirname(os.path.abspath(__file__))
SANS = 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Inter, sans-serif'
# Same stack for a font-family="" attribute, where the inner quotes would end the
# attribute and produce markup that does not parse.
SANS_ATTR = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"

# The page fill and the spine notch both have to invert with the theme; a notch
# cut in the background colour would show as a dark bar on a white tab.
INK_STYLE = f"""  <style>
    .ink {{ fill: {INK_D}; }}
    .cut {{ stroke: {BG_D}; }}
    @media (prefers-color-scheme: light) {{
      .ink {{ fill: {INK_L}; }}
      .cut {{ stroke: {BG_L}; }}
    }}
  </style>"""


# ------------------------------------------------------------------ geometry
# Each returns markup on a 0 0 32 32 grid so one function can serve the favicon,
# the wordmark lockup and the social card at three different scales.

def g_arch_book(i="  "):
    # The arch is a bare canopy with no legs and the book is deliberately narrower
    # than the arch span, with daylight between the two. An arch whose span matches
    # the object below it reads as a lowercase "n": the curve becomes the shoulder
    # and the object becomes the stem. Narrow book + visible gap breaks that read.
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M2.5 15 a13.5 13.5 0 0 1 27 0" stroke="{RED}" stroke-width="3.4"'
        ' stroke-linecap="round" fill="none"/>',
        '<path d="M15.2 28.5 c-2.3 -2.6 -4.8 -3 -7.4 -2.2 v-6.6 c2.6 -0.8 5.1 -0.4 7.4 2.2 z"'
        ' class="ink"/>',
        f'<path d="M16.8 28.5 c2.3 -2.6 4.8 -3 7.4 -2.2 v-6.6 c-2.6 -0.8 -5.1 -0.4 -7.4 2.2 z"'
        f' fill="{GRN}"/>',
    ])


def g_posts_book(i="  "):
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M4.5 5 v22" stroke="{RED}" stroke-width="4" stroke-linecap="round" fill="none"/>',
        f'<path d="M27.5 5 v22" stroke="{GRN}" stroke-width="4" stroke-linecap="round" fill="none"/>',
        '<path d="M11 10.5 h10 a2 2 0 0 1 2 2 v7 a2 2 0 0 1 -2 2 h-10 a2 2 0 0 1 -2 -2'
        ' v-7 a2 2 0 0 1 2 -2 z" class="ink"/>',
        '<path d="M16 10.5 v11" class="cut" stroke-width="2.2" fill="none"/>',
    ])


def g_spine_book(i="  "):
    # Two lines, not three. At 16px a third line closed the gaps and the whole
    # mark filled in as a solid rectangle; two heavier lines keep visible gaps.
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M7.5 6 h14 a3.5 3.5 0 0 1 3.5 3.5 v13 a3.5 3.5 0 0 1 -3.5 3.5 h-14 z"'
        f' fill="none" stroke="{RED}" stroke-width="2.6" stroke-linejoin="round"/>',
        f'<path d="M7.5 6 v20" stroke="{RED}" stroke-width="4.5" stroke-linecap="round"/>',
        f'<path d="M12.5 12.5 h8.5" stroke="{GRN}" stroke-width="3" stroke-linecap="round"/>',
        f'<path d="M12.5 19.5 h5.5" stroke="{DIM}" stroke-width="3" stroke-linecap="round"/>',
    ])


def g_arches(i="  "):
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M 2 27 V 15.5 A 5.5 5.5 0 0 1 13 15.5 V 27" fill="none" stroke="{RED}"'
        ' stroke-width="3.5" stroke-linecap="round"/>',
        f'<path d="M 19 27 V 15.5 A 5.5 5.5 0 0 1 30 15.5 V 27" fill="none" stroke="{GRN}"'
        ' stroke-width="3.5" stroke-linecap="round"/>',
    ])


VARIANTS = {
    "arch-book": (g_arch_book,
                  "An open book passing beneath the gate arch. Reviewed before it is readable."),
    "posts-book": (g_posts_book,
                   "A closed book held between two gates: admission, then ratification."),
    "spine-book": (g_spine_book,
                   "A book whose spine is the gate; the first line inside is the signed one."),
    "arches": (g_arches,
               "Two separate gates: admission, then ratification. Nothing is readable "
               "until it passes both."),
}

SIZES = [16, 22, 32, 48, 64, 128]


# --------------------------------------------------------------- asset emit

def logo(geom, desc):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32"'
        ' role="img" aria-label="KnowledgeGate">\n'
        '  <title>KnowledgeGate</title>\n'
        f'  <desc>{desc}</desc>\n{INK_STYLE}\n{geom("  ")}\n</svg>\n'
    )


def wordmark(geom, desc):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 120" width="760" height="120"'
        ' role="img" aria-label="KnowledgeGate — reviewed before it is remembered">\n'
        '  <title>KnowledgeGate</title>\n'
        f'  <desc>{desc}</desc>\n'
        '  <style>\n'
        f'    .wm {{ font-family: {SANS}; }}\n'
        f'    .name {{ font-size: 54px; font-weight: 650; letter-spacing: -1.2px; fill: {INK_D}; }}\n'
        f'    .tag  {{ font-size: 20px; fill: {DIM}; }}\n'
        f'    .ink {{ fill: {INK_D}; }}\n'
        f'    .cut {{ stroke: {BG_D}; }}\n'
        '    @media (prefers-color-scheme: light) {\n'
        f'      .name {{ fill: {INK_L}; }}\n'
        '      .tag  { fill: #55606f; }\n'
        f'      .ink {{ fill: {INK_L}; }}\n'
        f'      .cut {{ stroke: {BG_L}; }}\n'
        '    }\n'
        '  </style>\n'
        '  <g transform="translate(14 12) scale(2.0)">\n'
        f'{geom("    ")}\n'
        '  </g>\n'
        '  <text class="wm name" x="112" y="60">KnowledgeGate</text>\n'
        '  <text class="wm tag"  x="114" y="92">reviewed before it is remembered</text>\n'
        '</svg>\n'
    )


def social_card(geom, desc):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630"'
        ' role="img" aria-label="KnowledgeGate — reviewed, signed, shared">\n'
        '  <title>KnowledgeGate</title>\n'
        f'  <desc>{desc}</desc>\n'
        f'  <style>.ink {{ fill: {INK_D}; }} .cut {{ stroke: {BG_D}; }}</style>\n'
        f'  <rect width="1200" height="630" fill="{BG_D}"/>\n'
        f'  <rect x="0" y="0" width="600" height="4" fill="{RED}"/>\n'
        f'  <rect x="600" y="0" width="600" height="4" fill="{GRN}"/>\n'
        '  <g transform="translate(104 226) scale(5.2)">\n'
        f'{geom("    ")}\n'
        '  </g>\n'
        f'  <text x="300" y="286" font-family="{SANS_ATTR}" font-size="72" font-weight="650"'
        f' letter-spacing="-1.6" fill="{INK_D}">KnowledgeGate</text>\n'
        f'  <text x="302" y="344" font-family="{SANS_ATTR}" font-size="29" fill="{DIM}">'
        "Your organization's AI knowledge, reviewed and shared</text>\n"
        '</svg>\n'
    )


def sz(svg, px):
    return re.sub(r'width="32" height="32"', f'width="{px}" height="{px}"', svg, count=1)


def force(svg, light):
    """Resolve the media query by hand, in BOTH directions.

    A browser applies prefers-color-scheme from the OS and headless Chrome defaults
    to *light*, so a dark preview pane that leans on the media query renders dark
    ink on dark ground — the mark then looks like it is missing elements when it is
    not. Both branches have to be resolved explicitly for the sheet to be evidence.
    """
    if light:
        return (svg.replace(f"fill: {INK_D}", f"fill: {INK_L}")
                   .replace(f"stroke: {BG_D}", f"stroke: {BG_L}")
                   .replace(f'fill="{INK_D}"', f'fill="{INK_L}"'))
    return re.sub(r"@media \(prefers-color-scheme: light\) \{.*?\n\s*\}\n", "", svg, flags=re.S)


def preview(assets):
    def pane(light):
        bg, fg = (BG_L, INK_L) if light else (BG_D, INK_D)
        blocks = []
        for name, (lg, wm) in assets.items():
            ladder = "".join(
                f'<div class="s"><div class="h">{sz(force(lg, light), px)}</div>'
                f'<i>{px}</i></div>' for px in SIZES)
            lock = f'<div class="lock">{force(wm, light)}</div>'
            blocks.append(f'<h3>{name}</h3><div class="row">{ladder}</div>{lock}')
        return (f'<section style="background:{bg};color:{fg}">'
                f'<div class="tag">{"light" if light else "dark"}</div>'
                f'{"".join(blocks)}</section>')

    css = """
    body{margin:0;font-family:ui-sans-serif,system-ui,sans-serif}
    section{padding:26px 32px}
    .tag{font:11px ui-monospace,monospace;opacity:.55;letter-spacing:.08em;
         text-transform:uppercase;margin-bottom:20px}
    h3{font:600 14px ui-monospace,monospace;margin:26px 0 10px;letter-spacing:.02em}
    .row{display:flex;align-items:flex-end;gap:26px}
    .s{text-align:center}
    .h{display:flex;align-items:flex-end;justify-content:center;height:132px}
    i{display:block;font:10px ui-monospace,monospace;opacity:.45;font-style:normal;margin-top:6px}
    .lock{margin:14px 0 4px}.lock svg{width:420px;height:auto}
    """
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<title>KnowledgeGate — mark candidates</title><style>{css}</style></head>'
            f'<body>{pane(False)}{pane(True)}</body></html>\n')


if __name__ == "__main__":
    assets = {}
    for name, (geom, desc) in VARIANTS.items():
        lg, wm, sc = logo(geom, desc), wordmark(geom, desc), social_card(geom, desc)
        for text, suffix in ((lg, "logo"), (wm, "wordmark"), (sc, "social-card")):
            ET.fromstring(text)  # never write markup that will not parse
            open(os.path.join(HERE, f"{suffix}-{name}.svg"), "w").write(text)
        assets[name] = (lg, wm)

    open(os.path.join(HERE, "preview.html"), "w").write(preview(assets))

    chrome = os.environ.get("CHROME_PATH") or os.path.expanduser(
        "~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome")
    if os.path.exists(chrome):
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars '
                        f'--virtual-time-budget=4000 --screenshot={HERE}/preview.png '
                        f'--window-size=900,2000 {HERE}/preview.html 2>/dev/null'], check=False)
    print(f"{len(VARIANTS)} variants x 3 assets -> {HERE}")
