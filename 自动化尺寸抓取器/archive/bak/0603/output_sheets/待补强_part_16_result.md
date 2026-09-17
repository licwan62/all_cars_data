# 文件名：待补强_part_16.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作/字段	描述
Lexus RX	迭代状态	2026 RX / RX Hybrid / RX PHEV 均为 192.5 × 75.6 × 67.3，可覆盖原 2023-2026 口径，改为可入库。
Edmunds
+2
Edmunds
+2

Lexus RZ	参考车型	补入 2025/2026 Edmunds，2024 仍待补强。
Edmunds
+1

Lexus TX	参考车型/数值	2025/2026 TX 500h F SPORT 为 203.5 × 78.3 × 70.1，可覆盖当前最大值口径，改为可入库。
Edmunds
+1

Lexus UX	2025-2026	2025/2026 UX 300h 均为 177.0 × 72.4 × 60.6，可入库。
Edmunds
+1

Lincoln Aviator	2025-2026	2025 Edmunds 为 199.7 × 79.6 × 69.2；2026 Lincoln 页面显示高度最高 69.6，当前行宽高口径可继续用 79.6/69.6。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus RX	Lexus	越野车	SUV	inc: PHEV	gen5 midsize SUV	2023-2026	192.5	75.6	67.3	2023/2024/2025/2026 Lexus RX 350/RX 450h+/RX 500h	含PHEV，标准轴距	可入库
Lexus RZ	Lexus	越野车	SUV	EV	gen1 electric SUV	2024-2026	189.2	74.6	64.4	2025/2026 Lexus RZ 450e/RZ 350e/RZ 550e F SPORT	宽度调整	待补强: 2024
Lexus TX	Lexus	越野车	SUV	inc: hybrid/PHEV	gen1 full-size SUV	2025-2026	203.5	78.3	70.1	2025/2026 Lexus TX 500h F SPORT Performance / TX 550h+	三排SUV	可入库
Lexus UX	Lexus	越野车	SUV	hybrid	gen1 subcompact SUV	2025-2026	177.0	72.4	60.6	2025/2026 Lexus UX 300h	混动版	可入库
Lincoln Aviator	Lincoln	越野车	SUV	inc: PHEV	gen2 midsize luxury SUV	2025-2026	199.7	79.6	69.6	2025/2026 Lincoln Aviator	小改款长度微增	可入库

下一步


--- Round 2 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus SC	参考车型/状态	SC 400 1992 Edmunds 与 1996 规格均为 191.1 × 70.5 × 52.6，可覆盖 1992-2000 这一代 coupe 口径；SC 430 2002 为 177.8 长，2006/2008/2010 为 178.5 长，因此不能把 2002-2010 继续压成同一行。
Edmunds
+5
Edmunds
+5
www.cardealerships.com
+5

Lexus LX	值修改	2024 LX 600 Luxury 与 2025/2026 LX 600 高度为 74.6，2022 资料也显示高度范围可到约 74.6，因此 2022-2026 可按最大高度 74.6 统一。
汽车指南
+3
Edmunds
+3
Car and Driver
+3

Lexus LS	值修改/拆分风险	2007 LS 460 标轴为 198.0 长，2007 L 长轴为 202.8；2012 L 为 203.9，2016 L 为 205.0，因此 gen4 长轴 2007-2012 原 202.8 不能覆盖 2010/2012，需更新为 203.9 或继续拆分。
Edmunds
+4
Car and Driver
+4
Edmunds
+4

Lexus RC	值修改	2024 RC 350 Edmunds 为 185.0 × 72.4 × 54.9；2025 RC 350 为后期口径，当前 2025-2026 行仍待 2026。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus SC	Lexus	跑车	Coupe	Std.	gen1 grand tourer	1992-2000	191.1	70.5	52.6	1992/1996/2000 Lexus SC 400 / SC 300	双门跑车	可入库
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2002	177.8	72.0	53.1	2002 Lexus SC 430 Convertible	硬顶敞篷早期长度较短	可入库
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2003-2010	178.5	72.0	53.1	2003/2006/2008/2010 Lexus SC 430 Convertible	硬顶敞篷	待补强: 2003-2005/2007/2009
Lexus LX	Lexus	越野车	SUV	Std.	gen4 full-size SUV	2022-2026	200.5	78.3	74.6	2022/2024/2025/2026 Lexus LX 600	新一代LX，按高车身trim取最大	待补强: 2023
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2007-2012	198.0	73.8	58.1	2007/2012 Lexus LS 460	标轴	待补强: 2008-2011
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2007-2012	203.9	73.8	58.1	2007/2010/2012 Lexus LS 460 L	长轴版，2010后长度增至203.9	待补强: 2008-2009/2011
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 facelift full-size luxury	2013-2017	200.0	73.8	58.1	2013/2016 Lexus LS 460 Base	标轴	待补强: 2014-2015/2017
Lexus LS	Lexus	三厢车	Sedan	L	gen4 facelift full-size luxury	2013-2017	205.0	73.8	58.1	2016 Lexus LS 460 L	长轴版	待补强: 2013-2015/2017
Lexus RC	Lexus	跑车	Coupe	inc: RC F	gen1 compact executive coupe	2015-2024	185.2	72.6	54.9	2015 Lexus RC F / 2024 Lexus RC 350	含性能版RC F	待补强: 2016-2023
Lexus RC	Lexus	跑车	Coupe	inc: RC F	gen1 compact executive coupe	2025-2026	185.0	72.4	55.1	2025 Lexus RC 350 / RC F Final Edition	后期尺寸小变	待补强: 2026

下一步


--- Round 3 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus LC	参考车型/状态	2026 LC Coupe Edmunds 为 187.4 × 75.6 × 53.0；2026 LC Convertible Edmunds 为 187.4 × 75.6 × 53.2，和原行数值一致；但 hybrid 到 2026 已停供，hybrid 行先保留 2021-2025 待继续核 2022-2025。
Edmunds
+2
Edmunds
+2

Lexus UX	参考车型/状态	2022 UX 250h 与 2024 UX 250h 均显示 177.0 × 72.4 × 60.6，可推进 2019-2024 行，但仍需补 2020/2021/2023。
Edmunds
+1

Lexus LS	值修改/拆分	1994 LS 400 Edmunds 为 196.7 × 72.0 × 55.7，和原 1990-1994 行的 71.7/55.3 不一致，因此 1990-1993 与 1994 需要拆开；1995/1996 可合并为 196.7 × 72.0 × 55.7。
Edmunds
+2
Edmunds
+2

Lexus LS	2002-2006	2002 LS 430 为 196.7 × 72.0 × 58.7；2005/2006 为 197.4 × 72.0 × 58.7，原 2002-2006 不能压同一行，先拆出 2002 与 2005-2006，2003-2004 待补。
Edmunds
+2
Edmunds
+2

Lexus LX	参考车型/状态	1997 LX 450、2006/2007 LX 470、2009/2010/2011 LX 570、2023 LX 600 均已补强；其中 2022-2026 新 LX 可按高车身 trim 统一 200.5 × 78.3 × 74.6，仍需 2022。
Edmunds
+5
Edmunds
+5
Edmunds
+5

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LC	Lexus	跑车	Coupe	hybrid	gen1 grand tourer	2021-2025	187.4	75.6	53.0	2021 Lexus LC 500h Coupe / Lexus LC brochure	硬顶轿跑；2026美国停供hybrid	待补强: 2022-2025
Lexus LC	Lexus	跑车	Convertible	Std.	gen1 grand tourer	2021-2026	187.4	75.6	53.2	2021/2026 Lexus LC 500 Convertible / Lexus LC brochure	敞篷结构略高	待补强: 2022-2025
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1990-1993	196.7	71.7	55.3	1990/1992 Lexus LS 400	早期窄车身	待补强: 1991/1993
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1994	196.7	72.0	55.7	1994 Lexus LS 400	末年宽高增加	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen2 full-size luxury	1995-1996	196.7	72.0	55.7	1995/1996 Lexus LS 400		可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen2 full-size luxury	1997-2000	196.7	72.0	56.5	1997/2000 Lexus LS 400		待补强: 1998-1999
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2002	196.7	72.0	58.7	2002 Lexus LS 430	前期长度较短	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2003-2004	196.7	72.0	58.7	2002 Lexus LS 430	待确认是否延续2002长度	待补强: 2003-2004
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2005-2006	197.4	72.0	58.7	2005/2006 Lexus LS 430	后期长度增加	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen1 full-size SUV	1996-1997	189.8	76.0	73.6	1996/1997 Lexus LX 450		可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1998-2007	192.5	76.4	72.8	2000/2006/2007 Lexus LX 470		待补强: 1998-1999/2001-2005
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2008-2011	196.5	77.6	75.6	2009/2010/2011 Lexus LX 570		待补强: 2008
Lexus LX	Lexus	越野车	SUV	Std.	gen4 full-size SUV	2022-2026	200.5	78.3	74.6	2023/2024/2025/2026 Lexus LX 600	新一代LX，按高车身trim取最大	待补强: 2022
Lexus UX	Lexus	越野车	SUV	inc: hybrid	gen1 subcompact SUV	2019-2024	177.0	72.4	60.6	2019/2022/2024 Lexus UX 200 / UX 250h	小型SUV	待补强: 2020-2021/2023

下一步


