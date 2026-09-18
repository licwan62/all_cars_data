# 文件名：待补强_part_24.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作	描述
Pontiac Grand Am	稳定	1999/2000/2001/2002/2003/2004/2005 Edmunds 尺寸一致，补齐参考车型范围，推进为可入库。
Edmunds
+6
Edmunds
+6
Edmunds
+6

Pontiac GTO	稳定	2004/2005/2006 GTO coupe 尺寸一致，补齐 2005-2006。
Edmunds
+2
Edmunds
+2

Pontiac Torrent	稳定	2006/2007/2008/2009 Torrent SUV 尺寸一致，补齐 2006-2008。
Edmunds
+3
Edmunds
+3
Edmunds
+3

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen5 compact	1999-2005	186.3	70.4	55.1	1999/2000/2001/2002/2003/2004/2005 Pontiac Grand Am Sedan, Edmunds	四门	可入库
Pontiac GTO	Pontiac	跑车	Coupe	Std.	gen4 captive import	2004-2006	189.8	72.5	54.9	2004/2005/2006 Pontiac GTO Coupe, Edmunds	澳洲Monaro双门	可入库
Pontiac Torrent	Pontiac	越野车	SUV	Std.	gen1 compact SUV	2006-2009	188.8	71.4	69.3	2006/2007/2008/2009 Pontiac Torrent SUV, Edmunds		可入库

下一步。


--- Round 2 / 下一步 ---
更新点

车型	操作	描述
Pontiac Solstice	稳定	2006/2007/2008/2009 Roadster/Convertible 三维一致，补齐 2006/2008-2009，推进为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Pontiac Vibe	稳定	gen2 2009/2010 按 GT 最大值取 172.1 × 69.5 × 61.4，补齐 2009，推进为可入库。
Edmunds
+1

Porsche Cayenne	值修改	2024-2026 facelift 段重新按 SUV/Coupe 最大值核对：2025 Cayenne Base 高度 66.9，高于原 66.8，因此本行高度改为 66.9；2025 已补齐，但 2026 仍需继续核对 SUV 全量 trims。
Edmunds
+2
Car and Driver
+2

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Solstice	Pontiac	跑车	Roadster	Std.	gen1 roadster	2006-2009	157.2	71.3	50.1	2006/2007/2008/2009 Pontiac Solstice Roadster/Convertible, Edmunds	小型敞篷跑车	可入库
Pontiac Vibe	Pontiac	两厢车	Hatchback	Std.	gen2 compact	2009-2010	172.1	69.5	61.4	2009/2010 Pontiac Vibe GT, Edmunds	高顶两厢/wagon轮廓	可入库
Porsche Cayenne	Porsche	越野车	SUV	inc: PHEV	gen3 midsize SUV facelift	2024-2026	194.1	78.7	66.9	2024/2025 Porsche Cayenne SUV/Coupe trims, Edmunds / Porsche dealer dimensions	SUV/Coupe已取最大值	待补强: 2026 SUV trims

下一步。


--- Round 3 / 下一步 ---
更新点

车型	操作	描述
Pontiac Vibe	值修改	gen1 2003 为 171.9×69.9×63.0；2004/2005/2008 为 171.9×69.9×62.2，原 2003-2008 不能继续压成一个三维一致区间，本轮先拆出 2003 与 2004-2008。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Pontiac Sunfire	值修改	1995 与 1996、2002/2005 高度/长度不一致，原 1995-2005 不能直接压缩；本轮先按已核对点拆出 1995、1996、2002-2005 待继续补中间年份。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Porsche Boxster	值修改	gen1 1997/2001 为 171.0×70.1×50.8，2004 长度为 170.1；原 1997-2004 的 171.0 长度不能覆盖 2004，本轮先拆出 2004。
Edmunds
+2
Edmunds
+2

