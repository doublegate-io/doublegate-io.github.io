#!/usr/bin/env python3
"""Build ONE page showing every candidate mark from every round, side by side.

Run from the repo root:  python3 assets/gallery.py
Then:                    python3 -m http.server 8137 --bind 127.0.0.1
Open:                    http://localhost:8137/assets/gallery.html

WHY THIS EXISTS
---------------
Every round wrote its own preview.html into its own directory, and nothing links
to any of them. So "browsing the site" shows only the live mark and the work is
invisible — which is a real reporting failure, not a user error. Four
directories, 30-odd candidates, no single view.

This page is generated from the SVGs ON DISK rather than from the build scripts,
so it shows what is actually there. It is deliberately NOT linked from any site
page: these are candidates, and linking them would pre-empt the decision.

Each mark is shown at 16 / 22 / 32 / 64 / 128 px on both themes, with the ink
ratio and separability numbers from the measurement harness printed beside it, so
the page carries the evidence rather than just the picture.
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
BG_D, BG_L = "#08090c", "#ffffff"
INK_D, INK_L = "#e6e9ef", "#10131a"
SIZES = [16, 22, 32, 64, 128]
SANS = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Inter, sans-serif"

# Ordered newest-first: the current recommendation should be the first thing seen.
GROUPS = [
    ("Round 4 — one or two elements, no diagram (Rand: a logo does not explain the business)",
     "gate-v2/round4", [
        ("offset", "STRONGEST — two identical squares, one offset · reads 'two overlapping squares'"),
        ("seam", "one square cut once, halves offset · reads 'a square divided by a diagonal'"),
        ("wedge", "one wedge with a slot cut through · reads 'a triangle with a bar through it'"),
        ("halfring", "one broken ring — reads as a C/horseshoe, class C"),
        ("bite", "one square, one notch — FUSED at 16px"),
        ("dg", "control monogram — reads as 'S', not 'dg'"),
    ]),
    ("Round 3 — arch-free, all four failure classes dodged", "gate-v2/round3", [
        ("twoseals", "RECOMMENDED — a tablet carrying two seals struck at different depths"),
        ("countermark", "a struck lozenge with a countermark across its corner"),
        ("notch", "a solid block with two notches cut out — gates as absence"),
        ("relay", "a hand-off between two custodians"),
    ]),
    ("Round 2 — arch abandoned", "gate-v2/round2", [
        ("turnstile", "two barriers across a channel"),
        ("airlock", "two shutters from opposite edges"),
        ("ratchet", "two steps of a stair"),
        ("sluice", "two shutters on one run"),
        ("twokeys", "two keyholes, the second turns"),
        ("ledgerline", "signature then countersignature"),
    ]),
    ("Round 1 — the arch family (all read as letters)", "gate-v2", [
        ("live", "THE SHIPPED MARK — reads as 'nn'"),
        ("depth", "same paths, order by depth not hue"),
        ("step", "order by height"),
        ("transit", "artifact between the gates"),
        ("stack", "a corridor, not a pair"),
        ("numbered", "order by tally"),
    ]),
    ("Name candidates (from the naming sweep — for a renamed product)",
     "naming-options", [
        ("accession", "spines on a register line, one still outside"),
        ("countersigned", "two signatures, each on its own rule"),
        ("escrow", "two parties bracketing a held artifact"),
        ("correctorium", "exemplar and copy, the copy corrected"),
        ("adlectio", "items on the roll, one arriving"),
        ("lectorium", "a lectern with a leaf on it"),
        ("holdshelf", "a shelf with a gate line running past"),
        ("assayoffice", "a hallmark punch"),
        ("poundlock", "a canal lock from above"),
        ("knowledgediode", "the diode glyph, vertical"),
        ("knowledgeporter", "a lodge hatch"),
        ("agentlibrarian", "an open book with a date stamp"),
    ]),
    ("Earlier: KnowledgeGate variants", "knowledgegate", [
        ("arch-book", "book under a gate arch"),
        ("posts-book", "two posts holding a closed book"),
        ("spine-book", "the book IS the gate"),
        ("arches", "two arches, no book"),
    ]),
]


def force(svg, light):
    """Resolve prefers-color-scheme in code, both directions.

    A browser applies the media query from the OS, so a dark pane on a
    light-themed desktop renders dark ink on dark ground and the mark looks
    absent. Substitute for the light pane; strip the light branch for the dark.
    """
    if light:
        return (svg.replace(f"fill: {INK_D}", f"fill: {INK_L}")
                   .replace(f"stroke: {INK_D}", f"stroke: {INK_L}")
                   .replace(f'stroke="{INK_D}"', f'stroke="{INK_L}"')
                   .replace(f'fill="{INK_D}"', f'fill="{INK_L}"'))
    return re.sub(r"@media \(prefers-color-scheme: light\) \{.*?\n\s*\}\n", "", svg, flags=re.S)


def sz(svg, px):
    return re.sub(r'width="\d+" height="\d+"', f'width="{px}" height="{px}"', svg, count=1)


def measured():
    """Pull the 16px numbers from the measurement harness so the page carries
    evidence, not just pictures. Best-effort: no numbers is better than wrong."""
    out = {}
    chrome = os.path.expanduser(
        "~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome")
    for script in ("gate-v2/measure3.js", "gate-v2/measure2.js", "gate-v2/measure.js",
                   "naming-options/measure.js"):
        p = os.path.join(ROOT, script)
        if not os.path.exists(p):
            continue
        try:
            r = subprocess.run(["node", p], cwd=os.path.dirname(ROOT), capture_output=True,
                               text=True, timeout=240, env={**os.environ, "CHROME_PATH": chrome})
            for line in r.stdout.splitlines():
                m = re.match(r"\s{2}(\S+)\s+(separable|marginal|FUSED)\s+\((\d+) separating"
                             r" scanlines, (\d+) colours, ink ([\d.]+)\)", line)
                if m:
                    out[m.group(1)] = (m.group(2), m.group(3), m.group(5))
        except Exception:
            pass
    return out


def main():
    stats = measured()
    blocks = []
    missing = []

    for title, subdir, marks in GROUPS:
        rows = []
        for key, blurb in marks:
            path = os.path.join(ROOT, subdir, f"logo-{key}.svg")
            if not os.path.exists(path):
                missing.append(f"{subdir}/logo-{key}.svg")
                continue
            raw = open(path).read()
            verdict = stats.get(key)
            note = (f'<span class="m {verdict[0]}">{verdict[0]}</span>'
                    f'<span class="n">{verdict[1]} scanlines · ink {verdict[2]}</span>'
                    if verdict else '<span class="n">not measured</span>')
            panes = []
            for light in (False, True):
                s = force(raw, light)
                cells = "".join(f'<div class="c"><div class="h">{sz(s, px)}</div>'
                                f'<i>{px}</i></div>' for px in SIZES)
                panes.append(f'<div class="pane" style="background:'
                             f'{BG_L if light else BG_D}">{cells}</div>')
            rows.append(f'<article><header><b>{key}</b>{note}'
                        f'<em>{blurb}</em></header>{"".join(panes)}</article>')
        if rows:
            blocks.append(f'<section><h2>{title}</h2>{"".join(rows)}</section>')

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>doublegate — every candidate mark</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin:0; background:#0b0d11; color:#e6e9ef;
         font:14px/1.5 {SANS}; padding:28px 32px 60px; }}
  h1 {{ font-size:19px; margin:0 0 4px; }}
  .lead {{ color:#97a1b2; margin:0 0 28px; max-width:70ch; }}
  .lead code {{ color:#fbbf24; }}
  h2 {{ font-size:12px; letter-spacing:1.6px; text-transform:uppercase;
        color:#64748b; margin:34px 0 12px; border-top:1px solid #1c2128; padding-top:14px; }}
  article {{ margin:0 0 18px; }}
  header {{ display:flex; align-items:baseline; gap:10px; margin-bottom:6px; }}
  header b {{ font-size:14px; }}
  header em {{ font-style:normal; color:#78849a; font-size:13px; }}
  .m {{ font-size:10px; letter-spacing:.8px; text-transform:uppercase;
        padding:2px 6px; border-radius:3px; }}
  .separable {{ background:#0f2f22; color:#34d399; }}
  .marginal {{ background:#33280c; color:#fbbf24; }}
  .FUSED {{ background:#3a1418; color:#fb7185; }}
  .n {{ font-size:11px; color:#5c6879; font-variant-numeric:tabular-nums; }}
  .pane {{ display:flex; align-items:flex-end; gap:18px; padding:14px 18px;
           border:1px solid #1c2128; }}
  .pane:first-of-type {{ border-bottom:0; }}
  .c {{ text-align:center; }}
  .h {{ display:flex; align-items:center; justify-content:center; height:132px; }}
  .c i {{ display:block; font-size:10px; opacity:.35; font-style:normal; margin-top:4px; }}
  .pane:last-of-type .c i {{ color:#10131a; opacity:.45; }}
</style></head><body>
<h1>doublegate — every candidate mark, one page</h1>
<p class="lead">Generated from the SVGs on disk by <code>assets/gallery.py</code>.
Each mark at 16/22/32/64/128&nbsp;px on dark then light, with its measured 16&nbsp;px
verdict. <strong>Nothing here is wired into the site</strong> — the live mark is still
<code>assets/logo.svg</code>, which is the first entry under Round&nbsp;1.
The <code>prefers-color-scheme</code> query is resolved in code for both panes, so
neither pane depends on your OS theme.</p>
{"".join(blocks)}
</body></html>
"""
    out = os.path.join(ROOT, "gallery.html")
    open(out, "w").write(html)
    n = sum(len(g[2]) for g in GROUPS) - len(missing)
    print(f"{n} marks -> {out}")
    if missing:
        print("missing (skipped): " + ", ".join(missing))
    print(f"{len(stats)} measured verdicts embedded")
    print("\nserve it:  python3 -m http.server 8137 --bind 127.0.0.1")
    print("open:      http://localhost:8137/assets/gallery.html")


if __name__ == "__main__":
    main()
