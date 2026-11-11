// Derived views only: never infer annual sales from interval potential or size counts.
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ModelDashboard = api;
})(typeof window === "undefined" ? globalThis : window, function () {
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const count = value => Number(value).toLocaleString("zh-CN");
  function summarize(records, zoom) {
    const rows = [...new Map(records.filter(r => !zoom || r.intervals.some(i => i.startYear <= zoom.endValue && i.endYear >= zoom.startValue)).map(r => [r.recordKey, r])).values()];
    const sizes = new Map(), years = new Set();
    rows.forEach(r => {
      const size = r.sizeValue || "未记录";
      sizes.set(size, (sizes.get(size) || 0) + 1);
      r.intervals.forEach(i => {
        for (let year = i.startYear; year <= i.endYear; year++) if (!zoom || (year >= Math.ceil(zoom.startValue) && year <= Math.floor(zoom.endValue))) years.add(year);
      });
    });
    const potentials = rows.filter(r => Number.isFinite(r.marketPotential));
    return { rows, types: [...new Set(rows.map(r=>r.type).filter(Boolean))], cabs: [...new Set(rows.map(r=>r.cab).filter(Boolean))], sizes: [...sizes].sort((a,b) => b[1]-a[1] || a[0].localeCompare(b[0])), years: [...years].sort((a,b)=>a-b), configurations: new Set(rows.map(r=>r.configurationKey)).size,
      potential: potentials.length ? potentials.reduce((sum,r)=>sum+r.marketPotential,0) : null, missingPotential: rows.length-potentials.length,
      matched: rows.filter(r=>r.matchStatus === "matched").length,
      dimensions: ["lengthMm","widthMm","heightMm"].map(key => { const v=rows.map(r=>r[key]).filter(Number.isFinite); return v.length ? [Math.min(...v),Math.max(...v)] : null; }) };
  }
  function metricsMarkup(s, format) {
    const range = s.years.length ? `${s.years[0]}–${s.years.at(-1)}` : "—";
    const cards = [["年份覆盖",range,`${s.years.length} 个有记录年份`],["尺寸记录",count(s.rows.length),`${s.configurations} 个可见配置`],["已匹配记录",`${s.matched} / ${s.rows.length}`,"以发布数据匹配结果为准"],["市场潜力",s.potential === null ? "—" : count(Math.round(s.potential)),`区间分数合计${s.missingPotential ? ` · 缺失 ${s.missingPotential} 条` : " · 不按年重复"}`]];
    return `<div class="dashboard-kpis">${cards.map(([label,value,note])=>`<article><span>${label}</span><strong>${value}</strong><small>${note}</small></article>`).join("")}</div><div class="dashboard-dimensions">${s.dimensions.map((range,i)=>`<span>${["车长","车宽","车高"][i]} <strong>${range ? range.map(format.measurement).join("–") : "—"}</strong> ${esc(format.unit)}</span>`).join("")}<span>车身 ${esc(s.types.join(" / ") || "未注明")}${s.cabs.length ? ` · CAB ${esc(s.cabs.join(" / "))}` : ""}</span></div>`;
  }
  function sizesMarkup(s, shipping) {
    const max = Math.max(1,...s.sizes.map(x=>x[1]));
    return `<article class="dashboard-card"><h3>${shipping ? "发货尺码" : "匹配尺码"}分布</h3><p>按唯一尺寸记录计数，不代表销量占比。</p><div class="dashboard-size-bars">${s.sizes.length ? s.sizes.map(([size,n])=>`<div class="dashboard-bar"><span>${esc(size)}</span><meter min="0" max="${max}" value="${n}" aria-label="${esc(size)}：${n} 条记录">${n}</meter><strong>${n}</strong></div>`).join("") : '<p>当前配置与年份范围没有记录。</p>'}</div></article>`;
  }
  function salesMarkup(sales, state, zoom, error) {
    const lead = '<div class="dashboard-sales">';
    if (state === "loading") return lead+'<p role="status">加载销量中…</p></div>';
    if (state === "error") return lead+`<p role="alert">${esc(error || "销量加载失败")}</p><button type="button" data-dashboard-sales-retry>重试销量</button></div>`;
    if (!sales) return lead+'<p>暂无同口径年度销量数据。</p></div>';
    const entries = [...sales.totals].filter(([year])=>!zoom || (year>=Math.ceil(zoom.startValue) && year<=Math.floor(zoom.endValue))).sort((a,b)=>a[0]-b[0]);
    if (!entries.length) return lead+'<p>当前范围没有年度销量记录。</p></div>';
    return lead+`<details><summary>查看 ${entries.length} 年的原始销量</summary><div class="dashboard-sales-table"><table><thead><tr><th>年份</th><th>预估销量（千辆）</th><th>原始销量（辆）</th></tr></thead><tbody>${entries.map(([year,r])=>`<tr><td>${year}</td><td>${r.missing ? "—" : Math.round(r.known/1000)}</td><td>${r.missing ? `已知 ${count(r.known)} · 缺失 ${r.missing} 条` : count(r.known)}</td></tr>`).join("")}</tbody></table></div></details></div>`;
  }
  return { summarize, metricsMarkup, sizesMarkup, salesMarkup };
});
