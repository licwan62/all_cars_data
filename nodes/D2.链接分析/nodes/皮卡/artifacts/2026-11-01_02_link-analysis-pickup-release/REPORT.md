# 发布报告

- 节点：`link-analysis-pickup`（`nodes/D2.链接分析/nodes/皮卡`）
- 版本：`20261101_02`
- 发布时间：`2026-11-01T02:28:21+08:00`
- 发布原因：交付物变化：链接分析报告.md；上游输入变化；规则变化（修改 data/发货单明细.xlsx；新增 data/发货事实.csv）。

## 规则（data/）

- 相对上一版本：修改 data/发货单明细.xlsx；新增 data/发货事实.csv。

## 上游输入依据

- `size-calculation` `20261101_07`：运行批次实际读取，1 个文件。

## 交付物与变更

### `链接字段审核.csv`

- 内容未变化；引用 `nodes/D2.链接分析/nodes/皮卡/artifacts/2026-10-28_09_pickup-link-audit/output/链接字段审核-20261028_09.csv`，未复制。

### `上架链接明细.csv`

- 内容未变化；引用 `nodes/D2.链接分析/nodes/皮卡/artifacts/2026-10-28_09_pickup-link-audit/output/上架链接明细-20261028_09.csv`，未复制。

### `发货分配核对.csv`

- 内容未变化；引用 `nodes/D2.链接分析/nodes/皮卡/artifacts/2026-10-28_10_link-analysis-pickup-release/output/发货分配核对-20261028_10.csv`，未复制。

### `SKU发货数量.csv`

- 内容未变化；引用 `nodes/D2.链接分析/nodes/皮卡/artifacts/2026-10-28_09_pickup-link-audit/output/SKU发货数量-20261028_09.csv`，未复制。

### `链接分析报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/D2.链接分析/nodes/皮卡/artifacts/2026-11-01_01_pickup-link-audit/output/链接分析报告-20261101_01.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。
