# 发布报告

- 节点：`shape-classification`（`nodes/03.车形分类核定`）
- 版本：`20261102_15`
- 发布时间：`2026-11-02T18:42:05+08:00`
- 发布原因：上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_15`：发布时上游版本（未经运行记录核实），12 个文件。
- `structure-review` `20261102_10`：运行批次实际读取，1 个文件。

## 身份承接

- `车形分类.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `COVER_SHAPE.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。

## 交付物与变更

### `车形分类.csv`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-02_10_regional-shapes/output/车形分类-20261102_10.csv`，未复制。

### `参考尺寸计算.csv`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-02_01_regional-shapes/output/参考尺寸计算-20261102_01.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-02_11_representative-cover-shape/output/COVER_SHAPE-20261102_11.csv`，未复制。

### `cover_shape_summary.json`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-02_11_representative-cover-shape/output/cover_shape_summary-20261102_11.json`，未复制。

### `shape_research_queue.jsonl`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-02_11_representative-cover-shape/output/shape_research_queue-20261102_11.jsonl`，未复制。
