#!/usr/bin/env python3
"""Marks for the naming shortlist — one geometry source per candidate name.

Run from the repo root:  python3 assets/naming-options/build.py
Writes a logo and a wordmark per candidate plus preview.html with the full size
ladder on both themes.

These are not four variants of one brand. Each mark belongs to a different
*name* on the shortlist in the design repo's docs/research/15-naming-options.md,
so the comparison being made here is between metaphors, not between drafts.

Every geometry rule the KnowledgeGate ladder established is carried over rather
than rediscovered — see assets/knowledgegate/README.md:
  - ink fills must flip through prefers-color-scheme or they vanish on a light tab
  - an arch whose span matches the object beneath it reads as a lowercase "n"
  - three thin parallel lines fill in solid at 16px; two heavier ones survive
  - font-family in an *attribute* cannot contain quotes or the SVG will not parse
"""
import os
import re
import subprocess
import xml.etree.ElementTree as ET

RED, GRN, DIM, AMB = "#fb7185", "#34d399", "#97a1b2", "#fbbf24"
INK_D, INK_L = "#e6e9ef", "#10131a"
BG_D, BG_L = "#08090c", "#ffffff"
HERE = os.path.dirname(os.path.abspath(__file__))
SANS_ATTR = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"

INK_STYLE = f"""  <style>
    .ink {{ fill: {INK_D}; }}
    .ink-s {{ stroke: {INK_D}; }}
    .cut {{ stroke: {BG_D}; }}
    @media (prefers-color-scheme: light) {{
      .ink {{ fill: {INK_L}; }}
      .ink-s {{ stroke: {INK_L}; }}
      .cut {{ stroke: {BG_L}; }}
    }}
  </style>"""


# ------------------------------------------------------------------ geometry

def g_accession(i="  "):
    """A shelf, and one item being pushed into line with it.

    Accession is the moment an item joins the collection, so the mark is the
    instant before that: accessioned spines standing on a shelf rule, one more
    still outside it and coloured as not-yet-admitted.

    Two spines, not three. Three equal-width bars on a baseline is the universal
    bar-chart/analytics icon and a first render read as exactly that. Two spines
    of clearly unequal height plus a tilted arrival is a shelf, because a chart
    does not have a tilted bar.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 26.5 h26" stroke="{GRN}" stroke-width="2.8" stroke-linecap="round"/>',
        '<rect x="5" y="8.5" width="5.4" height="15.5" rx="1.3" class="ink"/>',
        '<rect x="12.2" y="13" width="5.4" height="11" rx="1.3" class="ink"/>',
        f'<rect x="22" y="6" width="5.4" height="14" rx="1.3" fill="{RED}"'
        ' transform="rotate(14 24.7 13)"/>',
    ])


def g_assay_office(i="  "):
    """A hallmark punch: the struck mark itself, not a shield around a tick.

    The first draft was a shield containing a tick, which is the security-software
    icon every OS ships — vision named it "verified/security" unprompted. A real
    hallmark is a *punch*: an outline whose shape identifies the office, with the
    fineness figure struck inside it. So the container is a lozenge (the UK
    fineness-mark shape) and the content is a struck bar, not a checkmark.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M16 3.5 l12.5 12.5 l-12.5 12.5 l-12.5 -12.5 z" fill="none" stroke="{RED}"'
        ' stroke-width="2.8" stroke-linejoin="round"/>',
        f'<path d="M11 16 h10" stroke="{GRN}" stroke-width="3.2" stroke-linecap="round"/>',
        '<path d="M13 11 h6" class="ink-s" stroke-width="2.4" stroke-linecap="round"/>',
        '<path d="M13 21 h6" class="ink-s" stroke-width="2.4" stroke-linecap="round"/>',
    ])


def g_pound_lock(i="  "):
    """A canal pound lock seen from above: two gates, a chamber, a load inside.

    The whole idea of a pound lock is that both gates are never open at once.
    First draft filled in at 16px — the boat was a solid arrow nearly touching
    both gates, and the negative space closed. The chamber walls are dropped and
    the load is a plain block with real daylight on both sides, so what survives
    downscaling is gate / gap / block / gap / gate.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M3 5.5 v21" stroke="{RED}" stroke-width="4" stroke-linecap="round"/>',
        f'<path d="M29 5.5 v21" stroke="{GRN}" stroke-width="4" stroke-linecap="round"/>',
        '<rect x="12" y="11" width="8" height="10" rx="1.6" class="ink"/>',
    ])


def g_diode(i="  "):
    """The diode glyph, vertical: a triangle firing into a bar it cannot cross.

    Horizontal, this is the play button — the single most-used glyph in software.
    Rotated to fire upward it stops being a transport control, since nothing plays
    upward.

    The leads are asymmetric on purpose. With a centred lead above and below, the
    measured pass found zero horizontal scanlines separating any two elements: a
    vertical stalk running the full height means every row it crosses is one
    unbroken run. Offsetting the upper lead gives the mark a horizontal break.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M16 30 v-5.5" stroke="{DIM}" stroke-width="2.8" stroke-linecap="round"/>',
        f'<path d="M7.5 24 l8.5 -13 l8.5 13 z" fill="{RED}"/>',
        f'<path d="M6.5 9 h19" stroke="{GRN}" stroke-width="3.8" stroke-linecap="round"/>',
        f'<path d="M9 4 h14" stroke="{DIM}" stroke-width="2.8" stroke-linecap="round"/>',
    ])


