const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.SIZE_MATCH_PLAYWRIGHT||'playwright');
const args=Object.fromEntries(process.argv.slice(2).reduce((a,v,i,values)=>i%2?a:[...a,[v.replace(/^--/,''),values[i+1]]],[]));
const base=args.url||'http://127.0.0.1:1997/',out=args.out||'output/playwright/compare-review/browser.json';
fs.mkdirSync(path.dirname(out),{recursive:true});
(async()=>{
  const browser=await chromium.launch({headless:true,channel:process.env.SIZE_MATCH_BROWSER||undefined});
  const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true});page.setDefaultTimeout(20000);
  const errors=[],results=[];page.on('pageerror',e=>errors.push(e.message));
  const models=[['nonpick','Toyota','Camry'],['nonpick','Honda','Accord']];
  const href=(source='US',selection=models)=>`${base}model-compare.html?${new URLSearchParams({source,models:JSON.stringify(selection)})}`;
  const ready=()=>page.waitForFunction(()=>document.querySelector('[data-compare-results]')?.hidden===false&&document.querySelector('[data-compare-run]')?.disabled===false);
  const option=name=>page.evaluate(name=>{const o=echarts.getInstanceByDom(document.querySelector(`[data-compare-chart="${name}"]`)).getOption();return {x:o.xAxis,y:o.yAxis,series:o.series.map(s=>({id:s.id,name:s.name,data:s.data}))};},name);
  const check=async(name,fn)=>{try{await fn();results.push({name,status:'passed'});console.log('PASS '+name);}catch(e){results.push({name,status:'failed',error:e.message});console.error('FAIL '+name+': '+e.message);}};
  try{
    await check('comparison entry preserves listing return state',async()=>{
      await page.goto(`${base}size-match.html?q=toyota%20camry&view=compressed`);await page.waitForSelector('.search-summary[data-status="ready"]');
      assert.equal(await page.locator('[data-evolution-toolbar]').isVisible(), false);
      await page.selectOption('[data-dashboard-select]', { label: 'Toyota Camry' });
      assert.ok(await page.locator('[data-dashboard-link]').isVisible());
      await page.click('[data-compare-link]');await ready();assert.match(await page.locator('[data-compare-selected]').innerText(),/Toyota Camry/);
      await page.click('[data-compare-back]');await page.waitForSelector('.search-summary[data-status="ready"]');
      assert.equal(await page.locator('.global-search-input').inputValue(),'toyota camry');assert.equal(await page.locator('.search-summary').getAttribute('data-view-mode'),'compressed');
    });
    await check('cross-brand comparisons preserve totals under structure regrouping and unit conversion',async()=>{
      await page.goto(href());await ready();assert.equal(await page.locator('[data-compare-table] tbody tr').count(),2);
      const original=await option('sales');assert.equal(original.series.length,3);const total=original.series.find(s=>s.id==='compare-total').data;
      const cm=(await option('dimensions')).series[0].data[0].value;
      await page.selectOption('[data-compare-unit]','mm');const mm=(await option('dimensions')).series[0].data[0].value;assert.ok(Math.abs(cm[1]*10-mm[1])<1e-5);
      await page.selectOption('[data-compare-group]','structure');assert.ok(await page.locator('[data-compare-table] tbody tr').count()>2);
      assert.deepEqual((await option('sales')).series.find(s=>s.id==='compare-total').data,total);
      assert.match(await page.locator('[data-compare-table]').innerText(),/Sedan/);
      await page.selectOption('[data-compare-structure]','Sedan');assert.equal(await page.locator('[data-compare-table] tbody tr').count(),1);
      await page.fill('[data-compare-from]','2010');await page.locator('[data-compare-to]').focus();await page.fill('[data-compare-to]','2020');await page.locator('[data-compare-group]').focus();
      assert.equal((await option('sales')).series.find(s=>s.id==='compare-total').data.length,11);
      await page.reload();await ready();assert.equal(await page.locator('[data-compare-group]').inputValue(),'structure');assert.equal(await page.locator('[data-compare-from]').inputValue(),'2010');assert.equal(await page.locator('[data-compare-structure]').inputValue(),'Sedan');
      await page.selectOption('[data-compare-structure]','');await page.selectOption('[data-compare-unit]','cm');await page.click('[data-compare-years]');
      await page.screenshot({path:path.join(path.dirname(out),'structure-desktop.png'),fullPage:true});
    });
    await check('model selection spans brands and categories; pickup structure exposes CAB BED and versions',async()=>{
      await page.goto(href());await ready();await page.getByRole('checkbox',{name:'RAV4',exact:true}).check();
      await page.selectOption('[data-compare-make]','Honda');await page.getByRole('checkbox',{name:'Civic',exact:true}).check();
      assert.equal(await page.locator('[data-compare-remove]').count(),4);await page.click('[data-compare-run]');await ready();assert.equal(await page.locator('[data-compare-table] tbody tr').count(),4);
      await page.goto(href('US',[['pick','Ford','F-150'],['pick','Chevrolet','Silverado 1500']]));await ready();await page.selectOption('[data-compare-group]','structure');
      assert.match(await page.locator('[data-compare-table]').innerText(),/SuperCrew/);assert.match(await page.locator('[data-compare-table]').innerText(),/Raptor/);assert.match(await page.locator('[data-compare-table]').innerText(),/ft/);
      await page.selectOption('[data-compare-kind]','nonpick');await page.selectOption('[data-compare-make]','Toyota');await page.getByRole('checkbox',{name:'Camry',exact:true}).check();await page.click('[data-compare-run]');await ready();
      assert.equal(await page.locator('[data-compare-remove]').count(),3);assert.match(await page.locator('[data-compare-table]').innerText(),/Sedan/);
      await page.click('[data-compare-clear]');assert.equal(await page.locator('[data-compare-results]').isVisible(),false);assert.equal(await page.locator('[data-compare-remove]').count(),0);
    });
    await check('EU missing markets and source reset cannot mix country data',async()=>{
      await page.goto(href('EU',[['nonpick','BMW','7'],['nonpick','BMW','3']]));await ready();assert.match(await page.locator('[data-compare-sales-status]').innerText(),/暂无同口径/);assert.equal(await page.locator('[data-compare-chart="sales"]').isVisible(),false);assert.match(await page.locator('[data-compare-potential-status]').innerText(),/暂无同口径/);
      await page.selectOption('[data-compare-source]','US');assert.equal(await page.locator('[data-compare-remove]').count(),0);assert.equal(await page.locator('[data-compare-results]').isVisible(),false);
      await page.selectOption('[data-compare-make]','Toyota');await page.getByRole('checkbox',{name:'Camry',exact:true}).check();await page.click('[data-compare-run]');await ready();assert.equal(await page.locator('[data-compare-chart="sales"]').isVisible(),true);
    });
    await check('sales failure retains dimensions and retry restores the market chart',async()=>{
      await page.route('**/sales-year-data*',r=>r.abort());await page.goto(href());await ready();await page.waitForSelector('[data-compare-retry]');assert.ok((await option('dimensions')).series[0].data.length);
      await page.unroute('**/sales-year-data*');await page.click('[data-compare-retry]');await ready();assert.equal(await page.locator('[data-compare-chart="sales"]').isVisible(),true);
    });
    for(const width of [1440,768,390,360])await check(`comparison ${width}px responsive charts and local table scrolling`,async()=>{
      await page.setViewportSize({width,height:900});await page.goto(href());await ready();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
      if(width<=760)assert.equal(await page.locator('.compare-selection').evaluate(el=>el.open),false);
      await page.locator('[data-compare-chart="dimensions"]').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(path.dirname(out),`compare-${width}.png`)});
      assert.ok(await page.locator('.compare-table-wrap').evaluate(el=>el.clientWidth<=innerWidth));
      await page.selectOption('[data-compare-metric]','widthMm');assert.match((await option('dimensions')).x[0].name,/车宽/);
    });
    await check('comparison has no browser script errors',async()=>assert.deepEqual(errors,[]));
  }finally{await browser.close();fs.writeFileSync(out,JSON.stringify({base,results,errors},null,2));}
  if(results.some(r=>r.status!=='passed'))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
