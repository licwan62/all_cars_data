// 尺码配对页 A/B 行为比对：同一组交互分别在旧站点（当前 public）与新站点（沙箱构建）上执行，记录每步的可见状态。
// node ab_browser.cjs <baseURL> <输出 json> [截图目录]
const { chromium } = require("D:/Licheng/Repo/4Afitment/scrapers/4afitment/node_modules/playwright");
const fs = require("node:fs");

const [base, outFile, shotDir] = process.argv.slice(2);
const log = [];
const errors = [];

async function snapshot(page, step) {
  const state = await page.evaluate(() => {
    const text = (el) => (el ? el.textContent.replace(/\s+/g, " ").trim() : null);
    const rows = [...document.querySelectorAll(".size-results-table tbody tr")];
    return {
      summary: text(document.querySelector(".search-summary, .result-summary, [class*=summary]")),
      header: [...document.querySelectorAll(".size-results-table thead th")].map(text),
      rowCount: rows.length,
      firstRows: rows.slice(0, 6).map(text),
      activeKind: text(document.querySelector("[data-vehicle-kind].is-active")),
      activeUnit: text(document.querySelector("[data-size-unit].is-active")),
      activeSource: text(document.querySelector("[data-sidebar-source].is-active")),
      checked: document.querySelectorAll(".size-results-table [data-evolution-select]:checked").length,
      toolbar: text(document.querySelector("[data-evolution-toolbar]")),
      floating: text(document.querySelector(".size-reference-floating")),
      floatingVisible: !!document.querySelector(".size-reference-floating") && getComputedStyle(document.querySelector(".size-reference-floating")).display !== "none"
        && !document.querySelector(".size-reference-floating").hidden,
      evo: text(document.querySelector("[data-evo-subtitle]")),
      evoMeta: text(document.querySelector("[data-evo-meta]")),
      evoDetail: text(document.querySelector("[data-evo-detail]")),
      located: text(document.querySelector(".is-evolution-located")),
      sourceRows: document.querySelectorAll(".size-results-table tr.source-row, .size-results-table tr[class*=source]").length,
      filterChips: [...document.querySelectorAll("[data-filter-chip-key]")].map(text)
    };
  });
  log.push({ step, ...state });
  if (shotDir) await page.screenshot({ path: `${shotDir}/${String(log.length).padStart(2, "0")}-${step}.png` });
}

