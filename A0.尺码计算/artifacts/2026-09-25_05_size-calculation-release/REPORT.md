# 发布报告

- 节点：`size-calculation`（`A0.尺码计算`）
- 版本：`20260925_05`
- 发布时间：`2026-09-25T13:29:14+08:00`
- 工作描述：size-calculation 输出刷新。

## 规则（data/）

- 相对上一版本：修改 data/eu/尺码匹配规则.csv。

## 交付物与变更

### `全量表_US.csv`

- 内容未变化；仅产生新的发布版本。

### `全量表_EU.csv`

- 内容已变化：29707 行 → 29707 行。
- 行级差异：新增 0，删除 0，修改 4476。
- 变更字段计数：`候选` 2211，`自动尺码` 2265。
- 修改示例（最多 20 条）：
  - `AMC Matador 1971 72 Wagon 1970-1974 EU`：`自动尺码`
  - `AMC Matador 1973 Wagon 1970-1974 EU`：`自动尺码`
  - `AMC Matador 1974 Wagon 1970-1974 EU`：`候选`
  - `Alpina B5 E61 Wagon 2005-2010 EU`：`自动尺码`
  - `Alpina B5 E61 Wagon 2007-2010 EU`：`自动尺码`
  - `Alpina B5 F11 Wagon 2010-2011 EU`：`自动尺码`
  - `Alpina B5 F11 Wagon 2012-2014 EU`：`自动尺码`
  - `Alpina B5 F11 Wagon 2015-2016 EU`：`自动尺码`
  - `Alpina B5 G31 Wagon 2017-2020 EU`：`自动尺码`
  - `Alpina B5 G31 Wagon 2020-2024 EU`：`自动尺码`
  - `Alpina B5 G31 Wagon 2023-2024 EU`：`自动尺码`
  - `Alpina D5 F11 Wagon 2011-2016 EU`：`自动尺码`
  - `Alpina D5 G31 Wagon 2017-2020 EU`：`自动尺码`
  - `Alpina D5 G31 Wagon 2020-2024 EU`：`自动尺码`
  - `Asia Motors Hi-Topic AM725 MPV 1993-1999 EU`：`自动尺码`
  - `Aston Martin Lagonda i shooting brake Wagon 1976-1997 EU`：`自动尺码`
  - `Aston Martin Lagonda i shooting brake Wagon 1985-1987 EU`：`自动尺码`
  - `Aston Martin Rapide Hatchback 2010-2013 EU`：`自动尺码`
  - `Aston Martin Rapide Hatchback 2013-2014 EU`：`自动尺码`
  - `Aston Martin Rapide Hatchback 2014-2026 EU`：`自动尺码`

### `全量表_RU.csv`

- 内容未变化；仅产生新的发布版本。

### `尺寸分析表_US.csv`

- 内容未变化；仅产生新的发布版本。

### `店铺全量_HNT.csv`

- 内容未变化；仅产生新的发布版本。

### `店铺全量_TM.csv`

- 内容未变化；仅产生新的发布版本。

### `店铺全量_TM_拆分.csv`

- 内容未变化；仅产生新的发布版本。

### `尺码匹配规则.csv`

- 内容未变化；仅产生新的发布版本。

### `尺码匹配规则_EU.csv`

- 内容已变化：45 行 → 45 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码匹配规则_RU.csv`

- 内容未变化；仅产生新的发布版本。

### `店铺货架.csv`

- 内容未变化；仅产生新的发布版本。

### `尺码匹配报告_EU.json`

- 内容未变化；仅产生新的发布版本。

### `尺码匹配报告_US.json`

- 内容已变化：None 行 → None 行。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `尺码匹配报告_RU.json`

- 内容未变化；仅产生新的发布版本。
