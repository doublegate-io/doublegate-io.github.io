// No connector may be routed through the interior of a box.
//
// This check exists because it happened. Separating two crowded branches in
// hero-flow.svg moved the author fast lane from x=640 to x=648 — which is inside
// THE SECOND GATE box (x 632..772). The dashed line and its animated dot climbed
// vertically through 78px of that box's interior, and it shipped.
//
// Nothing else could see it. svg-geometry.js compares TEXT nodes to each other,
// svg-bounds.js compares text to the viewBox, svg-scale.js measures rendered font
// size. A path crossing a rect is invisible to all three: no text is involved.
//
// Method: flatten every <path> to points (lines and quadratic curves), then test
// each point against every stage/panel rect. A 2px inset tolerance lets a
// connector legitimately touch a box's edge — which is how it attaches — while
// still catching one that runs through the middle.
//
// Usage:  node svg-routes.js
const path = require('path');
const fs = require('fs');

const DIR = path.join(__dirname, 'assets');
const INSET = 2;        // px — touching an edge is attachment, not a crossing
const MIN_BOX = 60;     // px wide — ignore small glyph decorations, dots, ticks

function flatten(d) {
  const pts = [];
  const re = /([MLQCmlqc])([-\d.,\s]*)/g;
  let cur = null, m;
  while ((m = re.exec(d)) !== null) {
    const cmd = m[1];
    const v = (m[2].match(/-?[\d.]+/g) || []).map(Number);
    if (cmd === 'M' || cmd === 'm') {
      cur = [v[0], v[1]];
      pts.push(cur);
      for (let i = 2; i + 1 < v.length; i += 2) { cur = [v[i], v[i + 1]]; pts.push(cur); }
    } else if (cmd === 'L' || cmd === 'l') {
      for (let i = 0; i + 1 < v.length; i += 2) {
        const nxt = cmd === 'L' ? [v[i], v[i + 1]] : [cur[0] + v[i], cur[1] + v[i + 1]];
        for (let k = 0; k <= 20; k++) {
          const t = k / 20;
          pts.push([cur[0] + (nxt[0] - cur[0]) * t, cur[1] + (nxt[1] - cur[1]) * t]);
        }
        cur = nxt;
      }
    } else if (cmd === 'Q' || cmd === 'q') {
      for (let i = 0; i + 3 < v.length; i += 4) {
        const c1 = cmd === 'Q' ? [v[i], v[i + 1]] : [cur[0] + v[i], cur[1] + v[i + 1]];
        const nxt = cmd === 'Q' ? [v[i + 2], v[i + 3]] : [cur[0] + v[i + 2], cur[1] + v[i + 3]];
        for (let k = 0; k <= 40; k++) {
          const t = k / 40, u = 1 - t;
          pts.push([
            u * u * cur[0] + 2 * u * t * c1[0] + t * t * nxt[0],
            u * u * cur[1] + 2 * u * t * c1[1] + t * t * nxt[1],
          ]);
        }
        cur = nxt;
      }
    }
  }
  return pts;
}

function rects(src) {
  const out = [];
  const re = /<rect\b([^>]*)>/g;
  let m;
  while ((m = re.exec(src)) !== null) {
    const a = m[1];
    const num = k => {
      const r = a.match(new RegExp(k + '="([-\\d.]+)"'));
      return r ? parseFloat(r[1]) : null;
    };
    const x = num('x'), y = num('y'), w = num('width'), h = num('height');
    if (x === null || y === null || w === null || h === null) continue;
    if (w < MIN_BOX || h < 20) continue;
    // Container panels are meant to hold connectors: artifact-flow.svg wraps each
    // numbered zone in a `.panel`/`.panelIn` rect, and every arrow between stages
    // inside that zone is legitimately within it. Only leaf boxes — the stages a
    // line should route AROUND — are candidates for a crossing.
    const cls = (a.match(/class="([^"]*)"/) || ['', ''])[1];
    if (/\bpanel(In)?\b/.test(cls)) continue;
    out.push({ x, y, w, h });
  }
  return out;
}

let problems = 0;
const files = fs.readdirSync(DIR).filter(f => f.endsWith('.svg')).sort();

for (const file of files) {
  const src = fs.readFileSync(path.join(DIR, file), 'utf8');
  const vb = src.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
  const vw = vb ? parseFloat(vb[1]) : Infinity;
  const vh = vb ? parseFloat(vb[2]) : Infinity;
  const boxes = rects(src).filter(b => !(b.w >= vw * 0.98 && b.h >= vh * 0.98));

  let hits = 0;
  // Only VISIBLE connectors are policed. Two exclusions, both deliberate:
  //
  //   * <path id="..."> inside <defs> is a motion track for animateMotion. The
  //     travelling artifact is SUPPOSED to pass through the stage boxes — that is
  //     what the animation depicts.
  //   * a glyph drawn inside its own box (a checkmark, a tick) is decoration, not
  //     a route. Those are short: a real connector spans the gap between boxes.
  const defs = (src.match(/<defs>[\s\S]*?<\/defs>/) || [''])[0];
  const paths = [...src.matchAll(/<path\b([^>]*)\bd="([^"]+)"/g)]
    .filter(m => !defs.includes(m[0]))          // not a motion track
    .filter(m => !/\bid="/.test(m[1]))          // nor a referenced definition
    .map(m => m[2])
    .filter(d => {
      // Span of the path, walked properly: a decorative glyph (checkmark, tick)
      // stays inside ~30px, a real connector spans the gap between boxes. Naively
      // min/maxing every number in `d` gets this wrong, because relative commands
      // (`l 3.4 3.6`) are offsets, not coordinates — a 7px tick then measures as
      // hundreds of px and slips past the filter.
      const pts = flatten(d);
      if (pts.length < 2) return false;
      const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
      const span = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
      return span > 30;
    });
  for (const d of paths) {
    for (const [px, py] of flatten(d)) {
      const bad = boxes.find(b =>
        px > b.x + INSET && px < b.x + b.w - INSET &&
        py > b.y + INSET && py < b.y + b.h - INSET);
      if (bad) {
        console.log(`${file}: a connector runs through a box at (${px.toFixed(0)},${py.toFixed(0)}) ` +
                    `— box x${bad.x}..${bad.x + bad.w} y${bad.y}..${bad.y + bad.h}`);
        console.log(`  path: ${d.slice(0, 72)}`);
        hits++;
        break;
      }
    }
  }
  if (hits) problems += hits;
  else console.log(`${file}: ${paths.length} path(s), ${boxes.length} box(es) — no crossings`);
}

if (problems) {
  console.log(`\nFAIL — ${problems} connector(s) routed through a box`);
  process.exit(1);
}
console.log(`\nPASS — ${files.length} SVG assets, no connector crosses a box`);