def g_librarian(i="  "):
    """An open book with a date stamp struck across its corner.

    The stamp was a circle with a bar through it, which is the prohibition sign —
    "no entry", the opposite of what this mark means. It is now a rotated stamp
    block overlapping the page corner: something pressed onto the book rather than
    a symbol placed beside it.

    Measured weakest of the six at 16px (6 separating scanlines against 21 for the
    porter hatch), and the reason is countable rather than aesthetic: ten distinct
    colours in a 16x16 field, because a rotated outline antialiases into several
    intermediate tones. The stamp is heavier and squarer here to cut that down,
    but the mark is inherently the busiest in the set.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<path d="M15.1 28 c-2.8 -3 -6.4 -3.4 -9.6 -2.4 v-11.5 c3.2 -1 6.8 -0.6 9.6 2.4 z"'
        ' class="ink"/>',
        f'<path d="M16.9 28 c2.8 -3 6.4 -3.4 9.6 -2.4 v-11.5 c-3.2 -1 -6.8 -0.6 -9.6 2.4 z"'
        f' fill="{GRN}"/>',
        f'<rect x="16" y="3" width="12" height="9" rx="1.5" fill="none" stroke="{AMB}"'
        ' stroke-width="2.6"/>',
        f'<path d="M19 7.5 h6" stroke="{AMB}" stroke-width="2.4" stroke-linecap="round"/>',
    ])


def g_porter(i="  "):
    """A lodge hatch with something presented at it.

    The receptionist family drawn as the place rather than the person — a figure
    at a desk cannot survive 16px, a hatch can. First draft was a bare arch over a
    rule and read as a letter U. The counter now runs the full width and an item
    sits on it, which an arch alone does not have.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M5 21 v-8 a11 11 0 0 1 22 0 v8" fill="none" stroke="{RED}"'
        ' stroke-width="2.8" stroke-linejoin="round"/>',
        f'<path d="M2.5 24.5 h27" stroke="{GRN}" stroke-width="3.4" stroke-linecap="round"/>',
        '<rect x="12.5" y="14.5" width="7" height="7" rx="1.4" class="ink"/>',
    ])


CANDIDATES = {
    "accession": (g_accession, "Accession",
                  "A shelf of accessioned items and one still outside the collection. "
                  "Admission is the moment it joins the line."),
    "assayoffice": (g_assay_office, "AssayOffice",
                    "A hallmark struck into a shield: tested by an independent office, "
                    "and the mark says which one."),
    "poundlock": (g_pound_lock, "PoundLock",
                  "A canal pound lock from above: a gate at each end, never both open, "
                  "with the load held in the chamber between them."),
    "knowledgediode": (g_diode, "KnowledgeDiode",
                       "The diode glyph: passes one direction, blocked in the other by "
                       "construction rather than by policy."),
    "agentlibrarian": (g_librarian, "AgentLibrarian",
                       "An open book with a stamp struck across it: read only after "
                       "someone accountable signed it in."),
    "knowledgeporter": (g_porter, "KnowledgePorter",
                        "A porter's lodge hatch: you present what you have at the desk, "
                        "and the desk decides."),
}

SIZES = [16, 22, 32, 48, 64, 128]


def logo(geom, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32"'
            ' role="img" aria-label="mark">\n  <title>mark</title>\n'
            f'  <desc>{desc}</desc>\n{INK_STYLE}\n{geom("  ")}\n</svg>\n')


