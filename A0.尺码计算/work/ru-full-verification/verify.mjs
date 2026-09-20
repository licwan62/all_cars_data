import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Workbook } from "@oai/artifact-tool";

const here = path.dirname(fileURLToPath(import.meta.url));
const csvPath = path.resolve(here, "..", "..", "output", "RU全尺码全量.csv");
const workbook = await Workbook.fromCSV(await fs.readFile(csvPath, "utf8"), { sheetName: "RU" });
const sample = await workbook.inspect({
  kind: "table",
  sheetId: "RU",
  range: "A1:AB6",
  include: "values",
  tableMaxRows: 6,
  tableMaxCols: 28,
  maxChars: 7000,
});
const errors = await workbook.inspect({
  kind: "match",
  sheetId: "RU",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "RU output error scan",
});
console.log(sample.ndjson);
console.log(errors.ndjson);