Porsche Boxster	值修改	gen2 2005 为 171.6×70.9×51.0，2012 为 172.1×70.9×50.9；原 2005-2012 的 172.1×70.9×50.9 不能覆盖 2005，本轮先拆出 2005 与 2012。
Edmunds
+1

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Vibe	Pontiac	两厢车	Hatchback	Std.	gen1 compact	2003	171.9	69.9	63.0	2003 Pontiac Vibe GT/Base, Edmunds	高顶两厢/wagon轮廓	可入库
Pontiac Vibe	Pontiac	两厢车	Hatchback	Std.	gen1 compact	2004-2008	171.9	69.9	62.2	2004/2005/2008 Pontiac Vibe Base Wagon, Edmunds	高顶两厢/wagon轮廓	待补强: 2006-2007
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	1995	181.9	67.4	53.2	1995 Pontiac Sunfire Sedan, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	1995	181.9	67.4	53.2	1995 Pontiac Sunfire Coupe, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1995	181.9	67.4	53.2	1995 Pontiac Sunfire Convertible, Edmunds	软顶结构	可入库
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	1996	182.4	68.4	51.9	1996 Pontiac Sunfire Sedan, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	1996	182.4	68.4	51.9	1996 Pontiac Sunfire Coupe, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1996	182.4	68.4	51.9	1996 Pontiac Sunfire Convertible, Edmunds	软顶结构	可入库
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	2002-2005	182.0	68.4	53.0	2002/2005 Pontiac Sunfire Sedan, Edmunds		待补强: 2003-2004
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	2002-2005	182.0	68.4	53.0	2002/2005 Pontiac Sunfire Coupe, Edmunds		待补强: 2003-2004
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	2002-2005	182.0	68.4	53.0	2002/2005 Pontiac Sunfire Convertible, Edmunds	软顶结构	待补强: 2003-2004
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen1 986	1997-2003	171.0	70.1	50.8	1997/2001 Porsche Boxster, Edmunds		待补强: 1998-2000/2002-2003
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen1 986	2004	170.1	70.1	50.8	2004 Porsche Boxster, Edmunds		可入库
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2005	171.6	70.9	51.0	2005 Porsche Boxster, Edmunds		可入库
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2006-2011	172.1	70.9	50.9	2012 Porsche Boxster, Edmunds		待补强: 2006-2011
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2012	172.1	70.9	50.9	2012 Porsche Boxster, Edmunds		可入库

下一步。


--- Round 4 / 下一步 ---
更新点

