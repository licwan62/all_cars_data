// 尺码配对页 SIZE 规则（viewer.js 的 SIZE 悬停与车型可视化规则叠加）：规则索引、店铺发货尺码换回匹配尺码、按 规则ID 精确查找、悬停 HTML。
// 数据来自 size-rules.json（A0 <国别>/尺码规则.json）与 store-groups.json（A0 US/店铺货架.json）。不依赖 DOM 与页面状态：
// 来源分组（sourceGroup）由页面注入，长度显示单位每次调用传入 format = { measurement(mm) → 字符串, unit }。
// 浏览器下挂到 window.SizeViewerRules（须在 viewer-data.js 之后、viewer.js 之前加载），Node 下 module.exports 供 node --test 使用。
// 2026-10-15 从 viewer.js 拆出，查找与 HTML 结果与拆分前逐项一致。
(function (root, factory) {
  const isNode = typeof module === "object" && module.exports;
  const api = factory(isNode ? require("./viewer-data.js") : root.SizeViewerData);
  if (isNode) module.exports = api;
  else root.SizeViewerRules = api;
})(typeof self !== "undefined" ? self : this, function ({ cleanField, escapeHtml }) {
  // 规则索引：国别 → 尺码 → 规则行、国别 → 规则ID → 规则行、国别 → 余量长容差、店铺 → 发货尺码 → [匹配尺码]
  function createRuleIndex({ sourceGroup }) {
    const sizeRuleIndexes = new Map();
    const sizeRuleTolerances = new Map();
    // 全量表 规则ID → 该国别规则表中的行（A0 规则表末列）；只在全量数据与规则来自同一 A0 版本时用于精确解释（版本由页面判断）
    const sizeRuleIdIndexes = new Map();
    const storeShippingSizes = new Map();
    const candidateGroups = new Map();
    const lengthFamilies = new Map();
    const conditionFields = ["分类", "尺码池", "模式", "版本", "CAB", "车型白名单", "插片指数上限", "插片指数下限"];
    const groupKey = (region, row) => JSON.stringify([region, ...conditionFields.map(key => cleanField(row[key]))]);
    // 同尺码系列的插片指数阈值可随档位变化，不能据此拆断长度档位。
    const lengthFamilyKey = (region, row) => JSON.stringify([region, ...conditionFields.slice(0, -2).map(key => cleanField(row[key]))]);
    const lengthUpper = (region, row) => numeric(row[region === "RU" ? "长_mm" : "长上限"]);

    function load(rules, groups) {
      candidateGroups.clear();
      lengthFamilies.clear();
      sizeRuleIndexes.clear();
      sizeRuleTolerances.clear();
      storeShippingSizes.clear();
      sizeRuleIdIndexes.clear();
      Object.entries(rules?.regions || {}).forEach(([region, payload]) => {
        const keyField = (payload.headers || [])[0];
        const index = new Map();
        const byId = new Map();
        (payload.rows || []).forEach((row) => {
          const key = cleanField(row[keyField]).toUpperCase();
          if (key && !index.has(key)) index.set(key, row);
          const id = cleanField(row["规则ID"]);
          if (id && !byId.has(id)) byId.set(id, row);
          const group = groupKey(region.toUpperCase(), row);
          if (!candidateGroups.has(group)) candidateGroups.set(group, []);
          candidateGroups.get(group).push(row);
          const family = lengthFamilyKey(region.toUpperCase(), row);
          const upper = lengthUpper(region.toUpperCase(), row);
          if (upper > 0) {
            if (!lengthFamilies.has(family)) lengthFamilies.set(family, new Set());
            lengthFamilies.get(family).add(upper);
          }
        });
        sizeRuleIndexes.set(region.toUpperCase(), index);
        sizeRuleIdIndexes.set(region.toUpperCase(), byId);
        sizeRuleTolerances.set(region.toUpperCase(), payload.length_tolerance);
      });
      Object.entries(groups?.stores || {}).forEach(([store, rows]) => {
        const shipping = new Map();
        (rows || []).forEach((row) => {
          const shipSize = cleanField(row["发货尺码"]).toUpperCase();
          const matchSize = cleanField(row["匹配尺码"]);
          if (shipSize && matchSize) shipping.set(shipSize, [...(shipping.get(shipSize) || []), matchSize]);
        });
        storeShippingSizes.set(store.toUpperCase(), shipping);
      });
    }

    function scope(sourceName) {
      const store = cleanField(sourceName).toUpperCase();
      const isStore = storeShippingSizes.has(store);
      const group = cleanField(sourceGroup(sourceName)).toUpperCase();
      const region = sizeRuleIndexes.has(group) ? group : (isStore ? "US" : "");
      return { region, store: isStore ? store : "", index: sizeRuleIndexes.get(region) };
    }

    function ruleFor(value, sourceName) {
      const ruleScope = scope(sourceName);
      const key = cleanField(value).toUpperCase();
      if (!ruleScope.index || !key) return null;
      // 店铺列表的 SIZE 是发货尺码：多个匹配尺码可发同一个发货尺码，逐个列出对应规则
      const matchSizes = ruleScope.store ? (storeShippingSizes.get(ruleScope.store).get(key) || []) : [key];
      const rows = matchSizes.map((size) => ruleScope.index.get(cleanField(size).toUpperCase())).filter(Boolean);
      if (!rows.length) return null;
      return { ...ruleScope, size: cleanField(value), matchSizes, rows, tolerance: sizeRuleTolerances.get(ruleScope.region) };
    }

    // 记录的 规则ID（命中规则）；版本一致性由调用方先判断
    function exactForRecord(record, sourceName) {
      const ruleId = cleanField(record?.values?.["规则ID"]);
      if (!ruleId) return null;
      const ruleScope = scope(sourceName);
      const row = sizeRuleIdIndexes.get(ruleScope.region)?.get(ruleId);
      if (!row) return null;
      const matchSize = cleanField(record.values["匹配尺码"]) || (ruleScope.store ? "" : cleanField(record.values["SIZE"] || record.size));
      return { ruleId, row, region: ruleScope.region, store: ruleScope.store, matchSize, tolerance: sizeRuleTolerances.get(ruleScope.region) };
    }

    function lengthPredecessor({ region, row }) {
      const upper = lengthUpper(region, row);
      const family = lengthFamilies.get(lengthFamilyKey(region, row));
      return Math.max(0, ...Array.from(family || []).filter(limit => limit < upper)) || null;
    }

    // SIZE 单元格悬停：带 规则ID 时只显示命中的那一条，查不到退回按尺码列出
    function exactFor(ruleId, sourceName, size, matchSize) {
      const ruleScope = scope(sourceName);
      const row = sizeRuleIdIndexes.get(ruleScope.region)?.get(cleanField(ruleId));
      if (!row) return ruleFor(size, sourceName);
      return { ...ruleScope, exact: true, ruleId: cleanField(ruleId), size: cleanField(size), matchSizes: [cleanField(matchSize) || cleanField(size)], rows: [row], tolerance: sizeRuleTolerances.get(ruleScope.region) };
    }

    function neighbors(record, sourceName, versionsConsistent = true) {
      const values = record?.values || {};
      const length = numeric(values["L-MM"]);
      const currentSize = cleanField(values.SIZE || record?.size);
      const result = { length, currentSize, bands: [], reason: "" };
      if (!(length > 0)) return { ...result, reason: "缺少车长" };
      if (!versionsConsistent) return { ...result, reason: "尺码规则版本不一致" };
      let exact = exactForRecord(record, sourceName);
      if (!exact && !cleanField(values["规则ID"])) {
        const fallback = ruleFor(currentSize, sourceName);
        if (fallback?.rows.length === 1) {
          const row = fallback.rows[0];
          const names = ["尺码", "亚马逊尺码", "内部尺码"];
          const matches = [...(sizeRuleIdIndexes.get(fallback.region)?.values() || [])].filter(candidate => names.some(key => row[key] && candidate[key] === row[key]));
          if (matches.length === 1) exact = { ...fallback, row };
        }
      }
      if (!exact) return { ...result, reason: "无法唯一确定适用规则" };
      const currentUpper = numeric(exact.row[exact.region === "RU" ? "长_mm" : "长上限"]);
      const currentTolerance = numeric(exact.row["余量长上限_mm"]) ?? numeric(exact.tolerance);
      if (currentUpper > 0 && currentTolerance > 0) result.currentBand = { upper: currentUpper, lower: Math.max(0,currentUpper-currentTolerance), size: cleanField(exact.row["尺码"] || exact.row["亚马逊尺码"] || exact.row["内部尺码"]), delta: currentUpper-length };
      const rows = candidateGroups.get(groupKey(exact.region, exact.row)) || [];
      const byUpper = new Map();
      for (const row of rows) {
        if (exact.region === "RU" && [ ["宽_mm", "W-MM"], ["高_mm", "H-MM"] ].some(([limit, field]) =>
          !(numeric(values[field]) > 0) || numeric(values[field]) > numeric(row[limit]))) continue;
        const upper = numeric(row[exact.region === "RU" ? "长_mm" : "长上限"]);
        const tolerance = numeric(row["余量长上限_mm"]) ?? numeric(exact.tolerance);
        if (!(upper > 0) || !(tolerance > 0)) continue;
        const size = cleanField(row["尺码"] || row["亚马逊尺码"] || row["内部尺码"]);
        if (!byUpper.has(upper)) byUpper.set(upper, { upper, lower: Math.max(0, upper - tolerance), names: [] });
        const band = byUpper.get(upper);
        band.lower = Math.max(band.lower, Math.max(0, upper - tolerance));
        if (!band.names.includes(size)) band.names.push(size);
      }
      const sorted = [...byUpper.values()].sort((a, b) => a.upper - b.upper);
      const nearest = sorted.findIndex(band => band.upper >= length);
      const center = nearest < 0 ? sorted.length - 1 : nearest;
      const start = Math.max(0, Math.min(center - 2, sorted.length - 5));
      result.comparisonBands = sorted.slice(start, start + 5).map(band => ({ ...band, size: band.names.join(" / "), delta: band.upper - length }));
      const left = sorted.filter(band => band.upper < length).at(-1);
      const right = sorted.find(band => band.upper >= length);
      result.bands = [left, right].filter(Boolean).map(band => ({ ...band, size: band.names.join(" / "), delta: band.upper - length }));
      if (!result.bands.length) result.reason = "暂无可比较的尺码";
      return result;
    }

    return { load, scope, ruleFor, exactForRecord, exactFor, neighbors, lengthPredecessor };
  }

  function numeric(value) {
    if (value === null || value === undefined || !String(value).trim()) return null;
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  const FITMENT_ZONES = [
    { kind: "over", start: 0, end: 50, color: "#778496", label: "灰度 · 超上限 0–5cm" },
    { kind: "green", start: -200, end: 0, color: "#258260", label: "最佳 · 上限内 20cm" },
    { kind: "orange", start: -400, end: -200, color: "#c8751c", label: "警戒 · 余量 20–40cm" }
  ];
  const FITMENT_BAND_OPACITY = 0.24;

  function fitmentSegments(upper, { previousUpper } = {}) {
    if (!Number.isFinite(upper) || upper <= 0) return [];
    return FITMENT_ZONES.map(({ kind, start, end, color }) => {
      let from = Math.max(0, upper + start);
      if (previousUpper !== undefined) {
        if (kind === "orange") from = previousUpper ?? upper;
        if (kind === "green" && previousUpper !== null) from = Math.max(from, previousUpper);
      }
      return { kind, color, from, to: upper + end };
    }).filter(({ from, to }) => to > from).reverse();
  }

  function fitmentLegendMarkup({ adjacent = false } = {}) {
    return `<div class="scatter-band-legend">${FITMENT_ZONES.map(zone =>
      `<span><i style="background:${zone.color}"></i>${adjacent && zone.kind === "orange" ? "警戒 · 小一号长上限至最佳区" : zone.label}</span>`).join("")}</div>`;
  }

  function fitmentAxis(fit, bands, format, compact = false) {
    const low = Math.min(fit.length - 30, ...bands.flatMap(band => fitmentSegments(band.upper).map(segment => segment.from)));
    const high = Math.max(fit.length + 30, ...bands.map(band => band.upper + 50));
    const x = value => 8 + (value - low) / (high - low) * 204;
    const height = compact ? 21 : bands.length * 26 + 17;
    const markup = bands.map((band, index) => {
      const y = compact ? 3 : 16 + index * 26;
      const segments = fitmentSegments(band.upper);
      return (compact ? "" : `<text x="8" y="${y - 3}" font-size="10">${escapeHtml(band.size)} · 上限 ${format.measurement(band.upper)}</text>`) + segments.map(({ from, to, color }) => `<rect x="${x(from)}" y="${y}" width="${x(to)-x(from)}" height="7" fill="${color}"/>`).join("");
    }).join("");
    return `<svg viewBox="0 0 220 ${height}" role="img" aria-label="${compact ? "当前自动匹配尺码数轴" : "相邻尺码数轴"}">${markup}<path d="M ${x(fit.length)} ${compact ? 0 : 14} V ${compact ? 12 : height-18}" stroke="#263b50" stroke-width="2"/><text x="8" y="${height-1}" font-size="9">${format.measurement(low)}</text><text x="212" y="${height-1}" text-anchor="end" font-size="9">${format.measurement(high)} ${format.unit}</text></svg>`;
  }

  function fitmentMarkup(fit, format) {
    const label = escapeHtml(fit.currentSize || "未匹配");
    if (!fit.currentBand) return `<div class="fitment-mini"><button type="button" class="fitment-trigger fitment-unavailable" aria-label="查看尺码匹配详情"><b>${label}</b><small>${escapeHtml(fit.reason || "暂无匹配规则")}</small></button></div>`;
    const describe = band => `${band.size} 上限 ${format.measurement(band.upper)} ${format.unit}，${band.delta >= 0 ? "余量" : "超出"} ${format.measurement(Math.abs(band.delta))} ${format.unit}`;
    const delta = fit.currentBand.delta;
    return `<div class="fitment-mini"><button type="button" class="fitment-trigger" aria-label="${label}；${escapeHtml(describe(fit.currentBand))}；查看多尺码对比"><span><b>${label}</b><small>${delta >= 0 ? "余量" : "超出"} ${format.measurement(Math.abs(delta))} ${format.unit} ↗</small></span>${fitmentAxis(fit,[fit.currentBand],format,true)}</button></div>`;
  }

  function bindFitment(root, onOpen) {
    root.querySelectorAll(".fitment-trigger").forEach(button => {
      button.onclick = event => { event.stopPropagation(); onOpen?.(button); };
    });
  }

  function fitmentDetailMarkup(fit, format) {
    if (!fit.currentBand) return `<p class="detail-empty">${escapeHtml(fit.reason || "暂无匹配规则")}，暂不能绘制尺码对比。</p>`;
    const bands = [fit.currentBand, ...(fit.comparisonBands || fit.bands).filter(b => b.upper !== fit.currentBand.upper)].sort((a,b) => a.upper-b.upper);
    const low = Math.min(fit.length - 100, ...bands.map(b => b.upper - 400));
    const high = Math.max(fit.length + 100, ...bands.map(b => b.upper + 50));
    const x = value => 24 + (value-low)/(high-low)*592;
    const height = bands.length*82+52;
    const f = value => escapeHtml(format.measurement(value));
    const ticks = Array.from({length:5}, (_,i) => low+(high-low)*i/4);
    const rows = bands.map((band,i) => {
      const y = 50+i*82, current = band.upper === fit.currentBand.upper;
      return `<g class="fitment-detail-band" data-upper="${band.upper}"><text x="24" y="${y-16}" font-size="13" font-weight="${current ? 700 : 500}">${escapeHtml(band.size)}${current ? " · 当前匹配" : ""}</text><text x="616" y="${y-16}" text-anchor="end" font-size="11">上限 ${f(band.upper)} · ${band.delta>=0 ? "余量" : "超出"} ${f(Math.abs(band.delta))} ${escapeHtml(format.unit)}</text>${fitmentSegments(band.upper).map(s=>`<rect x="${x(s.from)}" y="${y}" width="${x(s.to)-x(s.from)}" height="12" rx="2" fill="${s.color}" opacity=".55"/>`).join("")}<path d="M ${x(band.upper)} ${y-4} v 20" stroke="currentColor"/><circle class="fitment-match-point" cx="${x(fit.length)}" cy="${y+6}" r="5" fill="#08654f" stroke="white" stroke-width="2"/></g>`;
    }).join("");
    return `<div class="fitment-detail-chart"><svg viewBox="0 0 640 ${height}" role="img" aria-label="多尺码统一车长数轴与匹配点对比"><g fill="currentColor">${ticks.map(v=>`<path d="M ${x(v)} 20 V ${height-24}" stroke="currentColor" opacity=".08"/><text x="${x(v)}" y="${height-7}" text-anchor="middle" font-size="10">${f(v)}</text>`).join("")}<path d="M ${x(fit.length)} 20 V ${height-24}" stroke="#08654f" stroke-dasharray="3 4" opacity=".55"/>${rows}</g></svg></div><div class="fitment-detail-legend">${FITMENT_ZONES.map(z=>`<span><i style="background:${z.color}"></i>${z.label}</span>`).join("")}<span><i class="point"></i>车辆长度 ${f(fit.length)} ${escapeHtml(format.unit)}</span></div><p class="detail-note">各尺码使用同一车长刻度，圆点为当前车辆。色带表示长度关系，相邻尺码仅用于对比，最终匹配以发布数据为准。</p>`;
  }

  function ruleMarkup(rule, format) {
    const sections = rule.rows.map((row, index) => {
      const matchSize = cleanField(rule.matchSizes[index]);
      const via = rule.store && (rule.exact || rule.rows.length > 1 || matchSize.toUpperCase() !== rule.size.toUpperCase())
        ? `<div class="size-reference-meta">匹配尺码 ${escapeHtml(matchSize)} → 发货 ${escapeHtml(rule.size)}</div>`
        : "";
      return `${via}${rule.region === "RU" ? ruMarkup(row, rule, format) : lengthMarkup(row, rule, format)}`;
    }).join('<hr class="size-reference-divider">');
    const scope = rule.store ? `${rule.region} · 店铺 ${rule.store}` : rule.region;
    const heading = rule.exact ? `命中规则 ${rule.ruleId}` : "尺码规则";
    return `
      <div class="size-reference-title">${escapeHtml(rule.size)}<small>${escapeHtml(scope)} ${escapeHtml(heading)}</small></div>
      ${sections}
    `;
  }

  // US/EU：车长 ≤ 长上限 且 长上限 − 车长 ≤ 余量长容差，适配车长即 [长上限 − 容差, 长上限]
  function lengthMarkup(row, rule, format) {
    const meta = rule.region === "EU"
      ? [cleanField(row["模式"]), cleanField(row["分类"]), cleanField(row["版本"]) && `版本 ${cleanField(row["版本"])}`]
      : [cleanField(row["分类"]), cleanField(row["尺码池"]) && `尺码池 ${cleanField(row["尺码池"])}`];
    const lengthMax = Number(cleanField(row["长上限"]) || NaN);
    const tolerance = Number(rule.tolerance ?? NaN);
    const hasRange = Number.isFinite(lengthMax) && Number.isFinite(tolerance) && tolerance > 0;
    const items = [
      ["适配车长", hasRange ? rangeDisplay(lengthMax - tolerance, lengthMax, format) : ""],
      ["长上限", Number.isFinite(lengthMax) ? dimensionDisplay(lengthMax, format) : ""],
      ["余量容差", hasRange ? `≤ ${dimensionDisplay(tolerance, format)}` : ""],
      ["插片指数", insertDisplay(row["插片指数上限"], row["插片指数下限"])],
      ["白名单", cleanField(row["车型白名单"])],
      ["备注", cleanField(row["备注"])]
    ];
    return `${metaMarkup(meta)}${itemsMarkup(items)}`;
  }

  // RU：车型长宽高均不超过规则长宽高，且 长_mm − 车长 ≤ 余量长上限_mm（缺省用报告的余量长容差）
  function ruMarkup(row, rule, format) {
    const meta = [
      cleanField(row["分类"]),
      cleanField(row["OZON尺码"]) && `OZON ${cleanField(row["OZON尺码"])}`,
      cleanField(row["发货尺码"]) && `发货 ${cleanField(row["发货尺码"])}`
    ];
    const lengthMax = Number(cleanField(row["长_mm"]) || NaN);
    const rowTolerance = Number(cleanField(row["余量长上限_mm"]) || NaN);
    const tolerance = Number.isFinite(rowTolerance) ? rowTolerance : Number(rule.tolerance ?? NaN);
    const hasRange = Number.isFinite(lengthMax) && Number.isFinite(tolerance) && tolerance > 0;
    const items = [
      ["适配车长", hasRange ? rangeDisplay(lengthMax - tolerance, lengthMax, format) : ""],
      ["余量容差", hasRange ? `≤ ${dimensionDisplay(tolerance, format)}` : ""]
    ];
    return `${metaMarkup(meta)}
      <div class="size-reference-dims">
        ${dimensionMarkup("长上限", row["长_mm"], format)}
        ${dimensionMarkup("宽上限", row["宽_mm"], format)}
        ${dimensionMarkup("高上限", row["高_mm"], format)}
      </div>
      ${itemsMarkup(items)}`;
  }

  function metaMarkup(parts) {
    const text = parts.filter(Boolean).join(" · ");
    return text ? `<div class="size-reference-common">${escapeHtml(text)}</div>` : "";
  }

  function itemsMarkup(items) {
    const visible = items.filter(([, value]) => value);
    return visible.length
      ? `<dl class="size-reference-rows">${visible.map(([label, value]) => `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`).join("")}</dl>`
      : "";
  }

  function rangeDisplay(low, high, format) {
    return `${format.measurement(Math.max(0, low))} – ${format.measurement(high)} ${format.unit}`;
  }

  // 插片指数上限 999 表示不限
  function insertDisplay(upper, lower) {
    const max = Number(cleanField(upper) || NaN);
    const min = cleanField(lower);
    const parts = [];
    if (min) parts.push(`> ${min}`);
    if (Number.isFinite(max) && max < 999) parts.push(`≤ ${max}`);
    return parts.join("，");
  }

  function dimensionMarkup(label, value, format) {
    const display = dimensionDisplay(value, format);
    return `<span><em>${escapeHtml(label)}</em><strong>${escapeHtml(display || "-")}</strong></span>`;
  }

  function dimensionDisplay(value, format) {
    const number = Number(value);
    if (!Number.isFinite(number)) {
      return cleanField(value);
    }
    return `${format.measurement(number)} ${format.unit}`;
  }

  return { createRuleIndex, FITMENT_ZONES, FITMENT_BAND_OPACITY, fitmentSegments, fitmentLegendMarkup, fitmentMarkup, fitmentDetailMarkup, bindFitment, ruleMarkup, insertDisplay, dimensionMarkup, dimensionDisplay };
});
