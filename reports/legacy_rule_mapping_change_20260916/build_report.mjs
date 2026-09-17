import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = new URL("./", import.meta.url);
const payload = JSON.parse(await fs.readFile(new URL("report_data.json", outputDir), "utf8"));
const workbook = Workbook.create();
const font = "Arial";
const navy = "#1F4E78";
const blue = "#D9EAF7";
const lightBlue = "#EAF3F8";
const paleRed = "#FCE8E6";
const gray = "#666666";

function colName(index) {
  let n = index + 1;
  let name = "";
  while (n > 0) {
    const rem = (n - 1) % 26;
    name = String.fromCharCode(65 + rem) + name;
    n = Math.floor((n - 1) / 26);
  }
  return name;
}

function writeTable(sheet, startRow, startCol, headers, rows, name) {
  const matrix = [headers, ...rows.map((row) => headers.map((header) => row[header] ?? null))];
  sheet.getRangeByIndexes(startRow, startCol, matrix.length, headers.length).values = matrix;
  const end = `${colName(startCol + headers.length - 1)}${startRow + matrix.length}`;
  const start = `${colName(startCol)}${startRow + 1}`;
  const table = sheet.tables.add(`${start}:${end}`, true, name);
  table.style = "TableStyleMedium2";
  table.showBandedRows = true;
  return { range: sheet.getRange(`${start}:${end}`), table };
}

function baseSheet(name, tabColor = null) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridLines = false;
  if (tabColor) sheet.tabColor = tabColor;
  return sheet;
}

const summary = baseSheet("总览", navy);
summary.getRange("A2:H2").merge();
summary.getRange("A2").values = [["Legacy 与 public 当前发布版车型尺码映射变动报告"]];
summary.getRange("A2:H2").format = {
  font: { name: font, size: 16, bold: true, color: "#1F1F1F" },
  verticalAlignment: "center",
};
summary.getRange("A3:H3").format.borders = { bottom: { style: "thin", color: navy } };
summary.getRange("A5:B13").values = [
  ["指标", "结果"],
  ["全量记录数", payload.metrics["全量记录数"]],
  ["变动记录数", payload.metrics["变动记录数"]],
  ["记录变动率", payload.metrics["记录变动率"]],
  ["变动销量", payload.metrics["变动销量"]],
  ["新增可匹配", payload.metrics["新增可匹配"]],
  ["新增不可用", payload.metrics["新增不可用"]],
  ["可用尺码之间迁移", payload.metrics["可用尺码迁移"]],
  ["不可用状态变化", payload.metrics["不可用状态变化"]],
];
summary.getRange("A5:B5").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
summary.getRange("A6:A13").format.font = { name: font, bold: true };
summary.getRange("B6:B13").format.font = { name: font, size: 11 };
summary.getRange("B6:B7").format.numberFormat = "#,##0";
summary.getRange("B8").format.numberFormat = "0.0%";
summary.getRange("B9:B13").format.numberFormat = "#,##0";
summary.getRange("D5:H5").merge();
summary.getRange("D5").values = [["结论与口径"]];
summary.getRange("D5:H5").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
summary.getRange("D6:H10").merge(true);
summary.getRange("D6:D10").values = [
  [`${payload.metrics["全量记录数"].toLocaleString()} 条车型全量一对一对齐，${payload.metrics["变动记录数"].toLocaleString()} 条尺码映射发生变化。`],
  [`变动车型涉及销量 ${payload.metrics["变动销量"].toLocaleString()}。`],
  [`${payload.metrics["新增可匹配"]} 条由不可用转为可匹配，${payload.metrics["新增不可用"]} 条由可匹配转为不可用。`],
  ["跨版本使用 MAKE、MODEL、版本、结构、YEAR、CAB、BED 的清洗业务键对齐。"],
  ["两份原始 DIMENSION-ID 文本直接相等为 0 条，不作为跨版本连接键。"],
];
summary.getRange("D6:H10").format = { font: { name: font, color: "#333333" }, wrapText: true, verticalAlignment: "center" };
summary.getRange("A15:F15").values = [["分类", "全量记录数", "变动记录数", "记录变动率", "变动销量", "销量影响率"]];
const categoryRows = payload.category.map((r) => [r["分类"], r["全量记录数"], r["变动记录数"], r["记录变动率"], r["变动销量"], r["销量影响率"]]);
summary.getRangeByIndexes(15, 0, categoryRows.length, 6).values = categoryRows;
summary.getRange("A15:F15").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
summary.getRange(`B16:C${15 + categoryRows.length}`).format.numberFormat = "#,##0";
summary.getRange(`D16:D${15 + categoryRows.length}`).format.numberFormat = "0.0%";
summary.getRange(`E16:E${15 + categoryRows.length}`).format.numberFormat = "#,##0";
summary.getRange(`F16:F${15 + categoryRows.length}`).format.numberFormat = "0.0%";
summary.getRange(`A15:F${15 + categoryRows.length}`).format.borders = { preset: "inside", style: "thin", color: "#D9E2F3" };
const chart = summary.charts.add("bar", [summary.getRange(`A15:A${15 + categoryRows.length}`), summary.getRange(`C15:C${15 + categoryRows.length}`)]);
chart.title = "各分类变动记录数";
chart.titleTextStyle.typeface = font;
chart.hasLegend = false;
chart.xAxis = { axisType: "textAxis", textStyle: { typeface: font, fontSize: 10 } };
chart.yAxis = { numberFormatCode: "0", numberFormatSourceLinked: false, textStyle: { typeface: font } };
chart.setPosition("H14", "N27");
summary.getRange("A1:N28").format.font = { name: font, size: 10 };
summary.getRange("A:A").format.columnWidth = 22;
summary.getRange("B:B").format.columnWidth = 16;
summary.getRange("C:F").format.columnWidth = 14;
summary.getRange("D:H").format.columnWidth = 15;
summary.getRange("A2:H2").format.rowHeight = 26;

