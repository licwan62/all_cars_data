# 文件名：待补强_part_26.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作	描述
Subaru Legacy gen1 Sedan	拆出	1990、1991、1992-1994 三段尺寸不完全一致，不能压成 1990-1994。Edmunds 可核到 1990/1991/1992/1993/1994。
Subaru Legacy gen1 Wagon	拆出	1990、1991、1992-1994 三段尺寸不完全一致，不能压成 1990-1994。
Subaru Legacy gen2 Sedan	拆出	1995-1996 与 1997-1999 尺寸不同，拆成两段。
Subaru Legacy gen3/gen4/gen5/gen6/gen7	稳定	本轮先补强已有参考点；部分中间年份还未完整覆盖，继续下一轮。

本轮主要依据 Edmunds 可核到 Legacy 1990/1994 sedan、1990/1994 wagon、1995-1999 sedan、2004 sedan/wagon、2007 wagon、2014/2019/2020/2025 sedan 的外廓尺寸字段。
Edmunds
+14
Edmunds
+14
Edmunds
+14

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen1 compact	1990	177.6	66.5	54.3	1990 Subaru Legacy Sedan, Edmunds		可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen1 compact	1991	177.6	66.5	53.5	1991 Subaru Legacy Sedan AWD, Edmunds		可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen1 compact	1992-1994	178.9	66.5	53.5	1992/1993/1994 Subaru Legacy Sedan, Edmunds		可入库
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen1 compact	1990	181.1	66.5	56.3	1990 Subaru Legacy LS Wagon AWD, Edmunds	AWD wagon更高	可入库
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen1 compact	1991	181.1	66.5	54.7	1991 Subaru Legacy Wagon AWD, Edmunds	AWD wagon	可入库
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen1 compact	1992-1994	181.9	66.5	56.3	1992/1993/1994 Subaru Legacy Wagon LS, Edmunds	AWD wagon更高	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen2 compact	1995-1996	180.9	67.5	55.3	1995/1996 Subaru Legacy Sedan, Edmunds		可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen2 compact	1997-1999	181.5	67.5	55.7	1997/1998/1999 Subaru Legacy Sedan GT, Edmunds		可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen3 compact	2000-2004	184.4	68.7	55.7	2004 Subaru Legacy Sedan, Edmunds		待补强: 2000-2003
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen3 compact	2000-2004	187.4	68.7	59.6	2004 Subaru Legacy Wagon, Edmunds		待补强: 2000-2003
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen4 compact	2005-2007	188.7	68.1	58.1	2007 Subaru Legacy Wagon, Edmunds		待补强: 2005-2006
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen5 large	2010-2014	187.2	71.7	59.3	2014 Subaru Legacy Sedan, Edmunds		待补强: 2010-2013
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen6 large	2015-2019	189.1	72.4	59.0	2019 Subaru Legacy Sedan, Edmunds		待补强: 2015-2018
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen7 large	2020	190.6	72.4	59.1	2020 Subaru Legacy Sedan, Edmunds		可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen7 large	2021-2025	191.1	72.4	59.1	2025 Subaru Legacy, Edmunds		待补强: 2021-2024

下一步


--- Round 2 / 下一步 ---
更新点

车型	操作	描述
Subaru Outback gen2	拆出	2000 与 2001-2004 高度不同，不能直接压成 2000-2004。
Subaru Outback gen3	拆出	2005-2008 与 2009 长度不同，2009 单独拆出。
Subaru Outback gen4	拆出	2010-2013 与 2014 高度不同，2014 单独拆出。
Subaru Solterra	稳定	2025/2026 Edmunds 尺寸一致；参考车型补足到 2023-2026 口径，仍需下一轮确认 2023-2024 是否同尺寸。
Subaru Tribeca	拆出	2006-2007 B9 Tribeca 与 2008-2014 facelift 长度不同，拆成两段。
Subaru WRX	拆出/值修改	2004-2007 WRX/STI sedan 使用 STI 宽体最大值；2008-2014 需要继续按 hatch/sedan 年份补强。

