# Round 12 — the portrait mark: deeper overlap, visible on both grounds

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build12.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure12.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round12/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round12/one-*.png
```

## "Similar colours, visible on both grounds" hits a wall — with numbers

The request implies two fixed colours, both fully visible on dark and light. That is
mathematically impossible where the strokes touch:

- A colour clears 3:1 on **both** grounds only if its luminance sits in the band
  `[0.108, 0.300]`.
- Two colours inside that band are at most **2.21:1** apart — under the 3:1
  ink-vs-ink gate (WCAG 1.4.11 applies to what adjoins, and these strokes cross).

So no two fixed colours can satisfy all four constraints at once. One has to give,
and the honest construction is **one constant + a partner per ground**:

| Role | Colour | dark | white | vs granat | vs ink |
|---|---|---|---|---|---|
| **the constant** | `#2563eb` blue 600 | **3.85:1** | **5.17:1** | **3.14:1** | **4.25:1** |
| paper partner | `#0A1F44` granat | 1.23:1 | 16.25:1 | — | — |
| dark partner | `#e6e9ef` ink | 16.37:1 | 1.22:1 | — | — |

Blue 600 is the only value in the family that clears 3:1 on all four counts, so it
appears in every render and the brand reads as the same mark on both grounds — only
its **role** changes (front on paper, rear on dark).

## The overlap ladder, measured

Offset 8 = round 11's `r-3x2-vert`. Smaller offset = deeper overlap.

| Variant | Offset | 16px | Reads back as |
|---|---|---|---|
| v-8 | 8 | 21 scanlines, ink 0.391 | "**phones or tablets** stacked" |
| **v-7** | 7 | 20 scanlines, ink 0.402 | "**stacked documents or windows**" |
| **v-6** | **6** | **19 scanlines, ink 0.398** | "**a document or page**" |
| v-5 | 5 | 19 scanlines, ink 0.387 | "**layered documents**" |
| v-4 | 4 | 14 scanlines, ink 0.414 | "a **pill or capsule**" — fused |
| v-6-rx4 | 6, rx4 | 19 scanlines, ink 0.398 | — |
| dark-v-6 | 6 | 19 scanlines, ink 0.398 | "two overlapping rounded rectangles" |

**Two predictions held, one better than expected.**

**The phone read died exactly where "a little more" lands.** At offset 8 the vision
read is *"phones or tablets"* — the device affordance that made portrait risky in
round 11. At 7 it becomes *"stacked documents or windows"*, at 6 *"a document or
page"*. A phone-stack icon needs clear air between the two devices; deeper overlap
makes the pair read as one layered object. The user's instinct was right.

**Ink stayed near-flat.** Round 10 measured 8→6 costing ink 0.336→0.531 on the
*square* mark. The portrait at the same depths ran 0.391→0.414 — because the 13px
portrait is narrower, the crossing region is a smaller fraction of the whole mark.
The predicted cost barely materialized.

**Offset 4 is the fusion boundary.** It reads as *"a pill or capsule"* — one shape,
both rects gone, 14 scanlines. The ladder's floor is real and it is one step below
the pick.

## The pick

`logo-themed-v-6.svg` — portrait 13×20, rx2, offset 6, one file:

- **paper**: granat `#0A1F44` rear + blue 600 `#2563eb` front
- **dark**: blue 600 rear + ink `#e6e9ef` front

19 separating scanlines at 16px, ink 0.398, 8/8 audit-clean, reads as *a document*,
and the constant-plus-partner construction keeps every render fully visible on its
ground.

`v-5` is the runner-up: same 19 scanlines at the lowest ink of the round (0.387),
deeper still. `v-7` buys one more scanline at the cost of the phone-adjacent read.

**Known trade, stated rather than hidden:** a mark that reads as "a document" is
generic-adjacent — documents are the most common icon subject in software. The
two-rectangles-interlocking read of round 11's landscape 3:2 was more distinctive;
the portrait trades that for the document association. If "document" is the *wrong*
association for the product, the landscape `themed-3x2` from round 11 remains the
alternative, and it is not going anywhere.