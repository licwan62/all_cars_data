# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261102_04`
- 发布时间：`2026-11-02T09:05:45+08:00`
- 发布原因：交付物变化：原子销量.csv、原子销量待核.csv、市场潜力.csv；上游输入变化；规则变化（）。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_02`：运行批次实际读取，4 个文件。
- `dimension-crawler` `20261101_03`：运行批次实际读取，1 个文件。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。
- `市场潜力.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容已变化：15315 行 → 15580 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_01_atomic-sales/output/原子销量-20261102_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `原子销量待核.csv`

- 内容已变化：94 行 → 339 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_01_atomic-sales/output/原子销量待核-20261102_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `RU代理销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。

### `市场潜力.csv`

- 内容已变化：4475 行 → 4740 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_03_us-market-potential/output/市场潜力-20261102_03.csv`。
- 行级差异：新增 265，删除 0，修改 10。
- 变更字段计数：`市场潜力` 10，`销量潜力调整` 10。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。
- 修改示例（最多 20 条）：
  - `Cadillac Lyriq Lyriq-V SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2023-2025 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `MINI Countryman JCW SUV 2016 US`：`市场潜力`、`销量潜力调整`
  - `MINI Countryman JCW SUV 2018 US`：`市场潜力`、`销量潜力调整`
  - `MINI Countryman SUV 2011-2015 US`：`市场潜力`、`销量潜力调整`
  - `MINI Countryman SUV 2017-2024 US`：`市场潜力`、`销量潜力调整`
  - `MINI Countryman SUV 2025-2026 US`：`市场潜力`、`销量潜力调整`
  - `Volvo XC40 SUV 2019 US`：`市场潜力`、`销量潜力调整`
  - `Volvo XC40 SUV 2020-2025 US`：`市场潜力`、`销量潜力调整`

### `积加销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-28_01_us-market-potential/rules/data/商业潜力调整/积加销量.csv`，未复制。
