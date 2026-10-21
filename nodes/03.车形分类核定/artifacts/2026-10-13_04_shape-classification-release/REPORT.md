# 发布报告

- 节点：`shape-classification`（`03.车形分类核定`）
- 版本：`20261013_04`
- 发布时间：`2026-10-13T03:07:12+08:00`
- 发布原因：交付物变化：COVER_SHAPE.csv、cover_shape_summary.json、shape_research_queue.jsonl；规则变化（修改 data/cover_shape/family_cache.csv）。

## 规则（data/）

- 相对上一版本：修改 data/cover_shape/family_cache.csv。

## 交付物与变更

### `车形分类.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv`，未复制。

### `参考尺寸计算.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容已变化：47356 行 → 47356 行；存于 `03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/COVER_SHAPE-20261013_03.csv`。
- 行级差异：新增 0，删除 0，修改 349。
- 变更字段计数：`SHAPE` 33，`SHAPE_ALTERNATES` 7，`SHAPE_METHOD` 73，`SHAPE_SOURCE` 349，`SHAPE_STATUS` 73，`SHAPE_YEAR` 187。
- 修改示例（最多 20 条）：
  - `Audi A8/S8 LWB Sedan 2000-2003 US`：`SHAPE_SOURCE`
  - `Audi A8/S8 LWB Sedan 2004-2010 US`：`SHAPE_SOURCE`
  - `Audi A8/S8 LWB Sedan 2011-2018 US`：`SHAPE_SOURCE`
  - `Audi A8/S8 Sedan 1997-2003 US`：`SHAPE_SOURCE`
  - `Audi A8/S8 Sedan 2004-2010 US`：`SHAPE_SOURCE`
  - `Audi A8/S8 Sedan 2011-2018 US`：`SHAPE_SOURCE`
  - `Audi A8/S8 Sedan 2019-2026 US`：`SHAPE_SOURCE`
  - `Audi Q4 e-tron SUV 2022-2026 US`：`SHAPE`、`SHAPE_SOURCE`
  - `Audi Q4 e-tron Sportback SUV 2022-2026 US`：`SHAPE_ALTERNATES`、`SHAPE_SOURCE`
  - `Audi Q5/SQ5 SUV 2014-2017 US`：`SHAPE_SOURCE`
  - `Audi Q5/SQ5 SUV 2018-2024 US`：`SHAPE`、`SHAPE_SOURCE`
  - `Audi Q5/SQ5 SUV 2025-2026 US`：`SHAPE`、`SHAPE_SOURCE`
  - `Audi Q5/SQ5 Sportback SUV 2021-2024 US`：`SHAPE`、`SHAPE_SOURCE`
  - `Audi Q5/SQ5 Sportback SUV 2026 US`：`SHAPE`、`SHAPE_SOURCE`
  - `Audi Q6/SQ6 e-tron SUV 2025 US`：`SHAPE_SOURCE`
  - `Audi Q6/SQ6 e-tron Sportback SUV 2025 US`：`SHAPE_SOURCE`
  - `Audi Q8 e-tron/SQ8 e-tron SUV 2024-2025 US`：`SHAPE`、`SHAPE_SOURCE`
  - `Audi Q8 e-tron/SQ8 e-tron Sportback SUV 2024-2025 US`：`SHAPE`、`SHAPE_SOURCE`
  - `Audi e-tron/S e-tron SUV SUV 2019-2023 US`：`SHAPE_SOURCE`
  - `Audi e-tron/S e-tron Sportback SUV 2020-2023 US`：`SHAPE_SOURCE`

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/cover_shape_summary-20261013_03.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-13_03_representative-cover-shape/output/shape_research_queue-20261013_03.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
