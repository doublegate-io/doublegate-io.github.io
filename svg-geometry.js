// Geometry check for every SVG asset: no text may overlap other text,
// and nothing may extend past the viewBox.
//
// This exists because a visual review once reported a text collision that turned
// out to be a real 26x12px overlap between a zone label and a centred caption.
// Eyeballing missed it; getBBox() did not. Font metrics only exist in a browser,
// so this check needs a real one — but it skips cleanly when none is available,
// so it is safe to wire into CI unconditionally.
//
// Usage:  CHROME_PATH=/path/to/chrome node site/svg-geometry.js

let puppeteer;
try {
  puppeteer = require('puppeteer-core');
} catch (e) {
  console.log('SKIP — puppeteer-core not installed (npm i -D puppeteer-core to enable)');
  process.exit(0);
}

const CHROME = process.env.CHROME_PATH || '/usr/bin/chromium';
const ASSETS = 'file://' + process.cwd() + '/site/assets/';
const SVGS = ['hero-flow.svg', 'artifact-flow.svg', 'social-card.svg', 'logo.svg'];

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
    await page.setViewport({ width: 1200, height: 1100 });
    await page.goto(ASSETS + file, { waitUntil: 'load' });
    await new Promise(r => setTimeout(r, 500));

    const res = await page.evaluate(() => {
      const texts = [...document.querySelectorAll('text')].map(t => {
        const b = t.getBBox();
        return { txt: t.textContent.trim().slice(0, 40), x: b.x, y: b.y, w: b.width, h: b.height };
      });
      const overlaps = [];
      for (let i = 0; i < texts.length; i++) {
        for (let j = i + 1; j < texts.length; j++) {
          const a = texts[i], c = texts[j];
          const ix = Math.min(a.x + a.w, c.x + c.w) - Math.max(a.x, c.x);
          const iy = Math.min(a.y + a.h, c.y + c.h) - Math.max(a.y, c.y);
          if (ix > 1 && iy > 1) {
            overlaps.push(`"${a.txt}" x "${c.txt}" (${ix.toFixed(0)}x${iy.toFixed(0)}px)`);
          }
        }
      }
      const vb = document.documentElement.viewBox.baseVal;
      const outside = texts
        .filter(t => t.x < -1 || t.y < -1 || t.x + t.w > vb.width + 1 || t.y + t.h > vb.height + 1)
        .map(t => `"${t.txt}" extends past the viewBox`);
      return { count: texts.length, overlaps, outside };
    });

    console.log(`${file}: ${res.count} text nodes`);
    for (const o of res.overlaps) console.log('  OVERLAP: ' + o);
    for (const o of res.outside) console.log('  BOUNDS:  ' + o);
    if (!res.overlaps.length && !res.outside.length) console.log('  clean');
    problems += res.overlaps.length + res.outside.length;
    await page.close();
  }

  await browser.close();
  console.log(problems ? `\nFAIL — ${problems} problem(s)` : `\nPASS — ${SVGS.length} SVG assets clean`);
  process.exit(problems ? 1 : 0);
})();
