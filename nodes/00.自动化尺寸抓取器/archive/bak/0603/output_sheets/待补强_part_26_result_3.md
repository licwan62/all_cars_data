# 文件名：待补强_part_26.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作	描述
Subaru Legacy gen1 Sedan	拆出 / 值修改	1990-1991 与 1992-1994 长度/高度不同，不能压成同一行；已按 Edmunds 年份点拆分。
Subaru Legacy gen1 Wagon	拆出 / 值修改	1990-1991 与 1992-1994 长度不同；Wagon 高度取 AWD/LS 等高值 56.3。
Subaru Legacy gen2 Sedan	拆出 / 值修改	1995-1996 与 1997-1999 长度/高度不同，拆分后推进。
Subaru Legacy gen3/gen4/gen5/gen6/gen7	稳定	已补入更多 Edmunds 年份点，部分区间仍需继续补齐中间年份。

本轮主要依据 Edmunds：1990/1991/1992/1993/1994 Legacy Sedan/Wagon、1995/1996/1997/1999 Legacy Sedan、2004 Sedan/Wagon、2005/2006/2007 Wagon、2010/2014/2015/2019/2025 Legacy 尺寸页；其中 1990-1994 Legacy 的年份点显示 gen1 前后期长度不同，1995-1999 sedan 也存在前后期长度/高度变化。
Edmunds
+20
Edmunds
+20
Edmunds
+20

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen1 compact	1990-1991	177.6	66.5	54.3	1990/1991 Subaru Legacy Sedan, Edmunds	早期gen1 sedan	待补强: 1991 AWD最高点
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen1 compact facelift	1992-1994	178.9	66.5	53.5	1992/1993/1994 Subaru Legacy Sedan, Edmunds	后期gen1 sedan更长	可入库
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen1 compact	1990-1991	181.1	66.5	56.3	1990/1991 Subaru Legacy Wagon, Edmunds	早期AWD wagon更高	待补强: 1991 LS/AWD最高点
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen1 compact facelift	1992-1994	181.9	66.5	56.3	1992/1993/1994 Subaru Legacy Wagon, Edmunds	后期wagon更长	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen2 compact	1995-1996	180.9	67.5	55.3	1995/1996 Subaru Legacy Sedan, Edmunds	二代前期sedan	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen2 compact facelift	1997-1999	181.5	67.5	55.7	1997/1998/1999 Subaru Legacy Sedan GT, Edmunds	后期GT高度最大	待补强: 1998
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen3 compact	2000-2004	184.4	68.7	55.7	2004 Subaru Legacy Sedan, Edmunds	三代sedan	待补强: 2000-2003
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen3 compact	2000-2004	187.4	68.7	59.6	2004 Subaru Legacy Wagon, Edmunds	三代wagon	待补强: 2000-2003
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen4 compact	2005-2007	188.7	68.1	58.1	2005/2006/2007 Subaru Legacy Wagon, Edmunds	四代wagon	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen5 large	2010-2014	187.2	71.7	59.3	2010/2014 Subaru Legacy Sedan, Edmunds	五代sedan	待补强: 2011-2013
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen6 large	2015-2019	189.1	72.4	59.0	2015/2019 Subaru Legacy Sedan, Edmunds	六代sedan	待补强: 2016-2018
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen7 large	2020-2025	191.1	72.4	59.1	2025 Subaru Legacy, Edmunds	七代sedan	待补强: 2020-2024

下一步。

--- Round 2 / 人工 ---

