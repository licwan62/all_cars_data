# 发布报告

- 节点：`sku-clustering`（`nodes/D1.发货评估`）
- 版本：`20261023_30`
- 发布时间：`2026-10-23T16:15:39+08:00`
- 发布原因：交付物变化：W型车发货评估.csv、全量车型发货评估明细.csv、普通车发货评估.csv、皮卡发货评估.csv。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `size-calculation` `20261019_10`：运行批次实际读取，2 个文件。
- `negative-review-analysis` `20261009_04`：运行批次实际读取，1 个文件。

## 身份承接

- `发货评估身份映射.csv` ← `size-calculation` `US/全量/全量表.csv`（equal）：通过。

## 交付物与变更

### `全量车型发货评估明细.csv`

- 内容已变化：1529 行 → 1529 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/output/全量车型发货评估明细-20261023_29.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `发货评估身份映射.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_20_delivery-evaluation/output/发货评估身份映射-20261023_20.csv`，未复制。

### `W型车发货评估.csv`

- 内容已变化：158 行 → 158 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/output/W型车发货评估-20261023_29.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `皮卡发货评估.csv`

- 内容已变化：98 行 → 98 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/output/皮卡发货评估-20261023_29.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `普通车发货评估.csv`

- 内容已变化：1273 行 → 1273 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_29_delivery-evaluation/output/普通车发货评估-20261023_29.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `灰度匹配审核.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_08_delivery-evaluation/output/灰度匹配审核-20261023_08.csv`，未复制。
