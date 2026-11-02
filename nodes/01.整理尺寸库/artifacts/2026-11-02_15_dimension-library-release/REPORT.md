# 发布报告

- 节点：`dimension-library`（`nodes/01.整理尺寸库`）
- 版本：`20261102_15`
- 发布时间：`2026-11-02T18:41:40+08:00`
- 发布原因：交付物变化：US_补库核对.csv、尺寸库.csv、尺寸库_US.csv；规则变化（修改 data/us/year_gap_resolutions.json）。

## 规则（data/）

- 相对上一版本：修改 data/us/year_gap_resolutions.json。

## 上游输入依据

- `dimension-crawler` `20261102_01`：运行批次实际读取，8 个文件。

## 交付物与变更

### `尺寸库.csv`

- 内容已变化：47815 行 → 47815 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-02_14_regional-library/output/尺寸库-20261102_14.csv`。
- 行级差异：新增 0，删除 0，修改 3。
- 变更字段计数：`W-IN` 3，`参考车型` 1，`备注` 3，`迭代状态` 3。
- 修改示例（最多 20 条）：
  - `smart fortwo Coupe 2017 US`：`W-IN`、`参考车型`、`备注`、`迭代状态`
  - `smart fortwo Coupe 2018 US`：`W-IN`、`备注`、`迭代状态`
  - `smart fortwo Coupe 2019 US`：`W-IN`、`备注`、`迭代状态`

### `尺寸库_US.csv`

- 内容已变化：4837 行 → 4837 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-02_14_regional-library/output/尺寸库_US-20261102_14.csv`。
- 行级差异：新增 0，删除 0，修改 3。
- 变更字段计数：`W-IN` 3，`参考车型` 1，`备注` 3，`迭代状态` 3。
- 修改示例（最多 20 条）：
  - `smart fortwo Coupe 2017 US`：`W-IN`、`参考车型`、`备注`、`迭代状态`
  - `smart fortwo Coupe 2018 US`：`W-IN`、`备注`、`迭代状态`
  - `smart fortwo Coupe 2019 US`：`W-IN`、`备注`、`迭代状态`

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

- 内容已变化：504 行 → 504 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-02_14_regional-library/output/US_补库核对-20261102_14.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US_补库待核.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_19_regional-library/output/US_补库待核-20261101_19.csv`，未复制。

### `EU_ID迁移.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv`，未复制。

### `来源映射_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv`，未复制。

### `来源映射_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv`，未复制。