def wordmark(geom, name, desc):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 120" width="820"'
            f' height="120" role="img" aria-label="{name}">\n  <title>{name}</title>\n'
            f'  <desc>{desc}</desc>\n'
            '  <style>\n'
            f'    .wm {{ font-family: {SANS_ATTR}; }}\n'
            f'    .name {{ font-size: 54px; font-weight: 650; letter-spacing: -1.2px;'
            f' fill: {INK_D}; }}\n'
            f'    .tag {{ font-size: 20px; fill: {DIM}; }}\n'
            f'    .ink {{ fill: {INK_D}; }}\n'
            f'    .ink-s {{ stroke: {INK_D}; }}\n'
            f'    .cut {{ stroke: {BG_D}; }}\n'
            '    @media (prefers-color-scheme: light) {\n'
            f'      .name {{ fill: {INK_L}; }}\n'
            '      .tag { fill: #55606f; }\n'
            f'      .ink {{ fill: {INK_L}; }}\n'
            f'      .ink-s {{ stroke: {INK_L}; }}\n'
            f'      .cut {{ stroke: {BG_L}; }}\n'
            '    }\n'
            '  </style>\n'
            '  <g transform="translate(14 12) scale(2.0)">\n'
            f'{geom("    ")}\n'
            '  </g>\n'
            f'  <text class="wm name" x="112" y="60">{name}</text>\n'
            '  <text class="wm tag"  x="114" y="92">reviewed before it is remembered</text>\n'
            '</svg>\n')


def sz(svg, px):
    return re.sub(r'width="32" height="32"', f'width="{px}" height="{px}"', svg, count=1)


def force(svg, light):
    """Resolve the media query by hand, in BOTH directions.

    This is not cosmetic. A browser applies prefers-color-scheme from the OS, and
    headless Chrome defaults to *light* — so a dark-background preview pane that
    relies on the media query renders dark ink on dark ground and the mark looks
    like it is missing elements. The first render of this sheet did exactly that
    and a vision read reported the spines as "dark grey", which was true and was
    an artifact of the harness, not of the mark.
    """
    if light:
        return (svg.replace(f"fill: {INK_D}", f"fill: {INK_L}")
                   .replace(f"stroke: {INK_D}", f"stroke: {INK_L}")
                   .replace(f"stroke: {BG_D}", f"stroke: {BG_L}"))
    # Strip the light branch so the dark values are the only ones left.
    return re.sub(r"@media \(prefers-color-scheme: light\) \{.*?\n\s*\}\n", "", svg, flags=re.S)


def preview(assets):
    def pane(light):
        bg, fg = (BG_L, INK_L) if light else (BG_D, INK_D)
        out = []
        for key, (lg, wm, name) in assets.items():
            l_, w_ = force(lg, light), force(wm, light)
            ladder = "".join(f'<div class="s"><div class="h">{sz(l_, px)}</div><i>{px}</i></div>'
                             for px in SIZES)
            out.append(f'<h3>{name}</h3><div class="row">{ladder}</div>'
                       f'<div class="lock">{w_}</div>')
        return (f'<section style="background:{bg};color:{fg}">'
                f'<div class="tag">{"light" if light else "dark"}</div>{"".join(out)}</section>')

    css = """body{margin:0;font-family:ui-sans-serif,system-ui,sans-serif}
    section{padding:26px 32px}
    .tag{font:11px ui-monospace,monospace;opacity:.55;letter-spacing:.08em;
         text-transform:uppercase;margin-bottom:20px}
    h3{font:600 14px ui-monospace,monospace;margin:26px 0 10px}
    .row{display:flex;align-items:flex-end;gap:26px}
    .s{text-align:center}
    .h{display:flex;align-items:flex-end;justify-content:center;height:132px}
    i{display:block;font:10px ui-monospace,monospace;opacity:.45;font-style:normal;margin-top:6px}
    .lock{margin:14px 0 4px}.lock svg{width:440px;height:auto}"""
    return (f'<!doctype html><html><head><meta charset="utf-8">'
            f'<title>Naming shortlist — marks</title><style>{css}</style></head>'
            f'<body>{pane(False)}{pane(True)}</body></html>\n')


if __name__ == "__main__":
    assets = {}
    for key, (geom, name, desc) in CANDIDATES.items():
        lg, wm = logo(geom, desc), wordmark(geom, name, desc)
        for text, kind in ((lg, "logo"), (wm, "wordmark")):
            ET.fromstring(text)
            open(os.path.join(HERE, f"{kind}-{key}.svg"), "w").write(text)
        assets[key] = (lg, wm, name)

    open(os.path.join(HERE, "preview.html"), "w").write(preview(assets))

    chrome = os.environ.get("CHROME_PATH") or os.path.expanduser(
        "~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome")
    if os.path.exists(chrome):
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars '
                        f'--virtual-time-budget=4000 --screenshot={HERE}/preview.png '
                        f'--window-size=930,2700 {HERE}/preview.html 2>/dev/null'], check=False)
    print(f"{len(CANDIDATES)} candidate marks -> {HERE}")
