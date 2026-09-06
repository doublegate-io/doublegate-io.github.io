# site/ — Working Agreement for the Landing Site

Rules for **client-facing copy**: `pages/*.html` and the assets they carry.

Scope boundaries — this file does not repeat what these already say:

- the design repo's working agreement (private) — sourcing, honesty, the forbidden-claim lists, the
  tier boundary, terminology. **Read it first; it governs here too.** In
  particular §3b (regulatory claims), §3c (safety claims) and §5 (lead with the
  buyer's problem) are the ones this file builds on.
- [README.md](README.md) — build commands, structure, the eleven `check.py`
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

`check.py` has no opinion on tone — grep for these before every commit.

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

`python3 check.py` is eleven checks, each from a real failure. Hand-rolled
greps have missed the anchor case, the nav-parity case and the README inline-HTML
case. Run the gate, and add a check to it when you find a new class of failure —
do not keep the check in your head.

---

## Before you commit

```bash
python3 build.py            # regenerate; pages/ is the source, *.html is output
python3 check.py            # eleven gates, exits non-zero on failure
node    svg-geometry.js     # text-overlap check; skips without a browser
```

```python
# TONE AUDIT (rules 1-3). check.py has no opinion on register; this does.
import pathlib, re
PATTERNS = {
    "defensive": r"not just another|we are not claiming|nothing is built yet"
                 r"|we don't claim|isn't a silver|to be clear|let's be clear",
    "ai-tell":   r"delve|leverage|robust|seamless|cutting-edge|game.chang"
                 r"|revolution|unlock|empower|harness",
    "hedge":     r"\bmay\b|\bmight\b|\bcould\b|\bperhaps\b|aims to|seeks to",
}
for f in sorted(pathlib.Path("pages").glob("*.html")):
    visible = re.sub(r"<[^>]+>", " ", f.read_text())
    for kind, pat in PATTERNS.items():
        hits = re.findall(pat, visible, re.I)
        if hits:
            print(f"{f.name:26s} {kind:10s} {len(hits):2d}  {sorted(set(h.lower() for h in hits))[:5]}")
# defensive + ai-tell: fix all. hedge: read each one and decide.
```

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
