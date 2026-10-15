// 等价比对：拆分前 viewer.js 的 SIZE 规则函数 vs viewer-rules.js，使用真实 size-rules.json / store-groups.json。
// node equiv_rules.cjs <拆分前 viewer.js> <网站仓库根>
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");

const [origPath, repo] = process.argv.slice(2);
const app = path.join(repo, "site_overrides", "assets", "app");
const D = require(path.join(app, "viewer-data.js"));
const R = require(path.join(app, "viewer-rules.js"));
const orig = fs.readFileSync(origPath, "utf8");
const slice = (start, end) => {
  const i = orig.indexOf(start), j = orig.indexOf(end);
  assert.ok(i >= 0 && j > i, start);
  return orig.slice(i, j);
};
const rulesJson = JSON.parse(fs.readFileSync(path.join(repo, "public", "data", "generated", "size-rules.json"), "utf8"));
const groupsJson = JSON.parse(fs.readFileSync(path.join(repo, "public", "data", "generated", "store-groups.json"), "utf8"));
const matchSources = [
  { name: "US", group: "US" }, { name: "HNT", group: "US" }, { name: "TM", group: "US" },
  { name: "TM_拆分", group: "US" }, { name: "EU", group: "EU" }, { name: "RU", group: "RU" }
];
const sourceGroup = (name) => D.cleanField(matchSources.find((s) => s.name === name)?.group) || D.cleanField(name);

// 原实现：在同名依赖下求值切片
const body = `
  const sizeRuleIndexes = new Map(); const sizeRuleTolerances = new Map();
  const sizeRuleIdIndexes = new Map(); const storeShippingSizes = new Map();
  let sizeRulesOrigin = null, storeGroupsOrigin = null;
  function loadOrig(rules, groups) {
${slice("    sizeRuleIndexes.clear();\n", "  function resultHeaderClass(column) {\n")}
${slice("  function sizeRuleScope(sourceName) {\n", "  function ensureSizeReferenceFloating() {\n")}
${slice("  function sizeReferenceDimension(label, value) {\n", "  function sizeBackground(value) {\n")}
${slice("  function measurementDisplay(millimetres) {\n", "  function resultColumnValue(record, column) {\n")}
  return { loadOrig, sizeRuleScope, sizeRuleFor, exactSizeRule, exactSizeRuleFor, sizeRuleMarkup, sizeReferenceDimension };
`;
const searchState = { dimensionUnit: "mm", selectedSource: "" };
const matchDataOrigins = new Map([["m", { a0_version: rulesJson.source?.version }]]);
const O = new Function("cleanField", "escapeHtml", "sourceGroup", "searchState", "matchDataOrigins", "configuredMatchPath", "recordSourceName", body)(
  D.cleanField, D.escapeHtml, sourceGroup, searchState, matchDataOrigins, () => "m", (record) => record.source
);
O.loadOrig(rulesJson, groupsJson);
// 原实现 sizeRuleVersionsConsistent 读取闭包内的 sizeRulesOrigin（由 loadOrig 设置），此处已同版本

const index = R.createRuleIndex({ sourceGroup });
index.load(rulesJson, groupsJson);
const consistent = () => true;
const exactNew = (record) => (!D.cleanField(record?.values?.["规则ID"]) || !consistent()) ? null : index.exactForRecord(record, record.source);
const format = () => ({ measurement: (mm) => String(Math.round(mm * ({ mm: 1, cm: 0.1, in: 1 / 25.4 }[searchState.dimensionUnit] || 1))), unit: searchState.dimensionUnit });

const sources = [...matchSources.map((s) => s.name), "", "XX"];
const sizes = new Set(["", "  ", "zz"]);
const ids = new Set(["", "nope"]);
for (const payload of Object.values(rulesJson.regions)) {
  const key = (payload.headers || [])[0];
  for (const row of payload.rows) { sizes.add(row[key]); sizes.add(String(row[key]).toLowerCase()); ids.add(row["规则ID"]); }
}
for (const rows of Object.values(groupsJson.stores)) for (const row of rows) { sizes.add(row["发货尺码"]); sizes.add(row["匹配尺码"]); }

let checks = 0;
for (const unit of ["mm", "cm", "in"]) {
  searchState.dimensionUnit = unit;
  for (const source of sources) {
    const scopeOld = O.sizeRuleScope(source), scopeNew = index.scope(source);
    assert.deepEqual({ ...scopeNew, index: !!scopeNew.index }, { ...scopeOld, index: !!scopeOld.index });
    for (const size of sizes) {
      const a = O.sizeRuleFor(size, source), b = index.ruleFor(size, source);
      assert.deepEqual(b, a, `ruleFor ${size} ${source}`);
      if (a) assert.equal(R.ruleMarkup(b, format()), O.sizeRuleMarkup(a), `markup ${size} ${source} ${unit}`);
      for (const id of ids) {
        for (const match of ["", size]) {
          const x = O.exactSizeRuleFor(id, source, size, match), y = index.exactFor(id, source, size, match);
          assert.deepEqual(y, x, `exactFor ${id} ${size} ${source}`);
          if (x) assert.equal(R.ruleMarkup(y, format()), O.sizeRuleMarkup(x));
          checks += 1;
        }
        const record = { source, size, values: { "规则ID": id, "匹配尺码": "", SIZE: size } };
        assert.deepEqual(exactNew(record), O.exactSizeRule(record), `exactSizeRule ${id} ${source}`);
        const record2 = { source, size, values: { "规则ID": id, "匹配尺码": size } };
        assert.deepEqual(exactNew(record2), O.exactSizeRule(record2));
        checks += 2;
      }
    }
    for (const value of ["4500", "abc", "", "12.6", undefined]) {
      assert.equal(R.dimensionMarkup("长", value, format()), O.sizeReferenceDimension("长", value));
      checks += 1;
    }
  }
}
console.log(`equivalent: ${checks} checks, ${sizes.size} sizes, ${ids.size} rule ids, ${sources.length} sources`);