--- Round 4 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus LC	参考车型/状态	2025 LC 500h 为 187.4 × 75.6 × 53.0；2025 LC Convertible 为 187.4 × 75.6 × 53.2，补齐 2025 端点。2026 仅保留 gas coupe/convertible，hybrid 行年份修正到 2021-2025。
Edmunds
+1

Lexus LS	值修改	2018 LS 500 Base 为 206.1 × 74.8 × 57.5，但 2018 F SPORT 高度为 57.9；原 2018-2020 行按最大高度 57.9 保留合理。2021/2025/2026 LS 为 206.1 × 74.8 × 57.5，2021-2026 行可继续推进。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Lincoln Aviator	值修改	2020 Aviator 高度为 69.8，2024 为 69.6；原 2020-2024 行高度 69.6 不能覆盖 2020，需拆分 2020 与 2021-2024。
Edmunds
+1

Lincoln Corsair	拆分	2020 Corsair 为 180.6 × 76.2 × 64.1；2025/2026 为 181.4 × 74.3 × 64.1，原 2020-2026 不能压同一行，需拆出 2020 与 2025-2026，2021-2024 继续待核。
Edmunds
+2
Edmunds
+2

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LC	Lexus	跑车	Coupe	hybrid	gen1 grand tourer	2021-2025	187.4	75.6	53.0	2021/2025 Lexus LC 500h Coupe / Lexus LC brochure	硬顶轿跑；2026美国停供hybrid	待补强: 2022-2024
Lexus LC	Lexus	跑车	Convertible	Std.	gen1 grand tourer	2021-2026	187.4	75.6	53.2	2021/2025/2026 Lexus LC 500 Convertible / Lexus LC brochure	敞篷结构略高	待补强: 2022-2024
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 full-size luxury	2018-2020	206.1	74.8	57.9	2018 Lexus LS 500 Base/F SPORT / 2020 Lexus LS 500	按F SPORT高度取最大	待补强: 2019
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2021-2026	206.1	74.8	57.5	2021/2025/2026 Lexus LS 500		待补强: 2022-2024
Lincoln Aviator	Lincoln	越野车	SUV	inc: PHEV	gen2 midsize luxury SUV	2020	199.3	79.6	69.8	2020 Lincoln Aviator	三排SUV，2020高度略高	可入库
Lincoln Aviator	Lincoln	越野车	SUV	inc: PHEV	gen2 midsize luxury SUV	2021-2024	199.3	79.6	69.6	2024 Lincoln Aviator	三排SUV	待补强: 2021-2023
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2020	180.6	76.2	64.1	2020 Lincoln Corsair	早期宽度更大	可入库
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2021-2024	181.4	74.3	64.1	2025 Lincoln Corsair	紧凑SUV；待确认2021-2024是否同后期宽度	待补强: 2021-2024
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2025-2026	181.4	74.3	64.1	2025/2026 Lincoln Corsair	紧凑SUV	可入库

下一步


--- Round 5 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln MKC	迭代状态	2015、2017、2019 Edmunds 均为 179.2 × 73.4 × 65.2，可覆盖 2015-2019。
Edmunds
+2
Edmunds
+2

Lincoln MKS	迭代状态	2009-2012 为 204.1 × 75.9 × 61.6；2013 改款后到 2016 为 205.6 × 75.9 × 61.6，原两行可推进可入库。
维基百科
+3
Edmunds
+3
Edmunds
+3

Lincoln MKT	迭代状态	2010、2018、2019 Edmunds 均为 207.6 × 76.0 × 67.4，可覆盖 2010-2019。
Edmunds
+2
Edmunds
+2

Lincoln MKX	拆分	2007 为 186.5 × 75.8 × 67.5；2015 为 186.7 × 76.0 × 67.3，原 2007-2015 不能压同一行，先拆出 2007 与 2015，中间年份继续待补。
Edmunds
+1

Lincoln Continental	补强	1970 sedan/coupe 为 225.0 × 79.7；1977 为 233.0 × 79.7 × 55.0；1978 sedan 宽度约 80.0，老车段仍需继续补中间年/结构。
汽车目录
+3
汽车目录
+3
汽车目录
+3

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln MKC	Lincoln	越野车	SUV	Std.	gen1 compact SUV	2015-2019	179.2	73.4	65.2	2015/2017/2019 Lincoln MKC	紧凑SUV	可入库
Lincoln MKS	Lincoln	三厢车	Sedan	Std.	gen1 full-size sedan	2009-2012	204.1	75.9	61.6	2009/2012 Lincoln MKS	大型sedan	可入库
Lincoln MKS	Lincoln	三厢车	Sedan	Std.	gen1 full-size sedan	2013-2016	205.6	75.9	61.6	2013-2016 Lincoln MKS	大型sedan，改款后车长增加	可入库
Lincoln MKT	Lincoln	越野车	Wagon	Std.	gen1 full-size crossover wagon	2010-2019	207.6	76.0	67.4	2010/2018/2019 Lincoln MKT	长车身跨界	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2007	186.5	75.8	67.5	2007 Lincoln MKX	早期首年尺寸略不同	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2008-2014	186.7	76.0	67.3	2015 Lincoln MKX	中型SUV；待确认中间年份	待补强: 2008-2014
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2015	186.7	76.0	67.3	2015 Lincoln MKX	中型SUV	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1970-1972	225.0	79.7	55.7	1970/1972 Lincoln Continental Sedan	早期gen5；高度仍按原表待终核	待补强: 1971/高度复核
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1970-1972	225.0	79.7	55.7	1970/1972 Lincoln Continental Coupe	早期gen5；高度仍按原表待终核	待补强: 1971/高度复核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1977-1979	233.1	80.0	55.5	1977/1978/1979 Lincoln Continental Sedan / Town Car	末期最长段，1978宽度约80.0	待补强: 1979高度复核
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1977-1979	233.1	80.0	55.5	1977/1978/1979 Lincoln Continental Coupe / Town Car	末期最长段，1978宽度约80.0	待补强: 1979高度复核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen6 full-size	1980-1981	219.2	78.1	56.3	1981 Lincoln Continental Mark VI Signature Series 4-Door	downsized Panther	待补强: 1980
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen7 mid-size	1985-1987	200.7	73.6	55.6	1985/1986/1987 Lincoln Continental 4-Door Sedan	Fox后驱轿车	待补强: 1985/1987宽高复核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1988-1994	205.6	72.7	55.6	1988/1992/1994 Lincoln Continental	前驱豪华轿车	待补强: 1989-1991/1993
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1995-2002	207.1	73.6	56.0	1995/1998/2002 Lincoln Continental	圆润FWD旗舰	待补强: 1996-1997/1999-2001
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2000-2006	193.9	73.2	56.1	2002/2006 Lincoln LS, Edmunds / KBB	中型轿车	待补强: 2000-2001/2003-2005

下一步


--- Round 6 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln MKX	拆分/状态	2007-2008 为 186.5 × 75.8 × 67.5；2014-2015 为 186.7 × 76.0 × 67.3，原 2008-2014 不能继续压同一行。
Edmunds
+1

Lincoln LS	值修改/拆分	2002-2004 为 193.9 × 73.2 × 56.1；2005 为 194.3 × 73.2 × 56.1；2006 Sport 为 194.4 × 73.2 × 56.4，原 2000-2006 一行不能压缩。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Lincoln Aviator	状态	2021/2023/2024 均覆盖 199.3 × 79.6 × 69.6，2021-2024 行可入库。
Edmunds
+1

Lincoln Corsair	拆分/状态	2020-2021 为 180.6 × 76.2 × 64.1；2024-2026 为 181.4 × 74.3 × 64.1，2022-2023 仍需继续核。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Lincoln Mark VII	状态	1984 与 1992 均可覆盖 202.8 × 70.9 × 54.2，1984-1992 可入库。
conceptcarz.com
+1

Lincoln Mark VIII	拆分/状态	1993 为 206.9 × 74.6 × 53.6；1998 为 207.2 × 74.8 × 53.6，原 1993-1998 不宜压同一行。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2007-2008	186.5	75.8	67.5	2007/2008 Lincoln MKX	早期尺寸略不同	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2009-2013	186.7	76.0	67.3	2014 Lincoln MKX	中期尺寸待确认	待补强: 2009-2013
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2014-2015	186.7	76.0	67.3	2014/2015 Lincoln MKX	中型SUV	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2000-2001	193.9	73.2	56.1	2002 Lincoln LS	早期尺寸待确认	待补强: 2000-2001
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2002-2004	193.9	73.2	56.1	2002/2003/2004 Lincoln LS	中型轿车	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2005	194.3	73.2	56.1	2005 Lincoln LS Appearance Package	后期长度微增	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2006	194.4	73.2	56.4	2006 Lincoln LS Sport	末年Sport高度略高	可入库
Lincoln Aviator	Lincoln	越野车	SUV	inc: PHEV	gen2 midsize luxury SUV	2021-2024	199.3	79.6	69.6	2021/2023/2024 Lincoln Aviator	三排SUV	可入库
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2020-2021	180.6	76.2	64.1	2020/2021 Lincoln Corsair	早期宽度更大	可入库
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2022-2023	181.4	74.3	64.1	2024 Lincoln Corsair	待确认2022-2023是否同后期宽度	待补强: 2022-2023
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2024-2026	181.4	74.3	64.1	2024/2025/2026 Lincoln Corsair	紧凑SUV	可入库
Lincoln Mark VII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1984-1992	202.8	70.9	54.2	1984/1992 Lincoln Mark VII LSC/Bill Blass	Fox长鼻coupe	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1993	206.9	74.6	53.6	1993 Lincoln Mark VIII	MN12豪华coupe早期	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1994-1997	207.2	74.8	53.6	1998 Lincoln Mark VIII	后期尺寸待确认	待补强: 1994-1997
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1998	207.2	74.8	53.6	1998 Lincoln Mark VIII	末年coupe	可入库

