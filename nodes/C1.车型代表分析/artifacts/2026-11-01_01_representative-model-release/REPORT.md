# 发布报告

- 节点：`representative-model`（`nodes/C1.车型代表分析`）
- 版本：`20261101_01`
- 发布时间：`2026-11-01T02:37:34+08:00`
- 发布原因：交付物变化：代表车型.csv、代表车型报告.md；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `size-calculation` `20261101_07`：发布时上游版本（未经运行记录核实），15 个文件。
- `size-compression` `20261101_03`：发布时上游版本（未经运行记录核实），18 个文件。
- 无运行记录可核实的交付物：`代表车型.csv`、`代表车型.tsv`、`代表车型报告.md`。

## 交付物与变更

### `代表车型.csv`

- 内容已变化：116 行 → 116 行；存于 `nodes/C1.车型代表分析/artifacts/2026-11-01_01_representative-model-release/output/代表车型-20261101_01.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `代表车型.tsv`

- 内容未变化；引用 `nodes/C1.车型代表分析/artifacts/2026-10-09_05_representative-model-release/output/代表车型-20261009_05.tsv`，未复制。

### `代表车型报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/C1.车型代表分析/artifacts/2026-11-01_01_representative-model-release/output/代表车型报告-20261101_01.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
