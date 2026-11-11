// Responsive workspace and shared chart acceptance against a built site.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.SIZE_MATCH_PLAYWRIGHT || 'playwright');
const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, i, values) => i % 2 ? pairs : [...pairs, [value.replace(/^--/, ''), values[i + 1]]], []));
const base = args.url || 'http://127.0.0.1:8766/';
const out = args.out || 'logs/acceptance/visual-workspace/browser.json';
fs.mkdirSync(path.dirname(out), { recursive: true });
(async () => {
  const browser = await chromium.launch({ headless: true, channel: process.env.SIZE_MATCH_BROWSER || undefined });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(12000);
  const errors = [], results = [];
  page.on('pageerror', error => errors.push(error.message));
  const ready = () => page.waitForSelector('.search-summary[data-status="ready"]');
  const open = async (query = 'toyota camry', mode = 'full', source = 'US') => {
    await page.goto(`${base}size-match.html?q=${encodeURIComponent(query)}&view=${mode}`);
    await ready();
    if (source !== 'US') {
      if (['EU', 'RU'].includes(source)) await page.click(`[data-sidebar-source="${source}"]`);
      else await page.selectOption('[data-lazy-source]', source);
      await ready();
    }
  };
  const launch = async () => {
    if (!await page.locator('[data-evolution-launch]').isVisible()) {
      await page.selectOption('[data-dashboard-select]', { index: 1 });
    }
    await page.click('[data-evolution-launch]');
    await page.waitForSelector('[data-evo-chart] canvas');
    await page.waitForFunction(()=>echarts.getInstanceByDom(document.querySelector('[data-evo-chart]'))?.getOption().series?.length);
  };
  const chart = (market=false) => page.evaluate(market => {
    const option = echarts.getInstanceByDom(document.querySelector(market ? '[data-market-chart]' : '[data-evo-chart]')).getOption();
    return { titles: option.title.map(t => t.text), series: option.series.map(s => ({ id:s.id, type:s.type, data:s.data })), zoom: option.dataZoom[0], axes: option.xAxis.map(a => a.type), xNames: option.xAxis.map(a=>a.name), yNames: option.yAxis.map(a=>a.name), grid:option.grid };
  },market);
  const check = async (name, run) => {
    try { await run(); results.push({ name, status:'passed' }); console.log(`PASS ${name}`); }
    catch (error) { results.push({ name, status:'failed', error:error.message }); console.error(`FAIL ${name}: ${error.message}`); }
  };
  try {
    await check('fitment columns stay aligned and record actions appear at the bottom', async () => {
      await page.setViewportSize({ width: 900, height: 900 });
      try {
        await open('acura', 'compressed');
        const toolbar = page.locator('[data-evolution-toolbar]');
        assert.equal(await toolbar.isVisible(), false);
        const wrap = page.locator('.size-results-wrap');
        assert.ok(await wrap.evaluate((el) => el.scrollWidth > el.clientWidth));
        const offsets = await wrap.evaluate((el) => {
          const headers = [...el.querySelectorAll('th')];
          const cells = el.querySelector('tbody tr').cells;
          const keys = ['L-CM', 'W-CM', 'H-CM', 'SIZE'];
          return [0, (el.scrollWidth - el.clientWidth) / 2, el.scrollWidth].flatMap((offset) => {
            el.scrollLeft = offset;
            return keys.map((key) => {
              const index = headers.findIndex((header) => header.dataset.colKey === key);
              return Math.abs(headers[index].getBoundingClientRect().left - cells[index].getBoundingClientRect().left);
            });
          });
        });
        assert.ok(offsets.every((offset) => offset < 1), `misaligned columns: ${offsets}`);
        await page.locator('[data-evolution-select]').first().check();
        assert.match(await toolbar.innerText(), /已选 1 条记录 · 1 款车型/);
        const scatter = new URL(await page.locator('[data-scatter-link]').getAttribute('href'), base);
        assert.equal(scatter.hash, '#scatter');
        assert.equal(JSON.parse(scatter.searchParams.get('models'))[0][1], 'Acura');
        await page.click('[data-evolution-clear]');
        assert.equal(await toolbar.isVisible(), false);
        assert.equal(await page.locator('[data-evolution-select]:checked').count(), 0);
      } finally {
        await page.setViewportSize({ width: 1440, height: 1000 });
      }
    });
    await check('full table: fitment SVG, thousand-unit sales, raw sorting and margin filter', async () => {
      await open();
      assert.ok(await page.locator('.fitment-mini svg').count());
      assert.equal(await page.locator('th[data-col-key="长度余量"]').count(), 0);
      assert.match(await page.locator('th[data-col-key="SIZE"]').innerText(), /尺码适配/);
      assert.match(await page.locator('th[data-col-key="销量合计"]').innerText(), /千辆/);
      const sales = await page.locator('td.sales-total-cell:not(.potential-cell)').evaluateAll(cells => cells.map(cell => [cell.textContent, cell.title]));
      for (const [shown, raw] of sales) assert.equal(Number(shown.replace(/,/g,'')), Math.round(Number(raw.replace(/[^\d.]/g,'')) / 1000));
      await page.click('[data-size-sort-toggle="销量合计"]');
      const raw = await page.locator('td.sales-total-cell:not(.potential-cell)').evaluateAll(cells => cells.map(cell => Number(cell.title.replace(/[^\d.]/g,''))));
      assert.deepEqual(raw, [...raw].sort((a,b) => a-b));
      await page.click('[data-size-open-filter="长度余量"]');
      assert.equal(await page.locator('[data-size-range-filter="长度余量"]').count(), 2);
      await page.keyboard.press('Escape');
      const fitment = page.locator('.fitment-mini').first();
      const rowHeight = await fitment.evaluate(el=>el.closest('tr').getBoundingClientRect().height);
      assert.equal(await fitment.locator('.fitment-trigger svg').count(),1);
      await fitment.locator('button').click();
      assert.equal(await page.locator('[data-detail-panel="fitment"]').isVisible(), true);
      await page.locator('.detail-rule summary').click();
      assert.match(await page.locator('.detail-rule').innerText(), /上限/);
      assert.equal(await fitment.evaluate(el=>el.closest('tr').getBoundingClientRect().height),rowHeight);
      assert.ok(rowHeight < 65, `compact row was ${rowHeight}px`);
      await page.keyboard.press('Escape');
      await page.locator('.vehicle-detail-drawer').waitFor({state:'hidden'});
      await page.mouse.move(0,0);
      await fitment.locator('button').hover();
      assert.equal(await page.locator('.vehicle-detail-drawer').isVisible(), false);
      assert.equal(await fitment.evaluate(el=>el.closest('tr').getBoundingClientRect().height),rowHeight);
      await page.mouse.move(0,0);
    });
    await check('model dashboard: exact model, deep link, shared controls and return state', async () => {
      await open('toyota camry', 'compressed');
      await page.selectOption('[data-dashboard-select]', { label: 'Toyota Camry' });
      await page.locator('[data-dashboard-link]').click();
      await page.waitForSelector('.is-dashboard [data-evo-chart] canvas');
      assert.ok(page.url().includes('model-dashboard.html'));
      assert.match(await page.locator('#evo-title').innerText(), /Toyota Camry.*Dashboard/);
      assert.equal(await page.locator('.evo-dialog').getAttribute('role'),'region');
      assert.equal(await page.locator('.dashboard-kpis article').count(),4);
      assert.match(await page.locator('[data-dashboard-sizes]').textContent(), /匹配尺码分布/);
      await page.waitForSelector('[data-market-chart] canvas');
      const salesOption=await chart(true);
      const bars=salesOption.series.filter(s=>s.id.startsWith('sales|'));
      assert.equal(bars.length,3);
      const total=salesOption.series.find(s=>s.id==='sales-total');
      assert.ok(total && total.type==='line');
      for (const row of total.data.filter(row=>row.value[1]!==null)) assert.equal(row.value[1],row.meta.raw/1000);
      for (const bar of bars) for (const row of bar.data) assert.equal(row.value[1],row.meta.raw/1000);
      await page.locator('[data-evo-legend-only]').first().click();
      assert.match(await page.locator('.dashboard-kpis').innerText(), /1 个可见配置/);
      const before = await page.locator('.dashboard-kpis').innerText();
      await page.click('[data-market-tab="potential"]');
      assert.equal(await page.locator('.dashboard-kpis').innerText(), before);
      assert.ok((await chart(true)).series.find(s=>s.id==='potential-total').data.some(({value:[,score]})=>score===null));
      await page.reload();
      await page.waitForSelector('.is-dashboard [data-evo-chart] canvas');
      await page.click('[data-evo-close]');
      await ready();
      assert.equal(await page.locator('.global-search-input').inputValue(),'toyota camry');
      assert.equal(await page.locator('.search-summary').getAttribute('data-view-mode'),'compressed');
      await page.goto(`${base}model-dashboard.html?source=HNT&kind=nonpick&make=Toyota&model=Camry`);
      await page.waitForSelector('.dashboard-kpis');
      assert.match(await page.locator('[data-dashboard-sizes]').textContent(), /发货尺码分布/);
      await page.goto(`${base}model-dashboard.html?source=EU&kind=nonpick&make=BMW&model=7`);
      await page.waitForSelector('.dashboard-kpis');
      await page.waitForFunction(()=>document.querySelector('.dashboard-sales')?.textContent.includes('暂无同口径'));
      await page.setViewportSize({width:390,height:844});
      await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth);
      await page.screenshot({path:path.join(path.dirname(out),'dashboard-mobile.png'),fullPage:true});
      await page.setViewportSize({width:1440,height:1000});
      await page.goto(`${base}model-dashboard.html?source=US&kind=nonpick&make=Toyota&model=Camry`);
      await page.waitForSelector('[data-market-chart] canvas');
      await page.screenshot({path:path.join(path.dirname(out),'dashboard-desktop.png'),fullPage:true});
    });
    await check('shared panel, compact tooltip and configuration selection persist across tabs', async () => {
      await open(); await launch();
      assert.equal(await page.locator('[data-evo-main]').count(),0);
      assert.equal((await chart()).titles.length, 2);
      assert.ok((await chart()).series.some(s=>s.id==='size-band'));
      const initial=await chart();
      assert.ok(initial.grid[1].left+initial.grid[1].width < initial.grid[0].left);
      assert.doesNotMatch(await page.locator('[data-evo-legend]').innerText(),/未注明版本|座位未知/);
      const railAlignment=await page.evaluate(()=>{
        const c=echarts.getInstanceByDom(document.querySelector('[data-evo-chart]')),o=c.getOption();
        const rail=o.series.find(s=>s.id==='size-band'),r=rail.data[0],year=(r.value[0]+r.value[1])/2;
        const length=o.series.find(s=>s.id.startsWith('length|')&&s.data.some(d=>d.meta?.recordKey===r.meta.recordKey));
        const lengthRow=length.data.find(d=>d.meta?.recordKey===r.meta.recordKey);
        return [c.convertToPixel({xAxisIndex:rail.xAxisIndex,yAxisIndex:rail.yAxisIndex},[r.value[2],year])[1],c.convertToPixel({xAxisIndex:0,yAxisIndex:0},[lengthRow.value[2],year])[1],o.dataZoom[0].yAxisIndex];
      });
      assert.ok(Math.abs(railAlignment[0]-railAlignment[1])<0.1);
      assert.deepEqual(railAlignment[2],[0,1]);
      assert.equal(await page.getAttribute('[data-evo-toggle="rules"]','aria-pressed'),'true');
      assert.ok((await chart()).series.some(s=>s.id === 'rule|length'));
      await page.waitForSelector('[data-evo-capsule]');
      assert.match((await chart()).xNames[0], /长度/);
      assert.equal((await chart()).yNames[0], "年份");
      assert.equal(await page.locator('[data-evo-legend]').count(),1);
      assert.equal(await page.locator('.evo-top-filters').count(),0);
      await page.locator('[data-evo-legend-only]').filter({hasText:'仅此项'}).nth(1).click();
      assert.match(await page.locator('.evo-legend-count').innerText(), /已显示 1/);
      const selected = await page.locator('[data-evo-legend-key]:checked').getAttribute('data-evo-legend-key');
      const point = await page.evaluate(() => {
        const element = document.querySelector('[data-evo-chart]');
        const instance = echarts.getInstanceByDom(element);
        const series = instance.getOption().series.find(s => s.id.startsWith('length|'));
        const row = series.data.find(d => d.meta?.recordKey);
        const xy = instance.convertToPixel({xAxisIndex: series.xAxisIndex, yAxisIndex: series.yAxisIndex}, [row.value[2],(row.value[0]+row.value[1])/2]);
        const rect = element.getBoundingClientRect(); return { x:rect.x+xy[0], y:rect.y+xy[1] };
      });
      await page.mouse.move(point.x,point.y);
      assert.match(await page.locator('[data-evo-tooltip]').innerText(), /车长/);
      assert.match(await page.locator('[data-evo-tooltip]').innerText(), /余量|超出/);
      assert.doesNotMatch(await page.locator('[data-evo-tooltip]').innerText(), /DIMENSION-ID|销量潜力调整/);
      await page.mouse.click(point.x,point.y);
      assert.match(await page.locator('[data-evo-detail]').innerText(), /已锁定记录/);
      const locked = await page.locator('[data-evo-detail]').innerText();
      await page.fill('[data-evo-year="from"]','1990');
      await page.fill('[data-evo-year="to"]','2026');
      await page.press('[data-evo-year="to"]','Enter');
      await page.click('[data-market-tab="potential"]');
      const option = await chart(true);
      assert.equal(option.titles.length,1);
      const bars = option.series.find(s => s.id.startsWith('potential|'));
      const total = option.series.find(s => s.id === 'potential-total');
      assert.equal(bars.type,'custom');
      assert.equal(total.type,'line');
      assert.ok(bars.data.every(({value:[year, score]})=>year>=1983 && year<=2026 && score>=0));
      assert.ok(bars.data.every(({value:[year,score]})=>total.data.some(({value:[y,t]})=>y===year && t===score)));
      assert.ok(option.axes.every(type => type === 'value'));
      assert.equal(option.zoom.startValue,1989.5);
      assert.equal(await page.locator('[data-evo-legend-key]:checked').getAttribute('data-evo-legend-key'),selected);
      assert.equal(await page.locator('[data-evo-detail]').innerText(),locked);
      await page.screenshot({path:path.join(path.dirname(out),'detail-desktop.png')});
    });
    await check('compressed sources, stores and pickup charts', async () => {
      await open('toyota camry','compressed');
      await page.locator('[data-source-toggle]').first().click();
      assert.ok(await page.locator('.source-detail-row .fitment-mini').count());
      await launch(); await page.click('[data-market-tab="potential"]');
      assert.ok((await chart(true)).series.some(s=>s.id.startsWith('potential|')));
      await open('toyota camry','full','HNT'); await launch();
      await page.click('[data-market-tab="potential"]');
      assert.ok((await chart(true)).series.some(s=>s.id.startsWith('potential|')));
      await open('ford f150'); await launch();
      await page.waitForSelector('[data-evo-capsule]');
      assert.match(await page.locator('[data-evo-rail-headers]').innerText(), /Reg-6\.5ft/);
      const bands = (await chart()).series.find(s => s.id === 'rule|length').data;
      assert.ok(bands.some(row => row.color === '#c8751c' && row.value[2] === 530 && row.value[3] === 543));
      await page.locator('[data-evo-chart]').scrollIntoViewIfNeeded();
      const pickupPoint = await page.evaluate(() => {
        const element = document.querySelector('[data-evo-chart]');
        const instance = echarts.getInstanceByDom(element);
        const series = instance.getOption().series.find(s => s.id.startsWith('length|') && s.name.includes('Regular'));
        const row = series.data.find(d => d.meta?.recordKey);
        const [x, y] = instance.convertToPixel({ gridIndex: 0 }, [row.value[2], (row.value[0] + row.value[1]) / 2]);
        const rect = element.getBoundingClientRect();
        return { x: rect.left + x, y: rect.top + y };
      });
      await page.mouse.move(pickupPoint.x, pickupPoint.y);
      await page.waitForSelector('[data-evo-tooltip] .evo-compact-tip');
      assert.equal(await page.locator('[data-evo-tooltip] .evo-compact-tip').count(), 1);
      await page.waitForFunction(() => {
        const instance = echarts.getInstanceByDom(document.querySelector('[data-evo-chart]'));
        const widths = instance.getModel().getSeries().filter(series => series.id.startsWith('length|')).map(series => {
          const el = series.getData().getItemGraphicEl(0);
          return el?.childAt?.(1)?.style;
        });
        return widths.some(style => style?.lineWidth === 5.5) && widths.some(style => style?.lineWidth === 1 && style?.stroke === '#8a94a5');
      });
      await page.mouse.move(0, 0);
      assert.equal(await page.locator('[data-evo-tooltip]').isVisible(), false);
      assert.match((await page.locator('[data-evo-capsule]').allTextContents()).join(' '), /ft/);
      await page.locator('[data-evo-capsule]').first().click();
      assert.match(await page.locator('[data-evo-detail]').innerText(), /已锁定记录/);
      const boxes=await page.locator('[data-evo-capsule]').evaluateAll(nodes=>nodes.map(n=>{const r=n.getBoundingClientRect();return {l:r.left,r:r.right,t:r.top,b:r.bottom};}));
      boxes.forEach((a,i)=>boxes.slice(i+1).forEach(b=>assert.ok(a.r<=b.l || b.r<=a.l || a.b<=b.t || b.b<=a.t)));
      await page.screenshot({path:path.join(path.dirname(out),'pickup-capsules-desktop.png')});
      await page.setViewportSize({width:390,height:900});
      await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth && [...document.querySelectorAll('[data-evo-capsule]')].every(el=>el.getBoundingClientRect().right<=innerWidth));
      await page.screenshot({path:path.join(path.dirname(out),'pickup-capsules-mobile.png')});
      await page.click('.evo-more > summary');
      await page.click('[data-evo-toggle="labels"]');
      assert.equal(await page.locator('[data-evo-capsule]').count(),0);
      await page.click('[data-evo-toggle="rules"]');
      assert.ok(!(await chart()).series.some(s=>s.id.startsWith('rule|')));
      await page.setViewportSize({width:1440,height:1000});
      await page.click('[data-evo-config]');
      assert.match(await page.locator('.evo-config-dialog').innerText(), /CAB/);
    });
    await check('EU missing potential is explicit; annual sales retry remains available', async () => {
      await open('bmw 7','full','EU'); await launch(); await page.click('[data-market-tab="potential"]');
      assert.match(await page.locator('[data-market-status]').innerText(), /暂无同口径市场潜力/);
      assert.equal(await page.locator('[data-market-chart]').isVisible(),false);
      await page.route('**/sales-year-data*', route=>route.abort());
      await open(); await launch();
      await page.waitForSelector('[data-dashboard-sales-retry]');
      await page.unroute('**/sales-year-data*'); await page.click('[data-dashboard-sales-retry]');
      await page.waitForFunction(()=>echarts.getInstanceByDom(document.querySelector('[data-market-chart]'))?.getOption().series.some(s=>s.id.startsWith('sales|')));
    });
    for (const width of [1440,768,390,360]) await check(`${width}px layout, drawer and chart switching`, async () => {
      await page.setViewportSize({width,height:900}); await open();
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth));
      if (width <= 760) {
        assert.equal(await page.locator('.viewer-side').isVisible(),false);
        await page.click('[data-mobile-filters]');
        assert.equal(await page.locator('.mobile-filter-drawer').evaluate(d=>d.open),true);
        await page.selectOption('[data-lazy-make]','Toyota'); await ready();
        await page.keyboard.press('Escape');
        assert.equal(await page.locator('.mobile-filter-drawer').evaluate(d=>d.open),false);
        assert.equal(await page.locator('[data-mobile-filters]').evaluate(e=>e===document.activeElement),true);
      }
      await page.screenshot({path:path.join(path.dirname(out),`table-${width}.png`)});
      await launch(); await page.click('[data-market-tab="potential"]');
      assert.ok(await page.locator('.evo-dialog').evaluate(d=>d.scrollWidth <= d.clientWidth+1));
      await page.click('[data-evo-config]'); await page.keyboard.press('Escape');
      assert.equal(await page.locator('.evo-overlay').isVisible(),true);
      await page.screenshot({path:path.join(path.dirname(out),`detail-${width}.png`)});
      await page.click('[data-evo-close]');
    });
    await check('no browser script errors',async()=>assert.deepEqual(errors,[]));
  } finally {
    await browser.close(); fs.writeFileSync(out,JSON.stringify({base,results,errors},null,2));
  }
  if(results.some(r=>r.status!=='passed')) process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1;});
