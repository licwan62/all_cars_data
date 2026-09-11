# 0910.3 逻辑尺码代表车型

生成日期：2026-09-10  
数据源：当前发布的 `public/全量数据.csv` 与 `public/尺码匹配规则.csv`。  
目标逻辑尺码：`3XL`、`3XXL`、`3XL-W`、`3XXL-W`、`3XXXL`、`3XXXXL`。

本批次仿照 `2026-09-07_01_all-size-representatives` 生成：

- `代表车型.csv`：字段为 `车型、dimension-id、型号、车长、车宽、车高、车形、销量、参考半周长、in_eagle`。
- `代表车型.tsv`：便于复制粘贴，仅保留 `车型、型号、车长、车宽、车高、车形`。
- `report.md`：记录筛选口径、尺码分布、代表性与空簇原因。

当前正式全量表已把旧字段“参考半周长”更名为“等效长”。为了保持 0907 交付结构，CSV 中的 `参考半周长` 列承载当前 `等效长` 数值。`in_eagle` 本轮未连接 Eagle 复核，统一保留为 `0`。

## 口径

全量表保存的是内部尺码，不能直接区分 `3XL` 与 `3XL-W`。本报告按 0910.3 启用规则的实际匹配顺序重新还原逻辑尺码：在同一分类池中按档位序号升序选择第一个同时满足车长与插片指数上限的规则，并检查 500 mm 余量容差。

代表车型分两层选择：

1. 每个逻辑尺码按累计销量列出主要车型。
2. 每种实际车形选择销量最高的一条作为车形代表，防止高销量 SD1 掩盖同尺码内的 SD0、SD2 或专用车形。

最终 CSV/TSV 沿用 0907 的正式选取算法：每个非空逻辑尺码输出 4 条；优先采用正销量记录；综合得分为车长 30%、等效长 30%、销量对数 20%、结束年份 20%；先覆盖不同 `MAKE + MODEL + 版本 + CAB + BED` 组合，再补足至 4 条。两个 W 空簇不制造虚假代表。

## 尺码簇概览

| 逻辑尺码 | 记录数 | 销量合计 | 长度范围 mm | 插片指数范围 | 主要车形 |
| --- | ---: | ---: | ---: | ---: | --- |
| 3XL | 534 | 98,623,258 | 4,737–5,050 | -165–150 | SD1 301；SD0 202；SD2 22；dodge-challenger 5；SU1 4 |
| 3XXL | 57 | 1,894,387 | 5,202–5,486 | -94–150 | SD1 51；SD0 4；SD2 2 |
| 3XL-W | 0 | 0 | — | — | 当前规则顺序下不可达 |
| 3XXL-W | 0 | 0 | — | — | 当前规则顺序下不可达 |
| 3XXXL | 199 | 22,879,004 | 5,202–5,697 | 157–276 | SD2 199，纯度 100% |
| 3XXXXL | 164 | 11,777,978 | 5,502–5,921 | -47–276 | SD2 159；SD0 3；SD1 2，SD2 纯度 97.0% |

## 各车形代表

| 逻辑尺码 | 车形 | 代表车型 | L×W×H mm | 插片指数 | 销量 | 内部尺码 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 3XL | SD1 | Toyota Camry Sedan 2012-2017 | 4,849×1,821×1,471 | -54 | 2,447,027 | 3XL |
| 3XL | SD0 | Pontiac Firebird Trans Am Coupe 1974-1981 | 4,999×1,859×1,260 | -106 | 1,001,288 | 3XL-0 |
| 3XL | SD2 | Oldsmobile Cutlass Ciera Sedan 1983-1988 | 4,785×1,765×1,374 | 132 | 626,669 | 3XL |
| 3XL | dodge-challenger | Dodge Challenger Coupe 2008-2014 | 5,022×1,923×1,450 | -5 | 265,795 | 3XL-0 |
| 3XL | SU1 | Mercedes-Benz GLE-Class Coupe 2021-2026 | 4,961×2,017×1,720 | -5 | 158,824 | 3XL-0 |
| 3XXL | SD1 | Chrysler Concorde Sedan 1998-2001 | 5,311×1,897×1,420 | -24 | 207,304 | 3XXL |
| 3XXL | SD0 | Lincoln Mark VIII Coupe 1994-1998 | 5,265×1,900×1,361 | -92 | 86,650 | 3XXL-0 |
| 3XXL | SD2 | Cadillac Seville Sedan 1983-1984 | 5,202×1,801×1,379 | 150 | 70,427 | 3XXL |
| 3XXXL | SD2 | Mercury Grand Marquis Sedan 1983-1991 | 5,436×1,968×1,410 | 234 | 987,818 | 3XXXL-0 |
| 3XXXXL | SD2 | Ford Thunderbird Coupe 1977-1979 | 5,517×1,994×1,341 | 247 | 936,038 | 3XXXXL-0 |
| 3XXXXL | SD0 | Buick Riviera Coupe 1973 | 5,674×2,032×1,372 | -46 | 34,080 | 3XXXXL-0 |
| 3XXXXL | SD1 | Lincoln Continental Coupe 1946-1948 | 5,578×1,976×1,359 | 6 | 950 | 3XXXXL-0 |

