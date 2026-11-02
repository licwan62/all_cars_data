# 发布报告

- 节点：`shape-classification`（`nodes/03.车形分类核定`）
- 版本：`20261102_12`
- 发布时间：`2026-11-02T18:25:24+08:00`
- 发布原因：交付物变化：COVER_SHAPE.csv、cover_shape_summary.json、shape_research_queue.jsonl、车形分类.csv；上游输入变化；规则变化（修改 data/US车形补充核定.csv）。

## 规则（data/）

- 相对上一版本：修改 data/US车形补充核定.csv。

## 上游输入依据

- `dimension-library` `20261102_12`：发布时上游版本（未经运行记录核实），12 个文件。
- `structure-review` `20261102_08`：运行批次实际读取，1 个文件。

## 身份承接

- `车形分类.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `COVER_SHAPE.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。

## 交付物与变更

### `车形分类.csv`

- 内容已变化：47815 行 → 47815 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_10_regional-shapes/output/车形分类-20261102_10.csv`。
- 行级差异：新增 11，删除 11，修改 0。
- 新增示例（最多 10 条）：`BMW X2 SUV 2027 US`；`Ford Transit Connect SWB Van 2014 US`；`Ford Transit Connect SWB Van 2015 US`；`Ford Transit Connect SWB Van 2016 US`；`Ford Transit Connect SWB Van 2017 US`；`Ford Transit Connect SWB Van 2018 US`；`Ford Transit Connect SWB Van 2019 US`；`Ford Transit Connect SWB Van 2020 US`；`Ford Transit Connect SWB Van 2021 US`；`Ford Transit Connect SWB Van 2022 US`。
- 删除示例（最多 10 条）：`BMW X2 Coupe 2027 US`；`Ford Transit Connect Van 2014 US`；`Ford Transit Connect Van 2015 US`；`Ford Transit Connect Van 2016 US`；`Ford Transit Connect Van 2017 US`；`Ford Transit Connect Van 2018 US`；`Ford Transit Connect Van 2019 US`；`Ford Transit Connect Van 2020 US`；`Ford Transit Connect Van 2021 US`；`Ford Transit Connect Van 2022 US`。

### `参考尺寸计算.csv`

- 内容未变化；引用 `nodes/03.车形分类核定/artifacts/2026-11-02_01_regional-shapes/output/参考尺寸计算-20261102_01.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容已变化：47815 行 → 47815 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_11_representative-cover-shape/output/COVER_SHAPE-20261102_11.csv`。
- 行级差异：新增 11，删除 11，修改 0。
- 新增示例（最多 10 条）：`BMW X2 SUV 2027 US`；`Ford Transit Connect SWB Van 2014 US`；`Ford Transit Connect SWB Van 2015 US`；`Ford Transit Connect SWB Van 2016 US`；`Ford Transit Connect SWB Van 2017 US`；`Ford Transit Connect SWB Van 2018 US`；`Ford Transit Connect SWB Van 2019 US`；`Ford Transit Connect SWB Van 2020 US`；`Ford Transit Connect SWB Van 2021 US`；`Ford Transit Connect SWB Van 2022 US`。
- 删除示例（最多 10 条）：`BMW X2 Coupe 2027 US`；`Ford Transit Connect Van 2014 US`；`Ford Transit Connect Van 2015 US`；`Ford Transit Connect Van 2016 US`；`Ford Transit Connect Van 2017 US`；`Ford Transit Connect Van 2018 US`；`Ford Transit Connect Van 2019 US`；`Ford Transit Connect Van 2020 US`；`Ford Transit Connect Van 2021 US`；`Ford Transit Connect Van 2022 US`。

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_11_representative-cover-shape/output/cover_shape_summary-20261102_11.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `nodes/03.车形分类核定/artifacts/2026-11-02_11_representative-cover-shape/output/shape_research_queue-20261102_11.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
