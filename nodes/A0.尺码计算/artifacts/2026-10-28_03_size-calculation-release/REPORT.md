# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261028_03`
- 发布时间：`2026-10-28T15:38:14+08:00`
- 发布原因：交付物变化：US/全量/全量表.csv、US/尺码匹配报告.md、US/店铺/店铺全量_HNT.csv、US/店铺/店铺全量_TM.csv、US/店铺/店铺全量_TM_拆分.csv、US/新旧尺码对应.csv；上游输入变化；规则变化（修改 data/参考/新旧尺码对应/新旧尺码对应2.csv；删除 data/商业潜力调整/参数.json, data/商业潜力调整/来源.json, data/商业潜力调整/积加销量.csv, data/商业潜力调整/竞品车罩销量统计表.csv）；pending/发布说明变化。

## 规则（data/）

- 相对上一版本：修改 data/参考/新旧尺码对应/新旧尺码对应2.csv；删除 data/商业潜力调整/参数.json, data/商业潜力调整/来源.json, data/商业潜力调整/积加销量.csv, data/商业潜力调整/竞品车罩销量统计表.csv。

## 上游输入依据

- `dimension-library` `20261009_08`：运行批次实际读取，7 个文件。
- `structure-review` `20261019_02`：运行批次实际读取，4 个文件。
- `shape-classification` `20261019_04`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261028_02`：运行批次实际读取，3 个文件。
- 无运行记录可核实的交付物：`RU/全量/全量表.csv`。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-28_02_match-report-shape/output/US/尺码匹配报告-20261028_02.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/全量/全量表.csv`

- 内容已变化：4383 行 → 4383 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/全量/全量表-20261028_01.csv`。
- 行级差异：新增 0，删除 0，修改 4383。
- 变更字段计数：`销量潜力调整` 4383。
- 修改示例（最多 20 条）：
  - `Acura ADX SUV 2025-2026 US`：`销量潜力调整`
  - `Acura CL Coupe 1997-1999 US`：`销量潜力调整`
  - `Acura CL Coupe 2001-2003 US`：`销量潜力调整`
  - `Acura ILX Sedan 2013-2015 US`：`销量潜力调整`
  - `Acura ILX Sedan 2016-2018 US`：`销量潜力调整`
  - `Acura ILX Sedan 2019-2022 US`：`销量潜力调整`
  - `Acura Integra Coupe 1994 US`：`销量潜力调整`
  - `Acura Integra Coupe 1995-2001 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1986-1989 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1990 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1991-1993 US`：`销量潜力调整`
  - `Acura Integra Hatchback 2023-2026 US`：`销量潜力调整`
  - `Acura Integra Sedan 1990 US`：`销量潜力调整`
  - `Acura Integra Sedan 1991-1993 US`：`销量潜力调整`
  - `Acura Integra Sedan 1994 US`：`销量潜力调整`
  - `Acura Integra Sedan 1995-2001 US`：`销量潜力调整`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`销量潜力调整`
  - `Acura Legend Coupe 1987-1990 US`：`销量潜力调整`
  - `Acura Legend Coupe 1991-1995 US`：`销量潜力调整`
  - `Acura Legend Sedan 1986-1988 US`：`销量潜力调整`

### `US/店铺/店铺全量_HNT.csv`

- 内容已变化：4383 行 → 4383 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/店铺/店铺全量_HNT-20261028_01.csv`。
- 行级差异：新增 0，删除 0，修改 4383。
- 变更字段计数：`销量潜力调整` 4383。
- 修改示例（最多 20 条）：
  - `Acura ADX SUV 2025-2026 US`：`销量潜力调整`
  - `Acura CL Coupe 1997-1999 US`：`销量潜力调整`
  - `Acura CL Coupe 2001-2003 US`：`销量潜力调整`
  - `Acura ILX Sedan 2013-2015 US`：`销量潜力调整`
  - `Acura ILX Sedan 2016-2018 US`：`销量潜力调整`
  - `Acura ILX Sedan 2019-2022 US`：`销量潜力调整`
  - `Acura Integra Coupe 1994 US`：`销量潜力调整`
  - `Acura Integra Coupe 1995-2001 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1986-1989 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1990 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1991-1993 US`：`销量潜力调整`
  - `Acura Integra Hatchback 2023-2026 US`：`销量潜力调整`
  - `Acura Integra Sedan 1990 US`：`销量潜力调整`
  - `Acura Integra Sedan 1991-1993 US`：`销量潜力调整`
  - `Acura Integra Sedan 1994 US`：`销量潜力调整`
  - `Acura Integra Sedan 1995-2001 US`：`销量潜力调整`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`销量潜力调整`
  - `Acura Legend Coupe 1987-1990 US`：`销量潜力调整`
  - `Acura Legend Coupe 1991-1995 US`：`销量潜力调整`
  - `Acura Legend Sedan 1986-1988 US`：`销量潜力调整`

