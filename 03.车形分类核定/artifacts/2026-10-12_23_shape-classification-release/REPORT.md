# 发布报告

- 节点：`shape-classification`（`03.车形分类核定`）
- 版本：`20261012_23`
- 发布时间：`2026-10-12T20:36:39+08:00`
- 发布原因：交付物变化：COVER_SHAPE.csv、cover_shape_summary.json、shape_research_queue.jsonl；规则变化（修改 data/cover_shape/evidence.jsonl）。

## 规则（data/）

- 相对上一版本：修改 data/cover_shape/evidence.jsonl。

## 交付物与变更

### `车形分类.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv`，未复制。

### `参考尺寸计算.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容已变化：47356 行 → 47356 行；存于 `03.车形分类核定/artifacts/2026-10-12_22_shape-queue-research/output/COVER_SHAPE-20261012_22.csv`。
- 行级差异：新增 0，删除 0，修改 5。
- 变更字段计数：`SHAPE` 2，`SHAPE_ALTERNATES` 4，`SHAPE_METHOD` 5，`SHAPE_SOURCE` 5，`SHAPE_YEAR` 4。
- 修改示例（最多 20 条）：
  - `Acura Integra Hatchback 2023-2026 US`：`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`
  - `Honda Accord Sedan 2023-2026 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`
  - `Nissan Z Coupe 2023-2026 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`
  - `Toyota C-HR Crossover 2020-2022 US`：`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`
  - `Toyota Land Cruiser SUV 2024-2026 US`：`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-12_22_shape-queue-research/output/cover_shape_summary-20261012_22.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-12_22_shape-queue-research/output/shape_research_queue-20261012_22.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
