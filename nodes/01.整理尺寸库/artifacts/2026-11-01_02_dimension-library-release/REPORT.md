# 发布报告

- 节点：`dimension-library`（`nodes/01.整理尺寸库`）
- 版本：`20261101_02`
- 发布时间：`2026-11-01T02:17:33+08:00`
- 发布原因：上游输入变化；规则变化（新增 data/build_config.json；删除 data/eu/0916/00_EU尺寸库.csv, data/eu/0916/DimensionGroup尺寸.csv, data/eu/0916/Ktype.csv, data/eu/0916/KtypeMatched.csv, data/eu/0916/来源映射_EU.csv, data/ru/0916/00_RU尺寸库.csv, data/ru/0916/auto_ru_catalog_rank.csv, data/ru/0916/auto_ru_dimensions_with_match_key.csv, data/ru/0916/auto_ru_model_sales_with_match_key.csv, data/ru/0916/来源映射_RU.csv, data/us/0916/00_US尺寸库.csv）。

## 规则（data/）

- 相对上一版本：新增 data/build_config.json；删除 data/eu/0916/00_EU尺寸库.csv, data/eu/0916/DimensionGroup尺寸.csv, data/eu/0916/Ktype.csv, data/eu/0916/KtypeMatched.csv, data/eu/0916/来源映射_EU.csv, data/ru/0916/00_RU尺寸库.csv, data/ru/0916/auto_ru_catalog_rank.csv, data/ru/0916/auto_ru_dimensions_with_match_key.csv, data/ru/0916/auto_ru_model_sales_with_match_key.csv, data/ru/0916/来源映射_RU.csv, data/us/0916/00_US尺寸库.csv。

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

### `EU_ID迁移.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv`，未复制。

### `来源映射_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv`，未复制。

### `来源映射_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv`，未复制。
