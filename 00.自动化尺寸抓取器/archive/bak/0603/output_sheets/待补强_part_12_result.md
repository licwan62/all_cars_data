# 文件名：待补强_part_12.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作/字段	描述
Hyundai Elantra Tour	拆出	2009 与 2012 长度不同，原 2009-2012 不可直接压缩为同一尺寸区间
Hyundai Equus	参考车型	2011 与 2016 口径补齐，可覆盖 2011-2016
Hyundai IONIQ 5	参考车型	2022-2024、2025-2026 分段参考车型补齐
Hyundai IONIQ 6	参考车型	暂按 2023-2025 常规 IONIQ 6 补齐，2026 需单独终核是否仍适用常规版
Hyundai Kona	参考车型	gen1 / gen2 参考范围补齐
Hyundai Nexo	参考车型	2023-2024 补齐
Hyundai Palisade	参考车型	2020-2022、2023-2025 分段参考车型补齐

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Hyundai Elantra Tour	Hyundai	两厢车	Wagon	Std.	gen1 compact wagon	2009	176.2	69.5	59.8	2009 Hyundai Elantra Touring	旅行两厢	可入库
Hyundai Elantra Tour	Hyundai	两厢车	Wagon	Std.	gen1 compact wagon	2010-2011	176.6	69.5	59.8	2010-2011 Hyundai Elantra Touring	旅行两厢	待终核: 2010-2011长度需复核
Hyundai Elantra Tour	Hyundai	两厢车	Wagon	Std.	gen1 compact wagon	2012	176.6	69.5	59.8	2012 Hyundai Elantra Touring SE	旅行两厢	可入库
Hyundai Equus	Hyundai	三厢车	Sedan	Std.	gen2 full-size luxury sedan	2011-2016	203.1	74.4	58.7	2011-2016 Hyundai Equus Signature / Ultimate	大型豪华轿车	可入库
Hyundai IONIQ 5	Hyundai	越野车	SUV	EV	gen1 EV SUV	2022-2024	182.5	74.4	63.0	2022-2024 Hyundai IONIQ 5 SE / SEL / Limited	纯电SUV	可入库
Hyundai IONIQ 5	Hyundai	越野车	SUV	EV	gen1 EV SUV facelift	2025-2026	183.3	74.4	63.0	2025-2026 Hyundai IONIQ 5 SE / SEL / Limited	纯电SUV	可入库
Hyundai IONIQ 6	Hyundai	三厢车	Sedan	EV	gen1 EV sedan	2023-2025	191.1	74.0	58.9	2023-2025 Hyundai IONIQ 6 SE / SEL / Limited	电动流线轿车	可入库
Hyundai IONIQ 6	Hyundai	三厢车	Sedan	EV	gen1 EV sedan	2026	191.1	74.0	58.9	2026 Hyundai IONIQ 6	电动流线轿车	待终核: 2026美国常规版/性能版口径
Hyundai Kona	Hyundai	越野车	CUV	Std.	gen1 subcompact CUV	2018-2023	164.0	70.9	61.6	2018-2023 Hyundai Kona Limited / Ultimate		可入库
Hyundai Kona	Hyundai	越野车	CUV	Std.	gen2 subcompact CUV	2024-2026	171.3	71.9	62.6	2024-2026 Hyundai Kona Limited	换代加长	可入库
Hyundai Nexo	Hyundai	越野车	SUV	fuel-cell	gen1 fuel-cell SUV	2023-2024	183.9	73.2	64.6	2023-2024 Hyundai Nexo Limited	高度变化	可入库
Hyundai Palisade	Hyundai	越野车	SUV	Std.	gen1 midsize SUV	2020-2022	196.1	77.8	68.9	2020-2022 Hyundai Palisade Limited / SEL	三排SUV	可入库
Hyundai Palisade	Hyundai	越野车	SUV	Std.	gen1 midsize SUV facelift	2023-2025	196.7	77.8	68.9	2023-2025 Hyundai Palisade XRT / Limited / Calligraphy	三排SUV	可入库

下一步


--- Round 2 / 下一步 ---
更新点

车型	操作/字段	描述
Hyundai Tucson	值修改	gen4 2022-2024 原高度 65.6 偏低，Tucson 2024 Edmunds 为 66.3；2025 Hybrid 为 66.3，本轮改为 66.3
Hyundai Tucson	参考车型	gen1/gen2/gen3/gen4 补充覆盖区间参考；2016-2021 暂保留待终核，因为本轮只核到 2016/2021 关键点
Hyundai Veloster	值修改	2015-2017 Turbo 高度应取 55.3，原 55.1 偏低；2017 Turbo R-Spec Edmunds 为 167.3/71.1/55.3
Hyundai Veloster	参考车型	2012-2014、2015-2017、2021-2022 参考车型补齐
Hyundai Venue	参考车型	2020-2026 补齐；本轮核到 2026 Edmunds 为 159.1/69.7/61.6
Hyundai Veracruz / XG	参考车型	暂按区间补齐参考，仍需终核中间年份页面
Ineos Grenadier	结构处理	SUV 与 Quartermaster 分开保留；2024 与 2025-2026 分段继续保留，避免 SUV/Pickup 混用

本轮 Tucson 主要核到 Edmunds 2009、2010/2015、2024/2025 Tucson；Veloster 核到 Edmunds 2012/2014、2015/2017 Turbo、2021/2022 N；Venue 核到 2026 Edmunds。
Edmunds
+11
Edmunds
+11
Edmunds
+11

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Hyundai Tucson	Hyundai	越野车	SUV	Std.	gen1 compact SUV	2005-2009	170.3	72.1	68.1	2005-2009 Hyundai Tucson LX / Limited	紧凑SUV	可入库
Hyundai Tucson	Hyundai	越野车	SUV	Std.	gen2 compact SUV	2010-2015	173.2	71.7	66.3	2010-2015 Hyundai Tucson Limited	紧凑SUV	可入库
Hyundai Tucson	Hyundai	越野车	SUV	Std.	gen3 compact SUV	2016-2021	176.4	72.8	65.0	2016/2021 Hyundai Tucson Ultimate / Limited	紧凑SUV	待终核: 2017-2020
Hyundai Tucson	Hyundai	越野车	SUV	inc: hybrid/PHEV	gen4 compact SUV	2022-2024	182.3	73.4	66.3	2022-2024 Hyundai Tucson / Tucson Hybrid / Tucson PHEV	含混动/PHEV	可入库
Hyundai Veloster	Hyundai	两厢车	Hatchback	Std.	gen1 3-door hatchback	2012-2014	166.1	70.5	55.1	2012-2014 Hyundai Veloster Base	三门coupe-like hatch	可入库
Hyundai Veloster	Hyundai	两厢车	Hatchback	Turbo	gen1 3-door hatchback	2015-2017	167.3	71.1	55.3	2015-2017 Hyundai Veloster Turbo / Turbo R-Spec	Turbo更长更宽	可入库
Hyundai Veloster	Hyundai	两厢车	Hatchback	N	gen2 3-door hatchback	2021-2022	167.9	71.3	54.9	2021-2022 Hyundai Veloster N	N后期高度小差异	可入库
Hyundai Venue	Hyundai	越野车	SUV	Std.	gen1 subcompact SUV	2020-2026	159.1	69.7	61.6	2020-2026 Hyundai Venue SE / SEL / Limited	小型SUV	可入库
Hyundai Veracruz	Hyundai	越野车	SUV	Std.	gen1 midsize SUV	2007-2012	190.6	76.6	71.1	2007-2012 Hyundai Veracruz Limited	三排SUV	待终核: 2007-2011
Hyundai XG	Hyundai	三厢车	Sedan	Std.	gen1 full-size sedan	2001-2005	191.9	71.9	55.9	2001-2005 Hyundai XG300 / XG350	大型轿车	待终核: 2001-2004
Ineos Automotive Grenadier	Ineos Automotive	越野车	SUV	Std.	gen1 off-road SUV	2024	191.2	76.0	80.7	2024 Ineos Grenadier SUV	高车身硬派SUV	待终核: 2024美国版配置口径
Ineos Automotive Grenadier	Ineos Automotive	越野车	SUV	Std.	gen1 off-road SUV	2025-2026	191.2	76.0	80.7	2025-2026 Ineos Grenadier SUV	高车身硬派SUV	待终核: 2025-2026
Ineos Automotive Grenadier	Ineos Automotive	越野车	Pickup	Quartermaster	gen1 off-road pickup	2024	212.6	76.5	79.4	2024 Ineos Grenadier Quartermaster	长车身皮卡	待终核: 2024美国版配置口径
Ineos Automotive Grenadier	Ineos Automotive	越野车	Pickup	Quartermaster	gen1 off-road pickup	2025-2026	212.6	76.5	79.5	2025-2026 Ineos Grenadier Quartermaster	长车身皮卡	待终核: 2025-2026

