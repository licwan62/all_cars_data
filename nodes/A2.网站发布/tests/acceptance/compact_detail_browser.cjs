const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.SIZE_MATCH_PLAYWRIGHT || 'playwright');
const args = Object.fromEntries(process.argv.slice(2).reduce((a,v,i,values)=>i%2?a:[...a,[v.replace(/^--/,''),values[i+1]]],[]));
const base = args.url || process.env.SIZE_MATCH_URL || 'http://127.0.0.1:1998/';
const out = path.resolve(args.out ? path.join(path.dirname(args.out), 'compact-detail') : process.env.SIZE_MATCH_OUT || 'output/playwright/compact-detail');
fs.mkdirSync(out, {recursive:true});
(async () => {
  const browser = await chromium.launch({headless:true,channel:process.env.SIZE_MATCH_BROWSER || undefined});
  const context = await browser.newContext({viewport:{width:1440,height:960},permissions:['clipboard-read','clipboard-write']});
  const page = await context.newPage();
  const errors = [], checks = [];
  page.on('pageerror', e => errors.push(e.message));
  const ready = () => page.waitForSelector('.search-summary[data-status="ready"]');
  const close = async () => { await page.keyboard.press('Escape'); await page.locator(".vehicle-detail-drawer").waitFor({state:"hidden"}); };
  const check = async (name, fn) => { await fn(); checks.push(name); console.log('PASS '+name); };
  try {
    await page.goto(base+'size-match.html?q=toyota%20camry'); await ready();
    await check('row opens vehicle drawer, SHAPE stays in details, copying is explicit', async () => {
      assert.equal(await page.locator('th[data-col-key="SHAPE"]').count(),0);
      await page.locator('.vehicle-detail-row [data-model-cell]').last().click();
      assert.equal(await page.locator('.vehicle-detail-drawer').isVisible(),true);
      assert.match(await page.locator('[data-detail-panel="vehicle"]').innerText(),/SHAPE/);
      assert.equal(await page.locator('[data-copy-text]').first().isVisible(),false);
      await page.locator('.vehicle-other-actions summary').click();
      const button=page.getByRole('button',{name:'复制车型信息',exact:true});
      const expected=await button.getAttribute('data-copy-text');
      await button.click();
      await page.waitForFunction(() => document.querySelector('[data-detail-status]').textContent==='已复制');
      assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),expected);
      await page.screenshot({path:path.join(out,'vehicle.png')});
      await close();
      assert.equal(await page.evaluate(()=>document.activeElement.matches('.vehicle-detail-row')),true);
    });
    await check('hover stays inline; click compares multiple aligned match points',async()=>{
      const button=page.locator('.fitment-trigger').last();
      await button.hover();
      assert.equal(await page.locator('.fitment-explanation').count(),0);
      assert.equal(await page.locator('.vehicle-detail-drawer').isVisible(),false);
      await button.click();
      assert.equal(await page.locator('[data-detail-panel="fitment"]').isVisible(),true);
      const points=await page.locator('.fitment-match-point').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('cx')));
      assert.ok(points.length>=3); assert.equal(new Set(points).size,1);
      await page.locator('.detail-rule summary').click();
      assert.match(await page.locator('.detail-rule').innerText(),/3XL.*US 命中规则/s);
      await page.screenshot({path:path.join(out,'fitment.png')}); await close();
    });
    await check('checkboxes preserve selection and never open the drawer',async()=>{
      await page.locator('tbody input[type="checkbox"]').first().check();
      assert.equal(await page.locator('.vehicle-detail-drawer').isVisible(),false);
      assert.equal(await page.locator('[data-evolution-toolbar]').isVisible(),true);
      await page.locator('[data-evolution-clear]').click();
    });
    await check('source rows, outline details and keyboard navigation remain usable',async()=>{
      await page.locator('[data-source-toggle]').first().click();
      await page.locator('.source-detail-row [data-model-cell]').first().click();
      assert.equal(await page.locator('[data-detail-panel="vehicle"]').isVisible(),true); await close();
      await page.locator('[data-result-view="outline"]').click();
      await page.locator('[data-detail-open]').first().click();
      assert.equal(await page.locator('.vehicle-detail-drawer').isVisible(),true); await close();
      await page.locator('[data-result-view="table"]').click();
      await page.locator('.vehicle-detail-row').first().focus(); await page.keyboard.press('Enter');
      assert.equal(await page.locator('.vehicle-detail-drawer').isVisible(),true); await close();
    });
    for(const query of ['toyota camry','ford f-150']) {
      await page.goto(base+'size-match.html?q='+encodeURIComponent(query)+'&view=full'); await ready();
      for(const width of [1920,1440,1366,1280]) await check(`${query}: no horizontal scroll at ${width}px`,async()=>{
        await page.setViewportSize({width,height:960});
        await page.waitForTimeout(350);
        const size=await page.locator('.size-results-wrap').evaluate(el=>({scroll:el.scrollWidth,client:el.clientWidth,top:el.getBoundingClientRect().top,page:document.documentElement.scrollWidth,viewport:innerWidth}));
        assert.ok(size.scroll<=size.client+1,JSON.stringify(size));
        assert.ok(size.page<=size.viewport,JSON.stringify(size));
        assert.ok(size.top<190,JSON.stringify(size));
        await page.screenshot({path:path.join(out,`${query.replaceAll(' ','-')}-${width}.png`)});
      });
    }
    await check('mobile drawer fits the viewport',async()=>{
      await page.setViewportSize({width:390,height:844}); await page.waitForTimeout(350);
      await page.locator('.vehicle-detail-row [data-model-cell]').first().click();
      assert.ok(await page.locator('.vehicle-detail-drawer').evaluate(el=>el.scrollWidth<=el.clientWidth));
      await page.getByRole('button',{name:'尺码匹配对比',exact:true}).click();
      await page.waitForTimeout(300); await page.screenshot({path:path.join(out,'mobile.png')}); await close();
    });
    assert.deepEqual(errors,[]);
  } finally { fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({checks,errors},null,2)); await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
