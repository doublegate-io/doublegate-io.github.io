#!/usr/bin/env python3
"""Generate hero-field.svg -- what the gate DOES to each thing submitted.

The subject, and why it changed twice
------------------------------------
Draft 1 drew a pipeline: the sequence one claim passes through. That is what
artifact-flow.svg already draws on how-it-works, in full, with 44 labels.

Draft 2 drew a population: 500 agent dots siloed, pooled, gated. That answered
"should we pool our knowledge at all?" -- and by the time a reader has scrolled
to this section they have conceded that. It also needed 1500 dots to say it.

This draws the answer to the question actually left open: submit a memory or a
skill, and what comes back? Five verdicts, and every submission lands in exactly
one of them. That is the thing no other figure on the site shows, and the thing a
reader evaluating a *gate* wants to know.

Four of the five verdicts are the design's own; SHARPENED is a named-for-the-figure
reading of single-parent consolidation, flagged as such below:

  NEW        nothing like it existed; promoted as a new artifact
  SHARPENED  it corrects an existing skill, so a revision supersedes the parent.
             Read from ADR-0016 + ratification §4 pre-processing step 3 ("a
             revision supersedes, both retained"): sharpening is a consolidation
             whose parent set happens to be a single artifact. This is an
             inference from those two, NOT a separately stated decision -- there
             is no ADR naming "sharpening", so do not cite one.
  MERGED     several beliefs reconciled into one; parents superseded, not edited
             (ADR-0016: consolidation proposes, never decides; parents keep
              derives_from edges and are never deleted)
  HELD       contradicts something and the merge was refused, so BOTH parents
             stay ACTIVE and the contradiction stays visible with provenance
             (ADR-0016 decision 4 -- the store staying contradictory is the
              correct outcome, not a bug)
  REFUSED    injection, secrets, or simply wrong; never readable, reasons recorded

Honesty constraint
------------------
The proportions are illustrative and the figure says so on its face. This is a
design-phase product: there is no measured verdict mix, and the site's own rule
is "a citation, or an explicit unverified label". So the row lengths carry the
*shape* of the argument -- most knowledge is new or sharpens something, refusal
is the rare case -- while the caption states plainly that the mix is illustrative.
The one number that IS exact is the total: sixty submissions, sixty dots, rows
that sum to sixty and can be counted by eye.

Fewer dots on purpose
---------------------
1500 dots became 60. The population figure needed 500 because the number WAS the
claim. Here the number only needs to be countable: one dot per submission, one
row per verdict, and a reader can verify the arithmetic by looking at it. Six
strokes in the whole figure.

Deterministic: seeded jitter, computed geometry, byte-identical every run.

Run:  CHROME_PATH=... python3 hero-field.py
"""
from __future__ import annotations

import json
import os
import random
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "hero-field.svg"
CHROME = os.environ.get("CHROME_PATH", "")

FONT = "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Inter, sans-serif"

# ── canvas ──────────────────────────────────────────────────────────────────
W = 1080
PAD = 24
# The left column carries a verdict name AND its one-line meaning stacked, so it
# is sized for the wider of the two, measured -- not for the name alone. Sizing it
# at 132px for "SHARPENED" left the meaning line running through the count.
LABEL_W = 320
COUNT_W = 30           # the count, right-aligned just before the dots
ROW_H = 52
DOT_R = 5.2
DOT_GAP = 15.6         # centre to centre; a submission is an individual, not a bar
TRACK_X = PAD + LABEL_W + COUNT_W
# The consequence note sits under the meaning line, inside the same column: to the
# right of 23 dots there is no room for prose, and the alternative is shrinking the
# dots until they stop being countable.
NOTE_X = PAD
SEED = 20260907

TOTAL = 60

