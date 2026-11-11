# 发布报告

- 节点：`shape-classification`（`nodes/03.车形分类核定`）
- 版本：`20261108_03`
- 发布时间：`2026-11-08T17:02:45+08:00`
- 发布原因：交付物变化：COVER_SHAPE.csv、cover_shape_summary.json、shape_research_queue.jsonl、参考尺寸计算.csv、车形分类.csv；上游输入变化；规则变化（修改 data/US车形补充核定.csv）。

## 规则（data/）

- 相对上一版本：修改 data/US车形补充核定.csv。

## 上游输入依据

- `dimension-library` `20261108_02`：发布时上游版本（未经运行记录核实），12 个文件。
- `structure-review` `20261108_02`：运行批次实际读取，1 个文件。

## 身份承接

- `车形分类.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `COVER_SHAPE.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。

## 交付物与变更

### `车形分类.csv`

- 内容已变化：49313 行 → 49330 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-08_01_regional-shapes/output/车形分类-20261108_01.csv`。
- 行级差异：新增 20，删除 3，修改 0。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。

### `参考尺寸计算.csv`

- 内容已变化：17 行 → 17 行；存于 `nodes/03.车形分类核定/artifacts/2026-10-09_02_shape-classification-release/output/参考尺寸计算-20261009_02.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `COVER_SHAPE.csv`

- 内容已变化：49313 行 → 49330 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-08_02_representative-cover-shape/output/COVER_SHAPE-20261108_02.csv`。
- 行级差异：新增 20，删除 3，修改 0。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-08_02_representative-cover-shape/output/cover_shape_summary-20261108_02.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-08_02_representative-cover-shape/output/shape_research_queue-20261108_02.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
