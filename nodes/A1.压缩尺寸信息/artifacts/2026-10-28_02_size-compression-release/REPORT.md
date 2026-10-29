# 发布报告

- 节点：`size-compression`（`nodes/A1.压缩尺寸信息`）
- 版本：`20261028_02`
- 发布时间：`2026-10-28T15:39:42+08:00`
- 发布原因：交付物变化：HNT/压缩尺码表.csv、HNT/压缩尺码表_皮卡.csv、RU/压缩尺码表.csv、RU/压缩来源.csv、TM/压缩尺码表.csv、TM/压缩尺码表_皮卡.csv、TM_拆分/压缩尺码表.csv、TM_拆分/压缩尺码表_皮卡.csv、US/压缩尺码表.csv、US/压缩尺码表_皮卡.csv；上游输入变化；pending/发布说明变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `size-calculation` `20261028_03`：运行批次实际读取，6 个文件。
- `code-mapping` `20261019_02`：运行批次实际读取，1 个文件。

## 身份承接

- `US/压缩来源.csv` ← `size-calculation` `US/全量/全量表.csv`（subset）：通过。
- `EU/压缩来源.csv` ← `size-calculation` `EU/全量/全量表.csv`（subset）：通过。
- `RU/压缩来源.csv` ← `size-calculation` `RU/全量/全量表.csv`（subset）：通过。

## 交付物与变更

### `US/压缩尺码表.csv`

- 内容已变化：1370 行 → 1370 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-28_01_compress-by-line/output/US/压缩尺码表-20261028_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US/压缩尺码表_皮卡.csv`

- 内容已变化：143 行 → 143 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-28_01_compress-by-line/output/US/压缩尺码表_皮卡-20261028_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US/压缩来源.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/US/压缩来源-20261019_01.csv`，未复制。

### `HNT/压缩尺码表.csv`

- 内容已变化：1214 行 → 1214 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-28_01_compress-by-line/output/HNT/压缩尺码表-20261028_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `HNT/压缩尺码表_皮卡.csv`

- 内容已变化：134 行 → 134 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-28_01_compress-by-line/output/HNT/压缩尺码表_皮卡-20261028_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `HNT/压缩来源.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/HNT/压缩来源-20261019_01.csv`，未复制。

### `TM/压缩尺码表.csv`

- 内容已变化：1238 行 → 1238 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-28_01_compress-by-line/output/TM/压缩尺码表-20261028_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `TM/压缩尺码表_皮卡.csv`

- 内容已变化：143 行 → 143 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-28_01_compress-by-line/output/TM/压缩尺码表_皮卡-20261028_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `TM/压缩来源.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/TM/压缩来源-20261019_01.csv`，未复制。

### `TM_拆分/压缩尺码表.csv`

- 内容已变化：835 行 → 835 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-28_01_compress-by-line/output/TM_拆分/压缩尺码表-20261028_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `TM_拆分/压缩尺码表_皮卡.csv`

- 内容已变化：34 行 → 34 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-28_01_compress-by-line/output/TM_拆分/压缩尺码表_皮卡-20261028_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `TM_拆分/压缩来源.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/TM_拆分/压缩来源-20261019_01.csv`，未复制。

### `EU/压缩尺码表.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表-20261010_01.csv`，未复制。

### `EU/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表_皮卡-20261010_01.csv`，未复制。

### `EU/压缩来源.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩来源-20261010_01.csv`，未复制。

### `RU/压缩尺码表.csv`

- 内容已变化：7090 行 → 7090 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-26_03_compress-by-line/output/RU/压缩尺码表-20261026_03.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `RU/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-26_01_compress-by-line/output/RU/压缩尺码表_皮卡-20261026_01.csv`，未复制。

### `RU/压缩来源.csv`

- 内容已变化：13645 行 → 13645 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-10-26_03_compress-by-line/output/RU/压缩来源-20261026_03.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。
