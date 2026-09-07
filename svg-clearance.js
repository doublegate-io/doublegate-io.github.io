#!/usr/bin/env node
/* No line may crowd a label.
 *
 * This is the check behind the complaint "text is standing in the way of the
 * lines". The other five SVG checks all measure a label against something that
 * is not a line, or a line against something that is not a label:
 *
 *   svg-geometry.js  text vs OTHER TEXT     (do two labels collide?)
 *   svg-bounds.js    text vs THE VIEWBOX    (is a label off-canvas?)
 *   svg-scale.js     text vs MINIMUM SIZE   (legible when scaled down?)
 *   svg-fit.js       text vs ITS OWN BOX    (does a label fit its container?)
 *   svg-routes.js    path vs BOX INTERIOR   (does a connector cross a box?)
 *   svg-clearance.js path vs TEXT           <- this one
 *
 * A connector can miss every box, stay on-canvas, be perfectly legible and
 * still run 2px under a descender, which is what makes a figure look like a
 * draft. Nothing in the suite could see that gap.
 *
 * Method: sample every stroked path and line, take every text node's real
 * rendered bounding box, and require MIN_CLEAR px between them. Rects are
 * excluded on purpose -- a box border legitimately sits close to the label
 * inside it, and svg-fit.js already governs that relationship.
 *
 * The floor is deliberately modest. It is a "this looks broken" tripwire, not a
 * typographic ideal: the shipped figure measured 5px at its worst point and the
 * replacement measures 9px, so 6 catches a regression toward the old layout
 * without forbidding a tight-but-intentional composition.
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const ASSETS = path.join(__dirname, 'assets');
const MIN_CLEAR = 6;
const SAMPLES = 300;

function chrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  for (const g of ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
                   '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']) {
    if (fs.existsSync(g)) return g;
  }
  const cache = path.join(process.env.HOME || '', '.cache/puppeteer/chrome');
  if (fs.existsSync(cache)) {
    for (const d of fs.readdirSync(cache)) {
      const p = path.join(cache, d, 'chrome-linux64', 'chrome');
      if (fs.existsSync(p)) return p;
    }
  }
  return null;
}

(async () => {
  const exe = chrome();
  if (!exe) {
    console.log('SKIP — no browser found (set CHROME_PATH). Not a failure.');
    process.exit(0);
  }

  const files = fs.readdirSync(ASSETS).filter(f => f.endsWith('.svg')).sort();
  const browser = await puppeteer.launch({ executablePath: exe, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  let failures = 0;

  for (const f of files) {
    await page.goto('file://' + path.join(ASSETS, f), { waitUntil: 'load' });

    const report = await page.evaluate((MIN_CLEAR, SAMPLES) => {
      const svg = document.querySelector('svg');
      const texts = [...svg.querySelectorAll('text')].map(t => {
        const b = t.getBBox();
        return { s: t.textContent.trim().replace(/\s+/g, ' ').slice(0, 46),
                 x: b.x, y: b.y, w: b.width, h: b.height };
      }).filter(t => t.w > 0);

      // Every stroked line and path. Rects are excluded: a box border sitting
      // close to its own label is correct, and svg-fit.js owns that check.
      const lines = [];
      for (const el of svg.querySelectorAll('path, line')) {
        const stroke = el.getAttribute('stroke');
        if (!stroke || stroke === 'none' || el.closest('defs')) continue;
        if (el.tagName.toLowerCase() === 'line') {
          lines.push({ id: 'stem', pts: [[el.x1.baseVal.value, el.y1.baseVal.value],
                                         [el.x2.baseVal.value, el.y2.baseVal.value]] });
        } else {
          const L = el.getTotalLength();
          if (!L) continue;
          const pts = [];
          for (let i = 0; i <= SAMPLES; i++) {
            const q = el.getPointAtLength((L * i) / SAMPLES);
            pts.push([q.x, q.y]);
          }
          lines.push({ id: stroke, pts });
        }
      }

      const bad = [];
      let worst = Infinity;
      for (const t of texts) {
        let best = Infinity, id = null, at = null;
        for (const ln of lines) {
          for (const [x, y] of ln.pts) {
            const dx = Math.max(t.x - x, 0, x - (t.x + t.w));
            const dy = Math.max(t.y - y, 0, y - (t.y + t.h));
            const d = Math.hypot(dx, dy);
            if (d < best) { best = d; id = ln.id; at = [Math.round(x), Math.round(y)]; }
          }
        }
        if (best < worst) worst = best;
        if (best < MIN_CLEAR) bad.push({ t: t.s, d: +best.toFixed(1), id, at });
      }
      return { bad, worst: +worst.toFixed(1), nText: texts.length, nLines: lines.length };
    }, MIN_CLEAR, SAMPLES);

    if (report.bad.length) {
      failures += report.bad.length;
      for (const b of report.bad) {
        console.log(`${f}: a line passes ${b.d}px from a label (need ${MIN_CLEAR}px) — "${b.t}"`);
        console.log(`  closest stroke ${b.id} at (${b.at[0]},${b.at[1]})`);
      }
    } else if (report.nText && report.nLines) {
      console.log(`${f}: ${report.nText} label(s), ${report.nLines} line(s) — tightest ${report.worst}px`);
    } else if (report.nText) {
      console.log(`${f}: ${report.nText} label(s), no lines to clear`);
    } else {
      console.log(`${f}: no labels`);
    }
  }

  await browser.close();
  console.log(failures
    ? `\nFAIL — ${failures} label(s) crowded by a line`
    : `\nPASS — every label keeps at least ${MIN_CLEAR}px clear of every line`);
  process.exit(failures ? 1 : 0);
})();
