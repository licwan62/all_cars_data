# 发布报告

- 节点：`model-year-coverage`（`nodes/M0.车型年覆盖`）
- 版本：`20261112_07`
- 发布时间：`2026-11-12T01:33:53+08:00`
- 发布原因：交付物变化：名称映射审计.json、名称未匹配.json、回补候选.json、已对应缺口.json、映射影响.json、覆盖明细.json、覆盖汇总.json、车型覆盖明细.json；规则变化（修改 data/名称映射.csv；新增 data/名称映射说明.md, data/品牌映射.csv）。

## 规则（data/）

- 相对上一版本：修改 data/名称映射.csv；新增 data/名称映射说明.md, data/品牌映射.csv。

## 上游输入依据

- `dimension-library` `20261112_06`：运行批次实际读取，4 个文件。
- `structure-review` `20261112_01`：运行批次实际读取，3 个文件。

## 交付物与变更

### `覆盖汇总.json`

- 内容已变化：582 行 → 582 行；存于 `nodes/M0.车型年覆盖/artifacts/2026-11-12_06_model-year-coverage/output/覆盖汇总-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `覆盖明细.json`

- 内容已变化：80940 行 → 80940 行；存于 `nodes/M0.车型年覆盖/artifacts/2026-11-12_06_model-year-coverage/output/覆盖明细-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `车型覆盖明细.json`

- 内容已变化：58119 行 → 58119 行；存于 `nodes/M0.车型年覆盖/artifacts/2026-11-12_06_model-year-coverage/output/车型覆盖明细-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `车型名录.json`

- 内容未变化；引用 `nodes/M0.车型年覆盖/artifacts/2026-11-12_02_model-year-coverage/output/车型名录-20261112_02.json`，未复制。

### `车型年全集.json`

- 内容未变化；引用 `nodes/M0.车型年覆盖/artifacts/2026-11-12_02_model-year-coverage/output/车型年全集-20261112_02.json`，未复制。

### `回补候选.json`

- 内容已变化：80940 行 → 80940 行；存于 `nodes/M0.车型年覆盖/artifacts/2026-11-12_06_model-year-coverage/output/回补候选-20261112_06.json`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `来源关联.json`

- 内容未变化；引用 `nodes/M0.车型年覆盖/artifacts/2026-11-12_02_model-year-coverage/output/来源关联-20261112_02.json`，未复制。

### `来源统计.json`

- 内容未变化；引用 `nodes/M0.车型年覆盖/artifacts/2026-11-12_02_model-year-coverage/output/来源统计-20261112_02.json`，未复制。

### `名称未匹配.json`

- 本版本新增交付物，共 12226 行。

### `已对应缺口.json`

- 本版本新增交付物，共 1975 行。

### `映射影响.json`

- 本版本新增交付物，共 25 行。

### `名称映射审计.json`

- 本版本新增交付物，共 2028 行。
