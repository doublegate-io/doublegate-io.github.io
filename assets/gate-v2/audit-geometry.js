#!/usr/bin/env node
// Production-grade geometry audit for a 32px-grid mark, against published specs.
//
// The 16px separability measurement (measure.js) answers "do the elements stay
// apart when rasterised". It says nothing about whether the drawing is
// *constructed* properly. That is what this checks, and every rule below comes
// from a published icon system rather than from taste:
//
//   IBM Design Language, UI icons (ibm.com/design/language/iconography/ui-icons/design)
//     - base grid is 32x32, artwork snapped to the pixel grid
//     - "avoid random decimal points in the x and y coordinates"
//     - 2px padding reserved; artwork stays inside it unless it needs the weight
//     - ONE stroke weight per icon: "a single icon shouldn't contain a mix of
//       different stroke weights"
//     - corner radius 2px, or a multiple of two
//     - angles in multiples of 15 degrees; 45 degrees anti-aliases evenly
//
//   Material Design system icons — icons live on a fixed grid, designed at 100%
//   scale for pixel-perfect accuracy.
//
//   Favicon production guidance (favicon.now/guides/design) — 10-15% edge space
//   as a starting range, and reduction is its own design problem: heavier
//   strokes and fewer details than the master logo are normal, not a compromise.
//
// Usage:  node audit-geometry.js path/to/logo-*.svg
//
// Exit code is 0 always: this is an advisory report, not a gate. Some findings
// are legitimate to overrule (IBM says extend into the padding when the shape
// needs the visual weight) — but they should be overruled deliberately, in
// writing, not by accident.

const fs = require('fs');

const GRID = 32;
const PADDING = 2;          // IBM reserves 2px on a 32px grid
const RADIUS_STEP = 2;      // 2px, or multiples of two
const ANGLE_STEP = 15;      // multiples of 15 degrees

function nums(str) {
  return (str.match(/-?\d*\.?\d+/g) || []).map(Number);
}

// Every coordinate-bearing attribute we emit in this project.
function coords(svg) {
  const out = [];
  for (const m of svg.matchAll(/\sd="([^"]+)"/g)) out.push(...nums(m[1]));
  for (const attr of ['x', 'y', 'cx', 'cy', 'width', 'height', 'r']) {
    for (const m of svg.matchAll(new RegExp(`\\s${attr}="(-?[\\d.]+)"`, 'g'))) {
      // viewBox width/height on the root element are not artwork coordinates.
      out.push(Number(m[1]));
    }
  }
  return out;
}

