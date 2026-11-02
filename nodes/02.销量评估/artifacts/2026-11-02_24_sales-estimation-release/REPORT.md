# 发布报告

- 节点：`sales-estimation`（`nodes/02.销量评估`）
- 版本：`20261102_24`
- 发布时间：`2026-11-02T19:47:25+08:00`
- 发布原因：交付物变化：原子销量.csv、原子销量待核.csv、市场潜力.csv；上游输入变化。

## 规则（data/）

- 与上一版本相同。

## 上游输入依据

- `dimension-library` `20261102_17`：运行批次实际读取，4 个文件。
- `dimension-crawler` `20261102_01`：运行批次实际读取，1 个文件。

## 身份承接

- `原子销量.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。
- `RU代理销量.csv` ← `dimension-library` `尺寸库_RU.csv`（equal）：通过。
- `市场潜力.csv` ← `dimension-library` `尺寸库_US.csv`（equal）：通过。

## 交付物与变更

### `原子销量.csv`

- 内容已变化：15677 行 → 17175 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_21_atomic-sales/output/原子销量-20261102_21.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `原子销量待核.csv`

- 内容已变化：432 行 → 1925 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_21_atomic-sales/output/原子销量待核-20261102_21.csv`。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `RU代理销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-09_04_sales-estimation-release/output/RU代理销量-20261009_04.csv`，未复制。

### `市场潜力.csv`

- 内容已变化：4837 行 → 6335 行；存于 `nodes/02.销量评估/artifacts/2026-11-02_23_us-market-potential/output/市场潜力-20261102_23.csv`。
- 行级差异：新增 1498，删除 0，修改 33。
- 变更字段计数：`市场潜力` 33，`销量潜力调整` 33。
- 新增示例（最多 10 条）：`AMC Alliance Sedan 1983 US`；`AMC Alliance Sedan 1984 US`；`AMC Alliance Sedan 1985 US`；`AMC Alliance Sedan 1986 US`；`AMC Alliance Sedan 1987 US`；`AMC Ambassador Sedan 1963 US`；`AMC Ambassador Sedan 1964 US`；`AMC Ambassador Sedan 1967 US`；`AMC Ambassador Sedan 1968 US`；`AMC Eagle Hatchback 1980 US`。
- 修改示例（最多 20 条）：
  - `Audi A8 Sedan 2027 US`：`市场潜力`、`销量潜力调整`
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
  - `Chevrolet Suburban SUV 1998 US`：`市场潜力`、`销量潜力调整`
  - `Chevrolet Suburban SUV 1999 US`：`市场潜力`、`销量潜力调整`

### `积加销量.csv`

- 内容未变化；引用 `nodes/02.销量评估/artifacts/2026-10-28_01_us-market-potential/rules/data/商业潜力调整/积加销量.csv`，未复制。