下一步


--- Round 3 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti EX	参考车型	2012 EX35 Edmunds 为 182.3 / 71.0 / 61.9，原高度 62.6 需保留待终核，不直接可入库
Infiniti FX gen1	值修改	2008 FX35 Edmunds 高度为 65.9，高于原 65.0；2004 为 65.0，2007/2008 为 65.9，因此原 2003-2008 不宜一行压缩
Infiniti FX gen2	值修改	2013 FX Edmunds 为 191.3 / 75.9 / 65.0，原高度 66.1 需回调为 65.0
Infiniti G Sedan	拆出	2003 G35 sedan 为 186.5 / 69.0 / 57.7，2013 G Sedan 为 187.9 / 69.8 / 57.8，原 2003-2013 不能一行压缩
Infiniti G Coupe	拆出/值修改	2003 G35 coupe 为 182.2 / 71.5 / 54.8，2013 G Coupe 为 183.1 / 71.8 / 54.8；原 coupe 行用了 convertible 最大值，需分开
Infiniti G Convertible	年份修正	G Convertible 不应覆盖 2003-2013；美国 G Convertible 主要从 2009 起，2013 Edmunds 为 183.3 / 72.9 / 55.0
Infiniti I	参考车型	2003/2004 I35 Edmunds 均为 193.7 / 70.2 / 57.0，1996-2001 I30 仍待核

本轮主要依据 Edmunds：EX 2012、FX 2004/2007/2008/2012/2013、G 2003 sedan/coupe、G 2013 sedan/coupe/convertible、I35 2003/2004 等页面；其中 G Coupe 与 Sedan 的 2003 差异也由 Infiniti 官方新闻稿佐证。
Edmunds
+13
Edmunds
+13
Edmunds
+13

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2008-2013	182.3	71.0	62.6	2008/2012/2013 Infiniti EX35 / EX37	紧凑跨界SUV	待终核: 高度62.6来源需复核，Edmunds 2012为61.9
Infiniti FX	Infiniti	越野车	CUV	Std.	gen1 crossover SUV	2003-2004	189.1	75.8	65.0	2003-2004 Infiniti FX35		待终核: 2003
Infiniti FX	Infiniti	越野车	CUV	Std.	gen1 crossover SUV	2005-2008	189.1	75.8	65.9	2005-2008 Infiniti FX35		待终核: 2005-2006
Infiniti FX	Infiniti	越野车	CUV	Std.	gen2 crossover SUV	2009-2013	191.3	75.9	65.0	2009-2013 Infiniti FX35 / FX37 / FX50		待终核: 2009-2011
Infiniti G	Infiniti	三厢车	Sedan	Std.	gen3 sport sedan	2003	186.5	69.0	57.7	2003 Infiniti G35 Sedan		可入库
Infiniti G	Infiniti	三厢车	Sedan	Std.	gen3 sport sedan	2004-2006	186.5	69.0	57.7	2004-2006 Infiniti G35 Sedan		待终核: 2004-2006
Infiniti G	Infiniti	三厢车	Sedan	Std.	gen3 sport sedan	2007-2013	187.9	69.8	57.8	2007-2013 Infiniti G35 / G37 Sedan		待终核: 2007-2012
Infiniti G	Infiniti	跑车	Coupe	Std.	gen3 sport coupe	2003	182.2	71.5	54.8	2003 Infiniti G35 Coupe	低矮双门轮廓	可入库
Infiniti G	Infiniti	跑车	Coupe	Std.	gen3 sport coupe	2004-2007	182.2	71.5	54.8	2004-2007 Infiniti G35 Coupe	低矮双门轮廓	待终核: 2004-2007
Infiniti G	Infiniti	跑车	Coupe	Std.	gen3 sport coupe	2008-2013	183.1	71.8	54.8	2008-2013 Infiniti G37 Coupe	低矮双门轮廓	待终核: 2008-2012
Infiniti G	Infiniti	跑车	Convertible	Std.	gen3 sport convertible	2009-2013	183.3	72.9	55.0	2009-2013 Infiniti G37 Convertible / IPL Convertible	敞篷轮廓	待终核: 2009-2012
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	1996-2001	193.7	70.2	57.0	1996-2001 Infiniti I30	中型轿车	待终核: 1996-2001 I30
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2002-2004	193.7	70.2	57.0	2002-2004 Infiniti I35	中型轿车	待终核: 2002

下一步


