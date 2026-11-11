(function(root,factory){
  const api=factory(typeof module==="object"&&module.exports?require("./viewer-rules.js"):root.SizeViewerRules);
  if(typeof module==="object"&&module.exports)module.exports=api;
  else root.FitmentScatterData=api;
})(typeof window==="undefined"?globalThis:window,function(R){
  const identity=r=>JSON.stringify([r.source,r.recordKey||r.dimensionId]);
  const matchedSize=r=>r.rule?.size||r.matchedSize||(r.sizeMeaning==="shipping"?"":r.sizeValue)||"未解析匹配尺码";
  function segments(rule){
    return R.fitmentSegments(rule?.lengthMax);
  }
  function mergeIntervals(intervals){
    const sorted=intervals.map(i=>({...i})).sort((a,b)=>a.from-b.from||a.to-b.to),result=[];
    sorted.forEach(i=>{const last=result.at(-1);if(last&&i.from<=last.to+1)last.to=Math.max(last.to,i.to);else result.push(i);});
    return result;
  }
  function build(records,annual,{from=-Infinity,to=Infinity,metric="potential",size=""}={}){
    const unique=[...new Map(records.map(r=>[identity(r),r])).values()];
    const all=unique.filter(r=>r.intervals.some(i=>i.startYear<=to&&i.endYear>=from));
    const sizes=[...new Set(all.map(matchedSize))].sort((a,b)=>a.localeCompare(b,"en",{numeric:true}));
    const rows=all.filter(r=>!size||matchedSize(r)===size),points=[],rules=new Map();
    let skippedLength=0,unresolvedRules=0;
    rows.forEach(record=>{
      if(!Number.isFinite(record.lengthMm)||record.lengthMm<=0){skippedLength++;return;}
      const intervals=mergeIntervals(record.intervals.map(i=>({from:Math.max(i.startYear,Math.ceil(from)),to:Math.min(i.endYear,Math.floor(to))})).filter(i=>i.from<=i.to));
      const pairs=new Map(annual?.[record.dimensionId]||[]),seen=new Set();
      intervals.forEach(i=>{for(let year=i.from;year<=i.to;year++){
        if(seen.has(year))continue;seen.add(year);
        const value=metric==="sales"?pairs.get(year):record.marketPotential;
        points.push({record,year,lengthMm:record.lengthMm,value:Number.isFinite(value)&&value>=0?value:null,size:matchedSize(record),key:`${identity(record)}|${year}`});
      }});
      const bands=segments(record.rule);
      if(!bands.length){unresolvedRules++;return;}
      // Identical length geometry is drawn once; record-level rules remain on each point.
      const key=JSON.stringify([record.source,record.rule.lengthMax]);
      if(!rules.has(key))rules.set(key,{key,sizes:new Set(),upper:record.rule.lengthMax,displayStart:bands[0].from,segments:bands,intervals:[]});
      rules.get(key).sizes.add(matchedSize(record));
      rules.get(key).intervals.push(...intervals);
    });
    const overlays=[...rules.values()].map(({sizes,...r})=>({...r,size:[...sizes].sort().join(" / "),intervals:mergeIntervals(r.intervals)}));
    const max=Math.max(0,...points.map(p=>p.value??0));
    return {points,overlays,sizes,rows:rows.length,skippedLength,unresolvedRules,max,missing:points.filter(p=>p.value===null).length,zeros:points.filter(p=>p.value===0).length};
  }
  function diameter(value,max,largest=30){
    if(value===null)return 7;
    if(value===0)return 6;
    return max>0?Math.max(3,largest*Math.sqrt(value/max)):3;
  }
  return {build,segments,matchedSize,diameter,mergeIntervals};
});
