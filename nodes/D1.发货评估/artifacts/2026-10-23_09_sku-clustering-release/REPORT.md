# 发布报告

- 节点：`sku-clustering`（`nodes/D1.发货评估`）
- 版本：`20261023_09`
- 发布时间：`2026-10-23T11:49:14+08:00`
- 发布原因：交付物变化：W型车发货评估.csv、全量车型发货评估明细.csv、发货评估身份映射.csv、普通车发货评估.csv、灰度匹配审核.csv、皮卡发货评估.csv；规则变化（修改 data/README.md, data/发货评估.json）；pending/发布说明变化。

## 规则（data/）

- 相对上一版本：修改 data/README.md, data/发货评估.json。

## 上游输入依据

- `size-calculation` `20261019_10`：运行批次实际读取，2 个文件。
- `negative-review-analysis` `20261009_04`：运行批次实际读取，1 个文件。

## 身份承接

- `发货评估身份映射.csv` ← `size-calculation` `US/全量/全量表.csv`（equal）：通过。

## 交付物与变更

### `全量车型发货评估明细.csv`

- 内容已变化：4383 行 → 4383 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_08_delivery-evaluation/output/全量车型发货评估明细-20261023_08.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `发货评估身份映射.csv`

- 本版本新增交付物，共 4383 行。

### `W型车发货评估.csv`

- 内容已变化：313 行 → 313 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_08_delivery-evaluation/output/W型车发货评估-20261023_08.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `皮卡发货评估.csv`

- 内容已变化：235 行 → 235 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_08_delivery-evaluation/output/皮卡发货评估-20261023_08.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `普通车发货评估.csv`

- 内容已变化：1716 行 → 1716 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_08_delivery-evaluation/output/普通车发货评估-20261023_08.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `灰度匹配审核.csv`

- 内容已变化：275 行 → 275 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_08_delivery-evaluation/output/灰度匹配审核-20261023_08.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。
