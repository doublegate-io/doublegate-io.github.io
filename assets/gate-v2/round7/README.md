# Round 7 — the channel family, pushed to exhaustion

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build7.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure7.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round7/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round7/one-*.png
```

Eight variants on one stance, every one two elements and deliberately **not
left-right symmetric** — because round 6 established that symmetry manufactures
the letter (symmetric void → `H`, stepped head → `E`). Angles snapped to the 15°
step from the start, which was outstanding work from round 6.

## Results

| Variant | 16px | Audit | Reads back as |
|---|---|---|---|
| interlock | separable, 19 scanlines, ink 0.566 | **CLEAN** | "the letter **E**… a stylized **M**" |
| wicket | separable, 14 scanlines, ink 0.57 | **CLEAN** | "a stylized lowercase [letter]" |
| chamfer | separable, 12 scanlines, ink 0.496 | 1 angle | "a letter **P** or a flag/banner" |
| swung | separable, 12 scanlines, ink 0.477 | 2 findings | "**quotation marks**… a stylized **II**" |
| funnel | separable, 8 scanlines, ink 0.68 | 1 angle | "a letter **M** or a mountain peak" |
| stagger | separable, 8 scanlines, ink 0.742 | **CLEAN** | "the letter **E**" |
| shear | marginal, 6 scanlines, ink 0.438 | 2 angles | "a stylized **Z** or **N**" |
| slip | **FUSED**, 0 scanlines, ink 0.633 | 1 angle | — |

## The finding: the channel stance is exhausted, and asymmetry was not the cure

**Eight for eight read as letters or punctuation.** E, M, P, Z, N, II, quotation
marks, a lowercase something. Not one escaped, despite every variant being
deliberately asymmetric and structurally different from the others — rotational,
sheared, staggered, meshed, chamfered, overlapped, funnelled, nested.

Tallied across all three rounds that touched this stance, thirteen variants:

| Outcome | Variants |
|---|---|
| **read as a letter or punctuation** | `channel` H · `channel-jambs` E · `channel-threshold` H · `interlock` E/M · `wicket` lowercase · `chamfer` P · `swung` quote marks · `funnel` M · `stagger` E · `shear` Z/N — **10** |
| escaped the letter read | `channel-ajar` ribbon/bookmark · `channel-ajar-both` ribbon/lightning — **2** |
| fused before it could be read | `slip` — **1** |

That corrects what round 6 concluded. Asymmetry did break the `H` on the ajar
variants, and I generalised it into a rule — *symmetry manufactures the letter*.
Eight asymmetric variants later, the rule is too weak. The real constraint is
structural and it is about the stance itself:

> **Two vertical masses with a void between them is what a letter IS.** Nearly
> every glyph in a Latin typeface is exactly that: vertical strokes with counters
> and gaps between them. Placing two masses side by side puts the mark inside the
> alphabet's own design space, so the eye resolves it as type before it resolves
> it as an object. Asymmetry only changes *which* letter.

The two escapes are informative, and they escaped the same way: `channel-ajar` and
`channel-ajar-both` both replaced a straight-sided void with a **wedge** — a void
that is *wider at one end than the other along its whole length*. No Latin letter
has a tapering counter. Neither read as type; both read as "a folded ribbon".

So the productive residue of thirteen variants is one narrow rule: **if the gate
must be a void, the void has to taper.** A slot, a dogleg, a zigzag or a
parallelogram will find a letter. A wedge will not.

`channel-ajar-both` (round 6, ink 0.352, 17 scanlines) remains the best mark this
stance has produced, and this round did not beat it. Eight tries, all heavier —
ink 0.438 to 0.742 against its 0.352.

## Recommendation

Stop developing the channel. It has had three rounds and thirteen variants, the
failure is structural rather than a matter of refinement, and the one configuration
that works is already drawn.

The field leaders across seven rounds and 45 marks:

| Mark | Round | Ink | Scanlines | Reads as |
|---|---|---|---|---|
| **caret** | 5 | **0.281** | 14 | an arrow / a mountain peak |
| **channel-ajar-both** | 6 | 0.352 | 17 | a folded ribbon / lightning bolt |
| **offset** | 4 | 0.406 | 23 | two overlapping squares, a window-like frame |
| keystone-marked | 6 | 0.398 | 8 | a trapezoid with a diamond inside it |

Note what the three leaders have in common and the thirteen channel variants do
not: **none of them is a pair of side-by-side vertical masses.** A caret is an
apex, `offset` is two nested squares, `keystone-marked` is one trapezoid.
