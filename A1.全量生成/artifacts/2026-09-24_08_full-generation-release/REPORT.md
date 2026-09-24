# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20260924_08`
- 发布时间：`2026-09-24T18:53:48+08:00`
- 工作描述：full-generation 输出刷新。

## 交付物与变更

### `全量表_汇总.csv`

- 内容已变化：47695 行 → 47695 行。
- 行级差异：新增 0，删除 0，修改 16562。
- 变更字段计数：`OZON尺码` 277，`候选` 93，`分类` 277，`前宽-MM` 1270，`参考侧高` 8234，`发货尺码` 133，`后宽-MM` 2417，`插片指数` 1072，`等效长` 473，`自动尺码` 6630，`自动长度余量` 5154，`车形` 283。
- 修改示例（最多 20 条）：
  - `AC 428 Convertible 1965-1974 EU`：`自动尺码`、`自动长度余量`
  - `AC Ace Convertible 1995-1998 EU`：`自动尺码`、`自动长度余量`
  - `AC Ace Convertible 1998-2026 EU`：`自动尺码`、`自动长度余量`
  - `AC Cobra iv 291N Convertible 1997-2026 EU`：`自动尺码`、`自动长度余量`
  - `AMC Hornet Sedan 1969-1970 EU`：`自动尺码`、`自动长度余量`
  - `Acura CL Coupe 1997-1999 US`：`自动尺码`、`自动长度余量`
  - `Acura ILX Sedan 2013-2015 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Coupe 1994 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Coupe 1995-2001 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Hatchback 1986-1989 US`：`自动尺码`
  - `Acura Integra Hatchback 1990 US`：`自动尺码`
  - `Acura Integra Hatchback 1991-1993 US`：`自动尺码`
  - `Acura Integra Hatchback 2023-2026 US`：`自动尺码`
  - `Acura Integra Sedan 1990 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Sedan 1991-1993 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Sedan 1994 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Sedan 1995-2001 US`：`自动尺码`、`自动长度余量`
  - `Acura Integra Type S Hatchback 2024-2026 US`：`自动尺码`
  - `Acura Legend Coupe 1987-1990 US`：`参考侧高`、`自动尺码`
  - `Acura Legend Sedan 1986-1988 US`：`参考侧高`、`自动尺码`、`自动长度余量`

### `TRIM适配器.csv`

- 内容已变化：23324 行 → 23324 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺寸TRIM映射.csv`

- 内容未变化；仅产生新的发布版本。

### `尺码宽高统计.csv`

- 内容已变化：101 行 → 105 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码宽高极值车型.csv`

- 内容已变化：456 行 → 474 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码尺寸异常.csv`

- 内容已变化：2913 行 → 3097 行。
- 行级差异：新增 318，删除 134，修改 1125。
- 变更字段计数：`分类` 8，`宽IQR上界-MM` 913，`宽IQR下界-MM` 913，`宽Z分数` 1001，`异常原因` 113，`自动尺码` 380，`高IQR上界-MM` 709，`高IQR下界-MM` 709，`高Z分数` 1001。
- 新增示例（最多 10 条）：`Acura ILX Sedan 2013-2015 US`；`Alfa Romeo 164 164 Sedan 1994-1998 EU`；`Alfa Romeo 164 Sedan 1992-1997 EU`；`Alfa Romeo 1750-2000 Sedan 1968-1971 EU`；`Alfa Romeo 1750-2000 Sedan 1968-1972 EU`；`Alfa Romeo 2600 Berlina Sedan 1962-1968 RU`；`Alfa Romeo Giulietta 101.28 Sedan 1961-1962 EU`；`Alfa Romeo Giulietta 101.29 Sedan 1961-1962 EU`；`Apollo Arrow Coupe 2016-2026 EU`；`Arcfox Alpha S Liftback 2021-2025 RU`。
- 删除示例（最多 10 条）：`Acura Integra Sedan 1991-1993 US`；`Aistaland GT7 Wagon 2026-2026 RU`；`Alfa Romeo 6 119 Sedan 1980-1984 EU`；`Alfa Romeo 6 119 prefl Sedan 1979-1984 EU`；`Audi e-tron GT/RS e-tron GT Sedan 2022-2024 US`；`Audi e-tron GT/S e-tron GT/RS e-tron GT Sedan 2025-2026 US`；`BMW 315 Roadster 1934-1937 RU`；`BMW 320 320 Convertible 1937-1937 EU`；`BMW 320 320 Convertible 1937-1938 EU`；`BMW 320 320 Convertible 1938-1938 EU`。
- 修改示例（最多 20 条）：
  - `ARO 10 10.1 Convertible 1984-1999 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `ARO Spartana pick up Convertible 1997-2003 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Acura NSX Coupe 1991-1994 US`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`自动尺码`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Acura NSX Coupe 1995 US`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`自动尺码`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Acura NSX Coupe 1996-2005 US`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`自动尺码`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Adler Diplomat Pullman Sedan 1934-1940 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Adler Diplomat Sedan 1934-1940 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Adler Trumpf Junior Sedan 1934-1941 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 105/115 Berlina Sedan 1965-1977 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 1750-2000 105.12 Sedan 1971-1975 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`自动尺码`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alfa Romeo 1900 Berlina Sedan 1950-1959 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 6 Sedan 1979-1988 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Alfa Romeo 6C Convertible 1927-1933 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alfa Romeo Berlina 105 Sedan 1971-1977 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`自动尺码`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alfa Romeo Giulia 952 Sedan 2020-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Alpine A290 Hatchback 2024-2026 RU`：`宽Z分数`、`高Z分数`
  - `Apollo Apollo n Coupe 2016-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`自动尺码`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Arcfox Alpha S5 Sedan 2024-2026 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Asia Topic MPV 1987-1999 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
  - `Aston Martin Lagonda Wagon 1976-1997 RU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高Z分数`
