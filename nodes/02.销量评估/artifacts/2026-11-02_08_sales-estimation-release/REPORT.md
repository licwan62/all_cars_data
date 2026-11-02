# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261102_08`
- 发布时间：`2026-11-02T12:38:27+08:00`
- 发布原因：交付物变化：原子销量.csv、原子销量待核.csv、市场潜力.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_04`：运行批次实际读取，4 个文件。
- `dimension-crawler` `20261102_01`：运行批次实际读取，1 个文件。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。
- `市场潜力.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容已变化：15580 行 → 15650 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_05_atomic-sales/output/原子销量-20261102_05.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `原子销量待核.csv`

- 内容已变化：339 行 → 405 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_05_atomic-sales/output/原子销量待核-20261102_05.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `RU代理销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。

### `市场潜力.csv`

- 内容已变化：4740 行 → 4810 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_07_us-market-potential/output/市场潜力-20261102_07.csv`。
- 行级差异：新增 70，删除 0，修改 4。
- 变更字段计数：`市场潜力` 4，`销量潜力调整` 4。
- 新增示例（最多 10 条）：`Buick Terraza MPV 2005 US`；`Buick Terraza MPV 2006 US`；`Buick Terraza MPV 2007 US`；`Buick Terraza MPV 2008 US`；`Hummer H3 SUV 2006 US`；`Hummer H3 SUV 2007 US`；`Hummer H3 SUV 2008 US`；`Hummer H3 SUV 2009 US`；`Hummer H3 SUV 2010 US`；`Isuzu Ascender SUV 2003 US`。
- 修改示例（最多 20 条）：
  - `Nissan Quest MPV 2012 US`：`市场潜力`、`销量潜力调整`
  - `Nissan Quest MPV 2013 US`：`市场潜力`、`销量潜力调整`
  - `Nissan Quest MPV 2014 US`：`市场潜力`、`销量潜力调整`
  - `Nissan Quest MPV 2015 US`：`市场潜力`、`销量潜力调整`

### `积加销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-28_01_us-market-potential/rules/data/商业潜力调整/积加销量.csv`，未复制。
