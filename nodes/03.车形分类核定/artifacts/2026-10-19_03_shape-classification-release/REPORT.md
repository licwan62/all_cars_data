# 发布报告

- 节点：`shape-classification`（`03.车形分类核定`）
- 版本：`20261019_03`
- 发布时间：`2026-10-19T02:04:36+08:00`
- 发布原因：交付物变化：COVER_SHAPE.csv、cover_shape_summary.json、shape_research_queue.jsonl、车形分类.csv；上游输入变化；规则变化（修改 data/US车形ID迁移.csv；新增 data/US车形补充核定.csv）。

## 规则（data/）

- 相对上一版本：修改 data/US车形ID迁移.csv；新增 data/US车形补充核定.csv。

## 上游输入依据

- `dimension-library` `20261009_08`：发布时上游版本（未经运行记录核实），7 个文件。
- `structure-review` `20261019_02`：发布时上游版本（未经运行记录核实），4 个文件。
- 无运行记录可核实的交付物：`车形分类.csv`、`参考尺寸计算.csv`。

## 身份承接

- `车形分类.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。
- `COVER_SHAPE.csv` ← `dimension-library` `尺寸库.csv`（equal）：通过。

## 交付物与变更

### `车形分类.csv`

- 内容已变化：47356 行 → 47361 行；存于 `03.车形分类核定/artifacts/2026-10-19_03_shape-classification-release/output/车形分类-20261019_03.csv`。
- 行级差异：新增 9，删除 4，修改 0。
- 新增示例（最多 10 条）：`Chevrolet Cavalier Coupe 1984-1985 US`；`Chevrolet Cavalier Sedan 1984-1985 US`；`Chevrolet Chevelle Convertible 1966-1967 US`；`Chevrolet Chevelle Coupe 1969-1970 US`；`Chevrolet Chevelle Coupe 1972 US`；`Chevrolet Chevelle Wagon 1965-1967 US`；`Chevrolet Nova Coupe 1975 US`；`Ford Mustang Coupe 1970 US`；`MINI Countryman JCW SUV 2018 US`。
- 删除示例（最多 10 条）：`Chevrolet Cavalier Coupe 1985 US`；`Chevrolet Cavalier Sedan 1984 US`；`Chevrolet Chevelle Convertible 1966 US`；`Chevrolet Chevelle Wagon 1967 US`。

### `参考尺寸计算.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容已变化：47356 行 → 47361 行；存于 `03.车形分类核定/artifacts/2026-10-19_02_representative-cover-shape/output/COVER_SHAPE-20261019_02.csv`。
- 行级差异：新增 9，删除 4，修改 0。
- 新增示例（最多 10 条）：`Chevrolet Cavalier Coupe 1984-1985 US`；`Chevrolet Cavalier Sedan 1984-1985 US`；`Chevrolet Chevelle Convertible 1966-1967 US`；`Chevrolet Chevelle Coupe 1969-1970 US`；`Chevrolet Chevelle Coupe 1972 US`；`Chevrolet Chevelle Wagon 1965-1967 US`；`Chevrolet Nova Coupe 1975 US`；`Ford Mustang Coupe 1970 US`；`MINI Countryman JCW SUV 2018 US`。
- 删除示例（最多 10 条）：`Chevrolet Cavalier Coupe 1985 US`；`Chevrolet Cavalier Sedan 1984 US`；`Chevrolet Chevelle Convertible 1966 US`；`Chevrolet Chevelle Wagon 1967 US`。

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-19_02_representative-cover-shape/output/cover_shape_summary-20261019_02.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-19_02_representative-cover-shape/output/shape_research_queue-20261019_02.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