本轮 Outback/Tribeca/WRX 主要依据 Edmunds 的对应年份尺寸页：2001/2004 Outback、2005/2009 Outback、2011/2014 Outback、2006/2007 B9 Tribeca、2008/2014 Tribeca、2006/2007 Impreza WRX STI、2014 Impreza WRX sedan 等；Solterra 2025/2026 依据 Edmunds。
Edmunds
+13
Edmunds
+13
Edmunds
+13

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Subaru Outback	Subaru	越野车	Wagon	Std.	gen1 crossover	1995-1999	186.6	68.3	63.0	1998-1999 Subaru Outback wagon	早期跨界旅行	待补强: 1995-1997
Subaru Outback	Subaru	越野车	Wagon	Std.	gen2 crossover	2000	187.4	68.7	63.2	2000 Subaru Outback wagon	跨界旅行	待补强: 2000需复核最高trim
Subaru Outback	Subaru	越野车	Wagon	Std.	gen2 crossover	2001-2004	187.4	68.7	62.2	2001/2004 Subaru Outback wagon, Edmunds	跨界旅行	待补强: 2002-2003
Subaru Outback	Subaru	越野车	Wagon	Std.	gen3 crossover	2005-2008	188.7	69.7	63.2	2005 Subaru Outback wagon, Edmunds	跨界旅行	待补强: 2006-2008
Subaru Outback	Subaru	越野车	Wagon	Std.	gen3 crossover	2009	189.0	69.7	63.2	2009 Subaru Outback wagon, Edmunds	跨界旅行	可入库
Subaru Outback	Subaru	越野车	Wagon	Std.	gen4 crossover	2010-2013	188.2	71.7	65.7	2010/2011 Subaru Outback 2.5i / 3.6R, Edmunds	加高旅行	待补强: 2012-2013
Subaru Outback	Subaru	越野车	Wagon	Std.	gen4 crossover	2014	189.0	71.7	65.8	2014 Subaru Outback, Edmunds	加高旅行	可入库
Subaru Outback	Subaru	越野车	Wagon	Wilderness	gen6 crossover	2020-2024	191.3	74.6	66.9	2024 Subaru Outback Wilderness	含Wilderness	待补强: 2020-2023
Subaru Solterra	Subaru	越野车	SUV	EV	gen1 compact EV SUV	2023-2026	184.6	73.2	65.0	2023/2025/2026 Subaru Solterra Limited / Touring XT, Edmunds / C&D	EV SUV	待补强: 2024
Subaru Tribeca	Subaru	越野车	SUV	Std.	gen1 midsize SUV	2006-2007	189.8	73.9	66.4	2006/2007 Subaru B9 Tribeca, Edmunds	中型SUV	可入库
Subaru Tribeca	Subaru	越野车	SUV	Std.	gen1 midsize SUV facelift	2008-2014	191.5	73.9	67.7	2008/2014 Subaru Tribeca, Edmunds / C&D	中型SUV	待补强: 2009-2013高度需终核
Subaru WRX	Subaru	三厢车	Sedan	WRX/STI	gen1 performance	2002-2003	173.4	68.1	56.7	2002 Subaru Impreza WRX sedan	性能版	待补强: 2003
Subaru WRX	Subaru	两厢车	Wagon	WRX	gen1 performance	2002-2003	173.4	68.1	56.7	2002 Subaru Impreza WRX wagon	性能旅行版	待补强: 2003
Subaru WRX	Subaru	三厢车	Sedan	WRX/STI	gen1 facelift performance	2004-2007	175.8	68.5	56.3	2006/2007 Subaru Impreza WRX STI sedan, Edmunds	性能版	待补强: 2004-2005
Subaru WRX	Subaru	三厢车	Sedan	WRX/STI	gen2 performance	2008	173.8	68.5	58.1	2008 Subaru Impreza WRX, Edmunds	性能三厢/五门过渡	待补强: 2009-2013
Subaru WRX	Subaru	三厢车	Sedan	WRX/STI	gen2 performance	2014	180.3	70.7	58.1	2014 Subaru Impreza WRX sedan, Edmunds	性能三厢	可入库

下一步


--- Round 3 / 下一步 ---
更新点

