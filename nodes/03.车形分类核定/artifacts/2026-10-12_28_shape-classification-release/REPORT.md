# 发布报告

- 节点：`shape-classification`（`03.车形分类核定`）
- 版本：`20261012_28`
- 发布时间：`2026-10-12T21:07:19+08:00`
- 发布原因：交付物变化：cover_shape_summary.json、shape_research_queue.jsonl；规则变化（修改 data/cover_shape/README.md, data/cover_shape/research_queue.yaml；新增 data/cover_shape/family_cache.csv）。

## 规则（data/）

- 相对上一版本：修改 data/cover_shape/README.md, data/cover_shape/research_queue.yaml；新增 data/cover_shape/family_cache.csv。

## 交付物与变更

### `车形分类.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv`，未复制。

### `参考尺寸计算.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-12_22_shape-queue-research/output/COVER_SHAPE-20261012_22.csv`，未复制。

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-12_27_representative-cover-shape/output/cover_shape_summary-20261012_27.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-12_27_representative-cover-shape/output/shape_research_queue-20261012_27.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
