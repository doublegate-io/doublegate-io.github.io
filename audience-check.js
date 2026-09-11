// Audience IA and shared-hero contracts against the approved HTTP preview.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {execFileSync} = require('node:child_process');
const puppeteer = require('puppeteer-core');
const manifest = JSON.parse(execFileSync('python3', ['-c', 'import build,json;print(json.dumps({"pages":build.LISTED,"audiences":build.AUDIENCES,"redirects":build.REDIRECTS}))'], {cwd:__dirname}));
const base = process.env.BASE_URL || 'http://127.0.0.1:8792/';
const output = path.join(__dirname,'.tmp/business-ia');
(async () => {
 fs.mkdirSync(output,{recursive:true});
 const browser = await puppeteer.launch({executablePath:process.env.CHROME_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const results=[], errors=[];
 try {
  const page = await browser.newPage();
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error') errors.push(m.text());});
  page.on('response',r=>{if(r.status()>=400) errors.push(`${r.status()} ${r.url()}`);});
  async function load(route) {
   await page.goto(new URL(route,base).href,{waitUntil:'networkidle0'});
   await page.evaluate(()=>document.fonts.ready);
   await page.addStyleTag({content:'html{scroll-behavior:auto!important}'});
  }
  async function keyboard(selector) {
   await page.focus(selector);
   assert(await page.$eval(selector,e=>getComputedStyle(e).outlineStyle!=='none'),'keyboard focus visible');
   await page.keyboard.press('Enter');
  }
  for(const width of [1440,768,390,320]) {
   await page.setViewport({width,height:900});
   for(const [route] of manifest.pages) {
    await load(route);
    const geometry=await page.evaluate(()=>{
     const rect=s=>{let r=document.querySelector(s).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
     const h=document.querySelector('h1'), range=new Range();range.selectNodeContents(h);
     return {scrollWidth:document.documentElement.scrollWidth, h1count:document.querySelectorAll('h1').length,hero:rect('.page-hero'),headline:rect('h1'),complement:rect('.page-hero-complement'),glyphs:[...range.getClientRects()].map(r=>({x:r.x,right:r.right})),font:parseFloat(getComputedStyle(h).fontSize),weight:parseInt(getComputedStyle(h).fontWeight),mail:[...document.querySelectorAll('a[href^="mailto:"]')].map(a=>({footer:!!a.closest('footer'),text:a.textContent,href:a.getAttribute('href')})),nextY:document.querySelector('.page-hero').nextElementSibling.getBoundingClientRect().y};
    });
    assert.equal(geometry.h1count,1,route);
    assert(geometry.scrollWidth<=width,`${route} overflow at ${width}: ${geometry.scrollWidth}`);
    assert(geometry.glyphs.every(r=>r.x>=0&&r.right<=width),`${route} headline clipped ${width}`);
    assert(geometry.font>=32&&geometry.weight>=600,`${route} headline hierarchy`);
    assert.equal(geometry.mail.length,1);
    assert(geometry.mail[0].footer&&geometry.mail[0].text==='Email'&&!geometry.mail[0].href.includes('?'));
    assert(geometry.hero.height<720,`${route} overlong opening ${width}`);
    assert(geometry.nextY-geometry.hero.bottom<=1,`${route} dead space after opening`);
    if(width>900) assert(geometry.complement.x>geometry.headline.x+geometry.headline.width,`${route} not split`);
    else assert(geometry.complement.y>=geometry.headline.bottom,`${route} not stacked`);
    const nav=await page.$$eval('.desktop-nav a',xs=>xs.map(a=>a.textContent));
    assert.deepEqual(nav,['Home','For business','For engineers','How it works','Evidence','GitHub']);
    if(width<=1100) {
     await keyboard('.mobile-menu summary');
     assert(await page.$eval('.mobile-menu',e=>e.open));
     await keyboard('.mobile-menu summary');
     assert(!(await page.$eval('.mobile-menu',e=>e.open)));
    }
    const audience=Object.entries(manifest.audiences).find(([,links])=>links.some(([href])=>href===route));
    if(audience) {
     assert.equal(await page.$eval('.audience-nav [aria-current="page"]',e=>e.getAttribute('href')),route);
     for(const [href] of audience[1].filter(([href])=>!href.startsWith('https:'))) {
      await load(route);
      const selector=`.audience-nav a[href="${href}"]`;
      await keyboard(selector);
      await page.waitForFunction(href=>location.pathname.endsWith(href.split('#')[0])&&location.hash===(href.includes('#')?'#'+href.split('#')[1]:''),{},href);
      if(href.includes('#')) assert(await page.$('#'+href.split('#')[1]));
     }
    }
    await load(route);
    if(width===1440||width===390) {
     await page.screenshot({path:path.join(output,`${route.replace('.html','')}-${width}-hero.png`)});
     if(audience) await page.screenshot({path:path.join(output,`${route.replace('.html','')}-${width}-full.png`),fullPage:true});
    }
    results.push({route,width,...geometry});
   }
  }
  // Exercise every original Commons section bookmark, not just a sample hash.
  const legacy={ 'for-organizations.html':['top','accountability','offering','honest'], 'commons.html':['top','gap','how','properties','appeals','why-contribute','limits','next'] };
  let redirectChecks=0;
  for(const [old,target] of Object.entries(manifest.redirects)) for(const hash of legacy[old]) {
   await load(`${old}?from=bookmark#${hash}`);
   await page.waitForFunction(target=>location.pathname.endsWith(target),{},target);
   assert.equal(new URL(page.url()).hash,'#'+hash);
   assert.equal(new URL(page.url()).search,'?from=bookmark');
   assert(await page.$('#'+hash),`${old} lost bookmark #${hash}`);
   redirectChecks++;
  }
  await load('evidence.html');
  const evidence=await page.$$eval('#findings .ev',xs=>({visible:xs.filter(x=>x.getBoundingClientRect().height>0).length,primaryLinks:xs.flatMap(x=>[...x.querySelectorAll('a.src')]).length}));
  const source=fs.readFileSync(path.join(__dirname,'pages/evidence.html'),'utf8').split('<section id="against"')[0];
  assert.equal(evidence.visible,(source.match(/<article class="ev">/g)||[]).length);
  assert.equal(evidence.primaryLinks,(source.match(/<a class="src"/g)||[]).length);
  assert.deepEqual(errors,[]);
  const result={result:'PASS',base,viewports:[1440,768,390,320],pageCount:manifest.pages.length,routeViewportChecks:results.length,redirectChecks,evidence,consoleErrors:errors,measurements:results};
  fs.writeFileSync(path.join(output,'browser.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify({...result,measurements:undefined},null,2));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
