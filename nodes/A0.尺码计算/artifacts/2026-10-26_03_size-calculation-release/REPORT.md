# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261026_03`
- 发布时间：`2026-10-26T16:47:05+08:00`
- 发布原因：交付物变化：RU/全量/全量表.csv、RU/尺码匹配报告.md、RU/尺码规则.json；规则变化（修改 data/RU/规则/1023-亚马逊尺码更新.csv）。

## 规则（data/）

- 相对上一版本：修改 data/RU/规则/1023-亚马逊尺码更新.csv。

## 上游输入依据

- `dimension-library` `20261009_08`：运行批次实际读取，7 个文件。
- `structure-review` `20261019_02`：运行批次实际读取，4 个文件。
- `shape-classification` `20261019_04`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261019_02`：运行批次实际读取，2 个文件。
- 无运行记录可核实的交付物：`RU/全量/全量表.csv`。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_08_match-report-shape/output/US/尺码匹配报告-20261019_08.md`，未复制。

### `US/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_07_full-table-cover-shape/output/US/全量/全量表-20261019_07.csv`，未复制。

### `US/店铺/店铺全量_HNT.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_07_full-table-cover-shape/output/US/店铺/店铺全量_HNT-20261019_07.csv`，未复制。

### `US/店铺/店铺全量_TM.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_07_full-table-cover-shape/output/US/店铺/店铺全量_TM-20261019_07.csv`，未复制。

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_07_full-table-cover-shape/output/US/店铺/店铺全量_TM_拆分-20261019_07.csv`，未复制。

### `US/TRIM/TRIM适配器.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_06_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261019_06.csv`，未复制。

### `US/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/尺码规则-20261015_01.json`，未复制。

### `US/店铺货架.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/店铺货架-20261015_01.json`，未复制。

### `US/新旧尺码对应.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/新旧尺码对应-20261015_01.csv`，未复制。

### `EU/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/EU/尺码匹配报告-20261013_18.md`，未复制。

### `EU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv`，未复制。

### `EU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/EU/尺码规则-20261015_01.json`，未复制。

### `RU/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码匹配报告-20261026_02.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `RU/全量/全量表.csv`

- 内容已变化：13617 行 → 13617 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-26_03_size-calculation-release/output/RU/全量/全量表-20261026_03.csv`。
- 行级差异：新增 0，删除 0，修改 542。
- 变更字段计数：`发货尺码` 250，`自动尺码` 542，`规则ID` 542。
- 修改示例（最多 20 条）：
  - `Aistaland GT7 Wagon 2026-2026 RU`：`自动尺码`、`规则ID`
  - `Alpina B5 Wagon 2005-2007 RU`：`自动尺码`、`规则ID`
  - `Alpina B5 Wagon 2007-2010 RU`：`自动尺码`、`规则ID`
  - `Alpina B5 Wagon 2010-2013 RU`：`自动尺码`、`规则ID`
  - `Alpina B5 Wagon 2013-2017 RU`：`自动尺码`、`规则ID`
  - `Alpina B5 Wagon 2017-2020 RU`：`自动尺码`、`规则ID`
  - `Alpina B5 Wagon 2020-2024 RU`：`自动尺码`、`规则ID`
  - `Alpina D5 Wagon 2011-2013 RU`：`自动尺码`、`规则ID`
  - `Alpina D5 Wagon 2013-2017 RU`：`自动尺码`、`规则ID`
  - `Alpina D5 Wagon 2017-2020 RU`：`自动尺码`、`规则ID`
  - `Alpina D5 Wagon 2020-2024 RU`：`自动尺码`、`规则ID`
  - `Aston Martin Virage Wagon 1988-2000 RU`：`自动尺码`、`规则ID`
  - `Audi A6 Wagon 2004-2008 RU`：`自动尺码`、`规则ID`
  - `Audi A6 Wagon 2008-2011 RU`：`自动尺码`、`规则ID`
  - `Audi A6 Wagon 2011-2014 RU`：`自动尺码`、`规则ID`
  - `Audi A6 Wagon 2014-2018 RU`：`自动尺码`、`规则ID`
  - `Audi A6 Wagon 2018-2023 RU`：`自动尺码`、`规则ID`
  - `Audi A6 Wagon 2022-2025 RU`：`自动尺码`、`规则ID`
  - `Audi A6 Wagon 2025-2026 RU`：`自动尺码`、`规则ID`
  - `Audi A6 allroad Wagon 2006-2008 RU`：`自动尺码`、`规则ID`

### `RU/尺码规则.json`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码规则-20261026_02.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
