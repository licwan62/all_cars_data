# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20260924_04`
- 发布时间：`2026-09-24T09:46:34+08:00`
- 工作描述：full-generation 输出刷新。

## 交付物与变更

### `全量表_汇总.csv`

- 内容未变化；仅产生新的发布版本。

### `TRIM适配器.csv`

- 内容未变化；仅产生新的发布版本。

### `尺寸TRIM映射.csv`

- 内容未变化；仅产生新的发布版本。

### `尺码宽高统计.csv`

- 内容已变化：54 行 → 101 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码宽高极值车型.csv`

- 内容已变化：247 行 → 456 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码尺寸异常.csv`

- 内容已变化：2933 行 → 2913 行。
- 行级差异：新增 353，删除 373，修改 2560。
- 变更字段计数：`区域` 2560，`宽IQR上界-MM` 1840，`宽IQR下界-MM` 1857，`宽Z分数` 2016，`异常原因` 316，`高IQR上界-MM` 1969，`高IQR下界-MM` 1964，`高Z分数` 2024。
- 新增示例（最多 10 条）：`Acura NSX Coupe 1991-1994 US`；`Acura NSX Coupe 1995 US`；`Acura NSX Coupe 1996-2005 US`；`Aixam D-Truck Van 2014-2026 EU`；`Aixam D-Truck Van 2015-2026 EU`；`Alfa Romeo 1750-2000 105.12 Sedan 1971-1975 EU`；`Alfa Romeo Berlina 105 Sedan 1971-1977 EU`；`Alpine A290 Hatchback 2024-2026 RU`；`Arcfox Alpha S5 Sedan 2024-2026 RU`；`Aston Martin Rapide Liftback 2018-2026 EU`。
- 删除示例（最多 10 条）：`Acura Integra Sedan 1994 US`；`Alfa Romeo Disco Volante Coupe 2013-2013 RU`；`Aston Martin DB12 Coupe 2023-2026 RU`；`Aston Martin Vanquish Coupe 2024-2026 RU`；`Aston Martin Vanquish Volante Roadster 2012-2018 RU`；`Aston Martin Vanquish Volante Roadster 2024-2026 RU`；`Aston Martin Vulcan Coupe 2015-2016 RU`；`Audi A7/S7/RS7 Liftback 2019-2025 US`；`Audi R8 Coupe 2012-2015 RU`；`Audi R8 LMP Roadster 2000-2005 RU`。
- 修改示例（最多 20 条）：
  - `212 T01 SUV 2024-2026 RU`：`区域`、`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`异常原因`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `212 T10 SUV 2026-2026 RU`：`区域`
  - `AM General HMMWV (Humvee) SUV 1984-2006 RU`：`区域`、`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 10 10.1 Convertible 1984-1999 EU`：`区域`、`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 243 3dr facelift SUV 1978-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 243 3dr facelift SUV 1985-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 243 3dr prefl SUV 1978-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 243 3dr prefl SUV 1985-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 243 SUV 1989-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 244 5dr facelift SUV 1978-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 244 5dr facelift SUV 1985-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 244 5dr prefl SUV 1978-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 244 5dr prefl SUV 1985-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO 240-244 244 SUV 1989-1998 EU`：`区域`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO Spartana pick up Convertible 1997-2003 EU`：`区域`、`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Acura Integra Sedan 1991-1993 US`：`区域`、`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Adler Diplomat Pullman Sedan 1934-1940 RU`：`区域`
  - `Adler Diplomat Sedan 1934-1940 RU`：`区域`
  - `Adler Trumpf Junior Sedan 1934-1941 RU`：`区域`
  - `Aistaland GT7 Wagon 2026-2026 RU`：`区域`
