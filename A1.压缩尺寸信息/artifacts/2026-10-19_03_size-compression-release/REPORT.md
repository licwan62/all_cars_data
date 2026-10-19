# 发布报告

- 节点：`size-compression`（`A1.压缩尺寸信息`）
- 版本：`20261019_03`
- 发布时间：`2026-10-19T02:05:35+08:00`
- 发布原因：上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `size-calculation` `20261019_10`：运行批次实际读取，6 个文件。
- `code-mapping` `20261010_01`：运行批次实际读取，1 个文件。

## 身份承接

- `US/压缩来源.csv` ← `size-calculation` `US/全量/全量表.csv`（subset）：通过。
- `EU/压缩来源.csv` ← `size-calculation` `EU/全量/全量表.csv`（subset）：通过。
- `RU/压缩来源.csv` ← `size-calculation` `RU/全量/全量表.csv`（subset）：通过。

## 交付物与变更

### `US/压缩尺码表.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/US/压缩尺码表-20261019_01.csv`，未复制。

### `US/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/US/压缩尺码表_皮卡-20261010_01.csv`，未复制。

### `US/压缩来源.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/US/压缩来源-20261019_01.csv`，未复制。

### `HNT/压缩尺码表.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/HNT/压缩尺码表-20261019_01.csv`，未复制。

### `HNT/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/HNT/压缩尺码表_皮卡-20261010_01.csv`，未复制。

### `HNT/压缩来源.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/HNT/压缩来源-20261019_01.csv`，未复制。

### `TM/压缩尺码表.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/TM/压缩尺码表-20261019_01.csv`，未复制。

### `TM/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM/压缩尺码表_皮卡-20261010_01.csv`，未复制。

### `TM/压缩来源.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/TM/压缩来源-20261019_01.csv`，未复制。

### `TM_拆分/压缩尺码表.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/TM_拆分/压缩尺码表-20261019_01.csv`，未复制。

### `TM_拆分/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/TM_拆分/压缩尺码表_皮卡-20261010_01.csv`，未复制。

### `TM_拆分/压缩来源.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-19_01_compress-by-line/output/TM_拆分/压缩来源-20261019_01.csv`，未复制。

### `EU/压缩尺码表.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表-20261010_01.csv`，未复制。

### `EU/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩尺码表_皮卡-20261010_01.csv`，未复制。

### `EU/压缩来源.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/EU/压缩来源-20261010_01.csv`，未复制。

### `RU/压缩尺码表.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩尺码表-20261010_01.csv`，未复制。

### `RU/压缩尺码表_皮卡.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩尺码表_皮卡-20261010_01.csv`，未复制。

### `RU/压缩来源.csv`

- 内容未变化；引用 `A1.压缩尺寸信息/artifacts/2026-10-10_01_compress-by-line/output/RU/压缩来源-20261010_01.csv`，未复制。
