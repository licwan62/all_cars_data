# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261101_35`
- 发布时间：`2026-11-01T13:07:50+08:00`
- 发布原因：上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261101_18`：运行批次实际读取，12 个文件。
- `structure-review` `20261101_07`：运行批次实际读取，4 个文件。
- `shape-classification` `20261101_17`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261101_27`：运行批次实际读取，5 个文件。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_27_match-report-shape/output/US/尺码匹配报告-20261101_27.md`，未复制。

### `US/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_26_us-market-potential/output/US/全量/全量表-20261101_26.csv`，未复制。

### `US/店铺/店铺全量_HNT.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_26_us-market-potential/output/US/店铺/店铺全量_HNT-20261101_26.csv`，未复制。

### `US/店铺/店铺全量_TM.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_26_us-market-potential/output/US/店铺/店铺全量_TM-20261101_26.csv`，未复制。

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_26_us-market-potential/output/US/店铺/店铺全量_TM_拆分-20261101_26.csv`，未复制。

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

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_06_match-report-shape/output/RU/尺码匹配报告-20261101_06.md`，未复制。

### `RU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_04_full-table-cover-shape/output/RU/全量/全量表-20261101_04.csv`，未复制。

### `RU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码规则-20261026_02.json`，未复制。