### `US/店铺/店铺全量_TM.csv`

- 内容已变化：4383 行 → 4383 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/店铺/店铺全量_TM-20261028_01.csv`。
- 行级差异：新增 0，删除 0，修改 4383。
- 变更字段计数：`销量潜力调整` 4383。
- 修改示例（最多 20 条）：
  - `Acura ADX SUV 2025-2026 US`：`销量潜力调整`
  - `Acura CL Coupe 1997-1999 US`：`销量潜力调整`
  - `Acura CL Coupe 2001-2003 US`：`销量潜力调整`
  - `Acura ILX Sedan 2013-2015 US`：`销量潜力调整`
  - `Acura ILX Sedan 2016-2018 US`：`销量潜力调整`
  - `Acura ILX Sedan 2019-2022 US`：`销量潜力调整`
  - `Acura Integra Coupe 1994 US`：`销量潜力调整`
  - `Acura Integra Coupe 1995-2001 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1986-1989 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1990 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1991-1993 US`：`销量潜力调整`
  - `Acura Integra Hatchback 2023-2026 US`：`销量潜力调整`
  - `Acura Integra Sedan 1990 US`：`销量潜力调整`
  - `Acura Integra Sedan 1991-1993 US`：`销量潜力调整`
  - `Acura Integra Sedan 1994 US`：`销量潜力调整`
  - `Acura Integra Sedan 1995-2001 US`：`销量潜力调整`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`销量潜力调整`
  - `Acura Legend Coupe 1987-1990 US`：`销量潜力调整`
  - `Acura Legend Coupe 1991-1995 US`：`销量潜力调整`
  - `Acura Legend Sedan 1986-1988 US`：`销量潜力调整`

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容已变化：4383 行 → 4383 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-28_01_us-market-potential/output/US/店铺/店铺全量_TM_拆分-20261028_01.csv`。
- 行级差异：新增 0，删除 0，修改 4383。
- 变更字段计数：`销量潜力调整` 4383。
- 修改示例（最多 20 条）：
  - `Acura ADX SUV 2025-2026 US`：`销量潜力调整`
  - `Acura CL Coupe 1997-1999 US`：`销量潜力调整`
  - `Acura CL Coupe 2001-2003 US`：`销量潜力调整`
  - `Acura ILX Sedan 2013-2015 US`：`销量潜力调整`
  - `Acura ILX Sedan 2016-2018 US`：`销量潜力调整`
  - `Acura ILX Sedan 2019-2022 US`：`销量潜力调整`
  - `Acura Integra Coupe 1994 US`：`销量潜力调整`
  - `Acura Integra Coupe 1995-2001 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1986-1989 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1990 US`：`销量潜力调整`
  - `Acura Integra Hatchback 1991-1993 US`：`销量潜力调整`
  - `Acura Integra Hatchback 2023-2026 US`：`销量潜力调整`
  - `Acura Integra Sedan 1990 US`：`销量潜力调整`
  - `Acura Integra Sedan 1991-1993 US`：`销量潜力调整`
  - `Acura Integra Sedan 1994 US`：`销量潜力调整`
  - `Acura Integra Sedan 1995-2001 US`：`销量潜力调整`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`销量潜力调整`
  - `Acura Legend Coupe 1987-1990 US`：`销量潜力调整`
  - `Acura Legend Coupe 1991-1995 US`：`销量潜力调整`
  - `Acura Legend Sedan 1986-1988 US`：`销量潜力调整`

### `US/TRIM/TRIM适配器.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_06_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261019_06.csv`，未复制。

### `US/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/尺码规则-20261015_01.json`，未复制。

### `US/店铺货架.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/店铺货架-20261015_01.json`，未复制。

### `US/新旧尺码对应.csv`

- 内容已变化：35 行 → 35 行；存于 `nodes/A0.尺码计算/artifacts/2026-10-28_02_match-report-shape/output/US/新旧尺码对应-20261028_02.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `EU/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_18_size-calculation-release/output/EU/尺码匹配报告-20261013_18.md`，未复制。

### `EU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv`，未复制。

### `EU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/EU/尺码规则-20261015_01.json`，未复制。

### `RU/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码匹配报告-20261026_02.md`，未复制。

### `RU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_03_size-calculation-release/output/RU/全量/全量表-20261026_03.csv`，未复制。

### `RU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码规则-20261026_02.json`，未复制。