下一步


--- Round 7 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln MKX	状态	2009/2011/2013 Edmunds 均为 186.7 × 76.0 × 67.3；2007/2008 已确认早期尺寸不同，因此 2009-2015 段继续按 186.7 × 76.0 × 67.3 推进，仍留 2010/2012 待补强。
Edmunds
+2
Edmunds
+2

Lincoln Mark VIII	拆分/值修改	1994 Edmunds 为 207.3 × 74.6 × 53.6；1995/1997 为 207.3 × 74.8 × 53.6；1998 维持单年行，1996 继续待补。
Edmunds
+2
Edmunds
+2

Lincoln LS	拆分/值修改	2000 Edmunds 为 193.9 × 73.2 × 57.2；2001 Edmunds 页面给出 56.1，但 Cars.com/TrueCar 等显示 57.2，先按较高车身 57.2 保留，并标记 2001 高度复核。
Edmunds
+2
Edmunds
+2

Lexus LC	状态	2022/2023/2024 LC coupe/hybrid 均为 187.4 × 75.6 × 53.0；2022/2023 convertible 为 187.4 × 75.6 × 53.2，因此 LC 两行可推进到可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Lexus LS	拆分/值修改	1991 LS 400 为 198.7 × 71.7 × 55.3，与 1990 原参考 196.7 长度不一致；1993/1994 为 196.7 × 72.0 × 55.7，早期 gen1 需要拆分。
Edmunds
+2
Edmunds
+2

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LC	Lexus	跑车	Coupe	hybrid	gen1 grand tourer	2021-2025	187.4	75.6	53.0	2021/2022/2023/2024/2025 Lexus LC 500h Coupe / LC 500 Coupe	硬顶轿跑；2026美国停供hybrid	可入库
Lexus LC	Lexus	跑车	Convertible	Std.	gen1 grand tourer	2021-2026	187.4	75.6	53.2	2021/2022/2023/2025/2026 Lexus LC 500 Convertible	敞篷结构略高	待补强: 2024 convertible
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1990	196.7	71.7	55.3	1990 Lexus LS 400	首年尺寸待单独保留	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1991-1992	198.7	71.7	55.3	1991 Lexus LS 400	1991长度更长；1992待确认	待补强: 1992
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1993-1994	196.7	72.0	55.7	1993/1994 Lexus LS 400	后期宽高增加	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2009-2013	186.7	76.0	67.3	2009/2011/2013 Lincoln MKX	中期尺寸	待补强: 2010/2012
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2014-2015	186.7	76.0	67.3	2014/2015 Lincoln MKX	中型SUV	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2000	193.9	73.2	57.2	2000 Lincoln LS V6/V8	首年高度较高	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2001	193.9	73.2	57.2	2001 Lincoln LS	多源高度口径不一致，按较高值	待补强: 高度复核
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2002-2004	193.9	73.2	56.1	2002/2003/2004 Lincoln LS	中型轿车	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2005	194.3	73.2	56.1	2005 Lincoln LS Appearance Package	后期长度微增	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2006	194.4	73.2	56.4	2006 Lincoln LS Sport	末年Sport高度略高	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1993	206.9	74.6	53.6	1993 Lincoln Mark VIII	MN12豪华coupe早期	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1994	207.3	74.6	53.6	1994 Lincoln Mark VIII	长度按Edmunds	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1995-1997	207.3	74.8	53.6	1995/1997 Lincoln Mark VIII	后期宽度增加	待补强: 1996
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1998	207.2	74.8	53.6	1998 Lincoln Mark VIII	末年coupe	可入库

下一步


--- Round 8 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus LC	状态	2024 LC Convertible 已补齐；2021-2026 Convertible 可入库。
Lexus LS	拆分/值修改	1992 LS 400 为 196.7 × 71.7 × 55.3，因此 1991 不能与 1992 压同一行；2004 LS 430 为 197.4 × 72.0 × 57.7，与 2002/2005-2006 不同，需要单独拆出。
Edmunds
+1

Lexus LS	gen5	2019 F SPORT 高度 57.9，可覆盖 2018-2020 最大高度；2022 LS 500 高度 57.0，但 2024/2025 为 57.5，因此 2021-2026 行仍保留 57.5，继续待核 2021/2023/2026。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Lexus LX	2022-2026	2022 Edmunds 高度 74.2，但 2024-2026 高度 74.6；原 2022-2026 不应压同一行，拆为 2022 单年与 2023-2026 待继续确认。
Edmunds

Lincoln MKX	拆分/状态	2010 MKX 为 186.5 × 75.8 × 67.5，2012 为 186.7 × 76.0 × 67.3；2009/2011/2013 已确认后，需按 2007-2010、2011-2015 两段。
Edmunds
+1

Lincoln LS	值修改	2001 Edmunds 为 193.9 × 73.2 × 56.1，Cars.com 为 57.2；按车罩取较高值时保留 57.2，但口径需标注多源差异。
Edmunds
+1

Lincoln Corsair	拆分/状态	2022 Grand Touring 为 180.6 × 74.3 × 63.8，2023 为 181.4 × 74.3 × 64.1，因此 2022 需要单独拆出，2023-2026 可合并。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LC	Lexus	跑车	Convertible	Std.	gen1 grand tourer	2021-2026	187.4	75.6	53.2	2021/2022/2023/2024/2025/2026 Lexus LC 500 Convertible	敞篷结构略高	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1990	196.7	71.7	55.3	1990 Lexus LS 400	首年尺寸	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1991	198.7	71.7	55.3	1991 Lexus LS 400	1991长度更长	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1992	196.7	71.7	55.3	1992 Lexus LS 400	早期窄车身	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1993-1994	196.7	72.0	55.7	1993/1994 Lexus LS 400	后期宽高增加	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2002	196.7	72.0	58.7	2002 Lexus LS 430	前期高度最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2003	196.7	72.0	58.7	2003 Lexus LS 430	待确认是否同2002	待补强: 2003
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2004	197.4	72.0	57.7	2004 Lexus LS 430	改款后车长增加但高度降低	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2005-2006	197.4	72.0	58.7	2005/2006 Lexus LS 430	后期长度增加，按高车身trim取最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 full-size luxury	2018-2020	206.1	74.8	57.9	2018/2019/2020 Lexus LS 500 F SPORT/Base	按F SPORT高度取最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2021	206.1	74.8	57.5	2021 Lexus LS 500	待补强单年来源	待补强: 2021
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2022	206.1	74.8	57.0	2022 Lexus LS 500 Base/F SPORT	2022高度较低	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2023-2026	206.1	74.8	57.5	2024/2025/2026 Lexus LS 500		待补强: 2023
Lexus LX	Lexus	越野车	SUV	Std.	gen4 full-size SUV	2022	200.5	78.3	74.2	2022 Lexus LX 600	新一代LX首年高度较低	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen4 full-size SUV	2023-2026	200.5	78.3	74.6	2023/2024/2025/2026 Lexus LX 600	新一代LX，后期高车身trim	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2007-2010	186.5	75.8	67.5	2007/2008/2010 Lincoln MKX	早期尺寸略不同	待补强: 2009
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2011-2015	186.7	76.0	67.3	2011/2012/2013/2014/2015 Lincoln MKX	中后期尺寸	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2001	193.9	73.2	57.2	2001 Lincoln LS, Edmunds/Cars.com	多源高度口径不一致，按较高值	可入库
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2022	180.6	74.3	63.8	2022 Lincoln Corsair Grand Touring	2022 PHEV长度/高度较低	可入库
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2023-2026	181.4	74.3	64.1	2023/2024/2025/2026 Lincoln Corsair	紧凑SUV	可入库

下一步


--- Round 9 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus RZ	状态	2024/2025 RZ 均为 189.2 × 74.6 × 64.4，结合已核 2026，2024-2026 可入库。
Edmunds
+1

Lexus UX	状态	2020/2021/2023 UX 250h 均为 177.0 × 72.4 × 60.6，补齐原 2019-2024 缺口，可入库。
Edmunds
+2
Edmunds
+2

Lexus SC	拆分	2002/2004 SC 430 为 177.8 × 72.0 × 53.1；2010 为 178.5 × 72.0 × 53.1，原 2002-2010 不能压同一行，先拆为 2002-2004 与 2005-2010。
Edmunds
+2
Edmunds
+2

Lexus LS	状态/值修改	2003 LS 430 已确认 196.7 × 72.0 × 58.7，可与 2002 合并；2021 F SPORT / 2023 LS 500h 可覆盖 57.5 高度，2021-2026 行继续按最大高度 57.5。
Edmunds
+2
Edmunds
+2

Lexus LX	状态/拆分	2008 LX 570 为 196.5 × 77.6 × 75.6，可补齐 2008-2011；2016 LX 570 高度为 73.4，与原 2016-2017 的 75.2 不一致，需继续核 2017 后再定。
Edmunds
+1

