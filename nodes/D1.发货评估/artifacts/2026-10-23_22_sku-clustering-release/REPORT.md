# 发布报告

- 节点：`sku-clustering`（`nodes/D1.发货评估`）
- 版本：`20261023_22`
- 发布时间：`2026-10-23T14:20:22+08:00`
- 发布原因：交付物变化：W型车发货评估.csv、全量车型发货评估明细.csv、发货评估身份映射.csv、普通车发货评估.csv、皮卡发货评估.csv；规则变化（修改 data/README.md, data/发货评估.json）；pending/发布说明变化。

## 规则（data/）

- 相对上一版本：修改 data/README.md, data/发货评估.json。

## 上游输入依据

- `size-calculation` `20261019_10`：运行批次实际读取，2 个文件。
- `negative-review-analysis` `20261009_04`：运行批次实际读取，1 个文件。

## 身份承接

- `发货评估身份映射.csv` ← `size-calculation` `US/全量/全量表.csv`（equal）：通过。

## 交付物与变更

### `全量车型发货评估明细.csv`

- 内容已变化：1529 行 → 1529 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_21_delivery-evaluation/output/全量车型发货评估明细-20261023_21.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `发货评估身份映射.csv`

- 内容已变化：4383 行 → 4383 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_20_delivery-evaluation/output/发货评估身份映射-20261023_20.csv`。
- 行级差异：新增 0，删除 0，修改 4383。
- 变更字段计数：`MAKE` 4383，`MODEL` 4383，`SKU` 4383，`YEAR` 4383，`供货尺码` 4383。
- 修改示例（最多 20 条）：
  - `Acura ADX SUV 2025-2026 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura CL Coupe 1997-1999 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura CL Coupe 2001-2003 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura ILX Sedan 2013-2015 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura ILX Sedan 2016-2018 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura ILX Sedan 2019-2022 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Coupe 1994 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Coupe 1995-2001 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Hatchback 1986-1989 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Hatchback 1990 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Hatchback 1991-1993 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Hatchback 2023-2026 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Sedan 1990 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Sedan 1991-1993 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Sedan 1994 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Sedan 1995-2001 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Legend Coupe 1987-1990 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Legend Coupe 1991-1995 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`
  - `Acura Legend Sedan 1986-1988 US`：`MAKE`、`MODEL`、`SKU`、`YEAR`、`供货尺码`

### `W型车发货评估.csv`

- 内容已变化：158 行 → 158 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_21_delivery-evaluation/output/W型车发货评估-20261023_21.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `皮卡发货评估.csv`

- 内容已变化：98 行 → 98 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_21_delivery-evaluation/output/皮卡发货评估-20261023_21.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `普通车发货评估.csv`

- 内容已变化：1273 行 → 1273 行；存于 `nodes/D1.发货评估/artifacts/2026-10-23_21_delivery-evaluation/output/普通车发货评估-20261023_21.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `灰度匹配审核.csv`

- 内容未变化；引用 `nodes/D1.发货评估/artifacts/2026-10-23_08_delivery-evaluation/output/灰度匹配审核-20261023_08.csv`，未复制。
