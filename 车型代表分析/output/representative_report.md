# 车形三维代表性与销量报告

基于 `source/车型尺寸库.csv`、`source/车型形状分类.csv`、`source/atom_sales.csv` 生成。

## 方法口径

- **三维数据**: 每条记录的 L-IN / W-IN / H-IN(英寸); 缺失三维的记录不参与分档与选代表, 单独计数。
- **销量**: `atom_sales.csv` 中同一 DIMENSION-ID 各年预估销量之和; 无销量记录按 0 计。
- **整体代表点**: 车形内 L/W/H 的销量加权中位数(无销量记录权重为 0)。
- **分档保覆盖**: 每个车形内 L、W 按三分位分 3 档, H 按中位数分 2 档, 共 3×3×2=18 档; 有记录即视为覆盖。
- **档内代表**: 档内按综合得分排序取第一, 得分 = 0.6×销量归一 + 0.4×接近度归一; 接近度 = 1 - 记录到档内销量加权中位点的三维归一距离。
- **三维距离**: 按车形 min-max 归一化的 (L, W, H) 欧氏距离, 避免车长量纲主导。

## 全库概览

- 尺寸库记录合计 **4354** 条, 其中具有完整三维数据 **4350** 条(占比 99.9%)。
- 全部车形预估销量合计 **671,927,236** 台(历年累计)。

| 车形 | 分类 | 记录数 | 有销量记录 | 总销量 | L 中位 | W 中位 | H 中位 | 三维档覆盖 | 代表集销量占比 | 80%销量集中记录数 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | Pickup 普通皮卡 | 230 | 207 | 72,300,869 | 226.1 | 79.5 | 75.5 | 17/18 | 20.6% | 84 / 230 |
| 1 | Pickup 轮拱外扩皮卡 | 173 | 129 | 39,682,630 | 227.6 | 79.9 | 79.8 | 9/18 | 15.6% | 44 / 173 |
| 10 | Pickup 性能宽体皮卡 | 20 | 15 | 3,415,115 | 232.1 | 86.3 | 78.5 | 6/18 | 38.8% | 7 / 20 |
| 11 | Pickup 双后轮皮卡 | 39 | 23 | 10,180,747 | 226.6 | 94.3 | 76.0 | 11/18 | 71.8% | 6 / 39 |
| 20 | Hatchback/Wagon 圆头两厢/旅行 | 342 | 320 | 41,783,284 | 175.2 | 69.3 | 57.8 | 18/18 | 20.0% | 117 / 342 |
| 21 | Hatchback/Wagon 方头两厢/旅行 | 199 | 189 | 32,240,539 | 196.7 | 72.2 | 55.2 | 14/18 | 33.1% | 63 / 199 |
| 25 | Minivan 标准 MPV | 63 | 62 | 21,208,164 | 200.0 | 77.4 | 68.9 | 15/18 | 49.8% | 24 / 63 |
| 26 | Van 全尺寸货车 | 69 | 51 | 1,552,150 | 201.0 | 79.5 | 80.0 | 6/18 | 19.4% | 35 / 69 |
| 30 | Sedan 标准/Fastback 轿车 | 759 | 734 | 149,778,034 | 187.8 | 70.6 | 56.7 | 17/18 | 13.9% | 215 / 759 |
| 31 | Sedan/Coupe Low Sport | 636 | 598 | 41,933,838 | 187.4 | 71.8 | 52.4 | 17/18 | 16.1% | 161 / 636 |
| 32 | Sedan/Coupe Boxy Classic 老式方正轿车 | 886 | 837 | 96,356,483 | 204.0 | 75.0 | 54.4 | 14/18 | 9.8% | 335 / 886 |
| 40 | SUV 常规 SUV | 347 | 293 | 47,942,897 | 190.2 | 75.8 | 72.5 | 16/18 | 19.7% | 110 / 347 |
| 41 | SUV Fastback 溜背 SUV | 431 | 412 | 101,584,430 | 183.5 | 73.4 | 67.0 | 17/18 | 17.8% | 143 / 431 |
| 42 | SUV 方正 SUV | 96 | 83 | 5,058,763 | 188.8 | 75.6 | 64.0 | 13/18 | 45.7% | 24 / 96 |
| 50 | SUV 硬派方盒 SUV | 60 | 48 | 6,909,293 | 167.5 | 70.5 | 71.2 | 13/18 | 39.7% | 20 / 60 |

注: 中位数为销量加权中位数(英寸); 代表集 = 每个被覆盖档位的档内代表; 80%销量集中记录数 = 按销量降序累计达到车形 80% 销量所需记录数。

## 车形 0 — Pickup 普通皮卡

- 记录 230 条(含无三维 0 条), 有销量 207 条, 总销量 **72,300,869**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **226.1 / 79.5 / 75.5**。
- 销量集中度: 前 5 名占 9.7%; 累计 84 条记录(占记录数 36.5%)可达 80% 销量。
- 主要分类分布: 皮卡×230。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Ford|MODEL=F-150|VERSION=|STRUCTURE=Pickup|YEAR=1999-2003|CAB=Regular|BED=8 | 1999-2003 Ford F-150 Regular Cab long bed | 226.1 | 79.5 | 75.5 | 1,295,092 | 0.000 |
| MAKE=Ford|MODEL=F-150|VERSION=|STRUCTURE=Pickup|YEAR=1999-2003|CAB=SuperCab|BED=6.5 | 1999-2003 Ford F-150 SuperCab 6.5 ft | 225.9 | 79.5 | 75.5 | 1,295,091 | 0.003 |
| MAKE=Ram|MODEL=1500|VERSION=|STRUCTURE=Pickup|YEAR=2002-2008|CAB=Quad|BED=6.4 | Ram 1500 Quad Cab 6.4 ft | 227.7 | 79.9 | 75.0 | 0 | 0.036 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 41 | 2,606,933 | 202.9/74.7/70.1 | 1988-1998 Chevrolet C/K Regular Cab 6.5ft (`MAKE=Chevrolet|MODEL=C/K|VERSION=|STRUCTURE=Pickup|YEAR=1988-1998|CAB=Regular|BED=6.5`) | 194.5/77.1/70.8 | 677,500 | 0.887 |
| 短 | 中 | 低 | 11 | 6,385,353 | 206.3/79.5/72.5 | 1973-1986 Chevrolet C/K Regular Cab 8ft (`MAKE=Chevrolet|MODEL=C/K|VERSION=|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Regular|BED=8`) | 211.3/79.5/73.5 | 1,438,000 | 0.884 |
| 短 | 中 | 高 | 12 | 7,484,604 | 204.1/79.4/75.0 | Dodge Ram 1500 Regular Cab short bed (`MAKE=Ram|MODEL=1500|VERSION=|STRUCTURE=Pickup|YEAR=1994-2001|CAB=Regular|BED=6.4`) | 204.1/79.4/74.7 | 1,383,213 | 0.984 |
| 短 | 长 | 低 | 6 | 1,752,981 | 205.6/80.0/74.0 | 2014-2018 Chevrolet Silverado 1500 Regular Cab standard bed (`MAKE=Chevrolet|MODEL=Silverado 1500|VERSION=|STRUCTURE=Pickup|YEAR=2014-2018|CAB=Regular|BED=6.6`) | 205.6/80.0/74.0 | 719,155 | 1.000 |
| 短 | 长 | 高 | 7 | 3,626,313 | 209.3/79.9/75.8 | Ram 1500 Regular Cab short bed (`MAKE=Ram|MODEL=1500|VERSION=|STRUCTURE=Pickup|YEAR=2002-2008|CAB=Regular|BED=6.4`) | 207.7/79.9/75.0 | 1,241,093 | 0.801 |
| 中 | 短 | 低 | 24 | 3,395,940 | 219.4/77.1/71.0 | 1989-1998 Chevrolet C/K Extended Cab 6.5ft (`MAKE=Chevrolet|MODEL=C/K|VERSION=|STRUCTURE=Pickup|YEAR=1989-1998|CAB=Extended|BED=6.5`) | 218.5/77.1/70.8 | 617,500 | 0.938 |
| 中 | 短 | 高 | 2 | 176,496 | 225.9/78.5/75.0 | 2005 Silverado 1500 Crew Cab 5.8-ft short bed (`MAKE=Chevrolet|MODEL=Silverado 1500|VERSION=|STRUCTURE=Pickup|YEAR=2005|CAB=Crew|BED=5.8`) | 225.9/78.5/75.0 | 176,496 | 1.000 |
| 中 | 中 | 低 | 10 | 4,385,120 | 216.3/79.0/71.0 | 1992-1996 Ford F-150 Regular Cab 8.0 ft bed (`MAKE=Ford|MODEL=F-150|VERSION=|STRUCTURE=Pickup|YEAR=1992-1996|CAB=Regular|BED=8`) | 213.3/79.0/71.0 | 880,417 | 0.878 |
| 中 | 中 | 高 | 17 | 7,898,319 | 225.9/79.4/75.6 | 1999-2003 Ford F-150 SuperCab 6.5 ft (`MAKE=Ford|MODEL=F-150|VERSION=|STRUCTURE=Pickup|YEAR=1999-2003|CAB=SuperCab|BED=6.5`) | 225.9/79.5/75.5 | 1,295,091 | 0.984 |
| 中 | 长 | 低 | 10 | 3,036,480 | 224.5/80.0/73.9 | 2014-2018 Chevrolet Silverado 1500 Regular Cab long bed (`MAKE=Chevrolet|MODEL=Silverado 1500|VERSION=|STRUCTURE=Pickup|YEAR=2014-2018|CAB=Regular|BED=8`) | 224.4/80.0/74.0 | 719,154 | 0.989 |
| 中 | 长 | 高 | 15 | 5,334,805 | 228.9/80.0/76.9 | 2015-2020 Ford F-150 Regular Cab 8.0 ft, Ford Tech Specs/Edmunds/KBB/JD Power (`MAKE=Ford|MODEL=F-150|VERSION=|STRUCTURE=Pickup|YEAR=2015-2020|CAB=Regular|BED=8`) | 227.9/79.9/77.2 | 760,539 | 0.794 |
| 长 | 短 | 低 | 7 | 1,558,759 | 246.7/78.5/73.9 | 1999-2006 Sierra Extended Cab long bed (`MAKE=GMC|MODEL=Sierra 1500|VERSION=|STRUCTURE=Pickup|YEAR=1999-2006|CAB=Extended|BED=8`) | 246.7/78.5/73.7 | 374,245 | 0.938 |
| 长 | 短 | 高 | 5 | 1,060,488 | 237.4/76.8/76.0 | 1988-1998 Chevrolet C/K Extended Cab 8ft (`MAKE=Chevrolet|MODEL=C/K|VERSION=|STRUCTURE=Pickup|YEAR=1988-1998|CAB=Extended|BED=8`) | 237.4/76.8/76.0 | 677,500 | 1.000 |
| 长 | 中 | 低 | 6 | 3,693,182 | 244.1/79.5/72.7 | 1973-1986 Chevrolet C/K Crew Cab 8ft (`MAKE=Chevrolet|MODEL=C/K|VERSION=|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Crew|BED=8`) | 244.3/79.5/72.0 | 1,438,000 | 0.933 |
| 长 | 中 | 高 | 24 | 7,535,095 | 237.4/79.4/77.7 | 2009-2018 Ram 1500 Crew Cab 6.4 ft (`MAKE=Ram|MODEL=1500|VERSION=|STRUCTURE=Pickup|YEAR=2009-2018|CAB=Crew|BED=6.4`) | 237.9/79.4/77.7 | 825,520 | 0.907 |
| 长 | 长 | 低 | 5 | 959,376 | 248.8/79.9/73.6 | 2007-2013 Chevrolet Silverado 1500 Extended Cab long bed (`MAKE=Chevrolet|MODEL=Silverado 1500|VERSION=|STRUCTURE=Pickup|YEAR=2007-2013|CAB=Extended|BED=8`) | 248.8/79.9/73.6 | 623,231 | 1.000 |
| 长 | 长 | 高 | 28 | 11,410,625 | 232.9/80.2/77.3 | 2019-2026 Ram 1500 Crew Cab 5.6 ft (`MAKE=Ram|MODEL=1500|VERSION=|STRUCTURE=Pickup|YEAR=2019-2026|CAB=Crew|BED=5.6`) | 232.9/82.1/77.6 | 1,059,624 | 0.825 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Chevrolet|MODEL=C/K|VERSION=|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Regular|BED=8 | 1973-1986 Chevrolet C/K Regular Cab 8ft | 211.3 | 79.5 | 73.5 | 1,438,000 |
| MAKE=Chevrolet|MODEL=C/K|VERSION=|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Regular|BED=6.5 | 1973-1986 Chevrolet C/K Regular Cab 6.5ft | 191.3 | 79.5 | 72.3 | 1,438,000 |
| MAKE=Chevrolet|MODEL=C/K|VERSION=|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Crew|BED=8 | 1973-1986 Chevrolet C/K Crew Cab 8ft | 244.3 | 79.5 | 72.0 | 1,438,000 |
| MAKE=Ram|MODEL=1500|VERSION=|STRUCTURE=Pickup|YEAR=1994-2001|CAB=Regular|BED=6.4 | Dodge Ram 1500 Regular Cab short bed | 204.1 | 79.4 | 74.7 | 1,383,213 |
| MAKE=Ford|MODEL=F-150|VERSION=|STRUCTURE=Pickup|YEAR=1999-2003|CAB=Regular|BED=6.5 | 1999-2003 Ford F-150 Regular Cab short bed | 208.0 | 79.3 | 75.5 | 1,295,094 |

## 车形 1 — Pickup 轮拱外扩皮卡

