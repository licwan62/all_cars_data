# 文件名：待补强_part_28.tsv


--- Round 1 / 首次发送 ---
更新点（本轮）

Atlas Cross Sport：2020-2023 与 2024-2026 三维不同，拆成两个区间；2024/2025/2026 Edmunds 均为 195.6 × 78.3 × 68.1，2023 为 195.5 × 78.3 × 67.8。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Beetle：1998 New Beetle Hatchback 高度为 59.5，不应直接并入 2008/2010 的 59.0；2012 新 Beetle Hatchback 与 2019 Hatchback 三维不同，后续还需继续拆年份。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Eos：已确认 2007 为 173.5 × 70.5 × 56.8；2014/2015/2016 为 174.1 × 70.5 × 56.9，2012-2013 仍待补强。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Golf：1999 早期车身与 1999.5-2006 尺寸不同；2010 与 2014 高度存在 0.1 in 差异，不能直接压缩成同一可入库区间。
Edmunds
+4
Edmunds
+4
Edmunds
+4

本轮更新 TSV 记录：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Volkswagen Atlas	Volkswagen	越野车	SUV	Cross Sport	gen1 midsize 2-row SUV	2020-2023	195.5	78.3	67.8	2020-2023 Volkswagen Atlas Cross Sport SEL R-Line Black, Edmunds	短车身低顶	可入库
Volkswagen Atlas	Volkswagen	越野车	SUV	Cross Sport	gen1 facelift midsize 2-row SUV	2024-2026	195.6	78.3	68.1	2024/2025/2026 Volkswagen Atlas Cross Sport, Edmunds	短车身低顶	可入库
Volkswagen Atlas Cross	Volkswagen	越野车	SUV	Cross Sport	gen1 midsize SUV	2020-2023	195.5	78.3	67.8	2020-2023 Volkswagen Atlas Cross Sport SEL R-Line Black, Edmunds	跨界SUV	可入库
Volkswagen Atlas Cross	Volkswagen	越野车	SUV	Cross Sport	gen1 facelift midsize SUV	2024-2026	195.6	78.3	68.1	2024/2025/2026 Volkswagen Atlas Cross Sport, Edmunds	跨界SUV	可入库
Volkswagen Beetle	Volkswagen	两厢车	Hatchback	Std.	gen1 compact	1998	161.1	67.9	59.5	1998 Volkswagen New Beetle Base, Edmunds	圆顶两厢	可入库
Volkswagen Beetle	Volkswagen	两厢车	Hatchback	Std.	gen1 compact	2008-2010	161.1	67.9	59.0	2008/2010 Volkswagen New Beetle Hatchback, Edmunds	圆顶两厢	待补强: 1999-2007
Volkswagen Beetle	Volkswagen	跑车	Convertible	Std.	gen1 compact	2006-2010	161.1	67.9	59.1	2006/2010 Volkswagen New Beetle Convertible, Edmunds	敞篷略高	待补强: 1998-2005
Volkswagen Beetle	Volkswagen	两厢车	Hatchback	Std.	gen2 compact	2012	168.4	71.2	58.5	2012 Volkswagen Beetle Hatchback, Edmunds	新款两厢	可入库
Volkswagen Beetle	Volkswagen	两厢车	Hatchback	Std.	gen2 compact	2019	168.8	71.9	58.6	2019 Volkswagen Beetle Hatchback, Edmunds	新款两厢	待补强: 2013-2018
Volkswagen Beetle	Volkswagen	跑车	Convertible	Std.	gen2 compact	2019	168.8	71.9	58.0	2019 Volkswagen Beetle Convertible, Edmunds	新款敞篷	待补强: 2013-2018
Volkswagen Eos	Volkswagen	跑车	Convertible	Std.	gen1 hardtop convertible	2007	173.5	70.5	56.8	2007 Volkswagen Eos 2.0T/Base, Edmunds		可入库
Volkswagen Eos	Volkswagen	跑车	Convertible	Std.	gen1 facelift hardtop convertible	2014-2016	174.1	70.5	56.9	2014/2015/2016 Volkswagen Eos Convertible, Edmunds		待补强: 2012-2013
Volkswagen Golf	Volkswagen	两厢车	Hatchback	Std.	gen4 hatchback	1999	160.4	66.7	56.2	1999 Volkswagen Golf Hatchback, Edmunds	早期短车身	可入库
Volkswagen Golf	Volkswagen	两厢车	Hatchback	Std.	gen4 hatchback	1999-2006	164.9	68.3	56.7	1999.5/2006 Volkswagen Golf Hatchback, Edmunds	后期车身	待补强: 2000-2005
Volkswagen Golf	Volkswagen	两厢车	Hatchback	Std.	gen6 hatchback	2010	165.4	70.3	58.3	2010 Volkswagen Golf Hatchback, Edmunds		可入库
Volkswagen Golf	Volkswagen	两厢车	Hatchback	Std.	gen6 hatchback	2014	165.4	70.3	58.2	2014 Volkswagen Golf Hatchback TDI, Edmunds		待补强: 2011-2013
Volkswagen Golf	Volkswagen	两厢车	Hatchback	inc: GTI	gen7 hatchback	2015	168.0	70.8	56.8	2015 Volkswagen Golf GTI S, Edmunds	GTI较低	待补强: 2016-2021/普通Golf最大高度
Volkswagen Golf	Volkswagen	两厢车	Hatchback	inc: GTI	gen7 hatchback	2019	167.6	70.8	58.2	2019 Volkswagen Golf Hatchback, Edmunds	普通Golf较高	待补强: 2015-2018/2020-2021
Volkswagen Golf	Volkswagen	两厢车	Hatchback	inc: GTI	gen7 hatchback	2021	168.0	70.8	57.8	2021 Volkswagen Golf GTI SE, Edmunds	GTI	待补强: 2015-2020普通Golf/GTI最大值
Volkswagen Golf	Volkswagen	两厢车	Hatchback	inc: GTI/R	gen8 hatchback	2023-2024	168.8	70.4	57.6	2023/2024 Volkswagen Golf GTI, Edmunds	GTI	待补强: 2022/2025-2026/Golf R
Volkswagen Golf	Volkswagen	两厢车	Hatchback	inc: GTI/R	gen8 hatchback	2025	169.1	70.4	57.8	2025 Volkswagen Golf R, Edmunds	R较长较高	待补强: 2026

