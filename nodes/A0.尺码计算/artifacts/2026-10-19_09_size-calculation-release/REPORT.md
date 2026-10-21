# 发布报告

- 节点：`size-calculation`（`A0.尺码计算`）
- 版本：`20261019_09`
- 发布时间：`2026-10-19T02:04:36+08:00`
- 发布原因：交付物变化：US/TRIM/TRIM适配器.csv、US/全量/全量表.csv、US/尺码匹配报告.md、US/店铺/店铺全量_HNT.csv、US/店铺/店铺全量_TM.csv、US/店铺/店铺全量_TM_拆分.csv；上游输入变化；规则变化（修改 data/US/TRIM/TrimList_ID迁移.csv）。

## 规则（data/）

- 相对上一版本：修改 data/US/TRIM/TrimList_ID迁移.csv。

## 上游输入依据

- `dimension-library` `20261009_08`：运行批次实际读取，7 个文件。
- `structure-review` `20261010_01`：运行批次实际读取，2 个文件。
- `shape-classification` `20261013_04`：运行批次实际读取，1 个文件。
- `sales-estimation` `20261010_01`：运行批次实际读取，1 个文件。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `A0.尺码计算/artifacts/2026-10-19_08_match-report-shape/output/US/尺码匹配报告-20261019_08.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/全量/全量表.csv`

- 内容已变化：4378 行 → 4383 行；存于 `A0.尺码计算/artifacts/2026-10-19_07_full-table-cover-shape/output/US/全量/全量表-20261019_07.csv`。
- 行级差异：新增 9，删除 4，修改 118。
- 变更字段计数：`尺寸组销量` 17，`车型销量` 117。
- 新增示例（最多 10 条）：`Chevrolet Cavalier Coupe 1984-1985 US`；`Chevrolet Cavalier Sedan 1984-1985 US`；`Chevrolet Chevelle Convertible 1966-1967 US`；`Chevrolet Chevelle Coupe 1969-1970 US`；`Chevrolet Chevelle Coupe 1972 US`；`Chevrolet Chevelle Wagon 1965-1967 US`；`Chevrolet Nova Coupe 1975 US`；`Ford Mustang Coupe 1970 US`；`MINI Countryman JCW SUV 2018 US`。
- 删除示例（最多 10 条）：`Chevrolet Cavalier Coupe 1985 US`；`Chevrolet Cavalier Sedan 1984 US`；`Chevrolet Chevelle Convertible 1966 US`；`Chevrolet Chevelle Wagon 1967 US`。
- 修改示例（最多 20 条）：
  - `Chevrolet Cavalier Coupe 1983 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1987 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1989 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1990 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1991-1994 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1996 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1999 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 2000-2005 US`：`车型销量`
  - `Chevrolet Cavalier Hatchback 1984 US`：`尺寸组销量`、`车型销量`
  - `Chevrolet Cavalier Hatchback 1985-1987 US`：`尺寸组销量`、`车型销量`
  - `Chevrolet Cavalier Hatchback 1988 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1982 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1983 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1986 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1988 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1990 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1993-1994 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1995 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1996-1997 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1998-1999 US`：`车型销量`

### `US/店铺/店铺全量_HNT.csv`

- 内容已变化：4378 行 → 4383 行；存于 `A0.尺码计算/artifacts/2026-10-19_07_full-table-cover-shape/output/US/店铺/店铺全量_HNT-20261019_07.csv`。
- 行级差异：新增 9，删除 4，修改 118。
- 变更字段计数：`尺寸组销量` 17，`车型销量` 117。
- 新增示例（最多 10 条）：`Chevrolet Cavalier Coupe 1984-1985 US`；`Chevrolet Cavalier Sedan 1984-1985 US`；`Chevrolet Chevelle Convertible 1966-1967 US`；`Chevrolet Chevelle Coupe 1969-1970 US`；`Chevrolet Chevelle Coupe 1972 US`；`Chevrolet Chevelle Wagon 1965-1967 US`；`Chevrolet Nova Coupe 1975 US`；`Ford Mustang Coupe 1970 US`；`MINI Countryman JCW SUV 2018 US`。
- 删除示例（最多 10 条）：`Chevrolet Cavalier Coupe 1985 US`；`Chevrolet Cavalier Sedan 1984 US`；`Chevrolet Chevelle Convertible 1966 US`；`Chevrolet Chevelle Wagon 1967 US`。
- 修改示例（最多 20 条）：
  - `Chevrolet Cavalier Coupe 1983 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1987 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1989 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1990 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1991-1994 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1996 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1999 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 2000-2005 US`：`车型销量`
  - `Chevrolet Cavalier Hatchback 1984 US`：`尺寸组销量`、`车型销量`
  - `Chevrolet Cavalier Hatchback 1985-1987 US`：`尺寸组销量`、`车型销量`
  - `Chevrolet Cavalier Hatchback 1988 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1982 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1983 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1986 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1988 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1990 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1993-1994 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1995 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1996-1997 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1998-1999 US`：`车型销量`

