(function(){
  "use strict";
  const S=window.FitmentScatterData,D=window.SizeEvolutionData,R=window.SizeViewerRules;
  const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const num=v=>Number.isFinite(v)?v.toLocaleString("zh-CN",{maximumFractionDigits:4}):"—";
  function create(host,preferences={}){
    host.classList.add("fitment-scatter");
    host.innerHTML=`<div class="scatter-heading"><h3>尺码配对散点图</h3><div class="scatter-controls"><label>点大小<select data-scatter-metric aria-label="散点大小指标"><option value="potential">市场潜力</option><option value="sales">当年预估销量</option></select></label><label>匹配尺码<select data-scatter-size aria-label="散点匹配尺码"><option value="">全部匹配尺码</option></select></label><label class="scatter-overlay"><input type="checkbox" data-scatter-overlay checked>尺码长度图层</label></div></div>
      <p class="scatter-explanation" data-scatter-explanation></p>${R.fitmentLegendMarkup()}
      <div class="scatter-scale" data-scatter-scale aria-label="散点大小图例"></div><p class="scatter-status" data-scatter-status role="status"></p>
      <div class="scatter-chart-wrap"><div data-scatter-chart role="img" aria-label="横轴车长、纵轴年份，点面积表示潜力或销量，背景叠加尺码长度区间"></div><div class="scatter-tooltip" data-scatter-tooltip hidden></div></div>
      <details class="scatter-details" data-scatter-details><summary>点按散点查看记录及同坐标车型</summary><div data-scatter-records>点按图中散点可展开原始年份范围、配置、匹配规则和数值。</div></details>`;
    const el=s=>host.querySelector(s);
    const state={metric:preferences.metric==="sales"?"sales":"potential",size:preferences.size||"",overlay:preferences.overlay!==false,input:null,data:null,zoom:null,scope:"",locked:null};
    el("[data-scatter-metric]").value=state.metric;
    el("[data-scatter-overlay]").checked=state.overlay;
    const chart=window.echarts.init(el("[data-scatter-chart]"),null,{renderer:"canvas"});
    const measurement=value=>D.formatMeasure(value,state.input.unit||"cm");
    const valueText=p=>p.value===null?"缺失":`${num(p.value)} ${state.metric==="sales"?"辆":"分"}`;
    const label=r=>D.configurationLabel(r,{includeModel:true});
    const siblings=p=>state.data.points.filter(other=>other.year===p.year&&other.lengthMm===p.lengthMm);
    function pointText(p,full=false){
      const r=p.record,rule=r.rule,delta=rule&&Number.isFinite(rule.lengthMax)?rule.lengthMax-r.lengthMm:null;
      const size=r.sizeMeaning==="shipping"?`匹配尺码 ${p.size} → 发货 ${r.sizeValue||"—"}`:`匹配尺码 ${p.size}`;
      return `<strong>${esc(label(r))}</strong><br>${p.year} 年 · 车长 ${measurement(r.lengthMm)}<br>${esc(size)}${delta!==null?` · ${delta>=0?"余量":"超出"} ${measurement(Math.abs(delta))}`:""}<br>${state.metric==="sales"?"当年预估销量":"尺寸记录区间潜力"}：${valueText(p)}${full?`<br>原始年份 ${esc(r.yearText)} · DIMENSION-ID ${esc(r.dimensionId||"未记录")}<br>${rule?`规则 ${esc(rule.ruleId)} · 长度条件 ${measurement(rule.fitLow)}–${measurement(rule.lengthMax)}<br>${esc((rule.conditions||[]).join(" · "))}`:"无法解析同版本匹配规则，未叠加尺码范围"}`:""}`;
    }
    function details(){
      if(!state.locked)return;
      const point=state.data.points.find(p=>p.key===state.locked);
      if(!point){state.locked=null;el("[data-scatter-records]").textContent="已选散点不在当前筛选范围。";return;}
      const colocated=siblings(point);
      el("[data-scatter-records]").innerHTML=`<p>${point.year} 年 · ${measurement(point.lengthMm)} · 同坐标 ${colocated.length} 条记录</p>${colocated.map(p=>`<article>${pointText(p,true)}</article>`).join("")}`;
    }
    const hideTip=()=>{el("[data-scatter-tooltip]").hidden=true;};
    function showTip(params){
      if(params.seriesId!=="fitment-scatter-points")return;
      const point=state.data?.points[params.data.pointIndex];if(!point)return;
      const tip=el("[data-scatter-tooltip]"),wrap=el(".scatter-chart-wrap"),n=siblings(point).length;
      tip.innerHTML=pointText(point)+(n>1?`<br>同坐标 ${n} 条记录，点按展开全部`:"<br>点按查看依据");tip.hidden=false;
      const xy=chart.convertToPixel({xAxisIndex:0,yAxisIndex:0},params.data.value.slice(0,2));
      const x=params.event?.offsetX??xy[0],y=params.event?.offsetY??xy[1];
      tip.style.left=`${Math.max(4,Math.min(x+12,wrap.clientWidth-tip.offsetWidth-4))}px`;
      tip.style.top=`${Math.max(4,Math.min(y+12,wrap.clientHeight-tip.offsetHeight-4))}px`;
    }
    chart.on("mousemove",showTip);chart.on("mouseout",hideTip);chart.getZr().on("globalout",hideTip);
    chart.on("click",params=>{
      if(params.seriesId!=="fitment-scatter-points")return;
      const point=state.data.points[params.data.pointIndex];
      if(!point)return;
      state.locked=point.key;details();showTip(params);el("[data-scatter-details]").open=true;
    });
    chart.on("datazoom",()=>{const zoom=chart.getOption().dataZoom?.[0];if(zoom)state.zoom={start:zoom.start,end:zoom.end};});
    function render(){
      if(!state.input)return;
      hideTip();
      el(".scatter-band-legend").hidden = !state.overlay;
      const input=state.input,from=input.from,to=input.to,unit=input.unit||"cm";
      const all=S.build(input.records,input.annual,{from,to,metric:state.metric});
      if(!all.sizes.includes(state.size))state.size="";
      el("[data-scatter-size]").innerHTML='<option value="">全部匹配尺码</option>'+all.sizes.map(s=>`<option value="${esc(s)}">${esc(s)}</option>`).join("");
      el("[data-scatter-size]").value=state.size;
      state.data=state.size?S.build(input.records,input.annual,{from,to,metric:state.metric,size:state.size}):all;
      const data=state.data,largest=innerWidth<=760?24:32;
      el("[data-scatter-explanation]").textContent=state.metric==="sales"?"每条尺寸记录的每个有效年份一个点；点面积表示该年发布的预估销量（辆），缺失不补零。":"每条尺寸记录的每个有效年份一个点；点面积表示原始区间潜力分数，跨年重复仅用于定位，不重复计入潜力合计。";
      const notes=[`${data.rows} 条尺寸记录 · ${data.points.length} 个记录年份点`,data.skippedLength&&`${data.skippedLength} 条缺少车长未绘制`,data.unresolvedRules&&`${data.unresolvedRules} 条未能解析同版本尺码规则`,data.missing&&`${data.missing} 点数值缺失`].filter(Boolean);
      if(state.metric==="sales"&&input.salesState==="loading")notes.push("年度销量加载中");
      if(state.metric==="sales"&&input.salesError&&(!input.salesState||input.salesState==="error"))notes.push(`年度销量加载失败：${input.salesError}`);
      el("[data-scatter-status]").textContent=notes.join(" · ")+"。色带只解释当前发布的命中规则；长度颜色不改变匹配结果。";
      const samples=data.max>0?[data.max/4,data.max/2,data.max]:[];
      el("[data-scatter-scale]").innerHTML=samples.map(v=>`<span><i class="scatter-example" style="width:${S.diameter(v,data.max,largest)}px;height:${S.diameter(v,data.max,largest)}px"></i>${num(v)} ${state.metric==="sales"?"辆":"分"}</span>`).join("")+'<span><i class="scatter-zero"></i>零值</span><span><i class="scatter-missing"></i>缺失</span><small>面积按数值比例缩放，小值保留最小可见点；点颜色沿用配置／汇总图例。</small>';
      const canvas=el("[data-scatter-chart]");canvas.style.height=innerWidth<=760?"430px":"510px";chart.resize();
      const convert=v=>D.convertFromMm(v,unit),bandData=[];
      if(state.overlay)data.overlays.forEach(rule=>rule.intervals.forEach((interval,index)=>{
        rule.segments.forEach(segment=>bandData.push({value:[convert(segment.from),convert(segment.to),interval.from-.5,interval.to+.5],color:segment.color}));
        bandData.push({value:[convert(rule.upper),convert(rule.upper),interval.from-.5,interval.to+.5],line:true,label:index===0?`${rule.size} 上限 ${num(convert(rule.upper))}`:""});
      }));
      const points=data.points.map((p,index)=>({value:[convert(p.lengthMm),p.year,p.value],pointIndex:index,recordKey:p.record.recordKey,dimensionId:p.record.dimensionId,
        symbol:p.value===null?"diamond":"circle",symbolSize:S.diameter(p.value,data.max,largest),itemStyle:{color:p.value===null?"#94a3b8":p.value===0?"#ffffff":input.color?.(p.record)||"#2468b4",opacity:p.value===0?1:p.value===null?0.6:0.7,borderColor:p.value===0?(input.color?.(p.record)||"#2468b4"):"#fff",borderWidth:p.value===0?1.5:1}})).sort((a,b)=>(b.value[2]??-1)-(a.value[2]??-1));
      const lengths=data.points.map(p=>convert(p.lengthMm));
      if(state.overlay)data.overlays.forEach(r=>lengths.push(convert(r.displayStart),convert(r.upper+50)));
      const min=lengths.length?Math.min(...lengths):0,max=lengths.length?Math.max(...lengths):1,pad=Math.max((max-min)*.05,convert(20));
      chart.setOption({animation:false,grid:{left:innerWidth<=760?51:65,right:30,top:32,bottom:44},xAxis:{type:"value",min:min-pad,max:max+pad,name:`车长（${unit.toUpperCase()}）`,nameLocation:"middle",nameGap:28,axisLabel:{fontSize:11,formatter:v=>num(Math.round(v*10)/10)},splitLine:{lineStyle:{color:"#e9eef5"}}},yAxis:{type:"value",inverse:true,min:Number.isFinite(from)?from-.5:"dataMin",max:Number.isFinite(to)?to+.5:"dataMax",minInterval:1,splitNumber:8,name:"年份",nameLocation:"middle",nameGap:36,axisLabel:{fontSize:11,formatter:v=>Number.isInteger(v)?String(v):""},splitLine:{lineStyle:{color:"#edf1f6"}}},
        tooltip:{show:false},
        dataZoom:[{type:"inside",yAxisIndex:0,filterMode:"none",zoomOnMouseWheel:"ctrl",moveOnMouseWheel:false,...(state.zoom||{})},{type:"slider",yAxisIndex:0,orient:"vertical",right:2,top:32,bottom:44,width:12,filterMode:"none",labelFormatter:v=>String(Math.round(v)),...(state.zoom||{})}],
        series:[{id:"fitment-scatter-rules",type:"custom",silent:true,z:0,clip:true,encode:{x:[0,1],y:[2,3]},data:bandData,renderItem:(p,api)=>{
          const item=bandData[p.dataIndex],a=api.coord([api.value(0),api.value(2)]),b=api.coord([api.value(1),api.value(3)]),grid=p.coordSys;
          if(item.line){const top=Math.max(grid.y,a[1]),bottom=Math.min(grid.y+grid.height,b[1]);if(bottom<=top)return null;const children=[{type:"line",shape:{x1:a[0],y1:top,x2:a[0],y2:bottom},style:{stroke:"#64748b",lineWidth:1,lineDash:[4,4],opacity:.65}}];const alignRight=a[0]>grid.x+grid.width*.65;if(item.label&&bottom-top>35)children.push({type:"text",style:{x:a[0]+(alignRight?-4:4),y:top+3,text:item.label,align:alignRight?"right":"left",fill:"#52627d",fontSize:10}});return {type:"group",children};}
          const rect=window.echarts.graphic.clipRectByRect({x:a[0],y:Math.min(a[1],b[1]),width:Math.max(0,b[0]-a[0]),height:Math.abs(b[1]-a[1])},grid);
          return rect?{type:"rect",shape:rect,style:{fill:item.color,opacity:R.FITMENT_BAND_OPACITY}}:null;
        }},{id:"fitment-scatter-points",type:"scatter",z:3,clip:true,encode:{x:0,y:1},data:points,emphasis:{itemStyle:{opacity:1,borderColor:"#172033",borderWidth:2}}}]},{notMerge:true});
      if(!data.points.length)el("[data-scatter-status]").textContent="当前年份、配置或尺码范围没有可绘制的记录。";
      details();
    }
    el("[data-scatter-metric]").onchange=()=>{state.metric=el("[data-scatter-metric]").value;render();};
    el("[data-scatter-size]").onchange=()=>{state.size=el("[data-scatter-size]").value;state.zoom=null;render();};
    el("[data-scatter-overlay]").onchange=()=>{state.overlay=el("[data-scatter-overlay]").checked;render();};
    let timer,previousWidth=0;
    const observer=new ResizeObserver(entries=>{const width=entries[0].contentRect.width;if(Math.abs(width-previousWidth)<1)return;previousWidth=width;clearTimeout(timer);timer=setTimeout(render,80);});observer.observe(host);
    return {update(input){const scope=JSON.stringify([input.from,input.to,input.unit,input.records.map(r=>r.recordKey)]);if(scope!==state.scope){state.zoom=null;state.scope=scope;}state.input=input;render();},preferences(){return {metric:state.metric,size:state.size,overlay:state.overlay};},dispose(){observer.disconnect();clearTimeout(timer);chart.dispose();}};
  }
  window.FitmentScatter={create};
})();