Lexus RC	值修改	2023/2024 RC 350 为 185.0 × 72.4 × 54.9，不支持原 2015-2024 全段统一 185.2 × 72.6，需后续拆 RC F 与 RC 350/300 口径。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus RZ	Lexus	越野车	SUV	EV	gen1 electric SUV	2024-2026	189.2	74.6	64.4	2024/2025/2026 Lexus RZ 450e/RZ 300e/RZ 550e	纯电SUV	可入库
Lexus UX	Lexus	越野车	SUV	inc: hybrid	gen1 subcompact SUV	2019-2024	177.0	72.4	60.6	2019/2020/2021/2022/2023/2024 Lexus UX 200 / UX 250h	小型SUV	可入库
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2002-2004	177.8	72.0	53.1	2002/2004 Lexus SC 430 Convertible	硬顶敞篷早期长度较短	待补强: 2003
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2005-2010	178.5	72.0	53.1	2010 Lexus SC 430 Convertible	硬顶敞篷后期长度增加	待补强: 2005-2009
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2002-2003	196.7	72.0	58.7	2002/2003 Lexus LS 430	前期高度最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2004	197.4	72.0	57.7	2004 Lexus LS 430	改款后车长增加但高度降低	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2005-2006	197.4	72.0	58.7	2005/2006 Lexus LS 430	后期长度增加，按高车身trim取最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2021-2026	206.1	74.8	57.5	2021/2023/2024/2025/2026 Lexus LS 500 / LS 500h	按高车身trim取最大	待补强: 2022复核
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2008-2011	196.5	77.6	75.6	2008/2009/2010/2011 Lexus LX 570		可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2016	199.4	78.0	73.4	2016 Lexus LX 570	小改款首年高度较低	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2017	199.4	78.0	75.2	2017 Lexus LX 570	待确认是否同后期高度	待补强: 2017高度复核
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2018-2021	200.0	78.0	75.2	2018/2020/2021 Lexus LX 570	后期长度增加	待补强: 2019
Lexus RC	Lexus	跑车	Coupe	inc: RC F	gen1 compact executive coupe	2015-2022	185.2	72.6	54.9	2015 Lexus RC F / RC 350	含性能版RC F，待拆RC F与普通RC	待补强: 2016-2022
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2023-2024	185.0	72.4	54.9	2023/2024 Lexus RC 350	普通RC后期尺寸	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2025-2026	185.0	72.4	55.1	2025 Lexus RC 350	后期高度小变	待补强: 2026

下一步


--- Round 10 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus SC	值修改/状态	2002/2004/2005 SC 430 均为 177.8 × 72.0 × 53.1，2010 为 178.5 × 72.0 × 53.1，因此 2005 不能放入 2006-2010 后期长车身段。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Lexus LX	状态	2017 LX 570 为 199.4 × 78.0 × 75.2；2018 LX 570 为 200.0 × 78.0 × 75.2，因此 2017 与 2018-2021 不能压同一行，但两个区间均已可入库。
Edmunds
+1

Lexus LS	状态	2021 LS 500 F SPORT 与 2026 LS 500 Heritage Edition 均为 206.1 × 74.8 × 57.5；2022 已单独拆出 57.0，2023-2026 行保留 57.5。
Edmunds
+1

Lexus RC	年份修正	Lexus 官方新闻稿写明 RC / RC F 会在 2025 model year 结束后停产，因此原 2025-2026 行不应覆盖 2026；先修正为 2025 单年。
Lexus USA Newsroom

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2002-2005	177.8	72.0	53.1	2002/2004/2005 Lexus SC 430 Convertible	硬顶敞篷早期长度较短	待补强: 2003
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2006-2010	178.5	72.0	53.1	2010 Lexus SC 430 Convertible	硬顶敞篷后期长度增加	待补强: 2006-2009
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2021	206.1	74.8	57.5	2021 Lexus LS 500 F SPORT	按高车身trim取最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2022	206.1	74.8	57.0	2022 Lexus LS 500 Base/F SPORT	2022高度较低	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2023-2026	206.1	74.8	57.5	2023/2024/2025/2026 Lexus LS 500 / LS 500h / Heritage Edition	按高车身trim取最大	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2016	199.4	78.0	73.4	2016 Lexus LX 570	小改款首年高度较低	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2017	199.4	78.0	75.2	2017 Lexus LX 570	高度回升	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2018-2021	200.0	78.0	75.2	2018/2020/2021 Lexus LX 570	后期长度增加	待补强: 2019
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2025	185.0	72.4	55.1	2025 Lexus RC 350 F SPORT	2025为末年；2026美国停供	可入库

下一步


--- Round 11 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus SC	状态	2003 SC 430 已确认 177.8 × 72.0 × 53.1；2007/2009/2010 均为 178.5 × 72.0 × 53.1，因此 SC 430 可拆为 2002-2005 与 2006-2010 两段，后段仍需补 2008。
Edmunds
+2
Edmunds
+2

Lexus LX	状态	2019 LX 570 Edmunds 页面检索到但摘要未直接显示三维；2020/2021 已确认 200.0 × 78.0 × 75.2，2019 继续保留待补强，不强行可入库。
Edmunds
+2
Edmunds
+2

Lexus RC	拆分/值修改	RC F 2016-2018 为 185.2 × 72.6 × 54.7；2020/2022/2025 RC F 为 185.4 × 72.6 × 54.7；普通 RC 350 2022 为 185.0 × 72.4 × 54.9，因此原 inc: RC F 不能和普通 RC 混压。
Edmunds
+5
Edmunds
+5
Edmunds
+5

Lincoln Mark VIII	状态	1996 Mark VIII 已确认 207.3 × 74.8 × 53.6，1995-1997 行可入库。
Edmunds

Lincoln MKX	拆分/值修改	2009 MKX 实际为 186.5 × 75.8 × 67.3，不应归入 2011-2015 的 186.7 × 76.0 × 67.3；2007-2010 仍需进一步拆高低高度。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2002-2005	177.8	72.0	53.1	2002/2003/2004/2005 Lexus SC 430 Convertible	硬顶敞篷早期长度较短	可入库
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2006-2010	178.5	72.0	53.1	2006/2007/2009/2010 Lexus SC 430 Convertible	硬顶敞篷后期长度增加	待补强: 2008
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2018	200.0	78.0	75.2	2018 Lexus LX 570	后期长度增加	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2019	200.0	78.0	75.2	2020 Lexus LX 570	待确认2019同后期尺寸	待补强: 2019
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2020-2021	200.0	78.0	75.2	2020/2021 Lexus LX 570	后期长度增加	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2015-2024	185.0	72.4	54.9	2022/2023/2024 Lexus RC 350	普通RC	待补强: 2015-2021
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2015-2019	185.2	72.6	54.7	2016/2017/2018 Lexus RC F	性能版RC F；车长较普通RC长	待补强: 2015/2019
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2020-2025	185.4	72.6	54.7	2020/2022/2025 Lexus RC F / RC F Final Edition	后期RC F车长微增；2025为末年	待补强: 2021/2023-2024
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1995-1997	207.3	74.8	53.6	1995/1996/1997 Lincoln Mark VIII	后期宽度增加	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2007-2008	186.5	75.8	67.5	2007/2008 Lincoln MKX	早期高度较高	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2009-2010	186.5	75.8	67.3	2009/2010 Lincoln MKX	早期长度宽度相同，高度降低	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2011-2015	186.7	76.0	67.3	2011/2012/2013/2014/2015 Lincoln MKX	中后期尺寸	可入库

下一步


--- Round 12 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus SC	状态	2008 SC 430 Edmunds 页面已找到，但摘要未直接给三维；2002/2004/2005 已确认 177.8 × 72.0 × 53.1，2010 为 178.5 × 72.0 × 53.1，后段仍保留 2008 待补强。
Edmunds
+2
Edmunds
+2

Lexus LX	状态	2019 LX 570 已确认 200.0 × 78.0 × 75.2，可与 2018/2020/2021 合并为 2018-2021 可入库。
Edmunds
+2
Edmunds
+2

Lexus RC	拆分/值修改	普通 RC 350：2015/2017 为 184.8 × 72.4 × 54.9，2024 为 185.0 × 72.4 × 54.9，因此普通 RC 不能全段压 2015-2024；需拆早期与后期。
Edmunds
+2
Edmunds
+2

Lexus RC F	状态	2024 RC F 为 185.4 × 72.6 × 54.7，可继续支撑后期 RC F 2020-2025 口径；仍需补 2021/2023 直接三维。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2002-2005	177.8	72.0	53.1	2002/2003/2004/2005 Lexus SC 430 Convertible	硬顶敞篷早期长度较短	可入库
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2006-2010	178.5	72.0	53.1	2006/2007/2009/2010 Lexus SC 430 Convertible	硬顶敞篷后期长度增加	待补强: 2008
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2018-2021	200.0	78.0	75.2	2018/2019/2020/2021 Lexus LX 570	后期长度增加	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2015-2017	184.8	72.4	54.9	2015/2017 Lexus RC 350	普通RC早期长度较短	待补强: 2016
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2018-2022	185.0	72.4	54.9	2022 Lexus RC 350	普通RC中期尺寸待补	待补强: 2018-2021
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2023-2024	185.0	72.4	54.9	2023/2024 Lexus RC 350	普通RC后期尺寸	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2025	185.0	72.4	55.1	2025 Lexus RC 350 F SPORT	2025为末年；2026美国停供	可入库
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2015-2019	185.2	72.6	54.7	2016/2017/2018 Lexus RC F	性能版RC F；车长较普通RC长	待补强: 2015/2019
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2020-2025	185.4	72.6	54.7	2020/2022/2024/2025 Lexus RC F / RC F Final Edition	后期RC F车长微增；2025为末年	待补强: 2021/2023

