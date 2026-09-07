#!/usr/bin/env node
/* Every label must fit inside the box that contains it.
 *
 * This is the check that was missing, and its absence shipped the worst-looking
 * figure on the site. hero-flow.svg had text wider than its container in ELEVEN
 * places at once — "READABLE COMPANY-WIDE" was 198px of text in a 180px box, so
 * it bled 9px past the border on both sides. Six boxes, every one of them
 * overflowing, which is precisely what makes a diagram read as amateur.
 *
 * None of the other four SVG checks could see it, because none of them compares
 * a label to its own container:
 *
 *   svg-geometry.js  text vs OTHER TEXT      (do two labels collide?)
 *   svg-bounds.js    text vs THE VIEWBOX     (is a label off-canvas?)
 *   svg-scale.js     text vs MINIMUM SIZE    (is it legible when scaled down?)
 *   svg-routes.js    path vs BOX             (does a connector cross a box?)
 *   svg-fit.js       text vs ITS OWN BOX     <- this one
 *
 * A label that overflows is still on-canvas, still legible, and still not
 * touching another label, so the whole existing suite reported the file clean.
 *
 * Method: measure real rendered text with getBBox() in a browser, then for each
 * text node find the smallest rect that contains its anchor point and require
 * the text to fit within that rect minus a padding margin. Centre-anchored text
 * in a rounded box needs real breathing room, not zero clearance, or it reads as
 * cramped even when it technically fits.
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const ROOT = __dirname;
const ASSETS = path.join(ROOT, 'assets');
const PAD = 8;          // minimum clear space between glyph edge and box border
const IGNORE_W = 0.985; // a rect this close to the viewBox is a background, not a container

function chrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  const guesses = [
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  ];
  for (const g of guesses) if (fs.existsSync(g)) return g;
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
  let measured = 0;

  for (const f of files) {
    await page.goto('file://' + path.join(ASSETS, f), { waitUntil: 'load' });

    const bad = await page.evaluate((PAD, IGNORE_W) => {
      const svg = document.querySelector('svg');
      const vb = svg.viewBox.baseVal;
      const out = [];

      // every candidate container, smallest first, so a label inside a nested
      // box is measured against the box it actually sits in
      const rects = [...svg.querySelectorAll('rect')]
        .map(r => ({
          x: r.x.baseVal.value, y: r.y.baseVal.value,
          w: r.width.baseVal.value, h: r.height.baseVal.value,
        }))
        .filter(r => !(r.w >= vb.width * IGNORE_W && r.h >= vb.height * IGNORE_W))
        .sort((a, b) => a.w * a.h - b.w * b.h);

      for (const t of svg.querySelectorAll('text')) {
        const bb = t.getBBox();
        if (!bb.width) continue;
        const cx = bb.x + bb.width / 2, cy = bb.y + bb.height / 2;
        const box = rects.find(r => cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + r.h);
        if (!box) continue;   // free-standing label, svg-bounds.js covers it
        const avail = box.w - 2 * PAD;
        if (bb.width > avail) {
          out.push({
            text: t.textContent.trim().slice(0, 52),
            tw: +bb.width.toFixed(1),
            bw: +box.w.toFixed(1),
            avail: +avail.toFixed(1),
            over: +(bb.width - avail).toFixed(1),
          });
        }
      }
      return out;
    }, PAD, IGNORE_W);

    const total = await page.evaluate(() => document.querySelectorAll('text').length);
    measured += total;

    if (bad.length) {
      failures += bad.length;
      for (const b of bad) {
        console.log(`${f}: label overflows its box by ${b.over}px — "${b.text}"`);
        console.log(`  text ${b.tw}px, box ${b.bw}px, usable ${b.avail}px (${PAD}px padding each side)`);
      }
    } else {
      console.log(`${f}: ${total} label(s) — all fit`);
    }
  }

  await browser.close();
  console.log(failures
    ? `\nFAIL — ${failures} label(s) wider than the box containing them`
    : `\nPASS — ${measured} labels across ${files.length} SVG assets, every one fits its box`);
  process.exit(failures ? 1 : 0);
})();