车型	操作	描述
Toyota 86 gen1	稳定	2017-2020 尺寸一致，参考车型补足范围。
Toyota 86 / GR86 gen2	稳定	2022-2026 尺寸一致，参考车型补足范围。
Toyota Avalon gen5	稳定	2019-2022 尺寸一致，参考车型补足范围。
Toyota bZ4X	稳定	2023-2025 尺寸一致，参考车型补足范围。
Toyota Corolla Cross	稳定	2022-2026 gas/hybrid 外廓尺寸一致，参考车型补足范围。
Toyota Corolla GR	稳定	2023-2026 GR Corolla 尺寸一致，参考车型补足范围。
Tesla Model Y Performance	值修改	2026 Performance 高度为 63.4，不是 64.0；2025 仍需继续核对。

本轮 Toyota 86/GR86、Avalon、bZ4X、Corolla Cross、GR Corolla 主要依据 Edmunds 尺寸页：GR86 2025/2026 为 167.9 × 69.9 × 51.6，Avalon 2019/2022 为 195.9 × 72.8 × 56.5，bZ4X 2023/2025 为 184.6 × 73.2 × 65.0，Corolla Cross 2026 gas/hybrid 为 176.1 × 71.9 × 64.9，GR Corolla 2026 为 173.6 × 72.8 × 57.2。
Edmunds
+8
Edmunds
+8
Edmunds
+8
 Tesla Model Y Performance 2026 依据 Edmunds 和 Tesla owner manual，Performance 为 188.8 × 75.6 × 63.4。
Edmunds
+1

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Toyota 86	Toyota	跑车	Coupe	Std.	gen1 compact sports coupe	2017-2020	166.7	69.9	52.0	2017/2018/2019/2020 Toyota 86 GT, Edmunds	低矮双门跑车	可入库
Toyota 86	Toyota	跑车	Coupe	Std.	gen2 compact sports coupe	2022-2026	167.9	69.9	51.6	2022/2023/2024/2025/2026 Toyota GR86 Premium, Edmunds	第二代GR86车身	可入库
Toyota Avalon	Toyota	三厢车	Sedan	inc: hybrid	gen5 large sedan	2019-2022	195.9	72.8	56.5	2019/2020/2021/2022 Toyota Avalon / Avalon Hybrid, Edmunds	含混动车型	可入库
Toyota bZ4X	Toyota	越野车	SUV	EV	gen1 compact EV SUV	2023-2025	184.6	73.2	65.0	2023/2024/2025 Toyota bZ4X XLE / Limited, Edmunds	EV SUV	可入库
Toyota Corolla Cross	Toyota	越野车	SUV	inc: hybrid	gen1 compact SUV	2022-2026	176.1	71.9	64.9	2022/2023/2024/2025/2026 Toyota Corolla Cross / Corolla Cross Hybrid, Edmunds	小型SUV	可入库
Toyota Corolla GR	Toyota	两厢车	Hatchback	performance	gen1 hot hatch	2023-2026	173.6	72.8	57.2	2023/2024/2025/2026 Toyota GR Corolla, Edmunds	性能两厢	可入库
Tesla Model Y	Tesla	越野车	SUV	Performance	gen1 EV CUV facelift	2025	188.8	75.6	64.0	2025 Tesla Model Y Performance	EV	待补强: 2025 Performance高度/北美版本需终核
Tesla Model Y	Tesla	越野车	SUV	Performance	gen1 EV CUV facelift	2026	188.8	75.6	63.4	2026 Tesla Model Y Performance, Edmunds / Tesla owner manual	EV	可入库

下一步


--- Round 4 / 下一步 ---
更新点

车型	操作	描述
Toyota 4Runner gen3	拆出	1996、1997、1998 三年高度不同，不能继续压成 1996-1998。
Toyota 4Runner gen5	值修改	2010 Edmunds 高度为 71.5，不是原表 74.2；2014-2024 Edmunds 显示 191.3 × 75.8 × 71.5。
Toyota Camry gen2 Sedan	拆出	1991 Edmunds 可核到 182.1 × 67.4 × 54.1；1987-1990 继续待核。
Toyota Camry gen2 Wagon	稳定	1991 wagon Edmunds 为 183.1 × 67.4 × 54.5；1987-1990 继续待核。
Toyota Camry gen3 Wagon	稳定	1996 wagon Edmunds 为 189.4 × 69.7 × 57.1；1992-1995 继续待核。
Toyota Camry gen5 Sedan	值修改	2002 XLE V6 高度可到 58.3，原 58.3 保留；2003-2006 继续待核。

