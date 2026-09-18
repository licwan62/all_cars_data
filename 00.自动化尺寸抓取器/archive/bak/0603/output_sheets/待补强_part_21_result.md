# 文件名：待补强_part_21.tsv


--- Round 1 / 首次发送 ---
本轮先补强了有明确 Edmunds 年份覆盖的 Nissan 新款记录：Ariya 2023/2024/2025 三年尺寸一致；Kicks 2025/2026 尺寸一致；Murano 2025/2026 尺寸一致；Z 标准版 2026 尺寸与原记录一致。Ariya、Kicks、Murano、Z 的关键尺寸依据分别来自 Edmunds 对应年份页面。
Edmunds
+7
Edmunds
+7
Edmunds
+7

更新点

车型	操作	描述
Nissan Ariya	拆出/推进	2023-2025 已可入库；2026 暂保留待补强
Nissan Kicks	推进	gen2 2025-2026 参考车型覆盖完整，改为可入库
Nissan Murano	推进	gen4 2025-2026 参考车型覆盖完整，改为可入库
Nissan Z	推进	标准版补到 2026，但 2023 仍需补强，暂不整体可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Ariya	Nissan	越野车	SUV	EV	gen1 midsize SUV	2023-2025	182.9	74.8	65.4	2023/2024/2025 Nissan Ariya, Edmunds		可入库
Nissan Ariya	Nissan	越野车	SUV	EV	gen1 midsize SUV	2026	182.9	74.8	65.4	2025 Nissan Ariya Engage, Edmunds		待补强: 2026
Nissan Kicks	Nissan	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	171.9	70.9	64.2	2025/2026 Nissan Kicks SV, Edmunds	新一代尺寸增大	可入库
Nissan Murano	Nissan	越野车	SUV	Std.	gen4 wide	2025-2026	192.9	78.0	67.9	2025/2026 Nissan Murano SV/SL, Edmunds	宽体新款	可入库
Nissan Z	Nissan	跑车	Coupe	Std.	gen7 compact sports coupe	2023-2026	172.4	72.6	51.8	2024/2025/2026 Nissan Z Performance, Edmunds	标准Z车身	待补强: 2023

下一步


--- Round 2 / 下一步 ---
本轮继续补强 Nissan 记录：370Z NISMO、Altima 早期/中期 sedan、Altima Coupe、Altima gen5 sedan、Cube、Armada gen2 可直接推进；Armada gen1 发现 2004/2005 与 2014/2015 外部尺寸不完全一致，本轮按实际尺寸拆段。Altima gen3 的 2002 原记录长度 191.5 与 2006/代际资料 192.3 不一致，本轮采用整代最大值并把参考车型覆盖 2002-2006。370Z NISMO 2020 Edmunds 明确为 170.5 / 73.6 / 51.8；Altima 1993/1997 同为 180.5 / 67.1 / 55.9；2006 Altima 为 192.3 / 70.4 / 57.9；Altima Coupe 2011/2013 为 180.9 / 70.7 / 55.9；2013/2018 Altima sedan 宽高一致但长度 2018 为 191.9；Cube 2009/2014 同为 156.7 / 66.7 / 65.0；Armada 2022/2024 同为 208.9 / 79.9 / 75.8。
Edmunds
+12
Edmunds
+12
Edmunds
+12

更新点

车型	操作	描述
Nissan 370Z	推进	NISMO 2015-2020 参考车型覆盖完整，改为可入库
Nissan Altima	值修改	gen3 sedan 长度由 191.5 调整为 192.3，参考车型覆盖 2002-2006
Nissan Altima	值修改	Coupe 长度由 182.5 调整为 180.9，参考车型覆盖 2008-2013
Nissan Altima	值修改	gen5 sedan 长度由 191.5 调整为 191.9，参考车型覆盖 2013-2018
Nissan Armada	拆出	gen1 拆为 2004-2005 与 2014-2015，避免不同尺寸压缩；2006-2013 仍待补强
Nissan Armada	推进	gen2 2017-2024 参考车型覆盖完整，改为可入库
Nissan Cube	推进	2009-2014 参考车型覆盖完整，改为可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan 370Z	Nissan	跑车	Coupe	NISMO	gen1 Z34	2015-2020	170.5	73.6	51.8	2015-2020 Nissan 370Z NISMO, Edmunds	性能版更长更宽	可入库
Nissan Altima	Nissan	三厢车	Sedan	Std.	gen1 compact	1993-1997	180.5	67.1	55.9	1993/1997 Nissan Altima SE, Edmunds		可入库
Nissan Altima	Nissan	三厢车	Sedan	Std.	gen3 large	2002-2006	192.3	70.4	57.9	2002-2006 Nissan Altima sedan, Edmunds / Autoevolution		可入库
Nissan Altima	Nissan	跑车	Coupe	Std.	gen4 coupe	2008-2013	180.9	70.7	55.9	2008/2011/2012/2013 Nissan Altima Coupe, Edmunds	低车顶Coupe	可入库
Nissan Altima	Nissan	三厢车	Sedan	Std.	gen5 large	2013-2018	191.9	72.0	57.9	2013/2017/2018 Nissan Altima sedan, Edmunds		可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2004-2005	206.9	78.8	78.7	2004/2005 Nissan Armada LE, Edmunds / Carspecs	高车身早期款	可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2006-2013	207.7	79.3	78.0	2014/2015 Nissan Armada, Edmunds		待补强: 2006-2013
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2014-2015	207.7	79.3	78.0	2014/2015 Nissan Armada SV, Edmunds		可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen2 full-size SUV	2017-2024	208.9	79.9	75.8	2017/2022/2024 Nissan Armada, Edmunds		可入库
Nissan Cube	Nissan	两厢车	Wagon	Std.	gen3 box wagon	2009-2014	156.7	66.7	65.0	2009/2014 Nissan Cube 1.8, Edmunds	方盒轮廓	可入库

下一步


--- Round 3 / 下一步 ---
本轮补强 Nissan SUV / CUV 记录：Juke、Kicks gen1、Rogue Sport 可推进；Rogue gen1 / gen2 / gen3 按已核对到的最大 trim 尺寸推进；Murano gen1 / gen3 仍因中间年份覆盖不足只推进部分。Kicks gen1 需要把高度从 62.4 调整到 63.4，因为 2024 SR/SV 高度高于 2019 基础记录；Rogue gen2 需要保留原 184.5 / 72.4 / 68.5 最大值，2020 SL 支持该最大值。
Edmunds
+4
Edmunds
+4
Edmunds
+4

更新点

车型	操作	描述
Nissan Juke	推进	2011-2017 尺寸一致口径，参考车型覆盖完整，改为可入库
Nissan Kicks	值修改	gen1 高度由 62.4 调整为 63.4，覆盖 2018-2024 最大高度
Nissan Rogue	推进	gen1 2008-2013 参考车型覆盖完整，改为可入库
Nissan Rogue	推进	Rogue Select 2014-2015 参考车型覆盖完整，改为可入库
Nissan Rogue	推进	gen2 2014-2020 采用 2020 SL 最大高度 68.5，参考车型覆盖完整
Nissan Rogue	推进	gen3 2021-2026 参考车型覆盖完整，改为可入库
Nissan Rogue Sport	推进	2017-2022 采用 SL/高配最大高度 63.4，参考车型覆盖完整
Nissan Murano	推进	gen4 2025-2026 已在上轮可入库，本轮不重复输出
Nissan Murano	暂缓	gen1 / gen2 / gen3 中间年份仍需继续补强，不整体改可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Juke	Nissan	越野车	CUV	Std.	gen1 subcompact CUV	2011-2017	162.4	69.5	61.8	2011-2017 Nissan Juke SL, Edmunds		可入库
Nissan Kicks	Nissan	越野车	SUV	Std.	gen1 subcompact SUV	2018-2024	169.1	69.3	63.4	2018/2019/2024 Nissan Kicks S/SR, Car and Driver / Edmunds	小型SUV	可入库
Nissan Rogue	Nissan	越野车	SUV	Std.	gen1 compact SUV	2008-2013	183.3	70.9	66.3	2008/2013 Nissan Rogue, Edmunds	早期车型	可入库
Nissan Rogue	Nissan	越野车	SUV	Std.	gen1 compact SUV Select	2014-2015	183.3	70.9	65.3	2014/2015 Nissan Rogue Select S, Edmunds	Rogue Select	可入库
Nissan Rogue	Nissan	越野车	SUV	Std.	gen2 compact SUV	2014-2020	184.5	72.4	68.5	2014/2015/2020 Nissan Rogue S/SV/SL, Edmunds	2020高度最大	可入库
Nissan Rogue	Nissan	越野车	SUV	Std.	gen3 compact SUV	2021-2026	183.0	72.4	66.5	2021/2025/2026 Nissan Rogue, Edmunds	当前车型	可入库
Nissan Rogue Sport	Nissan	越野车	SUV	Std.	gen1 compact SUV	2017-2022	172.8	72.3	63.4	2017/2020/2022 Nissan Rogue Sport SL, Cars.com / Edmunds		可入库

下一步


--- Round 4 / 下一步 ---
本轮补强了 Versa / Versa Note / Sentra / Xterra / Maxima 部分记录。需要改值的地方主要是：2012 Sentra 最大长度应按 SE-R / 高配取 180.1；2004 Xterra 高顶版本高度应取 73.9；2019 Versa Note 的 Edmunds 长度为 163.0，但 JD Power / C&D 口径仍为 163.7，本轮保留原 163.7 最大值并写入多来源。2012 Sentra、2012 Versa Hatchback、2012 Versa Sedan、2019 Versa Note、2004 Xterra、2008 Maxima 的关键尺寸分别由 Edmunds / KBB / JD Power 等来源交叉确认。
Edmunds
+7
Edmunds
+7
Kbb.com
+7

更新点

车型	操作	描述
Nissan Sentra	值修改	gen6 长度由 179.8 调整为 180.1，覆盖 2007-2012 最大 trim
Nissan Versa	推进	Hatchback 2007-2012 参考车型覆盖完整，改为可入库
Nissan Versa	推进	Sedan gen2 2012-2019 参考车型覆盖完整，改为可入库
Nissan Versa Note	稳定	保留 163.7 最大长度，Edmunds 2019 为 163.0，JD Power/C&D 为 163.7
Nissan Xterra	值修改	gen1 高度由 73.6 调整为 73.9，采用 2004 SE S/C 高顶口径
Nissan Maxima	值修改	gen6 长度由 193.5 调整为 194.4；2005-2007 仍待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen6 tall	2007-2012	180.1	70.5	59.5	2007/2012 Nissan Sentra sedan SE-R / SL, Edmunds / KBB	高车身	可入库
Nissan Versa	Nissan	两厢车	Hatchback	Std.	gen1 hatchback	2007-2012	169.1	66.7	60.4	2007/2012 Nissan Versa 5-door Hatchback, Edmunds / JD Power	两厢车	可入库
Nissan Versa	Nissan	三厢车	Sedan	Std.	gen2 sedan	2012-2019	175.4	66.7	59.6	2012/2019 Nissan Versa Sedan, Edmunds	三厢车	可入库
Nissan Versa Note	Nissan	两厢车	Hatchback	Std.	gen1 subcompact	2014-2019	163.7	66.7	60.5	2014/2019 Nissan Versa Note, Edmunds / C&D / JD Power		可入库
Nissan Xterra	Nissan	越野车	SUV	Std.	gen1 compact SUV	2000-2004	178.0	70.4	73.9	2000/2004 Nissan Xterra SE / SE S/C, Edmunds / KBB	高车顶越野SUV	可入库
Nissan Maxima	Nissan	三厢车	Sedan	Std.	gen6 large sedan	2004-2008	194.4	71.7	58.3	2004/2008 Nissan Maxima 3.5 SE / SL, Edmunds	车身增大	待补强: 2005-2007

下一步


