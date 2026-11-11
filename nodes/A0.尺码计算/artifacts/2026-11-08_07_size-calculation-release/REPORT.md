# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261108_07`
- 发布时间：`2026-11-08T17:03:43+08:00`
- 发布原因：交付物变化：EU/尺码匹配报告.md、RU/尺码匹配报告.md、US/TRIM/TRIM适配器.csv、US/全量/全量表.csv、US/尺码匹配报告.md、US/店铺/店铺全量_HNT.csv、US/店铺/店铺全量_TM.csv、US/店铺/店铺全量_TM_拆分.csv；上游输入变化；规则变化（修改 data/US/TRIM/TrimList_ID迁移.csv）。

## 规则（data/）

- 相对上一版本：修改 data/US/TRIM/TrimList_ID迁移.csv。

## 上游输入依据

- `dimension-library` `20261108_02`：运行批次实际读取，12 个文件。
- `structure-review` `20261108_02`：运行批次实际读取，4 个文件。
- `shape-classification` `20261108_03`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261108_04`：运行批次实际读取，5 个文件。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-08_06_match-report-shape/output/US/尺码匹配报告-20261108_06.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/全量/全量表.csv`

- 内容已变化：6335 行 → 6352 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-08_05_us-market-potential/output/US/全量/全量表-20261108_05.csv`。
- 行级差异：新增 20，删除 3，修改 5。
- 变更字段计数：`车型销量` 5。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。
- 修改示例（最多 20 条）：
  - `Ford Ranger Pickup 1993-1997 Regular 6 US`：`车型销量`
  - `Ford Ranger Pickup 1993-1997 SuperCab 6 US`：`车型销量`
  - `Ford Ranger Pickup 2019-2023 SuperCrew 5 US`：`车型销量`
  - `Ford Ranger Pickup 2024-2026 SuperCrew 5 US`：`车型销量`
  - `Ford Ranger Raptor Pickup 2024-2026 SuperCrew 5 US`：`车型销量`

### `US/店铺/店铺全量_HNT.csv`

- 内容已变化：6335 行 → 6352 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-08_05_us-market-potential/output/US/店铺/店铺全量_HNT-20261108_05.csv`。
- 行级差异：新增 20，删除 3，修改 5。
- 变更字段计数：`车型销量` 5。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。
- 修改示例（最多 20 条）：
  - `Ford Ranger Pickup 1993-1997 Regular 6 US`：`车型销量`
  - `Ford Ranger Pickup 1993-1997 SuperCab 6 US`：`车型销量`
  - `Ford Ranger Pickup 2019-2023 SuperCrew 5 US`：`车型销量`
  - `Ford Ranger Pickup 2024-2026 SuperCrew 5 US`：`车型销量`
  - `Ford Ranger Raptor Pickup 2024-2026 SuperCrew 5 US`：`车型销量`

### `US/店铺/店铺全量_TM.csv`

- 内容已变化：6335 行 → 6352 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-08_05_us-market-potential/output/US/店铺/店铺全量_TM-20261108_05.csv`。
- 行级差异：新增 20，删除 3，修改 5。
- 变更字段计数：`车型销量` 5。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。
- 修改示例（最多 20 条）：
  - `Ford Ranger Pickup 1993-1997 Regular 6 US`：`车型销量`
  - `Ford Ranger Pickup 1993-1997 SuperCab 6 US`：`车型销量`
  - `Ford Ranger Pickup 2019-2023 SuperCrew 5 US`：`车型销量`
  - `Ford Ranger Pickup 2024-2026 SuperCrew 5 US`：`车型销量`
  - `Ford Ranger Raptor Pickup 2024-2026 SuperCrew 5 US`：`车型销量`

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容已变化：6335 行 → 6352 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-08_05_us-market-potential/output/US/店铺/店铺全量_TM_拆分-20261108_05.csv`。
- 行级差异：新增 20，删除 3，修改 5。
- 变更字段计数：`车型销量` 5。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。
- 修改示例（最多 20 条）：
  - `Ford Ranger Pickup 1993-1997 Regular 6 US`：`车型销量`
  - `Ford Ranger Pickup 1993-1997 SuperCab 6 US`：`车型销量`
  - `Ford Ranger Pickup 2019-2023 SuperCrew 5 US`：`车型销量`
  - `Ford Ranger Pickup 2024-2026 SuperCrew 5 US`：`车型销量`
  - `Ford Ranger Raptor Pickup 2024-2026 SuperCrew 5 US`：`车型销量`

### `US/TRIM/TRIM适配器.csv`

- 内容已变化：23258 行 → 23258 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-08_01_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261108_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/尺码规则-20261015_01.json`，未复制。

### `US/店铺货架.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/店铺货架-20261015_01.json`，未复制。

### `US/新旧尺码对应.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_02_match-report-shape/output/US/新旧尺码对应-20261028_02.csv`，未复制。

### `EU/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-13_27_match-report-shape/output/EU/尺码匹配报告-20261013_27.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `EU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv`，未复制。

### `EU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/EU/尺码规则-20261015_01.json`，未复制。

### `RU/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-01_06_match-report-shape/output/RU/尺码匹配报告-20261101_06.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `RU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_04_full-table-cover-shape/output/RU/全量/全量表-20261101_04.csv`，未复制。

### `RU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码规则-20261026_02.json`，未复制。
