# 发布报告

- 节点：`dimension-library`（`nodes/01.整理尺寸库`）
- 版本：`20261101_18`
- 发布时间：`2026-11-01T13:06:30+08:00`
- 发布原因：交付物变化：US_补库待核.csv、US_补库核对.csv；规则变化（修改 data/us/year_gap_resolutions.json；新增 data/us/evidence/1d9d4e5347c5f4b353571043792ab0a573d02da3ffd64d5190d864f39e5e8cd9.jpg, data/us/evidence/24dd2bd57e1186240596b24f12af9653e8fc6798d2c3ecada7570ab3cbeed63f.jpg, data/us/evidence/4de4ea15dd5226c1a6a0f2f7183b1873efdd8403a4dfbdadef3366fc42ff46a9.jpg, data/us/evidence/c799093196b835dcf9721f942603b2bf6fd10476c63f2b1311ae4993b0483e73.jpg）。

## 规则（data/）

- 相对上一版本：修改 data/us/year_gap_resolutions.json；新增 data/us/evidence/1d9d4e5347c5f4b353571043792ab0a573d02da3ffd64d5190d864f39e5e8cd9.jpg, data/us/evidence/24dd2bd57e1186240596b24f12af9653e8fc6798d2c3ecada7570ab3cbeed63f.jpg, data/us/evidence/4de4ea15dd5226c1a6a0f2f7183b1873efdd8403a4dfbdadef3366fc42ff46a9.jpg, data/us/evidence/c799093196b835dcf9721f942603b2bf6fd10476c63f2b1311ae4993b0483e73.jpg。

## 上游输入依据

- `dimension-crawler` `20261101_03`：运行批次实际读取，8 个文件。

## 交付物与变更

### `尺寸库.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_15_regional-library/output/尺寸库-20261101_15.csv`，未复制。

### `尺寸库_US.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-11-01_15_regional-library/output/尺寸库_US-20261101_15.csv`，未复制。

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

- 内容已变化：142 行 → 142 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-01_17_regional-library/output/US_补库核对-20261101_17.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US_补库待核.csv`

- 内容已变化：51 行 → 51 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-01_17_regional-library/output/US_补库待核-20261101_17.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `EU_ID迁移.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv`，未复制。

### `来源映射_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv`，未复制。

### `来源映射_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv`，未复制。
