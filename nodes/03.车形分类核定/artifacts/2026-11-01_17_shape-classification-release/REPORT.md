# 发布报告

- 节点：`shape-classification`（`nodes/03.车形分类核定`）
- 版本：`20261101_17`
- 发布时间：`2026-11-01T13:07:00+08:00`
- 发布原因：上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261101_18`：发布时上游版本（未经运行记录核实），12 个文件。
- `structure-review` `20261101_07`：运行批次实际读取，1 个文件。

## 身份承接

- `车形分类.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `COVER_SHAPE.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。

## 交付物与变更

### `车形分类.csv`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-01_12_regional-shapes/output/车形分类-20261101_12.csv`，未复制。

### `参考尺寸计算.csv`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-01_13_representative-cover-shape/output/COVER_SHAPE-20261101_13.csv`，未复制。

### `cover_shape_summary.json`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-01_13_representative-cover-shape/output/cover_shape_summary-20261101_13.json`，未复制。

### `shape_research_queue.jsonl`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-01_13_representative-cover-shape/output/shape_research_queue-20261101_13.jsonl`，未复制。