--- Round 5 / 下一步 ---
本轮继续补强 Maxima 与 Murano。Maxima gen5 原高度 56.5 需要改为 56.3，因为 2003 Edmunds 为 191.5 / 70.3 / 56.3；Maxima gen6 2004-2008 可以覆盖完整，采用 2008 Edmunds 最大值 194.4 / 71.7 / 58.3。Murano gen1 2003 起始年尺寸与原值一致；gen2 2009 Edmunds 为 188.5 / 74.1 / 67.0，原记录 68.1 高度暂保留，但 2010-2014 还要继续核；Murano gen3 2015-2024 可按 192.8 / 75.4 / 67.8 推进，2018 与 2023 Edmunds 均支持该尺寸。
Edmunds
+5
Edmunds
+5
Edmunds
+5

更新点

车型	操作	描述
Nissan Maxima	值修改	gen5 高度由 56.5 调整为 56.3，2000-2003 覆盖完整
Nissan Maxima	推进	gen6 2004-2008 参考车型覆盖完整，改为可入库
Nissan Murano	推进	gen1 已补到 2003/2008 端点，2004-2007 仍待终核
Nissan Murano	推进	gen3 2015-2024 参考车型覆盖完整，改为可入库
Nissan Murano	暂缓	gen2 2009-2014 仍需核 2010-2014 高度最大值来源，暂不整体可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Maxima	Nissan	三厢车	Sedan	Std.	gen5 midsize	2000-2003	191.5	70.3	56.3	2000/2003 Nissan Maxima sedan, Edmunds	VQ时代	可入库
Nissan Maxima	Nissan	三厢车	Sedan	Std.	gen6 large sedan	2004-2008	194.4	71.7	58.3	2004/2008 Nissan Maxima 3.5 SE / SL, Edmunds	车身增大	可入库
Nissan Murano	Nissan	越野车	SUV	Std.	gen1 early	2003-2008	187.6	74.0	66.5	2003/2008 Nissan Murano SE / SL, Edmunds	早期SUV	待补强: 2004-2007
Nissan Murano	Nissan	越野车	SUV	Std.	gen3 mid	2015-2024	192.8	75.4	67.8	2015/2018/2023/2024 Nissan Murano S/SV, Edmunds	中期更长	可入库
Nissan Murano	Nissan	越野车	SUV	Std.	gen2 early	2009-2014	188.5	74.1	68.1	2009/2010/2014 Nissan Murano LE/SL, Edmunds	高度增加	待补强: 2011-2013高度最大值

下一步


--- Round 6 / 下一步 ---
本轮补强了 Murano gen1/gen2、Pathfinder gen1、Sentra gen4、Xterra gen2。关键变化：Murano gen2 原长度 188.5 不够覆盖 2014，需改为 189.9；高度 68.1 改为 68.0，因为 Edmunds 2014 LE 为 189.9 / 74.1 / 68.0。Pathfinder gen1 原 185.6 / 70.7 / 66.1 与美国 WD21 资料不符，Edmunds 1990/1992/1995 显示长度 171.9、宽 66.5，高度最高 66.7，因此本轮按 1987-1989 与 1990-1995 拆段，早期 1987-1989 仍待补强。Xterra gen2 2015 Edmunds / JD Power 均支持 178.7 / 72.8 / 74.9。
JD Power
+6
Edmunds
+6
Edmunds
+6

更新点

车型	操作	描述
Nissan Murano	推进	gen1 2003-2008 参考车型覆盖完整，改为可入库
Nissan Murano	值修改	gen2 长度 188.5→189.9，高度 68.1→68.0，覆盖 2009-2014
Nissan Pathfinder	值修改/拆出	WD21 原尺寸偏大，拆出 1987-1989 待补强与 1990-1995 可入库
Nissan Sentra	值修改	gen4 长度 171.1→171.0，1995-1999 sedan 覆盖完整
Nissan Xterra	推进	gen2 2005-2015 参考车型覆盖完整，改为可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Murano	Nissan	越野车	SUV	Std.	gen1 early	2003-2008	187.6	74.0	66.5	2003/2004/2008 Nissan Murano SL/SE, Edmunds	早期SUV	可入库
Nissan Murano	Nissan	越野车	SUV	Std.	gen2 early	2009-2014	189.9	74.1	68.0	2009/2010/2014 Nissan Murano LE, Edmunds	高度增加	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1987-1989	171.9	66.5	66.7	1990 Nissan Pathfinder, Edmunds	早期WD21待终核	待补强: 1987-1989
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1990-1995	171.9	66.5	66.7	1990/1992/1995 Nissan Pathfinder, Edmunds	WD21四门	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen4 compact	1995-1999	171.0	66.6	54.5	1995/1998/1999 Nissan Sentra sedan, Edmunds / Carspecs		可入库
Nissan Xterra	Nissan	越野车	SUV	Std.	gen2 compact SUV	2005-2015	178.7	72.8	74.9	2005/2015 Nissan Xterra PRO-4X / S, Edmunds / JD Power	第二代更宽更高	可入库

下一步


--- Round 7 / 下一步 ---
本轮补强 Sentra gen7、Versa gen3、Nissan Z 标准版 / NISMO、Armada gen1 中段。Sentra gen7 2014 与 2019 Edmunds 均为 182.1 / 69.3 / 58.9，可覆盖 2013-2019；Versa gen3 2020 Edmunds 为 177.0 / 68.5 / 57.3，但 Nissan USA 2025 官方高度最高到 57.7，因此 2020-2025 改用 177.0 / 68.5 / 57.7，2026 因美国市场停售暂拆出“未在美国销售/无数据”。Nissan Z 标准版 2023 Edmunds 为 172.4 / 72.6 / 51.8；Z NISMO 2025/2026 Edmunds 均为 173.2 / 73.6 / 51.8。Armada 2006 为 206.9 / 78.8 / 78.7；2010 和 2013 为 207.7 / 79.3 / 77.2，所以 gen1 中段需要继续按尺寸拆段。
Edmunds
+10
Edmunds
+10
Edmunds
+10

更新点

车型	操作	描述
Nissan Sentra	推进	gen7 2013-2019 参考车型覆盖完整，改为可入库
Nissan Versa	值修改/拆出	gen3 改为 2020-2025 可入库；2026 美国市场停售，单独拆出无数据
Nissan Z	推进	标准版 2023-2026 参考车型覆盖完整，改为可入库
Nissan Z	推进	NISMO 2024-2026 参考车型覆盖完整，改为可入库
Nissan Armada	拆出	2006 与 2010/2013 尺寸不同，拆为 2006 和 2010-2013；2007-2009 仍待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen7 large	2013-2019	182.1	69.3	58.9	2013/2014/2019 Nissan Sentra sedan, Edmunds		可入库
Nissan Versa	Nissan	三厢车	Sedan	Std.	gen3 sedan	2020-2025	177.0	68.5	57.7	2020/2025 Nissan Versa Sedan, Edmunds / Nissan USA	三厢车	可入库
Nissan Versa	Nissan	三厢车	Sedan	Std.	gen3 sedan	2026				Nissan Versa ended U.S. production before 2026 model year	三厢车	无数据: 2026美国市场未售
Nissan Z	Nissan	跑车	Coupe	Std.	gen7 compact sports coupe	2023-2026	172.4	72.6	51.8	2023/2024/2025/2026 Nissan Z Performance, Edmunds	标准Z车身	可入库
Nissan Z	Nissan	跑车	Coupe	NISMO	gen7 compact sports coupe	2024-2026	173.2	73.6	51.8	2024/2025/2026 Nissan Z NISMO, Edmunds	NISMO更长更宽	可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2006	206.9	78.8	78.7	2006 Nissan Armada SE/LE, Edmunds	高车身早期款	可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2007-2009	207.7	79.3	78.0	2010 Nissan Armada, Edmunds		待补强: 2007-2009
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2010-2013	207.7	79.3	78.0	2010/2013 Nissan Armada, Edmunds / Nissan News		可入库

下一步


--- Round 8 / 下一步 ---
本轮主要收尾 Armada 2007-2009，并核对 Pathfinder / Sentra B11 早期资料。Armada 2007 Edmunds 明确为 206.9 / 78.8 / 78.7；2009 Edmunds 为 207.7 / 79.3 / 77.2，所以不能继续把 2007-2009 压成一行。1987 Pathfinder 的 CarsGuide 资料显示 4610 mm / 1690 mm / 1680 mm，换算约 181.5 / 66.5 / 66.1，但这与前面 Edmunds 1990-1995 的美国口径不一致，因此 1987-1989 不直接改可入库，继续保留待补强。Sentra B11 已确认美国有 sedan / hatchback / wagon 等多结构，但早期各结构尺寸仍需要继续逐结构核对，暂不整体可入库。
维基百科
+3
Edmunds
+3
Edmunds
+3

更新点

车型	操作	描述
Nissan Armada	拆出	2007 与 2009 尺寸不同，2008 仍待补强
Nissan Pathfinder	稳定	1987 fallback 资料与 1990-1995 美国口径不一致，暂不改可入库
Nissan Sentra	稳定	B11 多结构已确认，但 sedan/coupe/wagon/hatchback 仍需逐结构尺寸核对

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2007	206.9	78.8	78.7	2007 Nissan Armada SE/LE, Edmunds	高车身早期款	可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2008	207.7	79.3	77.2	2009 Nissan Armada, Edmunds		待补强: 2008
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2009	207.7	79.3	77.2	2009 Nissan Armada, Edmunds		可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1987-1989	171.9	66.5	66.7	1990 Nissan Pathfinder, Edmunds; 1987 CarsGuide fallback shows non-US/alternate 181.5 x 66.5 x 66.1	早期WD21待终核	待补强: 1987-1989美国口径
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1982-1986	168.7	64.6	54.3	Nissan Sentra B11 sedan	早期sedan	待补强: 1982-1986 sedan逐年尺寸
Nissan Sentra	Nissan	跑车	Coupe	Std.	gen1 compact	1982-1986	166.5	65.6	52.2	Nissan Sentra B11 sport coupe	早期coupe	待补强: 1982-1986 coupe逐年尺寸
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1982-1986	172.2	64.6	54.9	Nissan Sentra B11 wagon / 4WD wagon	wagon最高	待补强: 1982-1986 wagon逐年尺寸
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1986	162.4	64.6	55.3	Nissan Sentra B11 hatchback	hatch最高	待补强: 1982-1986 hatchback逐年尺寸

下一步


--- Round 9 / 下一步 ---
本轮推进了 Nissan Sentra B11 与 Oldsmobile 88 早期段。Sentra B11 目前可确认 1986 hatchback coupe 为 170.2 / 63.8 / 53.5，1986 wagon 仍缺直接长宽高摘要，所以 wagon 暂不改可入库；B11 sedan 原记录缺少 1982-1986 全年份直接尺寸覆盖，本轮也继续保留待补强。Oldsmobile 88 gen1 需要按 1949-1950 与 1951-1953 拆段：1949-1950 基础 88 长 202.0，1951-1953 Super 88 长 204.0，不应继续混压为同一行。1949/1950/1951/1952/1953 的早期 Oldsmobile 尺寸分别由 Over-Drive fact sheet、Automobile-Catalog 和 Conceptcarz 交叉确认。
汽车目录
+4
Over-Drive Magazine
+4
Over-Drive Magazine
+4

更新点

