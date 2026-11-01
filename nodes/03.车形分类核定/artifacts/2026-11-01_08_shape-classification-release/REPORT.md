# 发布报告

- 节点：`shape-classification`（`nodes/03.车形分类核定`）
- 版本：`20261101_08`
- 发布时间：`2026-11-01T12:36:00+08:00`
- 发布原因：交付物变化：COVER_SHAPE.csv、cover_shape_summary.json、shape_research_queue.jsonl、车形分类.csv；上游输入变化；规则变化（修改 data/US车形补充核定.csv）。

## 规则（data/）

- 相对上一版本：修改 data/US车形补充核定.csv。

## 上游输入依据

- `dimension-library` `20261101_12`：发布时上游版本（未经运行记录核实），12 个文件。
- `structure-review` `20261101_05`：运行批次实际读取，1 个文件。

## 身份承接

- `车形分类.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `COVER_SHAPE.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。

## 交付物与变更

### `车形分类.csv`

- 内容已变化：47361 行 → 47449 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-01_06_regional-shapes/output/车形分类-20261101_06.csv`。
- 行级差异：新增 88，删除 0，修改 0。
- 新增示例（最多 10 条）：`Acura RL Sedan 2005 US`；`Acura RL Sedan 2006 US`；`Acura RL Sedan 2007 US`；`Acura RL Sedan 2008 US`；`Acura RL Sedan 2009 US`；`Acura RL Sedan 2010 US`；`Acura RL Sedan 2011 US`；`Acura RL Sedan 2012 US`；`Audi 90 Sedan 1990 US`；`Audi 90 Sedan 1993 US`。

### `参考尺寸计算.csv`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容已变化：47361 行 → 47449 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-01_07_representative-cover-shape/output/COVER_SHAPE-20261101_07.csv`。
- 行级差异：新增 88，删除 0，修改 0。
- 新增示例（最多 10 条）：`Acura RL Sedan 2005 US`；`Acura RL Sedan 2006 US`；`Acura RL Sedan 2007 US`；`Acura RL Sedan 2008 US`；`Acura RL Sedan 2009 US`；`Acura RL Sedan 2010 US`；`Acura RL Sedan 2011 US`；`Acura RL Sedan 2012 US`；`Audi 90 Sedan 1990 US`；`Audi 90 Sedan 1993 US`。

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-01_07_representative-cover-shape/output/cover_shape_summary-20261101_07.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-01_07_representative-cover-shape/output/shape_research_queue-20261101_07.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
