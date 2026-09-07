# Round 6 — keystone and channel, developed with detail

Candidate marks. **Nothing here is wired into the site.**

```bash
python3 assets/gate-v2/build6.py
CHROME_PATH=~/.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome \
  node assets/gate-v2/measure6.js
node assets/gate-v2/audit-geometry.js assets/gate-v2/round6/logo-*.svg
python3 ~/.hermes/skills/creative/brand-mark-design/scripts/ask_open.py \
  assets/gate-v2/round6/one-*.png
```

Requested: keystone with more detail, channel with more detail, and channel with
one side of the door slightly opened. This deliberately relaxes round 4's
one-or-two-element budget, so every variant prints its element count and this file
records what the detail bought and what it cost.

## Results

Parents to beat: `keystone` FUSED at 0 separating scanlines, reads "play button".
`channel` marginal at 18 scanlines, reads **"a bold H"**.

| Variant | El. | 16px | Audit | Reads back as |
|---|---|---|---|---|
| **channel-ajar-both** | 2 | **separable, 17 scanlines, ink 0.352** | 4 angles off | "a lightning bolt or a folded ribbon" |
| **channel-ajar** | 2 | separable, 17 scanlines, ink 0.516 | 2 angles off | "a folded ribbon, a bookmark, or a play button" |
| **keystone-marked** | 1 | marginal, 8 scanlines, ink 0.398 | 1 angle off | "a white trapezoid with a black diamond centered inside it" |
| keystone-joints | 1 | marginal, 6 scanlines, ink 0.43 | 5 angles off | "a funnel… two dark stripes giving a sense of depth" |
| channel-jambs | 2 | marginal, 18 scanlines, ink 0.594 | **CLEAN** | "a stylized **E**" |
| channel-threshold | 3 | separable, 15 scanlines, ink 0.664 | **CLEAN** | "a stylized **H** with a horizontal bar beneath it" |
| keystone-seated | 3 | **FUSED**, 0 scanlines, ink 0.492 | 3 angles off | "a **bell** or a beaker/flask" |

## The hypothesis held: asymmetry breaks the letter

Both predictions were right, and they were right for the stated reason.

**Detail fixed the fusion.** `keystone` scored 0 separating scanlines because a
single solid convex shape has no interior void, and interior void is what survives
downscaling. Adding an interior feature was not decoration — it was the only
available fix. `keystone-marked` goes **0 → 8 scanlines** with one element and
*less* ink than the parent (0.398 vs 0.406).

**An opened leaf broke the H.** H is perfectly symmetric with two straight
uprights. A void with one straight side and one 60° side cannot be that letter, and
both ajar variants confirm it — "a folded ribbon", "a lightning bolt", no letter
anywhere. `channel-ajar-both` is the strongest: **17 scanlines at ink 0.352**,
against the parent's 18 at 0.625. Nearly half the paint for the same separability.

**The control proves the mechanism rather than the styling.** `channel-jambs` kept
both sides symmetric and only stepped the heads — and it became **"a stylized E"**.
Same failure class, new letter. So it is the *symmetry* that manufactures the
letter, not the plainness of the blocks. That is a sharper statement of class E
than round 5 could make.

## The result that inverts the round's own assumption

**More detail made things worse, twice, and both times by adding a third element.**

- `keystone-seated` (3 elements) **FUSED at 0 scanlines** — no better than the bare
  trapezoid it was meant to improve — and reads as **"a bell or a beaker/flask"**.
  Flanking the keystone with two cut-back stones produced a bell silhouette,
  because the outer profile is what the eye reads, not the internal joins.
- `channel-threshold` (3 elements) is the **heaviest mark in the round** at ink
  0.664, and it went straight back to **"a stylized H with a horizontal bar
  beneath it"** — the exact read the round existed to defeat. Adding a floor and
  an artifact re-symmetrised the composition.

So the useful distinction is not *detail vs. no detail*. It is **interior detail
vs. added elements**:

> Interior detail (a void cut inside an existing mass) improves both separability
> and ink. A third element re-symmetrises the composition and reintroduces the
> letter read — and it is the failure mode that killed rounds 1-3.

The one-or-two-element budget survives this round intact, with a better reason
behind it than "Rand said so".

## Where this leaves the field

Across six rounds and 37 marks, three candidates now lead on measurement *and*
survive an unprompted read:

| Mark | Round | Ink | Scanlines | Reads as |
|---|---|---|---|---|
| **caret** | 5 | **0.281** | 14 | an arrow / a mountain peak |
| **channel-ajar-both** | 6 | 0.352 | 17 | a folded ribbon / lightning bolt |
| **offset** | 4 | 0.406 | 23 | two overlapping squares, a window-like frame |

`keystone-marked` is the best one-element option (8 scanlines, ink 0.398, reads
literally as what it is) and the only surviving mark that keeps the gate lineage.

**Cheap work outstanding:** every variant except two carries angles off the 15°
step — 65.22°, 75.96°, 33.69°. Those are arbitrary diagonals that should snap to
60°, 75°, 30°. It is a one-line fix per path and it lowers anti-aliasing noise at
16px, which is exactly where these marks are judged.
