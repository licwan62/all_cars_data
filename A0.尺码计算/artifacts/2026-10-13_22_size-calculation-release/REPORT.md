# 发布报告

- 节点：`size-calculation`（`A0.尺码计算`）
- 版本：`20261013_22`
- 发布时间：`2026-10-13T18:41:46+08:00`
- 发布原因：交付物变化：US/TRIM/TRIM适配器.csv、US/全量/全量表.csv、US/尺码匹配报告.md、US/店铺/店铺全量_HNT.csv、US/店铺/店铺全量_TM.csv、US/店铺/店铺全量_TM_拆分.csv；规则变化（修改 data/全量SHAPE.yaml；新增 data/US/规则/SHAPE调整.yaml）。

## 规则（data/）

- 相对上一版本：修改 data/全量SHAPE.yaml；新增 data/US/规则/SHAPE调整.yaml。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `A0.尺码计算/artifacts/2026-10-13_21_match-report-shape/output/US/尺码匹配报告-20261013_21.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/全量/全量表.csv`

- 内容已变化：4378 行 → 4378 行；存于 `A0.尺码计算/artifacts/2026-10-13_20_full-table-cover-shape/output/US/全量/全量表-20261013_20.csv`。
- 行级差异：新增 0，删除 0，修改 37。
- 变更字段计数：`自动尺码` 37，`自动长度余量` 37，`规则ID` 37。
- 修改示例（最多 20 条）：
  - `Acura Integra Hatchback 1986-1989 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura Integra Hatchback 1991-1993 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura RSX Hatchback 2003-2004 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Nova Hatchback 1968-1972 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Nova Hatchback 1976-1979 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Volt Hatchback 2011-2015 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Volt Hatchback 2016-2019 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Dodge Charger Hatchback 1982-1987 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Focus Hatchback 2012-2018 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Fastback 1970 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Hatchback 1979-1986 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Hatchback 1987-1993 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Accord Hatchback 1986-1989 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda CR-Z Hatchback 2011-2015 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Hatchback 2017-2021 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Type R Hatchback 2017-2021 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Type R Hatchback 2022-2026 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Insight Hatchback 2010-2014 US`：`自动尺码`、`自动长度余量`、`规则ID`
  - `Mazda 3 Hatchback 2014-2018 US`：`自动尺码`、`自动长度余量`、`规则ID`

### `US/店铺/店铺全量_HNT.csv`

- 内容已变化：4378 行 → 4378 行；存于 `A0.尺码计算/artifacts/2026-10-13_20_full-table-cover-shape/output/US/店铺/店铺全量_HNT-20261013_20.csv`。
- 行级差异：新增 0，删除 0，修改 36。
- 变更字段计数：`候选` 32，`匹配尺码` 36，`原因` 32，`相差数值` 32，`自动尺码` 35，`自动长度余量` 36，`规则ID` 36。
- 修改示例（最多 20 条）：
  - `Acura Integra Hatchback 1986-1989 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura Integra Hatchback 1991-1993 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura RSX Hatchback 2003-2004 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Nova Hatchback 1968-1972 US`：`匹配尺码`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Nova Hatchback 1976-1979 US`：`匹配尺码`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Volt Hatchback 2011-2015 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Volt Hatchback 2016-2019 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Dodge Charger Hatchback 1982-1987 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Focus Hatchback 2012-2018 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Fastback 1970 US`：`匹配尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Hatchback 1979-1986 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Hatchback 1987-1993 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Accord Hatchback 1986-1989 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Hatchback 2017-2021 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Type R Hatchback 2017-2021 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Type R Hatchback 2022-2026 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Insight Hatchback 2010-2014 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Mazda 3 Hatchback 2014-2018 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Mazda 3 Hatchback 2019-2026 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`

### `US/店铺/店铺全量_TM.csv`

- 内容已变化：4378 行 → 4378 行；存于 `A0.尺码计算/artifacts/2026-10-13_20_full-table-cover-shape/output/US/店铺/店铺全量_TM-20261013_20.csv`。
- 行级差异：新增 0，删除 0，修改 36。
- 变更字段计数：`候选` 32，`匹配尺码` 36，`原因` 32，`相差数值` 32，`自动尺码` 36，`自动长度余量` 36，`规则ID` 36。
- 修改示例（最多 20 条）：
  - `Acura Integra Hatchback 1986-1989 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura Integra Hatchback 1991-1993 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Acura RSX Hatchback 2003-2004 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Nova Hatchback 1968-1972 US`：`匹配尺码`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Nova Hatchback 1976-1979 US`：`匹配尺码`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Volt Hatchback 2011-2015 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Chevrolet Volt Hatchback 2016-2019 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Dodge Charger Hatchback 1982-1987 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Focus Hatchback 2012-2018 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Fastback 1970 US`：`匹配尺码`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Hatchback 1979-1986 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Ford Mustang Hatchback 1987-1993 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Accord Hatchback 1986-1989 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Hatchback 2017-2021 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Type R Hatchback 2017-2021 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Civic Type R Hatchback 2022-2026 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Honda Insight Hatchback 2010-2014 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Mazda 3 Hatchback 2014-2018 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`
  - `Mazda 3 Hatchback 2019-2026 US`：`候选`、`匹配尺码`、`原因`、`相差数值`、`自动尺码`、`自动长度余量`、`规则ID`

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容已变化：4378 行 → 4378 行；存于 `A0.尺码计算/artifacts/2026-10-13_20_full-table-cover-shape/output/US/店铺/店铺全量_TM_拆分-20261013_20.csv`。
- 行级差异：新增 0，删除 0，修改 1。
- 变更字段计数：`匹配尺码` 1，`自动尺码` 1，`自动长度余量` 1，`规则ID` 1。
- 修改示例（最多 20 条）：
  - `Chevrolet Nova Hatchback 1976-1979 US`：`匹配尺码`、`自动尺码`、`自动长度余量`、`规则ID`

### `US/TRIM/TRIM适配器.csv`

- 内容已变化：23258 行 → 23258 行；存于 `A0.尺码计算/artifacts/2026-10-13_19_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261013_19.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `EU/尺码匹配报告.md`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/EU/尺码匹配报告-20261013_18.md`，未复制。

### `EU/全量/全量表.csv`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv`，未复制。

### `RU/尺码匹配报告.md`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/RU/尺码匹配报告-20261013_18.md`，未复制。

### `RU/全量/全量表.csv`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/RU/全量/全量表-20261013_16.csv`，未复制。
