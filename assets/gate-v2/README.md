# doublegate mark, v2 — improving the shipped logo

Candidate marks only. **Nothing here is wired into the site**; the live mark is
still `assets/logo.svg`. Wiring is a separate decision.

```bash
python3 assets/gate-v2/build.py     # round 1 — six rivals, arch family
python3 assets/gate-v2/build2.py    # round 2 — six rivals, arch-free
python3 assets/gate-v2/build3.py    # round 3 — four rivals, all classes dodged

CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure3.js   # 16px separability, measured not eyeballed
python3 .tmp/ask_open.py            # semantic read, one open question
```

## Why this exists

The live mark won its round honestly, and its case study left two defects on the
record rather than dressing them up:

1. **It says "two gates" but not "sequence."** The product is admission *then*
   ratification — ordered. The shipped `wide` variant is symmetric and carries no
   order. The `offset` variant ranked equally on the two-gates question and would
   have carried it; `wide` was chosen on 16px robustness alone.
2. **Red/green reads fail/pass.** Both gates are legitimate stages of one
   passage, not a bad one and a good one.

Both became the brief for this directory.

## The finding that matters: the shipped mark reads as "nn"

The live mark's case study recorded that a wide gap defeated the lowercase-`m`
trap. **It did not.** Asked a single open question with no menu of answers —
*"what is it?"* — the shipped mark comes back as:

> "two rounded shapes that look like the letter n … like two n letters"

The wide gap converted a one-letter read (`m`) into a two-letter read (`nn`), and
nobody re-asked after round 3 because the semantic question was considered
closed. It was not. **A round-topped shape with two descending legs is a
lowercase n**, and no amount of spacing, hue or height fixes it.

## Four structural failure classes

Fourteen rivals over three rounds, each read with one unprompted open question:

| Class | Silhouette | What it reads as | Rivals lost to it |
|---|---|---|---|
| **A** | round top + descending legs | lowercase n / u / horseshoe / E | `live`, `depth`, `step`, `transit`, `stack`, `numbered`, `notch` |
| **B** | stacked horizontal bars | bar chart, hamburger menu, list | `ledgerline` |
| **C** | circle, especially with a tail | Q, question mark, map pin | `twokeys` |
| **D** | narrow centred vertical stack | a person / figure icon | `turnstile` |

Two further reads that are not classes but are disqualifying: an **X** across a
mark reads as *reject* (`countermark`), and any two strokes meeting at a low
vertex read as a **tick** (`relay`), regardless of their directions.

This table is the durable output of the work. It is worth more than another six
drawings, because it rules out the shapes before they are drawn.

## Result: `twoseals`

The only rival of fourteen to clear all four classes. Read back as:

> "a document or file icon containing two diamonds."

A record carrying two independent seals — not a door. An object with two seals on
it cannot become an `n`, a chart, a pin, or a person, because its outer form is a
chamfered rectangle and its marks are lozenges.

- **Sequence** is stated by depth of strike: the slate seal is struck flush into
  the edge (passed, absorbed into the record), the green one still stands proud.
- **Measured at 16px:** ink 0.328, 18 separating scanlines, 4 colours — separable,
  and lighter than the shipped mark's 0.43.

Open, and worth saying: "document icon" is a *generic* read. It is not a stock UI
icon in the disqualifying sense — no OS ships a two-sealed tablet — but the
container is ordinary, and the seals are doing all the distinguishing work.

## Palette: depth, not hue

Red/green is dropped. The two gates are stages of one passage, so they take one
hue at two depths:

| Token | Colour | Means |
|---|---|---|
| slate | `#64748b` | the authority already passed |
| green | `#34d399` | the authority that admits |
| amber | `#fbbf24` | present, but not yet admitted |

Depth-not-hue also survives greyscale, which red/green does not — a favicon in a
monochrome tab strip keeps its order.

## Production-grade construction, measured against published specs

Separability (`measure3.js`) answers *"do the elements stay apart when
rasterised"*. It says nothing about whether the drawing is **constructed**
properly. `audit-geometry.js` checks that, and every rule in it comes from a
published icon system rather than from taste:

- **[IBM Design Language — UI icons](https://www.ibm.com/design/language/iconography/ui-icons/design/)**
  is the closest published spec to what this project already does: icons drawn on
  a **32×32 pixel grid** — our exact viewBox — and scaled down linearly. Its rules
  are checkable: snap artwork to the grid and *"avoid random decimal points in the
  x and y coordinates"*; reserve **2px padding**; use **one stroke weight per
  icon** (*"a mix … looks like a mistake"*); corner radius **2px or a multiple of
  two**; angles in **multiples of 15°**, since 45° anti-aliases evenly.
- **[Material Design system icons](https://m2.material.io/design/iconography/system-icons.html)**
  — designed at 100% scale on a fixed grid for pixel-perfect accuracy.
- **[Favicon production guidance](https://favicon.now/guides/design)** — 10-15%
  edge space as a starting range, and *"favicon design is reduction design"*:
  heavier strokes and fewer details than the master logo are normal, not a
  compromise.

### What the audit found on the first run

```
logo.svg           6 coords inside the reserved 2px padding
logo-countermark   mixed stroke weights: 2.8, 3.4
logo-relay         mixed weights 2.2/3.4 · radius 1.4 off the 2px step · 52.13° angles
logo-twoseals     12 coords off both the pixel and half-pixel grid (3.2, 3.6 …)
logo-notch         CLEAN
```

Four of five marks had real construction defects, including the winner, and none
of them were visible to the eye or to the separability measurement.

**Fixing the grid made the mark better, not just tidier.** Rebuilding `twoseals`
on whole-number offsets (3 and 4 instead of 3.2 and 3.6) and a single 2px stroke
dropped ink **0.328 → 0.262** while separability held at 18 scanlines. Cleaner
construction *is* a lighter mark.

The audit is advisory, not a gate. `assets/logo.svg` reaching into its padding is
exactly the case IBM allows — extend into the padding for additional visual
weight — but it should be overruled deliberately and in writing, which is what
this paragraph is.

## svgo: useful, and dangerous by default

`npx svgo --multipass` on the winner: **36% smaller**, and it

1. deleted `role="img"`,
2. inlined `class="ink-s"` as a hardcoded `style="stroke:#e6e9ef"`, and
3. **removed the entire `@media (prefers-color-scheme)` block.**

The result is a near-white mark with no light-theme branch — invisible on a light
browser tab. That is this project's single most-repeated defect, reintroduced by
the tool meant to polish the output. An optimiser that silently undoes a fix you
made twice is worse than no optimiser.

`svgo.config.mjs` disables the offending plugins by name, each with the reason it
costs us. With it: **2% smaller**, everything preserved, and the optimised file
measures byte-identical to the source at 16/22/32px (verified by running it
through `measure3.js` beside the original).

The honest conclusion is that **svgo has almost nothing to win here** — 652 bytes
down to 639. These marks are hand-written and already near-minimal. Keep the
config for the day someone pastes in an Illustrator export, where the same
plugins would strip 90% of genuine cruft.

## Rules carried over, not rediscovered

- **Never ask a leading question.** A first pass asked five numbered questions,
  one of which was *"does it read as a letter?"* — and all twelve rivals came back
  as letterforms. That is one leading question answered twelve times, not twelve
  findings. `ask_open.py` asks *"what is it?"* and nothing else; a letterform read
  that survives there is real. The original `m` discovery was credible precisely
  because it arrived unprompted.
- **Measure 16px, do not look at it.** `measure3.js` counts ink ratio, distinct
  colours, and scanlines separating two inked runs. Three vision passes over one
  identical sheet previously gave three different verdicts.
- **Sheet height must be derived from the rival count.** A hardcoded screenshot
  height silently crops the newest candidates and produces a confident vision
  report about missing elements.
- **One mark per image for the semantic read.** A 900×3000 sheet makes the model
  summarise the page instead of answering about each mark.
- **Resolve `prefers-color-scheme` in code, both directions.** Headless Chrome
  defaults to light, so a dark pane renders dark ink on dark ground.
