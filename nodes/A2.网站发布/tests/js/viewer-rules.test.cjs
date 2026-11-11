// node --test tests/js/viewer-rules.test.cjs
// viewer-rules.js 是 2026-10-15 从 viewer.js 拆出的 SIZE 规则索引与悬停 HTML（拆分时与原实现在真实 size-rules.json /
// store-groups.json 上逐项比对一致）；这里固定其行为。
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const APP = path.join(__dirname, "..", "..", "src", "site_overrides", "assets", "app");
const R = require(path.join(APP, "viewer-rules.js"));

const RULES = {
  source: { version: "20261013_28" },
  regions: {
    US: {
      headers: ["尺码", "分类", "尺码池", "长上限", "插片指数上限", "插片指数下限", "车型白名单", "备注", "规则ID"],
      length_tolerance: 550,
      rows: [
        { 尺码: "2M", 分类: "两厢车", 尺码池: "H", 长上限: "4500", 插片指数上限: "999", 插片指数下限: "", 车型白名单: "", 备注: "", 规则ID: "aaa" },
        { 尺码: "3M", 分类: "两厢车", 尺码池: "H", 长上限: "4800", 插片指数上限: "1.2", 插片指数下限: "0.8", 车型白名单: "Golf", 备注: "<注>", 规则ID: "bbb" },
        { 尺码: "2M", 分类: "重复", 长上限: "1", 规则ID: "ccc" }
      ]
    },
    EU: {
      headers: ["尺码", "模式", "分类", "版本", "长上限", "规则ID"],
      length_tolerance: 550,
      rows: [{ 尺码: "2M", 模式: "标准", 分类: "两厢车", 版本: "v2", 长上限: "4400", 规则ID: "eee" }]
    },
    RU: {
      headers: ["亚马逊尺码", "OZON尺码", "发货尺码", "分类", "长_mm", "宽_mm", "高_mm", "余量长上限_mm", "规则ID"],
      length_tolerance: 635,
      rows: [{ 亚马逊尺码: "YS-380", OZON尺码: "XS", 发货尺码: "S", 分类: "轿车", 长_mm: "3800", 宽_mm: "1700", 高_mm: "1500", 余量长上限_mm: "", 规则ID: "rrr" }]
    }
  }
};
const GROUPS = { stores: { HNT: [{ 匹配尺码: "2M", 发货尺码: "SH1" }, { 匹配尺码: "3M", 发货尺码: "SH1" }, { 匹配尺码: "3M", 发货尺码: "SH2" }] } };
const GROUP_OF = { US: "US", HNT: "US", EU: "EU", RU: "RU" };
const MM = { measurement: (mm) => String(Math.round(mm)), unit: "mm" };
const CM = { measurement: (mm) => String(Math.round(mm * 0.1)), unit: "cm" };

function index() {
  const rules = R.createRuleIndex({ sourceGroup: (name) => GROUP_OF[name] || name });
  rules.load(RULES, GROUPS);
  return rules;
}

test("scope picks region by source group; stores fall back to US", () => {
  const rules = index();
  assert.deepEqual({ ...rules.scope("EU"), index: undefined }, { region: "EU", store: "", index: undefined });
  assert.equal(rules.scope("HNT").store, "HNT");
  assert.equal(rules.scope("HNT").region, "US");
  assert.equal(rules.scope("XX").region, "");
  assert.equal(rules.scope("XX").index, undefined);
});

test("first row per size wins; store shipping size lists every matching size", () => {
  const rules = index();
  const us = rules.ruleFor(" 2m ", "US");
  assert.equal(us.size, "2m");
  assert.deepEqual(us.matchSizes, ["2M"]);
  assert.equal(us.rows[0]["规则ID"], "aaa");
  assert.equal(us.tolerance, 550);
  const store = rules.ruleFor("sh1", "HNT");
  assert.deepEqual(store.matchSizes, ["2M", "3M"]);
  assert.deepEqual(store.rows.map((row) => row["规则ID"]), ["aaa", "bbb"]);
  assert.equal(rules.ruleFor("2M", "HNT"), null, "店铺 SIZE 是发货尺码，匹配尺码本身查不到");
  assert.equal(rules.ruleFor("", "US"), null);
  assert.equal(rules.ruleFor("2M", "XX"), null);
});

