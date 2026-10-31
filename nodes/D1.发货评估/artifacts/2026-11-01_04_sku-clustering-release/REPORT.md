# 发布报告

- 节点：`sku-clustering`（`nodes/D1.发货评估`）
- 版本：`20261101_04`
- 发布时间：`2026-11-01T02:28:15+08:00`
- 发布原因：规则变化（新增 data/参考/历史定制预定车型.csv）。

## 规则（data/）

- 相对上一版本：新增 data/参考/历史定制预定车型.csv。

## 上游输入依据

- `size-calculation` `20261101_07`：运行批次实际读取，2 个文件。
- `negative-review-analysis` `20261009_04`：运行批次实际读取，1 个文件。
- `sales-estimation` `20261101_04`：运行批次实际读取，1 个文件。

## 身份承接

- `发货评估身份映射.csv` ← `size-calculation` `US/全量/全量表.csv`（equal）：通过。

## 交付物与变更

### `全量车型发货评估明细.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/output/全量车型发货评估明细-20261023_29.csv`，未复制。

### `发货评估身份映射.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_20_delivery-evaluation/output/发货评估身份映射-20261023_20.csv`，未复制。

### `W型车发货评估.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/output/W型车发货评估-20261023_29.csv`，未复制。

### `皮卡发货评估.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/output/皮卡发货评估-20261023_29.csv`，未复制。

### `普通车发货评估.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/output/普通车发货评估-20261023_29.csv`，未复制。

### `灰度匹配审核.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_08_delivery-evaluation/output/灰度匹配审核-20261023_08.csv`，未复制。
