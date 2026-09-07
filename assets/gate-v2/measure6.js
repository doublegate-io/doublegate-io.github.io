// Objective 16px legibility measurement for the candidate marks.
//
// Vision reads of a 16px favicon are unreliable — three passes over the same
// sheet gave three different answers about whether marks "fuse". So measure it
// instead: rasterise each SVG at 16px into a canvas, then report
//
//   inkRatio   fraction of pixels that are not background
//   colours    distinct quantised non-background colours present
//   gapRows    horizontal scanlines that cross background between two inked runs
//   gapCols    vertical scanlines that do the same
//
// A mark whose elements stay separable has gaps; a blob does not. This is what
// "fused at 16px" actually means, and it is a number rather than an opinion.
//
// Usage:  CHROME_PATH=/path/to/chrome node assets/naming-options/measure.js

const fs = require('fs');
const path = require('path');

let puppeteer;
try {
  puppeteer = require('puppeteer-core');
} catch (e) {
  console.log('SKIP — puppeteer-core not installed (npm i -D puppeteer-core to enable)');
  process.exit(0);
}

const CHROME =
  process.env.CHROME_PATH ||
  path.join(
    process.env.HOME,
    '.cache/puppeteer/chrome/linux-152.0.7977.75/chrome-linux64/chrome',
  );
const DIR = __dirname + '/round6';
const SIZES = [16, 22, 32];

// The dark branch is what a favicon shows on a dark tab strip; resolve the media
// query away so the measurement does not depend on the harness's OS theme.
function darkOnly(svg) {
  return svg.replace(/@media \(prefers-color-scheme: light\) \{[\s\S]*?\n\s*\}\n/, '');
}

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({ executablePath: CHROME, args: ['--no-sandbox'] });
  } catch (e) {
    console.log('SKIP — no usable browser at ' + CHROME);
    process.exit(0);
  }

  const files = fs
    .readdirSync(DIR)
    .filter(f => f.startsWith('logo-') && f.endsWith('.svg'))
    .sort();

  const page = await browser.newPage();
  await page.setContent('<canvas id="c"></canvas>');

  const rows = [];
  for (const file of files) {
    const svg = darkOnly(fs.readFileSync(path.join(DIR, file), 'utf8'));
    const name = file.replace(/^logo-|\.svg$/g, '');
    const measured = {};
    for (const size of SIZES) {
      measured[size] = await page.evaluate(
        async (svgText, s) => {
          const url = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgText)));
          const img = new Image();
          img.width = s;
          img.height = s;
          await new Promise((res, rej) => {
            img.onload = res;
            img.onerror = rej;
            img.src = url;
          });
          const c = document.getElementById('c');
          c.width = s;
          c.height = s;
          const ctx = c.getContext('2d', { willReadFrequently: true });
          ctx.clearRect(0, 0, s, s);
          ctx.drawImage(img, 0, 0, s, s);
          const d = ctx.getImageData(0, 0, s, s).data;

          const at = (x, y) => {
            const i = (y * s + x) * 4;
            return { r: d[i], g: d[i + 1], b: d[i + 2], a: d[i + 3] };
          };
          // Alpha is the background test: these SVGs paint no background rect, so
          // anything the mark did not touch is transparent regardless of theme.
          const inked = p => p.a > 40;
          const key = p => `${p.r >> 5},${p.g >> 5},${p.b >> 5}`;

          let ink = 0;
          const colours = new Set();
          for (let y = 0; y < s; y++) {
            for (let x = 0; x < s; x++) {
              const p = at(x, y);
              if (inked(p)) {
                ink++;
                colours.add(key(p));
              }
            }
          }

          // A line "has a gap" when it goes ink -> background -> ink: two
          // separable elements along that axis.
          const gaps = vertical => {
            let n = 0;
            for (let a = 0; a < s; a++) {
              let runs = 0;
              let prev = false;
              for (let b = 0; b < s; b++) {
                const p = vertical ? at(a, b) : at(b, a);
                const now = inked(p);
                if (now && !prev) runs++;
                prev = now;
              }
              if (runs >= 2) n++;
            }
            return n;
          };

          return {
            inkRatio: +(ink / (s * s)).toFixed(3),
            colours: colours.size,
            gapRows: gaps(false),
            gapCols: gaps(true),
          };
        },
        svg,
        size,
      );
    }
    rows.push({ name, measured });
  }

  await browser.close();

  const w = Math.max(...rows.map(r => r.name.length)) + 2;
  console.log(
    'ink = fraction of pixels painted · col = distinct colours · gapR/gapC = ' +
      'scanlines separating two elements\n',
  );
  console.log(
    'mark'.padEnd(w) +
      SIZES.map(s => `${('@' + s).padStart(6)}  ink   col  gapR  gapC`).join('   '),
  );
  for (const r of rows) {
    let line = r.name.padEnd(w);
    line += SIZES.map(s => {
      const m = r.measured[s];
      return (
        ''.padStart(6) +
        String(m.inkRatio).padStart(5) +
        String(m.colours).padStart(6) +
        String(m.gapRows).padStart(6) +
        String(m.gapCols).padStart(6)
      );
    }).join('   ');
    console.log(line);
  }

  console.log('\nverdict at 16px:');
  for (const r of rows) {
    const m = r.measured[16];
    const separable = m.gapRows + m.gapCols;
    const verdict =
      separable >= 8 && m.colours >= 2
        ? 'separable'
        : separable >= 3
          ? 'marginal'
          : 'FUSED';
    console.log(
      `  ${r.name.padEnd(w)} ${verdict.padEnd(10)} ` +
        `(${separable} separating scanlines, ${m.colours} colours, ink ${m.inkRatio})`,
    );
  }
})();
