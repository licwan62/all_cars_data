# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261102_12`
- 发布时间：`2026-11-02T12:43:45+08:00`
- 发布原因：交付物变化：原子销量.csv、原子销量待核.csv、市场潜力.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_10`：运行批次实际读取，4 个文件。
- `dimension-crawler` `20261102_01`：运行批次实际读取，1 个文件。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。
- `市场潜力.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容已变化：15650 行 → 15677 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_09_atomic-sales/output/原子销量-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `原子销量待核.csv`

- 内容已变化：405 行 → 432 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_09_atomic-sales/output/原子销量待核-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `RU代理销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。

### `市场潜力.csv`

- 内容已变化：4810 行 → 4837 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_11_us-market-potential/output/市场潜力-20261102_11.csv`。
- 行级差异：新增 27，删除 0，修改 0。
- 新增示例（最多 10 条）：`BYD e6 SUV 2012 US`；`BYD e6 SUV 2013 US`；`BYD e6 SUV 2014 US`；`BYD e6 SUV 2016 US`；`BYD e6 SUV 2017 US`；`BYD e6 SUV 2018 US`；`BYD e6 SUV 2020 US`；`Daewoo Lanos Sedan 2000 US`；`Daewoo Lanos Sedan 2001 US`；`Daewoo Lanos Sedan 2002 US`。

### `积加销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-28_01_us-market-potential/rules/data/商业潜力调整/积加销量.csv`，未复制。