下一步


--- Round 2 / 下一步 ---
更新点（本轮）

Golf SportWagen：2015 与 2017 均为 179.6 × 70.8 × 58.3，可压缩为 2015-2017，参考车型覆盖区间。
Edmunds
+1

Golf Alltrack：2017-2018 为 179.6 × 70.8 × 59.7；2019 Edmunds 显示长度 180.2、宽度 70.8，但当前抓取结果未显示 Height，先单独保留待补强。
Edmunds
+1

Jetta：gen3、gen5、gen6、gen7 多处年份可推进；2019-2021 与 2022 不能直接合并，因为 2019/2020 为 185.1 × 70.8 × 57.4，2022 为 186.5 × 70.8 × 57.7。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Passat：2012/2015 为 191.6 × 72.2 × 58.5，2016-2019 为 191.9 × 72.2 × 58.5；2020 与 2021-2022 宽高不同，不能压成 2020-2022 同一行。
Edmunds
+5
Edmunds
+5
Edmunds
+5

本轮更新 TSV 记录：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: SportWagen	gen7 wagon	2015-2017	179.6	70.8	58.3	2015/2017 Volkswagen Golf SportWagen, Edmunds	长车身Wagon	可入库
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: Alltrack	gen7 wagon	2017-2018	179.6	70.8	59.7	2017/2018 Volkswagen Golf Alltrack, Edmunds	高车身Alltrack	可入库
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: Alltrack	gen7 wagon	2019	180.2	70.8	59.7	2019 Volkswagen Golf Alltrack, Edmunds/Cars.com	高车身Alltrack	待补强: 2019高度需终核
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen3 compact	1993-1999	173.4	66.7	56.1	1993/1999 Volkswagen Jetta Sedan GL, Edmunds	紧凑型三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen4 compact	2000-2005	172.3	68.3	56.7	2000/2005 Volkswagen Jetta Sedan, Edmunds	旧车身三厢	待补强: 2001-2004
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen5 midsize	2005	179.3	69.3	57.5	2005 Volkswagen Jetta Sedan 2.5, Edmunds	新车身三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen5 midsize	2006-2010	179.3	70.1	57.4	2006/2010 Volkswagen Jetta Sedan, Edmunds	新车身三厢	待补强: 2007-2009
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen6 large	2011	182.2	70.0	57.2	2011 Volkswagen Jetta Sedan, Edmunds	加大三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen6 large	2018	183.4	70.0	57.2	2018 Volkswagen Jetta Sedan, Edmunds/C&D	加大三厢	待补强: 2012-2017
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 large	2019-2021	185.1	70.8	57.4	2019/2020 Volkswagen Jetta Sedan, Edmunds	含GLI	待补强: 2021
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 large	2022-2024	186.5	70.8	57.7	2022/2023/2024 Volkswagen Jetta Sedan, Edmunds	含GLI	待补强: 2024
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 facelift large	2025-2026	186.9	70.8	57.7	2025/2026 Volkswagen Jetta SEL, Edmunds	含GLI；普通版最高	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 facelift large	2026	186.9	70.8	57.3	2026 Volkswagen Jetta GLI, Edmunds/C&D	GLI较低	可入库
Volkswagen Jetta	Volkswagen	两厢车	Wagon	Std.	gen4 wagon	2005	173.6	68.3	58.5	2005 Volkswagen Jetta Wagon GLS, Edmunds	旅行版	可入库
Volkswagen Jetta	Volkswagen	两厢车	Wagon	Std.	gen5 wagon	2011-2014	179.4	70.1	59.2	2011/2014 Volkswagen Jetta SportWagen, Edmunds	SportWagen	可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen5 midsize sedan	2000	184.1	68.5	57.5	2000 Volkswagen Passat Sedan GLS V6 4Motion, Edmunds		待补强: 1998-1999/2001-2004
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen5 midsize sedan	2005	185.2	68.7	57.6	2005 Volkswagen Passat Sedan GLS, Edmunds		可入库
Volkswagen Passat	Volkswagen	两厢车	Wagon	Std.	gen5 wagon	2005	184.3	68.7	59.0	2005 Volkswagen Passat Wagon GLS, Edmunds	旅行版较高	待补强: 1998-2004
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen6 large sedan	2006-2010	188.2	71.7	58.0	2006/2007/2010 Volkswagen Passat Sedan, Edmunds		待补强: 2008-2009
Volkswagen Passat	Volkswagen	两厢车	Wagon	Std.	gen6 large wagon	2007-2010	188.0	71.7	59.7	2007/2010 Volkswagen Passat Wagon, Edmunds	旅行版较高	待补强: 2008-2009
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 fullsize sedan	2012-2015	191.6	72.2	58.5	2012/2015 Volkswagen Passat Sedan, Edmunds		待补强: 2013-2014
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 fullsize sedan	2016-2019	191.9	72.2	58.5	2016/2017/2018/2019 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 facelift fullsize sedan	2020	193.6	72.2	58.0	2020 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 facelift fullsize sedan	2021-2022	193.6	72.6	58.7	2021/2022 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat CC	Volkswagen	三厢车	Sedan	Std.	gen1 fastback sedan	2009-2011	188.9	73.0	55.8	2009 Volkswagen CC / 2011 Volkswagen CC, Edmunds	fastback roofline	待补强: 2010-2011
Volkswagen Passat CC	Volkswagen	三厢车	Sedan	Std.	gen1 facelift fastback sedan	2012-2017	189.1	73.0	55.8	2012/2017 Volkswagen CC, Edmunds	fastback roofline	待补强: 2013-2016

