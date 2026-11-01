# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261101_19`
- 发布时间：`2026-11-01T12:34:58+08:00`
- 发布原因：交付物变化：原子销量.csv、原子销量待核.csv、市场潜力.csv；上游输入变化；规则变化（修改 data/config.json；新增 data/销量依据/model_year_sales_holdouts.csv）。

## 规则（data/）

- 相对上一版本：修改 data/config.json；新增 data/销量依据/model_year_sales_holdouts.csv。

## 上游输入依据

- `dimension-library` `20261101_04`：运行批次实际读取，4 个文件。
- `dimension-crawler` `20261101_03`：运行批次实际读取，1 个文件。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。
- `市场潜力.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容已变化：15223 行 → 15311 行；存于 `nodes/02.销量评估/artifacts/2026-11-01_16_atomic-sales/output/原子销量-20261101_16.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `原子销量待核.csv`

- 本版本新增交付物，共 90 行。

### `RU代理销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。

### `市场潜力.csv`

- 内容已变化：4383 行 → 4471 行；存于 `nodes/02.销量评估/artifacts/2026-11-01_18_us-market-potential/output/市场潜力-20261101_18.csv`。
- 行级差异：新增 88，删除 0，修改 0。
- 新增示例（最多 10 条）：`Acura RL Sedan 2005 US`；`Acura RL Sedan 2006 US`；`Acura RL Sedan 2007 US`；`Acura RL Sedan 2008 US`；`Acura RL Sedan 2009 US`；`Acura RL Sedan 2010 US`；`Acura RL Sedan 2011 US`；`Acura RL Sedan 2012 US`；`Audi 90 Sedan 1990 US`；`Audi 90 Sedan 1993 US`。

### `积加销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-28_01_us-market-potential/rules/data/商业潜力调整/积加销量.csv`，未复制。
