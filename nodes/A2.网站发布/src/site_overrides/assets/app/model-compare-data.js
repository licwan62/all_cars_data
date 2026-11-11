// Comparison uses published dimension identities and annual sales atoms only.
(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports) module.exports=api;
  else root.ModelCompareData=api;
})(typeof window==="undefined"?globalThis:window,function(){
  const identity=r=>JSON.stringify([r.source,r.dimensionId||r.recordKey]);
  const modelKey=r=>JSON.stringify([r.kind,r.make,r.model]);
  function structure(r){
    return r.kind==="pick" ? ["Pickup",r.cab||"CAB 未记录",r.bed ? `${String(r.bed).replace(/\s*ft$/i,"")}ft` : "BED 未记录"].join(" · ") : r.type||"结构未记录";
  }
  function extent(records){
    const years=records.flatMap(r=>r.intervals.flatMap(i=>[i.startYear,i.endYear]));
    return years.length?[Math.min(...years),Math.max(...years)]:null;
  }
  function measure(values){
    const sorted=values.filter(Number.isFinite).sort((a,b)=>a-b),n=sorted.length;
    return n ? {min:sorted[0],max:sorted[n-1],median:(sorted[Math.floor((n-1)/2)]+sorted[Math.floor(n/2)])/2,count:n} : null;
  }
  function summarize(records,annual,options={}){
    const {from=-Infinity,to=Infinity,groupBy="model",structureFilter=""}=options;
    const unique=[...new Map(records.map(r=>[identity(r),r])).values()];
    const rows=unique.filter(r=>(!structureFilter||structure(r)===structureFilter)&&r.intervals.some(i=>i.startYear<=to&&i.endYear>=from));
    const byGroup=new Map();
    rows.forEach(r=>{
      const model=`${r.make} ${r.model}`,shape=structure(r);
      const key=JSON.stringify(groupBy==="structure"?[shape]:groupBy==="model-structure"?[modelKey(r),shape]:[modelKey(r)]);
      if(!byGroup.has(key))byGroup.set(key,{key,label:groupBy==="structure"?shape:groupBy==="model-structure"?`${model} · ${shape}`:model,records:[]});
      byGroup.get(key).records.push(r);
    });
    function metrics(list){
      const potentialRows=list.filter(r=>Number.isFinite(r.marketPotential));
      const years=new Map(),seen=new Set();
      if(annual)list.forEach(r=>{
        const pairs=new Map(annual[r.dimensionId]||[]);
        r.intervals.forEach(i=>{
          for(let year=Math.max(i.startYear,Math.ceil(from));year<=Math.min(i.endYear,Math.floor(to));year++){
            const atom=`${identity(r)}|${year}`;
            if(seen.has(atom))continue;seen.add(atom);
            if(!years.has(year))years.set(year,{year,known:0,missing:0,count:0});
            const item=years.get(year),value=pairs.get(year);item.count++;
            if(Number.isFinite(value))item.known+=value;else item.missing++;
          }
        });
      });
      return {models:new Set(list.map(modelKey)).size,count:list.length,dimensions:Object.fromEntries(["lengthMm","widthMm","heightMm"].map(key=>[key,measure(list.map(r=>r[key]))])),
        potential:potentialRows.length?potentialRows.reduce((sum,r)=>sum+r.marketPotential,0):null,missingPotential:list.length-potentialRows.length,
        years:[...years.values()].sort((a,b)=>a.year-b.year),sales:annual?[...years.values()].reduce((sum,r)=>sum+r.known,0):null,missingSales:[...years.values()].reduce((sum,r)=>sum+r.missing,0),
        versions:[...new Set(list.map(r=>r.version).filter(Boolean))]};
    }
    const groups=[...byGroup.values()].sort((a,b)=>a.label.localeCompare(b.label,"en",{numeric:true})).map(g=>({...g,...metrics(g.records)}));
    return {rows,groups,total:metrics(rows),extent:extent(rows)};
  }
  function annualSeries(years,from,to){
    const map=new Map(years.map(r=>[r.year,r]));
    return Array.from({length:Math.max(0,to-from+1)},(_,i)=>{const year=from+i,r=map.get(year);return [year,r&&!r.missing?r.known/1000:null];});
  }
  return {structure,extent,measure,summarize,annualSeries,modelKey};
});