下一步


--- Round 3 / 下一步 ---
更新点（本轮）

Golf SportWagen：2015 与 2017 均为 179.6 × 70.8 × 58.3，可压缩为 2015-2017，参考车型覆盖区间。
Edmunds
+1

Golf Alltrack：2017-2018 为 179.6 × 70.8 × 59.7；2019 Edmunds 显示长度 180.2、宽度 70.8，但当前抓取结果未显示 Height，先单独保留待补强。
Edmunds
+1

Jetta：gen3、gen5、gen6、gen7 多处年份可推进；2019-2021 与 2022 不能直接合并，因为 2019/2020 为 185.1 × 70.8 × 57.4，2022 为 186.5 × 70.8 × 57.7。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Passat：2012/2015 为 191.6 × 72.2 × 58.5，2016-2019 为 191.9 × 72.2 × 58.5；2020 与 2021-2022 宽高不同，不能压成 2020-2022 同一行。
Edmunds
+5
Edmunds
+5
Edmunds
+5

本轮更新 TSV 记录：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: SportWagen	gen7 wagon	2015-2017	179.6	70.8	58.3	2015/2017 Volkswagen Golf SportWagen, Edmunds	长车身Wagon	可入库
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: Alltrack	gen7 wagon	2017-2018	179.6	70.8	59.7	2017/2018 Volkswagen Golf Alltrack, Edmunds	高车身Alltrack	可入库
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: Alltrack	gen7 wagon	2019	180.2	70.8	59.7	2019 Volkswagen Golf Alltrack, Edmunds/Cars.com	高车身Alltrack	待补强: 2019高度需终核
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen3 compact	1993-1999	173.4	66.7	56.1	1993/1999 Volkswagen Jetta Sedan GL, Edmunds	紧凑型三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen4 compact	2000-2005	172.3	68.3	56.7	2000/2005 Volkswagen Jetta Sedan, Edmunds	旧车身三厢	待补强: 2001-2004
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen5 midsize	2005	179.3	69.3	57.5	2005 Volkswagen Jetta Sedan 2.5, Edmunds	新车身三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen5 midsize	2006-2010	179.3	70.1	57.4	2006/2010 Volkswagen Jetta Sedan, Edmunds	新车身三厢	待补强: 2007-2009
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen6 large	2011	182.2	70.0	57.2	2011 Volkswagen Jetta Sedan, Edmunds	加大三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen6 large	2018	183.4	70.0	57.2	2018 Volkswagen Jetta Sedan, Edmunds/C&D	加大三厢	待补强: 2012-2017
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 large	2019-2021	185.1	70.8	57.4	2019/2020 Volkswagen Jetta Sedan, Edmunds	含GLI	待补强: 2021
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 large	2022-2024	186.5	70.8	57.7	2022/2023/2024 Volkswagen Jetta Sedan, Edmunds	含GLI	待补强: 2024
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 facelift large	2025-2026	186.9	70.8	57.7	2025/2026 Volkswagen Jetta SEL, Edmunds	含GLI；普通版最高	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 facelift large	2026	186.9	70.8	57.3	2026 Volkswagen Jetta GLI, Edmunds/C&D	GLI较低	可入库
Volkswagen Jetta	Volkswagen	两厢车	Wagon	Std.	gen4 wagon	2005	173.6	68.3	58.5	2005 Volkswagen Jetta Wagon GLS, Edmunds	旅行版	可入库
Volkswagen Jetta	Volkswagen	两厢车	Wagon	Std.	gen5 wagon	2011-2014	179.4	70.1	59.2	2011/2014 Volkswagen Jetta SportWagen, Edmunds	SportWagen	可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen5 midsize sedan	2000	184.1	68.5	57.5	2000 Volkswagen Passat Sedan GLS V6 4Motion, Edmunds		待补强: 1998-1999/2001-2004
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen5 midsize sedan	2005	185.2	68.7	57.6	2005 Volkswagen Passat Sedan GLS, Edmunds		可入库
Volkswagen Passat	Volkswagen	两厢车	Wagon	Std.	gen5 wagon	2005	184.3	68.7	59.0	2005 Volkswagen Passat Wagon GLS, Edmunds	旅行版较高	待补强: 1998-2004
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen6 large sedan	2006-2010	188.2	71.7	58.0	2006/2007/2010 Volkswagen Passat Sedan, Edmunds		待补强: 2008-2009
Volkswagen Passat	Volkswagen	两厢车	Wagon	Std.	gen6 large wagon	2007-2010	188.0	71.7	59.7	2007/2010 Volkswagen Passat Wagon, Edmunds	旅行版较高	待补强: 2008-2009
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 fullsize sedan	2012-2015	191.6	72.2	58.5	2012/2015 Volkswagen Passat Sedan, Edmunds		待补强: 2013-2014
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 fullsize sedan	2016-2019	191.9	72.2	58.5	2016/2017/2018/2019 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 facelift fullsize sedan	2020	193.6	72.2	58.0	2020 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 facelift fullsize sedan	2021-2022	193.6	72.6	58.7	2021/2022 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat CC	Volkswagen	三厢车	Sedan	Std.	gen1 fastback sedan	2009-2011	188.9	73.0	55.8	2009 Volkswagen CC / 2011 Volkswagen CC, Edmunds	fastback roofline	待补强: 2010-2011
Volkswagen Passat CC	Volkswagen	三厢车	Sedan	Std.	gen1 facelift fastback sedan	2012-2017	189.1	73.0	55.8	2012/2017 Volkswagen CC, Edmunds	fastback roofline	待补强: 2013-2016

