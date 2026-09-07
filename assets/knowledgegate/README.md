# KnowledgeGate — mark candidates

Four marks for the renamed product, drafted at the same geometry and offered side
by side. **None is wired into the site.** The live mark is still `assets/logo.svg`
(two arches, doublegate); these are proposals pending the naming decision, which is
evidenced in the design repo at `docs/research/14-the-knowledgegate-name.md`.

Regenerate everything — logos, wordmarks, social cards, preview:

```bash
python3 assets/knowledgegate/build.py
open assets/knowledgegate/preview.html    # every size, both themes
```

One geometry function per variant feeds all three assets, so a favicon and a
1200×630 card cannot drift apart.

## The four

| Variant | Stance | Book? |
|---|---|---|
| `arch-book` | The live gate arch, with an open book passing under it | yes, the clearest |
| `posts-book` | Two posts — first gate, second gate — holding a closed book | yes, as a silhouette |
| `spine-book` | The book *is* the gate: red spine to pass, signed line first inside | yes, most literal |
| `arches` | The incumbent two arches, no book, under the new name | no |

`arch-book` is the recommendation. It is the only one that carries both halves of
the name in one shape, and it keeps continuity with what is live. `arches` is the
fallback if a book is judged too literal for infrastructure. `posts-book` is the
one that keeps *two of something* countable, which the single arch gives up.

## What the size ladder decided

Ranked blind at 16/22/32/48/64/128px on `#08090c` and `#ffffff`, three rounds.
Recorded so nobody re-argues it from taste:

- **An arch whose span matches the object beneath it is a lowercase "n".** First
  draft of `arch-book` was read as one at 16–22px. The fix is not colour — it is
  making the book narrower than the arch and leaving daylight between them, so the
  eye sees an object under a canopy instead of a shoulder and a stem.
- **`#e6e9ef` page fills are invisible on a light browser tab.** Every ink element
  now flips through `prefers-color-scheme` inside the SVG, including the spine
  notch — a notch cut in the dark background colour shows as a dark bar on white.
  That embedded style block is the only theming mechanism that works in a favicon.
- **Three page lines fill in at 16px.** `spine-book` originally drew three; the
  gaps closed and the mark became a solid rectangle. Two heavier lines survive.
- **A book below ~22px is a silhouette, nothing more.** Page detail is dropped
  rather than drawn finer, because finer strokes disappear instead of shrinking.
- **Do not trust an eyeball read of 16px — measure it.** `measure.js` (copied here
  from `assets/naming-options/`) rasterises each mark and counts scanlines that
  separate two inked runs. Run `node assets/knowledgegate/measure.js`. It
  overturned a claim previously written in this file: `arches` was described as
  fusing into one wavy shape at 16px, and it does not — 11 separating scanlines,
  the same order as the rest of the set. All four variants measure separable.
  `posts-book` is the closest to trouble on ink coverage (0.50 at 16px).

## Preview correctness

`force()` resolves `prefers-color-scheme` in **both** directions. Headless Chrome
defaults to light, so a dark preview pane that leans on the media query renders
dark ink on dark ground and the marks look like they are missing elements. This
file had that bug; a vision review of the dark pane before the fix was measuring
the harness, not the mark.

## Open, not resolved

Red and green read as fail/pass to every engineer alive, and here the two gates are
peers — first authority and second authority — not a bad one and a good one. The
palette is kept for site consistency, but it says something the mechanism does not.
Worth deciding deliberately rather than inheriting.
