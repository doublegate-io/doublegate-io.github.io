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
- **No AI tells.** The list is `ai_tells` in [voice.json](voice.json), the site's
  copy of the SDK's word list (ADR-0137 d6); gate 22 reads it from there.
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
to the next most likely question — `for-business` → `evidence`,
`for-engineers` → `evidence`, `governance` → `for-business`.

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

### 8. The reader is addressed only to act

A call to act, the text of a link or a button, may use the imperative and the
second person. Every other sentence names the organization, its team or the
operator in the third person: "A company's teams already teach their agents",
not "Your teams". The hero keeps the buyer's problem as its frame and changes only
the pronoun. No exclamation, "please", apology, praise or "I"; "we" stays for the
company's own commitments ("that is our bug", the roadmap). Quoted sources keep
their own words inside `<q>` or `<blockquote>`. Gate 24 holds this against
[voice.json](voice.json) and gate 25 holds that file equal to
`doublegate-sdk/src/doublegate_sdk/voice.json`: a change to the list is made in the
SDK and copied here by one `cp` in the same commit (ADR-0137 d6, d7).

### 9. One statement a sentence; the limit is the next sentence

Four readers of the 2026-10-06 copy stopped at the same shape: a benefit, a
semicolon, then one or two caveats. Two adjacent sentences are "the same breath";
a clause chain is not. Keep a sentence under 25 words (30 on for-engineers and
evidence, where a number carries its machine and date). A semicolon joins two
parallel facts of one kind, never a benefit and its limit.

> ✗ *Held in quarantine and scanned before the write returns; the scan matches
> patterns, so a new injection that fools it and the grader gets through.*

> ✓ *Held in the quarantine, the store where claims wait for review, and scanned
> before the agent gets its answer. The scan looks for leaked secrets and planted
> instructions by matching known patterns. A new kind of planted instruction that
> fools both the scan and the grading model gets through.*

### 10. Say what a plain install does first, then what changes it and when

A guarantee stated only by the setup in which it holds makes the reader invert the
sentence to learn the default. And "specified" in prose reads as "done" to every
reader: write "comes with the Solo release", "comes with Team" (what `NEXT_STEPS`
names) or "is designed and on the roadmap". The status label SPECIFIED stays in the
roadmap table, with its key under it.

> ✗ *The gate compares identities, so the rule holds against an agent that runs as
> another operating-system user (how to run one); a gate under its own service user
> is specified.*

> ✓ *If an agent runs as the same operating-system user as the gate, its shell can
> promote what its session wrote. That is the case when you start both yourself.
> Run the agent as another operating-system user and the rule holds against it (how
> to set that up). A gate that runs under a dedicated operating-system user is
> designed and on the roadmap.*

### 11. One name per thing, glossed once a page; one wording per recurring limit