- 记录 173 条(含无三维 3 条), 有销量 129 条, 总销量 **39,682,630**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **227.6 / 79.9 / 79.8**。
- 销量集中度: 前 5 名占 17.9%; 累计 44 条记录(占记录数 25.4%)可达 80% 销量。
- 另有 3 条无三维数据(如待补尺寸), 未参与选代表。
- 主要分类分布: 皮卡×176。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=2011-2016|CAB=Regular|BED=8 | 2011-2016 F-250/F-350 Regular Cab 8 ft SRW | 227.6 | 79.9 | 80.0 | 869,727 | 0.010 |
| MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=1999-2007|CAB=Regular|BED=8 | 1999-2007 F-250/F-350 Regular Cab 8 ft SRW | 226.6 | 79.9 | 79.7 | 1,528,840 | 0.012 |
| MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=2008-2010|CAB=Regular|BED=8 | 2008-2010 F-250/F-350 Regular Cab 8 ft SRW | 227.0 | 79.9 | 79.2 | 291,498 | 0.030 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 42 | 5,242,003 | 198.2/69.4/67.6 | 1998-2011 Ranger SuperCab 6 ft (`MAKE=Ford|MODEL=Ranger|VERSION=|STRUCTURE=Pickup|YEAR=1998-2011|CAB=SuperCab|BED=6`) | 202.9/69.4/67.7 | 801,457 | 0.954 |
| 短 | 中 | 低 | 13 | 2,085,697 | 196.0/70.3/67.7 | 1995-2004 Tacoma XtraCab 6 ft (`MAKE=Toyota|MODEL=Tacoma|VERSION=|STRUCTURE=Pickup|YEAR=1995-2004|CAB=XtraCab|BED=6`) | 202.9/70.3/67.7 | 671,911 | 0.940 |
| 短 | 中 | 高 | 4 | 1,485,000 | 192.0/75.7/75.3 | 1953/1956 (`MAKE=Ford|MODEL=F-100|VERSION=|STRUCTURE=Pickup|YEAR=1953-1956|CAB=Regular|BED=6.5`) | 189.1/75.7/75.3 | 650,000 | 0.938 |
| 中 | 短 | 低 | 21 | 995,415 | 207.1/68.6/67.6 | 2004-2012 Colorado Extended Cab 6 ft (`MAKE=Chevrolet|MODEL=Colorado|VERSION=|STRUCTURE=Pickup|YEAR=2004-2012|CAB=Extended|BED=6`) | 207.1/68.6/67.6 | 241,176 | 1.000 |
| 中 | 中 | 低 | 15 | 3,518,239 | 215.1/74.6/70.3 | 2005-2015 Tacoma Double Cab 6 ft (`MAKE=Toyota|MODEL=Tacoma|VERSION=|STRUCTURE=Pickup|YEAR=2005-2015|CAB=Double|BED=6`) | 221.3/74.6/70.3 | 756,761 | 0.907 |
| 中 | 中 | 高 | 18 | 3,454,327 | 212.3/75.2/71.6 | Ford Explorer Sport Trac (`MAKE=Ford|MODEL=Explorer|VERSION=Sport Trac|STRUCTURE=Pickup|YEAR=2001-2005|CAB=Crew|BED=4.2`) | 205.8/73.6/71.2 | 901,002 | 0.908 |
| 中 | 长 | 高 | 4 | 217,824 | 214.2/79.9/75.8 | 2026 Tacoma Trailhunter / TRD Pro (`MAKE=Toyota|MODEL=Tacoma|VERSION=TRD Pro/Trailhunter|STRUCTURE=Pickup|YEAR=2024-2026|CAB=Double|BED=5`) | 214.2/79.9/75.8 | 152,824 | 1.000 |
| 长 | 中 | 高 | 3 | 783,520 | 225.5/75.2/71.6 | 2016-2023 Tacoma Double Cab 6 ft (`MAKE=Toyota|MODEL=Tacoma|VERSION=|STRUCTURE=Pickup|YEAR=2016-2023|CAB=Double|BED=6`) | 225.5/75.2/71.6 | 477,871 | 1.000 |
| 长 | 长 | 高 | 53 | 21,900,605 | 246.2/79.9/80.8 | 1999-2007 Ford F-250/F-350 Super Duty Crew Cab 6.75 ft SRW (`MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=1999-2007|CAB=Crew|BED=6.8`) | 245.8/79.9/81.3 | 1,528,846 | 0.961 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=1999-2007|CAB=Crew|BED=6.8 | 1999-2007 Ford F-250/F-350 Super Duty Crew Cab 6.75 ft SRW | 245.8 | 79.9 | 81.3 | 1,528,846 |
| MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=1999-2007|CAB=Crew|BED=8 | 1999-2007 F-250 Crew Cab long bed SRW | 262.0 | 79.9 | 80.8 | 1,528,841 |
| MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=1999-2007|CAB=Regular|BED=8 | 1999-2007 F-250/F-350 Regular Cab 8 ft SRW | 226.6 | 79.9 | 79.7 | 1,528,840 |
| MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=1999-2007|CAB=SuperCab|BED=6.8 | 1999-2007 F-250/F-350 SuperCab 6.75 ft SRW | 231.4 | 79.9 | 80.2 | 1,528,839 |
| MAKE=Ford|MODEL=F-250/F-350 Super Duty|VERSION=|STRUCTURE=Pickup|YEAR=2017-2022|CAB=Crew|BED=6.8 | 2017-2022 Ford F-250 Super Duty Crew Cab 6.75 ft SRW | 250.0 | 80.0 | 81.5 | 973,993 |

## 车形 10 — Pickup 性能宽体皮卡

- 记录 20 条(含无三维 0 条), 有销量 15 条, 总销量 **3,415,115**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **232.1 / 86.3 / 78.5**。
- 销量集中度: 前 5 名占 68.2%; 累计 7 条记录(占记录数 35.0%)可达 80% 销量。
- 主要分类分布: 皮卡×20。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2011-2014|CAB=SuperCrew|BED=5.5 | 2011/2012/2013/2014 Ford F-150 SVT Raptor SuperCrew 5.5 ft | 232.1 | 86.3 | 78.5 | 370,528 | 0.000 |
| MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2017-2020|CAB=SuperCrew|BED=5.5 | 2017/2018/2019/2020 Ford F-150 Raptor SuperCrew 5.5 ft | 231.9 | 86.3 | 78.5 | 466,317 | 0.004 |
| MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2021-2026|CAB=SuperCrew|BED=5.5 | 2021/2022/2023/2024/2025/2026 Ford F-150 Raptor SuperCrew 5.5 ft | 232.6 | 86.6 | 79.8 | 486,904 | 0.071 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 6 | 34,125 | 204.7/71.9/63.4 | 2000 Chevrolet S-10 LS Wide Stance Extended Cab 6.0-ft Bed (`MAKE=Chevrolet|MODEL=S10|VERSION=ZR2|STRUCTURE=Pickup|YEAR=2000|CAB=Extended|BED=6`) | 204.7/71.9/63.4 | 18,125 | 1.000 |
| 短 | 短 | 高 | 1 | 31,428 | 188.7/71.9/67.5 | 1994 Chevrolet S-10 ZR2 Regular Cab 6.0-ft Bed (`MAKE=Chevrolet|MODEL=S10|VERSION=ZR2|STRUCTURE=Pickup|YEAR=1994|CAB=Regular|BED=6`) | 188.7/71.9/67.5 | 31,428 | 1.000 |
| 中 | 短 | 低 | 4 | 62,033 | 205.0/67.9/63.4 | 1998 Chevrolet S-10 ZR2 Extended Cab 6.0-ft Bed (`MAKE=Chevrolet|MODEL=S10|VERSION=ZR2|STRUCTURE=Pickup|YEAR=1998|CAB=Extended|BED=6`) | 204.8/67.9/63.4 | 19,444 | 0.832 |
| 中 | 中 | 高 | 2 | 533,786 | 220.0/86.3/78.5 | 2017/2018/2019/2020 Ford F-150 Raptor SuperCab 5.5 ft (`MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2017-2020|CAB=SuperCab|BED=5.5`) | 220.0/86.3/78.5 | 466,317 | 1.000 |
| 长 | 中 | 高 | 3 | 1,282,851 | 231.9/86.3/78.5 | 2017/2018/2019/2020 Ford F-150 Raptor SuperCrew 5.5 ft (`MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2017-2020|CAB=SuperCrew|BED=5.5`) | 231.9/86.3/78.5 | 466,317 | 1.000 |
| 长 | 长 | 高 | 4 | 1,470,892 | 232.6/87.0/80.6 | 2023/2024/2025/2026 Ford F-150 Raptor R SuperCrew 5.5 ft (`MAKE=Ford|MODEL=F-150|VERSION=Raptor R|STRUCTURE=Pickup|YEAR=2023-2026|CAB=SuperCrew|BED=5.5`) | 232.6/87.0/80.6 | 323,492 | 0.799 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2021-2026|CAB=SuperCrew|BED=5.5 | 2021/2022/2023/2024/2025/2026 Ford F-150 Raptor SuperCrew 5.5 ft | 232.6 | 86.6 | 79.8 | 486,904 |
| MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2017-2020|CAB=SuperCab|BED=5.5 | 2017/2018/2019/2020 Ford F-150 Raptor SuperCab 5.5 ft | 220.0 | 86.3 | 78.5 | 466,317 |
| MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2017-2020|CAB=SuperCrew|BED=5.5 | 2017/2018/2019/2020 Ford F-150 Raptor SuperCrew 5.5 ft | 231.9 | 86.3 | 78.5 | 466,317 |
| MAKE=Ram|MODEL=1500|VERSION=TRX|STRUCTURE=Pickup|YEAR=2021-2024|CAB=Crew|BED=5.6 | 2021-2024 Ram 1500 TRX Crew Cab 5.6 ft | 232.9 | 88.0 | 80.9 | 463,943 |
| MAKE=Ford|MODEL=F-150|VERSION=Raptor|STRUCTURE=Pickup|YEAR=2010-2014|CAB=SuperCab|BED=5.5 | 2010/2011/2012/2013/2014 Ford F-150 SVT Raptor SuperCab 5.5 ft | 220.9 | 86.3 | 78.5 | 446,006 |

## 车形 11 — Pickup 双后轮皮卡

- 记录 39 条(含无三维 0 条), 有销量 23 条, 总销量 **10,180,747**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **226.6 / 94.3 / 76.0**。
- 销量集中度: 前 5 名占 79.1%; 累计 6 条记录(占记录数 15.4%)可达 80% 销量。
- 主要分类分布: 皮卡×39。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Chevrolet|MODEL=C/K|VERSION=Classic DRW|STRUCTURE=Pickup|YEAR=1999-2000|CAB=Crew|BED=6.5 | 1999-2000 Chevrolet C/K Classic Crew Cab DRW 6.5ft | 231.9 | 94.3 | 74.5 | 26,889 | 0.182 |
| MAKE=Chevrolet|MODEL=C/K|VERSION=Classic DRW|STRUCTURE=Pickup|YEAR=1999-2000|CAB=Extended|BED=8 | 1999-2000 Chevrolet C/K Classic Extended Cab DRW 8ft | 237.4 | 94.3 | 76.0 | 26,889 | 0.195 |
| MAKE=Chevrolet|MODEL=C/K|VERSION=DRW|STRUCTURE=Pickup|YEAR=1988-1998|CAB=Extended|BED=8 | 1988-1998 Chevrolet C/K Extended Cab DRW 8ft | 237.4 | 94.3 | 76.0 | 677,500 | 0.195 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 8 | 3,200,167 | 212.5/94.3/73.5 | 1973-1986 Chevrolet C/K Regular Cab DRW 8ft (`MAKE=Chevrolet|MODEL=C/K|VERSION=DRW|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Regular|BED=8`) | 211.3/94.3/73.5 | 1,438,000 | 0.991 |
| 短 | 中 | 低 | 1 | 0 | 227.6/96.0/80.0 | 2011 F-350 DRW Regular Cab 8 ft | 2012 F-350 DRW Regular Cab 8 ft | 2013 F-350 DRW Regular Cab 8 ft | 2014 F-350 DRW Regular Cab 8 ft | 2015 F-350 DRW Regular Cab 8 ft | 2016 F-350 DRW Regular Cab 8 ft (`MAKE=Ford|MODEL=F-350 Super Duty|VERSION=DRW|STRUCTURE=Pickup|YEAR=2011-2016|CAB=Regular|BED=8`) | 227.6/96.0/80.0 | 0 | 0.400 |
| 短 | 中 | 高 | 4 | 3,822,098 | 226.6/95.5/81.7 | 1999-2007 F-350 DRW Regular Cab long bed (`MAKE=Ford|MODEL=F-350 Super Duty|VERSION=DRW|STRUCTURE=Pickup|YEAR=1999-2007|CAB=Regular|BED=8`) | 226.6/95.5/81.7 | 3,822,098 | 1.000 |
| 中 | 短 | 低 | 8 | 2,356,277 | 244.3/94.3/72.0 | 1973-1986 Chevrolet C/K Crew Cab DRW 8ft (`MAKE=Chevrolet|MODEL=C/K|VERSION=DRW|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Crew|BED=8`) | 244.3/94.3/72.0 | 1,438,000 | 1.000 |
| 中 | 中 | 低 | 1 | 36,000 | 258.4/96.0/77.8 | 2019 Chevrolet Silverado 3500HD Crew Cab long bed DRW (`MAKE=Chevrolet|MODEL=Silverado 2500HD/3500HD|VERSION=DRW|STRUCTURE=Pickup|YEAR=2019|CAB=Crew|BED=8`) | 258.4/96.0/77.8 | 36,000 | 1.000 |
| 中 | 中 | 高 | 3 | 450,732 | 261.8/96.0/81.7 | 2005 F-350 Crew Cab DRW 8 ft (`MAKE=Ford|MODEL=F-350 Super Duty|VERSION=DRW|STRUCTURE=Pickup|YEAR=2005|CAB=Crew|BED=8`) | 261.8/96.0/81.7 | 450,732 | 1.000 |
| 中 | 长 | 低 | 1 | 0 | 258.4/96.8/80.0 | 2015 Chevrolet Silverado 3500HD Crew Cab long bed DRW | 2016 Chevrolet Silverado 3500HD Crew Cab 8 ft configuration; 2015/2017 Chevrolet Silverado 3500HD Crew Cab long bed DRW cross-check | 2017 Chevrolet Silverado 3500HD Crew Cab long bed DRW | 2018 Chevrolet Silverado 3500HD Crew Cab 8 ft configuration; 2017/2019 Chevrolet Silverado 3500HD Crew Cab long bed DRW cross-check (`MAKE=Chevrolet|MODEL=Silverado 2500HD/3500HD|VERSION=DRW|STRUCTURE=Pickup|YEAR=2015-2018|CAB=Crew|BED=8`) | 258.4/96.8/80.0 | 0 | 0.400 |
| 长 | 中 | 低 | 1 | 0 | 263.0/96.0/79.8 | 2011 F-350 Crew Cab DRW 8 ft | 2012 F-350 Crew Cab DRW 8 ft | 2013 F-350 Crew Cab DRW 8 ft | 2014 F-350 Crew Cab DRW 8 ft | 2015 F-350 Crew Cab DRW 8 ft | 2016 F-350 Crew Cab DRW 8 ft (`MAKE=Ford|MODEL=F-350 Super Duty|VERSION=DRW|STRUCTURE=Pickup|YEAR=2011-2016|CAB=Crew|BED=8`) | 263.0/96.0/79.8 | 0 | 0.400 |
| 长 | 中 | 高 | 4 | 0 | 266.2/96.0/81.2 | 2017 F-350 Crew Cab DRW 8 ft | 2018 F-350 Crew Cab DRW 8 ft | 2019 F-350 Crew Cab DRW 8 ft (`MAKE=Ford|MODEL=F-350 Super Duty|VERSION=DRW|STRUCTURE=Pickup|YEAR=2017-2019|CAB=Crew|BED=8`) | 266.2/96.0/81.1 | 0 | 0.345 |
| 长 | 长 | 低 | 6 | 256,352 | 266.8/96.6/80.0 | 2025 Sierra 3500HD Crew Cab DRW long bed (`MAKE=GMC|MODEL=Sierra 2500HD/3500HD|VERSION=DRW|STRUCTURE=Pickup|YEAR=2001-2007|CAB=Crew|BED=8`) | 266.8/96.6/80.0 | 91,943 | 1.000 |
| 长 | 长 | 高 | 2 | 59,121 | 266.0/96.8/80.7 | 2024 Chevrolet Silverado 3500HD Crew Cab long bed DRW configuration dimensions (`MAKE=Chevrolet|MODEL=Silverado 2500HD/3500HD|VERSION=DRW|STRUCTURE=Pickup|YEAR=2024|CAB=Crew|BED=8`) | 266.0/96.8/80.7 | 36,749 | 1.000 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Ford|MODEL=F-350 Super Duty|VERSION=DRW|STRUCTURE=Pickup|YEAR=1999-2007|CAB=Regular|BED=8 | 1999-2007 F-350 DRW Regular Cab long bed | 226.6 | 95.5 | 81.7 | 3,822,098 |
| MAKE=Chevrolet|MODEL=C/K|VERSION=DRW|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Regular|BED=8 | 1973-1986 Chevrolet C/K Regular Cab DRW 8ft | 211.3 | 94.3 | 73.5 | 1,438,000 |
| MAKE=Chevrolet|MODEL=C/K|VERSION=DRW|STRUCTURE=Pickup|YEAR=1973-1986|CAB=Crew|BED=8 | 1973-1986 Chevrolet C/K Crew Cab DRW 8ft | 244.3 | 94.3 | 72.0 | 1,438,000 |
| MAKE=Chevrolet|MODEL=C/K|VERSION=DRW|STRUCTURE=Pickup|YEAR=1988-1998|CAB=Regular|BED=8 | 1988-1998 Chevrolet C/K Regular Cab DRW 8ft | 213.1 | 94.3 | 73.2 | 677,500 |
| MAKE=Chevrolet|MODEL=C/K|VERSION=DRW|STRUCTURE=Pickup|YEAR=1988-1998|CAB=Extended|BED=8 | 1988-1998 Chevrolet C/K Extended Cab DRW 8ft | 237.4 | 94.3 | 76.0 | 677,500 |

