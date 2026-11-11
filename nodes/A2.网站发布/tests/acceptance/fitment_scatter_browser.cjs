const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.SIZE_MATCH_PLAYWRIGHT||'playwright');
const args=Object.fromEntries(process.argv.slice(2).reduce((a,v,i,values)=>i%2?a:[...a,[v.replace(/^--/,''),values[i+1]]],[]));
const base=args.url||'http://127.0.0.1:1998/',out=args.out||'output/playwright/scatter-review/browser.json';fs.mkdirSync(path.dirname(out),{recursive:true});
(async()=>{
  const browser=await chromium.launch({headless:true,channel:process.env.SIZE_MATCH_BROWSER||undefined});
  const page=await browser.newPage({viewport:{width:1440,height:1000},hasTouch:true});page.setDefaultTimeout(20000);
  const errors=[],results=[];let active='';page.on('pageerror',e=>errors.push(`${active}: ${e.stack||e.message}`));
  const models=[['nonpick','Toyota','Camry'],['nonpick','Honda','Accord']];
  const href=(source='US',selection=models)=>`${base}model-compare.html?${new URLSearchParams({source,models:JSON.stringify(selection),from:2010,to:2020})}`;
  const ready=()=>page.waitForFunction(()=>{const el=document.querySelector('[data-scatter-chart]');return el&&window.echarts?.getInstanceByDom(el)?.getOption().series?.some(s=>s.id==='fitment-scatter-points'&&s.data.length);});
  const option=()=>page.evaluate(()=>{const o=echarts.getInstanceByDom(document.querySelector('[data-scatter-chart]')).getOption();return {x:o.xAxis[0],y:o.yAxis[0],points:o.series.find(s=>s.id==='fitment-scatter-points').data,rules:o.series.find(s=>s.id==='fitment-scatter-rules').data};});
  async function tapPoint(){
    await page.locator('[data-scatter-chart]').scrollIntoViewIfNeeded();
    const p=await page.evaluate(()=>{const el=document.querySelector('[data-scatter-chart]'),c=echarts.getInstanceByDom(el),o=c.getOption(),data=o.series.find(s=>s.id==='fitment-scatter-points').data;
      const row=data.find(p=>p.value[1]>o.yAxis[0].min+1&&p.value[1]<o.yAxis[0].max-1)||data[0];const xy=c.convertToPixel({xAxisIndex:0,yAxisIndex:0},row.value.slice(0,2)),r=el.getBoundingClientRect();return {x:r.x+xy[0],y:r.y+xy[1]};});
    await page.touchscreen.tap(p.x,p.y);await page.waitForFunction(()=>document.querySelector('[data-scatter-details]').open);
  }
  const check=async(name,fn)=>{active=name;try{await fn();results.push({name,status:'passed'});console.log('PASS '+name);}catch(e){results.push({name,status:'failed',error:e.message});console.error('FAIL '+name+': '+e.message);}};
  try{
    await check('listing scatter shortcut opens full-history points for the chosen model',async()=>{
      await page.goto(`${base}size-match.html?q=toyota%20camry&view=compressed`);await page.waitForSelector('.search-summary[data-status="ready"]');
      await page.locator('[data-evolution-select]').first().check();
      await page.click('[data-scatter-link]');await ready();assert.ok(page.url().endsWith('#scatter'));assert.match(await page.locator('[data-compare-selected]').innerText(),/Toyota Camry/);assert.ok((await option()).points.length>12);
    });
    await check('scatter uses true length/year coordinates, area scaling and published rule overlays',async()=>{
      await page.goto(href());await ready();const o=await option();assert.match(o.x.name,/车长.*CM/);assert.equal(o.y.name,'年份');assert.ok(o.rules.length);
      assert.ok(o.points.every(p=>p.value[0]>400&&p.value[0]<600&&p.value[1]>=2010&&p.value[1]<=2020));
      const values=new Map();o.points.forEach(p=>{if(!values.has(p.dimensionId))values.set(p.dimensionId,new Set());values.get(p.dimensionId).add(p.value[2]);});assert.ok([...values.values()].every(v=>v.size===1));
      const max=Math.max(...o.points.map(p=>p.value[2]||0));for(const p of o.points.filter(p=>p.value[2]>0))assert.ok(Math.abs(p.symbolSize-Math.max(3,32*Math.sqrt(p.value[2]/max)))<1e-8);
      await tapPoint();assert.match(await page.locator('[data-scatter-records]').innerText(),/DIMENSION-ID/);assert.match(await page.locator('[data-scatter-records]').innerText(),/规则/);assert.match(await page.locator('[data-scatter-tooltip]').innerText(),/车长/);
    });
    await check('sales metric uses yearly values and survives regrouping, units, year and size filters',async()=>{
      await page.selectOption('[data-scatter-metric]','sales');let o=await option();const before=o.points.length;
      const values=new Map();o.points.forEach(p=>{if(!values.has(p.dimensionId))values.set(p.dimensionId,new Set());values.get(p.dimensionId).add(p.value[2]);});assert.ok([...values.values()].some(v=>v.size>1));
      await page.selectOption('[data-compare-group]','structure');assert.equal((await option()).points.length,before);
      const cm=(await option()).points[0];await page.selectOption('[data-compare-unit]','mm');o=await option();const mm=o.points.find(p=>p.recordKey===cm.recordKey&&p.value[1]===cm.value[1]);assert.ok(Math.abs(mm.value[0]-cm.value[0]*10)<1e-5);assert.equal(await page.locator('[data-scatter-metric]').inputValue(),'sales');
      await page.selectOption('[data-scatter-size]','3XL');assert.ok((await option()).rules.filter(r=>r.line).every(r=>!r.label||r.label.startsWith('3XL ')));
      await page.locator('[data-scatter-overlay]').uncheck();assert.equal((await option()).rules.length,0);
      await page.fill('[data-compare-from]','2015');await page.locator('[data-compare-to]').focus();assert.ok((await option()).points.every(p=>p.value[1]>=2015));
      await page.locator('[data-scatter-overlay]').check();assert.ok((await option()).rules.length);
    });
    await check('store mappings and missing metrics do not invent fitment or sales',async()=>{
      await page.goto(href('HNT'));await ready();assert.ok((await option()).rules.length);await tapPoint();assert.match(await page.locator('[data-scatter-records]').innerText(),/匹配尺码.*→ 发货/);
      await page.goto(href('EU',[['nonpick','BMW','7']]));await ready();let o=await option();assert.ok(o.points.every(p=>p.value[2]===null&&p.symbol==='diamond'));assert.ok(o.rules.length);
      await page.selectOption('[data-scatter-metric]','sales');o=await option();assert.ok(o.points.every(p=>p.value[2]===null));assert.match(await page.locator('[data-scatter-status]').innerText(),/数值缺失/);
    });
    await check('rule version mismatch keeps points but suppresses overlays',async()=>{
      await page.route('**/size-rules.json*',async route=>{const response=await route.fetch(),body=await response.json();body.source.version='mismatch';await route.fulfill({response,json:body});});
      await page.goto(href());await ready();assert.equal((await option()).rules.length,0);assert.match(await page.locator('[data-scatter-status]').innerText(),/同版本尺码规则/);await page.unroute('**/size-rules.json*');
    });
    await check('single-model dashboard shares scatter controls and retains them after unit rerender',async()=>{
      await page.goto(`${base}model-dashboard.html?source=US&kind=nonpick&make=Toyota&model=Camry`);await ready();await page.selectOption('[data-scatter-metric]','sales');await page.locator('[data-scatter-overlay]').uncheck();await page.click('[data-evo-unit="mm"]');await ready();assert.equal(await page.locator('[data-scatter-metric]').inputValue(),'sales');assert.equal((await option()).rules.length,0);assert.match((await option()).x.name,/MM/);
    });
    await check('successful sales retry clears the scatter error notice and restores point sizes',async()=>{
      await page.route('**/sales-year-data*',route=>route.abort());
      await page.goto(`${base}model-dashboard.html?source=US&kind=nonpick&make=Toyota&model=Camry`);await ready();await page.selectOption('[data-scatter-metric]','sales');await page.waitForSelector('[data-dashboard-sales-retry]');assert.match(await page.locator('[data-scatter-status]').innerText(),/加载失败/);
      await page.unroute('**/sales-year-data*');await page.click('[data-dashboard-sales-retry]');
      await page.waitForFunction(()=>!document.querySelector('[data-scatter-status]').textContent.includes('加载失败')&&echarts.getInstanceByDom(document.querySelector('[data-scatter-chart]')).getOption().series.find(s=>s.id==='fitment-scatter-points').data.some(p=>p.value[2]!==null));
    });
    for(const width of [1440,768,390,360])await check(`scatter ${width}px controls, chart and touch details`,async()=>{
      await page.setViewportSize({width,height:1000});await page.goto(href());await ready();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await tapPoint();
      await page.locator('[data-scatter-details]').evaluate(el=>el.open=false);
      await page.locator('.fitment-scatter').screenshot({path:path.join(path.dirname(out),`scatter-${width}.png`)});
    });
    await check('scatter has no browser script errors',async()=>assert.deepEqual(errors,[]));
  }finally{await browser.close();fs.writeFileSync(out,JSON.stringify({base,results,errors},null,2));}
  if(results.some(r=>r.status!=='passed'))process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