车型	操作	描述
Nissan Sentra	值修改	B11 Hatchback 长度由 162.4 调整为 170.2，高度由 55.3 调整为 53.5；但 1982-1985 仍待补强
Nissan Sentra	稳定	B11 Sedan / Coupe / Wagon 仍缺完整 1982-1986 年份与结构覆盖，暂不改可入库
Oldsmobile 88	拆出	gen1 1949-1953 拆为 1949-1950 与 1951-1953，避免 202.0 与 204.0 混压
Oldsmobile 88	值修改	gen2 1954-1956 长宽高改为 205.3 / 78.6 / 61.0，参考车型覆盖 1954/1955/1956

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1982-1986	168.7	64.6	54.3	Nissan Sentra B11 sedan	早期sedan	待补强: 1982-1986 sedan逐年尺寸
Nissan Sentra	Nissan	跑车	Coupe	Std.	gen1 compact	1982-1986	166.5	65.6	52.2	Nissan Sentra B11 sport coupe	早期coupe	待补强: 1982-1986 coupe逐年尺寸
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1982-1986	172.2	64.6	54.9	1982/1986 Nissan Sentra Wagon, Automobile-Catalog	最高wagon待核	待补强: 1982-1986 wagon完整尺寸
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1986	170.2	63.8	53.5	1986 Nissan Sentra Hatchback Coupe SE, Automobile-Catalog	三门hatch/coupe低车顶	待补强: 1982-1985 hatchback
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen1 full-size	1949-1950	202.0	75.2	64.1	1949/1950 Oldsmobile 88, Over-Drive / Automobile-Catalog	Rocket 88早期	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen1 full-size	1949-1950	202.0	75.2	64.1	1949/1950 Oldsmobile 88 Club Coupe / Holiday Coupe, Over-Drive / Automobile-Catalog	Rocket 88早期	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen1 full-size	1951-1953	204.0	76.0	63.7	1951/1952/1953 Oldsmobile Super 88 Sedan, Over-Drive / Automobile-Catalog	Rocket 88早期	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen1 full-size	1951-1953	204.0	76.0	63.7	1951/1952/1953 Oldsmobile Super 88 Coupe, Automobile-Catalog / Conceptcarz	Rocket 88早期	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen2 full-size	1954-1956	205.3	78.6	61.0	1954/1955/1956 Oldsmobile Super 88 Sedan, Automobile-Catalog	宽体full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen2 full-size	1954-1956	205.3	78.6	61.0	1954/1955/1956 Oldsmobile Super 88 Coupe, Automobile-Catalog	宽体full-size	可入库

下一步


--- Round 10 / 下一步 ---
本轮补强 Oldsmobile 88 的 1961-1976 段。1961-1964 不能继续用同一组 215.0 / 78.6 / 55.0 混压：1961 brochure 给出 Dynamic 88 长 212.0、宽 77.2；1964 Automobile-Catalog 给出 215.3、78.0。1965-1970 段也不应继续用 220.0 / 79.7 / 54.4 混压：1968 为 217.8 / 80.0，1969 coupe 为 218.6 / 80.0 / 54.1。1971-1976 暂只确认该代 1974 达到 226.9 in 最大长度，wagon 使用更长 127 in 轴距，sedan/coupe 与 wagon 后续应拆开核对。
维基百科
+4
Over-Drive Magazine
+4
汽车目录
+4

更新点

车型	操作	描述
Oldsmobile 88	拆出	gen5 1961-1964 拆为 1961 已核、1962-1963 待补强、1964 已核
Oldsmobile 88	值修改/拆出	gen6 1965-1970 拆出 1968 与 1969 已核，1965-1967/1970 仍待补强
Oldsmobile 88	暂缓	gen7 1971-1976 sedan/coupe/wagon 不能混压，后续需继续拆结构核对

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1961	212.0	77.2	55.8	1961 Oldsmobile Dynamic 88 Sedan, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1961	212.0	77.2	55.8	1961 Oldsmobile Dynamic 88 Holiday Coupe, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1961	212.0	77.2	55.8	1961 Oldsmobile Dynamic 88 wagon, Oldsmobile brochure	full-size低车身	待补强: wagon高度/1962-1963
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1962-1963	215.0	78.0	55.0	1964 Oldsmobile Dynamic 88 fallback	中间年待核	待补强: 1962-1963
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1962-1963	215.0	78.0	55.0	1962 Oldsmobile Dynamic 88 Holiday Coupe partial / 1964 fallback	中间年待核	待补强: 1962-1963完整尺寸
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1962-1963	215.0	78.0	55.0	1964 Oldsmobile Dynamic 88 wagon fallback	中间年待核	待补强: 1962-1963 wagon完整尺寸
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1964	215.3	78.0	55.0	1964 Oldsmobile Dynamic 88 Sedan, Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1964	215.3	78.0	55.0	1964 Oldsmobile Dynamic 88 Holiday Coupe, Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1964	215.3	78.0	55.0	1964 Oldsmobile Dynamic 88 Station Wagon, Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1965-1967	217.8	80.0	55.5	1966 Oldsmobile Delta 88 Celebrity Sedan / 1968 fallback	B-body长车身	待补强: 1965/1967
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1965-1967	217.8	80.0	55.5	1966 Oldsmobile Delta 88 / 1968 fallback	B-body长车身	待补强: 1965/1967 coupe
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1967	217.8	80.0	55.5	1965 Oldsmobile full-line brochure / 1968 fallback	B-body长车身	待补强: wagon逐年尺寸
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1968	217.8	80.0	55.5	1968 Oldsmobile Delta 88 Holiday Sedan, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1968-1969	218.6	80.0	54.1	1968/1969 Oldsmobile Delta 88 Holiday Coupe, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1969-1970	218.6	80.0	54.1	1969 Oldsmobile Delta 88 / 1970 fallback	B-body长车身	待补强: 1970 sedan
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1968-1970	218.6	80.0	54.1	1968/1969 Oldsmobile 88 fallback	B-body长车身	待补强: wagon 1968-1970
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1971-1976	226.9	79.8	53.6	1971-1976 Oldsmobile Delta 88 generation note; 1974 max length confirmed	大型full-size	待补强: sedan 1971-1976逐年
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1971-1976	226.9	79.8	53.6	1971-1976 Oldsmobile Delta 88 coupe generation note; 1974 max length confirmed	大型full-size	待补强: coupe 1971-1976逐年
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size	1971-1976	226.9	79.8	53.6	1971-1976 Oldsmobile Custom Cruiser wagon note, longer 127 in wheelbase	长轴wagon	待补强: wagon需单独核对

下一步


--- Round 11 / 下一步 ---
本轮继续补强 Oldsmobile 88 gen7（1971-1976）段。该代 sedan/coupe 与 Custom Cruiser wagon 不能合并：1971 Delta 88 coupe/sedan 为 220.2 in 长、79.5 in 宽、约 53.4 in 高；1973 coupe 为 225.0 / 79.5 / 53.4；1975 sedan/coupe 长度达到 226.9；而 1973 Custom Cruiser wagon 为 228.3 / 79.5，1976 wagon 为 231.0 / 80.0，且使用 127 in 长轴距平台。Oldsmobile 88 第七代 1971 年换代并放大，1974 达到最大长度，Custom Cruiser wagon 使用更长 127 in 轴距，这也支持 wagon 单独拆出。
汽车目录
+4
维基百科
+4
汽车目录
+4

更新点

车型	操作	描述
Oldsmobile 88	拆出	gen7 sedan/coupe 不再按 1971-1976 混压，拆成 1971、1973、1975-1976 等待闭合段
Oldsmobile 88	拆出	Custom Cruiser wagon 长轴距、车身更长，独立为 wagon 行
Oldsmobile 88	推进	1971 coupe / sedan 与 1973 coupe、1975 sedan/coupe、1976 wagon 有明确尺寸来源
Oldsmobile 88	暂缓	1972/1974/1976 sedan/coupe 与 1971/1972/1974/1975 wagon 仍需继续补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1971	220.2	79.5	53.4	1971 Oldsmobile Delta 88 Town Sedan / Royale Sedan, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1971	220.2	79.5	53.4	1971 Oldsmobile Delta 88 Royale Hardtop Coupe, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1972	225.0	79.5	53.4	1973 Oldsmobile Delta 88 fallback	大型full-size	待补强: 1972 sedan
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1972-1973	225.0	79.5	53.4	1973 Oldsmobile Delta 88 Hardtop Coupe, Automobile-Catalog	大型full-size	待补强: 1972 coupe
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1973	225.0	79.5	53.4	1973 Oldsmobile Delta 88 Sedan fallback / Coupe confirmed, Automobile-Catalog	大型full-size	待补强: 1973 sedan
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1974	226.9	79.8	53.6	1975 Oldsmobile Delta Eighty-Eight Royale Town Sedan fallback	大型full-size	待补强: 1974 sedan
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1974	226.9	79.8	53.6	1975 Oldsmobile Delta Eighty-Eight Royale Coupe fallback	大型full-size	待补强: 1974 coupe
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1975-1976	226.9	79.8	53.6	1975 Oldsmobile Delta Eighty-Eight Royale Town Sedan / HardTop Sedan, Conceptcarz	大型full-size	待补强: 1976 sedan
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1975-1976	226.9	79.8	53.6	1975 Oldsmobile Delta Eighty-Eight Royale Coupe, Conceptcarz	大型full-size	待补强: 1976 coupe
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1971-1972	228.3	79.5	53.6	1973 Oldsmobile Custom Cruiser fallback; 1971-1972 wagon待核	长轴wagon	待补强: 1971-1972 wagon
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1973	228.3	79.5	53.6	1973 Oldsmobile Custom Cruiser Wagon, Automobile-Catalog	长轴wagon	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1974-1975	231.0	80.0	53.6	1976 Oldsmobile Custom Cruiser fallback; 1974-1975 wagon待核	长轴wagon	待补强: 1974-1975 wagon
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1976	231.0	80.0	53.6	1976 Oldsmobile Custom Cruiser Wagon, Automobile-Catalog	长轴wagon	可入库

下一步


--- Round 12 / 下一步 ---
本轮继续补 Oldsmobile 88 gen5 / gen6 / gen7 的缺口。1964 Conceptcarz / Automobile-Catalog 均支持 215.3 in 长；1964 Automobile-Catalog 明确宽 78.0、高 55.9，所以 1964 sedan/coupe/wagon 高度由 55.0 修正为 55.9。1974 sedan/coupe 已可入库：Automobile-Catalog 显示 1974 Delta 88 hardtop sedan 为 226.9 / 79.5 / 53.6，1974 hardtop coupe 为 226.9 / 79.5 / 53.4。1975 Custom Cruiser wagon 长度为 231.2、宽 79.5，1971-1976 Custom Cruiser 使用 127 in 长轴距、1974-1976 长度超过 19 ft，因此 wagon 继续独立，不与 sedan/coupe 合并。
维基百科
+5
conceptcarz.com
+5
汽车目录
+5

更新点

车型	操作	描述
Oldsmobile 88	值修改	gen5 1964 高度由 55.0 修正为 55.9
Oldsmobile 88	推进	gen7 1974 sedan / coupe 已核实，可入库
Oldsmobile 88	值修改/推进	gen7 wagon 1975 长度由 231.0 调整为 231.2，可入库
Oldsmobile 88	稳定	1971-1976 Custom Cruiser wagon 继续单独拆出，不能与 sedan/coupe 合并

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1964	215.3	78.0	55.9	1964 Oldsmobile Dynamic 88 Sedan, Conceptcarz / Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1964	215.3	78.0	55.9	1964 Oldsmobile Dynamic 88 Holiday Coupe, Conceptcarz / Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1964	215.3	78.0	55.9	1964 Oldsmobile Dynamic 88 Station Wagon, Conceptcarz / Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1974	226.9	79.5	53.6	1974 Oldsmobile Delta 88 Hardtop Sedan, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1974	226.9	79.5	53.4	1974 Oldsmobile Delta 88 Royale Hardtop Coupe, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1974	231.2	79.5	53.6	1975 Oldsmobile Custom Cruiser fallback; 1974 wagon待核	长轴wagon	待补强: 1974 wagon
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1975	231.2	79.5	53.6	1975 Oldsmobile Custom Cruiser 400 V8 Wagon, Automobile-Catalog	长轴wagon	可入库

下一步


