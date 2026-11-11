(function(){
  "use strict";
  const D=window.SizeEvolutionData,C=window.ModelCompareData;
  const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const number=v=>Number.isFinite(v)?v.toLocaleString("zh-CN",{maximumFractionDigits:4}):"—";
  const colors=["#2468b4","#cf5264","#188979","#9967b0","#bb7c16","#427c8f","#ab5b33","#68734a","#784e84","#50627e","#bd426e","#478443"];
  const MAX_MODELS=12;
  async function start(options){
    document.title="多车型对比 · BI";
    document.body.classList.add("model-compare-page");
    const root=document.getElementById("app"),params=new URLSearchParams(location.search);
    const state={source:options.source,kind:params.get("kind")==="pick"?"pick":"nonpick",make:"",selected:options.models||[],loaded:[],records:[],annual:null,origin:null,catalog:[],groupBy:["model","structure","model-structure"].includes(params.get("group"))?params.get("group"):"model",metric:"lengthMm",unit:["mm","cm","in"].includes(params.get("unit"))?params.get("unit"):"cm",from:null,to:null,filter:"",loadToken:0,catalogToken:0,busy:false};
    if(state.selected.length){state.kind=state.selected[0].kind;state.make=state.selected[0].make;}
    const charts=new Map(),colorKeys=new Map();
    let scatterView=null;
    const color=key=>{if(!colorKeys.has(key))colorKeys.set(key,colorKeys.size);return colors[colorKeys.get(key)%colors.length];};
    const key=m=>JSON.stringify([m.kind,m.make,m.model]);
    const label=m=>`${m.make} ${m.model}`;
    root.innerHTML=`<main class="compare-workspace"><header class="compare-header"><div><h1>多车型对比 <small>BI</small></h1><p>尺寸区间 · 年度销量 · 市场潜力</p></div><a data-compare-back href="size-match.html">← 返回一览表</a></header>
      <details class="compare-selection" open aria-label="选择对比车型"><summary>选择对比车型 <span data-compare-count></span></summary><div class="compare-toolbar"><label>来源<select data-compare-source>${options.sources.map(s=>`<option value="${esc(s.name)}">${esc(s.label||s.name)}</option>`).join("")}</select></label><label>类别<select data-compare-kind><option value="nonpick">非皮卡</option><option value="pick">皮卡</option></select></label><label>品牌<select data-compare-make aria-label="选择品牌"><option value="">选择品牌</option></select></label><label>车型搜索<input type="search" data-compare-search placeholder="在当前品牌中搜索" aria-label="搜索对比车型"></label></div><div data-compare-catalog-status role="status"></div><div class="compare-model-options" data-compare-models></div>
      <div class="compare-selected" data-compare-selected></div><div class="compare-actions"><button type="button" class="evo-primary" data-compare-run>更新对比</button><button type="button" data-compare-clear>清空选择</button><span data-compare-selection-note role="status"></span></div></details>
      <p class="compare-status" data-compare-status role="status">选择至少两个车型开始比较，也可先查看一个车型。</p>
      <section data-compare-results hidden><div class="compare-toolbar compare-analysis-controls"><label>汇总方式<select data-compare-group><option value="model">按车型</option><option value="structure">按结构（皮卡 CAB/BED）</option><option value="model-structure">车型 × 结构</option></select></label><label>结构筛选<select data-compare-structure><option value="">全部结构</option></select></label><label>起始年份<input type="number" data-compare-from aria-label="对比起始年份"></label><label>结束年份<input type="number" data-compare-to aria-label="对比结束年份"></label><button type="button" data-compare-years>全部年份</button><label>尺寸单位<select data-compare-unit><option value="mm">MM</option><option value="cm">CM</option><option value="in">IN</option></select></label></div>
      <div class="dashboard-kpis" data-compare-kpis></div><div class="compare-group-legend" data-compare-legend aria-label="汇总图例"></div>
      <div class="compare-chart-grid"><article class="dashboard-card compare-wide" id="scatter" data-compare-scatter></article><article class="dashboard-card"><div class="compare-card-heading"><h2>尺寸区间对比</h2><select data-compare-metric aria-label="对比尺寸"><option value="lengthMm">车长</option><option value="widthMm">车宽</option><option value="heightMm">车高</option></select></div><p>线段：最小–最大 · 圆点：中位数。每条尺寸记录计一次，不按年份或销量加权。</p><div data-compare-chart="dimensions" role="img" aria-label="各车型或结构的尺寸区间和中位数"></div></article>
      <article class="dashboard-card"><h2>市场潜力对比</h2><p>尺寸记录区间分数；窗口内相交记录只计一次，不代表年度销量或市场份额。</p><div data-compare-potential-status></div><div data-compare-chart="potential" role="img" aria-label="车型或结构市场潜力汇总"></div></article>
      <article class="dashboard-card compare-wide"><h2>年度预估销量</h2><p>单位：千辆 · 按唯一车型尺寸记录与年份去重；缺失断开，不补零。店铺来源也表示车型市场预估量，不代表店铺订单。</p><div data-compare-sales-status></div><div data-compare-chart="sales" role="img" aria-label="各车型或结构年度销量及去重合计"></div></article></div>
      <article class="dashboard-card compare-summary"><h2>汇总明细</h2><p>尺寸为最小–最大范围；销量先汇总原值再取整，悬浮可查看辆数。结构汇总只包含当前所选车型。</p><div class="compare-table-wrap"><table data-compare-table></table></div></article>
      <details class="compare-basis"><summary>统计口径与数据版本</summary><div data-compare-basis></div></details></section></main>`;
    const el=s=>root.querySelector(s);
    if(options.returnToken)el("[data-compare-back]").href=`size-match.html?restore=${encodeURIComponent(options.returnToken)}`;
    const readSelection=()=>state.selected.map(key).sort().join("|");
    const dirty=()=>readSelection()!==state.loaded.map(key).sort().join("|");
    const modelHref=m=>`model-dashboard.html?${new URLSearchParams({source:state.source,kind:m.kind,make:m.make,model:m.model,unit:state.unit})}`;
    function selectedUi(){
      el("[data-compare-count]").textContent=`已选 ${state.selected.length} 款`;
      el("[data-compare-selected]").innerHTML=state.selected.map((m,i)=>`<span><a href="${esc(modelHref(m))}">${esc(label(m))}</a><button type="button" data-compare-remove="${i}" aria-label="移除 ${esc(label(m))}">×</button></span>`).join("");
      root.querySelectorAll("[data-compare-remove]").forEach(b=>b.onclick=()=>{state.selected.splice(Number(b.dataset.compareRemove),1);selectedUi();catalogUi();});
      el("[data-compare-selection-note]").textContent=`已选 ${state.selected.length}/${MAX_MODELS}${dirty()?" · 选择已变更，点击更新对比":""}`;
      el("[data-compare-run]").disabled=state.busy||!state.selected.length;
      el("[data-compare-run]").textContent=state.busy?"加载对比中…":"更新对比";
    }
    function catalogUi(){
      const query=el("[data-compare-search]").value.trim().toLowerCase(),chosen=new Set(state.selected.map(key));
      const shown=state.catalog.filter(m=>label(m).toLowerCase().includes(query));
      el("[data-compare-models]").innerHTML=shown.map(m=>`<label><input type="checkbox" data-compare-model="${esc(key(m))}" ${chosen.has(key(m))?"checked":""} ${!chosen.has(key(m))&&state.selected.length>=MAX_MODELS?"disabled":""}>${esc(m.model)}</label>`).join("")|| (state.make?'<p>没有匹配的车型。</p>':"");
      root.querySelectorAll("[data-compare-model]").forEach(input=>input.onchange=()=>{
        const m=state.catalog.find(m=>key(m)===input.dataset.compareModel);
        if(input.checked&&state.selected.length<MAX_MODELS)state.selected.push(m);else state.selected=state.selected.filter(x=>key(x)!==key(m));
        selectedUi();catalogUi();
      });
    }
    async function catalog(resetMake=false){
      const token=++state.catalogToken;
      if(resetMake)state.make="";
      state.catalog=[];catalogUi();
      el("[data-compare-catalog-status]").textContent="加载车型目录…";
      try{
        const result=await options.loadCatalog(state.source,state.kind,state.make);
        if(token!==state.catalogToken)return;
        el("[data-compare-make]").innerHTML='<option value="">选择品牌</option>'+result.makes.map(m=>`<option value="${esc(m)}">${esc(m)}</option>`).join("");
        el("[data-compare-make]").value=state.make;
        state.catalog=result.models;catalogUi();
        el("[data-compare-catalog-status]").textContent=state.make?`${state.make} · ${state.catalog.length} 个车型；可跨品牌、跨类别添加`:"选择品牌后勾选车型；所选车型可跨品牌、跨类别保留。";
      }catch(error){if(token!==state.catalogToken)return;el("[data-compare-catalog-status]").innerHTML=`目录加载失败：${esc(error.message)} <button type="button" data-catalog-retry>重试</button>`;el("[data-catalog-retry]").onclick=()=>catalog();}
    }
    function url(){
      const next=new URL(location.href);next.searchParams.set("source",state.source);next.searchParams.set("models",JSON.stringify(state.loaded.map(m=>[m.kind,m.make,m.model])));next.searchParams.set("group",state.groupBy);next.searchParams.set("unit",state.unit);
      if(state.from!==null){next.searchParams.set("from",state.from);next.searchParams.set("to",state.to);}else{next.searchParams.delete("from");next.searchParams.delete("to");}if(state.filter)next.searchParams.set("structure",state.filter);else next.searchParams.delete("structure");
      history.replaceState(null,"",next);
    }
    function clearCharts(){charts.forEach(c=>c.clear());}
    async function run(){
      if(!state.selected.length||!window.echarts)return;
      const token=++state.loadToken,selected=state.selected.map(m=>({...m})),source=state.source;
      state.busy=true;selectedUi();el("[data-compare-status]").textContent="正在加载所选车型的完整尺寸记录与年度销量…";
      el("[data-compare-results]").hidden=true;
      try{
        const modelKeys=selected.map(m=>D.modelKey(source,m.kind,m.make,m.model));
        const [history,salesResult]=await Promise.all([options.loadHistory(modelKeys),options.loadSales(modelKeys).then(value=>({value}),error=>({error}))]);
        if(token!==state.loadToken)return;
        const version=history.origin?.data?.a0_version||history.origin?.data?.version;
        if(salesResult.value?.supported&&salesResult.value.origin.a0_version!==version)throw new Error("销量与尺寸记录版本不一致，请刷新后重试。");
        state.records=D.dedupeRecords(history.records.map(r=>D.normalizeRecord(r,{source,group:history.group})));
        state.records.forEach(record=>{record.rule=D.ruleOverlay(options.lookupRule?.(record.rawRefs[0]));});
        state.annual=salesResult.value?.supported?salesResult.value.records:null;state.salesError=salesResult.error?.message||"";state.origin=history.origin;state.salesOrigin=salesResult.value?.origin;state.loaded=selected;
        const range=C.extent(state.records);
        if(!range)throw new Error("所选车型没有可解析年份的尺寸记录，请调整选择。");
        const validYear=(value,fallback)=>value!==null&&value!==""&&Number.isFinite(Number(value))?Math.min(range[1],Math.max(range[0],Math.floor(Number(value)))):fallback;
        state.from=validYear(state.from??params.get("from"),range[0]);state.to=validYear(state.to??params.get("to"),range[1]);
        if(state.from>state.to)[state.from,state.to]=[state.to,state.from];
        const structures=[...new Set(state.records.map(C.structure))].sort();
        state.filter=structures.includes(state.filter||params.get("structure"))?(state.filter||params.get("structure")):"";
        el("[data-compare-structure]").innerHTML='<option value="">全部结构</option>'+structures.map(s=>`<option>${esc(s)}</option>`).join("");
        el("[data-compare-structure]").value=state.filter;
        el("[data-compare-results]").hidden=false;
        const found=new Set(state.records.map(C.modelKey)),missing=selected.filter(m=>!found.has(key(m)));
        el("[data-compare-status]").textContent=`已载入 ${found.size} 个车型的完整历史 · 下方按年份与结构筛选${missing.length?` · 未找到：${missing.map(label).join("、")}`:""}`;
        render();
        if(innerWidth<=760)el(".compare-selection").open=false;
        if(location.hash==="#scatter")el("[data-compare-scatter]").scrollIntoView({block:"start"});
      }catch(error){if(token!==state.loadToken)return;clearCharts();el("[data-compare-status]").textContent=`加载失败：${error.message}。可点击“更新对比”重试。`;}
      finally{if(token===state.loadToken){state.busy=false;selectedUi();}}
    }
    function chart(name,option,height){
      const node=el(`[data-compare-chart="${name}"]`);node.style.height=`${height}px`;
      if(!charts.has(name))charts.set(name,window.echarts.init(node,null,{renderer:"canvas"}));
      const instance=charts.get(name);instance.resize();instance.setOption(option,{notMerge:true});
    }
    function render(){
      const result=C.summarize(state.records,state.annual,{from:state.from,to:state.to,groupBy:state.groupBy,structureFilter:state.filter}),groups=result.groups,total=result.total;
      state.result=result;url();
      if(!scatterView)scatterView=window.FitmentScatter.create(el("[data-compare-scatter]"));
      const groupColors=new Map(groups.flatMap(g=>g.records.map(r=>[r.recordKey,color(g.key)])));
      scatterView.update({records:result.rows,annual:state.annual,from:state.from,to:state.to,unit:state.unit,salesError:state.salesError,color:r=>groupColors.get(r.recordKey)});
      el("[data-compare-from]").value=state.from;el("[data-compare-to]").value=state.to;
      const range=C.extent(state.records);["from","to"].forEach(k=>{el(`[data-compare-${k}]`).min=range[0];el(`[data-compare-${k}]`).max=range[1];});
      const cards=[["窗口内车型",total.models,`${groups.length} 个汇总组`],["尺寸记录",total.count,`${state.from}–${state.to} · 唯一记录`],["市场潜力（分）",total.potential,total.missingPotential?`已知小计 · 缺失 ${total.missingPotential} 条`:"区间分数合计，不按年重复"],["预估销量合计（千辆）",total.sales===null?null:Math.round(total.sales/1000),total.sales===null?"暂无同口径年度销量":`${total.missingSales?`已知小计 · 缺失 ${total.missingSales} 个记录年份`:"按记录年份去重"}`]];
      el("[data-compare-kpis]").innerHTML=cards.map(([name,value,note])=>`<article><span>${name}</span><strong>${number(value)}</strong><small>${note}</small></article>`).join("");
      el("[data-compare-legend]").innerHTML=groups.map(g=>`<span><i style="background:${color(g.key)}"></i>${esc(g.label)}</span>`).join("")||"当前年份与结构条件下没有记录。";
      const unit=state.unit.toUpperCase(),convert=v=>D.convertFromMm(v,state.unit),measure=v=>D.formatMeasure(v,state.unit,{withUnit:false});
      const narrow=innerWidth<=760,labelWidth=narrow?118:190,height=Math.max(250,groups.length*34+70);
      const base={animation:false,grid:{left:labelWidth,right:24,top:30,bottom:42},tooltip:{confine:true,trigger:"item",triggerOn:"mousemove|click"},yAxis:{type:"category",inverse:true,data:groups.map(g=>g.label),axisTick:{show:false},axisLabel:{width:labelWidth-20,overflow:"truncate",fontSize:11}},xAxis:{type:"value",scale:true,axisLabel:{fontSize:11},splitLine:{lineStyle:{color:"#edf1f7"}}}};
      chart("dimensions",{...base,xAxis:{...base.xAxis,name:`${({lengthMm:"车长",widthMm:"车宽",heightMm:"车高"})[state.metric]}（${unit}）`,nameLocation:"middle",nameGap:27},tooltip:{...base.tooltip,formatter:p=>{const g=groups[p.data.value[0]],m=g.dimensions[state.metric];return `${esc(g.label)}<br>最小 ${measure(m.min)} · 中位 ${measure(m.median)} · 最大 ${measure(m.max)} ${unit}<br>${m.count} 条有尺寸记录`; }},series:[{id:"compare-dimensions",type:"custom",encode:{x:[1,2,3],y:0},clip:true,data:groups.flatMap((g,i)=>{const m=g.dimensions[state.metric];return m?[{value:[i,convert(m.min),convert(m.max),convert(m.median)],itemStyle:{color:color(g.key)}}]:[];}),renderItem:(p,api)=>{const i=api.value(0),a=api.coord([api.value(1),i]),b=api.coord([api.value(2),i]),mid=api.coord([api.value(3),i]),stroke=color(groups[i].key);return {type:"group",children:[{type:"line",shape:{x1:a[0],y1:a[1],x2:b[0],y2:b[1]},style:{stroke,lineWidth:5}},{type:"circle",shape:{cx:mid[0],cy:mid[1],r:5},style:{fill:stroke,stroke:"white",lineWidth:2}}]};}}]},height);
      el("[data-compare-potential-status]").textContent=total.potential===null?"当前范围暂无同口径市场潜力分数。":total.missingPotential?`已知分数小计；${total.missingPotential} 条记录缺失。`:"";
      chart("potential",{...base,xAxis:{...base.xAxis,min:0,name:"区间分数（分）",nameLocation:"middle",nameGap:27},tooltip:{...base.tooltip,formatter:p=>{const g=groups[p.dataIndex];return `${esc(g.label)}<br>${g.missingPotential?"已知小计":"区间分数合计"} ${number(g.potential)} 分<br>缺失 ${g.missingPotential} 条`; }},series:[{id:"compare-potential",type:"bar",barMaxWidth:22,data:groups.map(g=>({value:g.potential,itemStyle:{color:color(g.key)}}))}]},height);
      const salesStatus=el("[data-compare-sales-status]");salesStatus.innerHTML=state.salesError?`销量加载失败：${esc(state.salesError)} <button type="button" data-compare-retry>重试</button>`:!state.annual?"暂无同口径年度销量数据；可继续对比尺寸。":total.missingSales?`存在 ${total.missingSales} 个缺失记录年份；不完整年份的曲线断开，已知小计见明细。`:"";
      el("[data-compare-retry]")?.addEventListener("click",run);
      const salesNode=el('[data-compare-chart="sales"]');salesNode.hidden=!state.annual;
      if(state.annual)chart("sales",{animation:false,grid:{left:55,right:20,top:36,bottom:40},xAxis:{type:"value",min:state.from,max:state.to,minInterval:1,axisLabel:{formatter:v=>String(Math.round(v))}},yAxis:{type:"value",name:"千辆",min:0},tooltip:{trigger:"axis",confine:true,triggerOn:"mousemove|click",formatter:p=>{const year=Math.round(Number(p[0]?.axisValue));const lines=[{label:"去重合计",...total},...groups].map(g=>{const v=g.years.find(y=>y.year===year);return v?`${esc(g.label)}：${number(v.known)} 辆${v.missing?` · 缺失 ${v.missing} 条`:""}`:"";}).filter(Boolean);return `${year}<br>${lines.join("<br>")}`;}},series:[...groups.map(g=>({id:g.key,name:g.label,type:"line",connectNulls:false,symbolSize:4,lineStyle:{color:color(g.key),width:2},itemStyle:{color:color(g.key)},data:C.annualSeries(g.years,state.from,state.to)})),{id:"compare-total",name:"去重合计",type:"line",connectNulls:false,symbol:"none",lineStyle:{color:"#172033",type:"dashed",width:2},data:C.annualSeries(total.years,state.from,state.to)}]},320);
      const rangeText=m=>m?`${measure(m.min)}–${measure(m.max)}`:"—";
      el("[data-compare-table]").innerHTML=`<thead><tr><th>汇总组</th><th>车型数</th><th>记录数</th><th>车长 ${unit}</th><th>车宽 ${unit}</th><th>车高 ${unit}</th><th>市场潜力（分）</th><th>销量合计（千辆）</th><th>版本</th></tr></thead><tbody>${groups.map(g=>`<tr><th>${esc(g.label)}</th><td>${g.models}</td><td>${g.count}</td>${["lengthMm","widthMm","heightMm"].map(k=>`<td>${rangeText(g.dimensions[k])}</td>`).join("")}<td>${number(g.potential)}${g.missingPotential?`<small>缺失 ${g.missingPotential} 条</small>`:""}</td><td title="${g.sales===null?"暂无数据":`${number(g.sales)} 辆`}">${g.sales===null?"—":number(Math.round(g.sales/1000))}${g.missingSales?`<small>已知小计 · 缺失 ${g.missingSales} 条</small>`:""}</td><td>${esc(g.versions.join(" / "))||"—"}</td></tr>`).join("")||'<tr><td colspan="9">当前条件没有记录。</td></tr>'}</tbody>`;
      el("[data-compare-basis]").innerHTML=`<p>范围：${esc(state.loaded.map(label).join("、"))} · 来源 ${esc(state.source)}。尺寸及潜力按 DIMENSION-ID 去重；年份窗口只筛选相交尺寸记录。销量仅累计窗口内发布的年度原子值；零值保留，缺失不补零，不用区间潜力推算销量。</p><p>尺寸版本 ${esc(state.origin?.data?.a0_version||state.origin?.data?.version||"未记录")} · 销量版本 ${esc(state.salesOrigin?.sales_version||"无同口径数据")}</p>`;
    }
    el("[data-compare-source]").value=state.source;el("[data-compare-kind]").value=state.kind;el("[data-compare-group]").value=state.groupBy;el("[data-compare-unit]").value=state.unit;
    el("[data-compare-source]").onchange=()=>{state.source=el("[data-compare-source]").value;state.loadToken++;state.busy=false;state.selected=[];state.loaded=[];state.records=[];state.from=null;state.to=null;state.filter="";params.delete("from");params.delete("to");params.delete("structure");el("[data-compare-results]").hidden=true;el("[data-compare-status]").textContent="来源已切换，请重新选择车型。";clearCharts();url();selectedUi();catalog(true);};
    el("[data-compare-kind]").onchange=()=>{state.kind=el("[data-compare-kind]").value;catalog(true);};el("[data-compare-make]").onchange=()=>{state.make=el("[data-compare-make]").value;catalog();};el("[data-compare-search]").oninput=catalogUi;
    el("[data-compare-run]").onclick=run;el("[data-compare-clear]").onclick=()=>{state.loadToken++;state.busy=false;state.selected=[];state.loaded=[];state.records=[];state.from=null;state.to=null;state.filter="";params.delete("from");params.delete("to");params.delete("structure");el("[data-compare-results]").hidden=true;el("[data-compare-status]").textContent="已清空对比，请选择车型。";clearCharts();url();selectedUi();catalogUi();};
    el("[data-compare-group]").onchange=()=>{state.groupBy=el("[data-compare-group]").value;render();};el("[data-compare-unit]").onchange=()=>{state.unit=el("[data-compare-unit]").value;render();};el("[data-compare-metric]").onchange=()=>{state.metric=el("[data-compare-metric]").value;render();};el("[data-compare-structure]").onchange=()=>{state.filter=el("[data-compare-structure]").value;render();};
    function years(){const range=C.extent(state.records),a=Number(el("[data-compare-from]").value),b=Number(el("[data-compare-to]").value);if(!range||!Number.isFinite(a)||!Number.isFinite(b))return;state.from=Math.max(range[0],Math.min(range[1],Math.floor(Math.min(a,b))));state.to=Math.max(range[0],Math.min(range[1],Math.floor(Math.max(a,b))));render();}
    ["from","to"].forEach(k=>el(`[data-compare-${k}]`).onchange=years);el("[data-compare-years]").onclick=()=>{[state.from,state.to]=C.extent(state.records);render();};
    let timer;const resize=()=>{clearTimeout(timer);timer=setTimeout(()=>{if(state.records.length&&!el("[data-compare-results]").hidden)render();},120);};window.addEventListener("resize",resize);window.addEventListener("pagehide",()=>{window.removeEventListener("resize",resize);clearTimeout(timer);charts.forEach(c=>c.dispose());scatterView?.dispose();},{once:true});
    selectedUi();catalog();
    try{if(!window.echarts)await new Promise((resolve,reject)=>{const script=document.createElement("script");script.src=options.echartsSrc;script.onload=resolve;script.onerror=()=>reject(new Error("图表资源加载失败，请刷新重试"));document.head.appendChild(script);});if(state.selected.length)await run();}catch(error){el("[data-compare-status]").textContent=error.message;}
  }
  window.ModelCompare={start};
})();