车型	操作	描述
Porsche Boxster	值修改	gen3 981 段需要按最大值保留 2016 GTS/Spyder 高度 50.1；2016 Base 高 49.7，不影响最大值。本轮补齐 2013-2016 口径。
Porsche Boxster	值修改	gen4 718 段原长度 173.9 更像 Spyder/GT4 RS 等长车身口径；常规 718 Boxster 2017/2025 为 172.4×70.9×50.4。本轮先拆出常规 2017-2025，原 173.9 需后续确认是否应单列 Spyder/特殊版。
Porsche Cayman	稳定	2006 Cayman S / 2012 Cayman S Black Edition 均为 172.1/171.1 附近，其中原表 171.1 与 2006 Cayman S 不一致；本轮先保留 2006 与 2012 已核点，2007-2011 待继续补。
Porsche Cayenne	值修改	gen2 2011 与 2018 S E-Hybrid 宽度不同，原 2011-2018 不能压成一行；本轮先拆出 2011 与 2018 已核点。
Porsche Cayenne	值修改	gen3 2019-2023 中 2023 Cayenne Coupe Turbo GT 长 194.6、宽 78.6，高 64.4；如果 SUV/Coupe 合并取最大，需要长度/宽度取 194.6/78.6，高度仍取 66.8。

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen3 981	2013-2016	173.8	70.9	50.1	2013/2014/2015/2016 Porsche Boxster Roadster, Edmunds		可入库
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen4 718	2017-2025	172.4	70.9	50.4	2017/2025 Porsche 718 Boxster Roadster, Car and Driver / Porsche dealer dimensions	常规718 Boxster；特殊长车身待单列	待补强: 2018-2024/Spyder口径
Porsche Cayman	Porsche	跑车	Coupe	Std.	gen2 987	2006	172.1	70.9	51.4	2006 Porsche Cayman S Coupe, Edmunds		可入库
Porsche Cayman	Porsche	跑车	Coupe	Std.	gen2 987	2007-2011	171.1	70.9	51.4	2012 Porsche Cayman S Black Edition, Edmunds		待补强: 2007-2011
Porsche Cayman	Porsche	跑车	Coupe	Std.	gen2 987	2012	171.1	70.9	51.4	2012 Porsche Cayman S Black Edition, Edmunds		可入库
Porsche Cayenne	Porsche	越野车	SUV	inc: PHEV	gen2 midsize SUV	2011	190.8	76.3	67.4	2011 Porsche Cayenne SUV Base, Edmunds		可入库
Porsche Cayenne	Porsche	越野车	SUV	inc: PHEV	gen2 midsize SUV	2012-2017	191.1	78.7	67.4	2018 Porsche Cayenne S E-Hybrid, Edmunds		待补强: 2012-2017
Porsche Cayenne	Porsche	越野车	SUV	inc: PHEV	gen2 midsize SUV	2018	191.1	78.7	67.4	2018 Porsche Cayenne S E-Hybrid, Edmunds		可入库
Porsche Cayenne	Porsche	越野车	SUV	inc: PHEV	gen3 midsize SUV	2019-2023	194.6	78.6	66.8	2019 Porsche Cayenne SUV trims / 2023 Porsche Cayenne Coupe Turbo GT, Edmunds	SUV/Coupe已取最大值	待补强: 2020-2022

依据简述：2016 Boxster Edmunds 给出 173.8×70.9×49.7，2016 GTS 为 173.4×70.9×50.1，所以合并取高 50.1；2006 Cayman S Edmunds 为 172.1×70.9×51.4；2018 Cayenne S E-Hybrid Edmunds 为 191.1×78.7×67.4；2011 Cayenne Base Edmunds 为 190.8×76.3×67.4；2023 Cayenne Coupe Turbo GT Edmunds 为 194.6×78.6×64.4，2019 Cayenne Edmunds SUV 最大高度 66.8。
Edmunds
+6
Edmunds
+6
Edmunds
+6

下一步。


--- Round 5 / 下一步 ---
更新点

车型	操作	描述
Pontiac Grand Prix	稳定	gen7 Coupe 2002 Edmunds 为 197.5×72.6×54.7；原行尺寸可保留，本轮补到 1998-2002 口径，但 1998-2001 仍未完全逐年闭环。
Pontiac Grand Prix	稳定	gen7 Sedan 2003 Edmunds 为 197.5×72.7×54.7；原行尺寸可保留，本轮补到 1998-2003 口径，但 1998-2002 仍未完全逐年闭环。
Pontiac Grand Prix	稳定	gen8 Sedan 2006/2008 Edmunds 均为 198.3×71.6×55.9，原 2004-2008 尺寸可保留；本轮补齐 2006/2008，仍需补 2007。

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Grand Prix	Pontiac	跑车	Coupe	Std.	gen7 W-body	1998-2002	197.5	72.6	54.7	1998/2002 Pontiac Grand Prix Coupe, Edmunds	同代2门	待补强: 1999-2001
Pontiac Grand Prix	Pontiac	三厢车	Sedan	Std.	gen7 W-body	1998-2003	197.5	72.7	54.7	1998/2003 Pontiac Grand Prix Sedan, Edmunds / AutoEvolution	同代4门	待补强: 1999-2002
Pontiac Grand Prix	Pontiac	三厢车	Sedan	Std.	gen8 W-body	2004-2008	198.3	71.6	55.9	2004/2005/2006/2008 Pontiac Grand Prix Sedan, Edmunds	最后一代4门	待补强: 2007

