# 发布报告

- 节点：`shape-classification`（`nodes/03.车形分类核定`）
- 版本：`20261102_03`
- 发布时间：`2026-11-02T09:05:45+08:00`
- 发布原因：交付物变化：COVER_SHAPE.csv、cover_shape_summary.json、shape_research_queue.jsonl、参考尺寸计算.csv、车形分类.csv；上游输入变化；规则变化（修改 data/US车形补充核定.csv）。

## 规则（data/）

- 相对上一版本：修改 data/US车形补充核定.csv。

## 上游输入依据

- `dimension-library` `20261102_02`：发布时上游版本（未经运行记录核实），12 个文件。
- `structure-review` `20261102_02`：运行批次实际读取，1 个文件。

## 身份承接

- `车形分类.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `COVER_SHAPE.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。

## 交付物与变更

### `车形分类.csv`

- 内容已变化：47453 行 → 47718 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_01_regional-shapes/output/车形分类-20261102_01.csv`。
- 行级差异：新增 265，删除 0，修改 0。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。

### `参考尺寸计算.csv`

- 内容已变化：17 行 → 17 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_01_regional-shapes/output/参考尺寸计算-20261102_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `COVER_SHAPE.csv`

- 内容已变化：47453 行 → 47718 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_02_representative-cover-shape/output/COVER_SHAPE-20261102_02.csv`。
- 行级差异：新增 265，删除 0，修改 0。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_02_representative-cover-shape/output/cover_shape_summary-20261102_02.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_02_representative-cover-shape/output/shape_research_queue-20261102_02.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