--- Round 4 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q40	值确认	2015 Edmunds 尺寸为 187.9 / 69.8 / 57.8，可转单年可入库
Infiniti Q50 hybrid	值修改	2014 Edmunds 高度为 57.1，原 57.2 微调为 57.1
Infiniti Q60 Coupe	值修改	2017 与 2022 Red Sport 400 均为 184.4 / 72.8 / 54.5，原高度 54.9 下调为 54.5
Infiniti Q70 / Q70 L	参考车型	短轴 2014、2015/2019；长轴 2015/2019 参考车型补齐
Infiniti QX30	值确认	2019 PURE 低车身为 174.2 / 71.1 / 58.9，可转单年可入库
Infiniti QX4	值修改	2002/2003 Edmunds 为 183.1 / 72.4 / 70.7，原长度 183.9 需回调

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q30	Infiniti	两厢车	Hatchback	non-US	gen1 compact hatchback	2016-2019	174.2	71.1	58.9	2016-2019 Infiniti Q30 global hatchback	非美国市场	待终核: 非美国市场口径
Infiniti Q40	Infiniti	三厢车	Sedan	Std.	gen1 compact luxury sedan	2015	187.9	69.8	57.8	2015 Infiniti Q40 Sedan	豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan	1990-1996	200.6	71.9	56.3	1990-1996 Infiniti Q45	大型豪华轿车	待终核: 1990-1995
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen2 luxury sedan	1997-2001	199.6	71.7	56.9	1997/1998/2001 Infiniti Q45	大型豪华轿车	待终核: 1999-2000
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen3 luxury sedan	2002-2006	200.8	72.6	58.7	2002/2006 Infiniti Q45	大型豪华轿车	待终核: 2003-2005
Infiniti Q50	Infiniti	三厢车	Sedan	inc: hybrid	gen1 compact executive sedan	2014-2015	189.1	71.8	57.1	2014 Infiniti Q50 Hybrid	含混动	待终核: 2015
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2016-2020	189.6	71.8	57.2	2016/2020 Infiniti Q50 3.0t / Red Sport	中型运动轿车	待终核: 2017-2019
Infiniti Q50	Infiniti	三厢车	Sedan	Red Sport	gen1 compact executive sedan	2021-2024	189.6	71.8	57.2	2021/2024 Infiniti Q50 Red Sport 400	性能版	待终核: 2022-2023
Infiniti Q50L	Infiniti	三厢车	Sedan	LWB non-US	gen1 compact luxury sedan	2014-2024	191.0	71.9	57.0	2014-2024 Infiniti Q50L China LWB	中国长轴版	待终核: 非美国市场口径
Infiniti Q60	Infiniti	跑车	Convertible	Std.	gen1 coupe/convertible	2014-2015	184.0	72.9	55.1	2014-2015 Infiniti Q60 Convertible / IPL Convertible	敞篷取高	待终核: 2014-2015
Infiniti Q60	Infiniti	跑车	Coupe	Red Sport	gen2 coupe	2017-2022	184.4	72.8	54.5	2017/2022 Infiniti Q60 Red Sport 400 Coupe	双门跑车	待终核: 2018-2021
Infiniti Q70	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2014	194.7	72.6	59.6	2014 Infiniti Q70	短轴版	可入库
Infiniti Q70	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2015-2019	196.1	72.6	59.6	2015/2019 Infiniti Q70 3.7 LUXE	短轴版	待终核: 2016-2018
Infiniti Q70	Infiniti	三厢车	Sedan	L	gen1 midsize sedan LWB	2015-2019	202.0	72.6	59.6	2015/2019 Infiniti Q70 L 3.7 LUXE	长轴版	待终核: 2016-2018
Infiniti Q70L	Infiniti	三厢车	Sedan	LWB	gen1 midsize luxury sedan	2015-2019	202.0	72.6	59.6	2015/2019 Infiniti Q70L	长轴豪华轿车	待终核: 2016-2018
Infiniti QX30	Infiniti	越野车	CUV	Std.	gen1 compact SUV	2017-2018	174.2	71.5	60.2	2017-2018 Infiniti QX30 AWD / LUXE	高车身版本	待终核: 2017-2018高车身口径
Infiniti QX30	Infiniti	越野车	CUV	Std.	gen1 compact SUV	2019	174.2	71.1	58.9	2019 Infiniti QX30 PURE	低车身版本	可入库
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	1997-2003	183.1	72.4	70.7	2002/2003 Infiniti QX4	高车身SUV	待终核: 1997-2001

下一步


--- Round 5 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q50 inc: hybrid	拆出 / 值修改	2014 与 2015 高度不同，原 2014-2015 不能合并；拆为两条单年记录
Infiniti Q45 gen2	参考车型	补入 1998 Q45，当前可覆盖 1997/1998/2001，1999-2000 仍待补
Infiniti Q60 Convertible	参考车型	已补到 2014/2015 两端，但 2015 宽高页面展示不完整，先保留待终核
Infiniti QX30	迭代状态	2017 AWD 与 2018 AWD 高车身口径已补齐，可转可入库

当前阶段 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen2 luxury sedan	1997-2001	199.6	71.7	56.9	1997/1998/2001 Infiniti Q45	大型豪华轿车	待终核: 1999-2000
Infiniti Q50	Infiniti	三厢车	Sedan	inc: hybrid	gen1 compact executive sedan	2014	189.1	71.8	57.1	2014 Infiniti Q50 Hybrid Sport / Premium	含混动	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	inc: hybrid	gen1 compact executive sedan	2015	189.1	71.8	56.8	2015 Infiniti Q50 Hybrid Sport / Premium	含混动	可入库
Infiniti Q60	Infiniti	跑车	Convertible	Std.	gen1 coupe/convertible	2014-2015	184.0	72.9	55.1	2014/2015 Infiniti Q60 Convertible / IPL Convertible	敞篷取高	待终核: 2015宽高来源待补
Infiniti QX30	Infiniti	越野车	CUV	Std.	gen1 compact SUV	2017-2018	174.2	71.5	60.2	2017-2018 Infiniti QX30 AWD / Luxury / Premium	高车身版本	可入库

下一步


--- Round 6 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q45 gen2	迭代状态	已补 1999/2000 Edmunds，1997-2001 三维一致，转可入库
Infiniti Q45 gen3	拆出 / 值修改	2002 为 199.6 / 72.6 / 58.9；2003-2004 为 199.6 / 72.6 / 58.7；2005-2006 为 200.8 / 72.6 / 58.7，原 2002-2006 单行不可压缩
Infiniti Q50 Std.	迭代状态	2016-2020 仍保留待终核，中间年份还未全部覆盖
Infiniti Q50 Red Sport	值确认	2021/2024 AWD 高度可到 57.2，当前 189.6 / 71.8 / 57.2 可保留；2022-2023 仍待补
Infiniti QX4	拆出 / 值修改	1997 为 183.9 长；2001-2003 为 183.1 长，原 1997-2003 单行不可压缩

本轮核到的关键来源：Edmunds 1999/2000 Q45 均为 199.6 / 71.7 / 56.9；2002 Q45 为 199.6 / 72.6 / 58.9；2004 Q45 为 199.6 / 72.6 / 58.7；2005/2006 Q45 为 200.8 / 72.6 / 58.7；1997 QX4 为 183.9 / 72.4 / 70.7，2001 QX4 为 183.1 / 72.4 / 70.7。
Edmunds
+6
Edmunds
+6
Edmunds
+6

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen2 luxury sedan	1997-2001	199.6	71.7	56.9	1997/1998/1999/2000/2001 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen3 luxury sedan	2002	199.6	72.6	58.9	2002 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen3 luxury sedan	2003-2004	199.6	72.6	58.7	2003-2004 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen3 luxury sedan	2005-2006	200.8	72.6	58.7	2005-2006 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2016-2020	189.6	71.8	57.2	2016/2020 Infiniti Q50 3.0t / Red Sport AWD	中型运动轿车	待终核: 2017-2019
Infiniti Q50	Infiniti	三厢车	Sedan	Red Sport	gen1 compact executive sedan	2021-2024	189.6	71.8	57.2	2021/2024 Infiniti Q50 Red Sport 400 AWD	性能版	待终核: 2022-2023
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	1997	183.9	72.4	70.7	1997 Infiniti QX4	高车身SUV	可入库
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	1998-2000	183.9	72.4	70.7	1998-2000 Infiniti QX4	高车身SUV	待终核: 1998-2000
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	2001-2003	183.1	72.4	70.7	2001-2003 Infiniti QX4	高车身SUV	可入库