依据简述：2002 Grand Prix Coupe Edmunds 显示 197.5×72.6×54.7；2003 Grand Prix Sedan Edmunds 显示 197.5×72.7×54.7；2006 与 2008 Grand Prix Sedan/GXP Edmunds 均显示 198.3×71.6×55.9。
Edmunds
+3
Edmunds
+3
Edmunds
+3

下一步。


--- Round 6 / 下一步 ---
更新点

车型	操作	描述
Pontiac Grand Prix	稳定	gen8 Sedan 2007 Edmunds 为 198.3×71.6×55.9，与 2004/2005/2006/2008 一致，本行补齐为可入库。
Pontiac Grand Prix	值修改	gen7 Coupe 中 2001 Edmunds 为 197.5×72.6×54.7，可补齐 2001；但 1999/2000 搜索结果显示 196.5×72.7×54.7，和原 1998-2002 压缩行不一致，不能直接合并。
Pontiac Grand Prix	稳定	gen7 Sedan 2003 Edmunds 为 197.5×72.7×54.7；2001 Sedan/GT 页面也显示 197.5×72.6×54.7，宽度与 sedan 原行 72.7 有差异，需继续确认 sedan/coupe 页面口径。

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Grand Prix	Pontiac	三厢车	Sedan	Std.	gen8 W-body	2004-2008	198.3	71.6	55.9	2004/2005/2006/2007/2008 Pontiac Grand Prix Sedan, Edmunds	最后一代4门	可入库
Pontiac Grand Prix	Pontiac	跑车	Coupe	Std.	gen7 W-body	2001-2002	197.5	72.6	54.7	2001/2002 Pontiac Grand Prix Coupe, Edmunds	同代2门	可入库
Pontiac Grand Prix	Pontiac	跑车	Coupe	Std.	gen7 W-body	1998-2000	196.5	72.7	54.7	1998/2000 Pontiac Grand Prix Coupe, Edmunds	同代2门；早期长度/宽度不同	待补强: 1999
Pontiac Grand Prix	Pontiac	三厢车	Sedan	Std.	gen7 W-body	1998-2003	197.5	72.7	54.7	1998/2003 Pontiac Grand Prix Sedan, Edmunds / AutoEvolution	同代4门	待补强: 1999-2002

依据简述：2007 Grand Prix Sedan Edmunds 显示 Length 198.3、Overall width without mirrors 71.6、Height 55.9；2001 Grand Prix Coupe Edmunds 显示 197.5×72.6×54.7；2003 Grand Prix SE Sedan Edmunds 显示 197.5×72.7×54.7；2000 Grand Prix Edmunds 搜索结果显示 196.5×72.7×54.7，所以 gen7 Coupe 不能继续用 1998-2002 单行压缩。
edmunds.com
+3
edmunds.com
+3
edmunds.com
+3

下一步。


--- Round 7 / 下一步 ---
更新点

车型	操作	描述
Pontiac Grand Prix	稳定	gen7 Coupe 1998/1999/2000 均为 196.5×72.7×54.7，补齐 1999，推进为可入库。
Edmunds
+2
Edmunds
+2

Pontiac Grand Prix	值修改	gen7 Sedan 1998/1999/2002 为 196.5×72.7×54.7，2003 为 197.5×72.7×54.7，因此原 1998-2003 不能压成一行；本轮拆出 1998-2002 与 2003。
Edmunds
+3
Edmunds
+3
Edmunds
+3

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Grand Prix	Pontiac	跑车	Coupe	Std.	gen7 W-body	1998-2000	196.5	72.7	54.7	1998/1999/2000 Pontiac Grand Prix Coupe, Edmunds	同代2门；早期长度/宽度不同	可入库
Pontiac Grand Prix	Pontiac	三厢车	Sedan	Std.	gen7 W-body	1998-2002	196.5	72.7	54.7	1998/1999/2002 Pontiac Grand Prix Sedan, Edmunds	同代4门；早期长度不同	待补强: 2000-2001
Pontiac Grand Prix	Pontiac	三厢车	Sedan	Std.	gen7 W-body	2003	197.5	72.7	54.7	2003 Pontiac Grand Prix Sedan, Edmunds	同代4门；末年长度增加	可入库

