// Browser contracts for the homepage. Run after build.py; set CHROME_PATH.
const assert = require('node:assert/strict');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const puppeteer = require('puppeteer-core');

(async () => {
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || '/usr/bin/chromium',
    headless: true,
    args: ['--no-sandbox'],
  });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const url = pathToFileURL(path.join(__dirname, 'index.html')).href;
    for (const width of [1440, 768, 390, 320]) {
      await page.setViewport({ width, height: 844 });
      await page.goto(url);
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `overflow at ${width}`);
      assert(await page.$$eval('.overview-hero .btn', buttons => buttons.every(button => button.getBoundingClientRect().bottom <= innerHeight)), `opening actions below fold at ${width}`);
      const summary = await page.$('.overview-fit summary');
      await summary.focus();
      await page.keyboard.press('Enter');
      assert(await page.$eval('.overview-fit details', details => details.open));
      await page.keyboard.press('Enter');
      assert(!(await page.$eval('.overview-fit details', details => details.open)));
      assert(await page.$('#proof a[href="evidence.html"]'), 'research route missing');
      const evidence = await browser.newPage();
      await evidence.setViewport({ width, height: 844 });
      await evidence.goto(pathToFileURL(path.join(__dirname, 'evidence.html')).href);
      for (const source of ['snyk.io/blog/toxicskills', 'aeaweb.org/articles', 'engineering.fb.com/2026/09/02']) {
        assert(await evidence.$$eval('a[href]', (links, source) => links.some(a => a.href.includes(source)), source), `missing research source ${source}`);
      }
      await evidence.close();
      await page.locator('#skymap').scroll();
      await page.waitForSelector('.sky-inspect', { timeout: 20000 });
      const button = await page.$('.sky-inspect');
      const expected = await button.$eval('.txt', text => text.textContent);
      await button.focus();
      assert.equal(await page.$eval('#sky-pause', button => button.getAttribute('aria-pressed')), 'true');
      await page.keyboard.press('Enter');
      const selected = await page.$eval('#sky-selection-text', node => node.textContent);
      assert(expected.startsWith(selected), 'selected claim does not match activity');
      assert.match(await page.$eval('#sky-selection-outcome', node => node.textContent), /New|Sharpened|Merged|Held|Refused/);
      assert.equal(await page.$eval('#sky-selection', node => node.getAttribute('aria-live')), 'polite');
      assert(await page.$eval('.sky-inspect:focus', node => getComputedStyle(node).outlineStyle !== 'none'), 'keyboard focus invisible');
    }
    await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
    await page.goto(url);
    assert.equal(await page.$eval('#sky-pause', button => button.getAttribute('aria-pressed')), 'true');
    await page.setJavaScriptEnabled(false);
    await page.reload();
    await page.click('.overview-fit summary');
    assert(await page.$eval('.overview-fit details', node => node.open), 'disclosure needs JavaScript');
    assert(await page.$('#proof a[href="evidence.html"]'), 'evidence route needs JavaScript');
    assert(await page.$eval('.sky-still', image => image.complete && image.naturalWidth > 0));
    assert.deepEqual(errors, []);
    console.log('PASS — homepage at four widths: overflow, opening actions, keyboard disclosure/selection, focus, citations, reduced motion and no-JS fallback.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