## 车形 20 — Hatchback/Wagon 圆头两厢/旅行

- 记录 342 条(含无三维 0 条), 有销量 320 条, 总销量 **41,783,284**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **175.2 / 69.3 / 57.8**。
- 销量集中度: 前 5 名占 10.4%; 累计 117 条记录(占记录数 34.2%)可达 80% 销量。
- 主要分类分布: 两厢车×337, 越野车×3, 跑车×2。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Mazda|MODEL=Speed3|VERSION=|STRUCTURE=Hatchback|YEAR=2007-2009 | 2009 Mazda Mazdaspeed3, Edmunds | 175.8 | 69.5 | 57.7 | 39,000 | 0.014 |
| MAKE=Mazda|MODEL=3|VERSION=|STRUCTURE=Hatchback|YEAR=2004-2006 | 2004-2006 Mazda 3 Hatchback | 176.6 | 69.1 | 57.7 | 43,524 | 0.020 |
| MAKE=Mazda|MODEL=3|VERSION=|STRUCTURE=Hatchback|YEAR=2010-2013 | 2010-2013 Mazda 3 Hatchback | 177.4 | 69.1 | 57.9 | 224,061 | 0.028 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 31 | 4,719,602 | 159.4/66.3/54.3 | 2000 Honda Civic Hatchback CX, Edmunds (`MAKE=Honda|MODEL=Civic|VERSION=|STRUCTURE=Hatchback|YEAR=1996-2000`) | 164.2/67.1/54.1 | 528,480 | 0.928 |
| 短 | 短 | 高 | 33 | 2,835,373 | 159.3/66.7/60.0 | 2009-2014 Honda Fit (`MAKE=Honda|MODEL=Fit|VERSION=|STRUCTURE=Hatchback|YEAR=2009-2014`) | 161.6/66.7/60.0 | 343,103 | 0.977 |
| 短 | 中 | 低 | 21 | 731,833 | 160.0/68.0/56.7 | 2006 Volkswagen Golf Hatchback Specs & Features / 2001-2006 Volkswagen Golf / GTI, Edmunds (`MAKE=Volkswagen|MODEL=Golf|VERSION=|STRUCTURE=Hatchback|YEAR=2000-2006`) | 164.9/68.3/56.7 | 197,952 | 0.832 |
| 短 | 中 | 高 | 17 | 1,149,961 | 161.1/68.3/59.0 | 2010 Volkswagen New Beetle Hatchback, Edmunds / 2003-2004 Volkswagen New Beetle Hatchback reference, Edmunds (`MAKE=Volkswagen|MODEL=Beetle|VERSION=|STRUCTURE=Hatchback|YEAR=1999-2010`) | 161.1/67.9/59.0 | 267,182 | 0.965 |
| 短 | 长 | 低 | 8 | 302,678 | 167.3/70.8/55.1 | Hyundai Veloster Base (`MAKE=Hyundai|MODEL=Veloster|VERSION=|STRUCTURE=Hatchback|YEAR=2012-2014`) | 166.1/70.5/55.1 | 96,411 | 0.942 |
| 短 | 长 | 高 | 4 | 161,996 | 165.4/70.3/58.3 | 2010-2012 Volkswagen Golf, Edmunds / 2010 Volkswagen Golf Specs & Features (`MAKE=Volkswagen|MODEL=Golf|VERSION=|STRUCTURE=Hatchback|YEAR=2010-2014`) | 165.4/70.3/58.3 | 148,041 | 1.000 |
| 中 | 短 | 低 | 28 | 4,578,751 | 172.7/66.7/53.9 | 1991/1995 Ford Escort Wagon (`MAKE=Ford|MODEL=Escort|VERSION=|STRUCTURE=Wagon|YEAR=1991-1996`) | 171.3/66.7/53.6 | 463,331 | 0.890 |
| 中 | 短 | 高 | 11 | 1,638,389 | 168.9/67.1/63.0 | 2010 Chrysler PT Cruiser (`MAKE=Chrysler|MODEL=PT Cruiser|VERSION=|STRUCTURE=Wagon|YEAR=2001-2010`) | 168.9/67.1/63.0 | 1,006,685 | 1.000 |
| 中 | 中 | 低 | 21 | 1,619,450 | 170.5/69.9/57.1 | 2019-2024 Toyota Corolla Hatchback SE/XSE (`MAKE=Toyota|MODEL=Corolla|VERSION=|STRUCTURE=Hatchback|YEAR=2019-2024`) | 169.9/69.9/57.1 | 661,712 | 0.993 |
| 中 | 中 | 高 | 25 | 4,821,496 | 175.0/69.1/58.7 | 2004-2009 Toyota Prius hatchback (`MAKE=Toyota|MODEL=Prius|VERSION=|STRUCTURE=Hatchback|YEAR=2004-2009`) | 175.0/67.9/58.7 | 748,400 | 0.890 |
| 中 | 长 | 低 | 19 | 2,178,599 | 175.3/70.7/57.2 | 2021 Honda Civic Hatchback, Edmunds (`MAKE=Honda|MODEL=Civic|VERSION=|STRUCTURE=Hatchback|YEAR=2017-2021`) | 177.9/70.8/56.3 | 410,405 | 0.806 |
| 中 | 长 | 高 | 10 | 1,148,590 | 172.9/71.8/58.2 | 2016-2017 Ford Focus Electric Edmunds/Ford media (`MAKE=Ford|MODEL=Focus|VERSION=|STRUCTURE=Hatchback|YEAR=2012-2018`) | 172.9/71.8/58.2 | 598,142 | 1.000 |
| 长 | 短 | 低 | 9 | 834,964 | 183.9/66.5/56.1 | 1993 Saab 900 Hatchback, Edmunds (`MAKE=Saab|MODEL=900|VERSION=|STRUCTURE=Hatchback|YEAR=1979-1993`) | 184.5/66.5/56.1 | 215,000 | 0.940 |
| 长 | 短 | 高 | 2 | 166,361 | 181.0/67.5/58.7 | 1995-1997 Volkswagen Passat Wagon, Edmunds (`MAKE=Volkswagen|MODEL=Passat|VERSION=|STRUCTURE=Wagon|YEAR=1995-1997`) | 181.0/67.5/58.7 | 154,866 | 1.000 |
| 长 | 中 | 低 | 14 | 1,311,107 | 185.8/69.6/56.7 | 2008 Mazda 6 Hatchback, Edmunds / 2004-2008 Mazda 6 Hatchback, Edmunds (`MAKE=Mazda|MODEL=6|VERSION=|STRUCTURE=Hatchback|YEAR=2003-2008`) | 186.8/70.1/56.7 | 286,847 | 0.968 |
| 长 | 中 | 高 | 17 | 2,834,079 | 186.6/69.3/59.6 | 2009-2014 Volkswagen Jetta SportWagen, Edmunds / 2011 Volkswagen Jetta SportWagen S Specs & Features (`MAKE=Volkswagen|MODEL=Jetta|VERSION=|STRUCTURE=Wagon|YEAR=2009-2014`) | 179.4/70.1/59.2 | 452,043 | 0.749 |
| 长 | 长 | 低 | 21 | 5,166,358 | 191.9/71.5/56.3 | 2000-2005 Ford Taurus Wagon, Edmunds (`MAKE=Ford|MODEL=Taurus|VERSION=|STRUCTURE=Wagon|YEAR=2000-2005`) | 197.7/73.0/57.8 | 906,923 | 0.808 |
| 长 | 长 | 高 | 51 | 5,583,697 | 190.0/72.6/65.7 | 2015-2019 Subaru Outback (`MAKE=Subaru|MODEL=Outback|VERSION=|STRUCTURE=Hatchback|YEAR=2015-2019`) | 189.6/72.4/66.1 | 884,110 | 0.978 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Chrysler|MODEL=PT Cruiser|VERSION=|STRUCTURE=Wagon|YEAR=2001-2010 | 2010 Chrysler PT Cruiser | 168.9 | 67.1 | 63.0 | 1,006,685 |
| MAKE=Ford|MODEL=Taurus|VERSION=|STRUCTURE=Wagon|YEAR=2000-2005 | 2000-2005 Ford Taurus Wagon, Edmunds | 197.7 | 73.0 | 57.8 | 906,923 |
| MAKE=Subaru|MODEL=Outback|VERSION=|STRUCTURE=Hatchback|YEAR=2015-2019 | 2015-2019 Subaru Outback | 189.6 | 72.4 | 66.1 | 884,110 |
| MAKE=Subaru|MODEL=Outback|VERSION=Wilderness|STRUCTURE=Wagon|YEAR=2020-2024 | 2024 Subaru Outback Wilderness / 2022-2024 Subaru Outback Wilderness, Edmunds | 191.3 | 74.6 | 66.9 | 785,195 |
| MAKE=Toyota|MODEL=Prius|VERSION=|STRUCTURE=Hatchback|YEAR=2004-2009 | 2004-2009 Toyota Prius hatchback | 175.0 | 67.9 | 58.7 | 748,400 |

## 车形 21 — Hatchback/Wagon 方头两厢/旅行

