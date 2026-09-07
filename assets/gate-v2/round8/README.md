# Round 8 — `offset` developed: overlap resolved, colour measured

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build8.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure8.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round8/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round8/one-*.png
```

`offset` earned this round: best of 59 marks, separable at 16px with 23 separating
scanlines, and the only mark in eight rounds to pass the geometry audit untouched.

## The visual defect, and the fix that changed the read

Where the two outlines crossed there were four line-crossings and a small closed
cell, and **nothing stated which square was in front**. That cost both ways —
semantically two intersecting squares are peers, and four crossings inside a 5×5px
region is where a favicon turns to mud.

Three resolutions tested. The vision read shifted, which is the result worth having:

| Variant | 16px | Reads back as |
|---|---|---|
| baseline (control) | separable, 23 scanlines, ink 0.406 | "a set of **overlapping** squares" |
| **knockout** | separable, 23 scanlines, ink 0.441 | "two overlapping squares forming a combined, **interlocking** shape" |
| **weave** | separable, 23 scanlines, ink 0.445 | "two overlapping squares forming an **interlocking** mark" |
| solidfront | separable, 15 scanlines, ink 0.52 | "a rounded square frame with a solid square overlapping it" |
| tight | separable, 20 scanlines, ink 0.547 | "two overlapping squares forming an interlocking mark" |
| axis | separable, 15 scanlines, ink 0.383 | "a rectangle with a vertical divider, a **window pane**" |

*Overlapping* → *interlocking* is the whole point. Interlocked is the accurate
relationship for a record and its countersignature: neither link opens alone. It
cost 0.035 ink and no scanlines.

`axis` failed its own hypothesis — removing the diagonal was supposed to kill the
duplicate-icon affordance, but it dropped to 15 scanlines and became a window pane,
i.e. a UI element rather than an object.

## The colour finding: every accent in the palette fails on white

Contrast measured, not eyeballed. 3:1 is the WCAG 1.4.11 graphical-object
threshold; below it a stroke stops being reliably visible.

| Accent | Hex | On `#08090c` | On white | |
|---|---|---|---|---|
| grn | `#34d399` | 10.36:1 | **1.92:1** | fails |
| cyn | `#22d3ee` | 11.02:1 | **1.81:1** | fails |
| amb | `#fbbf24` | 11.93:1 | **1.67:1** | fails |
| vio | `#a78bfa` | 7.32:1 | **2.72:1** | fails |
| dim | `#97a1b2` | 7.64:1 | **2.61:1** | fails |
| ink | `#e6e9ef` | 16.37:1 | **1.22:1** | fails (already themed, so fine) |

The palette is tuned for a dark page and it is correct there. The problem is that
`.ink` themes through `prefers-color-scheme` and **the accent never did** — it only
ever appeared on the dark site. A favicon cannot choose the tab colour, and a
browser in light mode paints a white tab strip.

Two fixes, both built:

- **`fix-oneshade`** — one hex on both grounds, `#059669` (emerald 600): 5.28:1
  dark / 3.77:1 white. Nothing to theme, nothing that can drift out of step. It is
  visibly duller, and on the dark page it will not match the green used elsewhere.
- **`fix-themed`** — `#34d399` on dark, `#059669` on light, exactly as `.ink`
  already flips. Same hue, correct weight on each ground, dark page keeps the
  site's own green. Costs one media-query line.

`fix-themed` is the recommendation. It measures identically to `knockout` (23
scanlines, ink 0.441), and the light-mode value resolves correctly in the preview.

Red `#fb7185` is excluded on **meaning** rather than contrast: red/green reads
fail/pass, and the two squares are sequential stages, not a bad one and a good one.

## This is a live bug, not just a candidate concern

`assets/logo.svg` — the favicon shipping on every page right now — is two arches in
`#fb7185` and `#34d399`, with **no media query at all**:

| Live stroke | On dark | On white |
|---|---|---|
| red arch `#fb7185` | 7.40:1 | **2.69:1** |
| green arch `#34d399` | 10.36:1 | **1.92:1** |

Both below 3:1 in a light-mode tab. Whatever mark is chosen, that wants fixing —
`#f43f5e` (3.67:1 white) and `#059669` are the drop-in shades if the current mark
stays.

## Audit false positive found and fixed

`audit-geometry.js` flagged all six knockout variants for *mixed stroke weights:
2.5, 4.5*. That was the audit being wrong: a knockout gap is a stroke painted in
the **background colour** — it deletes ink rather than adding any, so its width is
invisible by construction, and it *should* be heavier than the line it interrupts
or it closes up under anti-aliasing at 16px, which is the entire reason for drawing
it.

The check now counts only visible strokes, excluding `class="cut"` and any stroke
set to a background colour. Round 8 goes 13/13 clean; rounds 6 and 7 still report
6/15, so nothing was loosened retroactively.