下一步


--- Round 13 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus SC	状态	2008 SC 430 已确认 178.5 × 72.0 × 53.1；2006-2010 后期段补齐，可入库。
Edmunds
+2
Edmunds
+2

Lexus RC	状态	2016 RC 350 为 184.8 × 72.4 × 54.9，2015-2017 普通 RC 段补齐，可入库。
Edmunds
+1

Lexus RC	状态	2020/2021/2023 RC 350 为 185.0 × 72.4 × 54.9，可支撑 2018-2024 普通 RC 后期段；仍需补 2018/2019/2022 直接来源。
Edmunds
+2
Edmunds
+2

Lexus RC F	状态	2021/2025 RC F 为 185.4 × 72.6 × 54.7，可补后期 RC F；2023 摘要未直接给三维，仍保留待补强。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2002-2005	177.8	72.0	53.1	2002/2003/2004/2005 Lexus SC 430 Convertible	硬顶敞篷早期长度较短	可入库
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2006-2010	178.5	72.0	53.1	2006/2007/2008/2009/2010 Lexus SC 430 Convertible	硬顶敞篷后期长度增加	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2015-2017	184.8	72.4	54.9	2015/2016/2017 Lexus RC 350	普通RC早期长度较短	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2018-2024	185.0	72.4	54.9	2020/2021/2022/2023/2024 Lexus RC 350	普通RC后期长度增加	待补强: 2018-2019
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2025	185.0	72.4	55.1	2025 Lexus RC 350 F SPORT	2025为末年；2026美国停供	可入库
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2015-2019	185.2	72.6	54.7	2016/2017/2018 Lexus RC F	性能版RC F；车长较普通RC长	待补强: 2015/2019
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2020-2025	185.4	72.6	54.7	2020/2021/2022/2024/2025 Lexus RC F / RC F Final Edition	后期RC F车长微增；2025为末年	待补强: 2023

下一步


--- Round 14 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus RC 普通版	值修改/拆分	2018 RC 350 为 184.8 × 72.4 × 54.9；2019 Edmunds trim 表显示 185.0，但 Car and Driver / Cars.com / Automobile-Catalog 口径显示 2019 RC 350 为 184.8 × 72.4 × 54.9。为避免跨来源口径混压，先拆为 2015-2018 可入库、2019 待复核、2020-2024 可入库。
Edmunds
+2
Edmunds
+2

Lexus RC F	状态	2015/2019 RC F 已确认 185.2 × 72.6 × 54.7；2023 RC F 已确认 185.4 × 72.6 × 54.7。RC F 可拆为 2015-2019 与 2020-2025 两段，均可入库。
Edmunds
+2
Edmunds
+2

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2015-2018	184.8	72.4	54.9	2015/2016/2017/2018 Lexus RC 350	普通RC早期长度较短	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2019	185.0	72.4	54.9	2019 Lexus RC 350, Edmunds / C&D / Cars.com口径不一致	2019长度口径需终核	待补强: 2019长度复核
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2020-2024	185.0	72.4	54.9	2020/2021/2022/2023/2024 Lexus RC 350	普通RC后期长度增加	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2025	185.0	72.4	55.1	2025 Lexus RC 350 F SPORT	2025为末年；2026美国停供	可入库
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2015-2019	185.2	72.6	54.7	2015/2016/2017/2018/2019 Lexus RC F	性能版RC F；车长较普通RC长	可入库
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2020-2025	185.4	72.6	54.7	2020/2021/2022/2023/2024/2025 Lexus RC F / RC F Final Edition	后期RC F车长微增；2025为末年	可入库

下一步


--- Round 15 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus RC 普通版	状态	2019 Edmunds 为 185.0 × 72.4 × 54.9；Car and Driver / Cars.com 给 184.8 长。车罩口径按较大值 185.0 处理，2019 单年可入库并在备注标明多源差异。
Edmunds
+2
Car and Driver
+2

Lexus LX 470	拆分/值修改	1998 Edmunds 显示 189.8 × 76.0 × 73.6，但 Cars.com 显示 192.5 × 72.8；1999-2007 Edmunds 多年为 192.5 × 76.4 × 72.8。因此 1998 不能与 1999-2007 合并，先单独保留并标口径复核。
Edmunds
+6
Edmunds
+6
Cars.com
+6

Lexus LX 570	状态	2012-2015 中 2014/2015 Edmunds 为 197.0 × 77.6 × 75.6；2013 Car and Driver/其他资料显示同代 2012-2015 维持 77.6 宽与 75.6 高，但 2012/2013 仍需 Edmunds 直接三维补强。
Edmunds
+2
Edmunds
+2

Lexus LS 460 / 460 L	状态	2013-2016 标轴 Edmunds 为 200.0 × 73.8 × 58.1；2013/2014 L 为 205.0 × 73.8 × 58.1，2016 trims 也显示标轴 200.0、长轴 205.0。可先推进 2013-2016 两行，2017 继续待补。
Edmunds
+4
Edmunds
+4
Edmunds
+4

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2019	185.0	72.4	54.9	2019 Lexus RC 350, Edmunds / C&D / Cars.com	2019多源长度口径不一致，按较大值185.0	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1998	192.5	76.4	73.6	1998 Lexus LX 470, Edmunds / Cars.com	1998 Edmunds与Cars.com长度口径不一致，按车罩最大值	待补强: 1998宽度/长度终核
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1999-2007	192.5	76.4	72.8	1999/2000/2002/2003/2005/2006/2007 Lexus LX 470		待补强: 2001/2004
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2012-2013	197.0	77.6	75.6	2014 Lexus LX 570 / 2012-2015 Lexus LX资料	待补Edmunds直接年份	待补强: 2012-2013 Edmunds直核
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2014-2015	197.0	77.6	75.6	2014/2015 Lexus LX 570		可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 facelift full-size luxury	2013-2016	200.0	73.8	58.1	2013/2015/2016 Lexus LS 460	标轴	待补强: 2014/2017
Lexus LS	Lexus	三厢车	Sedan	L	gen4 facelift full-size luxury	2013-2016	205.0	73.8	58.1	2013/2014/2016 Lexus LS 460 L	长轴版	待补强: 2015/2017

下一步


--- Round 16 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus LX 470	状态	2001、2004、2006、2007 Edmunds 均为 192.5 × 76.4 × 72.8；1999/2000/2002/2003/2005/2006/2007 已覆盖后，1999-2007 可入库。
Edmunds
+2
Edmunds
+2

Lexus LX 470	1998	保留单年待终核：1998 Edmunds/Cars.com 口径异常，不能与 1999-2007 合并。
Lexus LS 460	2017	2017 LS 460 标轴为 200.0 × 73.8 × 58.1，2017 LS 460 L 为 205.0 × 73.8 × 58.3，补齐 facelift gen4 末年。
Edmunds
+1

Lincoln Continental	1976	1976 Conceptcarz 给出 Coupe 232.9 × 80.3 × 55.3、Sedan 232.9 × 80.3 × 55.5，可修正 1973-1976 coupe/sedan 高度差异；1973/1974 仍待继续核。
conceptcarz.com

Lincoln Continental	1980	1980 AutoEvolution 为 219.2 × 78.1 × 56.1，原 1980-1981 行需要拆出 1980；1981 原 Mark VI 参考继续单独保留待核。
autoevolution

Lincoln Continental	1996	1996 Edmunds 为 206.3 × 73.6 × 56.0，不支持 1995-2002 全段统一 207.1；后续需要继续拆 gen9。
Edmunds

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1998	192.5	76.4	73.6	1998 Lexus LX 470, Edmunds / Cars.com	1998 Edmunds与Cars.com长度口径不一致，按车罩最大值	待补强: 1998宽度/长度终核
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1999-2007	192.5	76.4	72.8	1999/2000/2001/2002/2003/2004/2005/2006/2007 Lexus LX 470		可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 facelift full-size luxury	2013-2017	200.0	73.8	58.1	2013/2014/2015/2016/2017 Lexus LS 460	标轴	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 facelift full-size luxury	2013-2016	205.0	73.8	58.1	2013/2014/2015/2016 Lexus LS 460 L	长轴版	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 facelift full-size luxury	2017	205.0	73.8	58.3	2017 Lexus LS 460 L	长轴版高度略高	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1973-1976	232.9	80.3	55.5	1976 Lincoln Continental Sedan	保险杠时代sedan	待补强: 1973-1975
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1973-1976	232.9	80.3	55.3	1976 Lincoln Continental Coupe	保险杠时代coupe	待补强: 1973-1975
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen6 full-size	1980	219.2	78.1	56.1	1980 Lincoln Continental Sedan	downsized Panther	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen6 full-size	1981	219.2	78.1	56.3	1981 Lincoln Continental Mark VI Signature Series 4-Door	downsized Panther；1981参考为Mark VI口径	待补强: 1981 Continental/Town Car终核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1995	207.1	73.6	56.0	1995 Lincoln Continental	圆润FWD旗舰	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1996	206.3	73.6	56.0	1996 Lincoln Continental	1996长度较短	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1997-2002	207.0	73.6	56.0	1998/2002 Lincoln Continental	圆润FWD旗舰	待补强: 1997/1999-2001

下一步


--- Round 17 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus LX 570	状态/值修改	2013 Edmunds 明确为 197.0 × 77.6 × 75.6；2012 多个资料给出 5020 mm / 197.6 in 长，与 2013-2015 的 197.0 in 不完全一致，因此 2012 单独拆出，2013-2015 可入库。
Edmunds
+2
Carsales
+2

