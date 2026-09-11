// Browser contracts for the built homepage. CHROME_PATH required off Linux defaults.
// BASE_URL optionally exercises the exact public HTTP preview instead of the build tree.
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const { pathToFileURL } = require('node:url');
const puppeteer = require('puppeteer-core');
const expected = "every alert has an owner team, a runbook link and a severity; the linter rejects an alert missing any of them";
(async () => {
  const browser = await puppeteer.launch({executablePath: process.env.CHROME_PATH || '/usr/bin/chromium', headless: true, args: ['--no-sandbox']});
  const url = process.env.BASE_URL || pathToFileURL(path.join(__dirname, 'index.html')).href;
  const evidence = path.join(__dirname, '.tmp/site-fixes');
  fs.mkdirSync(evidence, {recursive: true});
  const measurements = [];
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    async function load() {
      await page.goto(url, {waitUntil: 'networkidle0'});
      await page.evaluate(() => document.fonts.ready);
      await page.addStyleTag({content: 'html {scroll-behavior:auto!important}'});
    }
    async function keyboardClick(selector) {
      await page.focus(selector);
      await page.keyboard.press('Enter');
    }
    for (const width of [1440, 768, 390, 320]) {
      await page.setViewport({width, height: 900});
      await load();
      assert.equal(await page.$eval('#sky-selection-text', e => e.textContent), expected);
      assert(await page.$('.sky-inspect[aria-pressed="true"]'), 'default example unselected');
      const geometry = await page.evaluate(() => {
        const rect = s => { const r = document.querySelector(s).getBoundingClientRect(); return {x:r.x, y:r.y+scrollY, width:r.width, height:r.height}; };
        const glyphs = [...document.querySelector('h1').childNodes].filter(n => n.nodeType === 3).flatMap(n => { const r = new Range();r.selectNodeContents(n);return [...r.getClientRects()].map(b => ({left:b.left,right:b.right})); });
        return {width:innerWidth, scrollWidth:document.documentElement.scrollWidth, canvas:rect('#sky'), selection:rect('#sky-selection'), architecture:rect('.architecture'), glyphs};
      });
      assert(geometry.scrollWidth <= width, `overflow ${width}`);
      assert(geometry.glyphs.every(r => r.left >= 0 && r.right <= width), `headline clipped ${width}`);
      assert.equal(await page.$$eval('.authority-route > li:not(.flow-connector)', e => e.length), 5);
      measurements.push(geometry);
      if (width === 1440 || width === 390) {
        await page.screenshot({path:path.join(evidence, `final-${width}-hero.png`)});
        await page.screenshot({path:path.join(evidence, `final-${width}-full.png`),fullPage:true});
        for (const [name, selector] of [['demo','#cost'],['model','#model']]) {
          await page.$eval(selector, e => e.scrollIntoView({behavior:'instant',block:'start'}));
          await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
          await page.screenshot({path:path.join(evidence,`final-${width}-${name}.png`)});
        }
      }
      await keyboardClick('#sky-pause');
      assert.equal(await page.$eval('#sky-pause', e => e.textContent), 'Resume');
      const count = await page.$eval('#sky-count', e => e.textContent);
      await new Promise(r => setTimeout(r, 700));
      assert.equal(await page.$eval('#sky-count', e => e.textContent), count);
      await keyboardClick('#sky-pause');
      assert.equal(await page.$eval('#sky-pause', e => e.getAttribute('aria-pressed')), 'false');
      await page.waitForFunction(() => document.querySelectorAll('.sky-inspect').length > 1, {timeout:20000});
      await page.focus('.sky-inspect');
      assert.equal(await page.$eval('#sky-pause', e => e.getAttribute('aria-pressed')), 'true');
      assert(await page.$eval('.sky-inspect:focus', e => getComputedStyle(e).outlineStyle !== 'none'), 'focus invisible');
      const activity = await page.$eval('.sky-inspect .txt', e => e.textContent);
      await page.keyboard.press('Enter');
      assert(activity.startsWith(await page.$eval('#sky-selection-text', e => e.textContent)));
      assert.equal(await page.$eval('#sky-selection', e => e.getAttribute('aria-live')), 'polite');
      assert.match(await page.$eval('#sky-selection-outcome', e => e.textContent), /New|Sharpened|Merged|Held|Refused/);
      await keyboardClick('#sky-zoom-in');
      await page.waitForFunction(() => document.querySelector('#sky-zoom').textContent !== '1×');
      await keyboardClick('#sky-fit');
      await page.waitForFunction(() => document.querySelector('#sky-zoom').textContent === '1×');
      for (const route of ['for-business.html','for-engineers.html']) {
        await load();
        const nav = width <= 1100 ? '.mobile-menu' : '.desktop-nav';
        if (width <= 1100) {
          await keyboardClick('.mobile-menu summary');
          assert(await page.$eval('.mobile-menu', e => e.open));
          assert(await page.$eval('.mobile-menu summary', e => getComputedStyle(e).outlineStyle !== 'none'));
        }
        await Promise.all([page.waitForNavigation(), keyboardClick(`${nav} a[href="${route}"]`)]);
        assert(new URL(page.url()).pathname.endsWith(route));
        assert(await page.$('h1'));
      }
      await page.emulateMediaFeatures([{name:'prefers-reduced-motion',value:'reduce'}]);
      await load();
      assert.equal(await page.$eval('#sky-pause', e => e.getAttribute('aria-pressed')), 'true');
      assert.equal(await page.$eval('#sky-selection-text', e => e.textContent), expected);
      assert.equal(await page.$eval('#sky-count', e => e.textContent), '1');
      await new Promise(r => setTimeout(r, 700));
      assert.equal(await page.$eval('#sky-count', e => e.textContent), '1');
      await page.emulateMediaFeatures([]);
    }
    await page.setViewport({width:390,height:900});
    await page.setJavaScriptEnabled(false);
    await page.goto(url, {waitUntil:'networkidle0'});
    assert.equal(await page.$eval('#sky-selection-text', e => e.textContent), expected + '.');
    assert(await page.$eval('#sky-selection-outcome', e => e.textContent.includes('New')));
    assert(await page.$eval('.sky-still', e => e.complete && e.naturalWidth > 0 && e.getBoundingClientRect().height >= 300));
    assert.equal(await page.$eval('.sky-controls', e => getComputedStyle(e).display), 'none');
    await keyboardClick('.mobile-menu summary');
    assert(await page.$eval('.mobile-menu', e => e.open), 'menu requires JS');
    await Promise.all([page.waitForNavigation(), keyboardClick('.mobile-menu a[href="for-business.html"]')]);
    assert(new URL(page.url()).pathname.endsWith('for-business.html'));
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(evidence,'final-browser.json'), JSON.stringify({url,measurements,errors},null,2));
    console.log(JSON.stringify({result:'PASS',url,checks:'4 widths: glyph fit/overflow, selected organizational example, pause/resume, keyboard selection/focus, zoom/whole-field, both audience routes, reduced motion; mobile no-JS image/text/menu/navigation',measurements,errors}));
  } finally {await browser.close();}
})().catch(e => {console.error(e);process.exitCode=1;});