- 记录 199 条(含无三维 0 条), 有销量 189 条, 总销量 **32,240,539**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **196.7 / 72.2 / 55.2**。
- 销量集中度: 前 5 名占 28.6%; 累计 63 条记录(占记录数 31.7%)可达 80% 销量。
- 主要分类分布: 两厢车×199。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Pontiac|MODEL=LeMans|VERSION=|STRUCTURE=Wagon|YEAR=1979 | 1979 Pontiac Grand LeMans Safari Wagon, ConceptCarz | 197.8 | 72.4 | 54.8 | 17,500 | 0.032 |
| MAKE=Buick|MODEL=Century|VERSION=|STRUCTURE=Wagon|YEAR=1978-1981 | 1979/1981 Buick Century Station Wagon | 196.7 | 72.2 | 55.7 | 436,279 | 0.033 |
| MAKE=Pontiac|MODEL=LeMans|VERSION=|STRUCTURE=Wagon|YEAR=1980 | 1980 Pontiac Grand LeMans Safari Wagon, Automobile-Catalog | 197.8 | 72.6 | 54.8 | 16,666 | 0.038 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 48 | 8,887,731 | 169.4/65.6/53.7 | 1975-1976 Rabbit reference; 1977 Rabbit Diesel; 1981 Rabbit LS reference, Car and Driver / 1975-1976 Rabbit;1983 GTI | 1983 Volkswagen Rabbit GTI, Car and Driver (`MAKE=Volkswagen|MODEL=Rabbit|VERSION=|STRUCTURE=Hatchback|YEAR=1975-1984`) | 155.3/63.4/55.5 | 1,197,154 | 0.739 |
| 短 | 短 | 高 | 14 | 2,073,174 | 167.3/69.1/63.1 | 2013 Kia Soul ! / 2012-2013 Kia Soul, Edmunds (`MAKE=Kia|MODEL=Soul|VERSION=|STRUCTURE=Wagon|YEAR=2010-2013`) | 162.2/70.3/63.4 | 403,234 | 0.936 |
| 短 | 中 | 低 | 1 | 40,173 | 188.2/71.5/52.3 | 1961 Oldsmobile F-85 Wagon / 1961 brochure (`MAKE=Oldsmobile|MODEL=Cutlass|VERSION=F-85/Cutlass|STRUCTURE=Wagon|YEAR=1961`) | 188.2/71.5/52.3 | 40,173 | 1.000 |
| 短 | 中 | 高 | 4 | 1,218,243 | 163.0/70.9/63.0 | 2019 Kia Soul EV / 2015-2019 Kia Soul EV, Edmunds (`MAKE=Kia|MODEL=Soul|VERSION=EV|STRUCTURE=Hatchback|YEAR=2014-2019`) | 163.0/70.9/63.0 | 378,334 | 1.000 |
| 中 | 短 | 低 | 4 | 3,208,943 | 190.9/69.4/54.2 | 1988/1995 Buick Century Wagon (`MAKE=Buick|MODEL=Century|VERSION=|STRUCTURE=Wagon|YEAR=1982-1996`) | 190.9/69.4/54.2 | 2,246,096 | 1.000 |
| 中 | 短 | 高 | 1 | 2,700 | 191.4/68.9/57.6 | 1997-1998 Volvo V90 Wagon, Edmunds (`MAKE=Volvo|MODEL=V90|VERSION=|STRUCTURE=Wagon|YEAR=1997-1998`) | 191.4/68.9/57.6 | 2,700 | 1.000 |
| 中 | 中 | 低 | 35 | 3,805,500 | 199.2/74.6/54.5 | 1968-1972 Chevrolet Chevelle Station Wagon (`MAKE=Chevrolet|MODEL=Chevelle|VERSION=|STRUCTURE=Wagon|YEAR=1968-1972`) | 207.9/76.0/55.2 | 637,333 | 0.745 |
| 中 | 中 | 高 | 17 | 2,054,759 | 200.8/73.0/59.9 | 1979/1981 Buick Century Station Wagon (`MAKE=Buick|MODEL=Century|VERSION=|STRUCTURE=Wagon|YEAR=1978-1981`) | 196.7/72.2/55.7 | 436,279 | 0.704 |
| 中 | 长 | 低 | 2 | 269,050 | 210.8/79.6/55.5 | 1964 Chevrolet Bel Air Station Wagon (`MAKE=Chevrolet|MODEL=Bel Air|VERSION=|STRUCTURE=Wagon|YEAR=1964`) | 210.8/79.6/55.5 | 159,050 | 1.000 |
| 中 | 长 | 高 | 7 | 602,033 | 210.8/79.9/56.3 | 1963 Chevrolet Bel Air Station Wagon, Automobile-Catalog / Chevrolet Wagons brochure (`MAKE=Chevrolet|MODEL=Bel Air|VERSION=|STRUCTURE=Wagon|YEAR=1963`) | 210.4/79.4/56.0 | 177,050 | 0.873 |
| 长 | 中 | 低 | 3 | 136,583 | 213.7/76.8/54.8 | 1969-1972 Buick Skylark Sportwagon (`MAKE=Buick|MODEL=Skylark|VERSION=|STRUCTURE=Hatchback|YEAR=1969-1972`) | 213.7/76.8/54.8 | 83,250 | 1.000 |
| 长 | 中 | 高 | 7 | 734,177 | 215.2/76.8/56.0 | 1977 Chevrolet Chevelle Malibu Classic Estate Wagon / 1974-1975/1977 Chevrolet Chevelle Malibu Classic Estate Wagon / 1974-1975 Chevrolet Chevelle Malibu Classic Estate Wagon (`MAKE=Chevrolet|MODEL=Chevelle|VERSION=|STRUCTURE=Wagon|YEAR=1973-1977`) | 215.2/76.8/56.0 | 425,012 | 1.000 |
| 长 | 长 | 低 | 10 | 4,853,991 | 218.3/79.1/55.2 | 1977-1985 Chevrolet Impala Wagon (`MAKE=Chevrolet|MODEL=Impala|VERSION=|STRUCTURE=Wagon|YEAR=1965-1968`) | 218.3/79.1/55.2 | 2,941,400 | 1.000 |
| 长 | 长 | 高 | 46 | 4,353,482 | 220.3/79.6/56.7 | 1971-1976 Chevrolet Impala Wagon (`MAKE=Chevrolet|MODEL=Impala|VERSION=|STRUCTURE=Wagon|YEAR=1962-1963`) | 226.8/79.5/56.0 | 1,537,500 | 0.840 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Chevrolet|MODEL=Impala|VERSION=|STRUCTURE=Wagon|YEAR=1965-1968 | 1977-1985 Chevrolet Impala Wagon | 218.3 | 79.1 | 55.2 | 2,941,400 |
| MAKE=Buick|MODEL=Century|VERSION=|STRUCTURE=Wagon|YEAR=1982-1996 | 1988/1995 Buick Century Wagon | 190.9 | 69.4 | 54.2 | 2,246,096 |
| MAKE=Chevrolet|MODEL=Impala|VERSION=|STRUCTURE=Wagon|YEAR=1962-1963 | 1971-1976 Chevrolet Impala Wagon | 226.8 | 79.5 | 56.0 | 1,537,500 |
| MAKE=Buick|MODEL=Century|VERSION=|STRUCTURE=Wagon|YEAR=1973-1977 | 1974 Buick Century Station Wagon / 1973 Buick Century brochure | 218.2 | 79.0 | 55.5 | 1,305,814 |
| MAKE=Volkswagen|MODEL=Rabbit|VERSION=|STRUCTURE=Hatchback|YEAR=1975-1984 | 1975-1976 Rabbit reference; 1977 Rabbit Diesel; 1981 Rabbit LS reference, Car and Driver / 1975-1976 Rabbit;1983 GTI | 1983 Volkswagen Rabbit GTI, Car and Driver | 155.3 | 63.4 | 55.5 | 1,197,154 |

## 车形 25 — Minivan 标准 MPV

- 记录 63 条(含无三维 0 条), 有销量 62 条, 总销量 **21,208,164**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **200.0 / 77.4 / 68.9**。
- 销量集中度: 前 5 名占 29.9%; 累计 24 条记录(占记录数 38.1%)可达 80% 销量。
- 主要分类分布: 两厢车×58, 越野车×5。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Toyota|MODEL=Sienna|VERSION=|STRUCTURE=MPV|YEAR=2004-2006 | 2004-2006 Toyota Sienna LE/XLE Minivan | 200.0 | 77.4 | 68.9 | 483,768 | 0.000 |
| MAKE=Toyota|MODEL=Sienna|VERSION=|STRUCTURE=MPV|YEAR=2007-2010 | 2007-2010 Toyota Sienna XLE Minivan | 201.0 | 77.4 | 68.9 | 436,507 | 0.026 |
| MAKE=Chrysler|MODEL=Town & Country|VERSION=|STRUCTURE=MPV|YEAR=1996-2000 | 1998-1999 Chrysler Town & Country SWB; 2000 Chrysler Town & Country LWB | 199.7 | 76.8 | 68.7 | 246,517 | 0.055 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 13 | 2,119,446 | 178.1/72.0/65.7 | 1984-1990 Dodge Caravan SWB, AutoEvolution; 1987 Dodge Caravan SWB, Automobile-Catalog; 1989 Dodge Caravan brochure overall length; 1989 Dodge Caravan C/V PDF; 1990 Dodge Caravan Base, Edmunds (`MAKE=Dodge|MODEL=Caravan|VERSION=SWB|STRUCTURE=MPV|YEAR=1984-1990`) | 175.9/72.2/64.4 | 785,000 | 0.866 |
| 短 | 短 | 高 | 1 | 27,757 | 186.3/68.1/73.7 | 2015/2017-2018 Chevrolet City Express (`MAKE=Chevrolet|MODEL=City Express|VERSION=|STRUCTURE=Van|YEAR=2015-2018`) | 186.3/68.1/73.7 | 27,757 | 1.000 |
| 短 | 中 | 低 | 2 | 1,569,876 | 186.3/75.6/68.5 | 2007 Dodge Caravan SXT (`MAKE=Dodge|MODEL=Caravan|VERSION=SWB|STRUCTURE=MPV|YEAR=1996-2000`) | 186.3/75.6/68.5 | 1,472,658 | 1.000 |
| 短 | 中 | 高 | 3 | 662,500 | 176.8/77.0/73.7 | 1985 Chevrolet Astro Van; 1986 Chevrolet Astro Van; 1987 Chevrolet Astro Van; 1988 Chevrolet Astro Van (`MAKE=Chevrolet|MODEL=Astro|VERSION=|STRUCTURE=Wagon|YEAR=1985-1988`) | 176.8/77.0/73.7 | 350,000 | 1.000 |
| 短 | 长 | 低 | 2 | 1,660,639 | 189.3/78.6/68.9 | 2001-2007 Dodge Caravan SWB (`MAKE=Dodge|MODEL=Caravan|VERSION=SWB|STRUCTURE=MPV|YEAR=2001-2007`) | 189.3/78.6/68.9 | 1,576,709 | 1.000 |
| 中 | 短 | 低 | 6 | 1,805,771 | 192.8/72.0/67.3 | 1991/1992/1993/1994/1995 Dodge Grand Caravan LWB, Edmunds (`MAKE=Dodge|MODEL=Caravan|VERSION=Grand Caravan|STRUCTURE=MPV|YEAR=1991-1995`) | 192.8/72.0/67.3 | 650,000 | 1.000 |
| 中 | 短 | 高 | 1 | 84,519 | 191.0/72.0/70.5 | 2006 Chevrolet Uplander SWB; 2007 Chevrolet Uplander SWB; 2008 Chevrolet Uplander SWB (`MAKE=Chevrolet|MODEL=Uplander|VERSION=|STRUCTURE=Wagon|YEAR=2006-2008`) | 191.0/72.0/70.5 | 84,519 | 1.000 |
| 中 | 中 | 低 | 7 | 1,733,505 | 194.2/73.9/67.3 | 1998-2001 Toyota Sienna Minivan (`MAKE=Toyota|MODEL=Sienna|VERSION=|STRUCTURE=MPV|YEAR=1998-2001`) | 193.5/73.4/67.3 | 371,806 | 0.809 |
| 中 | 中 | 高 | 5 | 2,138,894 | 194.1/78.1/70.7 | 2011-2017 Toyota Sienna XLE/LE Minivan (`MAKE=Toyota|MODEL=Sienna|VERSION=|STRUCTURE=MPV|YEAR=2011-2017`) | 200.2/78.1/70.7 | 848,550 | 0.862 |
| 中 | 长 | 低 | 2 | 887,516 | 200.6/78.6/68.9 | 2002/2007 Chrysler Town & Country (`MAKE=Chrysler|MODEL=Town & Country|VERSION=|STRUCTURE=MPV|YEAR=2001-2007`) | 200.6/78.6/68.9 | 602,424 | 1.000 |
| 长 | 短 | 高 | 1 | 157,501 | 204.3/72.0/72.0 | 2005 Chevrolet Uplander LWB; 2006 Chevrolet Uplander LWB; 2007 Chevrolet Uplander LWB; 2008 Chevrolet Uplander LWB (`MAKE=Chevrolet|MODEL=Uplander|VERSION=LWB|STRUCTURE=Wagon|YEAR=2005-2008`) | 204.3/72.0/72.0 | 157,501 | 1.000 |
| 长 | 中 | 低 | 2 | 462,080 | 201.0/77.4/68.9 | 2007-2010 Toyota Sienna XLE Minivan (`MAKE=Toyota|MODEL=Sienna|VERSION=|STRUCTURE=MPV|YEAR=2007-2010`) | 201.0/77.4/68.9 | 436,507 | 1.000 |
| 长 | 中 | 高 | 6 | 1,982,993 | 202.0/77.1/69.7 | 2005-2010 Honda Odyssey (`MAKE=Honda|MODEL=Odyssey|VERSION=|STRUCTURE=MPV|YEAR=2005-2010`) | 202.1/77.1/70.0 | 866,965 | 0.905 |
| 长 | 长 | 低 | 2 | 941,112 | 202.9/79.2/68.4 | 2011-2017 Honda Odyssey (`MAKE=Honda|MODEL=Odyssey|VERSION=|STRUCTURE=MPV|YEAR=2011-2017`) | 202.9/79.2/68.4 | 833,122 | 1.000 |
| 长 | 长 | 高 | 10 | 4,974,055 | 203.7/78.7/69.9 | 2020 Dodge Grand Caravan (`MAKE=Dodge|MODEL=Caravan|VERSION=LWB|STRUCTURE=MPV|YEAR=2008-2020`) | 203.7/78.7/69.0 | 1,491,594 | 0.764 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Dodge|MODEL=Caravan|VERSION=SWB|STRUCTURE=MPV|YEAR=2001-2007 | 2001-2007 Dodge Caravan SWB | 189.3 | 78.6 | 68.9 | 1,576,709 |
| MAKE=Dodge|MODEL=Caravan|VERSION=LWB|STRUCTURE=MPV|YEAR=2008-2020 | 2020 Dodge Grand Caravan | 203.7 | 78.7 | 69.0 | 1,491,594 |
| MAKE=Dodge|MODEL=Caravan|VERSION=SWB|STRUCTURE=MPV|YEAR=1996-2000 | 2007 Dodge Caravan SXT | 186.3 | 75.6 | 68.5 | 1,472,658 |
| MAKE=Chrysler|MODEL=Town & Country|VERSION=|STRUCTURE=MPV|YEAR=2008-2016 | 2008 Chrysler Town & Country Limited | 202.8 | 78.7 | 71.4 | 934,707 |
| MAKE=Honda|MODEL=Odyssey|VERSION=|STRUCTURE=MPV|YEAR=2005-2010 | 2005-2010 Honda Odyssey | 202.1 | 77.1 | 70.0 | 866,965 |

## 车形 26 — Van 全尺寸货车