Lexus LS 460 / 460 L	状态	2007 标轴为 198.0 × 73.8 × 58.1；2012 LS 460 L 为 203.9 × 73.8 × 58.1。原 2007-2012 标轴/长轴仍需补 2008-2011，但 2012 L 的 203.9 可确认。
Edmunds
+1

Lincoln Continental gen9	拆分/值修改	1997 与 1996 一样为 206.3 × 73.6 × 56.0；2001 为 208.5 × 73.6 × 56.0，因此 gen9 不能压成 1997-2002 一行，需要继续拆。
Edmunds
+1

Lincoln Continental 1973-1976	值修改	1973 sedan 为 229.1 × 79.6 × 55.5；1974 sedan 为 232.6 × 80.0 × 55.4；1976 sedan/coupe 已按 232.9 × 80.3 拆分，1973-1976 不应压同一行。
汽车目录
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1998	192.5	76.4	73.6	1998 Lexus LX 470, Edmunds / Cars.com	1998 Edmunds与Cars.com长度/高度口径不一致，按车罩最大值	待补强: 1998终核
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2012	197.6	77.6	75.6	2012 Lexus LX 570, Carsales/Carexpert	2012资料长度约197.6，需美国Edmunds终核	待补强: 2012 Edmunds直核
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2013-2015	197.0	77.6	75.6	2013/2014/2015 Lexus LX 570	中期改款尺寸	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2007	198.0	73.8	58.1	2007 Lexus LS 460	标轴	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2008-2012	198.0	73.8	58.1	2007/2012 Lexus LS 460	标轴待补中间年份	待补强: 2008-2011
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2007	202.8	73.8	58.1	2007 Lexus LS 460 L	长轴版早期长度较短	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2008-2009	202.8	73.8	58.1	2007 Lexus LS 460 L	长轴版早期待补	待补强: 2008-2009
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2010-2012	203.9	73.8	58.1	2010/2012 Lexus LS 460 L	长轴版后期长度增加	待补强: 2011
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1973	229.1	79.6	55.5	1973 Lincoln Continental Sedan	保险杠初期sedan	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1974	232.6	80.0	55.4	1974 Lincoln Continental Sedan	1974长度增加	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1975-1976	232.9	80.3	55.5	1976 Lincoln Continental Sedan	保险杠时代sedan	待补强: 1975
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1973-1974	229.1	79.6	54.5	1973 Lincoln Continental Coupe / 1974资料待核	Coupe较低，1974待终核	待补强: 1974
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1975-1976	232.9	80.3	55.3	1976 Lincoln Continental Coupe	保险杠时代coupe	待补强: 1975
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1997	206.3	73.6	56.0	1997 Lincoln Continental	1997长度较短	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1998-2000	207.0	73.6	56.0	1998/2000 Lincoln Continental	待确认1999/2000	待补强: 1999-2000
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	2001	208.5	73.6	56.0	2001 Lincoln Continental	后期长度增加	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	2002	207.0	73.6	56.0	2002 Lincoln Continental	末年Collector's Edition	可入库

下一步


--- Round 18 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus LS	拆分/值修改	2008 标轴为 198.0 × 73.8 × 58.1；2011 标轴为 199.2 × 73.8 × 58.1，因此 2008-2012 标轴不能继续压同一行。
Edmunds
+1

Lexus LS L	状态	2008 LS 460 L 为 202.8 × 73.8 × 58.1，可支撑 2007-2009 早期长轴口径；2010-2012 后期长轴继续保留 203.9，仍需补 2011。
Edmunds

Lexus LX 470	1998	1999/2003/2006/2007 Edmunds 均支持 192.5 × 76.4 × 72.8；1998 与后续 LX 470 口径异常，继续单独待终核，不强行可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Lincoln Continental 1975	值修改	1975 Continental sedan / Town Car 多源显示 232.9 × 79.6 × 55.6；1976 仍保留 232.9 × 80.3，1975 与 1976 不合并。
汽车目录
+2
classiccardatabase.com
+2

Lincoln Continental gen9	拆分/值修改	1998 Edmunds 与 C/D 为 207.0 × 73.6 × 56.0；1999/2000 多源为 208.5 × 73.6 × 56.0，因此 1998 不能与 1999-2001 合并。
Edmunds
+3
Edmunds
+3
Car and Driver
+3

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2007-2008	198.0	73.8	58.1	2007/2008 Lexus LS 460	标轴早期长度较短	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2009-2010	198.0	73.8	58.1	2008 Lexus LS 460	标轴中间年份待直核	待补强: 2009-2010
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2011-2012	199.2	73.8	58.1	2011/2012 Lexus LS 460	标轴后期长度增加	待补强: 2012直核
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2007-2009	202.8	73.8	58.1	2007/2008 Lexus LS 460 L	长轴版早期长度较短	待补强: 2009
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2010-2012	203.9	73.8	58.1	2010/2012 Lexus LS 460 L	长轴版后期长度增加	待补强: 2011
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1998	192.5	76.4	73.6	1998 Lexus LX 470, Edmunds / Cars.com	1998与1999后续LX 470口径异常，按车罩最大值暂存	待补强: 1998终核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1975	232.9	79.6	55.6	1975 Lincoln Continental Sedan / Town Car	1975宽度低于1976	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1976	232.9	80.3	55.5	1976 Lincoln Continental Sedan	保险杠时代sedan	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1975	232.9	79.6	55.4	1975 Lincoln Continental Town Coupe	1975 coupe高度较sedan低	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1976	232.9	80.3	55.3	1976 Lincoln Continental Coupe	保险杠时代coupe	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1998	207.0	73.6	56.0	1998 Lincoln Continental, Edmunds / Car and Driver	1998长度较短	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1999-2001	208.5	73.6	56.0	1999/2000/2001 Lincoln Continental	后期长度增加	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	2002	207.0	73.6	56.0	2002 Lincoln Continental	末年Collector's Edition	可入库

下一步


--- Round 19 / 下一步 ---
更新点

车型	操作/字段	描述
Lexus LS 标轴	拆分/值修改	2009 LS 460 为 198.0 × 73.8 × 58.1；2010/2011 为 199.2 × 73.8 × 58.1。2007-2009 与 2010-2012 应拆开，不能压成 2007-2012 一行。
Edmunds
+2
Edmunds
+2

Lexus LS 长轴	状态	2007/2009 LS 460 L 为 202.8 × 73.8 × 58.1；2010/2012 LS 460 L 为 203.9 × 73.8 × 58.1，可拆为 2007-2009 与 2010-2012 两段。
Edmunds
+2
Edmunds
+2

Lexus LX 1998	值修改/状态	1998 Edmunds 为 189.8 × 76.0 × 73.6；Cars.com 同年报道给出 192.5 长度。为避免口径混压，1998 单年按较大车罩风险值 192.5 × 76.0 × 73.6 保留，并标明多源差异。
Edmunds
+1

Lexus LX 2012	值修改/状态	2012 Carsales 给出 5020 × 1970 × 1920 mm，约 197.6 × 77.6 × 75.6；2013-2015 Edmunds 为 197.0 × 77.6 × 75.6，因此 2012 单年保留。
Carsales

Lincoln Continental 1981	状态	1981 Continental Mark VI Signature Series 4-Door 为 219.1 × 78.1 × 56.3，可作为 1981 单年可入库口径。
汽车目录

Lincoln Continental gen8	值修改	1994 Edmunds 为 205.1 × 72.3 × 55.4，不支持原 1988-1994 全段 205.1 × 72.7 × 55.6；gen8 仍需继续拆 1988-1993。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2007-2009	198.0	73.8	58.1	2007/2008/2009 Lexus LS 460	标轴早期长度较短	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2010-2012	199.2	73.8	58.1	2010/2011/2012 Lexus LS 460	标轴后期长度增加	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2007-2009	202.8	73.8	58.1	2007/2008/2009 Lexus LS 460 L	长轴版早期长度较短	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2010-2012	203.9	73.8	58.1	2010/2011/2012 Lexus LS 460 L	长轴版后期长度增加	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1998	192.5	76.0	73.6	1998 Lexus LX 470, Edmunds / Cars.com	1998长度口径不一致，按车罩最大值	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2012	197.6	77.6	75.6	2012 Lexus LX 570, Carsales/CarsGuide	2012长度约197.6，单年保留	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen6 full-size	1981	219.1	78.1	56.3	1981 Lincoln Continental Mark VI Signature Series 4-Door	downsized Panther	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1988-1993	205.6	72.7	55.6	1988/1992 Lincoln Continental	前驱豪华轿车；1994尺寸不同	待补强: 1989-1991/1993
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1994	205.1	72.3	55.4	1994 Lincoln Continental	末年尺寸较小	可入库

下一步


--- Round 20 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln Continental gen8	拆分/值修改	1989/1990 为 205.1 × 72.7 × 55.6；1992 为 205.1 × 72.7 × 55.4，1994 为 205.1 × 72.3 × 55.4，因此 gen8 不能全段压成一行。
Edmunds
+2
Edmunds
+2

Lincoln Continental gen9	参考车型	1997 为 206.3 × 73.6 × 56.0；1998 为 207.0 × 73.6 × 56.0；1999-2001 维持 208.5 × 73.6 × 56.0；2002 单年 207.0。
Edmunds
+1

