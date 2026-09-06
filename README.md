<div align="center">

<img src="https://doublegate-io.github.io/assets/wordmark.svg" width="520" alt="doublegate — reviewed before it is remembered">

**The public site.** Eight static pages, no framework, no bundler, no `node_modules`.

[![live](https://img.shields.io/badge/live-doublegate--io.github.io-a78bfa?style=flat-square)](https://doublegate-io.github.io)
[![build](https://img.shields.io/badge/build-python%203.11%20only-22d3ee?style=flat-square)](#build)
[![gate](https://img.shields.io/badge/gate-13%20checks-34d399?style=flat-square)](#what-checkpy-enforces)
[![deps](https://img.shields.io/badge/runtime%20deps-none-fbbf24?style=flat-square)](#build)

</div>

---

## Build

```bash
python3 build.py           # regenerate *.html from pages/*.html
python3 build.py --check   # fail if output is stale (CI does this)
python3 check.py           # thirteen gate checks
node    svg-geometry.js    # SVG text-overlap and bounds (optional, needs a browser)
```

`*.html` at the root is **generated**. Edit `pages/*.html` and rebuild — a change made
directly to a built page is lost on the next build.

```mermaid
flowchart LR
  P["pages/*.html<br/><i>bodies only</i>"] --> B["build.py<br/><i>shared shell</i>"]
  B --> O["*.html<br/><i>generated</i>"]
  O --> C["check.py<br/><i>13 checks</i>"]
  O --> G["svg-geometry.js<br/><i>measured, not eyeballed</i>"]
  C --> D["GitHub Pages<br/><i>domain root</i>"]

  style P fill:#10131a,stroke:#8d97a9,color:#e6e9ef
  style B fill:#78350f,stroke:#fbbf24,color:#fde68a
  style O fill:#1e3a5f,stroke:#60a5fa,color:#dbeafe
  style C fill:#064e3b,stroke:#34d399,color:#a7f3d0
  style G fill:#064e3b,stroke:#34d399,color:#a7f3d0
  style D fill:#4c1d95,stroke:#a78bfa,color:#ddd6fe
```

## Layout

| Path | Purpose |
|---|---|
| `pages/*.html` | page bodies — `<section>` content only, no `<head>` or nav |
| `build.py` | shared shell, site map, per-page titles and meta descriptions |
| `check.py` | gate checks; exits non-zero on any failure |
| `svg-geometry.js` | text-overlap and viewBox-bounds check for every SVG asset |
| `assets/style.css` | one stylesheet for all eight pages |
| `assets/logo.svg` | brand mark — favicon and nav |
| `assets/wordmark.svg` | mark + name + tagline, for README embedding |
| `assets/social-card.svg` | 1200×630 link-preview card (`og:image`) |
| `assets/hero-flow.svg` | wide animated flow diagram, front page |
| `assets/artifact-flow.svg` | tall walkthrough diagram, how-it-works |
| `AGENTS.md` | working agreement: copy craft, positioning, claim limits |

## The eight pages

Each has exactly one reader and one job.

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

Every check exists because the failure happened at least once. That is the whole design
principle: **turn each found incoherence into an assertion**, because a class of error
that was possible once recurs during the next rewrite.

| # | Check | The failure that created it |
|---|---|---|
| 1 | Tag balance | an unclosed `<div>` silently swallows the rest of a page |
| 2 | In-page anchors resolve | a `#target` with no matching `id` |
| 3 | Cross-page links resolve | eight pages cross-link heavily; a rename broke one silently |
| 4 | Assets exist | a typo'd `src` renders as a broken image |
| 5 | No internal vocabulary | a visitor meeting a component ID learns the page was not written for them |
| 6 | Head metadata present | two pages shared a link preview and neither was findable |
| 7 | Every page has a call to action | a dead-end page is a lost reader |
| 8 | Images carry real alt text | the diagram carries the argument; `alt=""` drops it |
| 9 | `og:image`/`og:url` absolute | crawlers do not resolve relative Open Graph URLs — the preview silently had no image while the page rendered fine |
| 10 | No links into the private design repo | the design package is private; a deep link 404s and a reader cannot tell that from evidence not existing |
| 11 | Nav parity + label/heading agreement | four of six nav labels once disagreed with the heading they scrolled to |
| 12 | SVG motion paths resolve | an `mpath` pointing at a missing id animates to nowhere |
| 13 | README inline HTML well-formed | a string replacement dropped an `<img>` open tag; invisible in review |

## Design notes

Colour carries meaning consistently across the diagrams, the CSS and the brand mark:

| Meaning | Colour |
|---|---|
| held / quarantined | `#fb7185` red |
| scanned / checking | `#fbbf24` amber |
| graded / signed / safe | `#34d399` green |
| countersigned / ledger | `#a78bfa` violet |
| readable / distributed | `#22d3ee` cyan |
| records / evidence | `#60a5fa` blue |

**The brand mark is the product in one glyph:** a red post, a white square, a green post —
two gates with the artifact between them, so it reads *held → signed* rather than
decorating. Its geometry was derived rather than eyeballed. In a 32-unit viewBox the bars
sit at x=6 and x=26 with stroke-width 4 and the square is 6×6 centred, which yields a
**2px dark gap** either side at 16px, verified by reading the rasterized canvas scanline.

Two earlier attempts failed that measurement — four posts read as a barcode at favicon
size, and a wider bar left only 1.6px. Worth recording: **a vision read of the rendered
PNGs called all three versions unacceptable, including the one whose pixels were provably
clean.** It was right about the social card clipping, though, where the tagline measured
1214px in a 1200px viewBox. Both directions argue for the same discipline — measure.

Both flow diagrams are self-contained SVG: no JavaScript, no external fonts, no build
step. Animation is SMIL, which degrades to a static diagram where unsupported. Motion
tracks run on a rail *below* the boxes — an earlier version sent animated dots through the
labels, legible in a still and unreadable in motion.

**Narrow screens do not shrink the diagrams.** Scaling a 1080px figure into a 674px column
renders its smallest label at 7.2px. Below 900px the figure keeps a legible 1000px width
and scrolls horizontally instead.

## Related

The design package — requirements, architecture, decision records, cited research — is a
separate **private** repository. Nothing here links into it; every public claim cites its
primary source directly instead.

<div align="center">

[**doublegate-io**](https://github.com/doublegate-io) · [**the live site**](https://doublegate-io.github.io)

</div>