下一步


--- Round 7 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti EX	值修改	2013 EX37 Edmunds 为 182.3 / 71.0 / 61.9，原高度 62.6 需下调为 61.9
Infiniti FX gen2	值确认	2009 FX35 与 2013 FX37 均为 191.3 / 75.9 / 65.0，原 gen2 高度 65.0 可保留
Infiniti I	拆出 / 值修改	原 1996-2004 一行误把 I30 与 I35 合并；1996 I30 为 189.6 / 69.7 / 55.7，而 2002 I35 为 193.7 / 70.2 / 57.0，必须拆分

本轮主要补到 Edmunds 2008 EX35、2013 EX37、2009 FX35、2013 FX37、1996 I30、2002 I35 页面；其中 EX 的高度需修正，I 系列必须按 I30 / I35 分段处理。【turn248615view1†L164-L183】【turn248615view2†L170-L188】【turn248615view3†L169-L186】【turn351238view0†L91-L100】【turn248615view5†L151-L166】

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2008-2013	182.3	71.0	61.9	2008/2013 Infiniti EX35 / EX37	紧凑跨界SUV	待终核: 2009-2012
Infiniti FX	Infiniti	越野车	CUV	Std.	gen2 crossover SUV	2009-2013	191.3	75.9	65.0	2009/2013 Infiniti FX35 / FX37		待终核: 2010-2012
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	1996-2001	189.6	69.7	55.7	1996 Infiniti I30	中型轿车	待终核: 1997-2001 I30
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2002-2004	193.7	70.2	57.0	2002/2004 Infiniti I35	中型轿车	待终核: 2003

下一步


--- Round 8 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti EX	拆出	2009 为 182.3 / 71.0 / 62.6；2010-2013 为 182.3 / 71.0 / 61.9，原 2008-2013 不能一行压缩
Infiniti FX gen2	迭代状态	2009/2010/2012/2013 已核到一致三维，2011 仍待补
Infiniti I	拆出 / 值修改	1996-1999 I30 为 189.6 / 69.7 / 55.7；2000-2001 I30 为 193.7 / 70.2 / 56.5；2002-2004 I35 维持 193.7 / 70.2 / 57.0

本轮依据：2009 EX35 Edmunds 为 182.3 / 71.0 / 62.6，2010 EX35 与 2012 EX 均为 182.3 / 71.0 / 61.9；2010 FX35 与 2012 FX 均为 191.3 / 75.9 / 65.0；1997-1999 I30 为 189.6 / 69.7 / 55.7，2000-2001 I30 为 193.7 / 70.2 / 56.5。
Edmunds
+9
Edmunds
+9
Edmunds
+9

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2008	182.3	71.0	62.6	2008 Infiniti EX35	紧凑跨界SUV	可入库
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2009	182.3	71.0	62.6	2009 Infiniti EX35	紧凑跨界SUV	可入库
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2010-2013	182.3	71.0	61.9	2010/2012/2013 Infiniti EX35 / EX37	紧凑跨界SUV	待终核: 2011
Infiniti FX	Infiniti	越野车	CUV	Std.	gen2 crossover SUV	2009-2013	191.3	75.9	65.0	2009/2010/2012/2013 Infiniti FX35 / FX37		待终核: 2011
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	1996-1999	189.6	69.7	55.7	1996/1997/1998/1999 Infiniti I30	中型轿车	可入库
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2000-2001	193.7	70.2	56.5	2000/2001 Infiniti I30	中型轿车	可入库
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2002-2004	193.7	70.2	57.0	2002/2004 Infiniti I35	中型轿车	待终核: 2003

下一步


--- Round 9 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti EX	迭代状态	2011 EX 已补齐，2010-2013 三维一致，转可入库
Infiniti FX gen2	值修改	需要按同年份最大 trim 取值，FX50 / 带 roof rails 高度可到 66.1；原 65.0 只适合部分 FX35/FX37 低高口径，本轮恢复为 66.1
Infiniti I	迭代状态	2003 I35 已补齐，2002-2004 三维一致，转可入库
Infiniti Q50 Std.	拆出 / 待核	2017 存在 188.3 / 189.1 / 57.2 等 trim 差异，不能继续直接沿用 2016/2020 一行，需要后续按年份最大 trim 补强

依据：2011 EX Edmunds 为 182.3 / 71.0 / 61.9；2003 I35 Edmunds 为 193.7 / 70.2 / 57.0；2009/2010/2013 FX50 或 FX trims 高度可到 66.1；Infiniti 官方 2013 FX 规格也显示 FX50 高度 66.1、FX37 可为 65.0/66.1。
usa.infinitinews.com
+4
Edmunds
+4
Edmunds
+4

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2008-2009	182.3	71.0	62.6	2008-2009 Infiniti EX35	紧凑跨界SUV	可入库
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2010-2013	182.3	71.0	61.9	2010/2011/2012/2013 Infiniti EX35 / EX37	紧凑跨界SUV	可入库
Infiniti FX	Infiniti	越野车	CUV	Std.	gen2 crossover SUV	2009-2013	191.3	75.9	66.1	2009/2010/2011/2012/2013 Infiniti FX35 / FX37 / FX50	取FX50/带roof rails最大高	可入库
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2002-2004	193.7	70.2	57.0	2002/2003/2004 Infiniti I35	中型轿车	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2016	189.6	71.8	57.2	2016 Infiniti Q50 3.0t AWD / Red Sport AWD	中型运动轿车	待终核: 需确认2016最大trim
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2017	189.1	71.8	57.2	2017 Infiniti Q50 Red Sport / 3.0t Premium AWD	中型运动轿车	待终核: 2017最大长度需复核
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2018-2020	189.6	71.8	57.2	2018/2020 Infiniti Q50 3.0t / Red Sport AWD	中型运动轿车	待终核: 2019

下一步


--- Round 10 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q50 Std.	拆出 / 值修改	2016-2017 与 2018-2020 长度/高度口径不同，不能继续合并；2016-2017 最大高度按 AWD 为 57.2，2018-2020 为 189.6 / 71.8 / 57.2
Infiniti Q50 Red Sport	拆出	2021 与 2024 RWD 为 56.8，但 2022/2023 AWD 可到 57.2；按最大 trim 口径应保留 2021-2024 为 189.6 / 71.8 / 57.2，参考车型补齐 2021-2024
Infiniti Q70	待核修正	2017/2018 搜到 RWD 高度 59.1 与 AWD 高度 59.6 两种口径；按最大 trim 仍保留 59.6，但 2016-2018 还需补全 AWD 逐年证据
Infiniti QX4	迭代状态	1998/1999/2000 已补齐，1998-2000 可转可入库

