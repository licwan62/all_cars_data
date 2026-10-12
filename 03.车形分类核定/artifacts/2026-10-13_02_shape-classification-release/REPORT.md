# 发布报告

- 节点：`shape-classification`（`03.车形分类核定`）
- 版本：`20261013_02`
- 发布时间：`2026-10-13T00:20:31+08:00`
- 发布原因：交付物变化：COVER_SHAPE.csv、cover_shape_summary.json、shape_research_queue.jsonl；规则变化（修改 data/cover_shape/family_cache.csv, data/cover_shape/research_queue.yaml；新增 data/cover_shape/family_evidence.jsonl）。

## 规则（data/）

- 相对上一版本：修改 data/cover_shape/family_cache.csv, data/cover_shape/research_queue.yaml；新增 data/cover_shape/family_evidence.jsonl。

## 交付物与变更

### `车形分类.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/车形分类-20261009_04.csv`，未复制。

### `参考尺寸计算.csv`

- 内容未变化；引用 `03.车形分类核定/artifacts/2026-10-09_04_shape-classification-release/output/参考尺寸计算-20261009_04.csv`，未复制。

### `COVER_SHAPE.csv`

- 内容已变化：47356 行 → 47356 行；存于 `03.车形分类核定/artifacts/2026-10-13_01_representative-cover-shape/output/COVER_SHAPE-20261013_01.csv`。
- 行级差异：新增 0，删除 0，修改 4367。
- 变更字段计数：`SHAPE` 1576，`SHAPE_ALTERNATES` 3149，`SHAPE_METHOD` 4367，`SHAPE_SOURCE` 4367，`SHAPE_STATUS` 2740，`SHAPE_YEAR` 2433。
- 修改示例（最多 20 条）：
  - `Acura ADX SUV 2025-2026 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`
  - `Acura CL Coupe 1997-1999 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`
  - `Acura CL Coupe 2001-2003 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`
  - `Acura ILX Sedan 2013-2015 US`：`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`、`SHAPE_YEAR`
  - `Acura ILX Sedan 2016-2018 US`：`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`
  - `Acura ILX Sedan 2019-2022 US`：`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`
  - `Acura Integra Coupe 1994 US`：`SHAPE`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`
  - `Acura Integra Coupe 1995-2001 US`：`SHAPE`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`、`SHAPE_YEAR`
  - `Acura Integra Hatchback 1986-1989 US`：`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`
  - `Acura Integra Hatchback 1990 US`：`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`
  - `Acura Integra Hatchback 1991-1993 US`：`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`、`SHAPE_YEAR`
  - `Acura Integra Sedan 1990 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`
  - `Acura Integra Sedan 1991-1993 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`、`SHAPE_YEAR`
  - `Acura Integra Sedan 1994 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`
  - `Acura Integra Sedan 1995-2001 US`：`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`、`SHAPE_YEAR`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`、`SHAPE_YEAR`
  - `Acura Legend Coupe 1987-1990 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`
  - `Acura Legend Coupe 1991-1995 US`：`SHAPE`、`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`
  - `Acura Legend Sedan 1986-1988 US`：`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_STATUS`、`SHAPE_YEAR`
  - `Acura Legend Sedan 1989-1990 US`：`SHAPE_ALTERNATES`、`SHAPE_METHOD`、`SHAPE_SOURCE`、`SHAPE_YEAR`

### `cover_shape_summary.json`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-13_01_representative-cover-shape/output/cover_shape_summary-20261013_01.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `shape_research_queue.jsonl`

- 内容已变化：None 行 → None 行；存于 `03.车形分类核定/artifacts/2026-10-13_01_representative-cover-shape/output/shape_research_queue-20261013_01.jsonl`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