--- Round 13 / 下一步 ---
本轮继续补强 Oldsmobile 88 gen7 末段，并修正 1976 sedan/coupe 不能与 1975 混压的问题。1976 Delta 88 Royale Town Sedan 为 226.7 in 长、80.0 in 宽；1976 Royale Hardtop Coupe 同样为 226.7 / 80.0 / 53.4，因此 1975 与 1976 的宽度不同，不能压成 1975-1976 同一行。1975 sedan/coupe 仍按 226.9 / 79.8 / 53.6 处理。
汽车目录
+2
汽车目录
+2

更新点

车型	操作	描述
Oldsmobile 88	拆出	gen7 sedan 1975 与 1976 尺寸不同，拆成年份单行
Oldsmobile 88	拆出	gen7 coupe 1975 与 1976 尺寸不同，拆成年份单行
Oldsmobile 88	值修改	1976 sedan/coupe 宽度改为 80.0，长度改为 226.7
Oldsmobile 88	推进	1976 sedan/coupe 已核实，可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1975	226.9	79.8	53.6	1975 Oldsmobile Delta Eighty-Eight Royale Town Sedan / Hardtop Sedan, Automobile-Catalog / Conceptcarz	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1975	226.9	79.8	53.6	1975 Oldsmobile Delta Eighty-Eight Royale Coupe, Automobile-Catalog / Conceptcarz	大型full-size	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1976	226.7	80.0	53.4	1976 Oldsmobile Delta 88 Royale Town Sedan, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1976	226.7	80.0	53.4	1976 Oldsmobile Delta 88 Royale Hardtop Coupe, Automobile-Catalog	大型full-size	可入库

下一步


--- Round 14 / 下一步 ---
本轮继续补强 Oldsmobile 88 gen7 的 1972、1973 sedan/coupe 与 1974 wagon。1972 sedan / coupe 不能沿用 1973 的 225.0：1972 Delta 88 Town Sedan、Hardtop Sedan、Hardtop Coupe 资料均显示长度 222.1、宽 79.5，高度 sedan 53.6、coupe 53.4。1973 coupe 为 225.0 / 79.5 / 53.4。1974 Custom Cruiser wagon 明确为 231.2 / 79.5，因此 1974 wagon 可入库。
汽车目录
+3
汽车目录
+3
汽车目录
+3

更新点

车型	操作	描述
Oldsmobile 88	值修改	1972 sedan/coupe 从 225.0 fallback 改为 222.1 / 79.5
Oldsmobile 88	推进	1972 sedan/coupe 已核实，可入库
Oldsmobile 88	推进	1973 coupe 已核实，可入库
Oldsmobile 88	推进	1974 wagon 已核实，可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1972	222.1	79.5	53.6	1972 Oldsmobile Delta 88 Hardtop Sedan / Town Sedan, Automobile-Catalog / Oldsmobile brochure	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1972	222.1	79.5	53.4	1972 Oldsmobile Delta 88 Royale Hardtop Coupe, Automobile-Catalog / Oldsmobile brochure	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1973	225.0	79.5	53.4	1973 Oldsmobile Delta 88 Hardtop Coupe, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1974	231.2	79.5	53.6	1974 Oldsmobile Custom Cruiser Wagon, Automobile-Catalog	长轴wagon	可入库

下一步


--- Round 15 / 下一步 ---
本轮继续补强 Oldsmobile 88 的 1963、1970 与 1973 sedan 缺口。1963 Holiday Coupe 可确认 214.4 / 77.9，不能继续沿用 1964 的 215.3 / 78.0；1970 Delta 88 convertible 资料显示 219.1 / 79.9 / 54.7，因此 1970 sedan/coupe/wagon 暂不能和 1969 直接压缩；1973 sedan 通过 1973 Oldsmobile full-size brochure 口径补强，长度 226.8、宽 79.8、高 53.2，与 1973 coupe 的 225.0 / 79.5 / 53.4 不同，需要单独保留。
汽车目录
+2
汽车目录
+2

更新点

车型	操作	描述
Oldsmobile 88	拆出/值修改	gen5 1963 coupe 从 1962-1963 fallback 拆出，改为 214.4 / 77.9
Oldsmobile 88	稳定	gen5 1962 仍缺完整 sedan/coupe/wagon 逐结构尺寸
Oldsmobile 88	拆出/值修改	gen6 1970 不能和 1969 混压，先按 1970 convertible/大车身口径单独待补强
Oldsmobile 88	推进	gen7 1973 sedan 已核实，改为可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1962	215.0	78.0	55.0	1964 Oldsmobile Dynamic 88 fallback	中间年待核	待补强: 1962 coupe完整尺寸
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1963	214.4	77.9	55.0	1963 Oldsmobile Dynamic 88 Holiday Coupe, Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1970	219.1	79.9	54.7	1970 Oldsmobile Delta 88 convertible fallback, Automobile-Catalog	B-body长车身	待补强: 1970 sedan
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1970	219.1	79.9	54.7	1970 Oldsmobile Delta 88 convertible fallback, Automobile-Catalog	B-body长车身	待补强: 1970 coupe
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1970	219.1	79.9	54.7	1970 Oldsmobile Delta 88 convertible fallback; wagon待核	B-body长车身	待补强: 1970 wagon
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1973	226.8	79.8	53.2	1973 Oldsmobile Full Size brochure, Delta 88 sedan	大型full-size	可入库

下一步


--- Round 16 / 下一步 ---
本轮继续补强 Oldsmobile 88 gen5 / gen6 缺口。1962 Oldsmobile full-line brochure 明确 Dynamic 88 / Super 88 轴距 123 in、总长 213.9 in、总宽 77.9 in，并列出不同结构高度；1963 Automobile-Catalog 显示 sedan / coupe / wagon 均为 214.4 / 77.9，且 wagon 资料明确为 214.4 / 77.9。1966 Delta 88 Celebrity Sedan 来源显示 217.0 / 80.0 / 55.5，因此 1965-1967 段暂不再用 1968 fallback 混压，先把 1966 单年推进。
carfolio.com
+3
Over-Drive Magazine
+3
汽车目录
+3

更新点

车型	操作	描述
Oldsmobile 88	值修改/推进	gen5 1962 sedan/coupe/wagon 改为 213.9 / 77.9，并按结构高度区分
Oldsmobile 88	推进	gen5 1963 sedan/coupe/wagon 已核实，可入库
Oldsmobile 88	拆出/推进	gen6 1966 sedan 可入库；1965/1967 仍待补强
Oldsmobile 88	稳定	1965-1967 wagon 仍不能用 sedan/coupe 直接代表，继续待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1962	213.9	77.9	55.8	1962 Oldsmobile Dynamic 88 Celebrity Sedan / Holiday Sedan, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1962	213.9	77.9	55.8	1962 Oldsmobile Dynamic 88 Holiday Coupe, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1962	213.9	77.9	56.6	1962 Oldsmobile Dynamic 88 Fiesta Station Wagon, Oldsmobile brochure	高顶wagon	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1963	214.4	77.9	56.3	1963 Oldsmobile Dynamic 88 Celebrity Sedan / Super 88 Celebrity Sedan, Automobile-Catalog / Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1963	214.4	77.9	55.0	1963 Oldsmobile Dynamic 88 Holiday Coupe, Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1963	214.4	77.9	56.3	1963 Oldsmobile Super 88 Fiesta Wagon, Automobile-Catalog	高顶wagon	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1966	217.0	80.0	55.5	1966 Oldsmobile Delta 88 Celebrity Sedan, Carfolio / Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1966	217.0	80.0	55.5	1966 Oldsmobile Delta 88 Holiday Coupe fallback; sedan dimensions confirmed	B-body长车身	待补强: 1966 coupe
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1967	217.8	80.0	55.5	1965 Oldsmobile full-line brochure / 1968 fallback	B-body长车身	待补强: wagon 1965-1967逐年

下一步


--- Round 17 / 下一步 ---
本轮继续补强 Oldsmobile 88 gen6 缺口。1970 已确认 Delta 88 Convertible 为 219.1 / 79.9 / 54.7，Holiday Sedan 年款页面也能对应 1970 Delta 88 6th-gen；1967 Conceptcarz 页面能确认 1967 Delta Eighty-Eight 属于 1965-1970 生产系列，但当前搜索结果没有直接给完整长宽高，所以 1967 仍不改可入库。1973 coupe 维持 225.0 / 79.5 / 53.4；1971 coupe 维持 220.2 / 79.5 / 53.4。
汽车目录
+4
汽车目录
+4
汽车目录
+4

更新点

车型	操作	描述
Oldsmobile 88	推进	1970 convertible 尺寸已确认，但 sedan/coupe/wagon 仍不能直接替代
Oldsmobile 88	稳定	1967 Delta Eighty-Eight 只确认系列归属，缺完整长宽高，继续待补强
Oldsmobile 88	稳定	1971 / 1973 coupe 已有明确来源，保持可入库

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1965	217.0	80.0	55.5	1966 Oldsmobile Delta 88 Celebrity Sedan fallback	B-body长车身	待补强: 1965 sedan
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1965	217.0	80.0	55.5	1966 Oldsmobile Delta 88 Holiday Coupe fallback	B-body长车身	待补强: 1965 coupe
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1967	217.8	80.0	55.5	1967 Oldsmobile Delta Eighty-Eight series confirmed, Conceptcarz; 1968 fallback	B-body长车身	待补强: 1967 sedan完整尺寸
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1967	217.8	80.0	55.5	1967 Oldsmobile Delta Eighty-Eight series confirmed, Conceptcarz; 1968 fallback	B-body长车身	待补强: 1967 coupe完整尺寸
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1970	219.1	79.9	54.7	1970 Oldsmobile Delta 88 Holiday Sedan page / Convertible dimensions, Automobile-Catalog	B-body长车身	待补强: 1970 sedan需直接页
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1970	219.1	79.9	54.7	1970 Oldsmobile Delta 88 Convertible dimensions fallback, Automobile-Catalog	B-body长车身	待补强: 1970 coupe需直接页
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1970	219.1	79.9	54.7	1970 Oldsmobile Delta 88 Convertible fallback; wagon待核	B-body长车身	待补强: 1970 wagon

下一步


--- Round 18 / 下一步 ---
本轮继续补强 Oldsmobile 88 gen6。1967 sedan/coupe 已能分别按 Town Sedan 与 Custom Holiday Coupe 直接入库：1967 Town Sedan 为 217.0 / 80.0 / 55.5，1967 Custom Holiday Coupe 为 217.0 / 80.0 / 54.1。1970 sedan/coupe 也能直接入库：1970 Town Sedan 为 219.1 / 79.9 / 55.5，1970 Royale Holiday Coupe 为 219.1 / 79.9 / 54.7。1965 convertible 可确认为 216.9 / 80.0，但 sedan/coupe 仍需直接页，暂不改可入库。
汽车目录
+4
汽车目录
+4
汽车目录
+4

更新点

车型	操作	描述
Oldsmobile 88	推进	1967 sedan/coupe 已核实，可入库
Oldsmobile 88	值修改	1967 coupe 高度由 55.5 调整为 54.1
Oldsmobile 88	推进	1970 sedan/coupe 已核实，可入库
Oldsmobile 88	值修改	1970 sedan 高度由 54.7 调整为 55.5
Oldsmobile 88	稳定	1965 sedan/coupe 与 1965-1970 wagon 仍需直接结构页核对

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1967	217.0	80.0	55.5	1967 Oldsmobile Delmont 88 / Delta 88 Town Sedan, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1967	217.0	80.0	54.1	1967 Oldsmobile Delta 88 Custom Holiday Coupe, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1970	219.1	79.9	55.5	1970 Oldsmobile Delta 88 Town Sedan, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1970	219.1	79.9	54.7	1970 Oldsmobile Delta 88 Royale Holiday Coupe, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1965	216.9	80.0	55.5	1965 Oldsmobile Dynamic 88 Convertible fallback, Automobile-Catalog	B-body长车身	待补强: 1965 sedan直接页
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1965	216.9	80.0	54.7	1965 Oldsmobile Dynamic 88 Convertible fallback, Automobile-Catalog	B-body长车身	待补强: 1965 coupe直接页
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1970	217.8	80.0	55.5	1965 Oldsmobile full-line brochure / 1968 fallback	B-body长车身	待补强: wagon 1965-1970逐年

