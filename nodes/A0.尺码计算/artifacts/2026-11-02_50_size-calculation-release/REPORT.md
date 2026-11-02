# 发布报告

- 节点：`size-calculation`（`nodes/A0.尺码计算`）
- 版本：`20261102_50`
- 发布时间：`2026-11-02T19:48:45+08:00`
- 发布原因：交付物变化：US/全量/全量表.csv、US/尺码匹配报告.md、US/店铺/店铺全量_HNT.csv、US/店铺/店铺全量_TM.csv、US/店铺/店铺全量_TM_拆分.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_17`：运行批次实际读取，12 个文件。
- `structure-review` `20261102_12`：运行批次实际读取，4 个文件。
- `shape-classification` `20261102_18`：运行批次实际读取，5 个文件。
- `sales-estimation` `20261102_24`：运行批次实际读取，5 个文件。

## 身份承接

- `US/全量/全量表.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `EU/全量/全量表.csv` ← `dimension-library` `尺寸库_EU.csv`（equal）：通过。
- `RU/全量/全量表.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。

## 交付物与变更

### `US/尺码匹配报告.md`

- 内容已变化：None 行 → None 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_49_match-report-shape/output/US/尺码匹配报告-20261102_49.md`。
- 非 CSV 交付物，记录 checksum 变化，未生成内容差异。

### `US/全量/全量表.csv`

- 内容已变化：4837 行 → 6335 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_48_us-market-potential/output/US/全量/全量表-20261102_48.csv`。
- 行级差异：新增 1498，删除 0，修改 35。
- 变更字段计数：`市场潜力` 33，`车型销量` 3，`销量潜力调整` 33。
- 新增示例（最多 10 条）：`AMC Alliance Sedan 1983 US`；`AMC Alliance Sedan 1984 US`；`AMC Alliance Sedan 1985 US`；`AMC Alliance Sedan 1986 US`；`AMC Alliance Sedan 1987 US`；`AMC Ambassador Sedan 1963 US`；`AMC Ambassador Sedan 1964 US`；`AMC Ambassador Sedan 1967 US`；`AMC Ambassador Sedan 1968 US`；`AMC Eagle Hatchback 1980 US`。
- 修改示例（最多 20 条）：
  - `Audi A6 Sedan 1998-2000 US`：`车型销量`
  - `Audi A6 Sedan 2026 US`：`车型销量`
  - `Audi A8 Sedan 2027 US`：`市场潜力`、`车型销量`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1935-1940 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1941 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1946 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1947-1954 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1955-1959 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1960-1966 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1967-1969 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1970-1972 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1973-1980 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1981 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1982-1989 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1990-1991 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1992 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1993-1994 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1995 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1996 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1997 US`：`市场潜力`、`销量潜力调整`

### `US/店铺/店铺全量_HNT.csv`

- 内容已变化：4837 行 → 6335 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_48_us-market-potential/output/US/店铺/店铺全量_HNT-20261102_48.csv`。
- 行级差异：新增 1498，删除 0，修改 35。
- 变更字段计数：`市场潜力` 33，`车型销量` 3，`销量潜力调整` 33。
- 新增示例（最多 10 条）：`AMC Alliance Sedan 1983 US`；`AMC Alliance Sedan 1984 US`；`AMC Alliance Sedan 1985 US`；`AMC Alliance Sedan 1986 US`；`AMC Alliance Sedan 1987 US`；`AMC Ambassador Sedan 1963 US`；`AMC Ambassador Sedan 1964 US`；`AMC Ambassador Sedan 1967 US`；`AMC Ambassador Sedan 1968 US`；`AMC Eagle Hatchback 1980 US`。
- 修改示例（最多 20 条）：
  - `Audi A6 Sedan 1998-2000 US`：`车型销量`
  - `Audi A6 Sedan 2026 US`：`车型销量`
  - `Audi A8 Sedan 2027 US`：`市场潜力`、`车型销量`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1935-1940 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1941 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1946 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1947-1954 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1955-1959 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1960-1966 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1967-1969 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1970-1972 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1973-1980 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1981 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1982-1989 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1990-1991 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1992 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1993-1994 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1995 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1996 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1997 US`：`市场潜力`、`销量潜力调整`

### `US/店铺/店铺全量_TM.csv`