本轮 4Runner 主要依据 Edmunds：1996 为 178.7 × 66.5 × 68.7，1997 为 178.7 × 66.5 × 68.5，1998 为 178.7 × 66.5 × 67.5；2010 为 189.9 × 75.8 × 71.5，2014/2024 为 191.3 × 75.8 × 71.5。
Edmunds
+5
Edmunds
+5
Edmunds
+5

Camry 本轮主要依据 Edmunds：1991 sedan 为 182.1 × 67.4 × 54.1，1991 wagon 为 183.1 × 67.4 × 54.5，1996 wagon 为 189.4 × 69.7 × 57.1，2002 XLE V6 sedan 高度可到 58.3。
Edmunds
+3
Edmunds
+3
Edmunds
+3

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen3 mid-size	1996	178.7	66.5	68.7	1996 Toyota 4Runner Base / SR5 / Limited, Edmunds	中型SUV	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen3 mid-size	1997	178.7	66.5	68.5	1997 Toyota 4Runner, Edmunds	中型SUV	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen3 mid-size	1998	178.7	66.5	67.5	1998 Toyota 4Runner, Edmunds	中型SUV	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2010	189.9	75.8	71.5	2010 Toyota 4Runner, Edmunds	高车身越野SUV	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2011-2013	189.9	75.8	71.5	2010 Toyota 4Runner, Edmunds	高车身越野SUV	待补强: 2011-2013
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2014-2024	191.3	75.8	71.5	2014/2024 Toyota 4Runner, Edmunds	中大型越野SUV	待补强: 2015-2023
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen2 compact	1987-1990	177.2	67.1	55.1	1987 Toyota Camry Sedan / CarsGuide; 1991 Toyota Camry Sedan, Edmunds	紧凑三厢	待补强: 1987-1990
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen2 compact	1991	182.1	67.4	54.1	1991 Toyota Camry Sedan, Edmunds	紧凑三厢	可入库
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen2 compact	1987-1990	183.1	67.4	54.5	1991 Toyota Camry Wagon, Edmunds	长车顶	待补强: 1987-1990
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen2 compact	1991	183.1	67.4	54.5	1991 Toyota Camry Wagon Deluxe, Edmunds	长车顶	可入库
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen3 mid-size	1992-1995	189.4	69.7	57.1	1996 Toyota Camry Wagon, Edmunds	长车顶	待补强: 1992-1995
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen3 mid-size	1996	189.4	69.7	57.1	1996 Toyota Camry Wagon LE V6, Edmunds	长车顶	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2002	189.2	70.7	58.3	2002 Toyota Camry XLE V6, Edmunds	高车身三厢	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2003-2006	189.2	70.7	58.3	2002 Toyota Camry XLE V6, Edmunds	高车身三厢	待补强: 2003-2006

下一步


--- Round 5 / 下一步 ---
更新点

