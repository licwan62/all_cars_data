# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261028_02`
- 发布时间：`2026-10-28T15:37:37+08:00`
- 发布原因：交付物变化：市场潜力.csv；上游输入变化；规则变化（新增 data/商业潜力调整/README.md, data/商业潜力调整/参数.json, data/商业潜力调整/来源.json, data/商业潜力调整/积加销量.csv, data/商业潜力调整/竞品车罩销量统计表.csv）；pending/发布说明变化。

## 规则（data/）

- 相对上一版本：新增 data/商业潜力调整/README.md, data/商业潜力调整/参数.json, data/商业潜力调整/来源.json, data/商业潜力调整/积加销量.csv, data/商业潜力调整/竞品车罩销量统计表.csv。

## 上游输入依据

- `dimension-library` `20261009_08`：运行批次实际读取，1 个文件。
- 无运行记录可核实的交付物：`原子销量.csv`、`RU代理销量.csv`。

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

- 本版本新增交付物，共 4383 行。
