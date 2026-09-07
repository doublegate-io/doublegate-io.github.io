// Every embedded figure's smallest label must render at 10px or larger, in the
// real page layout, at every breakpoint.
//
// This is not the same check as svg-geometry.js (text colliding) or svg-bounds.js
// (text outside the viewBox). Both of those measure the SVG in isolation, where it
// is always its natural size. A figure can pass both and still be unreadable on the
// page, because the container it sits in decides the scale:
//
//   cost-flow.svg was dropped into a `.wrap tight` section (max-width 900px). A
//   1040px figure scaled to 0.78, so its 11.5px labels rendered at 9.0px -- under
//   the floor assets/style.css explicitly commits to, and invisible to every gate
//   we had. Moving it to a full `.wrap` restored it to 11.0px.
//
// Usage:  CHROME_PATH=/path/to/chrome node svg-scale.js
//         BASE=http://127.0.0.1:8137 node svg-scale.js   (defaults to file://)
const path = require('path');
const fs = require('fs');

let puppeteer;
try {
  puppeteer = require('puppeteer-core');
} catch (e) {
  console.log('SKIP — puppeteer-core not installed');
  process.exit(0);
}

const CHROME = process.env.CHROME_PATH || '/usr/bin/chromium';
const ROOT = __dirname;
const BASE = process.env.BASE || ('file://' + ROOT);
const FLOOR = 10;               // px — the readability floor style.css commits to
const WIDTHS = [1280, 900, 390]; // desktop, the scroll breakpoint, phone

// Smallest font-size declared in each figure's own stylesheet. Read from the file
// rather than hardcoded, so a figure that grows a smaller class is caught too.
function smallestFontSize(svgPath) {
  const src = fs.readFileSync(svgPath, 'utf8');
  const sizes = [...src.matchAll(/font-size:\s*([\d.]+)px/g)].map(m => parseFloat(m[1]));
  const attrs = [...src.matchAll(/font-size="([\d.]+)"/g)].map(m => parseFloat(m[1]));
  const all = [...sizes, ...attrs];
  return all.length ? Math.min(...all) : null;
}

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  } catch (e) {
    console.log('SKIP — no usable browser at ' + CHROME);
    process.exit(0);
  }

  const pages = fs.readdirSync(ROOT).filter(f => f.endsWith('.html') && !f.startsWith('.tmp')).sort();
  let problems = 0;
  let checked = 0;

  for (const pg of pages) {
    for (const vw of WIDTHS) {
      const page = await browser.newPage();
      await page.setViewport({ width: vw, height: 900 });
      await page.goto(BASE + '/' + pg, { waitUntil: 'load' });
      await new Promise(r => setTimeout(r, 250));

      const figures = await page.evaluate(() => {
        return [...document.querySelectorAll('img[src$=".svg"]')].map(img => ({
          src: img.getAttribute('src'),
          shown: img.getBoundingClientRect().width,
          natural: img.naturalWidth,
        })).filter(f => f.natural > 200);   // skip the brand mark in the nav
      });

      for (const f of figures) {
        const svgPath = path.join(ROOT, f.src);
        if (!fs.existsSync(svgPath)) continue;
        const min = smallestFontSize(svgPath);
        if (min === null || !f.natural) continue;
        const effective = min * (f.shown / f.natural);
        checked++;
        if (effective < FLOOR) {
          problems++;
          console.log(
            `${pg} @${vw}px: ${f.src} smallest label renders at ${effective.toFixed(1)}px ` +
            `(declared ${min}px, scaled ${(f.shown / f.natural).toFixed(3)})`
          );
        }
      }
      await page.close();
    }
  }

  await browser.close();
  if (problems) {
    console.log(`\nFAIL — ${problems} figure/breakpoint pair(s) under the ${FLOOR}px floor`);
    process.exit(1);
  }
  console.log(`PASS — ${checked} figure/breakpoint pairs, all labels at or above ${FLOOR}px`);
})();