下一步


--- Round 19 / 下一步 ---
本轮补强了 Nissan Sentra B11 末段和 Oldsmobile 88 的 1965 直接页。Sentra 1985/1986 Hatchback Coupe 可入库为 170.2 / 63.8 / 53.5；1986 Wagon 实测口径应为 165.6 / 63.8 / 53.3，不能继续沿用 172.2 / 64.6 / 54.9。Oldsmobile 1965 brochure 支持 full-size 88 的 123 in 轴距、216.9 in 长、80 in 宽；1965 Dynamic 88 Celebrity Sedan / Holiday Coupe 直接页已找到，但搜索摘要未展开高度，暂按 brochure/同系口径推进为“待终核高度直接页”。
汽车目录
+4
汽车目录
+4
汽车目录
+4

更新点

车型	操作	描述
Nissan Sentra	拆出/推进	B11 Hatchback 拆为 1982-1984 待补强、1985-1986 可入库
Nissan Sentra	值修改/拆出	B11 Wagon 1986 改为 165.6 / 63.8 / 53.3，1982-1985 仍待补强
Nissan Sentra	稳定	B11 Sedan / Coupe 1982-1986 仍缺完整结构直接页，继续待补强
Oldsmobile 88	推进	1965 sedan/coupe 直接页已定位，长宽可确认，仍需高度终核
Oldsmobile 88	稳定	1965-1970 wagon 仍缺逐年 wagon 直接页，继续待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1984	170.2	63.8	53.5	1985 Nissan Sentra Hatchback Coupe fallback, Automobile-Catalog	三门hatch/coupe低车顶	待补强: 1982-1984 hatchback
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1985-1986	170.2	63.8	53.5	1985/1986 Nissan Sentra Hatchback Coupe SE, Automobile-Catalog	三门hatch/coupe低车顶	可入库
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1982-1985	172.2	64.6	54.9	1982 Nissan Sentra Wagon / 1986 wagon revised source pending	最高wagon待核	待补强: 1982-1985 wagon完整尺寸
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1986	165.6	63.8	53.3	1986 Nissan Sentra Wagon Deluxe, Automobile-Catalog	wagon低顶	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1965	216.9	80.0	55.5	1965 Oldsmobile Dynamic 88 Celebrity Sedan, Automobile-Catalog / 1965 Oldsmobile full-line brochure	B-body长车身	待补强: 1965 sedan高度直接页终核
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1965	216.9	80.0	54.7	1965 Oldsmobile Dynamic 88 Holiday Coupe, Automobile-Catalog / 1965 Oldsmobile full-line brochure	B-body长车身	待补强: 1965 coupe高度直接页终核
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1970	217.8	80.0	55.5	1965 Oldsmobile full-line brochure / 1968 fallback	B-body长车身	待补强: wagon 1965-1970逐年

下一步


--- Round 20 / 下一步 ---
本轮继续补强 Nissan Sentra B11 / Pathfinder 早期段，并推进 Oldsmobile 88 gen6 的部分缺口。Sentra 1982 2-door sedan / 1982 MPG sedan 可按 167.3 / 63.7 / 54.5 入库；1983 wagon 为 167.3 / 63.7 / 53.3；1984 hatchback coupe 为 172.3 / 63.8 / 53.5。1987 Pathfinder 北美 Automobile-Catalog 页面高度为 66.1，CarGurus 美国页面给 171 / 66 / 65，因此本轮不继续沿用之前 181.5 的澳洲 CarsGuide 口径，改用美国口径但 1988-1989 仍待补强。Oldsmobile 1965 Dynamic 88 convertible 页面确认 216.9 / 80.0，1966 convertible 页面确认 217.0 / 80.0；1969 Town Sedan 为 218.6 / 80.0 / 54.7。
carfolio.com
+7
汽车目录
+7
汽车目录
+7

更新点

车型	操作	描述
Nissan Sentra	推进	B11 Sedan 1982 已核实；1983-1986 sedan 仍需补强
Nissan Sentra	推进	B11 Wagon 1983 已核实；1982/1984-1985 wagon 仍需补强
Nissan Sentra	推进	B11 Hatchback 1984 已核实，可与 1985-1986 按同尺寸区间推进
Nissan Pathfinder	值修改/推进	1987 改回美国 WD21 口径，1988-1989 继续待补强
Oldsmobile 88	推进	1969 sedan 已核实，可入库
Oldsmobile 88	稳定	1965/1966 wagon 仍缺 wagon 直接页，继续待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1982	167.3	63.7	54.5	1982 Nissan Sentra 2-Door Standard / MPG, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1986	168.7	64.6	54.3	Nissan Sentra B11 sedan	早期sedan	待补强: 1983-1986 sedan逐年尺寸
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1982	167.3	63.7	53.3	1983 Nissan Sentra Wagon Deluxe fallback	早期wagon	待补强: 1982 wagon直接页
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1983	167.3	63.7	53.3	1983 Nissan Sentra Wagon Deluxe, Automobile-Catalog	早期wagon	可入库
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	167.3	63.7	53.3	1983/1986 Nissan Sentra Wagon fallback	早期wagon	待补强: 1984-1985 wagon直接页
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1983	172.3	63.8	53.5	1984 Nissan Sentra Hatchback Coupe fallback	三门hatch/coupe低车顶	待补强: 1982-1983 hatchback
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1984-1986	172.3	63.8	53.5	1984/1985/1986 Nissan Sentra Hatchback Coupe, Automobile-Catalog	三门hatch/coupe低车顶	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1987	171.0	66.0	66.1	1987 Nissan Pathfinder 4x4 SE-V6, Automobile-Catalog / CarGurus	早期WD21两门	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1988-1989	171.0	66.0	66.1	1987 Nissan Pathfinder US reference fallback	早期WD21两门	待补强: 1988-1989美国口径
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1969	218.6	80.0	54.7	1969 Oldsmobile Delta 88 Town Sedan, Carfolio	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1966	217.0	80.0	55.5	1965/1966 Oldsmobile Dynamic 88 convertible/sedan reference; wagon待核	B-body长车身	待补强: 1965-1966 wagon直接页
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1967-1970	219.1	80.0	55.5	1969 Town Sedan / 1970 Delta 88 reference; wagon待核	B-body长车身	待补强: 1967-1970 wagon直接页

下一步


--- Round 21 / 下一步 ---
本轮继续补强 Nissan Sentra B11 与 Nissan Pathfinder 早期段。Sentra 1984-1986 的 Hatchback Coupe 已有直接尺寸页，保持 172.3 / 63.8 / 53.5；1985 2-door sedan 直接页显示 165.3 / 63.8 / 54.5，与原 168.7 不同，所以 sedan 不能把 1983-1986 继续合并。1987 Pathfinder 已按美国口径改为 171.0 / 66.0 / 66.1；1988-1989 仍缺直接美国页面，继续待补强。Oldsmobile 1963 wagon 来源确认 214.4 / 77.9，可支持前面 1963 wagon 可入库记录。
汽车目录
+2
汽车目录
+2

更新点

车型	操作	描述
Nissan Sentra	拆出/值修改	1985 sedan 不能沿用 168.7，改为 165.3 / 63.8 / 54.5
Nissan Sentra	稳定	1984-1986 Hatchback 已有直接来源，保持可入库
Nissan Pathfinder	稳定	1988-1989 仍缺美国直接页，继续待补强
Oldsmobile 88	稳定	1963 wagon 214.4 / 77.9 来源可支持已入库记录

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1984	168.7	64.6	54.5	1985 Nissan Sentra 2-Door Deluxe fallback; 1983-1984 sedan待核	早期sedan	待补强: 1983-1984 sedan直接页
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1985	165.3	63.8	54.5	1985 Nissan Sentra 2-Door Deluxe, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1986	168.7	64.6	54.5	1987 Nissan Sentra 2-Door Sedan E fallback; 1986 sedan待核	早期sedan	待补强: 1986 sedan直接页
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1984-1986	172.3	63.8	53.5	1984/1985/1986 Nissan Sentra Hatchback Coupe, Automobile-Catalog	三门hatch/coupe低车顶	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1988-1989	171.0	66.0	66.1	1987 Nissan Pathfinder US reference fallback	早期WD21两门	待补强: 1988-1989美国口径
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1963	214.4	77.9	56.3	1963 Oldsmobile Super 88 Fiesta Wagon, Automobile-Catalog	高顶wagon	可入库

下一步


--- Round 22 / 下一步 ---
本轮继续补强 Nissan Sentra B11 / Pathfinder 早期段，并修正 Oldsmobile 88 wagon 口径。1986 Sentra 2-Door Standard 有直接页面，因此 1986 sedan 可推进为可入库；1988-1989 Pathfinder 仍未找到直接美国尺寸页，继续待补强。Oldsmobile 88 gen6 的 wagon 段需要注意：1965 年后 full-size Dynamic 88 wagon 停止，Oldsmobile 的长款 wagon 主要转为 Vista Cruiser / Custom Cruiser 口径，因此不能继续把 1965-1970 wagon 当作 Oldsmobile 88 wagon 直接入库；本轮先改为“无数据/需确认是否仍属88车系”。1968 Vista Cruiser 资料显示 217.5 / 76.7，与 88 sedan/coupe 的 80.0 宽度不同，也进一步说明 wagon 不应直接沿用 88 sedan/coupe 尺寸。
汽车目录
+2
汽车目录
+2

更新点

车型	操作	描述
Nissan Sentra	推进	1986 sedan 找到直接页，可入库
Nissan Sentra	稳定	1983-1984 sedan、1982-1983 hatchback、1982/1984-1985 wagon 仍待补强
Nissan Pathfinder	稳定	1988-1989 仍缺美国直接页，继续待补强
Oldsmobile 88	值修改	gen6 wagon 不再沿用 sedan/coupe 尺寸；1965 后 full-size 88 wagon 口径需确认

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1986	168.7	64.6	54.5	1986 Nissan Sentra 2-Door Standard, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1984	168.7	64.6	54.5	1985/1986 Nissan Sentra 2-Door sedan fallback; 1983-1984 sedan待核	早期sedan	待补强: 1983-1984 sedan直接页
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1983	172.3	63.8	53.5	1984 Nissan Sentra Hatchback Coupe fallback	三门hatch/coupe低车顶	待补强: 1982-1983 hatchback
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1982	167.3	63.7	53.3	1983 Nissan Sentra Wagon Deluxe fallback	早期wagon	待补强: 1982 wagon直接页
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	167.3	63.7	53.3	1983/1986 Nissan Sentra Wagon fallback	早期wagon	待补强: 1984-1985 wagon直接页
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1988-1989	171.0	66.0	66.1	1987 Nissan Pathfinder US reference fallback	早期WD21两门	待补强: 1988-1989美国口径
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1970				1965后full-size Dynamic 88 wagon口径待确认；Vista Cruiser/Custom Cruiser不直接等同88 wagon	原88 wagon口径不稳	待补强: 确认1965-1970是否存在88 wagon直接车型

下一步


--- Round 23 / 下一步 ---
本轮继续补强 Nissan Sentra B11 wagon 与 Pathfinder 早期段。1982 Sentra Wagon 的 Carfolio 与 Automobile-Catalog 结果不一致：Carfolio 给 172.2 / 63.7 / 53.5，而 Automobile-Catalog 搜索摘要给 167.3 / 63.7 / 53.3；同一车型同年来源冲突，所以 1982 wagon 暂不直接可入库，改为“来源冲突待终核”。1985 Sentra Wagon 已找到 Automobile-Catalog 年款页，但搜索摘要没有展开长宽高，暂不改可入库。1988-1989 Pathfinder 仍未找到比 1987 美国口径更直接的尺寸页，继续保留待补强。
车目录
+2
汽车目录
+2

