# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261101_27`
- 发布时间：`2026-11-01T12:53:16+08:00`
- 发布原因：交付物变化：原子销量.csv、原子销量待核.csv、市场潜力.csv；规则变化（修改 data/销量依据/model_year_sales_holdouts.csv）。

## 规则（data/）

- 相对上一版本：修改 data/销量依据/model_year_sales_holdouts.csv。

## 上游输入依据

- `dimension-library` `20261101_16`：运行批次实际读取，4 个文件。
- `dimension-crawler` `20261101_03`：运行批次实际读取，1 个文件。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。
- `市场潜力.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容已变化：15314 行 → 15314 行；存于 `nodes/02.销量评估/artifacts/2026-11-01_24_atomic-sales/output/原子销量-20261101_24.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `原子销量待核.csv`

- 内容已变化：90 行 → 93 行；存于 `nodes/02.销量评估/artifacts/2026-11-01_24_atomic-sales/output/原子销量待核-20261101_24.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `RU代理销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。

### `市场潜力.csv`

- 内容已变化：4474 行 → 4474 行；存于 `nodes/02.销量评估/artifacts/2026-11-01_26_us-market-potential/output/市场潜力-20261101_26.csv`。
- 行级差异：新增 0，删除 0，修改 3。
- 变更字段计数：`市场潜力` 3。
- 修改示例（最多 20 条）：
  - `Mazda 2 Hatchback 2016 US`：`市场潜力`
  - `Mazda 2 Hatchback 2017 US`：`市场潜力`
  - `Mazda 2 Hatchback 2018 US`：`市场潜力`

### `积加销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-28_01_us-market-potential/rules/data/商业潜力调整/积加销量.csv`，未复制。