下一步。


--- Round 8 / 下一步 ---
更新点

车型	操作	描述
Pontiac Grand Prix	稳定	gen7 Sedan 2000/2001 Edmunds 均为 196.5×72.7×54.7；补齐 2000-2001 后，1998-2002 可推进为可入库。
Edmunds
+1

Pontiac Vibe	稳定	gen1 2006/2007 Edmunds 均为 171.9×69.9×62.2；补齐 2006-2007 后，2004-2008 可推进为可入库。
Edmunds
+1

Pontiac Sunfire	值修改	2002 Sedan Edmunds 为 181.8×67.9×54.7；2003 Coupe Edmunds 为 182.0×68.4×53.0，说明 Sunfire sedan/coupe/convertible 不能继续共用原 2002-2005 的同一三维。
Edmunds
+1

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Grand Prix	Pontiac	三厢车	Sedan	Std.	gen7 W-body	1998-2002	196.5	72.7	54.7	1998/1999/2000/2001/2002 Pontiac Grand Prix Sedan, Edmunds	同代4门；早期长度不同	可入库
Pontiac Vibe	Pontiac	两厢车	Hatchback	Std.	gen1 compact	2004-2008	171.9	69.9	62.2	2004/2005/2006/2007/2008 Pontiac Vibe Base Wagon, Edmunds	高顶两厢/wagon轮廓	可入库
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	2002	181.8	67.9	54.7	2002 Pontiac Sunfire Sedan, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	2003-2005	182.0	68.4	53.0	2003/2005 Pontiac Sunfire Coupe, Edmunds		待补强: 2004
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	2002	182.0	68.4	53.7	2002 Pontiac Sunfire Convertible, Edmunds / Pontiac Sunfire dimensions cross-check	软顶结构	待补强: 2003-2005是否仍销售/是否应保留

下一步。


--- Round 9 / 下一步 ---
更新点

车型	操作	描述
Pontiac Sunfire	值修改	Sedan 1998-1999 为 181.9/181.7 左右、宽 67.3、 高 54.7；2000-2002 Sedan 为 181.8×67.9×54.7；2003-2005 Sedan 为 183.2×67.9×54.7，因此原 Sedan 不能压成 1995-2005 一行。Edmunds 与车型资料均支持 sedan/coupe/convertible 尺寸分开处理。
Edmunds
+1

Pontiac Sunfire	稳定	Coupe 2003/2004/2005 Edmunds 均为 182×68.4×53，可补齐 2004，推进 2003-2005 Coupe 为可入库。
Edmunds
+2
Edmunds
+2

Pontiac Sunfire	稳定	2003-2005 常规 Sunfire Edmunds 页面显示 182×68.4×53；但 Convertible 在 2003 后是否继续销售需保留待核，不能直接并入 Coupe。
Edmunds
+1

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	1997	182.0	67.3	54.7	1997 Pontiac Sunfire Sedan, Edmunds / Pontiac Sunfire dimensions cross-check		待补强: 原1996-2005需继续拆分核对
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	1998-1999	181.9	67.3	54.7	1998/1999 Pontiac Sunfire Sedan, Edmunds / Pontiac Sunfire dimensions cross-check		可入库
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	2000-2002	181.8	67.9	54.7	2000/2001/2002 Pontiac Sunfire Sedan, Edmunds / Pontiac Sunfire dimensions cross-check		可入库
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	2003-2005	183.2	67.9	54.7	2003/2004/2005 Pontiac Sunfire Sedan, Pontiac Sunfire dimensions cross-check		待补强: 2003-2005 Edmunds sedan页面需继续确认
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	2003-2005	182.0	68.4	53.0	2003/2004/2005 Pontiac Sunfire Coupe, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1998-2002	181.9	68.4	53.7	1998/2002 Pontiac Sunfire Convertible, Pontiac Sunfire dimensions cross-check	软顶结构	待补强: 1999-2001