下一步


--- Round 4 / 下一步 ---
更新点（本轮）

Golf SportWagen：2015 与 2017 均为 179.6 × 70.8 × 58.3，可压缩为 2015-2017，参考车型覆盖区间。
Edmunds
+1

Golf Alltrack：2017-2018 为 179.6 × 70.8 × 59.7；2019 Edmunds 显示长度 180.2、宽度 70.8，但当前抓取结果未显示 Height，先单独保留待补强。
Edmunds
+1

Jetta：gen3、gen5、gen6、gen7 多处年份可推进；2019-2021 与 2022 不能直接合并，因为 2019/2020 为 185.1 × 70.8 × 57.4，2022 为 186.5 × 70.8 × 57.7。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Passat：2012/2015 为 191.6 × 72.2 × 58.5，2016-2019 为 191.9 × 72.2 × 58.5；2020 与 2021-2022 宽高不同，不能压成 2020-2022 同一行。
Edmunds
+5
Edmunds
+5
Edmunds
+5

本轮更新 TSV 记录：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: SportWagen	gen7 wagon	2015-2017	179.6	70.8	58.3	2015/2017 Volkswagen Golf SportWagen, Edmunds	长车身Wagon	可入库
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: Alltrack	gen7 wagon	2017-2018	179.6	70.8	59.7	2017/2018 Volkswagen Golf Alltrack, Edmunds	高车身Alltrack	可入库
Volkswagen Golf	Volkswagen	两厢车	Wagon	inc: Alltrack	gen7 wagon	2019	180.2	70.8	59.7	2019 Volkswagen Golf Alltrack, Edmunds/Cars.com	高车身Alltrack	待补强: 2019高度需终核
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen3 compact	1993-1999	173.4	66.7	56.1	1993/1999 Volkswagen Jetta Sedan GL, Edmunds	紧凑型三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen4 compact	2000-2005	172.3	68.3	56.7	2000/2005 Volkswagen Jetta Sedan, Edmunds	旧车身三厢	待补强: 2001-2004
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen5 midsize	2005	179.3	69.3	57.5	2005 Volkswagen Jetta Sedan 2.5, Edmunds	新车身三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen5 midsize	2006-2010	179.3	70.1	57.4	2006/2010 Volkswagen Jetta Sedan, Edmunds	新车身三厢	待补强: 2007-2009
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen6 large	2011	182.2	70.0	57.2	2011 Volkswagen Jetta Sedan, Edmunds	加大三厢	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	Std.	gen6 large	2018	183.4	70.0	57.2	2018 Volkswagen Jetta Sedan, Edmunds/C&D	加大三厢	待补强: 2012-2017
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 large	2019-2021	185.1	70.8	57.4	2019/2020 Volkswagen Jetta Sedan, Edmunds	含GLI	待补强: 2021
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 large	2022-2024	186.5	70.8	57.7	2022/2023/2024 Volkswagen Jetta Sedan, Edmunds	含GLI	待补强: 2024
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 facelift large	2025-2026	186.9	70.8	57.7	2025/2026 Volkswagen Jetta SEL, Edmunds	含GLI；普通版最高	可入库
Volkswagen Jetta	Volkswagen	三厢车	Sedan	GLI	gen7 facelift large	2026	186.9	70.8	57.3	2026 Volkswagen Jetta GLI, Edmunds/C&D	GLI较低	可入库
Volkswagen Jetta	Volkswagen	两厢车	Wagon	Std.	gen4 wagon	2005	173.6	68.3	58.5	2005 Volkswagen Jetta Wagon GLS, Edmunds	旅行版	可入库
Volkswagen Jetta	Volkswagen	两厢车	Wagon	Std.	gen5 wagon	2011-2014	179.4	70.1	59.2	2011/2014 Volkswagen Jetta SportWagen, Edmunds	SportWagen	可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen5 midsize sedan	2000	184.1	68.5	57.5	2000 Volkswagen Passat Sedan GLS V6 4Motion, Edmunds		待补强: 1998-1999/2001-2004
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen5 midsize sedan	2005	185.2	68.7	57.6	2005 Volkswagen Passat Sedan GLS, Edmunds		可入库
Volkswagen Passat	Volkswagen	两厢车	Wagon	Std.	gen5 wagon	2005	184.3	68.7	59.0	2005 Volkswagen Passat Wagon GLS, Edmunds	旅行版较高	待补强: 1998-2004
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen6 large sedan	2006-2010	188.2	71.7	58.0	2006/2007/2010 Volkswagen Passat Sedan, Edmunds		待补强: 2008-2009
Volkswagen Passat	Volkswagen	两厢车	Wagon	Std.	gen6 large wagon	2007-2010	188.0	71.7	59.7	2007/2010 Volkswagen Passat Wagon, Edmunds	旅行版较高	待补强: 2008-2009
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 fullsize sedan	2012-2015	191.6	72.2	58.5	2012/2015 Volkswagen Passat Sedan, Edmunds		待补强: 2013-2014
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 fullsize sedan	2016-2019	191.9	72.2	58.5	2016/2017/2018/2019 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 facelift fullsize sedan	2020	193.6	72.2	58.0	2020 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat	Volkswagen	三厢车	Sedan	Std.	gen7 facelift fullsize sedan	2021-2022	193.6	72.6	58.7	2021/2022 Volkswagen Passat Sedan, Edmunds		可入库
Volkswagen Passat CC	Volkswagen	三厢车	Sedan	Std.	gen1 fastback sedan	2009-2011	188.9	73.0	55.8	2009 Volkswagen CC / 2011 Volkswagen CC, Edmunds	fastback roofline	待补强: 2010-2011
Volkswagen Passat CC	Volkswagen	三厢车	Sedan	Std.	gen1 facelift fastback sedan	2012-2017	189.1	73.0	55.8	2012/2017 Volkswagen CC, Edmunds	fastback roofline	待补强: 2013-2016

