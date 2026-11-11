# 发布报告

- 节点：`dimension-library`（`nodes/01.整理尺寸库`）
- 版本：`20261108_02`
- 发布时间：`2026-11-08T17:02:10+08:00`
- 发布原因：交付物变化：US_ID迁移.csv、尺寸库.csv、尺寸库_US.csv；规则变化（新增 data/us/pickup_replacements.json）。

## 规则（data/）

- 相对上一版本：新增 data/us/pickup_replacements.json。

## 上游输入依据

- `dimension-crawler` `20261102_01`：运行批次实际读取，8 个文件。

## 交付物与变更

### `尺寸库.csv`

- 内容已变化：49313 行 → 49330 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-08_01_regional-library/output/尺寸库-20261108_01.csv`。
- 行级差异：新增 20，删除 3，修改 0。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。

### `尺寸库_US.csv`

- 内容已变化：6335 行 → 6352 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-08_01_regional-library/output/尺寸库_US-20261108_01.csv`。
- 行级差异：新增 20，删除 3，修改 0。
- 新增示例（最多 10 条）：`Ford Ranger Pickup 1998-2000 Regular 6 US`；`Ford Ranger Pickup 1998-2000 Regular 7 US`；`Ford Ranger Pickup 1998-2000 SuperCab 6 US`；`Ford Ranger Pickup 2001-2002 Regular 7 US`；`Ford Ranger Pickup 2001-2002 SuperCab 6 US`；`Ford Ranger Pickup 2001-2003 Regular 6 US`；`Ford Ranger Pickup 2003 Regular 7 US`；`Ford Ranger Pickup 2003 SuperCab 6 US`；`Ford Ranger Pickup 2004 Regular 6 US`；`Ford Ranger Pickup 2004 Regular 7 US`。
- 删除示例（最多 10 条）：`Ford Ranger Pickup 1998-2011 Regular 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 6 US`；`Ford Ranger Pickup 1998-2011 SuperCab 7 US`。

### `尺寸库_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_EU-20261009_06.csv`，未复制。

### `尺寸库_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/尺寸库_RU-20261009_06.csv`，未复制。

### `US_ID迁移.csv`

- 内容已变化：0 行 → 13 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-08_01_regional-library/output/US_ID迁移-20261108_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US_拆分候选.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_03_regional-library/output/US_拆分候选-20261101_03.csv`，未复制。

### `US_拆分待核.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_03_regional-library/output/US_拆分待核-20261101_03.csv`，未复制。

### `US_补库核对.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-02_16_regional-library/output/US_补库核对-20261102_16.csv`，未复制。

### `US_补库待核.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_19_regional-library/output/US_补库待核-20261101_19.csv`，未复制。

### `EU_ID迁移.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv`，未复制。

### `来源映射_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv`，未复制。

### `来源映射_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv`，未复制。