- 内容已变化：4837 行 → 6335 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_48_us-market-potential/output/US/店铺/店铺全量_TM-20261102_48.csv`。
- 行级差异：新增 1498，删除 0，修改 35。
- 变更字段计数：`市场潜力` 33，`车型销量` 3，`销量潜力调整` 33。
- 新增示例（最多 10 条）：`AMC Alliance Sedan 1983 US`；`AMC Alliance Sedan 1984 US`；`AMC Alliance Sedan 1985 US`；`AMC Alliance Sedan 1986 US`；`AMC Alliance Sedan 1987 US`；`AMC Ambassador Sedan 1963 US`；`AMC Ambassador Sedan 1964 US`；`AMC Ambassador Sedan 1967 US`；`AMC Ambassador Sedan 1968 US`；`AMC Eagle Hatchback 1980 US`。
- 修改示例（最多 20 条）：
  - `Audi A6 Sedan 1998-2000 US`：`车型销量`
  - `Audi A6 Sedan 2026 US`：`车型销量`
  - `Audi A8 Sedan 2027 US`：`市场潜力`、`车型销量`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1935-1940 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1941 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1946 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1947-1954 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1955-1959 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1960-1966 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1967-1969 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1970-1972 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1973-1980 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1981 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1982-1989 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1990-1991 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1992 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1993-1994 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1995 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1996 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1997 US`：`市场潜力`、`销量潜力调整`

### `US/店铺/店铺全量_TM_拆分.csv`

- 内容已变化：4837 行 → 6335 行；存于 `nodes/A0.尺码计算/artifacts/2026-11-02_48_us-market-potential/output/US/店铺/店铺全量_TM_拆分-20261102_48.csv`。
- 行级差异：新增 1498，删除 0，修改 35。
- 变更字段计数：`市场潜力` 33，`车型销量` 3，`销量潜力调整` 33。
- 新增示例（最多 10 条）：`AMC Alliance Sedan 1983 US`；`AMC Alliance Sedan 1984 US`；`AMC Alliance Sedan 1985 US`；`AMC Alliance Sedan 1986 US`；`AMC Alliance Sedan 1987 US`；`AMC Ambassador Sedan 1963 US`；`AMC Ambassador Sedan 1964 US`；`AMC Ambassador Sedan 1967 US`；`AMC Ambassador Sedan 1968 US`；`AMC Eagle Hatchback 1980 US`。
- 修改示例（最多 20 条）：
  - `Audi A6 Sedan 1998-2000 US`：`车型销量`
  - `Audi A6 Sedan 2026 US`：`车型销量`
  - `Audi A8 Sedan 2027 US`：`市场潜力`、`车型销量`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1935-1940 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1941 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1946 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1947-1954 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1955-1959 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1960-1966 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1967-1969 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1970-1972 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1973-1980 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1981 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1982-1989 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1990-1991 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1992 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1993-1994 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1995 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1996 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1997 US`：`市场潜力`、`销量潜力调整`

### `US/TRIM/TRIM适配器.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-19_06_us-size-trim-shape/output/US/TRIM/TRIM适配器-20261019_06.csv`，未复制。

### `US/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/尺码规则-20261015_01.json`，未复制。

### `US/店铺货架.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/US/店铺货架-20261015_01.json`，未复制。

### `US/新旧尺码对应.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-28_02_match-report-shape/output/US/新旧尺码对应-20261028_02.csv`，未复制。

### `EU/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-02_10_match-report-shape/output/EU/尺码匹配报告-20261102_10.md`，未复制。

### `EU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-13_16_full-table-cover-shape/output/EU/全量/全量表-20261013_16.csv`，未复制。

### `EU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-15_01_match-report-shape/output/EU/尺码规则-20261015_01.json`，未复制。

### `RU/尺码匹配报告.md`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-02_10_match-report-shape/output/RU/尺码匹配报告-20261102_10.md`，未复制。

### `RU/全量/全量表.csv`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-11-01_04_full-table-cover-shape/output/RU/全量/全量表-20261101_04.csv`，未复制。

### `RU/尺码规则.json`

- 内容未变化；引用 `nodes/A0.尺码计算/artifacts/2026-10-26_02_match-report-shape/output/RU/尺码规则-20261026_02.json`，未复制。
