# Round 5 — six untried stances, and one rule rewritten

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build5.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure5.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round5/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round5/one-*.png
```

Round 4 fixed the *level* of the problem — stop drawing the mechanism, one or two
elements, no diagram. But all six of its marks were solid geometric primitives:
square, triangle, ring. This round spends the same element budget on stances that
were unavailable while the marks were still diagrams.

## Results

| Mark | El. | 16px | Audit | Reads back as |
|---|---|---|---|---|
| **caret** | 2 | **separable, 14 scanlines, ink 0.281** | 1 angle off 15° | "an upward-pointing triangle with a horizontal line beneath it, resembling an arrow or a **mountain peak**" |
| **deboss** | 1 | marginal, 12 scanlines, ink 0.469 | **CLEAN** | "a square containing a diamond shape" |
| chainlink | 2 | separable, 8 scanlines, ink 0.484 | **CLEAN** | "two overlapping rounded rectangles" |
| channel | 2 | marginal, 18 scanlines, ink 0.625 | **CLEAN** | "a bold **H** letterform" |
| notchpair | 1 | marginal, 4 scanlines, ink 0.547 | 4 angles off 15° | "an **hourglass** or **bowtie** shape" |
| keystone | 1 | **FUSED**, 0 scanlines, ink 0.406 | **CLEAN** | "a **play button** or a trapezoid" |

`caret` is the strongest measured mark produced in five rounds — lightest ink
(0.281) with 14 separating scanlines.

## The finding that rewrites a rule

This project's standing rule, written after `countersigned` read as a tick twice:

> **any two strokes meeting at a low vertex read as a tick**, whatever direction
> each travels, because the eye resolves the lower junction first.

`caret` was built to test whether that rule is about the *strokes* or about the
*junction's position*. A proofreader's caret is two strokes meeting at a vertex —
but the vertex is at the **top**.

It reads as *"an arrow or a mountain peak."* **Not a tick.** So the rule was
under-specified: the tick-read comes from a **low** junction specifically, and
inverting it escapes the trap entirely. That widens what is drawable — an apex is
available, a valley is not.

`caret` also earns its meaning by inheritance rather than explanation, which is
what Rand's principle asks for: the caret is the editorial mark for *"insert this
here"*, and has meant that in manuscript correction for centuries. It is
appropriate to an admission gate without depicting one.

## Three failures, each of which teaches something

**`channel` reads as "H".** The FedEx principle — meaning in the void — applied as
literally as possible: two blocks, and the gates are *only* the negative space
between them. But two vertical masses with a gap between them **is** a capital H.
This is a fifth failure class, and it is the mirror image of class A: not "the
drawn shape is a letter" but **"the negative space is a letter."** Negative-space
marks must have their void checked as a glyph, not just the ink.

**`keystone` FUSED at 16px** — 0 separating scanlines, the worst possible result,
and it reads as a **play button**. Two lessons. A single solid convex shape can
never separate: there is no interior void, so every scanline crosses one unbroken
run (the same structural result as the solid triangle in the naming set). And a
trapezoid narrower at the top is close enough to a triangle to inherit the play
button — the single most-used glyph in software.

**`notchpair` reads as an hourglass/bowtie.** Cutting one form twice, on opposite
edges at different heights, was meant to be the most reduced statement of two
gates. But two opposing notches pinch the waist, and a pinched waist is an
hourglass. Symmetrical subtraction from opposite sides produces a new silhouette
rather than a marked one.

## Where this leaves the field

Across five rounds and 30 marks, two candidates now lead on measurement *and*
survive an unprompted read without collapsing into something else:

- **`caret`** (round 5) — ink 0.281, 14 scanlines, reads as an arrow/peak, borrows
  a working editorial symbol. One angle to snap from 56.31° to 60°.
- **`offset`** (round 4) — ink 0.406, 23 scanlines, the only mark to pass the grid
  audit untouched, reads as "two overlapping squares forming a window-like frame".

`deboss` is worth keeping in view as the one-element option: it answers why round
4's `bite` fused — an impression *inside* the mass creates interior negative space,
where a notch on the outer edge only removes silhouette. It reads cleanly ("a
square containing a diamond") and passes the audit, but 12 scanlines is mid-field.

Still open on `offset`: two nested squares are a common UI affordance
(copy/duplicate/layers). It has not surfaced in a read yet, and it is the next
thing to test before committing to that one.