车型	操作	描述
Toyota Camry gen3 Sedan	拆出	1992-1995 与 1996 尺寸不同，拆分为两段。
Toyota Camry gen3 Wagon	拆出	1992-1995 与 1996 尺寸不同，拆分为两段。
Toyota Camry gen4 Sedan	拆出	1997-2001 尺寸稳定，但仍需核对中间年份 1998-2001 是否完全一致。
Toyota Camry gen5 Sedan	稳定	2002-2006 XLE V6 高度 58.3 in，已补参考车型，继续待核 2003-2006。
Toyota Celica gen1-7	拆出	各代 Coupe/Convertible/Hatchback/All-Trac 结构及年份跨度不同，需按实际尺寸拆分每代并标注 All-Trac / Liftback / Convertible 特殊版本。

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen3 mid-size	1992-1995	188.2	69.7	55.5	1996 Toyota Camry Sedan / CarsGuide / XV10 specs	中型三厢	待补强: 1992-1995
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen3 mid-size	1996	188.2	69.7	55.5	1996 Toyota Camry Sedan / CarsGuide / XV10 specs	中型三厢	可入库
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen3 mid-size	1992-1995	189.4	69.7	57.1	1996 Toyota Camry Wagon / Edmunds	长车顶	待补强: 1992-1995
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen3 mid-size	1996	189.4	69.7	57.1	1996 Toyota Camry Wagon / Edmunds	长车顶	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen4 mid-size	1997-2001	188.5	70.1	55.4	1997 Toyota Camry Sedan	中型三厢	待补强: 1998-2001
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2002-2006	189.2	70.7	58.3	2002 Toyota Camry LE / XLE	高车身三厢	待补强: 2003-2006
Toyota Celica	Toyota	跑车	Coupe	Std.	gen1 sport compact	1971-1972	171.5	64.4	52.0	1971/1972 Celica	早期低车身	可入库
Toyota Celica	Toyota	跑车	Coupe	Std.	gen1 sport compact	1973-1974	171.5	64.4	52.0	1971/1972 Celica;1975-1977 Liftback	早期低车身	待补强: 1973-1974
Toyota Celica	Toyota	跑车	Coupe	Std.	gen2 sport compact	1978-1981	173.2	65.0	52.4	1978/1981 Celica	尺寸过渡期	待补强: 1979-1980
Toyota Celica	Toyota	跑车	Coupe	Std.	gen3 sport compact	1982-1983	175.2	67.3	52.0	1982/1983/1985 Celica	车身加宽	待补强: 1984
Toyota Celica	Toyota	跑车	Coupe	Std.	gen3 sport compact	1985	175.2	67.3	52.0	1982/1983/1985 Celica	车身加宽	可入库
Toyota Celica	Toyota	跑车	Coupe	All-Trac	gen4 sport compact	1986-1987	176.4	67.3	51.4	1988 Celica All-Trac	四驱版尺寸最大	待补强: 1986-1987
Toyota Celica	Toyota	跑车	Coupe	All-Trac	gen4 sport compact	1988-1989	176.4	67.3	51.4	1988 Celica All-Trac	四驱版尺寸最大	可入库
Toyota Celica	Toyota	跑车	Coupe	All-Trac	gen5 sport compact	1990	176.0	68.7	51.2	1990 Celica Coupe	宽体All-Trac	可入库
Toyota Celica	Toyota	跑车	Coupe	All-Trac	gen5 sport compact	1991-1992	176.0	68.7	51.2	1990 Celica Coupe;1993 All-Trac	宽体All-Trac	待补强: 1991-1992
Toyota Celica	Toyota	跑车	Coupe	All-Trac	gen5 sport compact	1993	176.0	68.7	51.2	1990 Celica Coupe;1993 All-Trac	宽体All-Trac	可入库
Toyota Celica	Toyota	跑车	Convertible	Std.	gen6 sport compact	1994-1995	177.0	68.9	52.4	1996 Celica GT Convertible	敞篷高度最大	待补强: 1994-1995
Toyota Celica	Toyota	跑车	Convertible	Std.	gen6 sport compact	1997-1999	177.0	68.9	52.4	1996 Celica GT Convertible	敞篷高度最大	待补强: 1997-1999
Toyota Celica	Toyota	跑车	Hatchback	Std.	gen7 sport compact	2000	170.9	68.3	51.4	2001 Celica GT/GT-S	短车身Liftback	待补强: 2000
Toyota Celica	Toyota	跑车	Hatchback	Std.	gen7 sport compact	2001-2004	170.9	68.3	51.4	2001/2004 Celica GT/GT-S	短车身Liftback	待补强: 2002-2003
Toyota Celica	Toyota	跑车	Hatchback	Std.	gen7 sport compact	2005	170.9	68.3	51.4	2001/2004 Celica GT/GT-S	短车身Liftback	可入库

下一步


--- Round 6 / 下一步 ---
更新点

车型	操作	描述
Toyota C-HR	拆出/完成	2018-2019 为 171.2 × 70.7 × 61.6；2020-2022 为 172.6 × 70.7 × 61.6，不能合并为同一段。
Toyota 4Runner gen5	值修改	2011 Trail/SR5/Limited 普通高度 71.5，但 Edmunds trim 对比显示 Trail 可到 74.2；保留 2010-2013 原高车身口径继续补强。
Toyota 4Runner gen5 facelift	值修改	2023 TRD Pro 高度 72.0，普通 SR5/Limited 为 71.5；原 2014-2024 的 71.5 不能覆盖 TRD Pro 最大高度。
Tesla Model X	拆出	2016 Edmunds 宽度显示 81.5，与 2026 的 78.9 不一致；本轮先拆出 2016 待复核宽度口径。
Toyota Camry gen4	稳定	1997 与 2001 Edmunds 尺寸一致，1998-2000 仍需补齐参考覆盖。
Toyota Camry gen5	值修改	2006 Edmunds 高度为 58.7，高于原 58.3；2002-2006 不能继续压成同一尺寸。