function audit(file) {
  const svg = fs.readFileSync(file, 'utf8');
  const findings = [];

  // ---- one stroke weight per icon (IBM: no mixed weights in a single icon)
  //
  // Only VISIBLE strokes count. A knockout gap is a stroke painted in the
  // background colour: it deletes ink rather than adding any, so its width is
  // invisible by construction and comparing it against the outline weight is
  // meaningless. Such a gap SHOULD be heavier than the line it interrupts —
  // matched to the outline it closes up under anti-aliasing at 16px, which is the
  // whole reason for drawing it.
  //
  // Flagged the six knockout variants in round 8 before this exclusion existed.
  // Detected two ways: class="cut" (this project's convention) or a stroke set
  // literally to a background colour.
  const BG_STROKE = /stroke="(#08090c|#0c0e13|#ffffff|#fff)"/i;
  const visibleStrokes = [...svg.matchAll(/<[^>]*stroke-width="([\d.]+)"[^>]*>/g)]
    .filter(m => !/class="[^"]*\bcut\b[^"]*"/.test(m[0]) && !BG_STROKE.test(m[0]))
    .map(m => Number(m[1]));
  const uniqueW = [...new Set(visibleStrokes)].sort((a, b) => a - b);
  if (uniqueW.length > 1) {
    findings.push(`mixed stroke weights: ${uniqueW.join(', ')} — IBM requires one ` +
                  `weight per icon; a mix "looks like a mistake"`);
  }

  // ---- off-grid coordinates (IBM: avoid random decimals)
  const body = svg.replace(/viewBox="[^"]*"/, '').replace(/<svg[^>]*>/, m =>
    m.replace(/\swidth="[^"]*"/, '').replace(/\sheight="[^"]*"/, ''));
  const cs = coords(body);
  const offGrid = cs.filter(n => Math.abs(n - Math.round(n)) > 1e-9);
  const halfPixel = offGrid.filter(n => Math.abs((n * 2) - Math.round(n * 2)) < 1e-9);
  const messy = offGrid.filter(n => !halfPixel.includes(n));
  if (messy.length) {
    const sample = [...new Set(messy)].slice(0, 8).join(', ');
    findings.push(`${messy.length} coordinate(s) off both the pixel and half-pixel ` +
                  `grid: ${sample}${messy.length > 8 ? ' …' : ''}`);
  }

  // ---- padding: does artwork reach into the reserved 2px edge?
  // Cheap conservative test — any coordinate outside [PADDING, GRID-PADDING].
  const extremes = cs.filter(n => n >= 0 && n <= GRID)
                     .filter(n => n < PADDING || n > GRID - PADDING);
  if (extremes.length) {
    findings.push(`${extremes.length} coordinate(s) inside the reserved ${PADDING}px ` +
                  `padding (min ${Math.min(...extremes)}, max ${Math.max(...extremes)}) — ` +
                  `legitimate only when the shape needs the extra visual weight`);
  }

  // ---- corner radii on the 2px step
  const radii = [...svg.matchAll(/\br[xy]?="([\d.]+)"/g)].map(m => Number(m[1]));
  const badR = radii.filter(r => Math.abs(r % RADIUS_STEP) > 1e-9);
  if (badR.length) {
    findings.push(`corner radius off the ${RADIUS_STEP}px step: ${[...new Set(badR)].join(', ')}`);
  }

  // ---- angles on the 15-degree step (line segments in path data)
  const angles = [];
  for (const m of svg.matchAll(/\sd="([^"]+)"/g)) {
    const d = m[1];
    // absolute L x y, and relative l dx dy — enough for the marks we hand-write
    for (const seg of d.matchAll(/[Ll]\s*(-?[\d.]+)[\s,]+(-?[\d.]+)/g)) {
      const [dx, dy] = [Number(seg[1]), Number(seg[2])];
      if (seg[0][0] === 'l' && (dx || dy)) {
        let a = Math.abs(Math.atan2(dy, dx) * 180 / Math.PI) % 90;
        angles.push(Number(a.toFixed(2)));
      }
    }
  }
  const badA = angles.filter(a => Math.min(a % ANGLE_STEP, ANGLE_STEP - (a % ANGLE_STEP)) > 0.6);
  if (badA.length) {
    findings.push(`${badA.length} angle(s) off the ${ANGLE_STEP}° step: ` +
                  `${[...new Set(badA)].slice(0, 6).join('°, ')}° — 45° anti-aliases evenly, ` +
                  `arbitrary angles do not`);
  }

  // ---- accessibility / metadata the project already requires
  for (const [re, what] of [[/<title>/, '<title>'], [/<desc>/, '<desc>'],
                            [/role="img"/, 'role="img"'], [/aria-label=/, 'aria-label']]) {
    if (!re.test(svg)) findings.push(`missing ${what}`);
  }
  // A mark that themes ink must resolve BOTH directions or it vanishes on a
  // light tab — the single most repeated defect in this project's history.
  if (/class="ink/.test(svg) && !/prefers-color-scheme/.test(svg)) {
    findings.push('uses .ink/.ink-s but has no prefers-color-scheme block — ' +
                  'near-white ink is invisible on a light browser tab');
  }

  return findings;
}

const files = process.argv.slice(2);
if (!files.length) {
  console.log('usage: node audit-geometry.js <logo.svg> [...]');
  process.exit(0);
}

let clean = 0;
for (const f of files) {
  const findings = audit(f);
  const name = f.split('/').pop();
  if (!findings.length) {
    clean++;
    console.log(`\x1b[32mCLEAN\x1b[0m  ${name}`);
  } else {
    console.log(`\x1b[33m${String(findings.length).padStart(2)} \x1b[0m     ${name}`);
    for (const x of findings) console.log(`          · ${x}`);
  }
}
console.log(`\n${clean}/${files.length} clean against IBM 32px-grid + favicon production rules`);
console.log('Advisory, not a gate — overrule a finding deliberately and in writing.');
