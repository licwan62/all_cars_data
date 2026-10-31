# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261101_04`
- 发布时间：`2026-11-01T02:17:33+08:00`
- 发布原因：交付物变化：积加销量.csv；上游输入变化；规则变化（修改 data/config.json；新增 data/销量依据/allocation_weights.csv, data/销量依据/sales_model_year_cache.csv；删除 data/ru/auto_ru_model_sales_with_match_key.csv）。

## 规则（data/）

- 相对上一版本：修改 data/config.json；新增 data/销量依据/allocation_weights.csv, data/销量依据/sales_model_year_cache.csv；删除 data/ru/auto_ru_model_sales_with_match_key.csv。

## 上游输入依据

- `dimension-library` `20261009_08`：运行批次实际读取，2 个文件。
- `dimension-crawler` `20261101_03`：发布时上游版本（未经运行记录核实），8 个文件。
- 无运行记录可核实的交付物：`RU代理销量.csv`。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。
- `市场潜力.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-19_02_sales-estimation-release/output/原子销量-20261019_02.csv`，未复制。

### `RU代理销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。

### `市场潜力.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-28_01_us-market-potential/output/市场潜力-20261028_01.csv`，未复制。

### `积加销量.csv`

- 本版本新增交付物，共 562 行。