# ── the five verdicts ───────────────────────────────────────────────────────
# n sums to TOTAL and is asserted below: a figure whose own arithmetic does not
# close has no business asking a reader to trust the product's.
VERDICTS = [
    dict(key="new", name="NEW", n=23, colour="#22d3ee",
         head="nothing like it existed",
         note="promoted as its own artifact, readable once signed"),
    dict(key="sharp", name="SHARPENED", n=14, colour="#34d399",
         head="it corrects a skill you already have",
         note="a revision supersedes the parent \u2014 both are kept"),
    dict(key="merge", name="MERGED", n=11, colour="#a78bfa",
         head="several beliefs reconciled into one",
         note="parents superseded, never edited, never deleted"),
    dict(key="held", name="HELD", n=8, colour="#fbbf24",
         head="it contradicts, and the merge was refused",
         note="both parents stay live, the disagreement stays open"),
    dict(key="refused", name="REFUSED", n=4, colour="#fb7185",
         head="injection, a secret, or simply wrong",
         note="never readable by anyone; the reasons are recorded"),
]
assert sum(v["n"] for v in VERDICTS) == TOTAL, sum(v["n"] for v in VERDICTS)

EYEBROW = "SIXTY THINGS YOUR AGENTS WROTE DOWN \u2014 WHAT CAME BACK"
FOOT = ("Every submission ends in exactly one verdict, signed. Nothing is edited in "
        "place, and nothing vanishes.")
CAVEAT = ("Design phase: the split across the five is illustrative, not a measured rate. "
          "The mechanism is what is being shown.")
# One entry per mark the rows use, in row order. Faint dots behind a mark are the
# parents the ledger retains -- the product's claim that nothing is deleted, drawn.
KEY_ITEMS = [
    ("plain", "one submission, no parent"),
    ("one", "supersedes one parent"),
    ("many", "supersedes several"),
    ("pair", "two, both left live"),
    ("hollow", "kept, never readable"),
]

STYLE = """    .eyebrow { font-size:11.5px; font-weight:700; letter-spacing:.1em; fill:#8d97a9; }
    .vn   { font-size:13px; font-weight:700; letter-spacing:.06em; }
    .vc   { font-size:15px; font-weight:700; fill:#e6e9ef; }
    .vh   { font-size:13px; font-weight:600; fill:#e6e9ef; }
    .vt   { font-size:12px; fill:#8d97a9; }
    .foot { font-size:13.5px; font-weight:600; fill:#e6e9ef; }
    .cav  { font-size:11.5px; fill:#6b7484; }

    /* A reader who asks the OS for less motion gets the static figure. The only
       motion is one ring on the newest submission; the figure reads standing still. */
    @media (prefers-reduced-motion: reduce) { .mover { display:none; } }"""

DEFS = """  <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#1e2430" stop-opacity="0"/>
    <stop offset=".08" stop-color="#232b39" stop-opacity="1"/>
    <stop offset=".92" stop-color="#232b39" stop-opacity="1"/>
    <stop offset="1" stop-color="#1e2430" stop-opacity="0"/>
  </linearGradient>
  <filter id="soft" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="2.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>"""


def measure(pairs):
    """Rendered width of each (class, string) at the class it will actually use."""
    if not CHROME:
        raise SystemExit("set CHROME_PATH")
    tmp = ROOT / ".tmp" / "_hf.svg"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    rows, y = [], 26
    for cls, txt in pairs:
        rows.append(f'<text class="{cls}" x="10" y="{y}">'
                    f'{txt.replace("&", "&amp;")}</text>')
        y += 30
    tmp.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" '
                   f'height="{y + 20}" font-family="{FONT}">'
                   f'<style>{STYLE}</style>' + "\n".join(rows) + "</svg>")
    js = ROOT / ".tmp" / "_hf.js"
    js.write_text("""
const puppeteer=require('puppeteer-core');
(async()=>{const b=await puppeteer.launch({executablePath:process.env.CHROME_PATH,args:['--no-sandbox']});
const p=await b.newPage();await p.goto('file://'+process.argv[2]);
const o=await p.evaluate(()=>{const r={};document.querySelectorAll('text')
.forEach(t=>r[t.textContent]=+t.getBBox().width.toFixed(1));return r;});
console.log(JSON.stringify(o));await b.close();})();""")
    r = subprocess.run(["node", str(js), str(tmp)], cwd=ROOT, capture_output=True,
                       text=True, env={**os.environ, "CHROME_PATH": CHROME})
    if r.returncode:
        raise SystemExit(r.stderr[-600:])
    return json.loads(r.stdout)


