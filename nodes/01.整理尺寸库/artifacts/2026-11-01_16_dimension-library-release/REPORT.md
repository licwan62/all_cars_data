# 发布报告

- 节点：`dimension-library`（`nodes/01.整理尺寸库`）
- 版本：`20261101_16`
- 发布时间：`2026-11-01T12:47:23+08:00`
- 发布原因：交付物变化：US_补库待核.csv、US_补库核对.csv、尺寸库.csv、尺寸库_US.csv；规则变化（修改 data/us/year_gap_resolutions.json）。

## 规则（data/）

- 相对上一版本：修改 data/us/year_gap_resolutions.json。

## 上游输入依据

- `dimension-crawler` `20261101_03`：运行批次实际读取，8 个文件。

## 交付物与变更

### `尺寸库.csv`

- 内容已变化：47449 行 → 47452 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-01_15_regional-library/output/尺寸库-20261101_15.csv`。
- 行级差异：新增 3，删除 0，修改 0。
- 新增示例（最多 10 条）：`Mazda 2 Hatchback 2016 US`；`Mazda 2 Hatchback 2017 US`；`Mazda 2 Hatchback 2018 US`。

### `尺寸库_US.csv`

- 内容已变化：4471 行 → 4474 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-01_15_regional-library/output/尺寸库_US-20261101_15.csv`。
- 行级差异：新增 3，删除 0，修改 0。
- 新增示例（最多 10 条）：`Mazda 2 Hatchback 2016 US`；`Mazda 2 Hatchback 2017 US`；`Mazda 2 Hatchback 2018 US`。

### `尺寸库_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv`，未复制。

### `尺寸库_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv`，未复制。

### `US_ID迁移.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_03_regional-library/output/US_ID迁移-20261101_03.csv`，未复制。

### `US_拆分候选.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_03_regional-library/output/US_拆分候选-20261101_03.csv`，未复制。

### `US_拆分待核.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_03_regional-library/output/US_拆分待核-20261101_03.csv`，未复制。

### `US_补库核对.csv`

- 内容已变化：142 行 → 142 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-01_15_regional-library/output/US_补库核对-20261101_15.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US_补库待核.csv`

- 内容已变化：54 行 → 51 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-01_15_regional-library/output/US_补库待核-20261101_15.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `EU_ID迁移.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv`，未复制。

### `来源映射_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv`，未复制。

### `来源映射_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv`，未复制。