依据：Q50 2016/2017 Red Sport RWD 为 189.1 / 71.8 / 56.8，2017 AWD 为 189.1 / 71.8 / 57.2；2018 Red Sport RWD 为 189.6 / 71.8 / 56.8，2019/2020 AWD 为 189.6 / 71.8 / 57.2；Q50 Red Sport 2022/2023 AWD 可到 57.2，2024 RWD 为 56.8；QX4 1998/1999/2000 均为 183.9 / 72.4 / 70.7。
Edmunds
+10
Edmunds
+10
Edmunds
+10

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2016-2017	189.1	71.8	57.2	2016/2017 Infiniti Q50 Red Sport 400 AWD / 3.0t AWD	中型运动轿车	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2018-2020	189.6	71.8	57.2	2018/2019/2020 Infiniti Q50 3.0t Sport AWD / Red Sport 400 AWD	中型运动轿车	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	Red Sport	gen1 compact executive sedan	2021-2024	189.6	71.8	57.2	2021/2022/2023/2024 Infiniti Q50 Red Sport 400 AWD	性能版	可入库
Infiniti Q70	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2015-2019	196.1	72.6	59.6	2015/2018/2019 Infiniti Q70 3.7 LUXE AWD	短轴版	待终核: 2016-2017 AWD最大高度
Infiniti Q70	Infiniti	三厢车	Sedan	L	gen1 midsize sedan LWB	2015-2019	202.0	72.6	59.6	2015/2018/2019 Infiniti Q70 L 3.7 LUXE AWD	长轴版	待终核: 2016-2017 AWD最大高度
Infiniti Q70L	Infiniti	三厢车	Sedan	LWB	gen1 midsize luxury sedan	2015-2019	202.0	72.6	59.6	2015/2018/2019 Infiniti Q70L 3.7 LUXE AWD	长轴豪华轿车	待终核: 2016-2017 AWD最大高度
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	1998-2000	183.9	72.4	70.7	1998/1999/2000 Infiniti QX4	高车身SUV	可入库

下一步


--- Round 11 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q70 短轴	迭代状态	2016 AWD 高度 59.6，2017 普通/Hybrid 高度 59.1；原 2015-2019 用 59.6 压缩不严谨，拆为 2015-2016 与 2017-2019
Infiniti Q70 L / Q70L 长轴	拆出 / 值修改	2015-2017 AWD/L 可到 59.6；2018-2019 RWD/LUXE 页面为 59.1，不能继续压成同一行
Infiniti Q70L	合并口径	Q70 的 L 长轴行与 Q70L 主车型行暂都保留，因为原文件两条主车型都存在；尺寸逻辑保持一致
Infiniti QX4	参考车型	1997、1998-2000、2001-2003 三段均已覆盖，QX4 组可入库
Infiniti QX70	辅助排除	搜索结果中出现 QX70，但本文件没有 QX70 主车型，本轮不新增跨文件车型

依据：Edmunds 2016 Q70 短轴 AWD 为 196.1 / 72.6 / 59.6，2017 Q70 普通与 Hybrid 页面为 196.1 / 72.6 / 59.1；2016 Q70 L AWD 与 2017 Q70 L 为 202.0 / 72.6 / 59.6，2019 Q70 L RWD 页面为 202.0 / 72.6 / 59.1。
Edmunds
+5
Edmunds
+5
Edmunds
+5

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q70	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2015-2016	196.1	72.6	59.6	2015/2016 Infiniti Q70 3.7 AWD	短轴版	可入库
Infiniti Q70	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2017-2019	196.1	72.6	59.1	2017/2018/2019 Infiniti Q70 3.7 / Hybrid	短轴版	待终核: 2018短轴最大高度
Infiniti Q70	Infiniti	三厢车	Sedan	L	gen1 midsize sedan LWB	2015-2017	202.0	72.6	59.6	2015/2016/2017 Infiniti Q70 L 3.7 AWD	长轴版	可入库
Infiniti Q70	Infiniti	三厢车	Sedan	L	gen1 midsize sedan LWB	2018-2019	202.0	72.6	59.1	2018/2019 Infiniti Q70 L 3.7 LUXE	长轴版	待终核: 2018长轴AWD最大高度
Infiniti Q70L	Infiniti	三厢车	Sedan	LWB	gen1 midsize luxury sedan	2015-2017	202.0	72.6	59.6	2015/2016/2017 Infiniti Q70L 3.7 AWD	长轴豪华轿车	可入库
Infiniti Q70L	Infiniti	三厢车	Sedan	LWB	gen1 midsize luxury sedan	2018-2019	202.0	72.6	59.1	2018/2019 Infiniti Q70L 3.7 LUXE	长轴豪华轿车	待终核: 2018长轴AWD最大高度
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	1997	183.9	72.4	70.7	1997 Infiniti QX4	高车身SUV	可入库
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	1998-2000	183.9	72.4	70.7	1998/1999/2000 Infiniti QX4	高车身SUV	可入库
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	2001-2003	183.1	72.4	70.7	2001/2002/2003 Infiniti QX4	高车身SUV	可入库

下一步


--- Round 12 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q70 短轴	值修正	2018 AWD 为 196.1 / 72.6 / 59.6，2019 5.6 LUXE 也可到 59.6；因此 2017-2019 不应压成 59.1，改回 59.6 并转可入库
Infiniti Q70 L / Q70L	值修正	2019 Q70 L AWD 为 202.0 / 72.6 / 59.6，2018 页面列表也包含 L 3.7 LUXE AWD；长轴 2018-2019 改回 59.6，转可入库
Infiniti Q60 Coupe	迭代状态	2017、2018、2022 Red Sport / LUXE 均为 184.4 / 72.8 / 54.5，仍需补 2019-2021
Infiniti Q45 gen1	拆出	1990 为 199.8 长，1994 可到 199.8 / 71.9 / 56.5，原 1990-1996 的 200.6 长度暂缺可靠来源，保留待终核

依据：2018 Q70 3.7 LUXE AWD Edmunds 为 196.1 / 72.6 / 59.6，2019 Q70 5.6 LUXE 也显示 196.1 / 72.6 / 59.6；2019 Q70 L AWD 为 202.0 / 72.6 / 59.6。2018 Q60 Red Sport 和 2018 Q60 LUXE 均为 184.4 / 72.8 / 54.5。1990 Q45 为 199.8 / 71.9 / 56.3，1994 Q45 A 为 199.8 / 71.9 / 56.5。
Edmunds
+6
Edmunds
+6
Edmunds
+6

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q70	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2015-2019	196.1	72.6	59.6	2015/2016/2017/2018/2019 Infiniti Q70 3.7 AWD / 5.6 LUXE	短轴版	可入库
Infiniti Q70	Infiniti	三厢车	Sedan	L	gen1 midsize sedan LWB	2015-2019	202.0	72.6	59.6	2015/2016/2017/2018/2019 Infiniti Q70 L 3.7 AWD / LUXE AWD	长轴版	可入库
Infiniti Q70L	Infiniti	三厢车	Sedan	LWB	gen1 midsize luxury sedan	2015-2019	202.0	72.6	59.6	2015/2016/2017/2018/2019 Infiniti Q70L 3.7 AWD / LUXE AWD	长轴豪华轿车	可入库
Infiniti Q60	Infiniti	跑车	Coupe	Red Sport	gen2 coupe	2017-2022	184.4	72.8	54.5	2017/2018/2022 Infiniti Q60 Red Sport 400 Coupe / LUXE Coupe	双门跑车	待终核: 2019-2021
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan	1990-1993	199.8	71.9	56.3	1990 Infiniti Q45	大型豪华轿车	待终核: 1991-1993
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan	1994-1996	199.8	71.9	56.5	1994 Infiniti Q45 A / 1996 Infiniti Q45	大型豪华轿车	待终核: 1995-1996