- 记录 69 条(含无三维 0 条), 有销量 51 条, 总销量 **1,552,150**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **201.0 / 79.5 / 80.0**。
- 销量集中度: 前 5 名占 25.7%; 累计 35 条记录(占记录数 50.7%)可达 80% 销量。
- 主要分类分布: 两厢车×69。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Chevrolet|MODEL=Chevy Van|VERSION=G20 Regular|STRUCTURE=Wagon|YEAR=1973-1975 | 1973 Chevrolet G20 Chevy Van 125-in Wheelbase | 1974 Chevrolet G20 Chevy Van 125-in Wheelbase | 1975 Chevrolet G20 Chevy Van 125-in Wheelbase | 201.0 | 79.5 | 80.0 | 0 | 0.000 |
| MAKE=Chevrolet|MODEL=Chevy Van|VERSION=G20 Regular|STRUCTURE=Wagon|YEAR=1977 | 1977 Chevrolet G20 Chevy Van 125-in Wheelbase | 201.0 | 79.5 | 80.0 | 25,000 | 0.000 |
| MAKE=Chevrolet|MODEL=Chevy Van|VERSION=G20 Regular|STRUCTURE=Wagon|YEAR=1980 | 1980 Chevrolet G20 Chevy Van 125-in Wheelbase | 202.2 | 79.5 | 80.0 | 19,000 | 0.016 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 19 | 354,070 | 177.0/79.5/79.4 | 1991-1992 Chevrolet G10 Chevy Van 110-in Wheelbase (`MAKE=Chevrolet|MODEL=Chevy Van|VERSION=G10 Short|STRUCTURE=Wagon|YEAR=1991-1992`) | 178.2/79.5/79.4 | 39,000 | 0.994 |
| 短 | 短 | 高 | 5 | 76,667 | 178.2/79.5/80.2 | 1979 Chevrolet G20 Chevy Van 110-in Wheelbase (`MAKE=Chevrolet|MODEL=Chevy Van|VERSION=G20 Short|STRUCTURE=Wagon|YEAR=1979`) | 178.2/79.5/80.2 | 20,000 | 1.000 |
| 中 | 短 | 低 | 22 | 458,001 | 201.0/79.5/79.4 | 1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase (`MAKE=Chevrolet|MODEL=Chevy Van|VERSION=Short|STRUCTURE=Wagon|YEAR=1993-1994`) | 180.0/79.1/80.0 | 58,334 | 0.841 |
| 中 | 短 | 高 | 14 | 282,333 | 202.2/79.5/81.0 | 1978 Chevrolet G30 Chevy Van 125-in Wheelbase (`MAKE=Chevrolet|MODEL=Chevy Van|VERSION=G30 Regular|STRUCTURE=Wagon|YEAR=1978`) | 202.2/79.5/81.0 | 27,000 | 0.815 |
| 长 | 短 | 低 | 2 | 20,000 | 204.1/79.5/79.7 | 1996 Chevrolet Chevy Van Classic G30 Regular 125-in Wheelbase (`MAKE=Chevrolet|MODEL=Chevy Van|VERSION=G-Classic Regular|STRUCTURE=Wagon|YEAR=1996`) | 204.1/79.5/79.7 | 20,000 | 1.000 |
| 长 | 短 | 高 | 7 | 361,079 | 238.8/79.3/83.7 | 1999 Chevrolet Express Extended (`MAKE=Chevrolet|MODEL=Express|VERSION=Extended|STRUCTURE=Van|YEAR=2016-2017`) | 238.8/79.4/83.7 | 137,171 | 0.979 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Chevrolet|MODEL=Express|VERSION=Extended|STRUCTURE=Van|YEAR=2016-2017 | 1999 Chevrolet Express Extended | 238.8 | 79.4 | 83.7 | 137,171 |
| MAKE=Chevrolet|MODEL=Express|VERSION=|STRUCTURE=Van|YEAR=2013 | 1996-1998 Chevrolet Express regular WB reference / 1999 Chevrolet Express Cargo | 221.5 | 79.2 | 83.7 | 79,087 |
| MAKE=Chevrolet|MODEL=Express|VERSION=|STRUCTURE=Van|YEAR=2021-2023 | 2024 Chevrolet Express Cargo 2500 regular / 2023-2026 Chevrolet Express Cargo 2500 regular | 224.1 | 79.3 | 84.8 | 62,411 |
| MAKE=Chevrolet|MODEL=Express|VERSION=Extended|STRUCTURE=Van|YEAR=2021-2023 | 2024 Chevrolet Express extended / max reference | 244.1 | 79.3 | 84.8 | 62,410 |
| MAKE=Chevrolet|MODEL=Chevy Van|VERSION=Short|STRUCTURE=Wagon|YEAR=1993-1994 | 1993-1994 Chevrolet Chevy Van G10/G20 Short Wheelbase | 180.0 | 79.1 | 80.0 | 58,334 |

## 车形 30 — Sedan 标准/Fastback 轿车

- 记录 759 条(含无三维 0 条), 有销量 734 条, 总销量 **149,778,034**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **187.8 / 70.6 / 56.7**。
- 销量集中度: 前 5 名占 7.3%; 累计 215 条记录(占记录数 28.3%)可达 80% 销量。
- 主要分类分布: 三厢车×620, 跑车×125, 两厢车×14。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Pontiac|MODEL=G6|VERSION=|STRUCTURE=Convertible|YEAR=2006-2009 | 2009 Pontiac G6 Convertible, Edmunds | 189.1 | 70.6 | 56.7 | 267,529 | 0.017 |
| MAKE=Lexus|MODEL=GS|VERSION=|STRUCTURE=Sedan|YEAR=1998-2005 | 1998 Lexus GS 300 / GS 400 | 2000-2005 Lexus GS 300/400, Edmunds | 189.2 | 70.9 | 56.7 | 0 | 0.025 |
| MAKE=Mercedes-Benz|MODEL=C-Class|VERSION=AMG|STRUCTURE=Sedan|YEAR=2008-2011 | 2008-2011 Mercedes-AMG C63 Sedan | 186.0 | 70.7 | 56.6 | 126,497 | 0.026 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 143 | 29,329,645 | 175.3/67.3/54.9 | 1998-2002 Toyota Corolla Sedan CE/LE (`MAKE=Toyota|MODEL=Corolla|VERSION=|STRUCTURE=Sedan|YEAR=1998-2002`) | 174.0/66.7/54.5 | 1,229,168 | 0.950 |
| 短 | 短 | 高 | 56 | 12,664,803 | 177.4/67.9/58.3 | 2003-2008 Toyota Corolla Sedan CE/LE/S (`MAKE=Toyota|MODEL=Corolla|VERSION=|STRUCTURE=Sedan|YEAR=2003-2008`) | 178.3/66.9/58.5 | 2,109,713 | 0.898 |
| 短 | 中 | 低 | 30 | 5,794,773 | 181.9/70.8/55.9 | 2008/2011-2013 Nissan Altima Coupe, Edmunds (`MAKE=Nissan|MODEL=Altima|VERSION=|STRUCTURE=Coupe|YEAR=2008-2013`) | 180.9/70.7/55.9 | 832,211 | 0.956 |
| 短 | 中 | 高 | 15 | 5,043,945 | 181.0/70.7/57.7 | 2016 Chevrolet Cruze LTZ (`MAKE=Chevrolet|MODEL=Cruze|VERSION=|STRUCTURE=Sedan|YEAR=2011-2016`) | 181.0/70.7/58.1 | 1,406,252 | 0.925 |
| 短 | 长 | 低 | 3 | 54,139 | 178.8/72.9/56.2 | 2022-2024 Audi A3/S3/RS3 Sedan (`MAKE=Audi|MODEL=A3/S3/RS3|VERSION=|STRUCTURE=Sedan|YEAR=2022-2024`) | 178.8/72.9/56.2 | 34,503 | 1.000 |
| 短 | 长 | 高 | 6 | 220,930 | 182.5/73.4/58.4 | 2018 Volvo S60, Car and Driver / JD Power; Edmunds宽度77.0疑似异常 / 2018 Volvo S60 (`MAKE=Volvo|MODEL=S60|VERSION=|STRUCTURE=Sedan|YEAR=2012-2018`) | 182.5/73.4/58.4 | 118,842 | 1.000 |
| 中 | 短 | 低 | 45 | 10,718,023 | 186.9/68.5/55.5 | 1996 Chevrolet Corsica (`MAKE=Chevrolet|MODEL=Corsica|VERSION=|STRUCTURE=Sedan|YEAR=1987-1996`) | 183.5/68.2/56.2 | 1,645,501 | 0.898 |
| 中 | 短 | 高 | 9 | 4,961,670 | 185.2/69.9/57.3 | 2014-2019 Toyota Corolla Sedan L/LE/S (`MAKE=Toyota|MODEL=Corolla|VERSION=|STRUCTURE=Sedan|YEAR=2014-2019`) | 183.1/69.9/57.3 | 1,866,393 | 0.929 |
| 中 | 中 | 低 | 72 | 17,476,244 | 187.8/70.6/55.4 | 1997 Toyota Camry sedan (`MAKE=Toyota|MODEL=Camry|VERSION=|STRUCTURE=Sedan|YEAR=1997-2001`) | 188.5/70.1/55.4 | 2,076,071 | 0.963 |
| 中 | 中 | 高 | 87 | 31,436,768 | 190.6/71.7/57.9 | 2012-2017 Toyota Camry sedan (`MAKE=Toyota|MODEL=Camry|VERSION=|STRUCTURE=Sedan|YEAR=2012-2017`) | 190.9/71.7/57.9 | 2,447,027 | 0.993 |
| 中 | 长 | 低 | 10 | 1,518,338 | 189.5/73.0/56.5 | 2017 Honda Accord Coupe LX-S, Edmunds (`MAKE=Honda|MODEL=Accord|VERSION=|STRUCTURE=Coupe|YEAR=2013-2017`) | 189.5/73.0/56.5 | 877,746 | 1.000 |
| 中 | 长 | 高 | 30 | 7,486,997 | 191.8/73.1/57.7 | Ford Fusion Energi Titanium / 2013-2018 Ford Fusion Edmunds (`MAKE=Ford|MODEL=Fusion|VERSION=|STRUCTURE=Sedan|YEAR=2013-2020`) | 191.8/72.9/58.2 | 1,828,083 | 0.940 |
| 长 | 短 | 低 | 3 | 205,126 | 199.5/69.7/54.3 | 1987/1990 Jaguar XJ6 Series III 美规 (`MAKE=Jaguar|MODEL=XJ|VERSION=|STRUCTURE=Sedan|YEAR=1979-1992`) | 199.5/69.7/54.3 | 148,568 | 1.000 |
| 长 | 中 | 低 | 33 | 4,086,519 | 198.3/72.5/55.2 | 1995-1999 Chevrolet Lumina Sedan (`MAKE=Chevrolet|MODEL=Lumina|VERSION=|STRUCTURE=Sedan|YEAR=1995-1999`) | 200.9/72.5/55.2 | 956,257 | 0.959 |
| 长 | 中 | 高 | 25 | 3,720,813 | 194.9/72.5/58.1 | 2012 Honda Accord Sedan, Edmunds (`MAKE=Honda|MODEL=Accord|VERSION=|STRUCTURE=Sedan|YEAR=2008-2012`) | 194.9/72.7/58.1 | 774,843 | 0.980 |
| 长 | 长 | 低 | 51 | 5,186,308 | 197.8/74.4/56.0 | 2000-2007 Ford Taurus Sedan, Edmunds (`MAKE=Ford|MODEL=Taurus|VERSION=|STRUCTURE=Sedan|YEAR=2000-2007`) | 197.6/73.0/56.1 | 1,149,906 | 0.922 |
| 长 | 长 | 高 | 141 | 9,872,993 | 196.8/74.0/58.0 | 2023/2025 Chevrolet Malibu (`MAKE=Chevrolet|MODEL=Malibu|VERSION=|STRUCTURE=Sedan|YEAR=2016-2025`) | 194.2/73.0/57.9 | 1,293,738 | 0.928 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Toyota|MODEL=Camry|VERSION=|STRUCTURE=Sedan|YEAR=2012-2017 | 2012-2017 Toyota Camry sedan | 190.9 | 71.7 | 57.9 | 2,447,027 |
| MAKE=Toyota|MODEL=Camry|VERSION=|STRUCTURE=Sedan|YEAR=2018-2024 | 2018-2024 Toyota Camry sedan | 192.7 | 72.4 | 56.9 | 2,165,059 |
| MAKE=Toyota|MODEL=Camry|VERSION=|STRUCTURE=Sedan|YEAR=2002-2006 | 2002 Toyota Camry LE / XLE | 189.2 | 70.7 | 58.3 | 2,147,686 |
| MAKE=Toyota|MODEL=Corolla|VERSION=|STRUCTURE=Sedan|YEAR=2003-2008 | 2003-2008 Toyota Corolla Sedan CE/LE/S | 178.3 | 66.9 | 58.5 | 2,109,713 |
| MAKE=Toyota|MODEL=Camry|VERSION=|STRUCTURE=Sedan|YEAR=1997-2001 | 1997 Toyota Camry sedan | 188.5 | 70.1 | 55.4 | 2,076,071 |

## 车形 31 — Sedan/Coupe Low Sport