def build(Wd):
    rnd = random.Random(SEED)
    o = []
    y = 92

    o.append(f'<text class="eyebrow" x="{PAD}" y="40">{EYEBROW}</text>')

    # A shape channel a reader cannot decode is decoration, so the key is stated
    # rather than left to be inferred: the faint dots behind a mark ARE the parents
    # the ledger retains, and that is the product's whole claim about not deleting.
    # Each glyph in the key is the glyph the rows use, in row order, so the
    # one-parent / two-parent / two-live / hollow distinctions are shown rather
    # than described. Drawn on its own line under the eyebrow: on one line with
    # the eyebrow there was room for the marks but not for naming them.
    ky = 60
    g = "#8d97a9"
    kx = PAD

    def swatch(x, kind):
        out = []
        if kind == "plain":
            out.append(f'<circle cx="{x:g}" cy="{ky:g}" r="4.8" fill="{g}" fill-opacity=".85"/>')
        elif kind == "one":
            out.append(f'<circle cx="{x - 3.6:g}" cy="{ky + 2.8:g}" r="3.6" fill="{g}" fill-opacity=".34"/>')
            out.append(f'<circle cx="{x:g}" cy="{ky:g}" r="4.8" fill="{g}" fill-opacity=".9"/>')
        elif kind == "many":
            out.append(f'<circle cx="{x - 4.6:g}" cy="{ky + 3.2:g}" r="3.1" fill="{g}" fill-opacity=".34"/>')
            out.append(f'<circle cx="{x + 1.1:g}" cy="{ky + 4.1:g}" r="3.1" fill="{g}" fill-opacity=".34"/>')
            out.append(f'<circle cx="{x:g}" cy="{ky:g}" r="4.8" fill="{g}" fill-opacity=".9"/>')
        elif kind == "pair":
            out.append(f'<circle cx="{x - 3.3:g}" cy="{ky:g}" r="3.2" fill="{g}" fill-opacity=".85"/>')
            out.append(f'<circle cx="{x + 3.3:g}" cy="{ky:g}" r="3.2" fill="{g}" fill-opacity=".85"/>')
        else:
            out.append(f'<circle cx="{x:g}" cy="{ky:g}" r="4.2" fill="none" stroke="{g}" '
                       f'stroke-width="1.5" stroke-opacity=".75"/>')
        return out

    for kind, text in KEY_ITEMS:
        o += swatch(kx + 5, kind)
        o.append(f'<text class="cav" x="{kx + 16:g}" y="{ky + 4:g}">{text}</text>')
        kx += 16 + Wd[text] + 24

    o.append(f'<path d="M {PAD} 76 L {W - PAD} 76" stroke="url(#rule)" '
             f'stroke-width="1" fill="none"/>')

    newest = None
    for vi, v in enumerate(VERDICTS):
        cy = y + ROW_H / 2

        # verdict name, then the count right-aligned against the start of its dots.
        # The count and the dots say the same thing, which is the point: a reader who
        # distrusts the number can count the row.
        o.append(f'<text class="vn" x="{PAD}" y="{cy - 11:g}" fill="{v["colour"]}">{v["name"]}</text>')
        o.append(f'<text class="vh" x="{PAD}" y="{cy + 6:g}">{v["head"]}</text>')
        o.append(f'<text class="vt" x="{PAD}" y="{cy + 23:g}">{v["note"]}</text>')
        cnt_x = TRACK_X - 12
        o.append(f'<text class="vc" x="{cnt_x:g}" y="{cy + 5:g}" text-anchor="end" '
                 f'fill="{v["colour"]}">{v["n"]}</text>')

        # the dots: one per submission, on one row, evenly pitched. No bar, no
        # rectangle -- a submission is an individual thing and the reader is meant
        # to be able to count them.
        # HELD draws two marks per submission, so it needs a wider pitch than the
        # single-mark rows or the pairs fuse into one long row and the count stops
        # being verifiable by eye.
        pitch = DOT_GAP * 1.55 if v["key"] == "held" else DOT_GAP
        for i in range(v["n"]):
            cx = TRACK_X + i * pitch
            jy = rnd.uniform(-0.5, 0.5)
            if v["key"] == "refused":
                # refused dots are hollow: present in the ledger, never readable.
                # That distinction is the product, so it gets a distinct shape
                # rather than only a colour.
                o.append(f'<circle cx="{cx:.1f}" cy="{cy + jy:.1f}" r="{DOT_R - 0.6:g}" '
                         f'fill="none" stroke="{v["colour"]}" stroke-width="1.5" '
                         f'stroke-opacity=".75"/>')
            elif v["key"] == "sharp":
                # ONE superseded parent behind the revision. Shape encodes parent
                # count, so sharpened and merged must not share a mark: sharpening
                # has exactly one parent skill, merging has several, and drawing
                # both as "dot with a shadow" gave one symbol two meanings.
                o.append(f'<circle cx="{cx - 4:.1f}" cy="{cy + jy + 3:.1f}" '
                         f'r="{DOT_R - 1.2:g}" fill="{v["colour"]}" fill-opacity=".34"/>')
                o.append(f'<circle cx="{cx:.1f}" cy="{cy + jy:.1f}" r="{DOT_R}" '
                         f'fill="{v["colour"]}" fill-opacity=".95"/>')
            elif v["key"] == "merge":
                # SEVERAL parents behind one candidate: two retained parents fanned
                # below, which is what a derives_from with multiple edges looks like.
                o.append(f'<circle cx="{cx - 5:.1f}" cy="{cy + jy + 3.4:.1f}" '
                         f'r="{DOT_R - 1.8:g}" fill="{v["colour"]}" fill-opacity=".34"/>')
                o.append(f'<circle cx="{cx + 1.2:.1f}" cy="{cy + jy + 4.4:.1f}" '
                         f'r="{DOT_R - 1.8:g}" fill="{v["colour"]}" fill-opacity=".34"/>')
                o.append(f'<circle cx="{cx:.1f}" cy="{cy + jy:.1f}" r="{DOT_R}" '
                         f'fill="{v["colour"]}" fill-opacity=".95"/>')
            elif v["key"] == "held":
                # held: two parents, both still live, neither preferred. Two dots
                # of equal weight touching -- the contradiction is not resolved.
                o.append(f'<circle cx="{cx - 2.6:.1f}" cy="{cy + jy:.1f}" '
                         f'r="{DOT_R - 2.2:g}" fill="{v["colour"]}" fill-opacity=".9"/>')
                o.append(f'<circle cx="{cx + 2.6:.1f}" cy="{cy + jy:.1f}" '
                         f'r="{DOT_R - 2.2:g}" fill="{v["colour"]}" fill-opacity=".9"/>')
            else:
                o.append(f'<circle cx="{cx:.1f}" cy="{cy + jy:.1f}" r="{DOT_R}" '
                         f'fill="{v["colour"]}" fill-opacity=".9"/>')

            if vi == 0 and i == v["n"] - 1:
                newest = (cx, cy + jy)

        y += ROW_H

    # one ring, on the most recent arrival. The only motion in the figure.
    if newest:
        nx, ny = newest
        o.append(f'<circle class="mover" cx="{nx:.1f}" cy="{ny:.1f}" r="{DOT_R + 2:g}" '
                 f'fill="none" stroke="#22d3ee" stroke-width="1.5">'
                 f'<animate attributeName="r" dur="3.6s" repeatCount="indefinite" '
                 f'values="{DOT_R + 2:g};{DOT_R + 11:g};{DOT_R + 2:g}" keyTimes="0;0.5;1"/>'
                 f'<animate attributeName="stroke-opacity" dur="3.6s" '
                 f'repeatCount="indefinite" values=".85;0;.85" keyTimes="0;0.5;1"/></circle>')

    base = y + 12
    o.append(f'<path d="M {PAD} {base:g} L {W - PAD} {base:g}" stroke="url(#rule)" '
             f'stroke-width="1" fill="none"/>')
    o.append(f'<text class="foot" x="{PAD}" y="{base + 26:g}">{FOOT}</text>')
    o.append(f'<text class="cav" x="{PAD}" y="{base + 46:g}">{CAVEAT}</text>')

    height = int(base + 66)
    desc = (
        "Five rows, one per verdict, showing what came back for sixty things agents "
        "wrote down. Twenty-three were NEW: nothing like them existed, so each was "
        "promoted as its own artifact, readable once signed. Fourteen were SHARPENED: "
        "they corrected a skill already held, so a revision superseded the parent and "
        "both are kept, drawn as a bright dot with the retained parent dimmer behind "
        "it. Eleven were MERGED: several beliefs reconciled into one, with the parents "
        "superseded rather than edited or deleted. Eight were HELD: they contradicted "
        "something and the merge was refused, so both parents stay live and the "
        "contradiction stays visible with its provenance, drawn as two dots of equal "
        "weight. Four were REFUSED as injection, a secret, or simply wrong, drawn "
        "hollow because they remain in the ledger with their reasons recorded but are "
        "never readable by anyone. The counts sum to sixty. Every submission ends in "
        "exactly one verdict, carrying a signature naming who decided and on what "
        "basis; nothing is edited in place and nothing vanishes. The split across the "
        "five verdicts is illustrative of the mechanism, not a measured rate.")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}"
     role="img" aria-labelledby="t d" font-family="{FONT}">
