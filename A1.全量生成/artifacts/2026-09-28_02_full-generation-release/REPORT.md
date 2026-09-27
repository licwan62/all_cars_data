# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20260928_02`
- 发布时间：`2026-09-28T04:35:28+08:00`
- 工作描述：full-generation 输出刷新。

## 规则（data/）

- 与上一版本相同。

## 交付物与变更

### `尺码宽高统计.csv`

- 内容已变化：106 行 → 106 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码宽高极值车型.csv`

- 内容已变化：464 行 → 464 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码尺寸异常.csv`

- 内容已变化：3152 行 → 3179 行。
- 行级差异：新增 65，删除 38，修改 1801。
- 变更字段计数：`分类` 8，`宽IQR上界-MM` 543，`宽IQR下界-MM` 543，`宽Z分数` 1799，`异常原因` 37，`自动尺码` 8，`高IQR上界-MM` 492，`高IQR下界-MM` 492，`高Z分数` 1796。
- 新增示例（最多 10 条）：`Aistaland GT7 Wagon 2026-2026 RU`；`BMW 315 Roadster 1934-1937 RU`；`Cadillac Celestiq Liftback 2024-2026 RU`；`Cadillac SRX Wagon 2004-2009 US`；`Chevrolet Celebrity Wagon 1982-1990 RU`；`Chevrolet Lumina APV Wagon 1993 US`；`Chevrolet Lumina APV Wagon 1994-1996 US`；`Chrysler Voyager Grand MPV 1995-2001 RU`；`Dacia Lodgy MPV 2017-2022 RU`；`Dodge Caravan Grand Caravan MPV 1990 US`。
- 删除示例（最多 10 条）：`Alfa Romeo 2600 Berlina Sedan 1962-1968 RU`；`Arcfox Alpha S Liftback 2021-2025 RU`；`Arcfox Alpha S6 Liftback 2025-2026 RU`；`Aston Martin Rapide Liftback 2018-2026 EU`；`BMW 326 Sedan 1936-1946 RU`；`Baojun RC-6 Liftback 2019-2021 RU`；`Buick Special Wagon 1954-1955 RU`；`Chevrolet Uplander LWB Wagon 2005-2008 US`；`Chevrolet Venture LWB Wagon 1997-2005 US`；`Dodge Dart Sedan 1973-1976 RU`。
- 修改示例（最多 20 条）：
  - `ARO 10 Convertible 1984-1999 EU`：`宽Z分数`、`高Z分数`
  - `ARO Spartana pick up Convertible 1997-2003 EU`：`宽Z分数`、`高Z分数`
  - `Adler Diplomat Pullman Sedan 1934-1940 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Adler Diplomat Sedan 1934-1940 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Adler Trumpf Junior Sedan 1934-1941 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 105/115 Berlina Sedan 1965-1977 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 164 Sedan 1992-1997 EU`：`宽Z分数`、`高Z分数`
  - `Alfa Romeo 164 Sedan 1994-1998 EU`：`宽Z分数`、`高Z分数`
  - `Alfa Romeo 1750-2000 Sedan 1968-1971 EU`：`宽Z分数`、`高Z分数`
  - `Alfa Romeo 1750-2000 Sedan 1968-1972 EU`：`宽Z分数`、`高Z分数`
  - `Alfa Romeo 1750-2000 Sedan 1971-1975 EU`：`宽Z分数`、`高Z分数`
  - `Alfa Romeo 1900 Berlina Sedan 1950-1959 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 6 Sedan 1979-1988 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 6C Convertible 1927-1933 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alfa Romeo Berlina Sedan 1971-1977 EU`：`宽Z分数`、`高Z分数`
  - `Alfa Romeo Giulia Sedan 2020-2026 EU`：`宽Z分数`
  - `Alfa Romeo Giulietta 101.28 Sedan 1961-1962 EU`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alfa Romeo Giulietta 101.29 Sedan 1961-1962 EU`：`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alpina B3 E90 L4545 W1817 H1422 Sedan 2010-2013 EU`：`宽Z分数`、`高Z分数`
  - `Alpina B3 E90 L4545 W1817 H1437 Sedan 2010-2013 EU`：`宽Z分数`、`高Z分数`
