# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261108_04`
- 发布时间：`2026-11-08T17:02:29+08:00`
- 发布原因：交付物变化：原子销量.csv、原子销量待核.csv、市场潜力.csv、积加销量.csv；上游输入变化；规则变化（修改 data/销量依据/allocation_weights.csv, data/销量依据/model_year_sales_holdouts.csv）。

## 规则（data/）

- 相对上一版本：修改 data/销量依据/allocation_weights.csv, data/销量依据/model_year_sales_holdouts.csv。

## 上游输入依据

- `dimension-library` `20261108_02`：运行批次实际读取，4 个文件。
- `dimension-crawler` `20261102_01`：运行批次实际读取，1 个文件。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。
- `市场潜力.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容已变化：17175 行 → 17175 行；存于 `nodes/02.销量评估/artifacts/2026-11-08_01_atomic-sales/output/原子销量-20261108_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `原子销量待核.csv`

- 内容已变化：1925 行 → 1967 行；存于 `nodes/02.销量评估/artifacts/2026-11-08_01_atomic-sales/output/原子销量待核-20261108_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `RU代理销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。

### `市场潜力.csv`

- 内容已变化：6335 行 → 6352 行；存于 `nodes/02.销量评估/artifacts/2026-11-08_03_us-market-potential/output/市场潜力-20261108_03.csv`。
- 行级差异：新增 20，删除 3，修改 0。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。

### `积加销量.csv`

- 内容已变化：562 行 → 562 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/input/积加销量.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。
