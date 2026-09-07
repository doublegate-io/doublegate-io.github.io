# Round 10 — `ink-square` in granat (navy) and blue

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build10.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure10.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round10/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round10/one-*.png
```

Geometry is round 9's `ink-square`, unchanged. Colour is the only variable.

## Granat has an escape garnet did not

Navy alone cannot sit on the dark site — same story as garnet:

| Navy | Hex | On `#08090c` | On white |
|---|---|---|---|
| near-black | `#0F172E` | **1.12:1** | 17.76:1 |
| **granat** | `#0A1F44` | **1.23:1** | **16.25:1** |
| blue 950 | `#172554` | **1.35:1** | 14.69:1 |
| royal | `#1B2F6B` | **1.58:1** | 12.61:1 |
| blue 800 | `#1E3A8A` | **1.92:1** | 10.36:1 |
| blue 700 | `#1E40AF` | **2.28:1** | 8.72:1 |

But navy and a mid blue are the **same hue at two values**, so the pair can swap
roles between grounds and the identity still reads as blue in both places. Garnet
had no such partner — it had to become a pink.

Of every lighter blue tested, **exactly one clears 3:1 on both grounds**:

| Blue | On `#08090c` | On white | |
|---|---|---|---|
| **blue 500 `#3b82f6`** | 5.41:1 | **3.68:1** | **the only one** |
| indigo 400 `#818cf8` | 6.67:1 | 2.98:1 | misses by 0.02 |
| blue 400 `#60a5fa` | 7.83:1 | 2.54:1 | fails |
| sky 500 `#0ea5e9` | 7.18:1 | 2.77:1 | fails |
| cyan 400 `#22d3ee` | 11.02:1 | 1.81:1 | fails |

`#3b82f6` is load-bearing. It appears unchanged wherever the mark goes, so the
**role** carries the theme instead of the colour:

- **paper** — granat `#0A1F44` rear, blue `#3b82f6` front
- **dark** — blue `#3b82f6` rear, ink `#e6e9ef` front; granat drops out

That is materially better than round 9's garnet plan, where the brand colour itself
changed between grounds. `logo-themed.svg` is one file that does both.

## Ink-vs-ink is a second, independent gate — and I failed it first

The squares cross, so the two strokes touch. Contrast against the ground is not
sufficient.

I drew a two-navy variant — `#0A1F44` and `#12275C`, 16.25:1 and 14.28:1 on white,
both excellent. Against **each other** they are **1.14:1**. The vision read is the
proof: `ink-two-navy` comes back as *"a cluster of **three** overlapping squares"* —
the strokes merged at the crossing and manufactured a third shape that isn't there.
`ink-navy-only` (one ink) does the same: *"a set of **three** overlapping squares."*

Measured separations for the pairs that work:

| Pair | Ink-vs-ink |
|---|---|
| granat vs blue `#3b82f6` | **4.42:1** |
| granat vs copper `#B45F06` | 3.54:1 |
| granat vs `#12275C` | **1.14:1** — fails |

`audit-geometry.js` now checks this. It caught `ink-two-navy` on the next run;
rounds 8–9 still report 22/23, so nothing was loosened retroactively.

## Results

| Variant | Ground | 16px | Reads back as |
|---|---|---|---|
| **themed** | both | **separable, 24 scanlines, ink 0.336** | "a set of overlapping squares" |
| ink-navy-blue | paper | separable, 24 scanlines, ink 0.336 | "squares with cut corners or overlapping outlines" |
| ink-navy-copper | paper | separable, 24 scanlines, ink 0.336 | "a **window** or a pair of overlapping frames" |
| dark-blue-ink | dark | separable, 24 scanlines, ink 0.336 | "squares offset/shifted relative to each other" |
| ink-navy-only | paper | **marginal** | "**three** overlapping squares" |
| ink-two-navy | paper | separable but 1.14:1 ink-vs-ink | "**three** overlapping squares" |
| dark-navy-proof | dark | — | "**a simple outlined square**" |

`dark-navy-proof` is the sharpest evidence in the round. Granat on black at 1.23:1
doesn't degrade — **it disappears**, and the vision read describes a single square
because only the blue one survived. That is what a 1.23:1 ratio means in practice.

Copper `#B45F06` (4.34:1 dark, 4.58:1 white, 3.54:1 vs navy) works as a second
**hue**, and would let the two gates read as different *kinds* of check rather than
two states of one. It reads as "a window", which is slightly more UI-flavoured than
the navy/blue pair. Emerald `#059669` passes every number and is excluded on
**meaning**: green beside blue reads pass/info, and these squares are sequential
stages.

## Two build traps worth recording

Both were caught by measuring against round 9 rather than trusting the preview:

**Offset.** Coordinates must be `3,3` and `11,11` — an 8px offset. I first drew
`4,4 / 10,10` (a 6px offset borrowed from round 6's `tight`) and it measured ink
0.531 / 20 scanlines instead of 0.336 / 24. A tighter overlap puts more stroke inside
the crossing region and costs both numbers.

**Primitive.** Must be `<rect>`, not `<path>` with `stroke-linejoin="miter"`.
Identical box, identical stroke width, and the path version measured **ink 0.406**
against rect's **0.336** — miter joins project past the corner and add paint a rect's
own corners do not.

## Recommendation

`logo-themed.svg`. One file, 24 separating scanlines at ink 0.336, audit-clean, and
correct on both grounds without the brand colour changing. Granat is the paper
weight, blue is the constant, ink takes over on dark.