- 记录 636 条(含无三维 0 条), 有销量 598 条, 总销量 **41,933,838**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **187.4 / 71.8 / 52.4**。
- 销量集中度: 前 5 名占 9.6%; 累计 161 条记录(占记录数 25.3%)可达 80% 销量。
- 主要分类分布: 跑车×561, 三厢车×60, 两厢车×15。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Ford|MODEL=Thunderbird|VERSION=|STRUCTURE=Coupe|YEAR=2002-2005 | 2002/2005 Ford Thunderbird Deluxe / Premium | 186.3 | 72.0 | 52.1 | 69,137 | 0.026 |
| MAKE=Ford|MODEL=Thunderbird|VERSION=|STRUCTURE=Convertible|YEAR=1956 | 1956 Ford Thunderbird Convertible | 185.2 | 71.3 | 52.4 | 15,631 | 0.042 |
| MAKE=Jaguar|MODEL=XK|VERSION=|STRUCTURE=Convertible|YEAR=1997-2004 | 1997/2004 Jaguar XK8 Convertible, Edmunds / Automobile-Catalog | 187.4 | 72.0 | 51.4 | 17,900 | 0.063 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 97 | 6,044,725 | 170.7/67.5/50.0 | 1974/1978 Ford Mustang II Coupe, CarsGuide/Automobile-Catalog (`MAKE=Ford|MODEL=Mustang|VERSION=|STRUCTURE=Coupe|YEAR=1974-1978`) | 175.0/70.2/49.6 | 553,861 | 0.760 |
| 短 | 短 | 高 | 33 | 1,515,697 | 173.2/68.5/52.8 | 2005 Scion tC Base (`MAKE=Scion|MODEL=tC|VERSION=|STRUCTURE=Coupe|YEAR=2005-2010`) | 174.0/69.1/55.7 | 291,574 | 0.796 |
| 短 | 中 | 低 | 39 | 329,469 | 172.5/71.7/51.1 | 2024 Porsche 718 Cayman trims, Edmunds / C&D (`MAKE=Porsche|MODEL=Cayman|VERSION=|STRUCTURE=Coupe|YEAR=2017-2025`) | 175.4/71.7/51.0 | 33,323 | 0.950 |
| 短 | 中 | 高 | 9 | 74,135 | 167.2/72.5/52.3 | 2013 Nissan 370Z Convertible, Edmunds (`MAKE=Nissan|MODEL=370Z|VERSION=|STRUCTURE=Convertible|YEAR=2010-2019`) | 167.2/72.6/52.2 | 27,246 | 0.956 |
| 短 | 长 | 低 | 34 | 154,957 | 175.6/75.9/49.0 | 2006-2008 Chevrolet Corvette Z06 (`MAKE=Chevrolet|MODEL=Corvette|VERSION=Z06|STRUCTURE=Coupe|YEAR=2006-2008`) | 175.6/75.9/49.0 | 54,945 | 1.000 |
| 中 | 短 | 低 | 32 | 3,623,887 | 181.6/68.2/51.4 | 1965-1966 Ford Mustang Convertible, Ford brochure/Carfolio (`MAKE=Ford|MODEL=Mustang|VERSION=|STRUCTURE=Convertible|YEAR=1965-1966`) | 181.6/68.2/51.4 | 583,510 | 1.000 |
| 中 | 短 | 高 | 35 | 4,417,312 | 179.6/69.1/52.1 | 1979/1986 Ford Mustang Coupe, Carfolio/Conceptcarz/MustangSpecs / 1985-1986 Ford Mustang Coupe MustangSpecs/Conceptcarz/Carfolio (`MAKE=Ford|MODEL=Mustang|VERSION=|STRUCTURE=Coupe|YEAR=1979-1986`) | 179.3/69.1/52.1 | 711,687 | 0.996 |
| 中 | 中 | 低 | 53 | 1,614,778 | 186.0/72.5/51.0 | 1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz (`MAKE=Chevrolet|MODEL=Camaro|VERSION=|STRUCTURE=Coupe|YEAR=1967-1969`) | 186.0/72.5/51.0 | 349,568 | 1.000 |
| 中 | 中 | 高 | 49 | 2,383,757 | 183.2/72.5/53.3 | 1999-2004 Ford Mustang Coupe/GT, Edmunds (`MAKE=Ford|MODEL=Mustang|VERSION=|STRUCTURE=Coupe|YEAR=1999-2004`) | 183.2/73.1/53.3 | 391,625 | 0.933 |
| 中 | 长 | 低 | 27 | 792,536 | 184.9/75.9/49.1 | 2013 Corvette ZR1 / base C6 (`MAKE=Chevrolet|MODEL=Corvette|VERSION=Z06/ZR1|STRUCTURE=Coupe|YEAR=2005-2013`) | 177.9/75.9/49.1 | 130,742 | 0.738 |
| 中 | 长 | 高 | 16 | 216,502 | 183.0/73.5/54.2 | 2013-2017 Audi A5/S5/RS5 Coupe (`MAKE=Audi|MODEL=A5/S5/RS5|VERSION=|STRUCTURE=Coupe|YEAR=2013-2017`) | 183.0/73.2/54.0 | 48,268 | 0.915 |
| 长 | 短 | 低 | 4 | 58,937 | 191.7/70.6/49.6 | 1984/1989-1991 Jaguar XJS Convertible, CarsGuide/Edmunds (`MAKE=Jaguar|MODEL=XJS|VERSION=|STRUCTURE=Convertible|YEAR=1984-1991`) | 191.7/70.6/49.6 | 34,199 | 1.000 |
| 长 | 短 | 高 | 22 | 2,482,940 | 192.6/70.1/54.2 | 1984/1988 Mercury Cougar XR7 (`MAKE=Mercury|MODEL=Cougar|VERSION=|STRUCTURE=Coupe|YEAR=1984-1988`) | 200.8/70.1/53.6 | 604,016 | 0.862 |
| 长 | 中 | 低 | 14 | 1,287,677 | 191.8/72.4/50.0 | 1983/1984/1985/1986/1987/1988 Firebird / Trans Am (`MAKE=Pontiac|MODEL=Firebird|VERSION=Trans Am|STRUCTURE=Coupe|YEAR=1983-1988`) | 191.8/72.4/50.0 | 560,573 | 1.000 |
| 长 | 中 | 高 | 45 | 6,502,223 | 196.5/72.5/54.7 | 1983-1986 Ford Thunderbird Coupe, Automobile-Catalog/Wikipedia (`MAKE=Ford|MODEL=Thunderbird|VERSION=|STRUCTURE=Coupe|YEAR=1983-1986`) | 197.6/71.1/53.2 | 608,367 | 0.851 |
| 长 | 长 | 低 | 31 | 4,339,883 | 195.4/74.1/49.6 | 1974-1981 Trans Am / Formula (`MAKE=Pontiac|MODEL=Firebird|VERSION=Trans Am|STRUCTURE=Coupe|YEAR=1974-1981`) | 196.8/73.2/49.6 | 1,001,288 | 0.952 |
| 长 | 长 | 高 | 96 | 6,094,423 | 193.8/75.0/55.2 | 2015-2023 Dodge Charger Sedan (`MAKE=Dodge|MODEL=Charger|VERSION=|STRUCTURE=Sedan|YEAR=2015-2023`) | 198.4/75.0/58.2 | 746,948 | 0.844 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Pontiac|MODEL=Firebird|VERSION=Trans Am|STRUCTURE=Coupe|YEAR=1974-1981 | 1974-1981 Trans Am / Formula | 196.8 | 73.2 | 49.6 | 1,001,288 |
| MAKE=Chevrolet|MODEL=Camaro|VERSION=|STRUCTURE=Coupe|YEAR=1978-1981 | 1980 Chevrolet Camaro Coupe, ConceptCarz | 197.6 | 74.5 | 49.2 | 833,346 |
| MAKE=Dodge|MODEL=Charger|VERSION=|STRUCTURE=Sedan|YEAR=2015-2023 | 2015-2023 Dodge Charger Sedan | 198.4 | 75.0 | 58.2 | 746,948 |
| MAKE=Ford|MODEL=Mustang|VERSION=|STRUCTURE=Coupe|YEAR=1979-1986 | 1979/1986 Ford Mustang Coupe, Carfolio/Conceptcarz/MustangSpecs / 1985-1986 Ford Mustang Coupe MustangSpecs/Conceptcarz/Carfolio | 179.3 | 69.1 | 52.1 | 711,687 |
| MAKE=Ford|MODEL=Mustang|VERSION=|STRUCTURE=Hatchback|YEAR=1979-1986 | 1979/1986 Ford Mustang Hatchback, Carfolio/Conceptcarz/MustangSpecs / 1985-1986 Ford Mustang Hatchback, CJ Pony Parts/Conceptcarz | 179.3 | 69.1 | 52.1 | 711,684 |

## 车形 32 — Sedan/Coupe Boxy Classic 老式方正轿车

- 记录 886 条(含无三维 0 条), 有销量 837 条, 总销量 **96,356,483**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **204.0 / 75.0 / 54.4**。
- 销量集中度: 前 5 名占 5.9%; 累计 335 条记录(占记录数 37.8%)可达 80% 销量。
- 主要分类分布: 跑车×477, 三厢车×405, 两厢车×4。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Oldsmobile|MODEL=Cutlass|VERSION=|STRUCTURE=Sedan|YEAR=1966 | 1966 Oldsmobile F-85 / Cutlass 4-Door Sedan | 204.2 | 75.4 | 54.5 | 63,333 | 0.019 |
| MAKE=Buick|MODEL=Skylark|VERSION=|STRUCTURE=Convertible|YEAR=1966 | 1966 Buick Skylark Convertible / 1966 Buick Skylark Coupe | 204.0 | 75.5 | 54.3 | 31,666 | 0.024 |
| MAKE=Buick|MODEL=Skylark|VERSION=|STRUCTURE=Coupe|YEAR=1966 | 1966 Buick Skylark Convertible / 1966 Buick Skylark Coupe | 204.0 | 75.5 | 54.3 | 31,667 | 0.024 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 148 | 25,042,439 | 188.4/71.0/53.7 | 1967-1968 Valiant Coupe (`MAKE=Plymouth|MODEL=Valiant|VERSION=|STRUCTURE=Coupe|YEAR=1967-1972`) | 188.4/71.1/54.0 | 1,017,101 | 0.953 |
| 短 | 短 | 高 | 90 | 13,564,400 | 196.2/72.4/55.5 | 1978-1987 Grand Prix LJ/Brougham (`MAKE=Pontiac|MODEL=Grand Prix|VERSION=|STRUCTURE=Coupe|YEAR=1978-1987`) | 201.9/72.8/54.7 | 1,061,437 | 0.942 |
| 短 | 中 | 低 | 44 | 5,211,151 | 197.5/75.0/53.0 | 1968-1972 Chevrolet Chevelle 2-Door / Convertible (`MAKE=Chevrolet|MODEL=Chevelle|VERSION=|STRUCTURE=Convertible|YEAR=1968-1972`) | 197.5/76.0/53.2 | 637,337 | 0.879 |
| 短 | 中 | 高 | 14 | 2,173,303 | 200.0/75.0/55.7 | 1992/1996 Buick LeSabre Sedan Edmunds (`MAKE=Buick|MODEL=LeSabre|VERSION=|STRUCTURE=Sedan|YEAR=1992-1996`) | 200.0/74.9/55.7 | 680,037 | 0.996 |
| 中 | 短 | 低 | 36 | 1,732,805 | 204.3/73.6/54.2 | 1994 Cadillac Seville STS/SLS (`MAKE=Cadillac|MODEL=Seville|VERSION=STS/SLS|STRUCTURE=Sedan|YEAR=1994-1997`) | 204.1/74.2/54.5 | 165,999 | 0.905 |
| 中 | 短 | 高 | 22 | 1,723,494 | 205.1/73.4/55.4 | 1988-1991 Lincoln Continental / 1988/1992/1994 Lincoln Continental (`MAKE=Lincoln|MODEL=Continental|VERSION=|STRUCTURE=Sedan|YEAR=1988-1993`) | 205.1/72.7/55.6 | 278,218 | 0.961 |
| 中 | 中 | 低 | 96 | 9,772,811 | 209.6/76.7/53.1 | 1976-1977 Chevrolet Monte Carlo Coupe / 1975-1977 Chevrolet Monte Carlo Coupe (`MAKE=Chevrolet|MODEL=Monte Carlo|VERSION=|STRUCTURE=Coupe|YEAR=1973-1977`) | 213.3/77.6/52.9 | 1,541,575 | 0.785 |
| 中 | 中 | 高 | 82 | 9,169,015 | 212.0/77.7/56.8 | 1983/1988/1991 Mercury Grand Marquis (`MAKE=Mercury|MODEL=Grand Marquis|VERSION=|STRUCTURE=Sedan|YEAR=1983-1991`) | 214.0/77.5/55.5 | 987,818 | 0.957 |
| 中 | 长 | 低 | 21 | 1,155,150 | 213.2/79.1/54.1 | 1973-1975 Buick Regal Hardtop Coupe (`MAKE=Buick|MODEL=Regal|VERSION=|STRUCTURE=Coupe|YEAR=1973-1975`) | 213.6/79.0/53.3 | 225,774 | 0.880 |
| 中 | 长 | 高 | 42 | 4,132,868 | 213.1/79.6/55.8 | 1969 Plymouth Fury (`MAKE=Plymouth|MODEL=Fury|VERSION=|STRUCTURE=Coupe|YEAR=1969-1972`) | 214.5/79.6/55.8 | 425,500 | 0.985 |
| 长 | 中 | 低 | 14 | 2,298,322 | 217.5/76.5/54.4 | 1975-1976 Oldsmobile Cutlass Sedan, Automobile-Catalog / 1976 brochure (`MAKE=Oldsmobile|MODEL=Cutlass|VERSION=|STRUCTURE=Sedan|YEAR=1975-1976`) | 215.7/76.7/54.1 | 460,000 | 0.899 |
| 长 | 中 | 高 | 46 | 3,813,332 | 218.9/76.9/56.0 | 1992-1997 Lincoln Town Car, Automobile-Catalog (`MAKE=Lincoln|MODEL=Town Car|VERSION=|STRUCTURE=Sedan|YEAR=1992-1997`) | 218.9/76.9/56.9 | 638,620 | 0.964 |
| 长 | 长 | 低 | 90 | 7,861,171 | 220.0/79.5/53.9 | 1977-1979 Ford Thunderbird Coupe (`MAKE=Ford|MODEL=Thunderbird|VERSION=|STRUCTURE=Coupe|YEAR=1977-1979`) | 217.2/78.5/52.8 | 936,038 | 0.751 |
| 长 | 长 | 高 | 141 | 8,706,222 | 221.7/79.9/55.6 | 1967-1969 Chevrolet Bel Air 2-Door Sedan / full-size / 1967-1969 Chevrolet Bel Air 4-Door Sedan / full-size (`MAKE=Chevrolet|MODEL=Bel Air|VERSION=|STRUCTURE=Sedan|YEAR=1967-1969`) | 219.9/80.0/55.4 | 370,000 | 0.981 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Chevrolet|MODEL=Monte Carlo|VERSION=|STRUCTURE=Coupe|YEAR=1973-1977 | 1976-1977 Chevrolet Monte Carlo Coupe / 1975-1977 Chevrolet Monte Carlo Coupe | 213.3 | 77.6 | 52.9 | 1,541,575 |
| MAKE=Buick|MODEL=Regal|VERSION=|STRUCTURE=Coupe|YEAR=1981-1987 | 1981-1987 Buick Regal Coupe | 200.6 | 71.6 | 54.5 | 1,083,320 |
| MAKE=Pontiac|MODEL=Grand Prix|VERSION=|STRUCTURE=Coupe|YEAR=1978-1987 | 1978-1987 Grand Prix LJ/Brougham | 201.9 | 72.8 | 54.7 | 1,061,437 |
| MAKE=Plymouth|MODEL=Valiant|VERSION=|STRUCTURE=Coupe|YEAR=1967-1972 | 1967-1968 Valiant Coupe | 188.4 | 71.1 | 54.0 | 1,017,101 |
| MAKE=Mercury|MODEL=Grand Marquis|VERSION=|STRUCTURE=Sedan|YEAR=1983-1991 | 1983/1988/1991 Mercury Grand Marquis | 214.0 | 77.5 | 55.5 | 987,818 |

## 车形 40 — SUV 常规 SUV

