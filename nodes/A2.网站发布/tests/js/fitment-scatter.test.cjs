const test=require('node:test'),assert=require('node:assert/strict');
const S=require('../../src/site_overrides/assets/app/fitment-scatter-data.js');
const row={source:'US',recordKey:'a',dimensionId:'a',lengthMm:4700,marketPotential:12.5,sizeValue:'L',intervals:[{startYear:2000,endYear:2002},{startYear:2005,endYear:2005}],rule:{ruleId:'r',size:'L',fitLow:4300,lengthMax:4800}};
test('one point per actual record-year; potential is repeated only for position and year gaps remain gaps',()=>{
  const p=S.build([row,row],null,{metric:'potential'});
  assert.deepEqual(p.points.map(p=>p.year),[2000,2001,2002,2005]);assert.equal(p.points.length,4);assert.ok(p.points.every(p=>p.value===12.5));assert.equal(p.rows,1);
  assert.deepEqual(p.overlays[0].intervals,[{from:2000,to:2002},{from:2005,to:2005}]);
  assert.deepEqual(S.build([row],null,{from:2001,to:2001}).points.map(p=>p.year),[2001]);
});
test('annual values use published dimension/year atoms and preserve zero, null and missing years',()=>{
  const p=S.build([row],{a:[[2000,72545],[2001,0],[2002,null],[2003,999]]},{metric:'sales'});
  assert.deepEqual(p.points.map(p=>p.value),[72545,0,null,null]);assert.equal(p.missing,2);assert.equal(p.zeros,1);
  assert.ok(S.build([row],null,{metric:'sales'}).points.every(p=>p.value===null));
});
test('length bands use only the upper limit, with fixed 20/40cm and 5cm offsets',()=>{
  const bands=S.segments(row.rule);
  assert.deepEqual(bands.map(s=>[s.from,s.to,s.kind]),[[4400,4600,'orange'],[4600,4800,'green'],[4800,4850,'over']]);
  assert.deepEqual(S.segments({...row.rule,fitLow:4750}),bands);
  assert.deepEqual(S.segments({...row.rule,fitLow:null}),bands);
  assert.deepEqual(S.segments({...row.rule,lengthMax:null}),[]);
});
test('shipping labels cannot masquerade as match sizes and unresolved rules never create bands',()=>{
  const ship={...row,source:'HNT',sizeMeaning:'shipping',sizeValue:'SHIP-XL',matchedSize:'L'};
  assert.equal(S.matchedSize(ship),'L');assert.equal(S.build([ship],null,{size:'L'}).points.length,4);
  const unknown={...ship,rule:null,matchedSize:''};assert.equal(S.matchedSize(unknown),'未解析匹配尺码');
  assert.equal(S.build([unknown],null).overlays.length,0);assert.equal(S.build([unknown],null).unresolvedRules,1);
  assert.equal(S.build([{...row,lengthMm:null}],null).skippedLength,1);
});
test('circle area, not diameter, scales with value; overlapping configurations remain distinct',()=>{
  assert.equal(S.diameter(100,100),30);assert.equal(S.diameter(25,100),15);
  const p=S.build([row,{...row,recordKey:'branch',dimensionId:'branch',marketPotential:0}],null);
  assert.equal(p.points.length,8);assert.equal(p.overlays.length,1);assert.equal(p.zeros,4);
});
test('identical length geometry merges labels while each record retains its actual rule',()=>{
  const other={...row,recordKey:'b',dimensionId:'b',rule:{...row.rule,ruleId:'other',size:'L-0',fitLow:4650}};
  const result=S.build([row,other],null);
  assert.equal(result.overlays.length,1);assert.equal(result.overlays[0].size,'L / L-0');
  assert.deepEqual([...new Set(result.points.map(p=>p.record.rule.ruleId))],['r','other']);
  assert.equal(S.build([row,other],null,{size:'L-0'}).overlays[0].size,'L-0');
});