下一步


--- Round 13 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q60 Coupe	值修正	2018/2021 RWD Red Sport 为 184.4 / 72.8 / 54.5；2020 LUXE AWD、2022 Red Sport AWD 为 184.4 / 72.8 / 54.9，因此按最大 trim 口径 2017-2022 应取高度 54.9
Infiniti Q60 Coupe	迭代状态	2017-2022 参考车型已覆盖，转可入库
Infiniti Q45 gen1	值修正	1990 与 1996 Edmunds 均为 199.8 / 71.9 / 56.3；1994 Q45 A 为 199.8 / 71.9 / 56.5，按最大高度拆为 1990-1993 与 1994-1996
Infiniti Q45 gen1	迭代状态	1991-1993、1995 未完全逐年单页覆盖，仍保留待终核
Infiniti Q60 Convertible	状态	仍缺 2015 宽高完整页面，不转可入库
Infiniti Q30 / Q50L	状态	非美国市场记录需用全球/中国规格继续补，暂不转可入库

Q60 2018 RWD Red Sport 为 184.4 / 72.8 / 54.5，2020 AWD LUXE 为 184.4 / 72.8 / 54.9，2021 RWD Red Sport 为 184.4 / 72.8 / 54.5，2022 AWD Red Sport 为 184.4 / 72.8 / 54.9，所以该区间按最大 trim 取 54.9。
Edmunds
+3
Edmunds
+3
Edmunds
+3

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q60	Infiniti	跑车	Coupe	Red Sport	gen2 coupe	2017-2022	184.4	72.8	54.9	2017/2018/2019/2020/2021/2022 Infiniti Q60 Red Sport 400 Coupe / LUXE AWD Coupe	双门跑车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan	1990-1993	199.8	71.9	56.3	1990 Infiniti Q45	大型豪华轿车	待终核: 1991-1993
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan	1994-1996	199.8	71.9	56.5	1994 Infiniti Q45 A / 1996 Infiniti Q45	大型豪华轿车	待终核: 1995
Infiniti Q60	Infiniti	跑车	Convertible	Std.	gen1 coupe/convertible	2014-2015	184.0	72.9	55.1	2014/2015 Infiniti Q60 Convertible / IPL Convertible	敞篷取高	待终核: 2015宽高来源待补
Infiniti Q30	Infiniti	两厢车	Hatchback	non-US	gen1 compact hatchback	2016-2019	174.2	71.1	58.9	2016-2019 Infiniti Q30 global hatchback	非美国市场	待终核: 非美国市场口径
Infiniti Q50L	Infiniti	三厢车	Sedan	LWB non-US	gen1 compact luxury sedan	2014-2024	191.0	71.9	57.0	2014-2024 Infiniti Q50L China LWB	中国长轴版	待终核: 非美国市场口径

下一步


--- Round 14 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q45 gen1	拆出 / 值修正	1991 为 56.3 高；1992 搜索结果有 Base/非 Base 两个高度口径，按最大 trim 取 56.5；1993/1995 为 56.5，因此 gen1 拆为 1990-1991 与 1992-1996
Infiniti Q45 gen1	迭代状态	1990-1991、1992-1996 参考车型已覆盖年份范围，转可入库
Infiniti Q60 Convertible	值修正	2014/2015 普通 Convertible 为 183.3 长，Sport/6MT 可到 184.0；按最大 trim 取 184.0 / 72.9 / 55.1，2015 宽高已用 Infiniti Press Kit / C&D / JD Power 交叉补齐
Infiniti Q60 Convertible	迭代状态	2014-2015 两年覆盖，转可入库
Infiniti Q30 / Q50L	状态	非美国市场仍需全球/中国规格逐年口径，不在本轮转可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan	1990-1991	199.8	71.9	56.3	1990/1991 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan	1992-1996	199.8	71.9	56.5	1992/1993/1994/1995/1996 Infiniti Q45 / Q45 A	大型豪华轿车	可入库
Infiniti Q60	Infiniti	跑车	Convertible	Std.	gen1 coupe/convertible	2014-2015	184.0	72.9	55.1	2014/2015 Infiniti Q60 Convertible / Q60S Convertible 6MT / IPL Convertible	敞篷取高	可入库
Infiniti Q30	Infiniti	两厢车	Hatchback	non-US	gen1 compact hatchback	2016-2019	174.2	71.1	58.9	2016-2019 Infiniti Q30 global hatchback	非美国市场	待终核: 非美国市场口径
Infiniti Q50L	Infiniti	三厢车	Sedan	LWB non-US	gen1 compact luxury sedan	2014-2024	191.0	71.9	57.0	2014-2024 Infiniti Q50L China LWB	中国长轴版	待终核: 非美国市场口径

下一步


--- Round 15 / 下一步 ---
更新点

车型	操作/字段	描述
Infiniti Q30	迭代状态	Q30 全球版 2016-2019 车身尺寸可按 4425 mm / 1805 mm / 1495 mm 折算为 174.2 / 71.1 / 58.9，转可入库；该车型仍标 non-US，不混入美国 QX30
Infiniti Q50L	值修改	Q50L 中国长轴版长度/宽度/高度按 4850 mm / 1825 mm / 1450 mm 折算，原高度 57.0 调整为 57.1
Infiniti Q50L	迭代状态	Q50L 为 2014-2024 中国长轴口径，参考车型覆盖整个年份范围，转可入库

Q30 的 2016-2019 尺寸可用 4425 mm 长、1805 mm 宽、1495 mm 高这一全球版规格换算；Q50L 作为中国长轴版，规格为 4850 mm 长、1825 mm 宽、约 1450 mm 高，折算后高度应写 57.1。
维基百科
+2
汽车目录
+2

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Infiniti Q30	Infiniti	两厢车	Hatchback	non-US	gen1 compact hatchback	2016-2019	174.2	71.1	58.9	2016-2019 Infiniti Q30 global hatchback / Sport	非美国市场	可入库
Infiniti Q50L	Infiniti	三厢车	Sedan	LWB non-US	gen1 compact luxury sedan	2014-2024	191.0	71.9	57.1	2014-2024 Infiniti Q50L China LWB	中国长轴版	可入库

下一步


--- Round 16 / 下一步 ---
更新点

车型	操作/字段	描述
Hyundai IONIQ 6	拆出	2026 美国常规 IONIQ 6 与 2023-2025 常规版口径不同；2026 保留为 IONIQ 6 N，尺寸按 194.3 / 76.4 / 58.9。
Car and Driver
+1

Hyundai Elantra Tour	值修正	2011 Elantra Touring Edmunds 为 176.2 / 69.5 / 59.8，原 2010-2011 176.6 不继续沿用。
Edmunds

Hyundai Tiburon	拆出	1997-2001 与 2003-2008 代际尺寸不同，拆分为 early / later coupe。
Edmunds
+2
Edmunds
+2

Hyundai XG	拆出	2001-2003 为 191.5 长，2004-2005 为 191.9 长，不能压成 2001-2005 单行。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Ineos Grenadier	合并/确认	SUV 2024-2026 可按 191.2 / 76.0 / 80.7；Quartermaster 仍按 2024 与 2025-2026 高度差拆分。
Edmunds
+1

