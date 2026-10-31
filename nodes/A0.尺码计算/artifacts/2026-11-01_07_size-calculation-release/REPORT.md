# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261101_07`
- 发布时间：`2026-11-01T02:27:57+08:00`
- 发布原因：交付物变化：RU/全量/全量表.csv、RU/尺码匹配报告.md；上游输入变化；规则变化（新增 data/参考/历史全域新旧尺码对应.csv）。

## 规则（data/）

- 相对上一版本：新增 data/参考/历史全域新旧尺码对应.csv。

## 上游输入依据

- `dimension-library` `20261101_02`：运行批次实际读取，7 个文件。
- `structure-review` `20261019_02`：运行批次实际读取，4 个文件。
- `shape-classification` `20261101_03`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261101_04`：运行批次实际读取，4 个文件。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_02_match-report-shape/output/US/尺码匹配报告-20261028_02.md`，未复制。

### `US/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/全量/全量表-20261028_01.csv`，未复制。

### `US/店铺/店铺全量_HNT.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/店铺/店铺全量_HNT-20261028_01.csv`，未复制。

### `US/店铺/店铺全量_TM.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/店铺/店铺全量_TM-20261028_01.csv`，未复制。

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/店铺/店铺全量_TM_拆分-20261028_01.csv`，未复制。

### `US/TRIM/TRIM适配器.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_06_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261019_06.csv`，未复制。

### `US/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/尺码规则-20261015_01.json`，未复制。

### `US/店铺货架.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/店铺货架-20261015_01.json`，未复制。

### `US/新旧尺码对应.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_02_match-report-shape/output/US/新旧尺码对应-20261028_02.csv`，未复制。

### `EU/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/EU/尺码匹配报告-20261013_18.md`，未复制。

### `EU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv`，未复制。

### `EU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/EU/尺码规则-20261015_01.json`，未复制。

### `RU/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-01_06_match-report-shape/output/RU/尺码匹配报告-20261101_06.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `RU/全量/全量表.csv`

- 内容已变化：13617 行 → 13617 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-01_04_full-table-cover-shape/output/RU/全量/全量表-20261101_04.csv`。
- 行级差异：新增 0，删除 0，修改 13617。
- 变更字段计数：`SHAPE` 13617，`车形` 13617。
- 修改示例（最多 20 条）：
  - `212 Explorer 01 Pickup 2026-2026 Double RU`：`SHAPE`、`车形`
  - `212 T01 SUV 2024-2026 RU`：`SHAPE`、`车形`
  - `212 T10 SUV 2026-2026 RU`：`SHAPE`、`车形`
  - `AC 378 GT Zagato Coupe 2012-2012 RU`：`SHAPE`、`车形`
  - `AC Ace Roadster 1992-2000 RU`：`SHAPE`、`车形`
  - `AC Aceca Coupe 1998-2000 RU`：`SHAPE`、`车形`
  - `AC Cobra GT Coupe 2023-2026 RU`：`SHAPE`、`车形`
  - `AC Cobra GT Roadster 2023-2026 RU`：`SHAPE`、`车形`
  - `AC Cobra Roadster 1965-1967 RU`：`SHAPE`、`车形`
  - `AC Cobra Roadster 1990-2001 RU`：`SHAPE`、`车形`
  - `AC Cobra Roadster 1999-2007 RU`：`SHAPE`、`车形`
  - `AC Cobra Roadster 2013-2015 RU`：`SHAPE`、`车形`
  - `AM General HMMWV (Humvee) SUV 1984-2006 RU`：`SHAPE`、`车形`
  - `AMC Eagle Hatchback 1979-1987 RU`：`SHAPE`、`车形`
  - `AMC Eagle Sedan 1979-1987 RU`：`SHAPE`、`车形`
  - `AMC Eagle Wagon 1979-1987 RU`：`SHAPE`、`车形`
  - `AMC Gremlin Hatchback 1970-1978 RU`：`SHAPE`、`车形`
  - `AMC Hornet Hatchback 1974-1975 RU`：`SHAPE`、`车形`
  - `AMC Matador Coupe 1974-1978 RU`：`SHAPE`、`车形`
  - `AMC Rambler Ambassador Sedan 1965-1972 RU`：`SHAPE`、`车形`

### `RU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码规则-20261026_02.json`，未复制。
