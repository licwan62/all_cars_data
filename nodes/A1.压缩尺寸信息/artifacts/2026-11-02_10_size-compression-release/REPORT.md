# 发布报告

- 节点：`size-compression`（`nodes/A1.压缩尺寸信息`）
- 版本：`20261102_10`
- 发布时间：`2026-11-02T18:43:25+08:00`
- 发布原因：交付物变化：HNT/压缩尺码表.csv、HNT/压缩来源.csv、TM/压缩尺码表.csv、TM/压缩来源.csv、TM_拆分/压缩尺码表.csv、TM_拆分/压缩来源.csv、US/压缩尺码表.csv、US/压缩来源.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `size-calculation` `20261102_43`：运行批次实际读取，6 个文件。
- `code-mapping` `20261102_12`：运行批次实际读取，1 个文件。

## 身份承接

- `US/压缩来源.csv` ← `size-calculation` `US/全量/全量表.csv`（subset）：通过。
- `EU/压缩来源.csv` ← `size-calculation` `EU/全量/全量表.csv`（subset）：通过。
- `RU/压缩来源.csv` ← `size-calculation` `RU/全量/全量表.csv`（subset）：通过。

## 交付物与变更

### `US/压缩尺码表.csv`

- 内容已变化：1454 行 → 1454 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_09_compress-by-line/output/US/压缩尺码表-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_03_compress-by-line/output/US/压缩尺码表_皮卡-20261102_03.csv`，未复制。

### `US/压缩来源.csv`

- 内容已变化：4850 行 → 4850 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_09_compress-by-line/output/US/压缩来源-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `HNT/压缩尺码表.csv`

- 内容已变化：1290 行 → 1290 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_09_compress-by-line/output/HNT/压缩尺码表-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `HNT/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_03_compress-by-line/output/HNT/压缩尺码表_皮卡-20261102_03.csv`，未复制。

### `HNT/压缩来源.csv`

- 内容已变化：4854 行 → 4854 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_09_compress-by-line/output/HNT/压缩来源-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `TM/压缩尺码表.csv`

- 内容已变化：1315 行 → 1315 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_09_compress-by-line/output/TM/压缩尺码表-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `TM/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_03_compress-by-line/output/US/压缩尺码表_皮卡-20261102_03.csv`，未复制。

### `TM/压缩来源.csv`

- 内容已变化：4852 行 → 4852 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_09_compress-by-line/output/TM/压缩来源-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `TM_拆分/压缩尺码表.csv`

- 内容已变化：896 行 → 896 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_09_compress-by-line/output/TM_拆分/压缩尺码表-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `TM_拆分/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_03_compress-by-line/output/TM_拆分/压缩尺码表_皮卡-20261102_03.csv`，未复制。

### `TM_拆分/压缩来源.csv`

- 内容已变化：4861 行 → 4861 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-02_09_compress-by-line/output/TM_拆分/压缩来源-20261102_09.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `EU/压缩尺码表.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表-20261010_01.csv`，未复制。

### `EU/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表_皮卡-20261010_01.csv`，未复制。

### `EU/压缩来源.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩来源-20261010_01.csv`，未复制。

### `RU/压缩尺码表.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-26_03_compress-by-line/output/RU/压缩尺码表-20261026_03.csv`，未复制。

### `RU/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-26_01_compress-by-line/output/RU/压缩尺码表_皮卡-20261026_01.csv`，未复制。

### `RU/压缩来源.csv`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-10-26_03_compress-by-line/output/RU/压缩来源-20261026_03.csv`，未复制。