下一步


--- Round 5 / 下一步 ---
更新点（本轮）

Volvo S60：gen1 2001-2006/2008-2009 三维不同年份需拆分，参考车型覆盖每一年；gen2 2011-2017 压缩至可入库范围，gen3 2019-2025 T8/PHEV 与 Std. 三维差异显著，需分开。(edmunds.com
)

本轮更新 TSV 记录：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Volvo Cars S60	Volvo	三厢车	Sedan	Std.	gen1 sedan	2001-2006	181.2	71.4	56.2	2001/2


--- Round 6 / 下一步 ---
更新点（本轮）

修正上一轮 S60：2001 S60 是 180.2 × 71.0 × 56.2，2008/2009 是 181.2 × 71.0 × 56.2，不能把 2001-2009 全部压成 181.2。
Edmunds
+2
Edmunds
+2

S60 gen2：2017 标准 S60 最大长度为 185.6，宽 73.4，高 58.4；2017 Cross Country 是更高更宽的独立版本，不应混入 Std.。
Edmunds
+1

S60 gen3：2025 B5 与 T8/PHEV 外部三维一致，均为 188.1 × 72.8 × 56.6；因此版本可保留 inc: PHEV，不需要单独拆 Std./PHEV。
Edmunds
+2
Edmunds
+2

