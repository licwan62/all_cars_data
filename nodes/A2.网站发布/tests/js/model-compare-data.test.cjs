const test=require('node:test'),assert=require('node:assert/strict');
const C=require('../../src/site_overrides/assets/app/model-compare-data.js');
const row=(id,model,type,overrides={})=>({source:'US',kind:'nonpick',make:'Toyota',model,type,dimensionId:id,recordKey:id,intervals:[{startYear:2000,endYear:2002}],lengthMm:4500,widthMm:1800,heightMm:1500,marketPotential:12.5,...overrides});
test('comparison deduplicates dimension identities and annual atoms; structure groups partition totals',()=>{
  const a=row('a','Camry','Sedan'),b=row('b','Corolla','Sedan',{lengthMm:4300,marketPotential:0}),c=row('c','RAV4','SUV',{lengthMm:4600,marketPotential:null});
  const annual={a:[[2000,72545],[2001,0],[2002,100]],b:[[2000,500],[2001,600],[2002,700]],c:[[2000,null],[2002,300]]};
  const result=C.summarize([a,a,b,c],annual,{groupBy:'structure',from:2000,to:2001});
  assert.equal(result.total.count,3);assert.equal(result.total.models,3);assert.equal(result.total.potential,12.5);assert.equal(result.total.missingPotential,1);
  assert.equal(result.total.sales,73645);assert.equal(result.total.missingSales,2);
  assert.equal(result.groups.reduce((s,g)=>s+g.sales,0),result.total.sales);
  assert.equal(result.groups.find(g=>g.label==='Sedan').dimensions.lengthMm.median,4400);
  assert.equal(C.summarize([a,b,c],annual,{from:2000,to:2000,structureFilter:'Sedan'}).total.count,2);
  assert.equal(C.summarize([a,b,c],annual,{from:1999,to:1999}).total.count,0);
});
test('year gaps and missing values are never zero-filled; zero remains valid and partial years remain null',()=>{
  assert.deepEqual(C.annualSeries([{year:2000,known:0,missing:0},{year:2002,known:72545,missing:0},{year:2003,known:100,missing:1}],2000,2003),[[2000,0],[2001,null],[2002,72.545],[2003,null]]);
  const r=row('a','Camry','Sedan',{intervals:[{startYear:2000,endYear:2000},{startYear:2002,endYear:2002}]});
  assert.deepEqual(C.summarize([r],{a:[[2000,1],[2001,999],[2002,2]]}).total.years.map(y=>y.year),[2000,2002]);
  assert.equal(C.summarize([r],null).total.sales,null);
});
test('pickup structure keeps CAB/BED; model x structure and missing dimensions remain separate',()=>{
  const a=row('a','F-150','Pickup',{kind:'pick',make:'Ford',cab:'SuperCrew',bed:'5.5',version:'Raptor'}),b=row('b','F-150','Pickup',{kind:'pick',make:'Ford',cab:'Regular',bed:'8.0',lengthMm:null});
  const r=C.summarize([a,b],null,{groupBy:'structure'});
  assert.equal(r.groups.length,2);assert.match(r.groups.find(g=>g.versions.includes('Raptor')).label,/SuperCrew.*5.5ft/);
  assert.equal(r.groups.find(g=>g.label.includes('Regular')).dimensions.lengthMm,null);
  assert.equal(C.summarize([a,b],null,{groupBy:'model'}).groups.length,1);
  assert.equal(C.summarize([a,b],null,{groupBy:'model-structure'}).groups.length,2);
  assert.deepEqual(C.measure([null,0,20,10]),{min:0,max:20,median:10,count:3});
});
