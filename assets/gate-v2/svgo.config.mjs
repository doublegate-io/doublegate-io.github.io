// svgo config for hand-written marks. The defaults BREAK theme-aware SVGs.
// Measured on logo-twoseals.svg with stock svgo 4.1.0 --multipass: 36% smaller,
// and it (a) deleted role="img", (b) inlined class="ink-s" as a hardcoded
// style="stroke:#e6e9ef", and (c) removed the whole @media (prefers-color-scheme)
// block. The result is a near-white mark with no light-theme branch — invisible
// on a light browser tab, which is this project's single most-repeated defect.
// An optimiser that silently reintroduces the bug you fixed twice is worse than
// no optimiser, so the plugins that do it are off by name rather than trusted.
// DELIBERATELY NOT ENABLED, with the reason each would cost us:
//   inlineStyles / minifyStyles — destroys the <style> block carrying the
//     prefers-color-scheme branch; the mark stops theming.
//   removeUnknownsAndDefaults — strips role="img", needed for accessibility.
//   removeViewBox — the mark must scale from 16px to a 1200px social card.
//   removeTitle / removeDesc — <desc> carries the MEANING of the mark, which
//     is documentation for the next session as much as it is a11y.
//   cleanupIds — no ids in these marks, but a future gradient would need them.
//   mergePaths — merging the two seals into one path destroys the per-seal
//     fills that carry the sequence, and the 16px separability that depends
//     on them being distinct runs.

export default {
  "multipass": true,
  "js2svg": {
    "indent": 2,
    "pretty": true
  },
  "plugins": [
    {
      "name": "removeComments"
    },
    {
      "name": "removeMetadata"
    },
    {
      "name": "removeEditorsNSData"
    },
    {
      "name": "cleanupAttrs"
    },
    {
      "name": "removeUselessDefs"
    },
    {
      "name": "removeEmptyAttrs"
    },
    {
      "name": "removeEmptyContainers"
    },
    {
      "name": "convertPathData",
      "params": {
        "//": "floatPrecision 0 keeps every coordinate on the pixel grid, which is",
        "//1": "the IBM Design Language rule (avoid random decimals). Half-pixel",
        "//2": "values in a mark are a signal to fix the geometry, not to preserve.",
        "floatPrecision": 1,
        "transformPrecision": 1
      }
    },
    {
      "name": "collapseGroups"
    },
    {
      "name": "convertShapeToPath",
      "params": {
        "convertArcs": false
      }
    }
  ]
};