下一步。


--- Round 10 / 下一步 ---
更新点

车型	操作	描述
Pontiac Sunfire	拆出	Sunfire 原 1995-2005 三结构共用尺寸不成立；公开资料明确列出 1995-97、1998-99、2000-02、2003-05 Sedan，以及 Coupe/Convertible 的不同长宽高区间。
维基百科

Pontiac Sunfire	稳定	2003/2004/2005 Coupe 均可按 Edmunds/Cars.com 口径确认为 182.0×68.4×53.0，推进为可入库。
Edmunds
+2
Edmunds
+2

Pontiac Sunfire	稳定	2000-2002 Coupe 与 2003-2005 Coupe 尺寸一致，可合并为 2000-2005 Coupe；2001 GT Edmunds 为 182×68.4×53。
Edmunds
+1

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	1995-1997	182.0	67.3	54.7	1995/1996/1997 Pontiac Sunfire Sedan, Edmunds / Pontiac Sunfire dimensions cross-check		待补强: 1996-1997 Edmunds逐年页
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	1998-1999	181.7	67.9	54.7	1998/1999 Pontiac Sunfire Sedan, Edmunds / Pontiac Sunfire dimensions cross-check		可入库
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	2000-2002	181.8	67.9	54.7	2000/2001/2002 Pontiac Sunfire Sedan, Edmunds / Pontiac Sunfire dimensions cross-check		可入库
Pontiac Sunfire	Pontiac	三厢车	Sedan	Std.	gen1 compact	2003-2005	183.2	67.9	54.7	2003/2004/2005 Pontiac Sunfire Sedan, Pontiac Sunfire dimensions cross-check		待补强: 2003-2005 Sedan专页
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	1995-1997	181.9	67.4	53.2	1995/1996/1997 Pontiac Sunfire Coupe, Edmunds / Pontiac Sunfire dimensions cross-check		待补强: 1996-1997
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	1998-1999	181.9	68.4	53.0	1998/1999 Pontiac Sunfire Coupe, Pontiac Sunfire dimensions cross-check		待补强: 1998-1999
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	2000-2005	182.0	68.4	53.0	2000/2001/2002/2003/2004/2005 Pontiac Sunfire Coupe, Edmunds / Cars.com		可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1995-1997	181.9	67.4	53.2	1995/1996/1997 Pontiac Sunfire Convertible, Pontiac Sunfire dimensions cross-check	软顶结构	待补强: 1996-1997
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1998-2002	181.9	68.4	53.7	1998/1999/2000/2001/2002 Pontiac Sunfire Convertible, Pontiac Sunfire dimensions cross-check	软顶结构	待补强: 1999-2001

下一步。


--- Round 11 / 下一步 ---
更新点

