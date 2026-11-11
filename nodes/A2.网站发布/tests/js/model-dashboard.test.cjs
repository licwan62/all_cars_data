const test=require('node:test');
const assert=require('node:assert/strict');
const M=require('../../src/site_overrides/assets/app/model-dashboard.js');
test('dashboard counts unique records and interval scores once; clips coverage without filling gaps',()=>{
  const first={recordKey:'one',configurationKey:'a',intervals:[{startYear:2000,endYear:2002}],sizeValue:'3M',marketPotential:10,matchStatus:'matched',lengthMm:4500,widthMm:1800,heightMm:1500};
  const second={...first,recordKey:'two',intervals:[{startYear:2005,endYear:2006}],marketPotential:null,lengthMm:4600};
  const s=M.summarize([first,first,second],null);
  assert.equal(s.rows.length,2);assert.equal(s.potential,10);assert.equal(s.missingPotential,1);
  assert.deepEqual(s.years,[2000,2001,2002,2005,2006]);assert.deepEqual(s.dimensions[0],[4500,4600]);
  assert.equal(M.summarize([first,second],{startValue:2001,endValue:2001}).potential,10);
  assert.equal(M.summarize([second],null).potential,null);
});
test('annual details retain raw counts, round thousands and distinguish missing values',()=>{
  const sales={totals:new Map([[2000,{known:72545,missing:0}],[2001,{known:300,missing:1}],[2002,{known:45000,missing:0}]])};
  const html=M.salesMarkup(sales,'ready',null);
  assert.match(html,/73/);assert.match(html,/72,545/);assert.match(html,/缺失 1 条/);
  assert.match(html, /<td>2001<\/td><td>—<\/td>/);
  assert.ok(!M.sizesMarkup({sizes:[['<script>',1]]},false).includes('<script>'));
});
