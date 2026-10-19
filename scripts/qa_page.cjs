// Run after building and verifying one version; never submits a reservation.
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const version = process.argv[2];
  assert.match(version, /^0[1-9]$|^10$/);
  const out = process.argv[3]; fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({headless:true, channel:'chrome'});
  const results = [];
  for (const width of [1440,390,320]) {
    const page = await browser.newPage({viewport:{width,height:900}});
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.route('**/functions/v1/**', route => route.abort());
    await page.goto(`http://127.0.0.1:4187/dist/hoban/${version}/`, {waitUntil:'networkidle'});
    const close = page.locator('.modal-close');
    if (await close.isVisible()) await close.click();
    await page.evaluate(async () => {
      const images = [...document.images];
      for (const img of images) img.loading = 'eager';
      await Promise.all(images.map(i => i.decode().catch(() => {})));
    });
    const state = await page.evaluate(() => ({
      viewport: innerWidth, scrollWidth: document.documentElement.scrollWidth,
      h1: [...document.querySelectorAll('h1')].map(e=>e.textContent),
      metadata: ['title','meta[name="description"]','meta[name="robots"]','link[rel="canonical"]'].map(s=>({selector:s,count:document.head.querySelectorAll(s).length,total:document.querySelectorAll(s).length})),
      brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.getAttribute('src')),
      updated: document.querySelector('time[data-date-kind="updated"]')?.dateTime
    }));
    assert(state.scrollWidth <= width, JSON.stringify(state));
    assert.equal(state.h1.length,1); assert.equal(state.brokenImages.length,0);
    assert(state.metadata.every(m=>m.count===1 && m.total===1));
    assert.equal(errors.length,0,errors.join('\n'));
    await page.screenshot({path:path.join(out,`${version}-${width}-hero.png`)});
    await page.locator('#version-answer, #focus').scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(out,`${version}-${width}-answer.png`)});
    if (width===390) {
      await page.locator('.menu-toggle').click();
      assert(await page.locator('#mobile-menu').isVisible());
      await page.locator('#mobile-menu a[href="#types"]').click();
      await page.locator('#unit-select').count().then(async n=>{if(n)await page.locator('#unit-select').selectOption('135');});
    }
    await page.locator('#budget-unit').selectOption('135');
    assert.equal(await page.locator('#budget-price').inputValue(), '71,600');
    await page.locator('#budget-unit').selectOption('84A');
    await page.locator('.site-footer').scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(out,`${version}-${width}-footer.png`)});
    results.push({...state,errors}); await page.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(out,`${version}-browser.json`), JSON.stringify(results,null,2));
  console.log(`${version}: browser DOM, images, widths 1440/390/320, menu and calculator passed; no reservation submitted`);
})().catch(e=>{console.error(e);process.exit(1)});
