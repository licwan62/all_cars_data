# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261101_28`
- 发布时间：`2026-11-01T12:54:21+08:00`
- 发布原因：交付物变化：US/全量/全量表.csv、US/尺码匹配报告.md、US/店铺/店铺全量_HNT.csv、US/店铺/店铺全量_TM.csv、US/店铺/店铺全量_TM_拆分.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261101_16`：运行批次实际读取，12 个文件。
- `structure-review` `20261101_07`：运行批次实际读取，4 个文件。
- `shape-classification` `20261101_14`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261101_27`：运行批次实际读取，5 个文件。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-01_27_match-report-shape/output/US/尺码匹配报告-20261101_27.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/全量/全量表.csv`

- 内容已变化：4474 行 → 4474 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-01_26_us-market-potential/output/US/全量/全量表-20261101_26.csv`。
- 行级差异：新增 0，删除 0，修改 4。
- 变更字段计数：`尺寸组销量` 3，`市场潜力` 3，`车型销量` 4。
- 修改示例（最多 20 条）：
  - `Mazda 2 Hatchback 2011-2014 US`：`车型销量`
  - `Mazda 2 Hatchback 2016 US`：`尺寸组销量`、`市场潜力`、`车型销量`
  - `Mazda 2 Hatchback 2017 US`：`尺寸组销量`、`市场潜力`、`车型销量`
  - `Mazda 2 Hatchback 2018 US`：`尺寸组销量`、`市场潜力`、`车型销量`

### `US/店铺/店铺全量_HNT.csv`

- 内容已变化：4474 行 → 4474 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-01_26_us-market-potential/output/US/店铺/店铺全量_HNT-20261101_26.csv`。
- 行级差异：新增 0，删除 0，修改 4。
- 变更字段计数：`尺寸组销量` 3，`市场潜力` 3，`车型销量` 4。
- 修改示例（最多 20 条）：
  - `Mazda 2 Hatchback 2011-2014 US`：`车型销量`
  - `Mazda 2 Hatchback 2016 US`：`尺寸组销量`、`市场潜力`、`车型销量`
  - `Mazda 2 Hatchback 2017 US`：`尺寸组销量`、`市场潜力`、`车型销量`
  - `Mazda 2 Hatchback 2018 US`：`尺寸组销量`、`市场潜力`、`车型销量`

### `US/店铺/店铺全量_TM.csv`

- 内容已变化：4474 行 → 4474 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-01_26_us-market-potential/output/US/店铺/店铺全量_TM-20261101_26.csv`。
- 行级差异：新增 0，删除 0，修改 4。
- 变更字段计数：`尺寸组销量` 3，`市场潜力` 3，`车型销量` 4。
- 修改示例（最多 20 条）：
  - `Mazda 2 Hatchback 2011-2014 US`：`车型销量`
  - `Mazda 2 Hatchback 2016 US`：`尺寸组销量`、`市场潜力`、`车型销量`
  - `Mazda 2 Hatchback 2017 US`：`尺寸组销量`、`市场潜力`、`车型销量`
  - `Mazda 2 Hatchback 2018 US`：`尺寸组销量`、`市场潜力`、`车型销量`

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容已变化：4474 行 → 4474 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-01_26_us-market-potential/output/US/店铺/店铺全量_TM_拆分-20261101_26.csv`。
- 行级差异：新增 0，删除 0，修改 4。
- 变更字段计数：`尺寸组销量` 3，`市场潜力` 3，`车型销量` 4。
- 修改示例（最多 20 条）：
  - `Mazda 2 Hatchback 2011-2014 US`：`车型销量`
  - `Mazda 2 Hatchback 2016 US`：`尺寸组销量`、`市场潜力`、`车型销量`
  - `Mazda 2 Hatchback 2017 US`：`尺寸组销量`、`市场潜力`、`车型销量`
  - `Mazda 2 Hatchback 2018 US`：`尺寸组销量`、`市场潜力`、`车型销量`

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
