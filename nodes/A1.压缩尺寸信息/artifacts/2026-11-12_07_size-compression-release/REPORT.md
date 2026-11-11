# 发布报告

- 节点：`size-compression`（`nodes/A1.压缩尺寸信息`）
- 版本：`20261112_07`
- 发布时间：`2026-11-12T02:43:15+08:00`
- 发布原因：交付物变化：HNT/压缩尺码表_皮卡.json、HNT/压缩来源.json、TM/压缩尺码表_皮卡.json、TM/压缩来源.json、US/压缩尺码表_皮卡.json、US/压缩来源.json；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `size-calculation` `20261112_07`：运行批次实际读取，6 个文件。
- `code-mapping` `20261112_01`：运行批次实际读取，1 个文件。

## 身份承接

- `US/压缩来源.json` ← `size-calculation` `US/全量/全量表.json`（subset）：通过。
- `EU/压缩来源.json` ← `size-calculation` `EU/全量/全量表.json`（subset）：通过。
- `RU/压缩来源.json` ← `size-calculation` `RU/全量/全量表.json`（subset）：通过。

## 交付物与变更

### `US/压缩尺码表.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/US/压缩尺码表-20261112_01.json`，未复制。

### `US/压缩尺码表_皮卡.json`

- 内容已变化：145 行 → 144 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_06_json-node/output/US/压缩尺码表_皮卡-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/压缩来源.json`

- 内容已变化：6397 行 → 6397 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_06_json-node/output/US/压缩来源-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `HNT/压缩尺码表.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/HNT/压缩尺码表-20261112_01.json`，未复制。

### `HNT/压缩尺码表_皮卡.json`

- 内容已变化：136 行 → 135 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_06_json-node/output/HNT/压缩尺码表_皮卡-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `HNT/压缩来源.json`

- 内容已变化：6412 行 → 6412 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_06_json-node/output/HNT/压缩来源-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `TM/压缩尺码表.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/TM/压缩尺码表-20261112_01.json`，未复制。

### `TM/压缩尺码表_皮卡.json`

- 内容已变化：145 行 → 144 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_06_json-node/output/US/压缩尺码表_皮卡-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `TM/压缩来源.json`

- 内容已变化：6410 行 → 6410 行；存于 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_06_json-node/output/TM/压缩来源-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `TM_拆分/压缩尺码表.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/TM_拆分/压缩尺码表-20261112_01.json`，未复制。

### `TM_拆分/压缩尺码表_皮卡.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/TM_拆分/压缩尺码表_皮卡-20261112_01.json`，未复制。

### `TM_拆分/压缩来源.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/TM_拆分/压缩来源-20261112_01.json`，未复制。

### `EU/压缩尺码表.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/EU/压缩尺码表-20261112_01.json`，未复制。

### `EU/压缩尺码表_皮卡.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/EU/压缩尺码表_皮卡-20261112_01.json`，未复制。

### `EU/压缩来源.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/EU/压缩来源-20261112_01.json`，未复制。

### `RU/压缩尺码表.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/RU/压缩尺码表-20261112_01.json`，未复制。

### `RU/压缩尺码表_皮卡.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/RU/压缩尺码表_皮卡-20261112_01.json`，未复制。

### `RU/压缩来源.json`

- 内容未变化；引用 `nodes/A1.压缩尺寸信息/artifacts/2026-11-12_01_json-interface-migration/output/RU/压缩来源-20261112_01.json`，未复制。