车型	操作	描述
Pontiac Sunfire	稳定	1997 Coupe Edmunds 为 181.9×68.4×53.2；1997 Convertible Edmunds 为 181.9×68.4×53.9，因此早期 Coupe 与 Convertible 不能共用 1995 的 67.4 宽度，也不能共用同一高度。
Pontiac Sunfire	拆出	Convertible 1997 高度 53.9，1998-2002 原资料为 53.7，建议拆成 1997 与 1998-2002；1995-1996 Convertible 仍需继续核对。
Porsche Boxster	稳定	gen1 986 中 1998/2002 Edmunds 均为 171.0×70.1×50.8，Excellence 亦显示 1998/2002 约 170.98×70.08×50.79；本轮将 1997-2003 继续补强为待只剩 1999-2000/2003。
Porsche Boxster	稳定	gen2 987 中 2006 Edmunds 为 171.6×70.9×51.0，2011 Edmunds 为 172.1×70.9×50.9，因此 2006-2011 不可直接与 2012 合并；先拆出 2006 与 2011-2012。

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	1995	181.9	67.4	53.2	1995 Pontiac Sunfire Coupe, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	1996-1997	181.9	68.4	53.2	1996/1997 Pontiac Sunfire Coupe, Edmunds / CarsDirect cross-check		待补强: 1996
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1995-1996	181.9	67.4	53.2	1995 Pontiac Sunfire Convertible, Edmunds / Pontiac Sunfire dimensions cross-check	软顶结构	待补强: 1996
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1997	181.9	68.4	53.9	1997 Pontiac Sunfire Convertible, Edmunds	软顶结构	可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1998-2002	181.9	68.4	53.7	1998/1999/2000/2001/2002 Pontiac Sunfire Convertible, Pontiac Sunfire dimensions cross-check	软顶结构	待补强: 1999-2001
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen1 986	1997-2003	171.0	70.1	50.8	1997/1998/2001/2002 Porsche Boxster, Edmunds / Excellence Magazine		待补强: 1999-2000/2003
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2005-2006	171.6	70.9	51.0	2005/2006 Porsche Boxster S, Edmunds / Excellence Magazine		可入库
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2007-2010	172.1	70.9	50.9	2011/2012 Porsche Boxster, Edmunds		待补强: 2007-2010
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2011-2012	172.1	70.9	50.9	2011/2012 Porsche Boxster, Edmunds		可入库

依据简述：1997 Sunfire Coupe Edmunds 为 181.9×68.4×53.2，1997 Sunfire Convertible Edmunds 为 181.9×68.4×53.9；1998 与 2002 Boxster Edmunds 均为 171.0×70.1×50.8，Excellence 的 1998/2002 986 数据也基本一致；2006 Boxster S Edmunds 为 171.6×70.9×51.0，2011 Boxster Edmunds 为 172.1×70.9×50.9。
edmunds.com
+5
edmunds.com
+5
edmunds.com
+5

下一步。


--- Round 12 / 下一步 ---
更新点

车型	操作	描述
Porsche Boxster	拆出	gen1 986 中 1999/2000 为 171.0×70.1×50.8，2003 为 170.1×70.1×50.8，因此 1997-2003 不能压成一行；拆为 1997-2002 与 2003-2004。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Porsche Boxster	拆出	gen2 987 中 2007/2008 为 171.6×70.9×50.9，2009/2010/2012 为 172.1×70.9×50.9，因此 2007-2012 需按长度拆分。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Pontiac Sunfire	值修改	1999 Convertible 为 181.9×68.4×54.1，2000 Convertible 为 182.9×68.4×54.1，原 1998-2002 Convertible 的 181.9×68.4×53.7 不可继续使用。
Edmunds
+1

Pontiac Sunfire	稳定	1996 Coupe Edmunds 为 182.0×67.4×53.2，可与 1995 Coupe 合并；1997 Coupe 仍保持单独核对行。
Edmunds

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen1 986	1997-2002	171.0	70.1	50.8	1997/1998/1999/2000/2001/2002 Porsche Boxster Roadster, Edmunds / Excellence Magazine		可入库
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen1 986	2003-2004	170.1	70.1	50.8	2003/2004 Porsche Boxster Roadster, Edmunds		可入库
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2005-2006	171.6	70.9	51.0	2005/2006 Porsche Boxster Roadster, Edmunds / Excellence Magazine		可入库
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2007-2008	171.6	70.9	50.9	2007/2008 Porsche Boxster Roadster, Edmunds		可入库
Porsche Boxster	Porsche	跑车	Roadster	Std.	gen2 987	2009-2012	172.1	70.9	50.9	2009/2010/2011/2012 Porsche Boxster Roadster, Edmunds / Excellence Magazine		可入库
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	1995-1996	182.0	67.4	53.2	1995/1996 Pontiac Sunfire Coupe, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Coupe	Std.	gen1 compact	1997	181.9	68.4	53.2	1997 Pontiac Sunfire Coupe, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1995-1996	181.9	67.4	53.2	1995/1996 Pontiac Sunfire Convertible, Edmunds / Pontiac Sunfire dimensions cross-check	软顶结构	待补强: 1996 Convertible专页
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1998-1999	181.9	68.4	54.1	1998/1999 Pontiac Sunfire Convertible GT, Edmunds / Automobile-Catalog	软顶结构	待补强: 1998
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	2000	182.9	68.4	54.1	2000 Pontiac Sunfire Convertible GT, Edmunds	软顶结构；长度增加	可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	2001-2002	181.9	68.4	54.1	1999/2000/2001/2002 Pontiac Sunfire Convertible cross-check	软顶结构	待补强: 2001-2002专页

