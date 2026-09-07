# Round 11 — two navies, rounded corners, stretched to rectangles

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build11.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure11.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round11/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round11/one-*.png
```

Three changes requested: `ink-two-navy`, rounded corners, stretched rectangles. Two
were straightforward. The two-navy pair needed a correction first.

## A true two-navy pair cannot be done

`ink-two-navy` was `#0A1F44` + `#12275C`, and those measure **1.14:1 against each
other** — round 10's vision read on that exact file came back as *"a cluster of
**three** overlapping squares"*, because the strokes merged at the crossing and
manufactured a square that was never drawn.

So: how far up the same-hue ramp must the partner go before two navies read as two?

| Partner | vs granat | |
|---|---|---|
| `#12275C` | **1.14:1** | merges — the original pair |
| `#173371` | 1.35:1 | merges |
| `#1B3A80` | 1.52:1 | merges |
| `#1E3A8A` blue 800 | 1.57:1 | merges |
| `#1E40AF` blue 700 | 1.86:1 | merges |
| `#2657B8` | 2.43:1 | marginal |
| **`#2563eb` blue 600** | **3.14:1** | **passes** |
| `#3b82f6` blue 500 | 4.42:1 | passes |

The partner has to travel all the way to **blue 600** before the two separate. This
round uses `#0A1F44` + `#2563eb` — the deepest possible partner that still reads as
two elements, i.e. the two-navy idea honoured as closely as the physics allows.

It comes with a bonus: `#2563eb` clears 3:1 on **all three** grounds at once —
3.85:1 dark, 5.17:1 white, 3.14:1 against granat. One value, usable in every
position.

## The stretch did what the knockout gap did, for free

`r-3x2` reads back as *"two overlapping rounded rectangles that **interlock** to form
a layered, window-like mark"* — and `r-3x2-rx4` as *"two **interlocking** rounded
rectangles"*.

Round 8 needed a background-coloured knockout gap to move the read from
*overlapping* to *interlocking*, at +0.035 ink and a themed class to keep in sync.
The stretch produces the same word with no gap at all. A rectangle's long edge
crosses its partner's short edge at a clearly different length, so the eye reads
depth without being told.

It also kills the affordance risk that has been open on this shape since round 4:
two overlapping **squares** is the copy/duplicate icon's exact gesture. A stretched
rectangle is a card, a plate, a label, a ledger line.

## Stretching costs scanlines, monotonically

| Variant | Ratio | 16px | Ink | Reads back as |
|---|---|---|---|---|
| r-4x3 | 4:3 | **22 scanlines** | 0.484 | "two overlapping rounded rectangles" |
| **r-3x2** | 3:2 | 21 scanlines | 0.453 | "**interlock**, window-like" |
| r-3x2-rx4 | 3:2, rx4 | 21 scanlines | **0.414** | "two **interlocking** rounded rectangles" |
| r-16x9 | 16:9 | 20 scanlines | 0.422 | "a set of overlapping rounded rectangles" |
| r-3x2-shift | sideways offset | 19 scanlines | 0.406 | — |
| r-2x1 | 2:1 | 18 scanlines | 0.391 | — |
| r-5x2 | 5:2 | **16 scanlines** | 0.359 | "two overlapping rounded rectangles" |

A wide rectangle has less height for horizontal scanlines to separate, and gapRows is
where the 16px verdict comes from. 4:3 measures best on separability and worst on
ink; past 16:9 the trade stops paying and the read flattens back to a plain
description.

**3:2 is the pick.** It is where "interlock" first appears and the last ratio before
separability starts falling.

**Portrait is out.** `r-3x2-vert` reads as *"stacked **phones or tablets**"* — a
device affordance, which is worse than the copy-icon one we were escaping.

## A real bug the audit caught

My first centring pass put the wide variants **inside the reserved 2px margin**: at
22px wide with an 8px offset the pair spans 30px, so a centred origin lands at x=1.
IBM reserves 2..30 on a 32px grid, and artwork in the margin is what gets clipped
when a platform applies its own mask.

`_origin()` now centres, clamps to 2, and **asserts** the pair fits — which
immediately caught three more variants I'd have shipped silently overflowing. Widths
came down to 20 and the round went from 7/12 to 11/12 clean. The one remaining flag
is `r-3x2-failed-pair`, kept deliberately as evidence.

## Recommendation

`logo-themed-3x2.svg`. 3:2, rx2, one file: granat `#0A1F44` + blue 600 `#2563eb` on
paper, blue 500 + ink on dark. 21 separating scanlines, audit-clean, and it reads as
interlocking without a knockout gap.

Worth weighing: `r-3x2-rx4` measures the same separability at **lower ink** (0.414 vs
0.453) and also reads as interlocking. It is softer — closer to an app icon, further
from a seal. That is a taste call rather than a measurement one.