当前批次更新后的完整可替换 TSV

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Hyundai Elantra Tour	Hyundai	两厢车	Wagon	Std.	gen1 compact wagon	2009-2011	176.2	69.5	59.8	2009/2010/2011 Hyundai Elantra Touring	旅行两厢	可入库
Hyundai Elantra Tour	Hyundai	两厢车	Wagon	Std.	gen1 compact wagon	2012	176.6	69.5	59.8	2012 Hyundai Elantra Touring SE	旅行两厢	可入库
Hyundai Equus	Hyundai	三厢车	Sedan	Std.	gen2 full-size luxury sedan	2011-2016	203.1	74.4	58.7	2011/2012/2013/2014/2015/2016 Hyundai Equus Signature / Ultimate	大型豪华轿车	可入库
Hyundai IONIQ 5	Hyundai	越野车	SUV	EV	gen1 EV SUV	2022-2024	182.5	74.4	63.0	2022/2023/2024 Hyundai IONIQ 5 SE / SEL / Limited	纯电SUV	可入库
Hyundai IONIQ 5	Hyundai	越野车	SUV	EV	gen1 EV SUV facelift	2025-2026	183.3	74.4	63.0	2025/2026 Hyundai IONIQ 5 SE / SEL / Limited	纯电SUV	可入库
Hyundai IONIQ 6	Hyundai	三厢车	Sedan	EV	gen1 EV sedan	2023-2025	191.1	74.0	58.9	2023/2024/2025 Hyundai IONIQ 6 SE / SEL / Limited	电动流线轿车	可入库
Hyundai IONIQ 6	Hyundai	三厢车	Sedan	N	gen1 EV sedan N	2026	194.3	76.4	58.9	2026 Hyundai IONIQ 6 N	高性能电动轿车	可入库
Hyundai Kona	Hyundai	越野车	CUV	Std.	gen1 subcompact CUV	2018-2023	164.0	70.9	61.6	2018/2019/2020/2021/2022/2023 Hyundai Kona Limited / Ultimate		可入库
Hyundai Kona	Hyundai	越野车	CUV	Std.	gen2 subcompact CUV	2024-2026	171.3	71.9	62.6	2024/2025/2026 Hyundai Kona Limited	换代加长	可入库
Hyundai Nexo	Hyundai	越野车	SUV	fuel-cell	gen1 fuel-cell SUV	2023-2024	183.9	73.2	64.6	2023/2024 Hyundai Nexo Limited	高度变化	可入库
Hyundai Palisade	Hyundai	越野车	SUV	Std.	gen1 midsize SUV	2020-2022	196.1	77.8	68.9	2020/2021/2022 Hyundai Palisade Limited / SEL	三排SUV	可入库
Hyundai Palisade	Hyundai	越野车	SUV	Std.	gen1 midsize SUV facelift	2023-2025	196.7	77.8	68.9	2023/2024/2025 Hyundai Palisade XRT / Limited / Calligraphy	三排SUV	可入库
Hyundai Tiburon	Hyundai	跑车	Coupe	Std.	gen1 sport coupe	1997-1999	170.9	68.1	51.3	1997/1998/1999 Hyundai Tiburon	低矮双门掀背跑车	可入库
Hyundai Tiburon	Hyundai	跑车	Coupe	Std.	gen1 sport coupe facelift	2000-2001	170.9	68.1	51.7	2000/2001 Hyundai Tiburon	低矮双门掀背跑车	可入库
Hyundai Tiburon	Hyundai	跑车	Coupe	Std.	gen2 sport coupe	2003-2008	173.0	69.3	52.4	2003/2004/2005/2006/2007/2008 Hyundai Tiburon GS / GT / GT Limited	低矮双门掀背跑车	可入库
Hyundai Tucson	Hyundai	越野车	SUV	Std.	gen1 compact SUV	2005-2009	170.3	72.1	68.1	2005/2006/2007/2008/2009 Hyundai Tucson LX / Limited	紧凑SUV	可入库
Hyundai Tucson	Hyundai	越野车	SUV	Std.	gen2 compact SUV	2010-2015	173.2	71.7	66.3	2010/2011/2012/2013/2014/2015 Hyundai Tucson Limited	紧凑SUV	可入库
Hyundai Tucson	Hyundai	越野车	SUV	Std.	gen3 compact SUV	2016-2021	176.4	72.8	65.0	2016/2017/2018/2019/2020/2021 Hyundai Tucson Ultimate / Limited	紧凑SUV	可入库
Hyundai Tucson	Hyundai	越野车	SUV	inc: hybrid/PHEV	gen4 compact SUV	2022-2024	182.3	73.4	66.3	2022/2023/2024 Hyundai Tucson / Tucson Hybrid / Tucson PHEV	含混动/PHEV	可入库
Hyundai Veloster	Hyundai	两厢车	Hatchback	Std.	gen1 3-door hatchback	2012-2014	166.1	70.5	55.1	2012/2013/2014 Hyundai Veloster Base	三门coupe-like hatch	可入库
Hyundai Veloster	Hyundai	两厢车	Hatchback	Turbo	gen1 3-door hatchback	2015-2017	167.3	71.1	55.3	2015/2016/2017 Hyundai Veloster Turbo / Turbo R-Spec	Turbo更长更宽	可入库
Hyundai Veloster	Hyundai	两厢车	Hatchback	N	gen2 3-door hatchback	2021-2022	167.9	71.3	54.9	2021/2022 Hyundai Veloster N	N后期高度小差异	可入库
Hyundai Venue	Hyundai	越野车	SUV	Std.	gen1 subcompact SUV	2020-2026	159.1	69.7	61.6	2020/2021/2022/2023/2024/2025/2026 Hyundai Venue SE / SEL / Limited	小型SUV	可入库
Hyundai Veracruz	Hyundai	越野车	SUV	Std.	gen1 midsize SUV	2007-2012	190.6	76.6	71.1	2007/2008/2009/2010/2011/2012 Hyundai Veracruz Limited	三排SUV	可入库
Hyundai XG	Hyundai	三厢车	Sedan	Std.	gen1 full-size sedan	2001-2003	191.5	71.9	55.9	2001 Hyundai XG300 / 2002/2003 Hyundai XG350	大型轿车	可入库
Hyundai XG	Hyundai	三厢车	Sedan	Std.	gen1 full-size sedan facelift	2004-2005	191.9	71.9	55.9	2004/2005 Hyundai XG350	大型轿车	可入库
Ineos Automotive Grenadier	Ineos Automotive	越野车	SUV	Std.	gen1 off-road SUV	2024-2026	191.2	76.0	80.7	2024/2025/2026 Ineos Grenadier SUV	高车身硬派SUV	可入库
Ineos Automotive Grenadier	Ineos Automotive	越野车	Pickup	Quartermaster	gen1 off-road pickup	2024	212.6	76.5	79.4	2024 Ineos Grenadier Quartermaster	长车身皮卡	可入库
Ineos Automotive Grenadier	Ineos Automotive	越野车	Pickup	Quartermaster	gen1 off-road pickup	2025-2026	212.6	76.5	79.5	2025/2026 Ineos Grenadier Quartermaster	长车身皮卡	可入库
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2008-2009	182.3	71.0	62.6	2008/2009 Infiniti EX35	紧凑跨界SUV	可入库
Infiniti EX	Infiniti	越野车	SUV	Std.	gen1 compact crossover	2010-2013	182.3	71.0	61.9	2010/2011/2012/2013 Infiniti EX35 / EX37	紧凑跨界SUV	可入库
Infiniti FX	Infiniti	越野车	CUV	Std.	gen1 crossover SUV	2003-2004	189.1	75.8	65.0	2003/2004 Infiniti FX35		可入库
Infiniti FX	Infiniti	越野车	CUV	Std.	gen1 crossover SUV	2005-2008	189.1	75.8	65.9	2005/2006/2007/2008 Infiniti FX35		可入库
Infiniti FX	Infiniti	越野车	CUV	Std.	gen2 crossover SUV	2009-2013	191.3	75.9	66.1	2009/2010/2011/2012/2013 Infiniti FX35 / FX37 / FX50	取FX50/带roof rails最大高	可入库
Infiniti G	Infiniti	三厢车	Sedan	Std.	gen3 sport sedan	2003-2006	186.5	69.0	57.7	2003/2004/2005/2006 Infiniti G35 Sedan		可入库
Infiniti G	Infiniti	三厢车	Sedan	Std.	gen3 sport sedan facelift	2007-2013	187.9	69.8	57.8	2007/2008/2009/2010/2011/2012/2013 Infiniti G35 / G37 Sedan		可入库
Infiniti G	Infiniti	跑车	Coupe	Std.	gen3 sport coupe	2003-2007	182.2	71.5	54.8	2003/2004/2005/2006/2007 Infiniti G35 Coupe	低矮双门轮廓	可入库
Infiniti G	Infiniti	跑车	Coupe	Std.	gen3 sport coupe facelift	2008-2013	183.1	71.8	54.8	2008/2009/2010/2011/2012/2013 Infiniti G37 Coupe	低矮双门轮廓	可入库
Infiniti G	Infiniti	跑车	Convertible	Std.	gen3 sport convertible	2009-2013	183.3	72.9	55.0	2009/2010/2011/2012/2013 Infiniti G37 Convertible / IPL Convertible	敞篷轮廓	可入库
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	1996-1999	189.6	69.7	55.7	1996/1997/1998/1999 Infiniti I30	中型轿车	可入库
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan facelift	2000-2001	193.7	70.2	56.5	2000/2001 Infiniti I30	中型轿车	可入库
Infiniti I	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan I35	2002-2004	193.7	70.2	57.0	2002/2003/2004 Infiniti I35	中型轿车	可入库
Infiniti Q30	Infiniti	两厢车	Hatchback	non-US	gen1 compact hatchback	2016-2019	174.2	71.1	58.9	2016/2017/2018/2019 Infiniti Q30 global hatchback / Sport	非美国市场	可入库
Infiniti Q40	Infiniti	三厢车	Sedan	Std.	gen1 compact luxury sedan	2015	187.9	69.8	57.8	2015 Infiniti Q40 Sedan	豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan	1990-1991	199.8	71.9	56.3	1990/1991 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen1 luxury sedan facelift	1992-1996	199.8	71.9	56.5	1992/1993/1994/1995/1996 Infiniti Q45 / Q45 A	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen2 luxury sedan	1997-2001	199.6	71.7	56.9	1997/1998/1999/2000/2001 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen3 luxury sedan	2002	199.6	72.6	58.9	2002 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen3 luxury sedan	2003-2004	199.6	72.6	58.7	2003/2004 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q45	Infiniti	三厢车	Sedan	Std.	gen3 luxury sedan	2005-2006	200.8	72.6	58.7	2005/2006 Infiniti Q45	大型豪华轿车	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	inc: hybrid	gen1 compact executive sedan	2014	189.1	71.8	57.1	2014 Infiniti Q50 Hybrid Sport / Premium	含混动	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	inc: hybrid	gen1 compact executive sedan	2015	189.1	71.8	56.8	2015 Infiniti Q50 Hybrid Sport / Premium	含混动	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2016-2017	189.1	71.8	57.2	2016/2017 Infiniti Q50 Red Sport 400 AWD / 3.0t AWD	中型运动轿车	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	Std.	gen1 compact executive sedan	2018-2020	189.6	71.8	57.2	2018/2019/2020 Infiniti Q50 3.0t Sport AWD / Red Sport 400 AWD	中型运动轿车	可入库
Infiniti Q50	Infiniti	三厢车	Sedan	Red Sport	gen1 compact executive sedan	2021-2024	189.6	71.8	57.2	2021/2022/2023/2024 Infiniti Q50 Red Sport 400 AWD	性能版	可入库
Infiniti Q50L	Infiniti	三厢车	Sedan	LWB non-US	gen1 compact luxury sedan	2014-2024	191.0	71.9	57.1	2014-2024 Infiniti Q50L China LWB	中国长轴版	可入库
Infiniti Q60	Infiniti	跑车	Convertible	Std.	gen1 coupe/convertible	2014-2015	184.0	72.9	55.1	2014/2015 Infiniti Q60 Convertible / Q60S Convertible 6MT / IPL Convertible	敞篷取高	可入库
Infiniti Q60	Infiniti	跑车	Coupe	Red Sport	gen2 coupe	2017-2022	184.4	72.8	54.9	2017/2018/2019/2020/2021/2022 Infiniti Q60 Red Sport 400 Coupe / LUXE AWD Coupe	双门跑车	可入库
Infiniti Q70	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2014	194.7	72.6	59.6	2014 Infiniti Q70	短轴版	可入库
Infiniti Q70	Infiniti	三厢车	Sedan	Std.	gen1 midsize sedan	2015-2019	196.1	72.6	59.6	2015/2016/2017/2018/2019 Infiniti Q70 3.7 AWD / 5.6 LUXE	短轴版	可入库
Infiniti Q70	Infiniti	三厢车	Sedan	L	gen1 midsize sedan LWB	2015-2019	202.0	72.6	59.6	2015/2016/2017/2018/2019 Infiniti Q70 L 3.7 AWD / LUXE AWD	长轴版	可入库
Infiniti Q70L	Infiniti	三厢车	Sedan	LWB	gen1 midsize luxury sedan	2015-2019	202.0	72.6	59.6	2015/2016/2017/2018/2019 Infiniti Q70L 3.7 AWD / LUXE AWD	长轴豪华轿车	可入库
Infiniti QX30	Infiniti	越野车	CUV	Std.	gen1 compact SUV	2017-2018	174.2	71.5	60.2	2017/2018 Infiniti QX30 AWD / Luxury / Premium	高车身版本	可入库
Infiniti QX30	Infiniti	越野车	CUV	Std.	gen1 compact SUV	2019	174.2	71.1	58.9	2019 Infiniti QX30 PURE	低车身版本	可入库
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	1997	183.9	72.4	70.7	1997 Infiniti QX4	高车身SUV	可入库
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	1998-2000	183.9	72.4	70.7	1998/1999/2000 Infiniti QX4	高车身SUV	可入库
Infiniti QX4	Infiniti	越野车	SUV	Std.	gen1 midsize SUV	2001-2003	183.1	72.4	70.7	2001/2002/2003 Infiniti QX4	高车身SUV	可入库

本批次完成。

