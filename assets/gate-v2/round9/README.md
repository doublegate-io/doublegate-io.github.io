# Round 9 — `baseline` in garnet and black

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build9.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure9.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round9/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round9/one-*.png
```

## Garnet decided the ground, and that is a fork worth stating

Garnet is a **dark** red. Measured against the 3:1 WCAG 1.4.11 threshold for
graphical objects, on the site's near-black `#08090c`:

| Garnet | Hex | On `#08090c` | On white |
|---|---|---|---|
| very deep | `#5C0A18` | **1.43:1** | 13.89:1 |
| deep | `#6E1423` | **1.69:1** | 11.75:1 |
| wine | `#7B1E3C` | **1.98:1** | 10.03:1 |
| gemstone | `#733635` | **2.19:1** | 9.10:1 |
| raspberry | `#9B2242` | **2.56:1** | 7.77:1 |
| light | `#A52A45` | **2.86:1** | 6.96:1 |

Every one fails on black. By the time a red clears 3:1 there (`#B03A52` 3.39:1,
`#C2334D` 3.67:1) it has become a pink or a crimson and the word garnet no longer
describes it.

So **garnet-and-black is a paper palette, not a dark-site palette** — garnet ink and
black ink on white, which is exactly where the colour comes from: wax seals, ledger
rules, law-book spine stamping, university crests. On white it measures 9–14:1 and
is genuinely excellent.

The fork, stated rather than buried: **choosing garnet makes the identity's home
ground light**, and the dark site becomes the inversion. The alternative is keeping
black as home and accepting a pink. Both are built here.

`BLACK` is `#10131a`, the site's own `--panel`, not pure `#000` — pure black on white
is harsher than any print ink and reads cheap.

## Results

| Variant | Ground | 16px | Reads back as |
|---|---|---|---|
| **ink-square** | paper | **separable, 24 scanlines, ink 0.336** | "a set of overlapping square outlines" |
| ink-garnet-front | paper | separable, 23 scanlines, ink 0.406 | "two overlapping rounded squares" |
| ink-garnet-rear | paper | separable, 23 scanlines, ink 0.406 | — |
| ink-deep | paper | separable, 23 scanlines, ink 0.406 | "rounded squares overlapping each other" |
| ink-occluded | paper | separable, 15 scanlines, ink 0.566 | "two overlapping rounded squares" |
| ink-mono-black | paper | **marginal**, 1 colour, ink 0.406 | — |
| dark-garnet-front | dark | separable, 23 scanlines, ink 0.406 | "a rounded square with a smaller square overlapping it" |
| dark-true-garnet | dark | separable, 23 scanlines, ink 0.406 | "one white/light and one **maroon/dark red**" |

**`ink-square` is the best-measuring mark of all 81 drawn so far** — 24 separating
scanlines at ink 0.336, beating `baseline` on both counts and `caret` (0.281 / 14
scanlines) on separability. Square corners, no radius. It reads as a plate or a
seal rather than a UI card, which was the standing affordance risk on this mark.

Three findings beyond the leader:

**Two inks state the order for free.** `knockout` needed a background-coloured gap
to say which square was in front, at +0.035 ink and a themed class to keep in sync.
With garnet crossing black, the colours do it alone — the crossing stops being mud
because the two lines are no longer the same colour. `ink-garnet-front` gets
knockout's ordering at baseline's ink and with no gap to maintain.

**The mono control proves garnet is earning its place.** `ink-mono-black` is the
identical geometry in one ink, and it drops to **marginal** at 16px. The second
colour is not decoration here; it is what makes the mark separable.

**Opaque occlusion costs too much.** `ink-occluded` removes the crossing entirely by
giving the front square a paper fill — and pays 15 scanlines and ink 0.566 for it.
Not worth it when two inks already resolve the order.

`dark-true-garnet` is included as evidence rather than as a candidate: true garnet on
black at 1.98:1, which the vision read describes as *"maroon/dark red"* — visible in
a 128px preview, and exactly the kind of thing that vanishes in a 16px tab.

## Recommendation

`ink-square` on paper, garnet front over black. It is the best-measured mark in the
project, audit-clean, and the colour is doing structural work rather than sitting on
top of it.

What that commits to: the identity's home ground becomes white, and the dark site
needs an inversion where garnet is replaced by `#C2334D`. That substitution is
already drawn (`dark-garnet-front`) and it is a visibly different colour — worth
looking at both panes in the gallery before settling, because a brand whose colour
changes between grounds is a real cost to weigh against garnet being the right
colour.
