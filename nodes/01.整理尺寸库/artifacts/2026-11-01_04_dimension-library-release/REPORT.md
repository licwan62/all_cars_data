# 发布报告

- 节点：`dimension-library`（`nodes/01.整理尺寸库`）
- 版本：`20261101_04`
- 发布时间：`2026-11-01T04:36:12+08:00`
- 发布原因：交付物变化：US_ID迁移.csv、US_拆分候选.csv、US_拆分待核.csv；规则变化（新增 data/data_source/trimslate-vehicles.csv, data/data_source/vehicles.csv, data/us/README.md, data/us/audi_a7_evidence.json, data/us/audi_a7_split.json, data/us/model_members.json）；pending/发布说明变化。

## 规则（data/）

- 相对上一版本：新增 data/data_source/trimslate-vehicles.csv, data/data_source/vehicles.csv, data/us/README.md, data/us/audi_a7_evidence.json, data/us/audi_a7_split.json, data/us/model_members.json。

## 上游输入依据

- `dimension-crawler` `20261101_03`：运行批次实际读取，8 个文件。

## 交付物与变更

### `尺寸库.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库-20261009_08.csv`，未复制。

### `尺寸库_US.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_08_dimension-library-release/output/尺寸库_US-20261009_08.csv`，未复制。

### `尺寸库_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv`，未复制。

### `尺寸库_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv`，未复制。

### `US_ID迁移.csv`

- 本版本新增交付物，共 0 行。

### `US_拆分候选.csv`

- 本版本新增交付物，共 42 行。

### `US_拆分待核.csv`

- 本版本新增交付物，共 6 行。

### `EU_ID迁移.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv`，未复制。

### `来源映射_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv`，未复制。

### `来源映射_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv`，未复制。