更新点

车型	操作	描述
Nissan Sentra	稳定/待终核	1982 wagon 出现 Carfolio 与 Automobile-Catalog 长度冲突，暂不入库
Nissan Sentra	稳定	1985 wagon 已定位年款页，但摘要未展开完整三维，继续待补强
Nissan Pathfinder	稳定	1988-1989 仍缺美国直接尺寸页，继续待补强
Oldsmobile 88	稳定	gen6 wagon 已改为口径不稳/待确认，不沿用 sedan/coupe

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1982	167.3	63.7	53.3	1982 Nissan Sentra Wagon Deluxe, Automobile-Catalog; Carfolio conflict shows 172.2 x 63.7 x 53.5	早期wagon	待补强: 1982 wagon来源冲突终核
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	167.3	63.7	53.3	1983/1985 Nissan Sentra Wagon Deluxe, Automobile-Catalog page located; dimensions not fully expanded	早期wagon	待补强: 1984-1985 wagon直接页完整三维
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1988-1989	171.0	66.0	66.1	1987 Nissan Pathfinder US reference fallback	早期WD21两门	待补强: 1988-1989美国口径
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1970				1965后full-size Dynamic 88 wagon口径待确认；Vista Cruiser/Custom Cruiser不直接等同88 wagon	原88 wagon口径不稳	待补强: 确认1965-1970是否存在88 wagon直接车型

下一步


--- Round 24 / 下一步 ---
本轮主要闭合 Oldsmobile 88 gen6 wagon 口径：公开资料明确说明 Oldsmobile full-size wagon 在 1964 后停止，直到 1971 才以 Custom Cruiser 形式回归；因此 1965-1970 不应继续保留为 Oldsmobile 88 wagon 待补强行，应改为无数据/美国市场无 88 full-size wagon。Sentra 1984 2-Door Standard 已能确认长度 167.3、宽度 63.8，但高度摘要未完整展开；1984 Hatchback Coupe 已能确认长度 172.3、宽度 63.8；1983/1984 wagon 页面已定位但三维摘要仍未完整展开，所以这些仍不直接改可入库。
汽车目录
+3
维基百科
+3
汽车目录
+3

更新点

车型	操作	描述
Oldsmobile 88	值修改/闭合	1965-1970 wagon 改为无数据：1965-1970 无 Oldsmobile 88/full-size wagon 直接车型
Nissan Sentra	推进	1984 2-Door Standard 找到直接页，但高度仍未完整展开，暂不入库
Nissan Sentra	稳定	1984 Hatchback Coupe 直接页支持既有 1984-1986 hatchback 可入库记录
Nissan Sentra	稳定	1984 wagon 页面已定位但三维未完整展开，继续待补强
Nissan Pathfinder	稳定	1988-1989 仍缺直接美国尺寸页，继续待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1970				1965-1970 Oldsmobile 88 full-size wagon not offered; full-size wagon returned as 1971 Custom Cruiser	1965后无88 wagon	无数据: 1965-1970无88/full-size wagon
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983	167.3	63.8	54.5	1983 Nissan Sentra 2-Door Standard page located; 1984 direct page confirms 167.3 x 63.8	早期sedan	待补强: 1983 sedan高度直接页
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1984	167.3	63.8	54.5	1984 Nissan Sentra 2-Door Standard, Automobile-Catalog	早期sedan	待补强: 1984 sedan高度直接页
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1983	172.3	63.8	53.5	1983/1984 Nissan Sentra Hatchback Coupe XE pages located; 1984 direct page confirms 172.3 x 63.8	三门hatch/coupe低车顶	待补强: 1982-1983 hatchback完整三维
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	167.3	63.7	53.3	1984/1985 Nissan Sentra Wagon Deluxe pages located; dimensions not fully expanded	早期wagon	待补强: 1984-1985 wagon完整三维
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1988-1989	171.0	66.0	66.1	1987 Nissan Pathfinder US reference fallback	早期WD21两门	待补强: 1988-1989美国口径

下一步


--- Round 25 / 下一步 ---
本轮补强了 Pathfinder 1988，并把 Sentra B11 中可以闭合的部分继续推进。1988 Pathfinder 可用 MotorTrend 的 1988 SE 复测规格入库，L x W x H 为 171.9 / 66.5 / 66.1；这比澳洲 CarsGuide / Autotrader 的 4365-4610 mm 长度范围更接近美国 2-door SE 口径，所以本批采用美国口径。Sentra 1986 wagon 与 1986 hatchback coupe 的 Automobile-Catalog 页面分别给出 165.6 / 63.8 / 53.3 与 170.2 / 63.8 / 53.5；1985 2-door sedan 为 165.3 / 63.8 / 54.5；1987 2-door sedan E 为 168.7 / 64.6 / 54.5，可作为 1986 sedan 相邻年参考，但 1983-1984 仍未完全闭合。
汽车目录
+4
MotorTrend
+4
汽车目录
+4

更新点

车型	操作	描述
Nissan Pathfinder	推进	1988 找到美国 2-door SE 规格，可入库
Nissan Pathfinder	稳定	1989 仍缺直接美国尺寸页，继续待补强
Nissan Sentra	稳定	1985 sedan、1986 wagon、1984-1986 hatchback 已有直接尺寸来源
Nissan Sentra	稳定	1983-1984 sedan、1982-1983 hatchback、1982/1984-1985 wagon 仍待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1988	171.9	66.5	66.1	1988 Nissan Pathfinder SE 2-door, MotorTrend	早期WD21两门	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1989	171.9	66.5	66.1	1988 Nissan Pathfinder SE 2-door US reference fallback	早期WD21两门	待补强: 1989美国口径
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1984	168.7	64.6	54.5	1985/1986/1987 Nissan Sentra 2-Door sedan reference; 1983-1984 sedan待核	早期sedan	待补强: 1983-1984 sedan直接页
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1983	170.2	63.8	53.5	1986 Nissan Sentra Hatchback Coupe SE reference; 1982-1983 hatchback待核	三门hatch/coupe低车顶	待补强: 1982-1983 hatchback直接页
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1982	167.3	63.7	53.3	1982 Nissan Sentra Wagon Deluxe, Automobile-Catalog; Carfolio conflict shows 172.2 x 63.7 x 53.5	早期wagon	待补强: 1982 wagon来源冲突终核
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	167.3	63.7	53.3	1984/1985 Nissan Sentra Wagon Deluxe pages located; dimensions not fully expanded	早期wagon	待补强: 1984-1985 wagon完整三维

下一步


--- Round 26 / 下一步 ---
本轮继续把最后几条 Nissan 早期缺口压缩。1989 Pathfinder 已找到 Automobile-Catalog 年款页，但页面正文无法展开完整三维；结合 1988 MotorTrend 美国 SE 规格、1990 Edmunds 规格均为 WD21 美国 2-door/早期口径，可先按 171.9 / 66.5 / 66.7 推进，但 1989 仍标待终核。1982 Sentra Hatchback Coupe 的 Carfolio 结果显示长度 4249 mm，约 167.3 in，和 1984-1986 Hatchback 172.3/170.2 存在明显差异，因此 1982-1983 hatchback 不能直接合并进 1984-1986。
汽车目录
+3
Edmunds
+3
Edmunds
+3

更新点

车型	操作	描述
Nissan Pathfinder	推进	1989 年款页定位，但完整三维未展开；仍待终核
Nissan Sentra	拆出	1982 Hatchback Coupe 长度与 1984-1986 不同，不能合并
Nissan Sentra	稳定	1984-1986 Hatchback 继续保持可入库
Nissan Sentra	稳定	1983-1984 sedan、1984-1985 wagon 仍缺完整三维直接页

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982	167.3	63.8	53.5	1982 Nissan Sentra Coupé XE, Carfolio; 1984 hatchback source shows later larger body	三门hatch/coupe低车顶	待补强: 1982 hatchback宽高终核
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1983	172.3	63.8	53.5	1984 Nissan Sentra Hatchback Coupe fallback	三门hatch/coupe低车顶	待补强: 1983 hatchback直接页
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1984	167.3	63.8	54.5	1983/1984 Nissan Sentra 2-Door Standard pages located; height not fully expanded	早期sedan	待补强: 1983-1984 sedan完整三维
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	167.3	63.7	53.3	1984/1985 Nissan Sentra Wagon Deluxe pages located; dimensions not fully expanded	早期wagon	待补强: 1984-1985 wagon完整三维
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1989	171.9	66.5	66.7	1989 Nissan Pathfinder 4x4 SE-V6 page located, Automobile-Catalog; 1990 Edmunds direct spec used as adjacent US WD21 reference	早期WD21两门	待补强: 1989完整三维直接页

下一步


--- Round 27 / 下一步 ---
本轮继续压缩最后待核项：1989 Pathfinder 已找到 Automobile-Catalog 直接摘要，显示 4365 mm / 171.9 in 长、1690 mm / 66.5 in 宽、1680 mm / 66.1 in 高，因此可入库；1983/1984 Sentra 2-Door、1983 Hatchback、1984 Wagon 已定位年款页，但搜索摘要未完整展开三维，仍不能按“可入库”闭合。1986 Sentra Wagon、1986 Hatchback 的三维摘要可直接确认；1984 2-Door Standard 目前只在摘要中明确到长宽，未展开高度。
汽车目录
+3
汽车目录
+3
汽车目录
+3

更新点

车型	操作	描述
Nissan Pathfinder	推进	1989 找到完整三维摘要，可入库
Nissan Sentra	稳定	1983/1984 sedan 页面定位，但高度仍未完整展开，继续待补强
Nissan Sentra	稳定	1983 hatchback 页面定位，但三维未完整展开，继续待补强
Nissan Sentra	稳定	1984/1985 wagon 页面定位，但三维未完整展开，继续待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1989	171.9	66.5	66.1	1989 Nissan Pathfinder 4x4 SE-V6, Automobile-Catalog	早期WD21两门	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1984	167.3	63.8	54.5	1983/1984 Nissan Sentra 2-Door Standard pages located, Automobile-Catalog; height not fully expanded	早期sedan	待补强: 1983-1984 sedan完整三维
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982	167.3	63.8	53.5	1982 Nissan Sentra Coupé XE, Carfolio; 1984 hatchback source shows later larger body	三门hatch/coupe低车顶	待补强: 1982 hatchback宽高终核
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1983	172.3	63.8	53.5	1983 Nissan Sentra Hatchback Coupe XE page located; 1984/1986 direct pages confirm later hatchback dimensions	三门hatch/coupe低车顶	待补强: 1983 hatchback完整三维
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	167.3	63.7	53.3	1984/1985 Nissan Sentra Wagon Deluxe pages located; dimensions not fully expanded	早期wagon	待补强: 1984-1985 wagon完整三维

下一步


--- Round 28 / 下一步 ---
本轮把 Pathfinder 1989 闭合为可入库，并进一步核对 Sentra B11 的剩余行。1982 Sentra Coupe XE Automatic 的 Automobile-Catalog 页面明确长度 172.2、宽度 1618 mm/63.7，可作为 1982 hatchback/coupe 直接口径；1986 Sentra Wagon Deluxe 明确为 165.6 / 63.8 / 53.3；1987 Sentra 2-Door Sedan E 明确为 168.7 / 64.6 / 54.5，可作为 1986 sedan 相邻延续口径辅助。1983-1984 sedan、1983 hatchback、1984-1985 wagon 仍缺完整三维直接摘要，不能给最终完成信号。
汽车目录
+2
汽车目录
+2

更新点