test("exact rule by 规则ID, with fallback to size lookup", () => {
  const rules = index();
  const record = { values: { 规则ID: "bbb", 匹配尺码: "", SIZE: "3M" } };
  assert.deepEqual(rules.exactForRecord(record, "US"), { ruleId: "bbb", row: RULES.regions.US.rows[1], region: "US", store: "", matchSize: "3M", tolerance: 550 });
  assert.equal(rules.exactForRecord({ values: { 规则ID: "bbb", SIZE: "SH1" } }, "HNT").matchSize, "", "店铺记录无 匹配尺码 时不拿发货尺码代替");
  assert.equal(rules.exactForRecord({ values: { 规则ID: "nope" } }, "US"), null);
  assert.equal(rules.exactForRecord({ values: {} }, "US"), null);
  const exact = rules.exactFor("bbb", "HNT", "SH1", "3M");
  assert.equal(exact.exact, true);
  assert.deepEqual(exact.matchSizes, ["3M"]);
  assert.deepEqual(rules.exactFor("nope", "HNT", "SH1", "3M"), rules.ruleFor("SH1", "HNT"));
});

test("load replaces previous data", () => {
  const rules = index();
  rules.load({ regions: {} }, {});
  assert.equal(rules.ruleFor("2M", "US"), null);
  assert.equal(rules.scope("HNT").store, "");
});

test("US markup: length range, unlimited insert index, escaped notes, store via-line", () => {
  const rules = index();
  const html = R.ruleMarkup(rules.ruleFor("SH1", "HNT"), MM);
  assert.match(html, /<div class="size-reference-title">SH1<small>US · 店铺 HNT 尺码规则<\/small><\/div>/);
  assert.match(html, /匹配尺码 2M → 发货 SH1/);
  assert.match(html, /<dt>适配车长<\/dt><dd>3950 – 4500 mm<\/dd>/);
  assert.match(html, /<dt>余量容差<\/dt><dd>≤ 550 mm<\/dd>/);
  assert.match(html, /<dt>插片指数<\/dt><dd>&gt; 0.8，≤ 1.2<\/dd>/, "上限 999 不显示，其余显示区间");
  assert.match(html, /<dd>&lt;注&gt;<\/dd>/);
  assert.equal((html.match(/size-reference-divider/g) || []).length, 1);
  assert.match(R.ruleMarkup(rules.ruleFor("2M", "US"), CM), /<dd>395 – 450 cm<\/dd>/, "单位随 format 切换");
  assert.match(R.ruleMarkup(rules.exactFor("aaa", "US", "2M", ""), MM), /US 命中规则 aaa/);
});

test("EU and RU markup", () => {
  const rules = index();
  assert.match(R.ruleMarkup(rules.ruleFor("2M", "EU"), MM), /标准 · 两厢车 · 版本 v2/);
  const ru = R.ruleMarkup(rules.ruleFor("ys-380", "RU"), MM);
  assert.match(ru, /轿车 · OZON XS · 发货 S/);
  assert.match(ru, /<em>宽上限<\/em><strong>1700 mm<\/strong>/);
  assert.match(ru, /<dt>适配车长<\/dt><dd>3165 – 3800 mm<\/dd>/, "行内 余量长上限_mm 为空时用报告容差 635");
});

test("dimension helpers", () => {
  assert.equal(R.dimensionMarkup("长", "4500", MM), "<span><em>长</em><strong>4500 mm</strong></span>");
  assert.equal(R.dimensionMarkup("长", "", MM), "<span><em>长</em><strong>0 mm</strong></span>");
  assert.equal(R.dimensionMarkup("长", "n/a", MM), "<span><em>长</em><strong>n/a</strong></span>");
  assert.equal(R.dimensionMarkup("长", undefined, MM), "<span><em>长</em><strong>-</strong></span>");
  assert.equal(R.insertDisplay("999", ""), "");
});