async function settle(page, ms = 600) {
  await page.waitForTimeout(ms);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
  await page.goto(`${base}/size-match.html`, { waitUntil: "networkidle" });
  await page.waitForSelector(".global-search-input");
  await settle(page, 1500);
  await snapshot(page, "load");

  // 产线 + 品牌（按 MAKE 分片懒加载）
  const makeSelect = page.locator("[data-lazy-make]");
  if (await makeSelect.count()) {
    const options = await makeSelect.locator("option").allTextContents();
    const ford = options.find((o) => /ford/i.test(o));
    if (ford) await makeSelect.selectOption({ label: ford });
    await settle(page, 2000);
  }
  await snapshot(page, "make-ford");

  // 车型代码检索（01039426 = Ford Mustang 1994-2026）
  await page.fill(".global-search-input", "01039426");
  await settle(page, 2500);
  await snapshot(page, "vehicle-code");

  // 排序：点 SIZE 列表头排序
  const sortButtons = page.locator("[data-size-sort-toggle]");
  const sortKeys = await sortButtons.evaluateAll((els) => els.map((el) => el.dataset.sizeSortToggle));
  const lengthKey = sortKeys.find((k) => /L-MM|长/.test(k)) || sortKeys[sortKeys.length - 1];
  await page.locator(`[data-size-sort-toggle="${lengthKey}"]`).click();
  await settle(page);
  await snapshot(page, `sort-${lengthKey}`);

  // 单位换算
  await page.locator('[data-size-unit="in"]').click();
  await settle(page);
  await snapshot(page, "unit-in");

  // SIZE 规则悬停
  const sizeCell = page.locator(".size-cell-has-ref").first();
  if (await sizeCell.count()) {
    await sizeCell.hover();
    await settle(page, 800);
  }
  await snapshot(page, "size-hover-in");
  await page.locator('[data-size-unit="mm"]').click();
  await settle(page);
  if (await sizeCell.count()) {
    await page.mouse.move(5, 5);
    await settle(page, 300);
    await page.locator(".size-cell-has-ref").first().hover();
    await settle(page, 800);
  }
  await snapshot(page, "size-hover-mm");

  // 展开来源行
  const toggle = page.locator("[data-source-toggle]").first();
  if (await toggle.count()) {
    await toggle.click();
    await settle(page);
  }
  await snapshot(page, "expand-source");

  // 勾选保留：勾两条，切单位后仍保留
  const checks = page.locator(".size-results-table tbody [data-evolution-select]");
  const n = await checks.count();
  for (let i = 0; i < Math.min(2, n); i += 1) await checks.nth(i).check();
  await settle(page);
  await page.locator('[data-size-unit="cm"]').click();
  await settle(page);
  await snapshot(page, "checked-after-unit");

  // 车型可视化 + 定位原记录
  const launch = page.locator("[data-evolution-launch]");
  if (await launch.count()) {
    await launch.click();
    await settle(page, 3000);
  }
  await snapshot(page, "evolution-open");
  const rulesToggle = page.locator('[data-evo-toggle="rules"]');
  if (await rulesToggle.count() && await rulesToggle.isEnabled()) {
    await rulesToggle.click();
    await settle(page, 800);
  }
  await snapshot(page, "evolution-rules");
  let locate = page.locator("[data-evo-locate]:visible").first();
  if (!(await locate.count())) {
    const chart = page.locator("[data-evo-chart]");
    const box = await chart.boundingBox();
    if (box) {
      for (const fx of [0.5, 0.4, 0.6, 0.3, 0.7]) {
        await page.mouse.click(box.x + box.width * fx, box.y + box.height * 0.5);
        await settle(page, 500);
        locate = page.locator("[data-evo-locate]:visible").first();
        if (await locate.count()) break;
      }
    }
  }
  await snapshot(page, "evolution-detail");
  if (await locate.count()) {
    await locate.click();
    await settle(page, 1500);
  }
  await snapshot(page, "locate");

  // 类别切换（皮卡）+ 筛选弹层
  await page.keyboard.press("Escape");
  await page.locator("[data-evo-close]").click().catch(() => {});
  await settle(page);
  await page.fill(".global-search-input", "");
  await settle(page, 1500);
  const pickup = page.locator('[data-vehicle-kind]').nth(1);
  if (await pickup.count()) {
    await pickup.click();
    await settle(page, 2500);
  }
  await snapshot(page, "kind-pickup");
  const filterButton = page.locator("[data-size-open-filter]").first();
  if (await filterButton.count()) {
    await filterButton.click();
    await settle(page);
    const first = page.locator(".header-filter-popover input[type=checkbox]").first();
    if (await first.count()) {
      await first.check();
      await settle(page);
    }
    await page.keyboard.press("Escape");
    await settle(page);
  }
  await snapshot(page, "filter");

  // 产线切换（侧栏 SOURCE：EU、RU）
  for (const source of ["EU", "RU"]) {
    const button = page.locator(`[data-sidebar-source="${source}"]`).first();
    if (await button.count()) {
      await button.click();
      await settle(page, 2500);
      const cell = page.locator(".size-cell-has-ref").first();
      if (await cell.count()) {
        await cell.hover();
        await settle(page, 800);
      }
    }
    await snapshot(page, `source-${source}`);
  }

  await browser.close();
  fs.writeFileSync(outFile, JSON.stringify({ base, errors, log }, null, 1));
  console.log(`${base}: ${log.length} steps, ${errors.length} errors`);
})().catch((error) => {
  fs.writeFileSync(outFile, JSON.stringify({ base, errors: [...errors, String(error.stack || error)], log }, null, 1));
  console.error(error);
  process.exit(1);
});
