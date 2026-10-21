# 发布报告

- 节点：`sales-estimation`（`02.销量评估`）
- 版本：`20261019_02`
- 发布时间：`2026-10-19T02:04:36+08:00`
- 发布原因：交付物变化：原子销量.csv。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261009_08`：发布时上游版本（未经运行记录核实），7 个文件。
- 无运行记录可核实的交付物：`原子销量.csv`、`RU代理销量.csv`。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容已变化：15210 行 → 15223 行；存于 `02.销量评估/artifacts/2026-10-19_02_sales-estimation-release/output/原子销量-20261019_02.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `RU代理销量.csv`

- 内容未变化；引用 `02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。
