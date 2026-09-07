// Measure every text node's right edge against the viewBox width.
//
// svg-geometry.js catches text nodes that COLLIDE with each other. It does not
// catch a single line that simply runs off the canvas — nothing overlaps it, so
// the overlap check passes while the sentence is clipped in the render. That is
// how the social card once shipped a 1214px tagline inside a 1200px viewBox.
//
// Usage:  CHROME_PATH=/path/to/chrome node svg-bounds.js
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
const DIR = path.join(__dirname, 'assets');
const ASSETS = 'file://' + DIR + '/';
const SVGS = fs.readdirSync(DIR).filter(f => f.endsWith('.svg')).sort();

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  } catch (e) {
    console.log('SKIP — no usable browser at ' + CHROME);
    process.exit(0);
  }

  let problems = 0;
  for (const file of SVGS) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1400, height: 1400 });
    await page.goto(ASSETS + file, { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 400));

    const res = await page.evaluate(() => {
      const svg = document.querySelector('svg');
      const vb = svg.viewBox.baseVal;
      const out = [];
      for (const t of document.querySelectorAll('text')) {
        const b = t.getBBox();
        const over = {
          right: b.x + b.width - (vb.x + vb.width),
          left: vb.x - b.x,
          bottom: b.y + b.height - (vb.y + vb.height),
          top: vb.y - b.y,
        };
        // 0.5px tolerance: sub-pixel glyph bearings are not overflow.
        const worst = Object.entries(over).filter(([, v]) => v > 0.5);
        if (worst.length) {
          out.push({
            txt: t.textContent.trim().slice(0, 52),
            edges: worst.map(([k, v]) => `${k} by ${v.toFixed(1)}px`).join(', '),
          });
        }
      }
      return { w: vb.width, h: vb.height, out };
    });

    if (res.out.length) {
      problems += res.out.length;
      console.log(`${file}: ${res.out.length} text node(s) outside the ${res.w}×${res.h} viewBox`);
      for (const o of res.out) console.log(`  "${o.txt}" — ${o.edges}`);
    } else {
      console.log(`${file}: all text inside ${res.w}×${res.h}`);
    }
    await page.close();
  }

  await browser.close();
  if (problems) {
    console.log(`\nFAIL — ${problems} text node(s) overflow their viewBox`);
    process.exit(1);
  }
  console.log(`\nPASS — ${SVGS.length} SVG assets within bounds`);
})();