本轮 C-HR 依据 Edmunds：2018/2019 为 171.2 × 70.7 × 61.6，2020/2021/2022 为 172.6 × 70.7 × 61.6。
Edmunds
+4
Edmunds
+4
Edmunds
+4

4Runner 依据 Edmunds：2011 常规尺寸为 189.9 × 75.8 × 71.5，但 trim 对比页显示 Trail 高度可到 74.2；2023 普通页为 191.3 × 75.8 × 71.5，TRD Pro 为 191.3 × 75.8 × 72.0。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Model X 依据 Edmunds：2016 页给出 198.3 长、81.5 w/o mirrors；2026 页为 199.1 × 78.9 × 66.1，因此原 2016-2026 不能直接压成一段。
Edmunds
+1

Camry 依据 Edmunds：1997/2001 gen4 sedan 均为 188.5 × 70.1 × 55.4；2006 gen5 sedan 为 189.2 × 70.7 × 58.7，高于原表 58.3。
Edmunds
+2
Edmunds
+2

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Toyota C-HR	Toyota	越野车	CUV	Std.	gen1 subcompact CUV	2018-2019	171.2	70.7	61.6	2018/2019 Toyota C-HR XLE / LE, Edmunds	轿跑化小型CUV	可入库
Toyota C-HR	Toyota	越野车	CUV	Std.	gen1 subcompact CUV facelift	2020-2022	172.6	70.7	61.6	2020/2021/2022 Toyota C-HR LE / Limited, Edmunds	小改款略长	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2010	189.9	75.8	74.2	2010 Toyota 4Runner Trail, Edmunds	高车身越野版	待补强: Trail高度需与2011-2013逐年确认
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2011	189.9	75.8	74.2	2011 Toyota 4Runner trims, Edmunds	高车身越野版	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2012-2013	189.9	75.8	74.2	2011 Toyota 4Runner trims, Edmunds	高车身越野版	待补强: 2012-2013 Trail高度
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2014-2022	191.3	75.8	72.0	2023 Toyota 4Runner TRD Pro, Edmunds	TRD Pro更高	待补强: 2014-2022 TRD Pro高度
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2023	191.3	75.8	72.0	2023 Toyota 4Runner TRD Pro, Edmunds	TRD Pro更高	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2024	191.3	75.8	72.0	2023 Toyota 4Runner TRD Pro, Edmunds	TRD Pro更高	待补强: 2024 TRD Pro高度
Tesla Model X	Tesla	越野车	SUV	EV	gen1 midsize EV SUV	2016	198.3	81.5	66.1	2016 Tesla Model X, Edmunds; 2026 Tesla Model X, Edmunds	EV SUV	待补强: 2016宽度口径与高度需终核
Tesla Model X	Tesla	越野车	SUV	EV	gen1 midsize EV SUV	2017-2025	199.1	78.9	66.1	2026 Tesla Model X, Edmunds	EV SUV	待补强: 2017-2025
Tesla Model X	Tesla	越野车	SUV	EV	gen1 midsize EV SUV	2026	199.1	78.9	66.1	2026 Tesla Model X, Edmunds	EV SUV	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen4 mid-size	1997	188.5	70.1	55.4	1997 Toyota Camry Sedan, Edmunds	中型三厢	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen4 mid-size	1998-2000	188.5	70.1	55.4	1997/2001 Toyota Camry Sedan, Edmunds	中型三厢	待补强: 1998-2000
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen4 mid-size	2001	188.5	70.1	55.4	2001 Toyota Camry LE, Edmunds	中型三厢	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2002	189.2	70.7	58.3	2002 Toyota Camry XLE V6, Edmunds	高车身三厢	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2003-2005	189.2	70.7	58.3	2002 Toyota Camry XLE V6, Edmunds	高车身三厢	待补强: 2003-2005
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2006	189.2	70.7	58.7	2006 Toyota Camry XLE V6 / LE, Edmunds	高车身三厢	可入库