下一步。


--- Round 13 / 下一步 ---
继续推进剩余 Pontiac Sunfire Convertible 1998-2002 的年份缺口，以及 Porsche Boxster/Cayman 的中间年份待核段。本轮仍输出更新记录，直到可入库范围尽量完整。


--- Round 14 / 下一步 ---
更新点

车型	操作	描述
Porsche Cayman	值修改	2011 Edmunds 为 172.3×70.9×51.3，Car and Driver 2010 也为 172.3×70.9×51.3；原 2007-2011 使用 171.1×70.9×51.4 不可继续覆盖。
Pontiac Sunfire	稳定	1995 Coupe Edmunds 为 181.9×67.4×53.2；2005 Coupe Edmunds 为 182×68.4×53，支持已拆分的 Coupe 早期/后期口径。
Pontiac Sunfire	保留待核	1998/2001/2002 Sunfire Convertible 搜索结果仍不够直接；继续保留 Convertible 1998-2002 的待补强，不强行转可入库。

阶段性 TSV（本轮更新记录）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Porsche Cayman	Porsche	跑车	Coupe	Std.	gen2 987	2006	172.1	70.9	51.4	2006 Porsche Cayman S Coupe, Edmunds		可入库
Porsche Cayman	Porsche	跑车	Coupe	Std.	gen2 987	2007-2009	171.1	70.9	51.4	2012 Porsche Cayman S Black Edition, Edmunds		待补强: 2007-2009
Porsche Cayman	Porsche	跑车	Coupe	Std.	gen2 987	2010-2011	172.3	70.9	51.3	2010/2011 Porsche Cayman Base, Car and Driver / Edmunds		可入库
Porsche Cayman	Porsche	跑车	Coupe	Std.	gen2 987	2012	171.1	70.9	51.4	2012 Porsche Cayman S Black Edition, Edmunds		可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	1998-1999	181.9	68.4	54.1	1999 Pontiac Sunfire Convertible GT, Edmunds / 1998待核	软顶结构	待补强: 1998
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	2000	182.9	68.4	54.1	2000 Pontiac Sunfire Convertible GT, Edmunds	软顶结构；长度增加	可入库
Pontiac Sunfire	Pontiac	跑车	Convertible	Std.	gen1 compact	2001-2002	181.9	68.4	54.1	2001/2002 Pontiac Sunfire Convertible待核	软顶结构	待补强: 2001-2002专页

依据简述：2011 Cayman Base Edmunds 显示 172.3×70.9×51.3；Car and Driver 的 2010 Cayman 规格同为 172.3×70.9×51.3；1995 Sunfire Coupe Edmunds 为 181.9×67.4×53.2，2005 Sunfire Coupe Edmunds 为 182×68.4×53。
edmunds.com
+3
edmunds.com
+3
caranddriver.com
+3

下一步。


--- Round 15 / 下一步 ---
继续推进 Pontiac Sunfire Convertible 1998-2002 的待补强年份段，同时逐步处理 Porsche Boxster/Cayman gen2 中未闭环年份。本轮仍只输出更新记录。

