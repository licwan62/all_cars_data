# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261112_07`
- 发布时间：`2026-11-12T02:41:16+08:00`
- 发布原因：交付物变化：US/TRIM/TRIM适配器.json、US/全量/全量表.json、US/尺码匹配报告.json、US/店铺/店铺全量_HNT.json、US/店铺/店铺全量_TM.json；上游输入变化；规则变化（新增 data/US/规则/同车型灰区.yaml）。

## 规则（data/）

- 相对上一版本：新增 data/US/规则/同车型灰区.yaml。

## 上游输入依据

- `dimension-library` `20261112_06`：运行批次实际读取，12 个文件。
- `structure-review` `20261112_01`：运行批次实际读取，4 个文件。
- `shape-classification` `20261112_01`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261112_01`：运行批次实际读取，5 个文件。

## 身份承接

- `US/全量/全量表.json` ← `dimension-library` `尺寸库_US.json`（equal）：通过。
- `EU/全量/全量表.json` ← `dimension-library` `尺寸库_EU.json`（equal）：通过。
- `RU/全量/全量表.json` ← `dimension-library` `尺寸库_RU.json`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.json`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-12_06_json-node/output/US/尺码匹配报告-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/全量/全量表.json`

- 内容已变化：6352 行 → 6352 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-12_06_json-node/output/US/全量/全量表-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/店铺/店铺全量_HNT.json`

- 内容已变化：6352 行 → 6352 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-12_06_json-node/output/US/店铺/店铺全量_HNT-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/店铺/店铺全量_TM.json`

- 内容已变化：6352 行 → 6352 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-12_06_json-node/output/US/店铺/店铺全量_TM-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/店铺/店铺全量_TM_拆分.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-12_01_json-interface-migration/output/US/店铺/店铺全量_TM_拆分-20261112_01.json`，未复制。

### `US/TRIM/TRIM适配器.json`

- 内容已变化：23258 行 → 23258 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-12_06_json-node/output/US/TRIM/TRIM适配器-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/尺码规则-20261015_01.json`，未复制。

### `US/店铺货架.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/店铺货架-20261015_01.json`，未复制。

### `US/新旧尺码对应.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-12_01_json-interface-migration/output/US/新旧尺码对应-20261112_01.json`，未复制。

### `EU/尺码匹配报告.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-12_01_json-interface-migration/output/EU/尺码匹配报告-20261112_01.json`，未复制。

### `EU/全量/全量表.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-12_01_json-interface-migration/output/EU/全量/全量表-20261112_01.json`，未复制。

### `EU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/EU/尺码规则-20261015_01.json`，未复制。

### `RU/尺码匹配报告.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-12_01_json-interface-migration/output/RU/尺码匹配报告-20261112_01.json`，未复制。

### `RU/全量/全量表.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-12_01_json-interface-migration/output/RU/全量/全量表-20261112_01.json`，未复制。

### `RU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码规则-20261026_02.json`，未复制。