The stored item is a **claim** on every page, never a memory, note, write,
lesson or contribution ("lesson" and "correction" only as examples of a claim).
Each product word carries the same plain gloss where a page first uses it: a claim,
one thing an agent or a person writes down for others to rely on; the gate, the
doublegate service on your machine that holds each claim until it is signed; a work
area, the named place a session's claims go; recall, the gate's search; the
journal, the signed record of every write and decision; the quarantine, the store
where claims wait for review. Insider shorthand gets its plain words ("without the
reviewer role", not "below reviewer"). A limit that recurs across pages is written
once and repeated word for word, so gate 23's notice on it is expected; a second
wording of the same limit is drift.

> ✗ *Below reviewer, another author's held claim is answered exactly as an id that
> names nothing.*

> ✓ *Say an agent asks the gate for another agent's held claim by its id. Without
> the reviewer role, it gets the same answer as for a claim that does not exist.*

---

## Before you commit

```bash
python3 build.py            # regenerate; pages/ is the source, *.html is output
python3 check.py            # twenty-five gates, exits non-zero on failure
node    svg-geometry.js     # text-overlap check; skips without a browser
```

Tone is the gate's business now, so there is nothing to run by hand. Gate 22
fails the build on an AI tell from the word list's `ai_tells`; gate 17 fails it
on defensive framing, a disclaimer in heading position, and a qualifier that opens
a section; gate 24 fails it on the second person outside a call to act and on the
list's banned words. Each names the sentence and the page. `python3 check.py
--selftest` runs gates 22 and 24 on the SDK's fixture, one caught and one passing
sentence per entry, and the full run does the same.

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

### 2026-10-04 — the copy describes the product as it stands
- The design's feature review (ADR-0110) declined the Commons, the organization gate's
  HTTP surface and storage, team attribution at submission, folder subscriptions, the gap
  report and the PROV export. Every page that sold one as the product or as a dated release
  now says what runs today, from source (one gate on one machine), and lists only the next
  two steps: the Solo release (installable, two-stage review, backup and restore, key
  rotation, content erasure) and Team (one gate a group shares, read access per folder).
  The second gate is named once per page where the name needs it, as a later step.
- **Removed:** `pages/commons-for-business.html` and `pages/commons-for-engineers.html`.
  Both URLs, and `commons.html`, redirect to the audience overviews; `audience-check.js`
  checks only `#top` for them, because the overview has none of their sections.
- **Undated:** `FIRST_RELEASE` (Q2 2027) is gone with the roadmap date it mirrored.
  `NEXT_STEPS` in `build.py` names what ships next, in order, and every page quotes it;
  the Solo release is dated when its acceptance list passes. Release numbers 2–5 are gone
  from visible copy.
- "The organization gate is private and proprietary" is gone from the footer, `pricing`
  and `for-business#offering`: the organization gate is archived and its licence is an
  open operator decision. The managed offering card went with it.
- `governance#standards` now shows the two commands that verify the record, in place of
  the W3C PROV and OpenLineage mappings. `for-engineers#agents` no longer lists the
  organization gate's OpenAPI snapshot, and `llms.txt` drops it and the rule about
  `PUT /submissions`.
- `check.py` gate 21 refuses a route to either Commons page; gate 19 lost the Commons
  ladder figure.
- **Verified.** `build.py --check` in sync (15 files); `check.py` reports one problem,
  `api-sync.py --check` (two snapshots behind the client gate's checkout), which `main`
  reports identically; `svg-routes.js` PASS; `/dg-tone pages --client` 0 must-fix hits.
  The browser checks were not run.

### 2026-10-04 — governance says who proposes a memory today
- `governance#how` and `#examples` described connectors as running: a contract naming a
  dataset, its fields and a refresh cadence, and beliefs linked to a source system's rows.
  No shipped program proposes from an outside system. Both sections now say who proposes today,
  an agent or a person under its own identity, held and reviewed, and name reading from outside
  systems as a later step taken by a separate program with its own key. The record's "where it
  came from" row and the page's hero follow, and the README's page table no longer lists
  connectors.
- **Verified.** `build.py` run twice changes nothing beyond the edited sources and the
  regenerated `governance.html`; `build.py --check` in sync (15 files); `check.py` PASS on all
  8 pages; `api-sync.py --check` OK, 5 files equal the checkouts. The page's `may`/`might`/`could`
  count went from five to four: three dates and the `may` of authorisation. The browser checks
  were not run.

### 2026-10-04 — the API snapshot follows the gate's smaller catalog
- The client gate retired `dg.rank`, `dg.space_link`, `dg.space_unlink`, `dg.crawler_policy`
  and the three `dg.submit*` verbs, took `rank`, `hide` and `ban` off the agent's tool list, and
  dropped the catalog's `service` column (design ADR-0110 d6, ADR-0112; hardening items H1.9 and
  H1.11). `api/daemon-rpc.json`, `api/mcp-tools.json` and `api/index.json` are regenerated from
  that checkout.
- `note.schema.json` moved with the notifier, which publishes the note, from the client gate to
  `doublegate-peers/docs/api/`: `api-sync.py` reads it there, stamps `doublegate-peers` in
  `api/index.json`, and takes `DOUBLEGATE_PEERS_SRC` to point elsewhere. The file's bytes did
  not change.
- **Verified.** `api-sync.py --check` OK, 5 files equal the checkouts; `build.py --check` in
  sync (15 files); `check.py` PASS on all 8 pages. No page changed. The browser checks were not
  run.

### 2026-10-06 — the offering pass: what runs today, what it costs, and the decided words
- Seven pages rewritten or edited from one plan, one writer per page, then read in order
  (index, for-business, how-it-works, governance, evidence, for-engineers, pricing) by one
  integrator. The offering statement is on `for-business#offering`; every other page quotes
  `AVAILABILITY` and `NEXT_STEPS`. New sections: index `#rules`; how-it-works `#areas` and
  `#after`; for-business `#asset`, `#review`, `#work-areas`, `#group`; for-engineers `#plugin`
  and `#console`; governance `#private`; evidence `#rules` and `#measured`; pricing
  `#costs-run`. `evidence#refuse` and `for-business#honest` are gone; `#against` is rewritten
  and still hidden. The two flow SVGs are HTML markup; `{role_table}` and `{agent_reach}`
  ("30 of 62") are counted from `api/daemon-rpc.json` at build time.
- Nine statements depend on the held-row fix (`fix/held-row-reads`); each carries its
  fallback in an HTML comment directly above it, so the swap is a delete or a paste.
- **Primary sources merged with the pages** (`design/site-evidence`, research 07, 11, 12, 20).
  Three sentences changed to match them: the provider-survey finding (Byterover holds only
  flagged changes and only from its team; Mnemosyne's approval is a tool the writing agent
  calls), the SkillCloak finding (two of its eight scanners are model judges, tried on 100
  skills, so a grade of a skill proves no more than the scan; on evidence and for-business),
  and the AER sentence on index ("detected no shift", the abstract's words, for "did not
  change").
- **Seams fixed while reading.** A bare "key" on index (3), evidence (3), governance (1) and
  for-engineers (1) became an agent-role API key, an API key or sign-in, or the signing key;
  `NEXT_STEPS` says "signing keys that rotate". The index crews row stopped repeating
  for-business word for word (gate 23). The four route figures paint held, signed and
  readable steps rose, green and cyan: the step rule lost to the card border before, so the
  computed top border was the neutral line on every step. Governance's "could sign" is "can
  sign", as index says it.
- **Index hero.** At 320 px it measured 767 px tall against `audience-check.js`'s 720 px
  bound; the body drops "One gate, on one machine" (the status line under it says so) and
  measures 697 px. The tallest openings now: 452 px at 1440 (how-it-works), 553 at 768
  (index), 658 at 390 and 711 at 320 (for-engineers, 9 px inside the bound).
- **Gate 5c** is new: a bare "key" or a sense ADR-0104 d8 retired outright (per folder, piece
  of work, pending review, projection, withdraw, assess, publication, two-stage, trust score,
  admission, ledger, inbox) in visible copy fails. Put back on index ("the author's own key"),
  it fails naming the page; on landing it found one more, for-engineers' "the key is shown
  once".
- **Verified.** `build.py --check` in sync (15 files). `check.py` PASS on 8 pages with three
  gate-23 notices, each a shared constant or a mirrored rule title (`NEXT_STEPS` on three
  pages, `AVAILABILITY` in two heroes, rule 4's title on index and evidence). `api-sync.py
  --check` 5 files equal; `ui-sync.py --check` match; `sky-data.py --check` 20 × 40.
  `svg-routes.js` 6 assets, no crossing; with Chromium: 80 labels fit, tightest line 34 px
  clear, smallest label ≥10 px at 3 figure/breakpoint pairs, `overview-check.js` PASS at
  1440/768/390/320 with five route steps. `audience-check.js` PASS: 24 route-viewport checks,
  6 redirect bookmarks, 7 visible evidence articles and 10 primary links, scrollWidth equal to
  the viewport at every width, no console errors. `verify.py doublegate-site --strict`: 10
  checks, 0 failed, 0 skipped (Python 3.12 only; CI's 3.11 and 3.13 lanes were not run here).
  `/dg-tone --client`: 0 must-fix on all seven pages; 10 hedges read, all the `may` of
  permission, the month May, or a quoted study's "could see it".
- **Read by hand.** The plan's banned list returns 6 hits: REJECTED as an outcome label in
  `claim-path.svg` and `hero-field.svg` (2 each, the labels the plan asks for) and
  "DoubleGate" in the aria-labels of the two logo marks `ui-sync.py` pins from
  `doublegate-ui`, which this site cannot edit. `wordmark.svg`, which only the README shows,
  now reads "doublegate — reviewed memory for AI agents", as the social card does. Each page names the second gate once. The plugin's eight tool
  names equal `doublegate-agent` `TOOLS`; no `dg.` string reaches the built for-engineers or
  evidence. Not checked: the console page and its images (phase 2), and the statements that
  wait on the operator's open questions, which stay out.
- **Caught by three independent readers, and fixed.** Three sentences the code does not
  support: "no caller can choose a lighter kind" (the caller names the kind; the gate refuses a
  supplied review class, so it now says no caller can ask for less review than its kind
  carries), "every write is held" on the for-engineers topology (records are kept at once as
  evidence; it now says every claim written), and the read-only notifier's promotion-only
  notes, which hold only on the held-row fix and now carry the tenth fallback comment. Four
  contradictions inside a page: the still map's HELD row called a held claim "live" (it is held
  beside the promoted claim it contradicts, and only that one is recalled), index rule 1 said
  an author can never sign and then that Claude Code's shell can (it now states the gate never
  counts the authoring identity's signature, with the shell as the consequence), the index
  route promised a cost on every step and named none on two, and governance said only agents
  and people write while its own examples include the skill watcher. Voice: index `#problem`
  stated no problem (it now opens with the session that pays to relearn a lesson), pricing
  argued with doubts nobody raised, governance's record note defined a journal by what it is
  not, four `Next` headings named no subject, and the SCAN label said "keys" for secrets. The
  hero's default-scope clause read "its own work area" as the claim's; the plan's full sentence
  failed `audience-check.js`'s 720 px bound at 320 px, and so did "by default an agent looks
  in its own work area and those above" (720.5 px), so it reads "by default, from the
  agent's own work area up" at 697 px. Re-run: `build.py --check` 15 files in sync; `check.py`
  PASS on 8 pages, the same three gate-23 notices; `api-sync`, `ui-sync`, `sky-data` and
  `claim-path.py --check` clean; `make check PKG=doublegate-site FLAGS=--strict` 10 checks, 0
  failed, 0 skipped; `audience-check.js` PASS, 24 route-viewport checks, 7 evidence articles,
  10 primary links; `/dg-tone --client` 0 must-fix on seven pages, the same 10 hedges.
- **Last nine findings closed.** The index hero says in a whole sentence that any agent on the gate can find a signed claim with a recall across the space and by default searches its own work area and those above it (the proposition lost "for the agents that come after" to fit: 716 px at 320); the for-engineers "Graded" step names the default, two readings that can promote with no person; the operating-system-user limit is stated in full only on for-engineers `#plugin`, with one linked sentence on index, for-business, governance, evidence and for-engineers `#operations`; "residues" left governance and index for "what such a caller can still learn"; the space named main needs no declaration (index step 1, for-engineers `#connect`); an administrator, not a reviewer, declares an absence; pricing words held claims by recall only; governance says each decision is recorded with who made it and signed with the gate's signing key. The voice reader's other three rewrites applied (the AER and SkillCloak sentences on for-business, the pricing tag). Re-run: `check.py` PASS on 8 pages with the same three notices; `audience-check.js` PASS, 24 route-viewport checks; `make check PKG=doublegate-site FLAGS=--strict` 10 checks, 0 failed, 0 skipped; `/dg-tone --client` 0 must-fix, the same 10 hedges.
- **The branch took `main`** (`c4549abf`: the held-row fix, the crews record, the showcase week, the console's label fix) by a merge, with no conflict. `api-sync.py` regenerated the snapshot from the merged catalog (`client-gate@5a490b0`), and the role table still reads `{agent_reach}` = "30 of 62": the fix changed what the by-id, listing and event verbs answer below reviewer, not which role each of the 62 methods needs. Every statement that waited on the fix is true of `main` and lost its fallback comment; index rule 4 and governance `#private` now say, as INV-SEC-10 does, that the timing residue confirms an id a caller holds or can compute (an id is a digest of the write). Re-run: `check.py` PASS with the same three notices; `make check PKG=doublegate-site FLAGS=--strict` 10 checks, 0 failed, 0 skipped; `audience-check.js` PASS, 24 route-viewport checks, 7 evidence articles, 10 primary links; `/dg-tone --client` 0 must-fix, the same 10 hedges; the design's docmap, audit, rendering, counts and vocabulary checks clean.

### 2026-10-06 — the wording pass: one statement a sentence, the default first, one name per thing
- **What the readers said failed.** Four readers (a budget holder with four minutes, a head of
  platform engineering, a copy editor, a cold visitor) read the copy as the operator had read it
  (tag `site-wording-before`) and agreed on the claims and not on the sentences. The index
  hero's first sentence used five words in a private sense ("write" as a noun, signs, gate,
  recall across the space, work area). The stored item had six names (claim, memory, note,
  write, lesson, contribution). A benefit was routinely followed by a semicolon and two caveats.
  "Specified" read as "done". Guarantees were stated only by the setup they hold in ("the rule
  holds against an agent that runs as another operating-system user"), so the reader had to
  invert the sentence to learn the default. Headings were slogans ("The evidence is the
  deliverable" over a list of limits), and insider shorthand stood in for the outcome ("below
  reviewer", "an id that names nothing", "closest", "recall keeps no receipt", "a shorter valid
  prefix").
- **The rules the voice guide set**, now hard rules 8–10 above: one statement a sentence, with
  the limit as the next sentence (25 words, 30 on for-engineers and evidence); the plain-install
  default first, then what changes it, with "comes with the Solo release", "comes with Team" or
  "is designed and on the roadmap" in place of "specified"; one name per thing, glossed once a
  page; outcome before mechanism; a heading that says what the section gives the reader; the
  page's own case (the payments sandbox, the alert policy's revisions 3 and 4, the five
  sessions) opening a hard section, marked as an illustration; each recurring limit worded once.
  No claim, number, source, status label, section id, link target or figure's data moved.
- **How it was done.** One writer a page committed its source; the integrator built, ran every
  check and read the site in the visitor's order as the budget holder and as the engineering
  lead. The integrator's changes: the operating-system-user limit had two wordings (for-business
  differed) and was 28 words on index and governance, so it is two sentences on all five pages
  ("If an agent runs as the same operating-system user as the gate, its shell can promote what
  its session wrote. That is the case when you start both yourself."), and "a service user of
  its own" and "a dedicated operating-system user" became the second one everywhere; the
  journal's gloss was worded four ways and is "the signed record of every write and decision"
  on every page; the quarantine and the work area each have one gloss; for-business names the
  review queue as the console page where held claims wait; governance's skill-bundle sentence
  stopped repeating index's word for word (gate 23); the guess-a-claim sentence on governance
  lost its semicolon.
- **Measures** (visible text at 1440 px, before → after; method in the scratch `measures.md`):
  11,021 → 13,392 words across seven pages; 752 → 1,106 sentences; mean 14.7 → 12.1 words a
  sentence; 90th percentile 25–31 → 18–22 on every page; semicolons 129 → 4 (two in the
  knowledge map's example claim, two joining parallel facts); sentences over the ceiling 88 → 0.
  The site is 21.5% longer: the glosses, the limits as their own sentences and the full forms
  of the recurring limits cost words. Cutting it back without dropping a gloss or a limit is the
  next pass's question.
- **Verified.** `build.py --check` 15 files in sync. `check.py` PASS on 8 pages with 20 gate-23
  notices, each read: the three recurring limits' fixed wording, the product words' glosses,
  `NEXT_STEPS` and `AVAILABILITY`, and the without-the-reviewer-role answer. `api-sync.py
  --check` 5 files equal; `ui-sync.py --check` match; `sky-data.py --check` 20 × 40;
  `svg-routes.js` 6 assets, no crossing. With Chromium: `svg-geometry`, `svg-bounds` clean;
  `svg-scale` 3 figure/breakpoint pairs at ≥10 px; `svg-fit` 80 labels fit; `svg-clearance`
  tightest 34 px; `overview-check.js` PASS at 1440/768/390/320. `audience-check.js` PASS: 24
  route-viewport checks, 6 redirects, 7 visible evidence articles, 10 primary links, no console
  errors. `make check PKG=doublegate-site FLAGS=--strict` 10 checks, 0 failed, 0 skipped
  (Python 3.12; CI's 3.11 and 3.13 lanes not run here). `/dg-tone --client` 0 must-fix on all
  seven pages; 10 hedges read, each the `may` of permission, the month May or the evidence
  page's "who could see it". The banned list returns the same 6 hits as the offering pass
  (REJECTED as an outcome label in two figures, "DoubleGate" in the pinned logo aria-labels).
- **Corrected after four verifiers compared before and after.** Thirteen sentences had moved a
  claim and are put back where the code or the source puts them: the plugin's hooks keep evidence
  at a session's start, before a compaction and at its end (no hook records tool calls); recall's
  default never searches a sibling area; the field experiment is not turned into a general law;
  Meta's words are quoted from "haven't seen"; the vector-search share reads one in six to one
  in five of the top 10; the business figure keeps group sharing with Team; governance says
  "reading from outside systems", since import exists; "four search scopes" is back; lineage is
  who worked in which work area; the console is the gate's web console; the id a write returns
  is not a promotion; every claim waits for review; the Ji heading says packed. Three benefits
  the pass had added (a person per kind of content on index and for-business, "every decision
  is signed" in the provider survey, the signed-decision remedy in the Ji item) are cut. Where
  the old sentence read better it came back (the digest, "stay fine", "A correction we made to
  our own case", the inline qualifier on the 100-skill sample); the operating-system-user limit
  is a sentence and a link on for-engineers `#operations` and governance `#regulatory`, where
  the full form already sits on the same or a linked section. 13,990 visible words, from 14,118;
  gate-23 notices 18, from 20. `build.py --check` 15 in sync; `check.py` PASS on 8 pages;
  `api-sync`, `ui-sync`, `sky-data --check` and `svg-routes.js` clean; with Chromium the five
  `svg-*` checks and `overview-check.js` PASS; `audience-check.js` PASS, 24 route-viewport
  checks and 6 redirects, 0 console errors (served from the preview on 8793); `make check
  PKG=doublegate-site FLAGS=--strict` 10 checks, 0 failed, 0 skipped; `/dg-tone --client` 0
  must-fix, the same 10 hedges; the banned list the same 6 hits.
- **Closed by an editor's pass (2026-10-07).** The meaning reader found seven sentences that
  drifted, and each now says what the code says: an id is a digest of the whole write (its
  author, time and text), not of its text (index rule 4, governance `#private`); the SCAN step
  holds a claim until rejected or expired only for a hard finding; steering reaches a work area
  and the areas below it (index roadmap, for-business `#group`, for-engineers `#try`); an
  administrator declares an absence; the map's claims are called illustrative again. Taken back
  where the readers said the old sentence was better: "a model that did not write it" on GRADE,
  "One developer, today" and the notfor summary on pricing, the asset card's "found by any agent
  that recalls across the space", the Claude Code card's new session that finds an earlier
  session's claims, the digest of about ten claims as a digest, Meta's card without Meta's praise
  first, one count of what a caller still learns (four) on index and governance, and a governance
  hero that names no command count. Length: every page is back within 5% of the copy the operator
  read (site 11,462 words from 11,021; it was 13,392). Each product word is glossed once a page
  in six words or fewer; the operating-system-user limit is in full only on for-engineers
  `#plugin` and one linked sentence elsewhere (7 occurrences, from 18); "designed and on the
  roadmap" is gone from prose (11 → 0) and the index legend carries the meaning; the BCBS 239
  lineage aside lives only on evidence; the registry is named as the Model Context Protocol's.
  Re-run: `build.py --check` 15 in sync; `check.py` PASS on 8 pages with 9 gate-23 notices, each
  a deliberate shared line; `api-sync`, `ui-sync`, `sky-data --check` and `svg-routes.js` clean;
  with Chromium the five `svg-*` checks and `overview-check.js` PASS; `audience-check.js` PASS,
  24 route-viewport checks, 6 redirects, 7 evidence articles, 10 primary links, 0 console
  errors (index hero 688.75 px at 320); `make check PKG=doublegate-site FLAGS=--strict` 10
  checks, 0 failed, 0 skipped; the banned list the same 6 hits.
- **Limits put back after the meaning reader (2026-10-07).** Sixteen limits the editor's pass cut are back, each one short sentence: index step 1's refusal of an unknown space and the administrator's declaration, step 3's one-model default, the absence rules on for-business (30 days by default, seven silent days, the 90-day ceiling), "The queue has no bulk act", a promoted skill written into your folders, Python 3.11, Meta's quoted claim, the console's reload and Live switch, governance's BCBS 239 line, evidence's held-claim article and the survey on request; "A gate that runs under a service user of its own is on the roadmap." now follows the separation on index, for-business, governance and evidence (settled conflict 6), and governance says "promote" like every page. Each page stays within 7% of the copy the operator read (site 11,686 from 11,021); `check.py` PASS on 8 pages with 9 gate-23 notices, `audience-check.js` PASS.
- **Clauses put back after the meaning lens (2026-10-07).** Fourteen clauses the wording pass dropped are back as short sentences: "Run the agent as another operating-system user and the rule holds against it." after the hole on index, for-business, governance `#how` and evidence, and the four-eyes row says whom it binds on one machine; an administrator declares an absence and expired claims name it; recall's default scope beside the RECALLED benefit; "The method names in these files predate the words on this site."; "Install one or the other."; why the scanner rate fell; Meta's article is not a market survey; the review's cost beside the asset benefit; the skill watcher writes a file once; the signature binds the decision to the claim. `check.py` PASS with 10 gate-23 notices (the new limit sentence is the tenth, deliberate); `overview-check.js` and `audience-check.js` PASS; index hero 688.75 px at 320.

### 2026-10-11 — the voice standard (ADR-0137, row VO7)
- **Gates.** Gate 24 is new: a page's own visible prose, less quotations, hidden
  sections and the text of links and buttons, breaks no entry of the word list.
  Gate 25 is new: `voice.json` equals the SDK's file, and skips with its reason in a
  checkout of the site alone. Gate 22 reads `ai_tells` from the list in place of its
  own pattern. `check.py --selftest` is new.
- **Measured** on the built pages before the rewrite: 69 second-person hits, index 12,
  for-business 16, for-engineers 14, governance 11, pricing 8, how-it-works 3,
  evidence 2, 404 3; after it, none. The record's 51 counted `pages/` alone; the
  rest stood in the hero, availability lines, footer and 404 that `build.py` writes.
- **Rule 8** is new, and rule 2's AI-tell line points at the list.
- The Hugging Face quotation on `evidence` moved into `<q>`, as `governance` marks
  its quotations; its words are the source's and are not rewritten.


### 2026-10-11 — the offering pass carried onto the voice standard
- `site/offering-pass` (2026-10-06 to 10-07) merged onto main after VO7. Its pages, hero,
  availability lines, titles, api manifest and gate 5c are the content; main's register is the
  voice. Its rules 8–10 are rules 9–11 here, because main's rule 8 (the reader is addressed
  only to act) keeps its number; the dated 10-06 entry above still says 8–10.
- **Measured** by gate 24 after the merge, before the register pass: 90 second-person hits
  (for-engineers 19, for-business 17, governance 17, index 12, evidence 10, how-it-works 7,
  pricing 7, 404 1) and one first person singular, "Annex I systems", which now reads
  "systems under EU product-safety law". After it, none. The operator, the organization, an
  auditor or "anyone holding it" now takes the sentence the reader held.
- The footer keeps main's wording; the console's refusal is quoted as the console now
  words it, <q>Refused: the claim's author cannot sign it</q>; the Claude Code plugin gives an
  agent eleven tools, not eight, and the api manifest stops counting them.