test("viewer.js delegates to viewer-rules.js and no longer keeps its own rule state", () => {
  const viewer = fs.readFileSync(path.join(APP, "viewer.js"), "utf8");
  assert.match(viewer, /window\.SizeViewerRules\.createRuleIndex\(/);
  for (const name of ["sizeRuleIndexes", "sizeRuleIdIndexes", "storeShippingSizes", "sizeRuleLengthMarkup", "sizeRuleRuMarkup", "sizeReferenceDimensionDisplay"]) {
    assert.ok(!viewer.includes(name), `${name} must live in viewer-rules.js`);
  }
});


test("neighbor bands bracket length in the same rule group, including exact upper boundary", () => {
  const rules = R.createRuleIndex({ sourceGroup: name => name });
  const rows = [4500, 4800, 5100].map((upper, i) => ({ 尺码: `S${i}`, 分类: "轿车", 尺码池: "S", 长上限: String(upper), 规则ID: `r${i}` }));
  rows.push({ 尺码: "wrong-pool", 分类: "轿车", 尺码池: "H", 长上限: "4799", 规则ID: "other" });
  rules.load({ regions: { US: { headers: ["尺码"], rows, length_tolerance: 550 } } }, {});
  const row = length => ({ values: { "L-MM": length, SIZE: "S1", 规则ID: "r1" } });
  assert.deepEqual(rules.neighbors(row(4800), "US").bands.map(b => b.upper), [4500, 4800]);
  assert.deepEqual(rules.neighbors(row(4801), "US").bands.map(b => b.upper), [4800, 5100]);
  assert.equal(rules.neighbors(row(5200), "US").bands.length, 1);
  assert.equal(rules.neighbors(row(""), "US").reason, "缺少车长");
  assert.equal(rules.neighbors(row(4800), "US", false).bands.length, 0);
  const fit = rules.neighbors(row(4800), "US");
  const html = R.fitmentMarkup(fit, MM);
  for (const color of ["#c8751c", "#258260", "#778496"]) assert.ok(html.includes(color));
  assert.equal(fit.bands[1].delta, 0);
  assert.equal(fit.bands[1].lower, 4250);
  assert.equal(fit.currentBand.upper, 4800);
  const differentMatch = rules.neighbors({ values: { "L-MM":4800, SIZE:"S2", 规则ID:"r2" } },"US");
  assert.equal(differentMatch.currentBand.upper,5100,"compact axis must use the published matched rule, not the nearest size");
  assert.ok(html.includes("余量 0 mm"));
  assert.ok(R.fitmentMarkup(fit, CM).includes("上限 480"));
  assert.deepEqual(fit.comparisonBands.map(b => b.upper), [4500,4800,5100]);
  const detail = R.fitmentDetailMarkup(fit, CM);
  const points = [...detail.matchAll(/class="fitment-match-point" cx="([^"]+)"/g)].map(m => m[1]);
  assert.equal(points.length,3);
  assert.equal(new Set(points).size,1,"each size uses the same length scale and matching point");
  assert.match(detail,/S1 · 当前匹配/);
  assert.match(detail,/上限 510 · 余量 30 cm/);
  assert.ok(!R.fitmentMarkup(fit,CM).includes('popover'));
  assert.ok(!R.fitmentDetailMarkup(rules.neighbors(row(4800),"US",false),CM).includes('<svg'));
});

test("evolution bands begin at the same family's preceding raw upper limit", () => {
  const rules = R.createRuleIndex({ sourceGroup: (source) => source });
  const rows = [
    { 尺码: "3M-0", 分类: "跑车", 尺码池: "S", 长上限: "4560", 插片指数上限: "999", 规则ID: "small" },
    { 尺码: "3L-0", 分类: "跑车", 尺码池: "S", 长上限: "4740", 插片指数上限: "120", 规则ID: "next" },
    { 尺码: "3XL-0", 分类: "跑车", 尺码池: "S", 长上限: "5050", 插片指数上限: "120", 规则ID: "large" },
    { 尺码: "YL", 分类: "越野车", 尺码池: "Y", 长上限: "4850", 规则ID: "other" }
  ];
  rules.load({ regions: { US: { headers: ["尺码"], rows } } });
  assert.equal(rules.lengthPredecessor({ region: "US", row: rows[0] }), null);
  assert.equal(rules.lengthPredecessor({ region: "US", row: rows[1] }), 4560);
  assert.equal(rules.lengthPredecessor({ region: "US", row: rows[2] }), 4740);
  const ranges = (upper, previousUpper) => R.fitmentSegments(upper, { previousUpper }).map(({ kind, from, to }) => [kind, from, to]);
  assert.deepEqual(ranges(5630, 5300), [["orange", 5300, 5430], ["green", 5430, 5630], ["over", 5630, 5680]]);
  assert.deepEqual(ranges(4740, 4560), [["green", 4560, 4740], ["over", 4740, 4790]]);
  assert.deepEqual(ranges(5300, null), [["green", 5100, 5300], ["over", 5300, 5350]]);
});

test("neighbor resolution respects store identity, ambiguous rule names, and RU dimensions", () => {
  const rules = index();
  assert.equal(rules.neighbors({ values: { "L-MM": 4400, SIZE: "SH1", 规则ID: "aaa" } }, "HNT").bands[0].upper, 4500);
  assert.equal(rules.neighbors({ values: { "L-MM": 4400, SIZE: "SH1" } }, "HNT").bands.length, 0);
  assert.equal(rules.neighbors({ values: { "L-MM": 4400, SIZE: "2M" } }, "US").bands.length, 0);
  assert.equal(rules.neighbors({ values: { "L-MM": 3700, "W-MM": 1800, "H-MM": 1400, 规则ID: "rrr" } }, "RU").bands.length, 0);
  assert.equal(rules.neighbors({ values: { "L-MM": 3700, "W-MM": 1600, "H-MM": 1400, 规则ID: "rrr" } }, "RU").bands[0].lower, 3165);
  assert.equal(rules.neighbors({ values: { "L-MM": 4300, SIZE: "2M", 规则ID: "eee" } }, "EU").bands[0].upper, 4400);
});
