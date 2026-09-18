import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Workbook } from "@oai/artifact-tool";

const here = path.dirname(fileURLToPath(import.meta.url));
const outputDir = path.resolve(here, "..", "..", "output");

for (const [region, lastRow] of [["EU", 29708], ["RU", 13851]]) {
  const csvPath = path.join(outputDir, `${region}尺寸库.csv`);
  const csvText = await fs.readFile(csvPath, "utf8");
  const workbook = await Workbook.fromCSV(csvText, { sheetName: region });
  const sample = await workbook.inspect({
    kind: "table",
    sheetId: region,
    range: "A1:G6",
    include: "values",
    tableMaxRows: 6,
    tableMaxCols: 7,
    maxChars: 2500,
  });
  const legacyDoor = await workbook.inspect({
    kind: "match",
    sheetId: region,
    range: `G1:G${lastRow}`,
    searchTerm: "-door",
    options: { useRegex: false, maxResults: 20 },
    summary: `${region} legacy door syntax`,
  });
  console.log(JSON.stringify({ region, sample: sample.ndjson, legacyDoor: legacyDoor.ndjson }));
}