主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen1 compact	1990-1991	177.6	66.5	54.3	1990-1991 Subaru Legacy Sedan, Edmunds	早期gen1 sedan	可入库
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen1 compact	1990-1991	181.1	66.5	56.3	1990-1991 Subaru Legacy Wagon, Edmunds	早期AWD wagon更高	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen1 compact facelift	1992-1994	178.9	66.5	53.5	1992-1994 Subaru Legacy Sedan, Edmunds	后期gen1 sedan更长	可入库
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen1 compact facelift	1992-1994	181.9	66.5	56.3	1992-1994 Subaru Legacy Wagon, Edmunds	后期wagon更长	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen2 compact	1995-1996	180.9	67.5	55.3	1995-1996 Subaru Legacy Sedan, Edmunds	二代前期sedan	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen2 compact facelift	1997-1999	181.5	67.5	55.7	1997-1999 Subaru Legacy Sedan GT, Edmunds	后期GT高度最大	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen3 compact	2000-2004	184.4	68.7	55.7	2000-2004 Subaru Legacy Sedan, Edmunds	三代sedan	可入库
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen3 compact	2000-2004	187.4	68.7	59.6	2000-2004 Subaru Legacy Wagon, Edmunds	三代wagon	可入库
Subaru Legacy	Subaru	三厢车	Wagon	Std.	gen4 compact	2005-2007	188.7	68.1	58.1	2005-2007 Subaru Legacy Wagon, Edmunds	四代wagon	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen5 large	2010-2014	187.2	71.7	59.3	2010-2014 Subaru Legacy Sedan, Edmunds	五代sedan	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen6 large	2015-2019	189.1	72.4	59.0	2015-2019 Subaru Legacy Sedan, Edmunds	六代sedan	可入库
Subaru Legacy	Subaru	三厢车	Sedan	Std.	gen7 large	2020-2025	191.1	72.4	59.1	2020-2025 Subaru Legacy, Edmunds	七代sedan	可入库
Subaru Outback	Subaru	越野车	Wagon	Std.	gen1 crossover	1995-1999	186.6	68.3	63.0	1995-1999 Subaru Outback Wagon, Edmunds	早期跨界旅行	可入库
Subaru Outback	Subaru	越野车	Wagon	Std.	gen2 crossover	2000-2004	187.4	68.7	63.2	2000-2004 Subaru Outback Wagon, Edmunds	跨界旅行	可入库
Subaru Outback	Subaru	越野车	Wagon	Std.	gen3 crossover	2005-2009	189.0	69.7	63.2	2005-2009 Subaru Outback Wagon, Edmunds	跨界旅行	可入库
Subaru Outback	Subaru	越野车	Wagon	Std.	gen4 crossover	2010-2014	188.2	71.7	65.7	2010-2014 Subaru Outback 2.5i / 3.6R, Edmunds	加高旅行	可入库
Subaru Outback	Subaru	越野车	Wagon	Wilderness	gen6 crossover	2022-2024	191.3	74.6	66.9	2022-2024 Subaru Outback Wilderness, Edmunds	Wilderness加高越野旅行	可入库
Subaru Solterra	Subaru	越野车	SUV	EV	gen1 compact EV SUV	2023-2026	184.6	73.2	65.0	2023-2026 Subaru Solterra Limited / Touring XT, Edmunds	EV SUV	可入库
Subaru Tribeca	Subaru	越野车	SUV	Std.	gen1 midsize SUV	2006-2014	191.5	73.9	67.7	2006-2014 Subaru Tribeca, Edmunds / C&D	中型SUV	可入库
Subaru WRX	Subaru	三厢车	Sedan	WRX	gen1 performance	2002	173.4	68.1	56.7	2002 Subaru Impreza WRX sedan, Edmunds	性能版	可入库
Subaru WRX	Subaru	两厢车	Wagon	WRX	gen1 performance	2002	173.4	68.1	56.7	2002 Subaru Impreza WRX wagon, Edmunds	性能旅行版	可入库
Subaru WRX	Subaru	两厢车	Wagon	WRX	gen1 performance	2003	173.4	68.1	56.7	2003 Subaru Impreza WRX wagon, Edmunds	性能旅行版	可入库
Subaru WRX	Subaru	三厢车	Sedan	WRX/STI	gen1 facelift performance	2004-2007	175.8	68.5	56.3	2004-2007 Subaru Impreza WRX STI, Edmunds	性能版	可入库
Subaru WRX	Subaru	三厢车	Sedan	WRX/STI	gen2 performance	2008-2014	180.3	70.7	58.1	2008-2014 Subaru Impreza WRX sedan, Edmunds	性能三厢	可入库
Tesla Model X	Tesla	越野车	SUV	EV	gen1 midsize EV SUV	2016-2026	199.1	78.9	66.1	2016-2026 Tesla Model X	EV SUV	可入库
Tesla Model Y	Tesla	越野车	SUV	Performance	gen1 EV CUV facelift	2025-2026	188.8	75.6	64.0	2025-2026 Tesla Model Y Performance	EV	可入库
Toyota 4Runner	Toyota	越野车	SUV	2dr	gen1 compact	1984-1989	174.6	66.5	66.1	1984-1989 Toyota 4Runner 2dr	2dr高车身SUV	可入库
Toyota 4Runner	Toyota	越野车	SUV	4dr	gen2 compact	1990-1995	176.0	66.5	68.1	1990-1995 Toyota 4Runner 4dr	4dr紧凑SUV	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen3 mid-size	1996-1998	178.7	66.5	68.7	1996-1998 Toyota 4Runner SR5 / Limited	中型SUV	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2010-2013	189.9	75.8	74.2	2010-2013 Toyota 4Runner Trail / Edmunds	高车顶越野版	可入库
Toyota 4Runner	Toyota	越野车	SUV	Std.	gen5 mid-size	2014-2024	191.3	75.8	71.5	2014-2024 Toyota 4Runner, Edmunds	中大型越野SUV	可入库
Toyota 86	Toyota	跑车	Coupe	Std.	gen1 compact sports coupe	2017-2020	166.7	69.9	52.0	2017-2020 Toyota 86 GT, Edmunds	低矮双门跑车	可入库
Toyota 86	Toyota	跑车	Coupe	Std.	gen2 compact sports coupe	2022-2026	167.9	69.9	51.6	2022-2026 Toyota GR86 Premium, Edmunds	第二代GR86车身	可入库
Toyota Avalon	Toyota	三厢车	Sedan	inc: hybrid	gen5 large sedan	2019-2022	195.9	72.8	56.5	2019-2022 Toyota Avalon / Avalon Hybrid, Edmunds	含混动车型	可入库
Toyota bZ4X	Toyota	越野车	SUV	EV	gen1 compact EV SUV	2023-2025	184.6	73.2	65.0	2023-2025 Toyota bZ4X, Edmunds / TheCarConnection	EV SUV	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen1 compact	1983-1986	175.6	66.5	54.9	1983-1986 Toyota Camry Sedan / Toyota brochure / Auto-Data	早期紧凑三厢	可入库
Toyota Camry	Toyota	两厢车	Hatchback	Std.	gen1 compact	1983-1986	174.6	66.5	53.9	1983-1986 Toyota Camry Liftback / Cars-Data	早期liftback轮廓	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen2 compact	1987-1991	177.2	67.1	55.1	1987-1991 Toyota Camry Sedan / CarsGuide	紧凑三厢	可入库
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen2 compact	1987-1991	183.1	67.4	54.5	1987-1991 Toyota Camry Wagon / Edmunds	长车顶	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen3 mid-size	1992-1996	188.2	69.7	55.5	1992-1996 Toyota Camry Sedan / CarsGuide / XV10 specs	中型三厢	可入库
Toyota Camry	Toyota	两厢车	Wagon	Std.	gen3 mid-size	1992-1996	189.4	69.7	57.1	1992-1996 Toyota Camry Wagon / Edmunds	长车顶	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen4 mid-size	1997-2001	188.5	70.1	55.4	1997-2001 Toyota Camry Sedan, Edmunds	中型三厢	可入库
Toyota Camry	Toyota	三厢车	Sedan	Std.	gen5 mid-size	2002-2006	189.2	70.7	58.7	2002-2006 Toyota Camry LE / XLE, Edmunds	高车身三厢	可入库
Toyota Celica	Toyota	跑车	Coupe	Std.	gen1 sport compact	1971-1977	171.5	64.4	52.0	1971-1977 Toyota Celica / Liftback, Edmunds	早期低车身	可入库
Toyota Celica	Toyota	跑车	Coupe	Std.	gen2 sport compact	1978-1981	173.2	65.0	52.4	1978-1981 Toyota Celica, Edmunds	尺寸过渡期	可入库
Toyota Celica	Toyota	跑车	Coupe	Std.	gen3 sport compact	1982-1985	175.2	67.3	52.0	1982-1985 Toyota Celica, Edmunds	车身加宽	可入库
Toyota Celica	Toyota	跑车	Coupe	All-Trac	gen4 sport compact	1986-1989	176.4	67.3	51.4	1986-1989 Toyota Celica All-Trac, Edmunds	四驱版尺寸最大	可入库
Toyota Celica	Toyota	跑车	Coupe	All-Trac	gen5 sport compact	1990-1993	176.0	68.7	51.2	1990-1993 Toyota Celica / All-Trac, Edmunds	宽体All-Trac	可入库
Toyota Celica	Toyota	跑车	Convertible	Std.	gen6 sport compact	1994-1999	177.0	68.9	52.4	1994-1999 Toyota Celica GT Convertible, Edmunds	敞篷高度最大	可入库
Toyota Celica	Toyota	跑车	Hatchback	Std.	gen7 sport compact	2000-2005	170.9	68.3	51.4	2000-2005 Toyota Celica GT/GT-S, Edmunds	短车身Liftback	可入库
Toyota C-HR	Toyota	越野车	CUV	Std.	gen1 subcompact CUV	2018-2019	171.2	70.7	61.6	2018-2019 Toyota C-HR XLE, Edmunds	轿跑化小型CUV	可入库
Toyota C-HR	Toyota	越野车	CUV	Std.	gen1 subcompact CUV facelift	2020-2022	172.6	70.7	61.6	2020-2022 Toyota C-HR Limited, Edmunds	小改款略长	可入库
Toyota Corolla Cross	Toyota	越野车	SUV	inc: hybrid	gen1 compact SUV	2022-2026	176.1	71.9	64.9	2022-2026 Toyota Corolla Cross / Corolla Cross Hybrid, Edmunds	小型SUV	可入库
Toyota Corolla GR	Toyota	两厢车	Hatchback	performance	gen1 hot hatch	2023-2026	173.6	72.8	57.2	2023-2026 Toyota GR Corolla, Edmunds	性能两厢	可入库