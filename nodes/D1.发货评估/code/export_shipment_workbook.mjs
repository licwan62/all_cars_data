import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

const require = createRequire(path.resolve('work/shipment-export/package.json'));
const { Workbook, SpreadsheetFile } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')));
const [input, output] = process.argv.slice(2);
const { records, stats } = JSON.parse(await fs.readFile(input, 'utf8'));
const wb = Workbook.create();
const columns = ['SKU', 'MAKE', 'MODEL', 'YEAR', '供货尺码', '定制标记', '差评标记',
  '第一批发货量', '第二批发货量', '总发货量', '调整后市场潜力值', '分配权重占比',
  '第二批类型', '结构', '版本', '代际', '差评原因', '差评备注'];
const numeric = new Set(['第一批发货量', '第二批发货量', '总发货量', '调整后市场潜力值', '分配权重占比']);
for (const [name, rows] of [ ['发货总表', records],
  ['第一批拣货', records.filter(r => r.第一批发货量 > 0)],
  ['第二批拣货', records.filter(r => r.第二批发货量 > 0)] ]) {
  const s = wb.worksheets.add(name);
  s.showGridLines = false;
  s.tabColor = '#254D72';
  s.getRange('A2').values = [[`普通车两批发货单 · ${name}`]];
  s.getRange('A2').format.font = {name: 'Arial', size: 14, bold: true};
  s.getRange('A4:F4').values = [['第一批件数', 1000, '第二批件数', 1000, '两批合计', 2000]];
  s.getRange('A5:F5').values = [['首批覆盖SKU', stats.batch1_skus, '第二批新增SKU', stats.new_skus_batch2, '累计覆盖SKU', stats.total_skus]];
  s.getRange('A7').values = [['覆盖优先：首批每SKU一件；次批先新增覆盖，再按权重分配余量；两批合计每SKU最多25件。']];
  s.getRange('A8').values = [['定制项供货尺码留空，SKU编号保留源记录身份。差评项保留参与分配。']];
  const data = [columns, ...rows.map(r => columns.map(c => numeric.has(c) ? Number(r[c]) : r[c] ?? ''))];
  s.getRange(`A10:R${9 + data.length}`).values = data;
  s.tables.add(`A10:R${9 + data.length}`, true, `Shipment${wb.worksheets.items?.length ?? name.length}${rows.length}`);
  s.getRange(`A10:R${9 + data.length}`).format.font = {name: 'Arial', size: 10};
  s.getRange(`A10:R${9 + data.length}`).format.rowHeight = 21;
  s.getRange('A10:R10').format = {fill: '#254D72', font: {bold: true, color: '#FFFFFF'}, rowHeight: 30, wrapText: true};
  s.getRange('A10:A10').format.columnWidth = 24;
  s.getRange('B10:B10').format.columnWidth = 20;
  s.getRange('C10:C10').format.columnWidth = 25;
  s.getRange('D10:D10').format.columnWidth = 16;
  s.getRange('E10:G10').format.columnWidth = 13;
  s.getRange('H10:J10').format.columnWidth = 14;
  s.getRange('K10:L10').format.columnWidth = 19;
  s.getRange('M10:P10').format.columnWidth = 24;
  s.getRange('Q10:R10').format.columnWidth = 50;
  s.getRange(`H11:J${10 + rows.length}`).setNumberFormat('#,##0');
  s.getRange(`K11:K${10 + rows.length}`).setNumberFormat('#,##0.00');
  s.getRange(`L11:L${10 + rows.length}`).setNumberFormat('0.00%');
  s.getRange(`F11:G${10 + rows.length}`).conditionalFormats.add('containsText', {text:'尺寸', format:{fill:'#FCE4D6'}});
  s.freezePanes.freezeRows(10);
  s.freezePanes.freezeColumns(3);
}
wb.recalculate();
console.log((await wb.inspect({kind:'region',sheetId:'发货总表',range:'A4:F5',maxChars:1500,tableMaxRows:2,tableMaxCols:6})).ndjson);
const preview = await wb.render({sheetName:'发货总表',range:'A1:L16',scale:1,format:'png'});
await fs.writeFile(path.join(path.dirname(input),'shipment-preview.png'),new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
