# doublegate — site

The public landing site for [doublegate](https://github.com/doublegate-io). Eight pages
of static HTML built from a shared shell. No framework, no bundler, no `node_modules`
required to build or check it — Python 3.11+ is enough.

```bash
python3 build.py           # regenerate *.html from pages/*.html
python3 build.py --check   # fail if output is stale (CI)
python3 check.py           # twelve gate checks
node    svg-geometry.js    # SVG text-overlap and bounds check (optional, needs a browser)
```

`*.html` at the root is **generated**. Edit `pages/*.html` and rebuild — a change made
directly to a built page is lost on the next build.

## Layout

| Path | Purpose |
|---|---|
| `pages/*.html` | page bodies — `<section>` content only, no `<head>` or nav |
| `build.py` | shared shell, site map, per-page titles and meta descriptions |
| `check.py` | gate checks; exits non-zero on any failure |
| `svg-geometry.js` | text-overlap and viewBox-bounds check for the SVG assets |
| `assets/style.css` | one stylesheet for every page |
| `assets/logo.svg` | brand mark — favicon and nav |
| `assets/social-card.svg` | 1200×630 link-preview card (`og:image`) |
| `assets/hero-flow.svg` | wide animated flow diagram, front page |
| `assets/artifact-flow.svg` | tall walkthrough diagram, how-it-works |
| `AGENTS.md` | working agreement: copy craft, positioning, claim limits |

## The eight pages

| Page | Reader | Job |
|---|---|---|
| `index` | anyone, 60 seconds | hook, diagram, four guarantees, route them onward |
| `how-it-works` | curious evaluator | the five stages, and what happens when each fails |
| `for-organizations` | budget holder | the measured business case |
| `for-engineers` | whoever will run it | interface, costs, dependencies, what is unfinished |
| `governance` | auditor, compliance | connectors, the four properties, requirement mapping |
| `commons` | contributor, sceptic | the public library, and why no registry does this today |
| `pricing` | buyer | four scopes, and why the boundaries sit where they do |
| `evidence` | sceptic | every claim with its primary source, including the awkward ones |

## What check.py enforces

Each check exists because the failure happened at least once.

1. **Tag balance** — an unclosed `<div>` silently swallows the rest of a page.
2. **In-page anchors resolve** — a `#target` with no matching `id`.
3. **Cross-page links resolve** — eight pages cross-link heavily.
4. **Assets exist** — a typo'd `src` renders as a broken image.
5. **No internal vocabulary** — component IDs, store filenames, tracker and milestone
   codes must never reach a visitor. Link *targets* are exempt; visible copy is not.
6. **Metadata present** — a title plus a description of at least 60 characters, or two
   pages share a link preview.
7. **Every page has a call to action** — a page with no way onward is a lost reader.
8. **Images carry real alt text**, unless `aria-hidden="true"` marks them decorative
   (the brand mark beside the word "doublegate" repeats adjacent text).
9. **No links into the private design repo** — the site is public and the design package
   is not. A visitor cannot tell a 404 from evidence that does not exist, so every claim
   cites its primary source directly instead.
10. **Nav parity** — byte-identical across pages, marking the current page exactly once.
11. **SVG motion paths resolve** — an `mpath` pointing at a missing id animates to nowhere.
12. **README inline HTML is well-formed.**

## Design notes

Colour carries meaning consistently across the diagrams and the CSS:

| Meaning | Colour |
|---|---|
| held / quarantined | `#fb7185` red |
| scanned / checking | `#fbbf24` amber |
| graded / signed / safe | `#34d399` green |
| countersigned / ledger | `#a78bfa` violet |
| readable / distributed | `#22d3ee` cyan |
| records / evidence | `#60a5fa` blue |

The brand mark is three shapes — red post, white square, green post: two gates with the
artifact between them, so the mark reads *held → signed* rather than decorating. Its
geometry was derived rather than eyeballed, giving a 2px dark gap either side of the
square when rasterized at 16px.

Both flow diagrams are self-contained SVG: no JavaScript, no external fonts, no build
step. Animation is SMIL, which degrades to a static diagram where unsupported. Motion
tracks run on a rail *below* the boxes — an earlier version sent animated dots through
the labels, legible in a still and unreadable in motion.

**Narrow screens do not shrink the diagrams.** Scaling a 1080px figure into a 674px
column renders its smallest label at 7.2px. Below 900px the figure keeps a legible
1000px width and scrolls horizontally instead.

## Licence

Content and code in this repository are published for reference. The product itself is
in design; see [doublegate-io](https://github.com/doublegate-io).