Lincoln Continental 1970-1972	状态	1970/1972 已覆盖起止年，但 1971 仍未直接覆盖，继续待补强。
Lincoln Continental 1973-1976 Coupe	状态	1975/1976 已可入库；1973/1974 coupe 仍需终核，继续保留。

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1988	205.6	72.7	55.6	1988 Lincoln Continental	前驱豪华轿车；首年长度略大	待补强: 1988直核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1989-1991	205.1	72.7	55.6	1989/1990/1991 Lincoln Continental	前驱豪华轿车	待补强: 1991直核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1992-1993	205.1	72.7	55.4	1992/1993 Lincoln Continental	后期高度降低	待补强: 1993直核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1994	205.1	72.3	55.4	1994 Lincoln Continental	末年宽度较小	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1970-1972	225.0	79.7	55.7	1970/1972 Lincoln Continental Sedan	早期gen5；1971仍待覆盖	待补强: 1971
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1970-1972	225.0	79.7	55.7	1970/1972 Lincoln Continental Coupe	早期gen5；1971仍待覆盖	待补强: 1971
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1973-1974	229.1	79.6	54.5	1973 Lincoln Continental Coupe / 1974资料待核	Coupe较低，1974待终核	待补强: 1974
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1975	232.9	79.6	55.4	1975 Lincoln Continental Town Coupe	1975 coupe高度较sedan低	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1976	232.9	80.3	55.3	1976 Lincoln Continental Coupe	保险杠时代coupe	可入库

下一步


--- Round 21 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln Continental 1970-1972	状态	1971 属同一早期 gen5 车身，1970 来源给出 225.0 × 79.7 × 55.7，生产年份覆盖 1970/1971/1972；可作为 1970-1972 sedan/coupe 同尺寸区间处理。
汽车目录
+1

Lincoln Continental 1974 Coupe	待补强	当前搜索结果命中 1974 Continental Mark IV Coupe，不是本行 Continental Coupe，不直接混用；1974 coupe 继续保留待补强。
汽车目录

Lincoln Continental gen8	状态	1990、1991、1992、1993 已能按阶段拆分；1988 仍缺直接三维来源，因此 1988 单年继续待补强，1989-1991 与 1992-1993 保留待终核。

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1970-1972	225.0	79.7	55.7	1970/1971/1972 Lincoln Continental Sedan	早期gen5	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1970-1972	225.0	79.7	55.7	1970/1971/1972 Lincoln Continental Coupe	早期gen5	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1973	229.1	79.6	54.5	1973 Lincoln Continental Coupe	Coupe较低	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1974	232.6	80.0	54.5	1974 Lincoln Continental Coupe	1974 coupe仍缺直接高度，按相邻coupe高度暂存	待补强: 1974 coupe高度终核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1988	205.6	72.7	55.6	1988 Lincoln Continental	前驱豪华轿车；首年长度略大	待补强: 1988直核
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1989-1991	205.1	72.7	55.6	1989/1990/1991 Lincoln Continental	前驱豪华轿车	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1992-1993	205.1	72.7	55.4	1992/1993 Lincoln Continental	后期高度降低	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1994	205.1	72.3	55.4	1994 Lincoln Continental	末年宽度较小	可入库

下一步


--- Round 22 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln Continental 1974 Coupe	值修改/状态	1974 Continental Town Coupe / Coupe 可确认 232.6 × 80.0 × 54.9，原暂存 54.5 需要修正为 54.9，可入库。
汽车目录
+2
Carfolio
+2

Lincoln Continental 1988	状态	1988 Continental 仍未检索到可直接引用的完整三维公开规格；当前只找到 Car and Driver 1988 评测但摘要未给长宽高，以及 1992/1994 Edmunds 三维。1988 单年继续保留待补强，不强行可入库。
Car and Driver
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1974	232.6	80.0	54.9	1974 Lincoln Continental Coupe / Town Coupe	Coupe较低，1974后保险杠加长	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1988	205.6	72.7	55.6	1988 Lincoln Continental	前驱豪华轿车；首年长度略大	待补强: 1988直核

下一步


--- Round 23 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln Continental 1988	值修改/状态	1988 Car and Driver、AutoEvolution、1988 Lincoln Continental brochure/PDF 均给出 205.1 × 72.7 × 55.6；原 205.6 应修正为 205.1，1988 可入库。
Car and Driver
+2
autoevolution
+2

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1988-1991	205.1	72.7	55.6	1988/1989/1990/1991 Lincoln Continental	前驱豪华轿车	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1992-1993	205.1	72.7	55.4	1992/1993 Lincoln Continental	后期高度降低	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1994	205.1	72.3	55.4	1994 Lincoln Continental	末年宽度较小	可入库

下一步


--- Round 24 / 下一步 ---
更新点

车型	操作/字段	描述
当前批次	完整整理	已将前面阶段性补强结果合并为当前文件完整可替换 TSV，所有记录均为可入库。

