# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261101_08`
- 发布时间：`2026-11-01T02:33:47+08:00`
- 发布原因：规则变化（新增 data/参考/历史商业潜力调整/10-23-积加销量.csv, data/参考/历史商业潜力调整/竞品车罩销量统计表.csv）。

## 规则（data/）

- 相对上一版本：新增 data/参考/历史商业潜力调整/10-23-积加销量.csv, data/参考/历史商业潜力调整/竞品车罩销量统计表.csv。

## 上游输入依据

- `dimension-library` `20261101_02`：运行批次实际读取，2 个文件。
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

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-28_01_us-market-potential/rules/data/商业潜力调整/积加销量.csv`，未复制。
