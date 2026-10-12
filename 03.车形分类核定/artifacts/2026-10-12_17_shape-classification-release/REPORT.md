# 发布报告

- 节点：`shape-classification`（`03.车形分类核定`）
- 版本：`20261012_17`
- 发布时间：`2026-10-12T19:19:12+08:00`
- 发布原因：交付物变化：cover_shape_summary.json、shape_research_queue.jsonl；规则变化（新增 data/cover_shape/research_queue.yaml）；pending/发布说明变化。

## 规则（data/）

- 相对上一版本：新增 data/cover_shape/research_queue.yaml。

## 交付物与变更

### `车形分类.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv`，未复制。

### `参考尺寸计算.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-12_14_representative-cover-shape/output/COVER_SHAPE-20261012_14.csv`，未复制。

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-12_16_representative-cover-shape/output/cover_shape_summary-20261012_16.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 本版本新增交付物，共 None 行。
