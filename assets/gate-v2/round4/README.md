# Round 4 — the diagnosis was never about arches

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build4.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure4.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round4/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round4/one-*.png
```

## What eighteen rejected rivals were actually telling us

Rounds 1-3 treated every rejection as a **shape** problem: the arch reads as an
`n`, so drop the arch; bars read as a chart, so drop the bars. That produced four
useful failure classes and no acceptable mark, because it was the wrong level of
diagnosis.

Every one of those marks was a small **diagram** — three or four elements
arranged to explain that a thing passes one authority and then a second one.

Paul Rand (IBM, UPS, ABC, NeXT) settled this in *Thoughts on Design*, 1947:

> A logo does not need to explain the business. It needs to be distinctive,
> memorable, and simple enough to work everywhere. A logo derives meaning from
> the quality of the thing it stands for, not the other way around. **The mark
> does not create the reputation. It stores it.**

Sagi Haviv (Chermayeff & Geismar) states the test as three conditions: a mark
must be **appropriate**, **distinctive**, and **simple enough to be drawn from
memory**.

That last clause is what we kept failing. Count the elements:

| Mark | Elements | Read back as |
|---|---|---|
| `live` (shipped) | 2 arches | "two n letters" |
| `twoseals` | tablet + 2 lozenges = 3 | "a document icon" |
| `relay` | 2 diagonals + block + rule = 4 | "a pen, a checkmark" |
| `turnstile` | 4 | "a person" |
| **Vercel** | **1 triangle** | — |
| **Apple** | **1 circle, one bite** | — |

Nobody can redraw a tablet with two lozenge seals struck at different depths.
Everyone can redraw a triangle.

## The constraint for this round

**One or two elements. No more.** A third element is a bug, not a refinement.
`build4.py` prints the element count on every run so the rule cannot quietly
erode.

Meaning is allowed to be **hidden** rather than **shown**. FedEx hides an arrow
in the gap between `E` and `x`; most people never consciously see it and it works
anyway. Amazon's single curve is a-to-z *and* a smile. That is the register — one
shape that happens to contain the second idea, not two shapes demonstrating a
process.

Palette narrows for the same reason. Rand drew the WWF panda in black and white
so it could print anywhere, and *the restraint is the meaning*. Each mark here is
one ink plus at most one accent, and each ships a flat monochrome variant that is
checked alongside.

## Results

Measured at 16px, audited against the IBM 32px grid, and read with one open
question (no menu of answers, so a letterform read is unprompted and real):

| Mark | Elements | 16px | Audit | Reads back as |
|---|---|---|---|---|
| **offset** | 2 | **separable, 23 scanlines, ink 0.406** | **CLEAN** | "two overlapping squares forming a window-like frame" |
| **seam** | 2 | marginal, 5 scanlines, ink 0.547 | 2 angles off 15° | "a square divided by a diagonal into two triangles" |
| **wedge** | 1 | marginal, 8 scanlines, ink 0.344 | 2 angles off 15° | "a triangle with a horizontal bar through its middle" |
| halfring | 2 | marginal, 6 scanlines | padding | "a crescent, a C shape, or a horseshoe" — **class C** |
| bite | 1 | **FUSED**, 2 scanlines, ink 0.547 | 2 angles off 15° | "a square with a triangular notch cut into its right side" |
| dg | 2 | separable, 9 scanlines | padding | "a stylized letter S" — **fails as a d/g monogram** |

**Three clean survivors: `offset`, `seam`, `wedge`.** This is the first round in
four where nothing collapsed into a letter, a chart, a pin, or a person — the
reads are literal descriptions of the geometry, which is what a mark holding no
diagram should produce.

Two informative failures:

- **`dg` was the control**, included because "it reads as a letter" is a *feature*
  for a monogram — Supabase, Stripe and Linear all lean on the name rather than
  the mechanism. It reads as **"S"**, not `dg`, so it fails at the one job a
  monogram has. Worth knowing before anyone proposes a monogram again.
- **`bite` FUSED at 16px** (2 separating scanlines, ink 0.547) despite being the
  simplest thing here — one square, one notch. A single solid mass has almost no
  internal negative space, and negative space is what survives downscaling. The
  Apple principle needs the notch to be *proportionally larger* than instinct
  suggests.

## Open

`offset` is the strongest on every measurement, and "two overlapping squares" is
an honest description of *original and countersigned copy* — but two nested
squares are also a common UI affordance (copy, duplicate, layers). That is not
one of the four failure classes and it did not surface in the read, but it is the
next thing I would test before committing.

The 15°-step audit findings on `seam` and `wedge` are real and fixable — those
are arbitrary diagonals (80.54°, 63.43°) that should be snapped to 75° and 60°.