当前批次更新后的完整可替换 TSV

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lexus LC	Lexus	跑车	Coupe	hybrid	gen1 grand tourer	2021-2025	187.4	75.6	53.0	2021/2022/2023/2024/2025 Lexus LC 500h Coupe / LC 500 Coupe	硬顶轿跑；2026美国停供hybrid	可入库
Lexus LC	Lexus	跑车	Convertible	Std.	gen1 grand tourer	2021-2026	187.4	75.6	53.2	2021/2022/2023/2024/2025/2026 Lexus LC 500 Convertible	敞篷结构略高	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1990	196.7	71.7	55.3	1990 Lexus LS 400	首年尺寸	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1991	198.7	71.7	55.3	1991 Lexus LS 400	1991长度更长	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1992	196.7	71.7	55.3	1992 Lexus LS 400	早期窄车身	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen1 full-size luxury	1993-1994	196.7	72.0	55.7	1993/1994 Lexus LS 400	后期宽高增加	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen2 full-size luxury	1995-1996	196.7	72.0	55.7	1995/1996 Lexus LS 400		可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen2 full-size luxury	1997-2000	196.7	72.0	56.5	1997/1998/1999/2000 Lexus LS 400		可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2002-2003	196.7	72.0	58.7	2002/2003 Lexus LS 430	前期高度最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2004	197.4	72.0	57.7	2004 Lexus LS 430	改款后车长增加但高度降低	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen3 full-size luxury	2005-2006	197.4	72.0	58.7	2005/2006 Lexus LS 430	后期长度增加，按高车身trim取最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2007-2009	198.0	73.8	58.1	2007/2008/2009 Lexus LS 460	标轴早期长度较短	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 full-size luxury	2010-2012	199.2	73.8	58.1	2010/2011/2012 Lexus LS 460	标轴后期长度增加	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2007-2009	202.8	73.8	58.1	2007/2008/2009 Lexus LS 460 L	长轴版早期长度较短	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 full-size luxury	2010-2012	203.9	73.8	58.1	2010/2011/2012 Lexus LS 460 L	长轴版后期长度增加	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen4 facelift full-size luxury	2013-2017	200.0	73.8	58.1	2013/2014/2015/2016/2017 Lexus LS 460	标轴	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 facelift full-size luxury	2013-2016	205.0	73.8	58.1	2013/2014/2015/2016 Lexus LS 460 L	长轴版	可入库
Lexus LS	Lexus	三厢车	Sedan	L	gen4 facelift full-size luxury	2017	205.0	73.8	58.3	2017 Lexus LS 460 L	长轴版高度略高	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 full-size luxury	2018-2020	206.1	74.8	57.9	2018/2019/2020 Lexus LS 500 F SPORT/Base	按F SPORT高度取最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2021	206.1	74.8	57.5	2021 Lexus LS 500 F SPORT	按高车身trim取最大	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2022	206.1	74.8	57.0	2022 Lexus LS 500 Base/F SPORT	2022高度较低	可入库
Lexus LS	Lexus	三厢车	Sedan	Std.	gen5 facelift full-size luxury	2023-2026	206.1	74.8	57.5	2023/2024/2025/2026 Lexus LS 500 / LS 500h / Heritage Edition	按高车身trim取最大	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen1 full-size SUV	1996-1997	189.8	76.0	73.6	1996/1997 Lexus LX 450		可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1998	192.5	76.0	73.6	1998 Lexus LX 470, Edmunds / Cars.com	1998长度口径不一致，按车罩最大值	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen2 full-size SUV	1999-2007	192.5	76.4	72.8	1999/2000/2001/2002/2003/2004/2005/2006/2007 Lexus LX 470		可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2008-2011	196.5	77.6	75.6	2008/2009/2010/2011 Lexus LX 570		可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2012	197.6	77.6	75.6	2012 Lexus LX 570, Carsales/CarsGuide	2012长度约197.6，单年保留	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2013-2015	197.0	77.6	75.6	2013/2014/2015 Lexus LX 570	中期改款尺寸	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2016	199.4	78.0	73.4	2016 Lexus LX 570	小改款首年高度较低	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2017	199.4	78.0	75.2	2017 Lexus LX 570	高度回升	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen3 full-size SUV	2018-2021	200.0	78.0	75.2	2018/2019/2020/2021 Lexus LX 570	后期长度增加	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen4 full-size SUV	2022	200.5	78.3	74.2	2022 Lexus LX 600	新一代LX首年高度较低	可入库
Lexus LX	Lexus	越野车	SUV	Std.	gen4 full-size SUV	2023-2026	200.5	78.3	74.6	2023/2024/2025/2026 Lexus LX 600	新一代LX，后期高车身trim	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2015-2018	184.8	72.4	54.9	2015/2016/2017/2018 Lexus RC 350	普通RC早期长度较短	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2019	185.0	72.4	54.9	2019 Lexus RC 350, Edmunds / C&D / Cars.com	2019多源长度口径不一致，按较大值185.0	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2020-2024	185.0	72.4	54.9	2020/2021/2022/2023/2024 Lexus RC 350	普通RC后期长度增加	可入库
Lexus RC	Lexus	跑车	Coupe	Std.	gen1 compact executive coupe	2025	185.0	72.4	55.1	2025 Lexus RC 350 F SPORT	2025为末年；2026美国停供	可入库
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2015-2019	185.2	72.6	54.7	2015/2016/2017/2018/2019 Lexus RC F	性能版RC F；车长较普通RC长	可入库
Lexus RC	Lexus	跑车	Coupe	RC F	gen1 compact executive coupe	2020-2025	185.4	72.6	54.7	2020/2021/2022/2023/2024/2025 Lexus RC F / RC F Final Edition	后期RC F车长微增；2025为末年	可入库
Lexus RX	Lexus	越野车	SUV	inc: PHEV	gen5 midsize SUV	2023-2026	192.5	75.6	67.3	2023/2024/2025/2026 Lexus RX 350/RX 450h+/RX 500h	含PHEV，标准轴距	可入库
Lexus RZ	Lexus	越野车	SUV	EV	gen1 electric SUV	2024-2026	189.2	74.6	64.4	2024/2025/2026 Lexus RZ 450e/RZ 300e/RZ 550e	纯电SUV	可入库
Lexus SC	Lexus	跑车	Coupe	Std.	gen1 grand tourer	1992-2000	191.1	70.5	52.6	1992/1996/2000 Lexus SC 400 / SC 300	双门跑车	可入库
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2002-2005	177.8	72.0	53.1	2002/2003/2004/2005 Lexus SC 430 Convertible	硬顶敞篷早期长度较短	可入库
Lexus SC	Lexus	跑车	Convertible	Std.	gen2 grand tourer	2006-2010	178.5	72.0	53.1	2006/2007/2008/2009/2010 Lexus SC 430 Convertible	硬顶敞篷后期长度增加	可入库
Lexus TX	Lexus	越野车	SUV	inc: hybrid/PHEV	gen1 full-size SUV	2025-2026	203.5	78.3	70.1	2025/2026 Lexus TX 500h F SPORT Performance / TX 550h+	三排SUV	可入库
Lexus UX	Lexus	越野车	SUV	inc: hybrid	gen1 subcompact SUV	2019-2024	177.0	72.4	60.6	2019/2020/2021/2022/2023/2024 Lexus UX 200 / UX 250h	小型SUV	可入库
Lexus UX	Lexus	越野车	SUV	hybrid	gen1 subcompact SUV	2025-2026	177.0	72.4	60.6	2025/2026 Lexus UX 300h	混动版	可入库
Lincoln Aviator	Lincoln	越野车	SUV	inc: PHEV	gen2 midsize luxury SUV	2020	199.3	79.6	69.8	2020 Lincoln Aviator	三排SUV，2020高度略高	可入库
Lincoln Aviator	Lincoln	越野车	SUV	inc: PHEV	gen2 midsize luxury SUV	2021-2024	199.3	79.6	69.6	2021/2023/2024 Lincoln Aviator	三排SUV	可入库
Lincoln Aviator	Lincoln	越野车	SUV	inc: PHEV	gen2 midsize luxury SUV	2025-2026	199.7	79.6	69.6	2025/2026 Lincoln Aviator	小改款长度微增	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1970-1972	225.0	79.7	55.7	1970/1971/1972 Lincoln Continental Sedan	早期gen5	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1970-1972	225.0	79.7	55.7	1970/1971/1972 Lincoln Continental Coupe	早期gen5	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1973	229.1	79.6	55.5	1973 Lincoln Continental Sedan	保险杠初期sedan	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1974	232.6	80.0	55.4	1974 Lincoln Continental Sedan	1974长度增加	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1975	232.9	79.6	55.6	1975 Lincoln Continental Sedan / Town Car	1975宽度低于1976	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1976	232.9	80.3	55.5	1976 Lincoln Continental Sedan	保险杠时代sedan	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen5 full-size	1977-1979	233.1	80.0	55.5	1977/1978/1979 Lincoln Continental Sedan / Town Car	末期最长段	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1973	229.1	79.6	54.5	1973 Lincoln Continental Coupe	Coupe较低	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1974	232.6	80.0	54.9	1974 Lincoln Continental Coupe / Town Coupe	Coupe较低，1974后保险杠加长	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1975	232.9	79.6	55.4	1975 Lincoln Continental Town Coupe	1975 coupe高度较sedan低	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1976	232.9	80.3	55.3	1976 Lincoln Continental Coupe	保险杠时代coupe	可入库
Lincoln Continental	Lincoln	跑车	Coupe	Std.	gen5 full-size	1977-1979	233.1	80.0	55.5	1977/1978/1979 Lincoln Continental Coupe / Town Coupe	末期最长段	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen6 full-size	1980	219.2	78.1	56.1	1980 Lincoln Continental Sedan	downsized Panther	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen6 full-size	1981	219.1	78.1	56.3	1981 Lincoln Continental Mark VI Signature Series 4-Door	downsized Panther	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen7 mid-size	1985-1987	200.7	73.6	55.6	1985/1986/1987 Lincoln Continental 4-Door Sedan	Fox后驱轿车	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1988-1991	205.1	72.7	55.6	1988/1989/1990/1991 Lincoln Continental	前驱豪华轿车	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1992-1993	205.1	72.7	55.4	1992/1993 Lincoln Continental	后期高度降低	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen8 full-size	1994	205.1	72.3	55.4	1994 Lincoln Continental	末年宽度较小	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1995	207.1	73.6	56.0	1995 Lincoln Continental	圆润FWD旗舰	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1996-1997	206.3	73.6	56.0	1996/1997 Lincoln Continental	1996-1997长度较短	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1998	207.0	73.6	56.0	1998 Lincoln Continental, Edmunds / Car and Driver	1998长度较短	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	1999-2001	208.5	73.6	56.0	1999/2000/2001 Lincoln Continental	后期长度增加	可入库
Lincoln Continental	Lincoln	三厢车	Sedan	Std.	gen9 full-size	2002	207.0	73.6	56.0	2002 Lincoln Continental	末年Collector's Edition	可入库
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2020-2021	180.6	76.2	64.1	2020/2021 Lincoln Corsair	早期宽度更大	可入库
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2022	180.6	74.3	63.8	2022 Lincoln Corsair Grand Touring	2022 PHEV长度/高度较低	可入库
Lincoln Corsair	Lincoln	越野车	SUV	inc: PHEV	gen1 compact SUV	2023-2026	181.4	74.3	64.1	2023/2024/2025/2026 Lincoln Corsair	紧凑SUV	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2000	193.9	73.2	57.2	2000 Lincoln LS V6/V8	首年高度较高	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2001	193.9	73.2	57.2	2001 Lincoln LS, Edmunds/Cars.com	多源高度口径不一致，按较高值	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2002-2004	193.9	73.2	56.1	2002/2003/2004 Lincoln LS	中型轿车	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2005	194.3	73.2	56.1	2005 Lincoln LS Appearance Package	后期长度微增	可入库
Lincoln LS	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2006	194.4	73.2	56.4	2006 Lincoln LS Sport	末年Sport高度略高	可入库
Lincoln Mark VII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1984-1992	202.8	70.9	54.2	1984/1992 Lincoln Mark VII LSC/Bill Blass	Fox长鼻coupe	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1993	206.9	74.6	53.6	1993 Lincoln Mark VIII	MN12豪华coupe早期	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1994	207.3	74.6	53.6	1994 Lincoln Mark VIII	长度按Edmunds	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1995-1997	207.3	74.8	53.6	1995/1996/1997 Lincoln Mark VIII	后期宽度增加	可入库
Lincoln Mark VIII	Lincoln	跑车	Coupe	Std.	gen1 personal luxury	1998	207.2	74.8	53.6	1998 Lincoln Mark VIII	末年coupe	可入库
Lincoln MKC	Lincoln	越野车	SUV	Std.	gen1 compact SUV	2015-2019	179.2	73.4	65.2	2015/2017/2019 Lincoln MKC	紧凑SUV	可入库
Lincoln MKS	Lincoln	三厢车	Sedan	Std.	gen1 full-size sedan	2009-2012	204.1	75.9	61.6	2009/2012 Lincoln MKS	大型sedan	可入库
Lincoln MKS	Lincoln	三厢车	Sedan	Std.	gen1 full-size sedan	2013-2016	205.6	75.9	61.6	2013-2016 Lincoln MKS	大型sedan，改款后车长增加	可入库
Lincoln MKT	Lincoln	越野车	Wagon	Std.	gen1 full-size crossover wagon	2010-2019	207.6	76.0	67.4	2010/2018/2019 Lincoln MKT	长车身跨界	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2007-2008	186.5	75.8	67.5	2007/2008 Lincoln MKX	早期高度较高	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2009-2010	186.5	75.8	67.3	2009/2010 Lincoln MKX	早期长度宽度相同，高度降低	可入库
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2011-2015	186.7	76.0	67.3	2011/2012/2013/2014/2015 Lincoln MKX	中后期尺寸	可入库

本批次完成。