下一步


--- Round 7 / 下一步 ---
更新点

车型	操作	描述
Toyota 4Runner gen2	值修改	1990 Edmunds 显示宽度 70.9，但 1995 为 66.5，存在年份/trim 口径差异，不能继续压成 1990-1995。
Toyota 4Runner gen2	拆出	1995 可单独入库；1990-1994 继续待补强。
Toyota Camry gen3 Sedan/Wagon	值修改	1992 Edmunds 显示 189.4 × 69.7 × 56.3，高于原 gen3 sedan 188.2 × 69.7 × 55.5，需继续拆分 sedan/wagon 最大 trim。
Toyota Camry gen4 Sedan	稳定	1997 与 2001 Edmunds 均为 188.5 × 70.1 × 55.4，中间年份仍需补参考覆盖。
Toyota Camry gen5 Sedan	值修改	2002 Edmunds 基础页为 189.2 × 70.7 × 57.9；上一轮保留 XLE V6 58.3，但 2006 可到 58.7，需拆开。

4Runner 本轮依据 Edmunds：1990 Toyota 4Runner 为 176.0 × 70.9 × 66.1，1995 Toyota 4Runner 为 176.0 × 66.5 × 66.1；1996/2001/2010 的 Edmunds 结果也显示不同代际尺寸差异明显，不能跨代合并。
Edmunds
+4
Edmunds
+4
Edmunds
+4
 Camry 本轮依据 Edmunds：1992 Camry 为 189.4 × 69.7 × 56.3，1997 Camry 为 188.5 × 70.1 × 55.4，2002 Camry 为 189.2 × 70.7 × 57.9。
Edmunds
+2
Edmunds
+2

阶段性 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen2 compact	1990	176.0	70.9	66.1	1990 Toyota 4Runner, Edmunds	4dr紧凑SUV	待补强: 1990宽度口径需终核
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen2 compact	1991-1994	176.0	66.5	66.1	1995 Toyota 4Runner, Edmunds	4dr紧凑SUV	待补强: 1991-1994
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen2 compact	1995	176.0	66.5	66.1	1995 Toyota 4Runner, Edmunds	4dr紧凑SUV	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen3 mid-size	1992	189.4	69.7	56.3	1992 Toyota Camry, Edmunds	中型三厢	待补强: sedan/wagon结构口径需终核
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen3 mid-size	1993-1995	188.2	69.7	55.5	1996 Toyota Camry Sedan / CarsGuide / XV10 specs	中型三厢	待补强: 1993-1995
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen3 mid-size	1996	188.2	69.7	55.5	1996 Toyota Camry Sedan / CarsGuide / XV10 specs	中型三厢	可入库
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen3 mid-size	1992	189.4	69.7	56.3	1992 Toyota Camry, Edmunds	长车顶	待补强: wagon结构口径需终核
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen3 mid-size	1993-1995	189.4	69.7	57.1	1996 Toyota Camry Wagon, Edmunds	长车顶	待补强: 1993-1995
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen3 mid-size	1996	189.4	69.7	57.1	1996 Toyota Camry Wagon, Edmunds	长车顶	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen4 mid-size	1997	188.5	70.1	55.4	1997 Toyota Camry Sedan, Edmunds	中型三厢	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen4 mid-size	1998-2000	188.5	70.1	55.4	1997/2001 Toyota Camry Sedan, Edmunds	中型三厢	待补强: 1998-2000
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen4 mid-size	2001	188.5	70.1	55.4	2001 Toyota Camry LE, Edmunds	中型三厢	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2002	189.2	70.7	58.3	2002 Toyota Camry XLE V6, Edmunds	高车身三厢	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2003-2005	189.2	70.7	58.3	2002 Toyota Camry XLE V6, Edmunds	高车身三厢	待补强: 2003-2005
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2006	189.2	70.7	58.7	2006 Toyota Camry XLE V6 / LE, Edmunds	高车身三厢	可入库

下一步


--- Round 8 / 下一步 ---
继续推进 Toyota Celica 后续代（gen6 / gen7 Convertible / Hatchback）以及 All-Trac 特殊版本的待核年份，优先处理 1994-2005 年段，拆分敞篷、Liftback、All-Trac，以确保尺寸和参考车型覆盖完整。

