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


def g_countersign(i="  "):
    """Two signature strokes stacked on a document, one above the other.

    Two failed attempts on the same defect, so the diagnosis is structural rather
    than a matter of nudging: **any two strokes that meet at a low vertex read as a
    tick**, regardless of which direction each one travels. Crossing them did not
    help, because the eye still resolves the lower junction first.

    So stop drawing a crossing. A real countersignature is not two crossed pen
    strokes — it is two signatures on the same document, one under the other, on
    their own rule. That is what this now draws, and a stacked pair on two rules
    cannot collapse into a checkmark because there is no vertex.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M4 12 c3 -4 5.5 -3.5 7 0 c1.5 3.5 4 4 7.5 -1" fill="none"'
        f' stroke="{RED}" stroke-width="2.8" stroke-linecap="round"/>',
        f'<path d="M4 15.5 h24" stroke="{DIM}" stroke-width="1.8" stroke-linecap="round"'
        ' opacity="0.5"/>',
        f'<path d="M4 24 c3 -4 5.5 -3.5 7 0 c1.5 3.5 4 4 7.5 -1" fill="none"'
        f' stroke="{GRN}" stroke-width="2.8" stroke-linecap="round"/>',
        f'<path d="M4 27.5 h24" stroke="{DIM}" stroke-width="1.8" stroke-linecap="round"'
        ' opacity="0.5"/>',
    ])


def g_holdshelf(i="  "):
    """Items on a shelf, with a gate line running past the shelf on both sides.

    Second attempt at the barrier. Making it thicker did not work: a thick vertical
    bar standing among vertical bars is still read as another bar, so the whole mark
    stayed a bar chart. Weight was the wrong variable.

    The barrier now differs in *kind* rather than degree — it runs above the tops of
    the spines and below the shelf rule, which no book on a shelf can do. That is
    what makes it a gate instead of a taller item.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M2.5 25.5 h14" stroke="{DIM}" stroke-width="2.4" stroke-linecap="round"/>',
        '<rect x="3.5" y="12" width="4.6" height="11" rx="1.2" class="ink"/>',
        '<rect x="9.6" y="15" width="4.6" height="8" rx="1.2" class="ink"/>',
        f'<path d="M19 1.5 v29" stroke="{RED}" stroke-width="3.4" stroke-linecap="round"/>',
        f'<path d="M22 25.5 h7.5" stroke="{DIM}" stroke-width="2.4" stroke-linecap="round"/>',
        f'<rect x="24" y="13" width="4.6" height="10" rx="1.2" fill="{GRN}"/>',
    ])


def g_correctorium(i="  "):
    """Two leaves side by side, the second bearing a correction stroke.

    A monastic scriptorium split the work: a copyist reproduced the exemplar, and a
    *corrector* — a different person — collated the new copy against it before
    release. That is the reviewer-is-never-the-author invariant as a working
    institution, so the mark draws the collation: exemplar on the left, copy on the
    right, and the corrector's mark on the copy.

    Both leaves are outlines. A solid left leaf measured ink 0.566 at 16px, well
    past the 0.45 threshold where a mark starts closing up — a filled rectangle
    covering a third of the field is simply too much paint. Outlines carry the same
    two-objects reading at a fraction of the coverage. The exemplar is still
    distinguished from the copy, by colour and by having no correction on it.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        '<rect x="3.5" y="6" width="10" height="20" rx="1.8" fill="none" class="ink-s"'
        ' stroke-width="2.4"/>',
        f'<rect x="18.5" y="6" width="10" height="20" rx="1.8" fill="none" stroke="{GRN}"'
        ' stroke-width="2.4"/>',
        f'<path d="M20.8 17 l2.6 2.8 l4.6 -6" fill="none" stroke="{RED}" stroke-width="2.6"'
        ' stroke-linecap="round" stroke-linejoin="round"/>',
    ])


def g_lectorium(i="  "):
    """A lectern with a leaf on it, under the reading-room's own roofline.

    Lectorium is the reading room — from legere, to read, the same root as lectern.
    What is on the lectern has been admitted to be read. The mark is the desk and
    the leaf, no arch: an arch over an object reads as a lowercase n, which the
    KnowledgeGate ladder already established.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M16 27 v-6" stroke="{DIM}" stroke-width="3" stroke-linecap="round"/>',
        f'<path d="M8 27 h16" stroke="{DIM}" stroke-width="2.8" stroke-linecap="round"/>',
        f'<path d="M4 18.5 l11.5 -4 l11.5 4 l-11.5 4 z" fill="{RED}"/>',
        f'<path d="M15.5 14.5 v-9" stroke="{GRN}" stroke-width="3" stroke-linecap="round"/>',
        f'<path d="M11 7 h9" stroke="{GRN}" stroke-width="2.8" stroke-linecap="round"/>',
    ])


