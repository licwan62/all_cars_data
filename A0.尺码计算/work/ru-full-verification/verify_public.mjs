import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Workbook } from "@oai/artifact-tool";

const here = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.resolve(here, "..", "..", "..", "public", "ru_data");
const files = [
  ["00_RU尺寸库.csv", "Dimensions", "A1:P5"],
  ["02_RU全量.csv", "Full", "A1:AB5"],
  ["03_RU尺码匹配规则.csv", "Rules", "A1:G8"],
];
for (const [name, sheetName, range] of files) {
  const workbook = await Workbook.fromCSV(await fs.readFile(path.join(publicDir, name), "utf8"), { sheetName });
  const sample = await workbook.inspect({
    kind: "table", sheetId: sheetName, range, include: "values",
    tableMaxRows: 8, tableMaxCols: 28, maxChars: 6000,
  });
  const errors = await workbook.inspect({
    kind: "match", sheetId: sheetName,
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
    options: { useRegex: true, maxResults: 100 }, summary: `${name} error scan`,
  });
  console.log(JSON.stringify({ name, sample: sample.ndjson, errors: errors.ndjson }));
}