const category = baseSheet("分类影响", "#5B9BD5");
const categoryHeaders = ["分类", "全量记录数", "变动记录数", "全量销量", "变动销量", "记录变动率", "销量影响率"];
writeTable(category, 1, 0, categoryHeaders, payload.category, "CategoryImpact");
category.getRange("B3:E100").format.numberFormat = "#,##0";
category.getRange("F3:G100").format.numberFormat = "0.0%";
category.freezePanes.freezeRows(2);

const transitions = baseSheet("迁移路径", "#5B9BD5");
const transitionHeaders = ["分类", "旧尺码", "新尺码", "记录数", "销量合计", "变更路径"];
writeTable(transitions, 1, 0, transitionHeaders, payload.transitions, "SizeTransitions");
transitions.getRange("D3:E500").format.numberFormat = "#,##0";
transitions.freezePanes.freezeRows(2);

const details = baseSheet("变动明细", "#70AD47");
const detailHeaders = ["MAKE", "MODEL", "SUB-MODEL", "版本", "代际", "YEAR", "分类", "结构", "CAB", "BED", "L-MM", "W-MM", "H-MM", "销量合计", "DIMENSION-ID", "新DIMENSION-ID", "旧尺码", "新尺码", "旧长度余量", "新长度余量", "变更路径"];
writeTable(details, 1, 0, detailHeaders, payload.details, "MappingChanges");
details.getRange("K3:N500").format.numberFormat = "#,##0";
details.getRange("S3:T3000").format.numberFormat = "#,##0";
details.getRange("Q3:R3000").conditionalFormats.addCustom('=$Q3<>$R3', { fill: paleRed, font: { color: "#9C0006", bold: true } });
details.freezePanes.freezeRows(2);
details.freezePanes.freezeColumns(2);

const audit = baseSheet("匹配键校验", "#A5A5A5");
writeTable(audit, 1, 0, ["校验项", "结果"], payload.match_audit, "MatchAudit");
audit.getRange("B3:B20").format.numberFormat = "#,##0";
audit.freezePanes.freezeRows(2);

for (const sheet of [category, transitions, details, audit]) {
  const used = sheet.getUsedRange();
  used.format.font = { name: font, size: 10, color: "#222222" };
  used.format.verticalAlignment = "center";
  used.format.autofitColumns();
  used.format.autofitRows();
}
category.getRange("A:G").format.columnWidth = 15;
transitions.getRange("A:F").format.columnWidth = 18;
details.getRange("A:U").format.columnWidth = 14;
details.getRange("C:C").format.columnWidth = 22;
details.getRange("O:P").format.columnWidth = 42;
details.getRange("U:U").format.columnWidth = 24;
audit.getRange("A:A").format.columnWidth = 36;
audit.getRange("B:B").format.columnWidth = 16;

workbook.recalculate();
const inspect = await workbook.inspect({ kind: "table", sheetId: "总览", range: "A2:N27", include: "values,formulas", tableMaxRows: 30, tableMaxCols: 14 });
await fs.writeFile(new URL("inspect_summary.ndjson", outputDir), inspect.ndjson, "utf8");
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan" });
await fs.writeFile(new URL("inspect_errors.ndjson", outputDir), errors.ndjson, "utf8");
const preview = await workbook.render({ sheetName: "总览", range: "A1:N28", scale: 1.2, format: "png" });
await fs.writeFile(new URL("preview.png", outputDir), new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(fileURLToPath(new URL("车型映射变动报告.xlsx", outputDir)));