- 记录 347 条(含无三维 0 条), 有销量 293 条, 总销量 **47,942,897**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **190.2 / 75.8 / 72.5**。
- 销量集中度: 前 5 名占 13.4%; 累计 110 条记录(占记录数 31.7%)可达 80% 销量。
- 主要分类分布: 越野车×345, 两厢车×2。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Land Rover|MODEL=LR4|VERSION=|STRUCTURE=SUV|YEAR=2013 | 2013 Land Rover LR4 | 190.1 | 75.4 | 72.5 | 7,093 | 0.021 |
| MAKE=Lexus|MODEL=LX|VERSION=|STRUCTURE=SUV|YEAR=1999-2007 | 2007 Lexus LX 470 / 1999-2007 Lexus LX 470 | 192.5 | 76.4 | 72.8 | 82,940 | 0.044 |
| MAKE=Toyota|MODEL=Land Cruiser|VERSION=|STRUCTURE=SUV|YEAR=1991-1997 | Toyota Land Cruiser 80 Series | 188.2 | 76.0 | 73.2 | 91,000 | 0.045 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 93 | 12,514,869 | 174.9/70.2/67.0 | Ford Explorer Sport (`MAKE=Ford|MODEL=Explorer|VERSION=|STRUCTURE=SUV|YEAR=1991-1994`) | 174.4/70.2/67.5 | 1,170,487 | 0.973 |
| 短 | 短 | 高 | 5 | 560,828 | 178.0/70.4/73.6 | 2000 Nissan Xterra SE (`MAKE=Nissan|MODEL=Xterra|VERSION=|STRUCTURE=SUV|YEAR=2000-2004`) | 178.0/70.4/73.6 | 375,268 | 1.000 |
| 短 | 中 | 低 | 12 | 1,513,559 | 174.8/74.2/70.2 | 2024 Ford Bronco Sport Big Bend, Edmunds (`MAKE=Ford|MODEL=Bronco Sport|VERSION=4dr|STRUCTURE=SUV|YEAR=2024-2026`) | 172.7/74.3/70.2 | 339,843 | 0.963 |
| 短 | 中 | 高 | 1 | 338,527 | 178.7/72.8/74.9 | 2015 Nissan Xterra X (`MAKE=Nissan|MODEL=Xterra|VERSION=|STRUCTURE=SUV|YEAR=2005-2015`) | 178.7/72.8/74.9 | 338,527 | 1.000 |
| 短 | 长 | 低 | 3 | 65,462 | 177.5/79.0/70.0 | 1972 Chevrolet K5 Blazer brochure (`MAKE=Chevrolet|MODEL=Blazer|VERSION=|STRUCTURE=SUV|YEAR=1972`) | 180.0/79.0/70.1 | 24,000 | 0.801 |
| 短 | 长 | 高 | 2 | 79,486 | 180.0/79.0/72.8 | 1971-1972 Chevrolet Blazer specs (`MAKE=Chevrolet|MODEL=K5 Blazer|VERSION=|STRUCTURE=SUV|YEAR=1971-1972`) | 180.0/79.0/72.8 | 61,486 | 1.000 |
| 中 | 短 | 低 | 12 | 975,887 | 189.5/72.1/71.9 | 2003-2005 Ford Explorer Edmunds (`MAKE=Ford|MODEL=Explorer|VERSION=|STRUCTURE=SUV|YEAR=2003-2005`) | 189.5/72.1/71.9 | 476,120 | 1.000 |
| 中 | 短 | 高 | 6 | 874,433 | 193.3/71.5/72.9 | 1999 Dodge Durango SUV (`MAKE=Dodge|MODEL=Durango|VERSION=|STRUCTURE=SUV|YEAR=1999-2001`) | 193.3/71.5/72.9 | 494,206 | 1.000 |
| 中 | 中 | 低 | 32 | 7,112,098 | 191.3/75.8/71.5 | 2023 Toyota 4Runner (`MAKE=Toyota|MODEL=4Runner|VERSION=|STRUCTURE=SUV|YEAR=2014-2024`) | 191.3/75.8/71.5 | 1,291,929 | 1.000 |
| 中 | 中 | 高 | 41 | 4,601,834 | 191.8/74.7/72.8 | 2005 Chevrolet Trailblazer LT (`MAKE=Chevrolet|MODEL=Trailblazer|VERSION=|STRUCTURE=SUV|YEAR=2002-2005`) | 191.8/74.7/72.5 | 1,038,536 | 0.974 |
| 中 | 长 | 低 | 9 | 435,962 | 184.5/79.5/71.9 | 1978-1979 Chevrolet K5 Blazer, Automobile-Catalog / UltimateSpecs (`MAKE=Chevrolet|MODEL=Blazer|VERSION=|STRUCTURE=SUV|YEAR=1978-1979`) | 184.5/79.6/72.1 | 175,000 | 0.969 |
| 中 | 长 | 高 | 15 | 4,275,186 | 184.8/79.6/73.8 | 1980/1990-1991 Chevrolet K5 Blazer (`MAKE=Chevrolet|MODEL=Blazer|VERSION=|STRUCTURE=SUV|YEAR=1980-1991`) | 184.8/79.6/73.8 | 1,651,410 | 1.000 |
| 长 | 中 | 低 | 14 | 1,053,669 | 201.8/76.4/70.1 | Ford Flex (`MAKE=Ford|MODEL=Flex|VERSION=|STRUCTURE=Crossover|YEAR=2009-2019`) | 201.8/75.9/68.0 | 287,790 | 0.814 |
| 长 | 中 | 高 | 16 | 1,876,875 | 204.6/78.6/76.6 | 1999-2000 Ford Expedition XLT/Eddie Bauer, Edmunds (`MAKE=Ford|MODEL=Expedition|VERSION=|STRUCTURE=SUV|YEAR=1997-2000`) | 204.6/78.6/76.6 | 862,895 | 1.000 |
| 长 | 长 | 低 | 1 | 118,000 | 219.1/79.6/72.0 | 1990-1991 Chevrolet Suburban 1500/2500, Edmunds (`MAKE=Chevrolet|MODEL=Suburban|VERSION=|STRUCTURE=SUV|YEAR=1990-1991`) | 219.1/79.6/72.0 | 118,000 | 1.000 |
| 长 | 长 | 高 | 85 | 11,546,222 | 210.0/79.8/76.5 | 2007-2008 Chevrolet Tahoe (`MAKE=Chevrolet|MODEL=Tahoe|VERSION=|STRUCTURE=SUV|YEAR=2007-2014`) | 202.0/79.0/76.9 | 721,634 | 0.869 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Chevrolet|MODEL=Blazer|VERSION=|STRUCTURE=SUV|YEAR=1980-1991 | 1980/1990-1991 Chevrolet K5 Blazer | 184.8 | 79.6 | 73.8 | 1,651,410 |
| MAKE=Toyota|MODEL=4Runner|VERSION=|STRUCTURE=SUV|YEAR=2014-2024 | 2023 Toyota 4Runner | 191.3 | 75.8 | 71.5 | 1,291,929 |
| MAKE=Ford|MODEL=Explorer|VERSION=|STRUCTURE=SUV|YEAR=1995-1997 | Ford Explorer Sport | 178.6 | 70.2 | 67.0 | 1,181,742 |
| MAKE=Ford|MODEL=Explorer|VERSION=|STRUCTURE=SUV|YEAR=1991-1994 | Ford Explorer Sport | 174.4 | 70.2 | 67.5 | 1,170,487 |
| MAKE=Chevrolet|MODEL=Tahoe|VERSION=|STRUCTURE=SUV|YEAR=2001-2006 | 2001-2003 Chevrolet Tahoe / 2001 Chevrolet Tahoe | 198.8 | 78.9 | 76.5 | 1,111,108 |

## 车形 41 — SUV Fastback 溜背 SUV

- 记录 431 条(含无三维 0 条), 有销量 412 条, 总销量 **101,584,430**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **183.5 / 73.4 / 67.0**。
- 销量集中度: 前 5 名占 10.5%; 累计 143 条记录(占记录数 33.2%)可达 80% 销量。
- 主要分类分布: 越野车×422, 跑车×7, 两厢车×2。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Kia|MODEL=Sportage|VERSION=PHEV|STRUCTURE=SUV|YEAR=2023-2026 | 2026 Kia Sportage Plug-In Hybrid, Edmunds / 2026 Kia Sportage Plug-In Hybrid | 184.4 | 73.4 | 66.9 | 337,759 | 0.016 |
| MAKE=Mazda|MODEL=CX-5|VERSION=|STRUCTURE=SUV|YEAR=2026 | 2026 Mazda CX-5 | 184.6 | 73.2 | 66.7 | 62,691 | 0.030 |
| MAKE=Pontiac|MODEL=Aztec|VERSION=|STRUCTURE=Crossover|YEAR=2001-2005 | 2005 Pontiac Aztek, Edmunds / Cars.com / KBB | 182.1 | 73.7 | 66.7 | 108,077 | 0.037 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 92 | 22,011,030 | 176.4/71.5/65.1 | Ford Escape Titanium (`MAKE=Ford|MODEL=Escape|VERSION=|STRUCTURE=SUV|YEAR=2013-2019`) | 178.1/72.4/66.3 | 2,037,674 | 0.932 |
| 短 | 短 | 高 | 21 | 4,674,134 | 180.1/72.4/67.3 | 2013-2018 Toyota RAV4 / 2013 Toyota RAV4 EV Edmunds (`MAKE=Toyota|MODEL=RAV4|VERSION=|STRUCTURE=SUV|YEAR=2013-2018`) | 180.1/72.6/67.1 | 1,745,287 | 0.980 |
| 短 | 中 | 低 | 19 | 3,898,040 | 176.4/73.8/64.8 | 2017-2026 Jeep Compass (`MAKE=Jeep|MODEL=Compass|VERSION=|STRUCTURE=SUV|YEAR=2017-2026`) | 173.4/73.8/64.8 | 1,033,947 | 0.878 |
| 短 | 中 | 高 | 5 | 862,522 | 181.1/73.0/68.7 | 2006-2008 Toyota RAV4 Sport/Limited Edmunds/KBB (`MAKE=Toyota|MODEL=RAV4|VERSION=|STRUCTURE=SUV|YEAR=2006-2008`) | 181.1/73.0/68.7 | 461,819 | 1.000 |
| 短 | 长 | 低 | 7 | 361,361 | 173.0/77.4/64.4 | 2012/2016 Range Rover Evoque, Edmunds (`MAKE=Land Rover|MODEL=Evoque|VERSION=|STRUCTURE=Coupe|YEAR=2012-2018`) | 172.0/78.1/64.4 | 81,016 | 0.696 |
| 中 | 短 | 低 | 15 | 7,092,025 | 183.1/72.4/66.1 | 2018-2024 Chevrolet Equinox (`MAKE=Chevrolet|MODEL=Equinox|VERSION=|STRUCTURE=SUV|YEAR=2018-2024`) | 183.1/72.6/65.4 | 1,747,486 | 0.924 |
| 中 | 短 | 高 | 20 | 8,597,712 | 184.5/72.4/68.9 | 2014-2015/2020 Nissan Rogue S/SV/SL, Edmunds / 2015/2020 Nissan Rogue SV/SL, Edmunds (`MAKE=Nissan|MODEL=Rogue|VERSION=|STRUCTURE=SUV|YEAR=2016-2020`) | 184.5/72.4/68.5 | 1,723,861 | 0.906 |
| 中 | 中 | 低 | 60 | 13,312,096 | 183.5/73.5/66.2 | 2022 Honda CR-V / CR-V Hybrid / 2020-2022 Honda CR-V / CR-V Hybrid, Edmunds (`MAKE=Honda|MODEL=CR-V|VERSION=|STRUCTURE=SUV|YEAR=2017-2022`) | 182.1/73.0/66.5 | 2,074,004 | 0.916 |
| 中 | 中 | 高 | 32 | 10,708,185 | 184.4/74.1/68.6 | 2019-2025 Toyota RAV4 Adventure / Hybrid / PHEV Edmunds (`MAKE=Toyota|MODEL=RAV4|VERSION=|STRUCTURE=SUV|YEAR=2019-2025`) | 181.5/73.4/68.6 | 3,002,109 | 0.863 |
| 中 | 长 | 低 | 9 | 396,221 | 186.1/76.2/63.9 | 2019-2025 Porsche Macan / Macan GTS (`MAKE=Porsche|MODEL=Macan|VERSION=|STRUCTURE=SUV|YEAR=2019-2025`) | 186.1/76.2/63.9 | 122,225 | 1.000 |
| 中 | 长 | 高 | 8 | 1,053,221 | 186.7/76.0/67.3 | 2011-2014 Ford Edge, Edmunds / Car and Driver (`MAKE=Ford|MODEL=Edge|VERSION=|STRUCTURE=SUV|YEAR=2011-2014`) | 184.2/76.0/67.0 | 487,644 | 0.952 |
| 长 | 短 | 低 | 1 | 464,036 | 192.4/72.2/66.6 | 2020 Dodge Journey (`MAKE=Dodge|MODEL=Journey|VERSION=|STRUCTURE=Crossover|YEAR=2009-2020`) | 192.4/72.2/66.6 | 464,036 | 1.000 |
| 长 | 短 | 高 | 2 | 514,115 | 192.4/72.2/67.0 | 2009 Dodge Journey (`MAKE=Dodge|MODEL=Journey|VERSION=|STRUCTURE=SUV|YEAR=2009-2020`) | 192.4/72.2/67.0 | 464,028 | 1.000 |
| 长 | 中 | 低 | 8 | 879,162 | 190.3/75.2/65.9 | 2010-2011/2014-2016 Cadillac SRX (`MAKE=Cadillac|MODEL=SRX|VERSION=|STRUCTURE=SUV|YEAR=2010-2016`) | 190.3/75.2/65.7 | 366,827 | 0.968 |
| 长 | 中 | 高 | 16 | 4,304,014 | 192.5/75.4/67.8 | 2014 Toyota Highlander Hybrid (`MAKE=Toyota|MODEL=Highlander|VERSION=|STRUCTURE=SUV|YEAR=2014-2019`) | 192.5/75.8/70.1 | 1,196,145 | 0.860 |
| 长 | 长 | 低 | 8 | 375,658 | 190.0/76.1/66.2 | 2023 Lincoln Nautilus / 2019 Lincoln official tech specs (`MAKE=Lincoln|MODEL=Nautilus|VERSION=|STRUCTURE=SUV|YEAR=2019-2023`) | 190.0/76.1/66.2 | 123,491 | 1.000 |
| 长 | 长 | 高 | 108 | 22,080,898 | 197.1/78.3/70.4 | 2016-2022 Honda Pilot Edmunds (`MAKE=Honda|MODEL=Pilot|VERSION=|STRUCTURE=SUV|YEAR=2016-2022`) | 196.5/78.6/70.6 | 909,116 | 0.860 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Toyota|MODEL=RAV4|VERSION=|STRUCTURE=SUV|YEAR=2019-2025 | 2019-2025 Toyota RAV4 Adventure / Hybrid / PHEV Edmunds | 181.5 | 73.4 | 68.6 | 3,002,109 |
| MAKE=Honda|MODEL=CR-V|VERSION=|STRUCTURE=SUV|YEAR=2017-2022 | 2022 Honda CR-V / CR-V Hybrid / 2020-2022 Honda CR-V / CR-V Hybrid, Edmunds | 182.1 | 73.0 | 66.5 | 2,074,004 |
| MAKE=Ford|MODEL=Escape|VERSION=|STRUCTURE=SUV|YEAR=2013-2019 | Ford Escape Titanium | 178.1 | 72.4 | 66.3 | 2,037,674 |
| MAKE=Chevrolet|MODEL=Equinox|VERSION=|STRUCTURE=SUV|YEAR=2010-2017 | 2010-2017 Chevrolet Equinox | 187.8 | 72.5 | 69.3 | 1,852,550 |
| MAKE=Chevrolet|MODEL=Equinox|VERSION=|STRUCTURE=SUV|YEAR=2018-2024 | 2018-2024 Chevrolet Equinox | 183.1 | 72.6 | 65.4 | 1,747,486 |

## 车形 42 — SUV 方正 SUV