<title id="t">What the gate returns for sixty submitted memories and skills</title>
<desc id="d">{desc}</desc>
<defs>
  <style><![CDATA[
{STYLE}
  ]]></style>
{DEFS}
</defs>
<rect width="{W}" height="{height}" fill="#08090c"/>
{chr(10).join(o)}
</svg>
"""


def main():
    pairs = [("eyebrow", EYEBROW), ("foot", FOOT), ("cav", CAVEAT)]
    pairs += [("cav", t) for _, t in KEY_ITEMS]
    for v in VERDICTS:
        pairs += [("vn", v["name"]), ("vh", v["head"]), ("vt", v["note"]),
                  ("vc", str(v["n"]))]
    Wd = measure(pairs)

    # Geometry checks BEFORE writing: the widest row of dots must not run into the
    # note column, and no label may exceed the space allotted to it. Getting this
    # wrong is what produced eleven overflowing labels in an earlier figure.
    widest = max(v["n"] for v in VERDICTS)
    track_end = TRACK_X + (widest - 1) * DOT_GAP + DOT_R
    problems = []
    if track_end > W - PAD:
        problems.append(f"dot track ends at {track_end:.0f}, past the {W - PAD} margin")
    avail = LABEL_W          # name, meaning and note all share the left column
    for v in VERDICTS:
        for field in ("name", "head", "note"):
            if Wd[v[field]] > avail:
                problems.append(f'{field} "{v[field]}" is {Wd[v[field]]:.0f}px > '
                                f'column {avail}px')
    for cls, t in (("foot", FOOT), ("cav", CAVEAT), ("eyebrow", EYEBROW)):
        if PAD + Wd[t] > W - PAD:
            problems.append(f"{cls} overruns by {PAD + Wd[t] - (W - PAD):.0f}px")
    key_end = PAD + sum(16 + Wd[t] + 24 for _, t in KEY_ITEMS)
    if key_end > W - PAD:
        problems.append(f"shape key overruns by {key_end - (W - PAD):.0f}px")
    if problems:
        for p in problems:
            print("  " + p)
        raise SystemExit("layout does not fit -- shorten copy, do not widen the canvas")

    svg = build(Wd)
    OUT.write_text(svg)
    dots = sum(v["n"] for v in VERDICTS)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(svg)} bytes, {dots} submissions in "
          f"{len(VERDICTS)} verdicts, track ends {track_end:.0f}, notes at {NOTE_X:.0f})")


if __name__ == "__main__":
    main()