### `US/店铺/店铺全量_TM.csv`

- 内容已变化：4378 行 → 4383 行；存于 `A0.尺码计算/artifacts/2026-10-19_07_full-table-cover-shape/output/US/店铺/店铺全量_TM-20261019_07.csv`。
- 行级差异：新增 9，删除 4，修改 118。
- 变更字段计数：`尺寸组销量` 17，`车型销量` 117。
- 新增示例（最多 10 条）：`Chevrolet Cavalier Coupe 1984-1985 US`；`Chevrolet Cavalier Sedan 1984-1985 US`；`Chevrolet Chevelle Convertible 1966-1967 US`；`Chevrolet Chevelle Coupe 1969-1970 US`；`Chevrolet Chevelle Coupe 1972 US`；`Chevrolet Chevelle Wagon 1965-1967 US`；`Chevrolet Nova Coupe 1975 US`；`Ford Mustang Coupe 1970 US`；`MINI Countryman JCW SUV 2018 US`。
- 删除示例（最多 10 条）：`Chevrolet Cavalier Coupe 1985 US`；`Chevrolet Cavalier Sedan 1984 US`；`Chevrolet Chevelle Convertible 1966 US`；`Chevrolet Chevelle Wagon 1967 US`。
- 修改示例（最多 20 条）：
  - `Chevrolet Cavalier Coupe 1983 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1987 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1989 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1990 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1991-1994 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1996 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1999 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 2000-2005 US`：`车型销量`
  - `Chevrolet Cavalier Hatchback 1984 US`：`尺寸组销量`、`车型销量`
  - `Chevrolet Cavalier Hatchback 1985-1987 US`：`尺寸组销量`、`车型销量`
  - `Chevrolet Cavalier Hatchback 1988 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1982 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1983 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1986 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1988 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1990 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1993-1994 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1995 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1996-1997 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1998-1999 US`：`车型销量`

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容已变化：4378 行 → 4383 行；存于 `A0.尺码计算/artifacts/2026-10-19_07_full-table-cover-shape/output/US/店铺/店铺全量_TM_拆分-20261019_07.csv`。
- 行级差异：新增 9，删除 4，修改 118。
- 变更字段计数：`尺寸组销量` 17，`车型销量` 117。
- 新增示例（最多 10 条）：`Chevrolet Cavalier Coupe 1984-1985 US`；`Chevrolet Cavalier Sedan 1984-1985 US`；`Chevrolet Chevelle Convertible 1966-1967 US`；`Chevrolet Chevelle Coupe 1969-1970 US`；`Chevrolet Chevelle Coupe 1972 US`；`Chevrolet Chevelle Wagon 1965-1967 US`；`Chevrolet Nova Coupe 1975 US`；`Ford Mustang Coupe 1970 US`；`MINI Countryman JCW SUV 2018 US`。
- 删除示例（最多 10 条）：`Chevrolet Cavalier Coupe 1985 US`；`Chevrolet Cavalier Sedan 1984 US`；`Chevrolet Chevelle Convertible 1966 US`；`Chevrolet Chevelle Wagon 1967 US`。
- 修改示例（最多 20 条）：
  - `Chevrolet Cavalier Coupe 1983 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1987 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1989 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1990 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1991-1994 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1996 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 1999 US`：`车型销量`
  - `Chevrolet Cavalier Coupe 2000-2005 US`：`车型销量`
  - `Chevrolet Cavalier Hatchback 1984 US`：`尺寸组销量`、`车型销量`
  - `Chevrolet Cavalier Hatchback 1985-1987 US`：`尺寸组销量`、`车型销量`
  - `Chevrolet Cavalier Hatchback 1988 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1982 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1983 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1986 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1988 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1990 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1993-1994 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1995 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1996-1997 US`：`车型销量`
  - `Chevrolet Cavalier Sedan 1998-1999 US`：`车型销量`

### `US/TRIM/TRIM适配器.csv`

- 内容已变化：23258 行 → 23258 行；存于 `A0.尺码计算/artifacts/2026-10-19_06_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261019_06.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `US/尺码规则.json`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/尺码规则-20261015_01.json`，未复制。

### `US/店铺货架.json`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/店铺货架-20261015_01.json`，未复制。

### `US/新旧尺码对应.csv`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/新旧尺码对应-20261015_01.csv`，未复制。

### `EU/尺码匹配报告.md`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/EU/尺码匹配报告-20261013_18.md`，未复制。

### `EU/全量/全量表.csv`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv`，未复制。

### `EU/尺码规则.json`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/EU/尺码规则-20261015_01.json`，未复制。

### `RU/尺码匹配报告.md`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/RU/尺码匹配报告-20261013_18.md`，未复制。

### `RU/全量/全量表.csv`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/RU/全量/全量表-20261013_16.csv`，未复制。

### `RU/尺码规则.json`

- 内容未变化；引用 `A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/RU/尺码规则-20261015_01.json`，未复制。