- 记录 96 条(含无三维 0 条), 有销量 83 条, 总销量 **5,058,763**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **188.8 / 75.6 / 64.0**。
- 销量集中度: 前 5 名占 51.6%; 累计 24 条记录(占记录数 25.0%)可达 80% 销量。
- 主要分类分布: 越野车×96。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Tesla|MODEL=Model Y|VERSION=Performance|STRUCTURE=SUV|YEAR=2025-2026 | 2026 Tesla Model Y Performance | 188.8 | 75.6 | 64.0 | 627,800 | 0.000 |
| MAKE=BMW|MODEL=X4|VERSION=|STRUCTURE=SUV|YEAR=2019-2025 | 2019-2021 BMW X4 xDrive30i / M40i, Edmunds | 2022-2025 BMW X4 xDrive30i, Edmunds | 187.6 | 75.5 | 63.8 | 0 | 0.036 |
| MAKE=Tesla|MODEL=Model Y|VERSION=|STRUCTURE=Crossover|YEAR=2020-2024 | 2020-2024 Tesla Model Y | 187.0 | 75.6 | 64.0 | 1,235,900 | 0.046 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 24 | 645,530 | 179.3/71.5/61.6 | 2024-2026 Buick Envista (`MAKE=Buick|MODEL=Envista|VERSION=|STRUCTURE=SUV|YEAR=2024-2026`) | 182.6/71.5/61.2 | 124,317 | 0.920 |
| 短 | 短 | 高 | 3 | 109,887 | 179.0/71.1/66.5 | 2026 Mitsubishi Eclipse Cross, Edmunds/C&D (`MAKE=Mitsubishi|MODEL=Eclipse Cross|VERSION=|STRUCTURE=Crossover|YEAR=2022-2026`) | 179.0/71.1/66.5 | 70,422 | 1.000 |
| 短 | 中 | 低 | 3 | 112,985 | 172.1/75.0/64.9 | 2020-2026 Land Rover Range Rover Evoque (`MAKE=Land Rover|MODEL=Range Rover Evoque|VERSION=|STRUCTURE=SUV|YEAR=2020-2026`) | 172.1/75.0/64.9 | 52,734 | 1.000 |
| 短 | 中 | 高 | 2 | 48,348 | 182.9/74.8/65.4 | 2023-2025 Nissan Ariya, Edmunds / 2025 Nissan Ariya Engage (`MAKE=Nissan|MODEL=Ariya|VERSION=|STRUCTURE=SUV|YEAR=2023-2026`) | 182.9/74.8/65.4 | 48,348 | 1.000 |
| 中 | 短 | 低 | 5 | 109,428 | 185.6/74.1/64.0 | 2021-2022 Ford Mustang Mach-E trims (`MAKE=Ford|MODEL=Mustang Mach-E|VERSION=|STRUCTURE=SUV|YEAR=2021-2022`) | 185.6/74.1/64.0 | 66,598 | 1.000 |
| 中 | 中 | 低 | 7 | 2,142,982 | 187.0/75.6/64.0 | 2020-2024 Tesla Model Y (`MAKE=Tesla|MODEL=Model Y|VERSION=|STRUCTURE=Crossover|YEAR=2020-2024`) | 187.0/75.6/64.0 | 1,235,900 | 1.000 |
| 中 | 中 | 高 | 10 | 723,767 | 191.4/76.7/67.0 | 2019-2022 Chevrolet Blazer (`MAKE=Chevrolet|MODEL=Blazer|VERSION=|STRUCTURE=SUV|YEAR=2019-2022`) | 191.4/76.7/67.0 | 290,284 | 1.000 |
| 中 | 长 | 低 | 1 | 1,200 | 190.5/79.1/60.4 | 2026 Polestar 4 Long Range / RAC-EVSpecifications fallback width (`MAKE=Polestar|MODEL=4|VERSION=|STRUCTURE=SUV|YEAR=2026`) | 190.5/79.1/60.4 | 1,200 | 1.000 |
| 中 | 长 | 高 | 9 | 314,158 | 192.0/79.5/70.1 | 2018 Range Rover Sport SVR / PHEV checked (`MAKE=Land Rover|MODEL=Range Rover Sport|VERSION=|STRUCTURE=SUV|YEAR=2018-2022`) | 192.2/79.5/71.0 | 100,209 | 0.932 |
| 长 | 中 | 低 | 6 | 97,115 | 196.7/77.8/63.9 | 2023-2025 Cadillac Lyriq (`MAKE=Cadillac|MODEL=Lyriq|VERSION=|STRUCTURE=SUV|YEAR=2023-2025`) | 196.7/77.8/63.9 | 58,527 | 1.000 |
| 长 | 中 | 高 | 4 | 12,758 | 197.0/77.5/66.1 | 2024 Maserati Levante GT Ultima / 2017 Maserati Levante SUV (`MAKE=Maserati|MODEL=Levante|VERSION=|STRUCTURE=SUV|YEAR=2017-2018`) | 197.0/77.5/66.1 | 6,958 | 1.000 |
| 长 | 长 | 低 | 2 | 18,861 | 192.7/78.0/64.8 | 2025 Chevrolet Blazer EV SS; 2026 Chevrolet Blazer EV SS (`MAKE=Chevrolet|MODEL=Blazer EV|VERSION=SS|STRUCTURE=Crossover|YEAR=2025-2026`) | 192.7/78.0/64.8 | 12,901 | 1.000 |
| 长 | 长 | 高 | 20 | 721,744 | 196.0/78.9/67.2 | 2026 Tesla Model X (`MAKE=Tesla|MODEL=Model X|VERSION=|STRUCTURE=SUV|YEAR=2016-2026`) | 199.1/78.9/66.1 | 244,837 | 0.880 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Tesla|MODEL=Model Y|VERSION=|STRUCTURE=Crossover|YEAR=2020-2024 | 2020-2024 Tesla Model Y | 187.0 | 75.6 | 64.0 | 1,235,900 |
| MAKE=Tesla|MODEL=Model Y|VERSION=Performance|STRUCTURE=SUV|YEAR=2025-2026 | 2026 Tesla Model Y Performance | 188.8 | 75.6 | 64.0 | 627,800 |
| MAKE=Chevrolet|MODEL=Blazer|VERSION=|STRUCTURE=SUV|YEAR=2019-2022 | 2019-2022 Chevrolet Blazer | 191.4 | 76.7 | 67.0 | 290,284 |
| MAKE=Tesla|MODEL=Model X|VERSION=|STRUCTURE=SUV|YEAR=2016-2026 | 2026 Tesla Model X | 199.1 | 78.9 | 66.1 | 244,837 |
| MAKE=Chevrolet|MODEL=Blazer|VERSION=|STRUCTURE=SUV|YEAR=2023-2026 | 2023-2026 Chevrolet Blazer RS | 191.9 | 76.7 | 67.0 | 213,508 |

## 车形 50 — SUV 硬派方盒 SUV

- 记录 60 条(含无三维 1 条), 有销量 48 条, 总销量 **6,909,293**。
- 三维整体代表点(L/W/H 销量加权中位, 英寸): **167.5 / 70.5 / 71.2**。
- 销量集中度: 前 5 名占 36.8%; 累计 20 条记录(占记录数 33.3%)可达 80% 销量。
- 另有 1 条无三维数据(如待补尺寸), 未参与选代表。
- 主要分类分布: 越野车×61。

### 近整体代表点 TOP3(最接近销量加权中位点的记录)

| 记录 | 代表车型 | L | W | H | 销量 | 距中心 |
|---|---|---:|---:|---:|---:|---:|
| MAKE=Jeep|MODEL=Wrangler|VERSION=2dr Unlimited Rubicon|STRUCTURE=SUV|YEAR=2005-2006 | 2006 Jeep Wrangler Unlimited Rubicon, Edmunds | 167.0 | 68.2 | 72.1 | 0 | 0.118 |
| MAKE=Jeep|MODEL=Wrangler|VERSION=2dr|STRUCTURE=SUV|YEAR=2015-2018 | 2015-2018 Jeep Wrangler JK 2dr, Edmunds / C&D | 164.3 | 73.7 | 72.6 | 352,507 | 0.173 |
| MAKE=Jeep|MODEL=Wrangler|VERSION=2dr|STRUCTURE=SUV|YEAR=2013-2014 | 2014 Jeep Wrangler 2dr, Car and Driver / Quadratec JK specs | 163.8 | 73.7 | 72.5 | 165,415 | 0.174 |

### 三维档位覆盖与档内代表

| L段 | W段 | H段 | 记录数 | 档销量 | 档中位 L/W/H | 档内代表 | 代表 L/W/H | 代表销量 | 得分 |
|---|---|---|---:|---:|---|---|---:|---:|---:|
| 短 | 短 | 低 | 14 | 1,137,538 | 153.0/66.0/71.9 | 1993 Jeep Wrangler S, Edmunds / YJ factory specs (`MAKE=Jeep|MODEL=Wrangler|VERSION=2dr|STRUCTURE=SUV|YEAR=1988-1990`) | 152.6/66.0/72.0 | 174,606 | 0.868 |
| 短 | 短 | 高 | 1 | 0 | 157.3/66.1/74.0 | 1983 Mitsubishi Montero 2-door (`MAKE=Mitsubishi|MODEL=Montero|VERSION=2dr SWB|STRUCTURE=SUV|YEAR=1983`) | 157.3/66.1/74.0 | 0 | 0.400 |
| 短 | 中 | 低 | 2 | 322,172 | 152.8/73.7/70.9 | 2007-2011 Jeep Wrangler 2dr, Edmunds (`MAKE=Jeep|MODEL=Wrangler|VERSION=2dr|STRUCTURE=SUV|YEAR=2007-2011`) | 152.8/73.7/70.9 | 251,337 | 1.000 |
| 短 | 中 | 高 | 3 | 231,125 | 152.1/68.8/73.2 | 1st gen Bronco specs，AutoEvolution / Kincer / CJ Pony Parts (`MAKE=Ford|MODEL=Bronco|VERSION=2dr|STRUCTURE=SUV|YEAR=1966-1977`) | 152.1/68.8/73.2 | 225,585 | 1.000 |
| 中 | 短 | 低 | 3 | 422,835 | 168.8/67.7/64.0 | 1994 Jeep Cherokee (`MAKE=Jeep|MODEL=Cherokee|VERSION=|STRUCTURE=SUV|YEAR=1994-1996`) | 168.8/67.7/64.0 | 343,889 | 1.000 |
| 中 | 中 | 低 | 8 | 2,757,392 | 167.5/70.5/64.0 | Cherokee XJ (`MAKE=Jeep|MODEL=Cherokee|VERSION=|STRUCTURE=SUV|YEAR=1984-1990`) | 165.3/70.5/64.0 | 817,649 | 0.967 |
| 中 | 中 | 高 | 2 | 50,000 | 173.7/75.9/74.1 | 2026 Ford Bronco 2-door Badlands/Sasquatch, Ford Canada / dealer specs (`MAKE=Ford|MODEL=Bronco|VERSION=2dr|STRUCTURE=SUV|YEAR=2026`) | 173.7/75.9/74.1 | 50,000 | 1.000 |
| 中 | 长 | 高 | 7 | 923,095 | 177.6/79.1/74.5 | 3rd gen Bronco，AutoEvolution / automobile-catalog / 1984-1986 Ford Bronco, Automobile-Catalog / AutoEvolution (`MAKE=Ford|MODEL=Bronco|VERSION=2dr|STRUCTURE=SUV|YEAR=1980-1986`) | 177.6/77.2/72.9 | 322,429 | 0.704 |
| 长 | 短 | 高 | 3 | 14,000 | 181.7/66.1/74.4 | 1990 Mitsubishi Montero LS 4-Door LWB, Edmunds (`MAKE=Mitsubishi|MODEL=Montero|VERSION=4dr LS LWB|STRUCTURE=SUV|YEAR=1990`) | 181.7/66.1/74.4 | 14,000 | 1.000 |
| 长 | 中 | 低 | 2 | 165,804 | 183.9/75.0/72.0 | 2014 Toyota FJ Cruiser (`MAKE=Toyota|MODEL=FJ Cruiser|VERSION=|STRUCTURE=SUV|YEAR=2007-2014`) | 183.9/75.0/72.0 | 165,804 | 1.000 |
| 长 | 中 | 高 | 4 | 317 | 181.1/70.5/90.0 | 1993 Land Rover Defender 110 NAS (`MAKE=Land Rover|MODEL=Defender|VERSION=110 NAS|STRUCTURE=SUV|YEAR=1993`) | 181.1/70.5/90.0 | 317 | 1.000 |
| 长 | 长 | 低 | 1 | 211,729 | 189.0/79.0/70.3 | Jeep Cherokee Chief / SJ (`MAKE=Jeep|MODEL=Cherokee|VERSION=|STRUCTURE=SUV|YEAR=1974-1983`) | 189.0/79.0/70.3 | 211,729 | 1.000 |
| 长 | 长 | 高 | 10 | 673,286 | 191.0/79.3/77.6 | 1996 Bronco，Edmunds / AutoEvolution (`MAKE=Ford|MODEL=Bronco|VERSION=2dr|STRUCTURE=SUV|YEAR=1992-1996`) | 183.6/79.1/74.5 | 162,703 | 0.711 |

### 销量 TOP5(不要求贴近三维中心)

| 记录 | 代表车型 | L | W | H | 销量 |
|---|---|---:|---:|---:|---:|
| MAKE=Jeep|MODEL=Cherokee|VERSION=|STRUCTURE=SUV|YEAR=1984-1990 | Cherokee XJ | 165.3 | 70.5 | 64.0 | 817,649 |
| MAKE=Jeep|MODEL=Cherokee|VERSION=|STRUCTURE=SUV|YEAR=1997-2001 | 1997-1999 Jeep Cherokee, Edmunds / Cherokee XJ | 167.5 | 69.4 | 64.0 | 657,547 |
| MAKE=Jeep|MODEL=Cherokee|VERSION=|STRUCTURE=SUV|YEAR=1991-1993 | 1994 / XJ source | 168.8 | 70.5 | 64.0 | 367,864 |
| MAKE=Jeep|MODEL=Wrangler|VERSION=2dr|STRUCTURE=SUV|YEAR=2015-2018 | 2015-2018 Jeep Wrangler JK 2dr, Edmunds / C&D | 164.3 | 73.7 | 72.6 | 352,507 |
| MAKE=Jeep|MODEL=Cherokee|VERSION=|STRUCTURE=SUV|YEAR=1994-1996 | 1994 Jeep Cherokee | 168.8 | 67.7 | 64.0 | 343,889 |

## 说明与风险

- 销量为历年原子销量累加, 含 2026 年未结束年份的年度化预估, 跨年份叠加仅为相对权重比较。
- 无销量记录(如停产早期年款)不代表不重要, 只说明未能关联到销量; 分档覆盖仍包含它们。
- 档内代表在销量为 0 的档位中按接近度选取, 可视为该尺寸区间的结构代表而非销量代表。
- 迭代状态非“可入库”的记录(待终核、待补尺寸等)仍纳入统计; 可 `record_scores.csv` 中查看状态列交叉核对。