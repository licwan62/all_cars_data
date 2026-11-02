# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261102_11`
- 发布时间：`2026-11-02T09:06:38+08:00`
- 发布原因：交付物变化：EU/尺码匹配报告.md、RU/尺码匹配报告.md、US/全量/全量表.csv、US/尺码匹配报告.md、US/店铺/店铺全量_HNT.csv、US/店铺/店铺全量_TM.csv、US/店铺/店铺全量_TM_拆分.csv；上游输入变化；规则变化（）。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_02`：运行批次实际读取，12 个文件。
- `structure-review` `20261102_02`：运行批次实际读取，4 个文件。
- `shape-classification` `20261102_03`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261102_04`：运行批次实际读取，5 个文件。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_10_match-report-shape/output/US/尺码匹配报告-20261102_10.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/全量/全量表.csv`

- 内容已变化：4475 行 → 4740 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_09_us-market-potential/output/US/全量/全量表-20261102_09.csv`。
- 行级差异：新增 265，删除 0，修改 50。
- 变更字段计数：`市场潜力` 10，`车型销量` 47，`销量潜力调整` 10。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。
- 修改示例（最多 20 条）：
  - `Cadillac Lyriq Lyriq-V SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2023-2025 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Ford Explorer SUV 1991-1994 US`：`车型销量`
  - `Ford Explorer SUV 1995-1997 US`：`车型销量`
  - `Ford Explorer SUV 1998 US`：`车型销量`
  - `Ford Explorer SUV 1999-2000 US`：`车型销量`
  - `Ford Explorer SUV 2001 US`：`车型销量`
  - `Ford Explorer SUV 2002 US`：`车型销量`
  - `Ford Explorer SUV 2003-2005 US`：`车型销量`
  - `Ford Explorer SUV 2006 US`：`车型销量`
  - `Ford Explorer SUV 2007-2010 US`：`车型销量`
  - `Ford Explorer SUV 2011-2015 US`：`车型销量`
  - `Ford Explorer SUV 2016-2018 US`：`车型销量`
  - `Ford Explorer SUV 2020-2024 US`：`车型销量`
  - `Ford Explorer SUV 2025 US`：`车型销量`
  - `Ford Explorer Timberline SUV 2023-2024 US`：`车型销量`
  - `Honda HR-V SUV 2016-2018 US`：`车型销量`
  - `Honda HR-V SUV 2019-2021 US`：`车型销量`
  - `Honda HR-V SUV 2023-2026 US`：`车型销量`

### `US/店铺/店铺全量_HNT.csv`

