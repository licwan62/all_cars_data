# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20260927_04`
- 发布时间：`2026-09-27T03:11:05+08:00`
- 工作描述：full-generation 输出刷新。

## 规则（data/）

- 与上一版本相同。

## 交付物与变更

### `尺码宽高统计.csv`

- 内容已变化：106 行 → 106 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码宽高极值车型.csv`

- 内容已变化：481 行 → 464 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码尺寸异常.csv`

- 内容已变化：3115 行 → 3150 行。
- 行级差异：新增 1302，删除 1267，修改 560。
- 变更字段计数：`L-MM` 1，`代际` 1，`宽IQR上界-MM` 316，`宽IQR下界-MM` 316，`宽Z分数` 560，`异常原因` 22，`高IQR上界-MM` 454，`高IQR下界-MM` 454，`高Z分数` 560。
- 新增示例（最多 10 条）：`ARO 10 Convertible 1984-1999 EU`；`ARO 240-244 3dr SUV 1989-1998 EU`；`ARO 240-244 3dr facelift SUV 1978-1998 EU`；`ARO 240-244 3dr facelift SUV 1985-1998 EU`；`ARO 240-244 3dr prefl SUV 1978-1998 EU`；`ARO 240-244 3dr prefl SUV 1985-1998 EU`；`ARO 240-244 5dr SUV 1989-1998 EU`；`ARO 240-244 5dr facelift SUV 1978-1998 EU`；`ARO 240-244 5dr facelift SUV 1985-1998 EU`；`ARO 240-244 5dr prefl SUV 1978-1998 EU`。
- 删除示例（最多 10 条）：`ARO 10 10.1 Convertible 1984-1999 EU`；`ARO 240-244 243 3dr facelift SUV 1978-1998 EU`；`ARO 240-244 243 3dr facelift SUV 1985-1998 EU`；`ARO 240-244 243 3dr prefl SUV 1978-1998 EU`；`ARO 240-244 243 3dr prefl SUV 1985-1998 EU`；`ARO 240-244 243 SUV 1989-1998 EU`；`ARO 240-244 244 5dr facelift SUV 1978-1998 EU`；`ARO 240-244 244 5dr facelift SUV 1985-1998 EU`；`ARO 240-244 244 5dr prefl SUV 1978-1998 EU`；`ARO 240-244 244 5dr prefl SUV 1985-1998 EU`。
- 修改示例（最多 20 条）：
  - `ARO Spartana pick up Convertible 1997-2003 EU`：`宽Z分数`、`高Z分数`
  - `Aixam D-Truck Van 2014-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aixam D-Truck Van 2015-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alfa Romeo 164 Sedan 1992-1997 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alfa Romeo 1750-2000 Sedan 1968-1971 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 1750-2000 Sedan 1968-1972 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo Giulietta 101.28 Sedan 1961-1962 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alfa Romeo Giulietta 101.29 Sedan 1961-1962 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Apollo Apollo n Coupe 2016-2026 EU`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Apollo Arrow Coupe 2016-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Lagonda i Sedan 1976-1997 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Rapide Liftback 2018-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Aston Martin Valhalla Coupe 2024-2026 EU`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Valhalla Coupe 2026-2026 EU`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Valkyrie Coupe 2021-2026 EU`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Vanquish Convertible 2025-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Vanquish Coupe 2024-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Virage saloon Sedan 1994-1995 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Virage saloon Sedan 1995-1995 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Audi A3 8YS L4542 W1851 H1412 Sedan 2021-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