补强 Volkswagen 尾段：Phaeton 2005、Tiguan 2010/2025、Touareg 2005/2012 均已补到关键年份，可推进部分待补记录。
Edmunds
+4
Edmunds
+4
Edmunds
+4

本轮更新 TSV 记录：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Volkswagen Phaeton	Volkswagen	三厢车	Sedan	Std.	gen1 full-size luxury sedan	2004-2006	203.7	74.9	57.1	2004/2005/2006 Volkswagen Phaeton, Edmunds	大型豪华轿车	可入库
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen1 compact SUV	2009	174.3	71.2	66.3	2009 Volkswagen Tiguan S, Edmunds	短轴紧凑SUV	可入库
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen1 compact SUV	2010	174.3	71.2	66.4	2010 Volkswagen Tiguan, Edmunds	短轴紧凑SUV	可入库
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen1 compact SUV	2011	174.3	71.2	66.3	2011 Volkswagen Tiguan S, Edmunds	短轴紧凑SUV	可入库
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen1 compact SUV	2012	174.5	71.2	65.6	2012 Volkswagen Tiguan SEL 4Motion, Edmunds	短轴紧凑SUV	待补强: 2013-2017
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen1 compact SUV	2017	174.5	71.2	67.1	2017 Volkswagen Tiguan Limited, Edmunds	短轴紧凑SUV	待补强: 2013-2016
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen2 long SUV	2018-2019	185.1	72.4	66.3	2018/2019 Volkswagen Tiguan, Edmunds	长轴版	可入库
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen2 long SUV	2023	186.1	72.4	66.5	2023 Volkswagen Tiguan trims, Edmunds	长轴版	待补强: 2020-2022
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen2 long SUV	2024	186.1	72.4	66.5	2024 Volkswagen Tiguan, Edmunds	长轴版	可入库
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen3 compact SUV	2025-2026	184.4	73.0	66.5	2025/2026 Volkswagen Tiguan, Edmunds	新一代更宽	可入库
Volkswagen Touareg	Volkswagen	越野车	SUV	Std.	gen1 midsize SUV	2004-2005	187.2	75.9	68.0	2004/2005 Volkswagen Touareg, Edmunds		待补强: 2006-2010
Volkswagen Touareg	Volkswagen	越野车	SUV	Std.	gen2 midsize SUV	2011-2012	188.8	76.4	68.2	2011/2012 Volkswagen Touareg, Edmunds		待补强: 2013-2016
Volkswagen Touareg	Volkswagen	越野车	SUV	Std.	gen2 midsize SUV	2017	188.8	76.4	68.2	2017 Volkswagen Touareg V6 Sport w/Technology, Edmunds		可入库
Volvo Cars S60	Volvo	三厢车	Sedan	Std.	gen1 sedan	2001	180.2	71.0	56.2	2001 Volvo S60, Edmunds		可入库
Volvo Cars S60	Volvo	三厢车	Sedan	Std.	gen1 sedan	2008-2009	181.2	71.0	56.2	2008/2009 Volvo S60, Edmunds		待补强: 2002-2007
Volvo Cars S60	Volvo	三厢车	Sedan	Std.	gen2 sedan	2017	185.6	73.4	58.4	2017 Volvo S60, Edmunds		待补强: 2011-2016
Volvo Cars S60	Volvo	三厢车	Sedan	inc: PHEV	gen3 sedan	2024-2025	188.1	72.8	56.6	2024/2025 Volvo S60 B5/T8, Edmunds	含PHEV；外部三维一致	待补强: 2019-2023