- 内容已变化：4475 行 → 4740 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_09_us-market-potential/output/US/店铺/店铺全量_HNT-20261102_09.csv`。
- 行级差异：新增 265，删除 0，修改 50。
- 变更字段计数：`市场潜力` 10，`车型销量` 47，`销量潜力调整` 10。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。
- 修改示例（最多 20 条）：
  - `Cadillac Lyriq Lyriq-V SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2023-2025 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Ford Explorer SUV 1991-1994 US`：`车型销量`
  - `Ford Explorer SUV 1995-1997 US`：`车型销量`
  - `Ford Explorer SUV 1998 US`：`车型销量`
  - `Ford Explorer SUV 1999-2000 US`：`车型销量`
  - `Ford Explorer SUV 2001 US`：`车型销量`
  - `Ford Explorer SUV 2002 US`：`车型销量`
  - `Ford Explorer SUV 2003-2005 US`：`车型销量`
  - `Ford Explorer SUV 2006 US`：`车型销量`
  - `Ford Explorer SUV 2007-2010 US`：`车型销量`
  - `Ford Explorer SUV 2011-2015 US`：`车型销量`
  - `Ford Explorer SUV 2016-2018 US`：`车型销量`
  - `Ford Explorer SUV 2020-2024 US`：`车型销量`
  - `Ford Explorer SUV 2025 US`：`车型销量`
  - `Ford Explorer Timberline SUV 2023-2024 US`：`车型销量`
  - `Honda HR-V SUV 2016-2018 US`：`车型销量`
  - `Honda HR-V SUV 2019-2021 US`：`车型销量`
  - `Honda HR-V SUV 2023-2026 US`：`车型销量`

### `US/店铺/店铺全量_TM.csv`

- 内容已变化：4475 行 → 4740 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_09_us-market-potential/output/US/店铺/店铺全量_TM-20261102_09.csv`。
- 行级差异：新增 265，删除 0，修改 50。
- 变更字段计数：`市场潜力` 10，`车型销量` 47，`销量潜力调整` 10。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。
- 修改示例（最多 20 条）：
  - `Cadillac Lyriq Lyriq-V SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2023-2025 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Ford Explorer SUV 1991-1994 US`：`车型销量`
  - `Ford Explorer SUV 1995-1997 US`：`车型销量`
  - `Ford Explorer SUV 1998 US`：`车型销量`
  - `Ford Explorer SUV 1999-2000 US`：`车型销量`
  - `Ford Explorer SUV 2001 US`：`车型销量`
  - `Ford Explorer SUV 2002 US`：`车型销量`
  - `Ford Explorer SUV 2003-2005 US`：`车型销量`
  - `Ford Explorer SUV 2006 US`：`车型销量`
  - `Ford Explorer SUV 2007-2010 US`：`车型销量`
  - `Ford Explorer SUV 2011-2015 US`：`车型销量`
  - `Ford Explorer SUV 2016-2018 US`：`车型销量`
  - `Ford Explorer SUV 2020-2024 US`：`车型销量`
  - `Ford Explorer SUV 2025 US`：`车型销量`
  - `Ford Explorer Timberline SUV 2023-2024 US`：`车型销量`
  - `Honda HR-V SUV 2016-2018 US`：`车型销量`
  - `Honda HR-V SUV 2019-2021 US`：`车型销量`
  - `Honda HR-V SUV 2023-2026 US`：`车型销量`

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容已变化：4475 行 → 4740 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_09_us-market-potential/output/US/店铺/店铺全量_TM_拆分-20261102_09.csv`。
- 行级差异：新增 265，删除 0，修改 50。
- 变更字段计数：`市场潜力` 10，`车型销量` 47，`销量潜力调整` 10。
- 新增示例（最多 10 条）：`Acura RDX SUV 2019 US`；`Audi A3 Hatchback 2027 US`；`Audi A5 Sedan 2027 US`；`Audi A6 e-tron Sedan 2027 US`；`Audi A8 Sedan 2027 US`；`Audi Q3 SUV 2027 US`；`Audi Q6 e-tron SUV 2025 US`；`Audi Q6 e-tron SUV 2027 US`；`Audi Q8 SUV 2027 US`；`Audi RS Q8 SUV 2027 US`。
- 修改示例（最多 20 条）：
  - `Cadillac Lyriq Lyriq-V SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2023-2025 US`：`市场潜力`、`销量潜力调整`
  - `Cadillac Lyriq SUV 2026 US`：`市场潜力`、`销量潜力调整`
  - `Ford Explorer SUV 1991-1994 US`：`车型销量`
  - `Ford Explorer SUV 1995-1997 US`：`车型销量`
  - `Ford Explorer SUV 1998 US`：`车型销量`
  - `Ford Explorer SUV 1999-2000 US`：`车型销量`
  - `Ford Explorer SUV 2001 US`：`车型销量`
  - `Ford Explorer SUV 2002 US`：`车型销量`
  - `Ford Explorer SUV 2003-2005 US`：`车型销量`
  - `Ford Explorer SUV 2006 US`：`车型销量`
  - `Ford Explorer SUV 2007-2010 US`：`车型销量`
  - `Ford Explorer SUV 2011-2015 US`：`车型销量`
  - `Ford Explorer SUV 2016-2018 US`：`车型销量`
  - `Ford Explorer SUV 2020-2024 US`：`车型销量`
  - `Ford Explorer SUV 2025 US`：`车型销量`
  - `Ford Explorer Timberline SUV 2023-2024 US`：`车型销量`
  - `Honda HR-V SUV 2016-2018 US`：`车型销量`
  - `Honda HR-V SUV 2019-2021 US`：`车型销量`
  - `Honda HR-V SUV 2023-2026 US`：`车型销量`

### `US/TRIM/TRIM适配器.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_06_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261019_06.csv`，未复制。

### `US/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/尺码规则-20261015_01.json`，未复制。

### `US/店铺货架.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/店铺货架-20261015_01.json`，未复制。

### `US/新旧尺码对应.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_02_match-report-shape/output/US/新旧尺码对应-20261028_02.csv`，未复制。

### `EU/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_10_match-report-shape/output/EU/尺码匹配报告-20261102_10.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `EU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv`，未复制。

### `EU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/EU/尺码规则-20261015_01.json`，未复制。

### `RU/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_10_match-report-shape/output/RU/尺码匹配报告-20261102_10.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `RU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_04_full-table-cover-shape/output/RU/全量/全量表-20261101_04.csv`，未复制。

### `RU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码规则-20261026_02.json`，未复制。