def g_adlectio(i="  "):
    """A dot crossing a line: the admission itself, and the domain hack.

    adlect.io is the Roman *adlectio* — formal admission to the Senate by decision
    of a separate authority, outside the ordinary rules. The name runs across the
    dot, so the mark makes the dot load-bearing: the item is the dot, the roll it
    joins is the line, and the mark is the instant of joining.

    Two dots are already on the line and signed; the third is arriving and still
    red. Nothing about this shape can be mistaken for a tick, a shield or a play
    button, which is the failure mode most of this set had to be walked back from.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M2.5 21.5 h27" stroke="{DIM}" stroke-width="2.4" stroke-linecap="round"/>',
        f'<circle cx="8" cy="21.5" r="3.4" fill="{GRN}"/>',
        '<circle cx="17" cy="21.5" r="3.4" class="ink"/>',
        f'<circle cx="25.5" cy="9" r="3.8" fill="{RED}"/>',
        f'<path d="M25.5 14 v3.5" stroke="{RED}" stroke-width="2.2" stroke-linecap="round"'
        ' opacity="0.55"/>',
    ])


def g_escrow(i="  "):
    """Two parties, and the held thing between them that neither can reach.

    Escrow is already a three-party institution every business buyer understands: a
    neutral holder keeps the asset until an independent condition is met, and
    crucially *neither counterparty can take it out unilaterally*. Source-code
    escrow is an established software category built on exactly this shape.

    The mark is the two parties as brackets facing the middle, and the held artifact
    between them — deliberately not touching either, because the whole guarantee is
    that neither side has reach.
    """
    return "\n".join(f"{i}{ln}" for ln in [
        f'<path d="M8 5.5 h-4.5 v21 h4.5" fill="none" stroke="{RED}" stroke-width="2.8"'
        ' stroke-linecap="round" stroke-linejoin="round"/>',
        f'<path d="M24 5.5 h4.5 v21 h-4.5" fill="none" stroke="{GRN}" stroke-width="2.8"'
        ' stroke-linecap="round" stroke-linejoin="round"/>',
        '<rect x="12.5" y="12" width="7" height="8" rx="1.5" class="ink"/>',
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
    "adlectio": (g_adlectio, "adlect.io",
                 "Items on the roll, and one arriving: formal admission by a separate "
                 "authority, with the name running across the dot."),
    "escrow": (g_escrow, "KnowledgeEscrow",
               "Two parties bracketing a held artifact neither can reach alone: "
               "released only when an independent condition is met."),
    "countersigned": (g_countersign, "Countersigned",
                      "Two signature strokes crossing: a second party validating the "
                      "first, which is the whole architecture."),
    "correctorium": (g_correctorium, "Correctorium",
                     "Exemplar and copy side by side, the copy carrying the corrector's "
                     "mark: collated by someone who did not write it."),
    "lectorium": (g_lectorium, "Lectorium",
                  "A lectern with a leaf on it: the reading room, where what has been "
                  "admitted may be read."),
    "holdshelf": (g_holdshelf, "HoldShelf",
                  "A shelf with one item held behind a barrier while the rest are "
                  "through: the library's own name for content awaiting release."),
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
        # Height is derived, not hardcoded. The sheet grows by one block per
        # candidate on each of two panes, so a fixed --window-size silently crops
        # the newest additions off the bottom — which it did, and a vision review
        # then reported the light pane as "not visible" for half the set. Screenshot
        # a page taller than the content and let Chrome clip the empty tail.
        per_candidate = 250          # ladder row + wordmark lockup + heading
        rows = len(CANDIDATES) * 2   # dark pane + light pane
        height = 220 + rows * per_candidate
        subprocess.run(["bash", "-c",
                        f'"{chrome}" --headless --disable-gpu --no-sandbox --hide-scrollbars '
                        f'--virtual-time-budget=4000 --screenshot={HERE}/preview.png '
                        f'--window-size=930,{height} {HERE}/preview.html 2>/dev/null'], check=False)
    print(f"{len(CANDIDATES)} candidate marks -> {HERE}")
