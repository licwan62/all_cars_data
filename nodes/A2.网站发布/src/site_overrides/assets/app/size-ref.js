(function () {
  const app = document.getElementById("app");
  const { esc, shell, bindSidebar, sourceText, getJson } = window.SiteCommon || {};
  if (!app || !shell) return;

  const regions = { US: "美国", EU: "欧洲", RU: "俄罗斯" };
  const defaultStores = ["HNT", "TM", "TM_拆分"];
  const fields = { 长_mm: "长上限", 宽_mm: "宽上限", 高_mm: "高上限", 余量长上限_mm: "余量长上限" };
  const number = new Intl.NumberFormat("zh-CN");
  const state = { rules: null, groups: null, loading: true };
  const storeKeys = () => Object.keys(state.groups?.stores || {}).length ? Object.keys(state.groups.stores) : defaultStores;
  const storeName = (key) => key.replaceAll("_", " ");
  const regionData = (key) => state.rules?.regions?.[key];
  const text = (value) => String(value ?? "").trim();
  const mm = (value) => text(value) ? `${number.format(Number(value))} mm` : "—";
  const href = (key, query = "") => `size-ref.html${query ? "?" + new URLSearchParams({ q: query }) : ""}#${encodeURIComponent(key)}`;

  function readLocation() {
    let key;
    try { key = decodeURIComponent(location.hash.slice(1)).toUpperCase(); } catch (_) { key = ""; }
    const choices = [...Object.keys(regions), ...storeKeys()];
    state.scope = choices.find((choice) => choice.toUpperCase() === key)
      || (app.hasAttribute("data-default-store") || key === "STORES" ? storeKeys()[0] : "US");
    state.query = new URLSearchParams(location.search).get("q") || "";
    state.category = "";
    state.order = "";
  }

  function categories(row) {
    const values = text(row["分类"]).split("|").map(text).filter(Boolean);
    return values.length ? values : [row["模式"] === "定制" ? "专车定制" : "未分类"];
  }

  function ruleItems(key) {
    return (regionData(key)?.rows || []).map((row, index) => ({
      index, row, size: text(row[key === "RU" ? "亚马逊尺码" : "尺码"]), categories: categories(row),
      length: Number(row[key === "RU" ? "长_mm" : "长上限"]) || 0
    }));
  }

  function storeItems(key) {
    const sameVersion = state.rules?.source?.version && state.rules.source.version === state.groups?.source?.version;
    const rulesBySize = new Map((sameVersion ? ruleItems("US") : []).map((rule) => [rule.size, rule]));
    const byShipment = new Map();
    for (const row of state.groups?.stores?.[key] || []) {
      const size = text(row["发货尺码"]);
      if (!byShipment.has(size)) {
        const rule = rulesBySize.get(size);
        byShipment.set(size, { size, rule, matches: [], categories: rule?.categories || ["未分类"], length: rule?.length || 0 });
      }
      byShipment.get(size).matches.push(text(row["匹配尺码"]));
    }
    return [...byShipment.values()];
  }

  function scopeLink(key, detail) {
    const current = key === state.scope;
    return `<a href="${href(key)}" class="ref-scope${current ? " is-current" : ""}"${current ? ' aria-current="page"' : ""}>
      <strong>${esc(storeName(key))}</strong><span>${esc(detail)}</span></a>`;
  }

  function render() {
    const key = state.scope;
    const isStore = !regions[key];
    const dataset = isStore ? state.groups?.stores?.[key] : regionData(key);
    const items = isStore ? storeItems(key) : ruleItems(key);
    const categoryOptions = [...new Set(items.flatMap((item) => item.categories))];
    const origin = isStore ? state.groups?.source : state.rules?.source;
    const sourceFile = isStore ? "" : dataset?.file;
    const message = state.loading ? "正在读取尺码资料…" : "暂时无法读取该入口的数据。";
    const isRu = key === "RU";
    app.innerHTML = shell("ref", `
      <section class="reference-workspace" aria-labelledby="ref-title">
        <header class="ref-heading">
          <div><div class="ref-kicker">车辆尺码资料库</div><h1 id="ref-title">尺码参考</h1>
          <p>查各地区的尺码条件，或按店铺查匹配尺码实际从哪个货架发货。</p></div>
          <a class="ref-match" href="size-match.html">去尺码配对 <span aria-hidden="true">↗</span></a>
        </header>
        <nav class="ref-scopes" aria-label="尺码资料入口">
          <div><h2>地区规则</h2><div class="ref-scope-grid">
            ${Object.entries(regions).map(([region, name]) => scopeLink(region, name)).join("")}
          </div></div>
          <div><h2>US 店铺分组</h2><div class="ref-scope-grid">
            ${storeKeys().map((store) => {
              const mapping = state.groups?.stores?.[store];
              return scopeLink(store, mapping ? `${new Set(mapping.map(row => row["发货尺码"])).size} 个发货尺码` : "发货尺码");
            }).join("")}
          </div></div>
        </nav>
        ${dataset ? `
          <section class="ref-results" aria-labelledby="ref-results-title">
            <div class="ref-section-heading"><div>
              <h2 id="ref-results-title">${esc(storeName(key))} ${isStore ? "发货尺码" : "尺码规则"}</h2>
              <p>${isStore ? "每张卡片对应一个发货尺码，卡内列出归入它的匹配尺码。" :
                isRu ? "以亚马逊尺码为主，卡片同时标出 OZON 与发货尺码。长度条按本地区最大长度等比显示。" :
                "长度条按本地区最大长度等比显示。打开卡片可查插片指数、白名单等规则条件。"}</p>
            </div><p class="ref-count" role="status"></p></div>
            <div class="ref-filters">
              <label class="ref-search"><span>搜索</span><input type="search" data-ref-query value="${esc(state.query)}"
                placeholder="${isStore ? "匹配尺码、发货尺码…" : "尺码、分类、车型白名单…"}"></label>
              <label><span>车型分类</span><select data-ref-category>
                <option value="">全部分类</option>${categoryOptions.map((name) => `<option value="${esc(name)}"${name === state.category ? " selected" : ""}>${esc(name)}</option>`).join("")}
              </select></label>
              <label><span>排序</span><select data-ref-order>
                <option value="">发布顺序</option>
                ${(isStore ? [["count", "匹配数从多到少"]] : [["short", "长上限从小到大"], ["long", "长上限从大到小"]])
                  .map(([value, label]) => `<option value="${value}"${value === state.order ? " selected" : ""}>${label}</option>`).join("")}
              </select></label>
              <button type="button" class="ref-reset" data-ref-reset>清除筛选</button>
            </div>
            <div class="ref-card-grid" data-ref-cards></div>
          </section>
          ${origin ? `<footer class="ref-source">${esc(sourceText(origin))}${sourceFile ? ` · ${esc(sourceFile)}` : ""}</footer>` : ""}
        ` : `<p class="ref-empty" role="status">${message}</p>`}
        <dialog class="ref-dialog" aria-labelledby="ref-dialog-title"></dialog>
      </section>`, "", { outline: false });
    bindSidebar(app, render);
    if (!dataset) return;

    const query = app.querySelector("[data-ref-query]");
    const category = app.querySelector("[data-ref-category]");
    const order = app.querySelector("[data-ref-order]");
    query.oninput = () => { state.query = query.value; update(items, isStore); };
    category.onchange = () => { state.category = category.value; update(items, isStore); };
    order.onchange = () => { state.order = order.value; update(items, isStore); };
    app.querySelector("[data-ref-reset]").onclick = () => {
      state.query = query.value = "";
      state.category = category.value = "";
      state.order = order.value = "";
      update(items, isStore);
      query.focus();
    };
    update(items, isStore);
  }

  function update(items, isStore) {
    const tokens = state.query.toLowerCase().split(/\s+/).filter(Boolean);
    const filtered = items.filter((item) => {
      if (state.category && !item.categories.includes(state.category)) return false;
      const values = isStore ? [item.size, ...item.matches, ...Object.values(item.rule?.row || {})] : Object.values(item.row);
      const searchable = [...values, ...item.categories].join(" ").toLowerCase();
      return tokens.every((token) => searchable.includes(token));
    });
    if (state.order === "count") filtered.sort((a, b) => b.matches.length - a.matches.length);
    if (state.order === "short") filtered.sort((a, b) => a.length - b.length);
    if (state.order === "long") filtered.sort((a, b) => b.length - a.length);
    const scale = Math.max(1, ...items.map((item) => item.length));
    app.querySelector(".ref-count").textContent = `${filtered.length} / ${items.length} ${isStore ? "个发货尺码" : "条规则"}`;
    app.querySelector("[data-ref-cards]").innerHTML = filtered.length ? filtered.map((item) =>
      isStore ? shipmentCard(item) : ruleCard(item, state.scope, scale)).join("") :
      '<p class="ref-empty">未找到匹配资料。可以清除筛选后重试。</p>';
  }

  function ruleCard(item, region, scale) {
    const { row, size, index, length } = item;
    return `<article class="ref-card ref-rule">
      <button type="button" data-ref-rule="${region}:${index}" aria-label="查看 ${esc(size)} 的规则${row["规则ID"] ? ` ${esc(row["规则ID"])}` : ""}">
        <span class="ref-card-top"><strong>${esc(size || "—")}</strong>
          <span class="ref-tag${row["模式"] === "定制" ? " is-custom" : ""}">${esc(item.categories.join(" / "))}</span></span>
        <span class="ref-card-meta">${region === "RU"
          ? `OZON ${esc(text(row["OZON尺码"]) || "—")} · 发货 ${esc(text(row["发货尺码"]) || "—")}`
          : esc([row["尺码池"] && `尺码池 ${row["尺码池"]}`, row["模式"], row["版本"]].filter(Boolean).join(" · "))}</span>
        <span class="ref-length"><span>长上限</span><strong>${esc(length ? mm(length) : "—")}</strong></span>
        <span class="ref-meter" aria-hidden="true"><span style="width:${length / scale * 100}%"></span></span>
        ${region === "RU" ? `<span class="ref-card-meta">宽 ${esc(mm(row["宽_mm"]))} · 高 ${esc(mm(row["高_mm"]))}</span>` :
          row["车型白名单"] ? `<span class="ref-card-meta">${esc(row["车型白名单"])}</span>` : ""}
        <span class="ref-card-action">查看规则 <span aria-hidden="true">→</span></span>
      </button>
    </article>`;
  }

  function shipmentCard(item) {
    return `<article class="ref-card ref-shipment">
      <div class="ref-card-top"><div><span class="ref-card-meta">发货尺码</span><h3>${esc(item.size || "—")}</h3></div>
        <span class="ref-tag">${item.matches.length} 个匹配尺码</span></div>
      <p class="ref-card-meta">${item.rule ? `${esc(item.categories.join(" / "))} · 长上限 ${esc(mm(item.length))}` : "暂无同版本 US 发货尺码规则"}</p>
      <div class="ref-matches"><span>匹配尺码</span><ul>
        ${item.matches.map((size) => `<li>${esc(size || "—")}</li>`).join("")}
      </ul></div>
      ${item.rule ? `<button type="button" class="ref-card-action" data-ref-rule="US:${item.rule.index}">查看 US 发货尺码规则 <span aria-hidden="true">→</span></button>` : ""}
    </article>`;
  }

  function openRule(region, index) {
    const data = regionData(region);
    const item = ruleItems(region)[index];
    const dialog = app.querySelector(".ref-dialog");
    if (!item || !dialog) return;
    const sameVersion = state.rules?.source?.version && state.rules.source.version === state.groups?.source?.version;
    const mappings = region === "US" && sameVersion ? storeKeys().flatMap((store) =>
      (state.groups?.stores?.[store] || []).filter(row => text(row["匹配尺码"]) === item.size)
        .map(row => `<a href="${esc(href(store, item.size))}">${esc(storeName(store))} · ${esc(row["发货尺码"])} <span aria-hidden="true">↗</span></a>`)) : [];
    dialog.innerHTML = `<div class="ref-dialog-content">
      <div class="ref-dialog-heading"><div><div class="ref-kicker">${region} 尺码规则</div>
        <h2 id="ref-dialog-title">${esc(item.size || "—")}</h2></div>
        <form method="dialog"><button type="submit" autofocus>关闭</button></form></div>
      <dl>${data.headers.map((field) => {
        const raw = text(item.row[field]);
        let value = raw || "—";
        if (raw && (fields[field] || field === "长上限")) value = mm(raw);
        if (field === "插片指数上限" && raw === "999") value = "不限（999）";
        return `<div><dt>${esc(fields[field] || field)}</dt><dd>${esc(value)}</dd></div>`;
      }).join("")}</dl>
      ${mappings.length ? `<div class="ref-related"><h3>该匹配尺码的店铺发货去向</h3>${mappings.join("")}</div>` : ""}
    </div>`;
    dialog.showModal();
  }

  app.addEventListener("click", (event) => {
    const button = event.target.closest("[data-ref-rule]");
    if (button) {
      const [region, index] = button.dataset.refRule.split(":");
      openRule(region, Number(index));
    }
    if (event.target.matches(".ref-dialog")) event.target.close();
  });
  window.addEventListener("hashchange", () => {
    const focusScope = document.activeElement?.matches(".ref-scope");
    readLocation();
    render();
    if (focusScope) app.querySelector(".ref-scope.is-current")?.focus({ preventScroll: true });
  });
  readLocation();
  render();
  Promise.allSettled([getJson("data/generated/size-rules.json"), getJson("data/generated/store-groups.json")])
    .then(([rules, groups]) => {
      state.rules = rules.status === "fulfilled" ? rules.value : null;
      state.groups = groups.status === "fulfilled" ? groups.value : null;
      state.loading = false;
      readLocation();
      render();
    });
})();