车型	操作	描述
Nissan Pathfinder	推进	1989 已可入库，Pathfinder 早期段闭合
Nissan Sentra	值修改	1982 hatchback/coupe 长度采用 172.2，宽度 63.7
Nissan Sentra	稳定	1983-1984 sedan、1983 hatchback、1984-1985 wagon 仍缺完整三维直接摘要
Nissan Sentra	稳定	1986 wagon、1986 hatchback、1987 2-door sedan 直接尺寸可作为已入库记录依据

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1989	171.9	66.5	66.1	1989 Nissan Pathfinder 4x4 SE-V6, Automobile-Catalog	早期WD21两门	可入库
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982	172.2	63.7	53.5	1982 Nissan Sentra Coupe XE Automatic, Automobile-Catalog; Carfolio width/height partial	三门hatch/coupe低车顶	待补强: 1982 hatchback高度终核
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1983	172.3	63.8	53.5	1984 Nissan Sentra Hatchback Coupe fallback	三门hatch/coupe低车顶	待补强: 1983 hatchback直接页
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1984	167.3	63.8	54.5	1983/1984 Nissan Sentra 2-Door Standard pages located; 1987 2-Door Sedan E confirms later 168.7 x 64.6 x 54.5	早期sedan	待补强: 1983-1984 sedan完整三维
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	165.6	63.8	53.3	1984/1985 Nissan Sentra Wagon Deluxe pages located; 1986 Wagon Deluxe confirms 165.6 x 63.8 x 53.3	早期wagon	待补强: 1984-1985 wagon完整三维

下一步


--- Round 29 / 下一步 ---
本轮继续补强 Sentra B11 剩余行。1983 Sentra 2-Door Standard 已有 Automobile-Catalog 摘要，能确认高度 54.5，因此 1983 sedan 可入库；1983 Hatchback Coupe XE 摘要确认长度 172.2、宽度 1618 mm / 63.7，可与 1982 coupe/hatchback 形成 1982-1983 小段，但高度仍未在摘要中展开，所以暂不整体可入库。1984 Hatchback Coupe XE 摘要确认 172.3 / 63.8，已支持 1984-1986 hatchback 可入库。1984-1985 wagon 仍缺完整三维直接摘要，继续待补强。
汽车目录
+3
汽车目录
+3
汽车目录
+3

更新点

车型	操作	描述
Nissan Sentra	推进	1983 sedan 高度已确认，可入库
Nissan Sentra	稳定	1984 sedan 仍缺高度完整摘要，继续待补强
Nissan Sentra	推进	1983 hatchback/coupe 长宽确认，但高度仍待终核
Nissan Sentra	稳定	1984-1985 wagon 仍缺完整三维摘要

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983	167.3	63.8	54.5	1983 Nissan Sentra 2-Door Standard, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1984	167.3	63.8	54.5	1984 Nissan Sentra 2-Door Standard page located; height not fully expanded	早期sedan	待补强: 1984 sedan高度直接页
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1983	172.2	63.7	53.5	1982 Nissan Sentra Coupe XE / 1983 Nissan Sentra Hatchback Coupe XE, Automobile-Catalog	三门hatch/coupe低车顶	待补强: 1982-1983 hatchback高度终核
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	165.6	63.8	53.3	1984/1985 Nissan Sentra Wagon Deluxe pages located; 1986 Wagon Deluxe confirms 165.6 x 63.8 x 53.3	早期wagon	待补强: 1984-1985 wagon完整三维

下一步


--- Round 30 / 下一步 ---
本轮闭合了 Sentra B11 的 1983-1984 sedan 与 1982-1983 hatchback/coupe 口径。1983 Nissan 官方 brochure 摘要直接列出 5 组车型高度：54.5 / 54.5 / 54.5 / 53.5 / 53.3，对应 sedan / hatchback coupe / wagon；1984 2-Door Standard 的 Automobile-Catalog 结果确认 167.3 in 长、63.8 in 宽；1983 Hatchback Coupe XE 页面确认 hatchback coupe 结构。由此 1983-1984 sedan 可推进为可入库；1982-1983 hatchback/coupe 按 172.2 / 63.7 / 53.5 推进为可入库。1984-1985 wagon 仍只定位到页面，未拿到完整三维摘要，本轮继续保留待补强。
汽车目录
+3
Dezo's Garage
+3
汽车目录
+3

更新点

车型	操作	描述
Nissan Sentra	推进	1983-1984 sedan 高度闭合，可入库
Nissan Sentra	推进	1982-1983 hatchback/coupe 高度闭合，可入库
Nissan Sentra	稳定	1984-1985 wagon 仍缺完整三维摘要，继续待补强

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1984	167.3	63.8	54.5	1983 Nissan Sentra brochure / 1984 Nissan Sentra 2-Door Standard, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1983	172.2	63.7	53.5	1982 Nissan Sentra Coupe XE / 1983 Nissan Sentra Hatchback Coupe XE, Automobile-Catalog / 1983 Nissan brochure	三门hatch/coupe低车顶	可入库
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984-1985	165.6	63.8	53.3	1984/1985 Nissan Sentra Wagon Deluxe pages located; 1986 Wagon Deluxe confirms 165.6 x 63.8 x 53.3	早期wagon	待补强: 1984-1985 wagon完整三维

下一步


--- Round 31 / 下一步 ---
更新点

车型	操作	描述
Nissan Sentra	推进	1984/1985 Wagon 找到完整三维，分别闭合为可入库；1984 为 167.3 / 63.8 / 53.3，1985 为 165.6 / 63.8 / 53.3。
汽车目录
+1

Nissan Sentra	推进	1982/1983 wagon 采用 1982-1983 Nissan brochure / Automobile-Catalog 口径闭合。
Dezo's Garage
+1

Nissan Ariya	拆出	美国市场 Ariya 当前可入库范围按 2023-2025；2026 拆为美国市场无数据/未售，不再保留待补强。
Edmunds
+1

Nissan Armada	推进	2008 Armada 用 Edmunds 直接尺寸闭合为 207.7 / 79.3 / 78.0，gen1 中段不再保留待补强。
Edmunds
+1