## 主要销量代表

### 3XL

| 车型 | 车形 | 销量 |
| --- | --- | ---: |
| Toyota Camry Sedan 2012-2017 | SD1 | 2,447,027 |
| Toyota Camry Sedan 2018-2024 | SD1 | 2,165,059 |
| Toyota Camry Sedan 2002-2006 | SD1 | 2,147,686 |
| Toyota Camry Sedan 1997-2001 | SD1 | 2,076,071 |
| Toyota Camry Sedan 2007-2011 | SD1 | 1,900,312 |
| Ford Fusion Sedan 2013-2020 | SD1 | 1,828,083 |

`3XL` 是标准大中型轿车主力簇，销量由 SD1 主导，但记录层面仍包含大量 SD0 跑车，因此不适合作为单一车形专用尺码。

### 3XXL

| 车型 | 车形 | 销量 |
| --- | --- | ---: |
| Chrysler Concorde Sedan 1998-2001 | SD1 | 207,304 |
| Cadillac DTS Sedan 2006-2011 | SD1 | 187,731 |
| Oldsmobile Aurora Sedan 1995-1999 | SD1 | 145,247 |
| Chrysler LHS Sedan 1994-1997 | SD1 | 134,713 |
| Cadillac DTS-L Sedan 2007-2011 | SD1 | 129,507 |
| Lincoln Mark VIII Coupe 1994-1998 | SD0 | 86,650 |

`3XXL` 主要代表现代长车身 SD1，SD2 仅有 2 条且刚好处在插片指数 150 上限附近。

### 3XXXL

| 车型 | 车形 | 销量 |
| --- | --- | ---: |
| Mercury Grand Marquis Sedan 1983-1991 | SD2 | 987,818 |
| Mercury Grand Marquis Sedan 1998-2005 | SD2 | 771,794 |
| Ford Crown Victoria Sedan 1997-2004 | SD2 | 750,453 |
| Lincoln Town Car Sedan 1982-1988 | SD2 | 697,317 |
| Lincoln Town Car Sedan 1992-1997 | SD2 | 638,620 |
| Mercury Grand Marquis Sedan 1992-1997 | SD2 | 561,177 |

`3XXXL` 已形成清晰的老式方正三厢车专用簇，记录与销量均为 100% SD2。

### 3XXXXL

| 车型 | 车形 | 销量 |
| --- | --- | ---: |
| Ford Thunderbird Coupe 1977-1979 | SD2 | 936,038 |
| Chevrolet Caprice Convertible 1972-1975 | SD2 | 417,500 |
| Chevrolet Impala Convertible 1976 | SD2 | 377,900 |
| Chevrolet Caprice Coupe 1973-1975 | SD2 | 320,000 |
| Cadillac DeVille Coupe 1968-1970 | SD2 | 263,360 |
| Chevrolet Impala Coupe 1974 | SD2 | 243,850 |

`3XXXXL` 主要代表超长老式方正 Coupe/Convertible。非 SD2 只有 5 条、103,493 销量，对整体代表性影响很小。

## W 逻辑尺码不可达

`3XL-W` 与 `3XXL-W` 虽已启用，但本次实际命中均为 0。原因是：

- 跑车 `3XXXXL` 的档位序号为 17，早于 `3XL-W=110`、`3XXL-W=111`。
- 三厢车 `3XXXL` 的档位序号为 26，早于 `3XL-W=130`、`3XXL-W=131`。
- 对插片指数大于 150 的较短车辆，算法先选择这些更大尺码规则；若长度余量超过 500 mm，会直接判为超余量，不会继续寻找后面的 W 规则。

因此当前无法为两个 W 逻辑尺码生成真实代表车型。如果预期 W 规则承接“长度仍属 3XL/3XXL、但插片指数超过 150”的车型，需要把 W 规则的档位序号放在对应普通尺码之后、老爷车专用大尺码之前，再重新计算。

## 结论

- `3XL`：混合车形主力尺码，核心代表为 Camry 等 SD1，同时覆盖大量 SD0。
- `3XXL`：以超长 SD1 为主，不是老爷车专用尺码。
- `3XL-W`、`3XXL-W`：当前规则顺序下无实际样本。
- `3XXXL`：纯 SD2 老爷车三厢簇，代表为 Grand Marquis、Crown Victoria、Town Car。
- `3XXXXL`：高纯度 SD2 超长 Coupe/Convertible 簇，代表为 Thunderbird、Caprice、Impala、DeVille。
