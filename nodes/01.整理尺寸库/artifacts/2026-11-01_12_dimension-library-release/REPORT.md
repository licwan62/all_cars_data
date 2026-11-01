# 发布报告

- 节点：`dimension-library`（`nodes/01.整理尺寸库`）
- 版本：`20261101_12`
- 发布时间：`2026-11-01T12:36:00+08:00`
- 发布原因：交付物变化：US_补库待核.csv、US_补库核对.csv、尺寸库.csv、尺寸库_US.csv；规则变化（新增 data/us/dimension_corrections.json, data/us/evidence/1c90c323e88fff89a0506dd4d943527e8c0dbb47ae121e31857ba47526109d3c.pdf, data/us/evidence/3d61409a721aa2dceb281b70fcc5d846e70ad5199f881d6e74ed3c8cb210b82f.pdf, data/us/evidence/5eab5cd6d3afb1a37f182c65464cf6f938f1ab601da5b139dbff13ef1d8f1a58.pdf, data/us/evidence/9c26a5bd9398f0734a2f9e74c6b1e4ce0fbec5cb787899e28b691ad7cf49c4cd.pdf, data/us/year_gap_resolutions.json, data/来源.md）；pending/发布说明变化。

## 规则（data/）

- 相对上一版本：新增 data/us/dimension_corrections.json, data/us/evidence/1c90c323e88fff89a0506dd4d943527e8c0dbb47ae121e31857ba47526109d3c.pdf, data/us/evidence/3d61409a721aa2dceb281b70fcc5d846e70ad5199f881d6e74ed3c8cb210b82f.pdf, data/us/evidence/5eab5cd6d3afb1a37f182c65464cf6f938f1ab601da5b139dbff13ef1d8f1a58.pdf, data/us/evidence/9c26a5bd9398f0734a2f9e74c6b1e4ce0fbec5cb787899e28b691ad7cf49c4cd.pdf, data/us/year_gap_resolutions.json, data/来源.md。

## 上游输入依据

- `dimension-crawler` `20261101_03`：运行批次实际读取，8 个文件。

## 交付物与变更

### `尺寸库.csv`

- 内容已变化：47361 行 → 47449 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-01_10_regional-library/output/尺寸库-20261101_10.csv`。
- 行级差异：新增 88，删除 0，修改 1。
- 变更字段计数：`H-IN` 1，`备注` 1。
- 新增示例（最多 10 条）：`Acura RL Sedan 2005 US`；`Acura RL Sedan 2006 US`；`Acura RL Sedan 2007 US`；`Acura RL Sedan 2008 US`；`Acura RL Sedan 2009 US`；`Acura RL Sedan 2010 US`；`Acura RL Sedan 2011 US`；`Acura RL Sedan 2012 US`；`Audi 90 Sedan 1990 US`；`Audi 90 Sedan 1993 US`。
- 修改示例（最多 20 条）：
  - `Pontiac Solstice Convertible 2009 US`：`H-IN`、`备注`

### `尺寸库_US.csv`

- 内容已变化：4383 行 → 4471 行；存于 `nodes/01.整理尺寸库/artifacts/2026-11-01_10_regional-library/output/尺寸库_US-20261101_10.csv`。
- 行级差异：新增 88，删除 0，修改 1。
- 变更字段计数：`H-IN` 1，`备注` 1。
- 新增示例（最多 10 条）：`Acura RL Sedan 2005 US`；`Acura RL Sedan 2006 US`；`Acura RL Sedan 2007 US`；`Acura RL Sedan 2008 US`；`Acura RL Sedan 2009 US`；`Acura RL Sedan 2010 US`；`Acura RL Sedan 2011 US`；`Acura RL Sedan 2012 US`；`Audi 90 Sedan 1990 US`；`Audi 90 Sedan 1993 US`。
- 修改示例（最多 20 条）：
  - `Pontiac Solstice Convertible 2009 US`：`H-IN`、`备注`

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

- 本版本新增交付物，共 142 行。

### `US_补库待核.csv`

- 本版本新增交付物，共 54 行。

### `EU_ID迁移.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/EU_ID迁移-20261009_06.csv`，未复制。

### `来源映射_EU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_EU-20261009_06.csv`，未复制。

### `来源映射_RU.csv`

- 内容未变化；引用 `nodes/01.整理尺寸库/artifacts/2026-10-09_06_dimension-library-release/output/来源映射_RU-20261009_06.csv`，未复制。
