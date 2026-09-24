# 发布报告

- 节点：`full-generation`（`A1.全量生成`）
- 版本：`20260924_12`
- 发布时间：`2026-09-24T20:38:55+08:00`
- 工作描述：full-generation 输出刷新。

## 交付物与变更

### `全量表_汇总.csv`

- 内容已变化：47695 行 → 47695 行。
- 行级差异：新增 0，删除 0，修改 3699。
- 变更字段计数：`候选` 6，`原因` 6，`相差数值` 6，`自动尺码` 3699，`自动长度余量` 209。
- 修改示例（最多 20 条）：
  - `Acura CL Coupe 1997-1999 US`：`自动尺码`、`自动长度余量`
  - `Acura Legend Sedan 1986-1988 US`：`自动尺码`、`自动长度余量`
  - `Acura TL Type-S Sedan 2004-2008 US`：`自动尺码`、`自动长度余量`
  - `Acura TLX Sedan 2015-2017 US`：`自动尺码`、`自动长度余量`
  - `Alfa Romeo 146 930 Hatchback 1994-1996 EU`：`自动尺码`
  - `Alfa Romeo 146 930 Hatchback 1994-1999 EU`：`自动尺码`
  - `Alfa Romeo 146 930 Hatchback 1995-2001 EU`：`自动尺码`
  - `Alfa Romeo 146 930 Hatchback 1996-2001 EU`：`自动尺码`
  - `Alfa Romeo 146 930 Hatchback 1997-2001 EU`：`自动尺码`
  - `Alfa Romeo 146 930 Hatchback 1998-2001 EU`：`自动尺码`
  - `Alfa Romeo 146 930B Hatchback 1999-2001 EU`：`自动尺码`
  - `Alfa Romeo 146 930B facelift Hatchback 1997-2000 EU`：`自动尺码`
  - `Alfa Romeo 146 930B prefl Hatchback 1997-2000 EU`：`自动尺码`
  - `Alfa Romeo 147 937 3dr Hatchback 2004-2010 EU`：`自动尺码`
  - `Alfa Romeo 147 937 3dr facelift Hatchback 2001-2009 EU`：`自动尺码`
  - `Alfa Romeo 147 937 3dr facelift Hatchback 2001-2010 EU`：`自动尺码`
  - `Alfa Romeo 147 937 3dr facelift Hatchback 2002-2010 EU`：`自动尺码`
  - `Alfa Romeo 147 937 3dr facelift Hatchback 2003-2010 EU`：`自动尺码`
  - `Alfa Romeo 147 937 3dr prefl Hatchback 2001-2009 EU`：`自动尺码`
  - `Alfa Romeo 147 937 3dr prefl Hatchback 2002-2010 EU`：`自动尺码`

### `TRIM适配器.csv`

- 内容已变化：23324 行 → 23324 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺寸TRIM映射.csv`

- 内容未变化；仅产生新的发布版本。

### `尺码宽高统计.csv`

- 内容已变化：105 行 → 106 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码宽高极值车型.csv`

- 内容已变化：474 行 → 481 行。
- CSV 内容已变化；缺少可唯一定位的 `DIMENSION-ID`，未生成行级差异。

### `尺码尺寸异常.csv`

- 内容已变化：3097 行 → 3115 行。
- 行级差异：新增 18，删除 0，修改 241。
- 变更字段计数：`宽IQR上界-MM` 48，`宽IQR下界-MM` 48，`宽Z分数` 74，`异常原因` 9，`自动尺码` 170，`高IQR上界-MM` 48，`高IQR下界-MM` 48，`高Z分数` 74。
- 新增示例（最多 10 条）：`Audi e-tron GT/RS e-tron GT Sedan 2022-2024 US`；`Audi e-tron GT/S e-tron GT/RS e-tron GT Sedan 2025-2026 US`；`BMW 5 Series Sedan 1989-1995 US`；`Buick Skylark Coupe 1992 US`；`Buick Skylark Coupe 1993 US`；`Buick Skylark Sedan 1992 US`；`Buick Skylark Sedan 1993 US`；`Chevrolet Nova Sedan 1967 US`；`Chrysler Cirrus Sedan 1998 US`；`Hyundai Sonata Sedan 1989-1993 US`。
- 修改示例（最多 20 条）：
  - `Apollo Arrow Coupe 2016-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`异常原因`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Vanquish Convertible 2025-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Aston Martin Vanquish Coupe 2024-2026 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Audi A6/S6/RS6 Sedan 2001-2004 US`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `BMW 5 Series GT Sedan 2010-2016 US`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Bedford Blitz Van 1969-1987 EU`：`自动尺码`
  - `Bedford Blitz swb Van 1973-1987 EU`：`自动尺码`
  - `Bedford Blitz swb Van 1980-1983 EU`：`自动尺码`
  - `Bedford Blitz swb Van 1981-1987 EU`：`自动尺码`
  - `Bedford Blitz swb Van 1985-1987 EU`：`自动尺码`
  - `Bristol 411 Coupe 1973-1976 EU`：`宽IQR上界-MM`、`宽IQR下界-MM`、`宽Z分数`、`高IQR上界-MM`、`高IQR下界-MM`、`高Z分数`
  - `Buick Roadmaster Convertible 1942 US`：`宽Z分数`、`高Z分数`
  - `Buick Roadmaster Convertible 1946-1947 US`：`宽Z分数`、`高Z分数`
  - `Buick Roadmaster Convertible 1948 US`：`宽Z分数`、`高Z分数`
  - `Buick Roadmaster Convertible 1954 US`：`宽Z分数`、`高Z分数`
  - `Buick Roadmaster Convertible 1958 US`：`宽Z分数`、`高Z分数`
  - `Buick Roadmaster Coupe 1942 US`：`宽Z分数`、`高Z分数`
  - `Buick Roadmaster Coupe 1946-1947 US`：`宽Z分数`、`高Z分数`
  - `Buick Roadmaster Coupe 1948 US`：`宽Z分数`、`高Z分数`
  - `Buick Roadmaster Coupe 1954 US`：`宽Z分数`、`高Z分数`