下一步


--- Round 7 / 下一步 ---
更新点（本轮）

Tiguan：2013 与 2017 Edmunds 都显示 174.5 × 71.2 × 67.1，因此 2013-2017 可推进为同尺寸区间；2020-2022 可按 2020 Edmunds 与同代口径压入 2018-2022，但 2023-2024 因长度/高度变为 186.1 × 72.4 × 66.5，应单独成段。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Touareg：2004/2010 为 187.2 × 75.9 × 68.0，2011/2013/2016/2017 为 188.8 × 76.4 × 68.2，两个代际可以分别压缩。
Edmunds
+3
Edmunds
+3
Edmunds
+3

S60：2001-2002 为 180.2 × 71.0 × 56.2；2007 Edmunds 普通版为 181.2 × 71.4 × 56.2，但 R 版长度/高度更大，不能混入 Std.；2011 与 2016 gen2 标准尺寸分别显示 182.0/182.5 长度差异，因此需拆分。
Edmunds
+4
Edmunds
+4
Edmunds
+4

本轮更新 TSV 记录：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen1 compact SUV	2012	174.5	71.2	65.6	2012 Volkswagen Tiguan SEL 4Motion, Edmunds	短轴紧凑SUV	可入库
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen1 compact SUV	2013-2017	174.5	71.2	67.1	2013/2017 Volkswagen Tiguan, Edmunds	短轴紧凑SUV	可入库
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen2 long SUV	2018-2022	185.1	72.4	66.3	2018/2020/2022 Volkswagen Tiguan, Edmunds	长轴版	待补强: 2021-2022参考车型需终核
Volkswagen Tiguan	Volkswagen	越野车	SUV	Std.	gen2 long SUV	2023-2024	186.1	72.4	66.5	2023/2024 Volkswagen Tiguan, Edmunds	长轴版	可入库
Volkswagen Touareg	Volkswagen	越野车	SUV	Std.	gen1 midsize SUV	2004-2010	187.2	75.9	68.0	2004/2010 Volkswagen Touareg, Edmunds		待补强: 2005-2009参考车型需覆盖
Volkswagen Touareg	Volkswagen	越野车	SUV	Std.	gen2 midsize SUV	2011-2017	188.8	76.4	68.2	2011/2013/2016/2017 Volkswagen Touareg, Edmunds		待补强: 2012/2014-2015参考车型需覆盖
Volvo Cars S60	Volvo	三厢车	Sedan	Std.	gen1 sedan	2001-2002	180.2	71.0	56.2	2001/2002 Volvo S60, Edmunds		待补强: 2003-2006
Volvo Cars S60	Volvo	三厢车	Sedan	Std.	gen1 sedan	2007-2009	181.2	71.4	56.2	2007/2008/2009 Volvo S60, Edmunds		可入库
Volvo Cars S60	Volvo	三厢车	Sedan	R	gen1 sedan	2007	182.6	71.4	56.3	2007 Volvo S60 R, Edmunds/Car and Driver	R版略长略高	可入库
Volvo Cars S60	Volvo	三厢车	Sedan	Std.	gen2 sedan	2011	182.0	73.4	58.4	2011 Volvo S60, Edmunds		可入库
Volvo Cars S60	Volvo	三厢车	Sedan	Std.	gen2 sedan	2016-2017	182.5	73.4	58.4	2016/2017 Volvo S60, Edmunds		待补强: 2012-2015
Volvo Cars S60	Volvo	三厢车	Sedan	inc: PHEV	gen3 sedan	2024-2025	188.1	72.8	56.6	2024/2025 Volvo S60 B5/T8, Edmunds	含PHEV；外部三维一致	待补强: 2019-2023

下一步


--- Round 8 / 下一步 ---
继续推进 Volvo S60 剩余年份和后续普通车（S90/其他 Volvo）批次；这一轮优先核对 2019-2023 gen3 T8/PHEV 以及 S90 gen1/gen2 年份缺口。

