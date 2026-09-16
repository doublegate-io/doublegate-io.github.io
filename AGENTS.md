# site/ — Working Agreement for the Landing Site

Rules for **client-facing copy**: `pages/*.html` and the assets they carry.

Scope boundaries — this file does not repeat what these already say:

- the design repo's working agreement (private) — sourcing, honesty, the forbidden-claim lists, the
  tier boundary, terminology. **Read it first; it governs here too.** In
  particular §3b (regulatory claims), §3c (safety claims) and §5 (lead with the
  buyer's problem) are the ones this file builds on.
- [README.md](README.md) — build commands, structure, the `check.py`
  gates, diagram colour and layout mechanics.

`*.html` is **generated**. Edit `pages/*.html`, run `python3 build.py`,
then `python3 check.py`. A change made directly to a built page is lost.

**This file evolves every time site work happens here.** Every rule is a
correction that was actually made on this project.

---

## The reader

One reader funds this and it is not the person who will run it. The pitch is an
**organizational asset**: a company is already paying to teach hundreds of private
agents, and none of that learning is recoverable or shareable. Individual safety is
the enabler, never the headline (the design repo (private)).

Every page answers *whose problem is this, and does that person hold a budget?*
`for-engineers` is the one page written for the operator — and even there the
frame is what it costs them to run, not how it works inside.

---

## Hard rules

### 1. No defensive framing

The single most-corrected failure on this project. Substance survives review;
**phrasing gets rejected.** Facts, numbers and citations land readily — the
sentence shapes around them are where the work is.

Never ship:

- "why this isn't just another X"
- "we are not claiming…"
- "nothing is built yet"
- "to be clear" / "let's be clear"
- any heading of the form *"What we are not"*

Each one hands the reader a doubt they had not formed yet, then argues with it.
The reader is evaluating a purchase, not a defence.

**Refusing a claim is right; framing the refusal as a disclaimer is not.** Same
fact, both ways:

> ✗ *What we are not claiming: that contributing improves your recruiting, your
> brand, or your models. Plausible, unmeasured, and not a reason we will put in a
> business case.*

> ✓ *The business case rests on the supply line, not on goodwill. Contributing may
> well help your recruiting, your brand and your models; all three are unmeasured,
> so none of them belongs in your numbers.*

The second refuses more credit than the first and reads as confidence. Lead with
what *is* true, and let the limit follow as a consequence.

`check.py` gate 17 holds this one: it reads every section's heading and its
opening paragraph, and fails on a disclaimer in either position. The patterns it
carries are the sentences below, so a new way of framing a refusal goes into the
gate in the same commit that finds it.

### 2. Businessy, not defensive; concrete, not adjectival

The register is a serious commercial document: plain, declarative, specific. It is
not startup copy and it is not a research abstract.

- **Numbers and named sources over adjectives.** "66 firms, 7,137 knowledge
  workers" beats "extensive research". Every claim carries its primary source per
  the sourcing rule.
- **No AI tells.** delve, leverage, robust, seamless, cutting-edge, game-changing,
  unlock, empower, harness, "in today's landscape".
- **State the benefit and its cost in the same breath** — the honesty rule is also
  a *style* rule, because a benefit with its price attached reads as trustworthy
  where a bare benefit reads as marketing.

### 3. Hedges are a tone smell — audit them, do not ban them

`may`, `might`, `could` are legitimate when the uncertainty is real and named
("append-only may conflict with erasure obligations until FR-16 lands"). They are
corrosive when they hedge a thing we actually know.

Count them per page before shipping. A page with four is either describing genuine
uncertainty or losing its nerve, and only reading them tells you which.

### 4. Never internal vocabulary in visible copy

Enforced by `check.py` gate 5, so this is mechanical — but the *reason* matters:
a visitor who meets `C5`, `limbo.db` or `M3` learns that this page was not written
for them. Link *targets* may carry anything; visible text may not.

The roadmap is the one bridge tier where `FR-n` is legitimate, because those are
the public tracking handles.

### 5. Every page routes the reader onward

Enforced by gate 7. A page with no way forward is a lost reader. The route is
deliberate: `index` hooks and dispatches; each specialist page ends by handing off
to the next most likely question — `for-organizations` → `pricing`,
`for-engineers` → `evidence`, `commons` → `governance`.

### 6. The diagram carries the argument, so it carries alt text

Enforced by gate 8. The hero diagram *is* the explanation for a reader who will
not read prose. `alt=""` drops the argument entirely for anyone not seeing it.

Motion rules that were learned the hard way live in
[README.md](README.md#design-notes) — animated dots below the boxes on a
rail, never through the labels; no downscaling below 900px.

### 7. Run the gate; do not hand-roll checks

`python3 check.py` is twenty-five checks, each from a real failure. Hand-rolled
greps have missed the anchor case, the nav-parity case and the README inline-HTML
case. Run the gate, and add a check to it when you find a new class of failure —
do not keep the check in your head.

---

## Before you commit

```bash
python3 build.py            # regenerate; pages/ is the source, *.html is output
python3 check.py            # twenty-five gates, exits non-zero on failure
node    svg-geometry.js     # text-overlap check; skips without a browser
```

Tone is the gate's business now, so there is nothing to run by hand. Gate 22
fails the build on an AI tell (`delve`, `leverage`, `robust`, …); gate 17 fails it
on defensive framing, a disclaimer in heading position, and a qualifier that opens
a section. Both name the sentence and the page.

Hedges are deliberately *not* in either — rule 3 audits them, it does not ban
them, and a count is not the finding. Read the `may`, `might` and `could`
sentences on a page you are about to ship and decide whether each names a real
uncertainty or is the sentence losing its nerve; `/dg-tone <file> --client` runs
that pass with the house vocabulary bar attached.

---

## How good copy actually got made here

**Expect to be told twice.** The user takes facts readily and rejects phrasing —
and the same phrasing failure recurs after it has been corrected once. When a
sentence is sent back, the fix is not a synonym: re-ask who the reader is and
what they are afraid of.

**Rewrite the frame, not the words.** The hero went through three versions:
"admission control for agent knowledge" (a category only we care about) → "your
agent believes whatever it writes down" (the reader's problem, but a developer's,
and developers do not sign annual contracts) → "your company is paying to teach
five hundred private AI agents" (same product, priced as an asset). Each step
changed *whose problem it was*, not the adjectives.

**Order matters as much as wording.** Live order is problem → what you get →
evidence → what changes → deployment → compare → roadmap. "What you get" sits
ahead of the evidence deliberately: the hero raises a question, the guarantees
answer it, and *then* the reader is willing to check whether it is true.

**The awkward facts are the asset.** The evidence page publishes the inconclusive
falsifier and the ~2.2-effective-votes finding. A page that only shows wins reads
as a brochure; the losses are what make the wins credible. This is a selling
decision, not just an honesty one.

---

## Changelog

Append an entry when site work happens here. Entries are history — do not rewrite
a dated one.

### 2026-09-06 — this file
- Created after the documentation inventory; site rules were previously spread
  between the design repo's working agreement (private) (tier leak, gate, nav sync) and
  [README.md](README.md) (mechanics), with the copy-craft corrections living
  nowhere.
- **Fixed:** the last "What we are not claiming" on `commons.html`, rewritten to
  lead with the supply-line case and let the unmeasured claims fall out as a
  consequence. Rule 1 is that correction, generalized.
- Tone audit at time of writing: `index` clean; one `could`/`may` on five pages
  and four on `governance`, all against genuinely open questions.

### 2026-09-11 — institutional infrastructure redesign
- Reframed the homepage around organizational authority, the two-gate model and a
  concrete governed decision object; the argument now becomes more technical as it proceeds.
- Replaced the overlapping-frame identity with the two-boundary `┃┃` primitive across
  the site mark, favicons, wordmark and social preview.
- Preserved the interactive knowledge-state map below the architecture and made maturity
  visible through implemented, experimental, specified and planned states.
- Renamed the public evidence chapter to “Evidence behind the proposition”; the negative
  findings chapter remains in source but is hidden from the rendered page by request.
- Moved platform tokens, the mark, maturity states, metadata and governed-object primitives
  behind the `doublegate-ui` contract; `ui-sync.py` pins those assets for static deployment.
- Rebuilt the path and flow figures around Gate I admission and Gate II projection, replacing
  the earlier multi-colour memory-provider pipeline language.

### 2026-09-16 — one grid, band rhythm, and the message pass
- **One grid.** `.wrap` is `max-width:1240px; padding:0 24px` on every page; the
  `.institutional`/`.overview` overrides are gone. `.wrap.tight` stopped being a narrower
  centred box and is now full-width with a 68ch measure on its own prose children, so a
  heading reaches the page's left edge while the paragraph under it stays readable. The
  homepage h1 and the interior h1s share one `clamp(42px,5.1vw,70px)` scale, so the front
  page stopped shouting at 1.6× the rest. Measured: `.tmp/edge.js` reports a single heading
  `x` of **124px** across every band of all eight pages at 1440px — before this it was 124
  on the homepage, 204 on the other pages' wide bands and 294 on `.wrap.tight`.
- **One system.** The breakpoint ladder went from 24 distinct breakpoints to four rungs (1100 /
  960 / 780 / 600). Superseded generations were folded and deleted — `.institutional h1` was
  defined twice (112px then 70px), `.institutional .band` twice (110px then 56px), `.btn`
  three times — and ~30 components that no page referenced (`.knowledge-object`,
  `.projection-grid`, `.gate-pair`, `.audit-log`, `.notfor`, `.contact*`) went with them.
  `style.css` lost ~500 lines. The `.sky-*` and `.v-*` sets are excluded: `sky.js` injects
  them and a grep sees them as dead.
- **Band rhythm and brand grammar.** The two runs of adjacent `alt` bands —
  `for-business #honest → #measured` and `commons-for-business #appeals → #limits` — were
  fixed, and the `┃┃` boundary mark stopped being a 4px detail inside one figure and became
  the section grammar: it rules the bands that are genuinely boundaries (the two gates, the
  audience splits, the footer) and anchors the hero at low opacity. On the homepage
  `#problem`'s three cards became a ruled two-column ledger, and a full-bleed statement band
  between `#example-source` and `#model` now carries the one sentence the page argues.
- **Message.** The hero keeps its category frame (`Governed memory for AI agents.`) and the
  buyer's problem moved to the first band after it, where it has room for a number. Headings
  that named a category now name a subject: `governance#honest` "We sell the evidence, not the
  verdict" → **"The evidence is the deliverable"**; `commons-for-business#limits` "Treat it as
  reviewed intake, not as trusted input" → **"Budget a review for anything you reuse"**;
  `for-business#why-not` "Sharing knowledge needs a review boundary" → **"A shared store
  distributes a mistake as readily as a fix"**; `evidence#refuse` "Measuring operational
  impact" → **"Time to a first verified task, and cost per correction"**.
- **One deviation from the plan, deliberate.** `commons-for-business#how` was planned as "Two
  decisions, two authorities" and shipped as **"Approval stops at the boundary that granted
  it"**. The ladder head immediately below it reads "Four scopes — separate authority at each
  boundary": the planned heading's "two" would have contradicted the next line on the same
  screen.
- **Say each thing once.** The two-stage review was stated in full on five pages — it is now
  full only on `how-it-works#stages`, with one sentence and a link everywhere else, and every
  number (0–100, APPROVE/REJECT, no second score) survives. "The organization gate is private
  and proprietary" was on six surfaces — it is now the footer and `for-business#offering`.
  `governance#regulatory` no longer reads as a row of yeses: the "no product makes you
  compliant" sentence moved above the table as its lede and the mechanism column was renamed
  to say what the product produces (the evidence, the audit trail) rather than what it
  satisfies.
- **Gates.** Gate 17 grew three patterns the old ones could not see: a heading stating the
  product by what it is not (`is not`, `, not a`), a qualifier marker in a section's *opening*
  paragraph, and a per-page budget of three qualifier markers. Gate 22 is new: no two adjacent
  bands may paint the same background, and an AI tell fails the build. Gate 23 is new and
  advisory — a sentence shared by two pages prints a notice with both locations, filtering out
  the shell (identical by construction) and quotations (which are *supposed* to repeat) so the
  signal is our own prose moved by copy-paste. All three were proved against the real defects
  before landing: re-introducing each historical failure makes the gate name it.
- **Rule 7 applied to this file.** The Python tone-audit snippet that lived under "Before you
  commit" is deleted — the AI tells are gate 22 now. Hedges stay out of the gate on purpose
  (rule 3 audits them, it does not ban them), and the 2026-09-16 read found **zero** that hedge
  a thing we know: `commons-for-business`'s "may well help your recruiting" names real
  uncertainty, `evidence`'s are the month in "ECB Guide … 3 May 2024" and a study's own
  "who could see it", and `governance`'s are the `may` of authorisation on the one page whose
  subject *is* permission. The count is not the finding — a raw grep flags a date.
- **`README.md`'s gate table** gained the four rows it was missing (19, and the new 21–23),
  and its numbering now matches `check.py`'s: rows 9–13 became 8a, 8b, 9, 10, 11, because
  `check.py` has no gates 12 and 13.
- **`evidence#refuse` hidden by request**, like `#against` above it: the measurement plan — the
  three metrics, the review-quality evaluation and the lifecycle-control verification — stays in
  source and stops rendering. Confirmed on the built page: the section has zero box, its text is
  absent from `document.body.innerText`, and the page now renders `#findings` and `#all` only.
  The illustration caveat that lived inside its closing note ("our own measurements are
  illustrations, not population findings") goes with it; the same disclosure survives on
  `how-it-works` for the token numbers and as the homepage map's caption, so the site still makes
  it, just not on the evidence page. Three references to the hidden section were removed rather
  than left pointing at nothing: `for-business`'s "Read the measurement plan, including the
  separate evaluations of review quality and lifecycle controls" (the clause named only hidden
  content), `for-engineers`'s "Review the measurement plan" (a paragraph that existed only to
  carry the link), and `for-business`'s source label "Review the evidence and evaluation plan" →
  **"Review the evidence"**. The evidence page's own `#all` lede lost its trailing "Illustrations
  and planned evaluations carry their status in the text", which referred to the same hidden note.