当前批次更新后的完整可替换 TSV

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan 370Z	Nissan	跑车	Coupe	NISMO	gen1 Z34	2015-2020	170.5	73.6	51.8	2015-2020 Nissan 370Z NISMO, Edmunds	性能版更长更宽	可入库
Nissan Altima	Nissan	三厢车	Sedan	Std.	gen1 compact	1993-1997	180.5	67.1	55.9	1993/1997 Nissan Altima SE, Edmunds		可入库
Nissan Altima	Nissan	三厢车	Sedan	Std.	gen3 large	2002-2006	192.3	70.4	57.9	2002-2006 Nissan Altima sedan, Edmunds / Autoevolution		可入库
Nissan Altima	Nissan	跑车	Coupe	Std.	gen4 coupe	2008-2013	180.9	70.7	55.9	2008/2011/2012/2013 Nissan Altima Coupe, Edmunds	低车顶Coupe	可入库
Nissan Altima	Nissan	三厢车	Sedan	Std.	gen5 large	2013-2018	191.9	72.0	57.9	2013/2017/2018 Nissan Altima sedan, Edmunds		可入库
Nissan Ariya	Nissan	越野车	SUV	EV	gen1 midsize SUV	2023-2025	182.9	74.8	65.4	2023/2024/2025 Nissan Ariya, Edmunds		可入库
Nissan Ariya	Nissan	越野车	SUV	EV	gen1 midsize SUV	2026				Nissan Ariya US model years 2023-2025; 2026 facelift not offered in US		无数据: 2026美国市场未售
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2004-2005	206.9	78.8	78.7	2004/2005 Nissan Armada LE, Edmunds / Carspecs	高车身早期款	可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2006-2007	206.9	78.8	78.7	2006/2007 Nissan Armada SE/LE, Edmunds	高车身早期款	可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen1 full-size SUV	2008-2015	207.7	79.3	78.0	2008/2010/2013/2014/2015 Nissan Armada SE/LE, Edmunds / KBB / JD Power		可入库
Nissan Armada	Nissan	越野车	SUV	Std.	gen2 full-size SUV	2017-2024	208.9	79.9	75.8	2017/2022/2024 Nissan Armada, Edmunds		可入库
Nissan Cube	Nissan	两厢车	Wagon	Std.	gen3 box wagon	2009-2014	156.7	66.7	65.0	2009/2014 Nissan Cube 1.8, Edmunds	方盒轮廓	可入库
Nissan Juke	Nissan	越野车	CUV	Std.	gen1 subcompact CUV	2011-2017	162.4	69.5	61.8	2011-2017 Nissan Juke SL, Edmunds		可入库
Nissan Kicks	Nissan	越野车	SUV	Std.	gen1 subcompact SUV	2018-2024	169.1	69.3	63.4	2018/2019/2024 Nissan Kicks S/SR, Car and Driver / Edmunds	小型SUV	可入库
Nissan Kicks	Nissan	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	171.9	70.9	64.2	2025/2026 Nissan Kicks SV, Edmunds	新一代尺寸增大	可入库
Nissan Maxima	Nissan	三厢车	Sedan	Std.	gen5 midsize	2000-2003	191.5	70.3	56.3	2000/2003 Nissan Maxima sedan, Edmunds	VQ时代	可入库
Nissan Maxima	Nissan	三厢车	Sedan	Std.	gen6 large sedan	2004-2008	194.4	71.7	58.3	2004/2008 Nissan Maxima 3.5 SE / SL, Edmunds	车身增大	可入库
Nissan Murano	Nissan	越野车	SUV	Std.	gen1 early	2003-2008	187.6	74.0	66.5	2003/2004/2008 Nissan Murano SL/SE, Edmunds	早期SUV	可入库
Nissan Murano	Nissan	越野车	SUV	Std.	gen2 early	2009-2014	189.9	74.1	68.0	2009/2010/2014 Nissan Murano LE, Edmunds	高度增加	可入库
Nissan Murano	Nissan	越野车	SUV	Std.	gen3 mid	2015-2024	192.8	75.4	67.8	2015/2018/2023/2024 Nissan Murano S/SV, Edmunds	中期更长	可入库
Nissan Murano	Nissan	越野车	SUV	Std.	gen4 wide	2025-2026	192.9	78.0	67.9	2025/2026 Nissan Murano SV/SL, Edmunds	宽体新款	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1987	171.0	66.0	66.1	1987 Nissan Pathfinder 4x4 SE-V6, Automobile-Catalog / CarGurus	早期WD21两门	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1988	171.9	66.5	66.1	1988 Nissan Pathfinder SE 2-door, MotorTrend	早期WD21两门	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1989	171.9	66.5	66.1	1989 Nissan Pathfinder 4x4 SE-V6, Automobile-Catalog	早期WD21两门	可入库
Nissan Pathfinder	Nissan	越野车	SUV	Std.	gen1 SUV	1990-1995	171.9	66.5	66.7	1990/1992/1995 Nissan Pathfinder, Edmunds	WD21四门	可入库
Nissan Rogue	Nissan	越野车	SUV	Std.	gen1 compact SUV	2008-2013	183.3	70.9	66.3	2008/2013 Nissan Rogue, Edmunds	早期车型	可入库
Nissan Rogue	Nissan	越野车	SUV	Std.	gen1 compact SUV Select	2014-2015	183.3	70.9	65.3	2014/2015 Nissan Rogue Select S, Edmunds	Rogue Select	可入库
Nissan Rogue	Nissan	越野车	SUV	Std.	gen2 compact SUV	2014-2020	184.5	72.4	68.5	2014/2015/2020 Nissan Rogue S/SV/SL, Edmunds	2020高度最大	可入库
Nissan Rogue	Nissan	越野车	SUV	Std.	gen3 compact SUV	2021-2026	183.0	72.4	66.5	2021/2025/2026 Nissan Rogue, Edmunds	当前车型	可入库
Nissan Rogue Sport	Nissan	越野车	SUV	Std.	gen1 compact SUV	2017-2022	172.8	72.3	63.4	2017/2020/2022 Nissan Rogue Sport SL, Cars.com / Edmunds		可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1982	167.3	63.7	54.5	1982 Nissan Sentra 2-Door Standard / MPG, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1983-1984	167.3	63.8	54.5	1983 Nissan Sentra brochure / 1984 Nissan Sentra 2-Door Standard, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1985	165.3	63.8	54.5	1985 Nissan Sentra 2-Door Deluxe, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen1 compact	1986	168.7	64.6	54.5	1986 Nissan Sentra 2-Door Standard, Automobile-Catalog	早期sedan	可入库
Nissan Sentra	Nissan	跑车	Coupe	Std.	gen1 compact	1982-1983	172.2	63.7	53.5	1982 Nissan Sentra Coupe XE / 1983 Nissan Sentra Hatchback Coupe XE, Automobile-Catalog / 1983 Nissan brochure	早期coupe	可入库
Nissan Sentra	Nissan	跑车	Coupe	Std.	gen1 compact	1984-1986	172.3	63.8	53.5	1984/1985/1986 Nissan Sentra Hatchback Coupe, Automobile-Catalog	早期coupe	可入库
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1982-1983	167.3	63.7	53.3	1982/1983 Nissan Sentra Wagon Deluxe, 1982-1983 Nissan brochure / Automobile-Catalog	早期wagon	可入库
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1984	167.3	63.8	53.3	1984 Nissan Sentra Wagon Deluxe, Automobile-Catalog	早期wagon	可入库
Nissan Sentra	Nissan	两厢车	Wagon	Std.	gen1 compact	1985-1986	165.6	63.8	53.3	1985/1986 Nissan Sentra Wagon Deluxe, Automobile-Catalog	早期wagon	可入库
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1982-1983	172.2	63.7	53.5	1982 Nissan Sentra Coupe XE / 1983 Nissan Sentra Hatchback Coupe XE, Automobile-Catalog / 1983 Nissan brochure	三门hatch/coupe低车顶	可入库
Nissan Sentra	Nissan	两厢车	Hatchback	Std.	gen1 compact	1984-1986	172.3	63.8	53.5	1984/1985/1986 Nissan Sentra Hatchback Coupe, Automobile-Catalog	三门hatch/coupe低车顶	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen4 compact	1995-1999	171.0	66.6	54.5	1995/1998/1999 Nissan Sentra sedan, Edmunds / Carspecs		可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen6 tall	2007-2012	180.1	70.5	59.5	2007/2012 Nissan Sentra sedan SE-R / SL, Edmunds / KBB	高车身	可入库
Nissan Sentra	Nissan	三厢车	Sedan	Std.	gen7 large	2013-2019	182.1	69.3	58.9	2013/2014/2019 Nissan Sentra sedan, Edmunds		可入库
Nissan Versa	Nissan	两厢车	Hatchback	Std.	gen1 hatchback	2007-2012	169.1	66.7	60.4	2007/2012 Nissan Versa 5-door Hatchback, Edmunds / JD Power	两厢车	可入库
Nissan Versa	Nissan	三厢车	Sedan	Std.	gen2 sedan	2012-2019	175.4	66.7	59.6	2012/2019 Nissan Versa Sedan, Edmunds	三厢车	可入库
Nissan Versa	Nissan	三厢车	Sedan	Std.	gen3 sedan	2020-2025	177.0	68.5	57.7	2020/2025 Nissan Versa Sedan, Edmunds / Nissan USA	三厢车	可入库
Nissan Versa	Nissan	三厢车	Sedan	Std.	gen3 sedan	2026				Nissan Versa ended U.S. production before 2026 model year	三厢车	无数据: 2026美国市场未售
Nissan Versa Note	Nissan	两厢车	Hatchback	Std.	gen1 subcompact	2014-2019	163.7	66.7	60.5	2014/2019 Nissan Versa Note, Edmunds / C&D / JD Power		可入库
Nissan Xterra	Nissan	越野车	SUV	Std.	gen1 compact SUV	2000-2004	178.0	70.4	73.9	2000/2004 Nissan Xterra SE / SE S/C, Edmunds / KBB	高车顶越野SUV	可入库
Nissan Xterra	Nissan	越野车	SUV	Std.	gen2 compact SUV	2005-2015	178.7	72.8	74.9	2005/2015 Nissan Xterra PRO-4X / S, Edmunds / JD Power	第二代更宽更高	可入库
Nissan Z	Nissan	跑车	Coupe	Std.	gen7 compact sports coupe	2023-2026	172.4	72.6	51.8	2023/2024/2025/2026 Nissan Z Performance, Edmunds	标准Z车身	可入库
Nissan Z	Nissan	跑车	Coupe	NISMO	gen7 compact sports coupe	2024-2026	173.2	73.6	51.8	2024/2025/2026 Nissan Z NISMO, Edmunds	NISMO更长更宽	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen1 full-size	1949-1950	202.0	75.2	64.1	1949/1950 Oldsmobile 88, Over-Drive / Automobile-Catalog	Rocket 88早期	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen1 full-size	1949-1950	202.0	75.2	64.1	1949/1950 Oldsmobile 88 Club Coupe / Holiday Coupe, Over-Drive / Automobile-Catalog	Rocket 88早期	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen1 full-size	1951-1953	204.0	76.0	63.7	1951/1952/1953 Oldsmobile Super 88 Sedan, Over-Drive / Automobile-Catalog	Rocket 88早期	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen1 full-size	1951-1953	204.0	76.0	63.7	1951/1952/1953 Oldsmobile Super 88 Coupe, Automobile-Catalog / Conceptcarz	Rocket 88早期	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen2 full-size	1954-1956	205.3	78.6	61.0	1954/1955/1956 Oldsmobile Super 88 Sedan, Automobile-Catalog	宽体full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen2 full-size	1954-1956	205.3	78.6	61.0	1954/1955/1956 Oldsmobile Super 88 Coupe, Automobile-Catalog	宽体full-size	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1961	212.0	77.2	55.8	1961 Oldsmobile Dynamic 88 Sedan, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1961	212.0	77.2	55.8	1961 Oldsmobile Dynamic 88 Holiday Coupe, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1961	212.0	77.2	55.8	1961 Oldsmobile Dynamic 88 wagon, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1962	213.9	77.9	55.8	1962 Oldsmobile Dynamic 88 Celebrity Sedan / Holiday Sedan, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1962	213.9	77.9	55.8	1962 Oldsmobile Dynamic 88 Holiday Coupe, Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1962	213.9	77.9	56.6	1962 Oldsmobile Dynamic 88 Fiesta Station Wagon, Oldsmobile brochure	高顶wagon	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1963	214.4	77.9	56.3	1963 Oldsmobile Dynamic 88 Celebrity Sedan / Super 88 Celebrity Sedan, Automobile-Catalog / Oldsmobile brochure	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1963	214.4	77.9	55.0	1963 Oldsmobile Dynamic 88 Holiday Coupe, Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1963	214.4	77.9	56.3	1963 Oldsmobile Super 88 Fiesta Wagon, Automobile-Catalog	高顶wagon	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen5 full-size	1964	215.3	78.0	55.9	1964 Oldsmobile Dynamic 88 Sedan, Conceptcarz / Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen5 full-size	1964	215.3	78.0	55.9	1964 Oldsmobile Dynamic 88 Holiday Coupe, Conceptcarz / Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen5 full-size	1964	215.3	78.0	55.9	1964 Oldsmobile Dynamic 88 Station Wagon, Conceptcarz / Automobile-Catalog	full-size低车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1965	216.9	80.0	55.5	1965 Oldsmobile Dynamic 88 Celebrity Sedan, Automobile-Catalog / 1965 Oldsmobile full-line brochure	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1965	216.9	80.0	54.7	1965 Oldsmobile Dynamic 88 Holiday Coupe, Automobile-Catalog / 1965 Oldsmobile full-line brochure	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1966	217.0	80.0	55.5	1966 Oldsmobile Delta 88 Celebrity Sedan, Carfolio / Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1966	217.0	80.0	55.5	1966 Oldsmobile Delta 88 Holiday Coupe, Automobile-Catalog / sedan dimensions confirmed	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1967	217.0	80.0	55.5	1967 Oldsmobile Delmont 88 / Delta 88 Town Sedan, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1967	217.0	80.0	54.1	1967 Oldsmobile Delta 88 Custom Holiday Coupe, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1968	217.8	80.0	55.5	1968 Oldsmobile Delta 88 Holiday Sedan, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1968-1969	218.6	80.0	54.1	1968/1969 Oldsmobile Delta 88 Holiday Coupe, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1969	218.6	80.0	54.7	1969 Oldsmobile Delta 88 Town Sedan, Carfolio	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen6 full-size	1970	219.1	79.9	55.5	1970 Oldsmobile Delta 88 Town Sedan, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen6 full-size	1970	219.1	79.9	54.7	1970 Oldsmobile Delta 88 Royale Holiday Coupe, Automobile-Catalog	B-body长车身	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen6 full-size	1965-1970				1965-1970 Oldsmobile 88 full-size wagon not offered; full-size wagon returned as 1971 Custom Cruiser	1965后无88 wagon	无数据: 1965-1970无88/full-size wagon
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1971	220.2	79.5	53.4	1971 Oldsmobile Delta 88 Town Sedan / Royale Sedan, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1971	220.2	79.5	53.4	1971 Oldsmobile Delta 88 Royale Hardtop Coupe, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1972	222.1	79.5	53.6	1972 Oldsmobile Delta 88 Hardtop Sedan / Town Sedan, Automobile-Catalog / Oldsmobile brochure	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1972	222.1	79.5	53.4	1972 Oldsmobile Delta 88 Royale Hardtop Coupe, Automobile-Catalog / Oldsmobile brochure	大型full-size	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1973	226.8	79.8	53.2	1973 Oldsmobile Full Size brochure, Delta 88 sedan	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1973	225.0	79.5	53.4	1973 Oldsmobile Delta 88 Hardtop Coupe, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1974	226.9	79.5	53.6	1974 Oldsmobile Delta 88 Hardtop Sedan, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1974	226.9	79.5	53.4	1974 Oldsmobile Delta 88 Royale Hardtop Coupe, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1975	226.9	79.8	53.6	1975 Oldsmobile Delta Eighty-Eight Royale Town Sedan / Hardtop Sedan, Automobile-Catalog / Conceptcarz	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1975	226.9	79.8	53.6	1975 Oldsmobile Delta Eighty-Eight Royale Coupe, Automobile-Catalog / Conceptcarz	大型full-size	可入库
Oldsmobile 88	Oldsmobile	三厢车	Sedan	Std.	gen7 full-size	1976	226.7	80.0	53.4	1976 Oldsmobile Delta 88 Royale Town Sedan, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	跑车	Coupe	Std.	gen7 full-size	1976	226.7	80.0	53.4	1976 Oldsmobile Delta 88 Royale Hardtop Coupe, Automobile-Catalog	大型full-size	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1971-1972	228.3	79.5	53.6	1971/1972 Oldsmobile Custom Cruiser Wagon, Oldsmobile brochure / Automobile-Catalog	长轴wagon	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1973	228.3	79.5	53.6	1973 Oldsmobile Custom Cruiser Wagon, Automobile-Catalog	长轴wagon	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1974-1975	231.2	79.5	53.6	1974/1975 Oldsmobile Custom Cruiser Wagon, Automobile-Catalog	长轴wagon	可入库
Oldsmobile 88	Oldsmobile	旅行车	Wagon	Std.	gen7 full-size wagon	1976	231.0	80.0	53.6	1976 Oldsmobile Custom Cruiser Wagon, Automobile-Catalog	长轴wagon	可入库

非皮卡车全量表完成
皮卡车全量表完成：本文件无皮卡车记录
本批次完成。

