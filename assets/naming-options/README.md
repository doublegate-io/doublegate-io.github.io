# Naming shortlist — one mark per candidate name

Six marks, one per name on the shortlist in the design repo at
`docs/research/15-naming-options.md`. **None is wired into the site.** These are
not variants of one brand — the comparison is between *metaphors*, so that a
naming decision can be made looking at the mark it would have to live with.

```bash
python3 assets/naming-options/build.py                      # regenerate all assets
node    assets/naming-options/measure.js                    # objective 16px legibility
open    assets/naming-options/preview.html                  # every size, both themes
```

## The twelve

| Mark | Name it serves | What it draws |
|---|---|---|
| `adlectio` | adlect.io | Items on the roll, one arriving — admission by a separate authority |
| `escrow` | KnowledgeEscrow | Two parties bracketing a held artifact neither can reach alone |
| `countersigned` | Countersigned | Two signatures stacked, each on its own rule |
| `correctorium` | Correctorium | Exemplar and copy, the copy carrying the corrector's mark |
| `lectorium` | Lectorium | A lectern with a leaf on it — the reading room |
| `holdshelf` | HoldShelf | Items on a shelf, with a gate line running past it |
| `accession` | Accession | Spines on a shelf rule, one tilted item still outside |
| `assayoffice` | AssayOffice | A hallmark punch: a lozenge with the fineness struck inside |
| `poundlock` | PoundLock | A canal lock from above — a gate at each end, load between |
| `knowledgediode` | KnowledgeDiode | The diode glyph, rotated vertical |
| `agentlibrarian` | AgentLibrarian | An open book with a date stamp struck across the corner |
| `knowledgeporter` | KnowledgePorter | A lodge hatch with something presented on the counter |

`countersigned` is the recommendation, matching the evidence repo's shortlist. It is
also the lightest mark in the set at ink 0.234 — two signatures and two rules,
nothing else.

## Measure the small sizes, do not look at them

`measure.js` rasterises each mark at 16/22/32px and counts:

- **ink** — fraction of pixels painted. Above ~0.45 a 16px mark is closing up.
- **col** — distinct quantised colours. High counts mean antialiasing is inventing
  intermediate tones, which is what "muddy at favicon size" actually is.
- **gapR / gapC** — scanlines that cross background *between* two inked runs. This
  is the real definition of "the elements stay separable"; a blob has none.

This exists because eyeballing 16px does not work, and neither does asking a
vision model. Three passes over the same sheet returned three different answers on
which marks fused — including confident claims about elements that were present
and correct. The numbers settled it, and twice they contradicted the eye:

| Claim from looking | What measurement said |
|---|---|
| "PoundLock fuses into a blob at 16px" | 14 separating scanlines — the most separable of the set on the horizontal |
| "AgentLibrarian is the most legible" | 4 scanlines, ink 0.49 — **the weakest of the six** |
| "arches fuse at 16px" (KnowledgeGate set) | 11 scanlines — separable; the earlier claim was wrong |

Run it before believing any statement about small sizes, including the ones in
this file.

### Standing results

Three marks are `marginal` and the reasons are structural, not fixable by nudging:

- **knowledgediode** has `gapR 0` at every size. A solid triangle is one unbroken
  run on every row it occupies, so the horizontal axis can never separate. It
  separates fine vertically (`gapC 6`). Acceptable for a mark whose whole point is
  a single directional glyph; worth knowing before it becomes a favicon.
- **lectorium** has the same `gapR 0` for the same reason — the lectern's desk is a
  solid quadrilateral spanning the full width.
- **agentlibrarian** is the busiest in the set — an open book *plus* a stamp is two
  objects with internal detail, in 256 pixels. It reads well from 32px up.

### Defects the measurement caught that looking did not

- **`countersigned` read as a tick twice.** First draft: both strokes in the same
  diagonal. Second draft: opposite diagonals so they genuinely cross — still a tick.
  The real rule is **any two strokes meeting at a low vertex read as a tick**,
  whatever direction each travels, because the eye resolves the lower junction
  first. Abandoning the crossing for two signatures stacked on their own rules took
  it from 4 separating scanlines to 17.
- **`correctorium` breached the ink threshold** at 0.566, against the 0.45 documented
  above. A filled rectangle covering a third of a 16px field is simply too much
  paint. Outlining it brought it to 0.465 and cost nothing in meaning.
- **`holdshelf`'s barrier needed to differ in kind, not degree.** Making it thicker
  failed — a thick vertical bar among vertical bars is just another bar, and the mark
  stayed a bar chart. Running it *past* the shelf line at both ends, which no book on
  a shelf can do, is what makes it a gate.
- **`preview.png` was silently cropping.** The sheet grows one block per candidate on
  each of two panes, while `--window-size` was hardcoded — so the newest candidates
  were cut off the bottom, and a vision review reported half the light pane as "not
  visible". Height is now derived from `len(CANDIDATES)`. Same class of bug as the
  theme-resolution one below: **the harness lied, and the vision model faithfully
  reported the lie.**

## Rules carried over, not rediscovered

From `assets/knowledgegate/README.md`, and all four still bind:

- Ink fills must flip through `prefers-color-scheme` inside the SVG or they vanish
  on a light browser tab. That embedded style block is the only theming mechanism
  a favicon has.
- An arch whose span matches the object beneath it reads as a lowercase **n**.
- Three thin parallel lines fill in solid at 16px; two heavier ones survive.
- `font-family` in an **attribute** cannot contain quotes, or the SVG will not
  parse. Use the quote-free stack; keep the quoted one for `<style>` blocks only.

And one found here, which invalidated a previous round of review:

- **Resolve the media query in both directions when building a preview.** Headless
  Chrome defaults to *light*, so a dark pane that relies on `prefers-color-scheme`
  renders dark ink on dark ground, and the marks look like they are missing
  elements. The first sheet did exactly that; a vision read faithfully reported
  spines as "dark grey" and it was an artifact of the harness. Both branches are
  now stripped or substituted explicitly. `assets/knowledgegate/build.py` had the
  same latent bug and is fixed too.

## Open

Red and green still read as fail/pass while the two gates are peers — unchanged
from the KnowledgeGate set, and it applies to `poundlock` most sharply, where the
two gates are the only elements carrying colour.

`assayoffice` deliberately avoids a shield-with-tick. That shape is the
security-software icon every OS ships, and a mark that looks like a system
affordance is not a brand. The lozenge is the UK fineness-mark shape, which is
less familiar and buys distinctiveness at the cost of needing one line of
explanation.