- **Gate 21 grew the check that would have caught that.** A fragment into a section that carries
  `hidden` resolves — the `id` is right there in the source — so the existing check passed and the
  click did nothing: the browser scrolls nowhere and the page looks like it ignored the reader.
  The gate now fails on a link into a hidden section, skipping anchors that live *inside* one
  (build.py stamps a chapter `#`-link into every heading, so `#against` and `#refuse` each appear
  as their own href and are not rendered either). Proved by re-adding the `for-engineers` link:
  `evidence.html#refuse points into a hidden section — the link resolves and renders nothing`.
- **Verified on the live preview.** `.tmp/hidden.js` at `evidence.html#refuse` reports the section
  with `hasBox: false`, `inLayout: false` and `scrolledTo: 0`; `.tmp/audience2.txt` re-runs
  `audience-check.js` against the post-hide build — PASS, 32 route-viewport checks, 12 redirect
  bookmarks, 6 visible evidence articles and 6 primary links, no console errors; `build.py --check`
  in sync (15 files); `check.py` back to its one pre-existing problem, so the hide added none.
- **Verified.** `build.py --check` in sync (15 files); `audience-check.js` PASS at
  1440/768/390/320 across 8 pages, 32 route-viewport checks, 12 redirect bookmarks, 6 visible
  evidence articles and 6 primary links, no console errors; `.tmp/edge.js` one left edge;
  `svg-routes.js` and the five browser SVG checks PASS (149 labels fit their boxes, the
  tightest 34px clear of a line); `overview-check.js` PASS with `scrollWidth == width` at every
  width; `ui-sync.py --check` and `sky-data.py --check` clean. `check.py` reports **one**
  problem, and it predates this work: `api-sync.py --check` says five `api/*.json` snapshots
  are behind the private checkouts beside this repo. Nothing is committed.
