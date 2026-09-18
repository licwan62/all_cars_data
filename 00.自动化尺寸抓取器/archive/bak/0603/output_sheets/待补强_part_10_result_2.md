# 文件名：待补强_part_10.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作/字段	描述
Honda Accord	参考车型/状态	2023 与 2026 Accord 三维一致，已把 2023-2026 参考车型改成覆盖区间，可入库。
Edmunds
+1

Honda Accord	状态	1994 wagon 与 1997 wagon Edmunds 数据存在 187.8/55.9 与 188.4/56.0 差异，1994-1997 不应直接整段可入库，继续待终核。
Edmunds
+1

Honda Clarity	参考车型/状态	已补 2017/2019/2020/2021 Clarity 关键年份，三维一致；2018 未在本轮完成，保留待终核。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Honda Crosstour / CR-V	参考车型	已补 2010 Crosstour、2015 Crosstour、1997/2001 CR-V 来源；中间年份未全量核完，继续保留待补强。
Edmunds
+3
Edmunds
+3
Edmunds
+3

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991-1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	待补强: 1991-1992
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990-1993	186.8	67.5	53.2	1993 Honda Accord Wagon EX, Edmunds	wagon更长更宽	待补强: 1990-1992
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽；Wagon车顶/尾厢需保留结构	待补强: 1994-1996
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1997	188.4	70.1	56.0	1994/1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	待终核: 1995-1996；1994尺寸低于1997需判断是否拆分
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1997	185.6	70.1	54.7	1997 Honda Accord Coupe, Edmunds	双门低车顶	待补强: 1994-1996
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2002	189.4	70.3	57.3	2002 Honda Accord Sedan, Edmunds		待补强: 1998-2001
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998-2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	待补强: 1998-2001
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2007	191.1	71.6	57.2	2003/2007 Honda Accord Sedan, Edmunds		待补强: 2004-2006
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.8	71.3	55.7	2003/2007 Honda Accord Coupe, Edmunds	双门低车顶	待补强: 2004-2006
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	待补强: 2008-2011
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2012 Honda Accord Coupe, Edmunds	双门较短低车顶	待补强: 2008-2011
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2017	192.5	72.8	57.7	2013/2017 Honda Accord Sedan, Edmunds		待补强: 2014-2016
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2017	189.5	73.0	56.5	2013/2017 Honda Accord Coupe LX-S, Edmunds	双门较短	待补强: 2014-2016
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023-2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1991	168.8	66.7	53.5	1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1990
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1991	157.1	66.3	52.5	1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1990
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1991	161.7	66.1	56.9	1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1990
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1991	148.5	65.9	50.1	1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1990
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992-1995	173.0	66.9	51.7	1993/1995 Honda Civic Sedan, Edmunds		待补强: 1992/1994
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1992-1995	172.8	66.9	50.9	1995 Honda Civic Coupe, Edmunds	双门低车顶	待补强: 1992-1994
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992-1995	160.2	66.9	50.7	1995 Honda Civic Hatchback, Edmunds	短车身低车顶	待补强: 1992-1994
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	2000 Honda Civic Sedan, Edmunds		待补强: 1996-1999
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	2000 Honda Civic Coupe, Edmunds	双门较低	待补强: 1996-1999
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	2000 Honda Civic Hatchback CX, Edmunds	短车身hatch	待补强: 1996-1999
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2005	175.4	67.5	56.7	2005 Honda Civic Sedan, Edmunds		待补强: 2001-2004
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2005	175.4	66.7	55.1	2005 Honda Civic Coupe, Edmunds	双门更窄更低	待补强: 2001-2004
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006-2011	177.3	69.0	56.5	2006/2011 Honda Civic Sedan, Edmunds		待补强: 2007-2010
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006-2011	175.5	68.9	55.0	2011 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2006-2010
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012-2015	179.4	69.0	56.5	2012/2015 Honda Civic Sedan, Edmunds		待补强: 2013-2014
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012-2015	177.9	69.0	55.0	2012/2015 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2013-2014
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2021	182.7	70.9	55.7	2021 Honda Civic Sedan, Edmunds		待补强: 2016-2020
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	待补强: 2017-2020
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2021 Honda Civic Type R, Edmunds	宽体性能版	待补强: 2017-2020
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	待补强: 2022-2024
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	待补强: 2022-2025
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2022-2026	180.9	74.4	55.4	2024/2025/2026 Honda Civic Type R, Edmunds / Honda	宽体性能版	待补强: 2022-2023
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	待终核: 2018
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	待补强: 2018-2019
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010 Honda Accord Crosstour, Edmunds	5门跨界hatch	待补强: 2011-2012
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013-2015	196.6	74.7	61.5	2015 Honda Crosstour, Edmunds / Honda News	后期车高降低	待补强: 2013-2014
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/2001 Honda CR-V, Edmunds	初代CR-V	待补强: 1998-2000

下一步


--- Round 2 / 下一步 ---
更新点

车型	操作/字段	描述
Honda Accord 1990-1993 Wagon	值修改/状态	1991 wagon 为 186.0 / 67.9 / 55.1，1993 wagon 为 186.8 / 67.5 / 53.2，区间三维不一致，不能整段标可入库。
Edmunds
+1

Honda Accord 1994-1997 Wagon	值修改/状态	1994/1995 wagon 为 187.8 / 70.1 / 55.9，1996 wagon 为 188.4 / 70.1 / 57.4，原 1994-1997 整段需要拆分或继续补 1997。
Edmunds
+2
Edmunds
+2

Honda Accord 1994-1997 Coupe	值修改/状态	1994/1995 coupe 为 184.0 / 70.1 / 54.7，1996 coupe 为 185.6 / 70.1 / 54.7，原整段 185.6 需要继续补 1997 后再拆分。
Edmunds
+2
Edmunds
+2

Honda Accord 1998-2002 Sedan/Coupe	值修改/状态	1998/1999/2000 sedan 与 coupe 均出现尺寸差异，不能用单个 2002 参考覆盖 1998-2002。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Honda Accord 2003-2007 Sedan/Coupe	参考车型	已补 2003 与 2005/2007 关键点，仍缺 2004/2006，继续待补强。
Edmunds
+1

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991-1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	待补强: 1991-1992
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990-1993	186.8	67.9	55.1	1991/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990/1992；1991与1993三维不一致，需判断拆分
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1997	188.4	70.1	56.0	1994/1995/1997 Honda Accord Sedan, Edmunds	Sedan/Wagon同长宽；Wagon车顶/尾厢需保留结构	待终核: 1996；1994-1997疑似年份差异需拆分判断
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1997	188.4	70.1	57.4	1994/1995/1996 Honda Accord Wagon, Edmunds	Wagon高尾厢	待终核: 1997；1994-1995与1996三维不一致，需拆分
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1997	185.6	70.1	54.7	1994/1995/1996 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1997；1994-1995与1996长度不一致，需拆分
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2002	189.4	70.3	57.3	1998/1999/2000/2002 Honda Accord Sedan, Edmunds		待终核: 2001；1998-2000与2002尺寸需拆分判断
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998-2002	188.8	70.3	56.9	1998/1999/2000/2002 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 2001；1998-2000与2002尺寸需拆分判断
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2007	191.1	71.6	57.2	2003/2007 Honda Accord Sedan, Edmunds		待补强: 2004-2006
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.8	71.3	55.7	2003/2005/2007 Honda Accord Coupe, Edmunds	双门低车顶	待补强: 2004/2006
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2012	194.9	72.7	58.1	2008/2012 Honda Accord Sedan, Edmunds	八代sedan较长	待补强: 2009-2011
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	待补强: 2008-2010
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2017	192.5	72.8	57.7	2013/2017 Honda Accord Sedan, Edmunds		待补强: 2014-2016
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2017	189.5	73.0	56.5	2013/2015/2016/2017 Honda Accord Coupe LX-S, Edmunds	双门较短	待补强: 2014
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023-2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1991	168.8	66.7	53.5	1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1990
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1991	157.1	66.3	52.5	1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1990
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1991	161.7	66.1	56.9	1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1990
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1991	148.5	65.9	50.1	1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1990
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992-1995	173.0	66.9	51.7	1993/1995 Honda Civic Sedan, Edmunds		待补强: 1992/1994
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1992-1995	172.8	66.9	50.9	1995 Honda Civic Coupe, Edmunds	双门低车顶	待补强: 1992-1994
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992-1995	160.2	66.9	50.7	1995 Honda Civic Hatchback, Edmunds	短车身低车顶	待补强: 1992-1994
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	2000 Honda Civic Sedan, Edmunds		待补强: 1996-1999
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	2000 Honda Civic Coupe, Edmunds	双门较低	待补强: 1996-1999
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	2000 Honda Civic Hatchback CX, Edmunds	短车身hatch	待补强: 1996-1999
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2005	175.4	67.5	56.7	2005 Honda Civic Sedan, Edmunds		待补强: 2001-2004
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2005	175.4	66.7	55.1	2005 Honda Civic Coupe, Edmunds	双门更窄更低	待补强: 2001-2004
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006-2011	177.3	69.0	56.5	2006/2011 Honda Civic Sedan, Edmunds		待补强: 2007-2010
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006-2011	175.5	68.9	55.0	2011 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2006-2010
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012-2015	179.4	69.0	56.5	2012/2015 Honda Civic Sedan, Edmunds		待补强: 2013-2014
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012-2015	177.9	69.0	55.0	2012/2015 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2013-2014
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2021	182.7	70.9	55.7	2021 Honda Civic Sedan, Edmunds		待补强: 2016-2020
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	待补强: 2017-2020
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2021 Honda Civic Type R, Edmunds	宽体性能版	待补强: 2017-2020
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	待补强: 2022-2024
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	待补强: 2022-2025
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2022-2026	180.9	74.4	55.4	2024/2025/2026 Honda Civic Type R, Edmunds / Honda	宽体性能版	待补强: 2022-2023
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	待终核: 2018
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	待补强: 2018-2019
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010 Honda Accord Crosstour, Edmunds	5门跨界hatch	待补强: 2011-2012
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013-2015	196.6	74.7	61.5	2015 Honda Crosstour, Edmunds / Honda News	后期车高降低	待补强: 2013-2014
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/2001 Honda CR-V, Edmunds	初代CR-V	待补强: 1998-2000

下一步


--- Round 3 / 下一步 ---
更新点

车型	操作	描述
Accord / Crosstour	拆出	Accord sedan / coupe 已按 2013-2015 与 2016-2017 拆开；Crosstour 已按 2013 与 2014-2015 拆开；2010-2012 Accord Crosstour 已推进为可入库。基于 Edmunds 已核到：2014/2015 Accord sedan 为 191.4×72.8×57.7，2017 Accord sedan 为 192.5×72.8×57.7；2015 Accord coupe 为 189.2×72.8×56.5，2017 Accord coupe 为 189.5×73.0×56.5；2011/2012 Accord Crosstour 为 196.8×74.7×65.7，2013 Crosstour 为 196.6×74.7×65.7，2014/2015 Crosstour 为 196.6×74.7×61.5。【turn796816view2†L186-L199】【turn796816view0†L182-L193】【turn796816view4†L176-L187】【turn796816view1†L182-L193】【turn796816view5†L183-L194】【turn578524view0†L191-L205】【turn578524view1†L195-L211】【turn578524view2†L195-L210】【turn578524view3†L180-L195】【turn381991search0†L1-L4】
Civic	拆出	Civic sedan 已按 2022-2024 与 2025-2026 拆开；Civic hatchback Std. 2022-2026 已补齐到可入库；Civic Type R 调整为 2023-2026 可入库。已核到：2024 Civic sedan 184.0×70.9×55.7，2025/2026 Civic sedan 184.8×70.9×55.7；2022-2026 Civic hatchback 均为 179.0×70.9×55.7；2023-2026 Civic Type R 均为 180.9×74.4×55.4。【turn578524view6†L182-L193】【turn578524view7†L186-L197】【turn827182view0†L185-L197】【turn519302view0†L183-L194】【turn985398view0†L175-L186】【turn985398view1†L183-L194】【turn519302view1†L187-L198】【turn827182view1†L177-L188】【turn519302view2†L185-L196】【turn519302view3†L177-L191】【turn519302view4†L178-L192】【turn519302view5†L178-L192】
CR-V	稳定	CR-V 1997-2001 已补齐 1998/1999/2000，区间推进为可入库；1998/1999/2000 均核到 177.6×68.9×65.9。【turn968983search2†L1-L4】【turn968983search2†L5-L13】【turn578524view4†L157-L167】【turn578524view5†L158-L170】

当前阶段完整 TSV

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	三厢车	Sedan	Std.	gen3 compact	1986-1989	181.1	68.1	54.1	1986/1988/1989 Honda Accord Sedan		待终核: 1987
Honda Accord	Honda	三厢车	Sedan	Std.	gen4 midsize	1990-1993	185.2	67.7	54.1	1990/1991/1992/1993 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen3 compact	1988-1989	181.1	66.7	52.4	1988/1989 Honda Accord Coupe		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen4 midsize	1990-1993	185.2	67.7	53.9	1990/1991/1992/1993 Honda Accord Coupe		可入库
Honda Accord	Honda	三厢车	Wagon	Std.	gen4 midsize	1991-1993	187.8	67.7	55.1	1991/1992/1993 Honda Accord Wagon		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1997	185.6	70.1	54.5	1994/1995/1996/1997 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen5 midsize	1994-1997	186.6	70.1	54.6	1994/1995/1996/1997 Honda Accord Coupe		可入库
Honda Accord	Honda	三厢车	Wagon	Std.	gen5 midsize	1994-1997	188.4	70.1	57.4	1994/1995/1996/1997 Honda Accord Wagon		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 midsize	1998-2002	189.4	70.3	56.1	1998/1999/2000/2001/2002 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen6 midsize	1998-2002	188.8	69.1	55.1	1998/1999/2000/2001/2002 Honda Accord Coupe		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 midsize	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen7 midsize	2003-2005	188.9	71.5	55.7	2003/2004/2005 Honda Accord Coupe		可入库
Honda Accord	Honda	三厢车	Sedan	hybrid	gen7 midsize	2005-2007	189.5	71.5	57.1	2005/2006/2007 Honda Accord Hybrid Sedan		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7.5 midsize	2006-2007	189.5	71.5	57.1	2006/2007 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen7.5 midsize	2006-2007	188.9	71.5	55.7	2006/2007 Honda Accord Coupe		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 midsize	2008-2012	194.9	72.7	58.1	2008/2009/2010/2011/2012 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen8 midsize	2008-2012	190.9	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe		可入库
Honda Accord	Honda	越野车	Hatchback	Std.	gen8 crossover	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour		可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen9 crossover	2013	196.6	74.7	65.7	2013 Honda Crosstour		可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen9.5 crossover	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour		可入库
Honda Accord	Honda	三厢车	Sedan	Plug-In Hybrid	gen9 midsize	2014	191.4	72.8	57.7	2014 Honda Accord Plug-In Hybrid Sedan		可入库
Honda Accord	Honda	三厢车	Sedan	hybrid	gen9 midsize	2014-2015	191.4	72.8	57.7	2014/2015 Honda Accord Hybrid Sedan		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 midsize	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen9 midsize	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe		可入库
Honda Accord	Honda	三厢车	Coupe	Std.	gen9.5 midsize	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe		可入库
Honda Accord	Honda	三厢车	Sedan	hybrid	gen9.5 midsize	2017	194.1	72.8	57.7	2017 Honda Accord Hybrid Sedan		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen10 midsize	2018-2022	196.1	73.3	57.1	2018/2019/2020/2021/2022 Honda Accord Sedan		可入库
Honda Accord	Honda	三厢车	Sedan	hybrid	gen10 midsize	2018-2022	196.1	73.3	57.1	2018/2019/2020/2021/2022 Honda Accord Hybrid Sedan		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 midsize	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 subcompact	1980-1983	163.0	65.0	53.1	1980/1981/1982/1983 Honda Civic Sedan		待终核: 1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 subcompact	1980-1983	155.4	65.0	53.1	1980/1981/1983 Honda Civic Hatchback		待终核: 1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 subcompact	1984-1987	166.5	66.5	53.9	1984/1985/1986/1987 Honda Civic Sedan		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 subcompact	1984-1987	157.0	66.5	53.9	1984/1985/1986/1987 Honda Civic Hatchback		可入库
Honda Civic	Honda	跑车	Hatchback	Std.	gen3 sporty	1984-1987	150.0	65.0	50.4	1984/1985/1986/1987 Honda Civic CRX		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1991	172.8	67.3	52.6	1988/1989/1990/1991 Honda Civic Sedan		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1991	156.1	66.7	52.2	1988/1989/1990/1991 Honda Civic Hatchback		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992-1995	160.1	66.7	53.2	1992/1993/1994/1995 Honda Civic Hatchback		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992-1995	172.0	66.9	53.2	1992/1993/1994/1995 Honda Civic Sedan		可入库
Honda Civic	Honda	三厢车	Coupe	Std.	gen5 compact	1993-1995	173.0	66.9	52.8	1993/1994/1995 Honda Civic Coupe		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.5	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.5	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Sedan		可入库
Honda Civic	Honda	三厢车	Coupe	Std.	gen6 compact	1996-2000	175.5	67.1	53.9	1996/1997/1998/1999/2000 Honda Civic Coupe		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2005	174.6	67.5	56.7	2001/2002/2003/2004/2005 Honda Civic Sedan		可入库
Honda Civic	Honda	三厢车	Coupe	Std.	gen7 compact	2001-2005	174.6	67.5	55.0	2001/2002/2003/2004/2005 Honda Civic Coupe		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen7 compact	2002-2005	168.8	67.5	58.1	2002/2003/2004/2005 Honda Civic Si Hatchback		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 compact	2006-2011	177.3	69.0	56.5	2006/2007/2008/2009/2010/2011 Honda Civic Sedan		可入库
Honda Civic	Honda	三厢车	Coupe	Std.	gen8 compact	2006-2011	175.5	69.0	55.0	2006/2007/2008/2009/2010/2011 Honda Civic Coupe		可入库
Honda Civic	Honda	三厢车	Sedan	hybrid	gen8 compact	2006-2011	177.3	69.0	56.3	2006/2007/2008/2009/2010/2011 Honda Civic Hybrid Sedan		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 compact	2012-2015	179.4	69.0	56.5	2012/2013/2014/2015 Honda Civic Sedan		可入库
Honda Civic	Honda	三厢车	Coupe	Std.	gen9 compact	2012-2015	177.3	69.0	55.0	2012/2013/2014/2015 Honda Civic Coupe		可入库
Honda Civic	Honda	三厢车	Sedan	hybrid	gen9 compact	2012-2015	179.4	69.0	56.3	2012/2013/2014/2015 Honda Civic Hybrid Sedan		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2017/2018/2019/2020/2021 Honda Civic Hatchback		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 compact	2016-2021	182.7	70.8	55.7	2016/2017/2018/2019/2020/2021 Honda Civic Sedan		可入库
Honda Civic	Honda	三厢车	Coupe	Std.	gen10 compact	2016-2020	177.3	70.8	54.8	2016/2017/2018/2019/2020 Honda Civic Coupe		可入库
Honda Civic	Honda	三厢车	Sedan	Si	gen10 sporty	2017-2020	182.8	70.8	55.5	2017/2018/2019/2020 Honda Civic Si Sedan		可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 sporty	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 compact	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 compact	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback		可入库
Honda Civic	Honda	三厢车	Sedan	Si	gen11 sporty	2022-2026	184.0	70.9	55.5	2024/2025/2026 Honda Civic Si Sedan		待终核: 2022-2023
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 sporty	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R		可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 alternative	2017-2021	192.7	73.9	58.2	2017/2019/2020/2021 Honda Clarity		待终核: 2018
Honda Clarity	Honda	三厢车	Sedan	Plug-In Hybrid	gen1 alternative	2018-2021	192.7	73.9	58.2	2018/2019/2021 Honda Clarity Plug-In Hybrid		待终核: 2020
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V		可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen2 compact SUV	2002-2006	178.6	70.2	66.2	2002/2003/2004/2005/2006 Honda CR-V		可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen3 compact SUV	2007-2011	179.3	71.6	66.1	2007/2008/2009/2010/2011 Honda CR-V		可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen4 compact SUV	2012-2014	179.4	71.6	65.1	2012/2013/2014 Honda CR-V		可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen4.5 compact SUV	2015-2016	179.4	71.6	64.7	2015/2016 Honda CR-V		可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen5 compact SUV	2017-2022	182.1	73.0	66.5	2017/2018/2019/2020/2021/2022 Honda CR-V		可入库
Honda CR-V	Honda	越野车	SUV	inc: hybrid	gen6 compact SUV	2023-2026	184.8	73.5	66.5	2023/2024/2025 Honda CR-V / 2024 Honda CR-V Hybrid		待终核: 2026
Honda Odyssey	Honda	越野车	Minivan	Std.	gen1 minivan	1995-1998	187.0	69.7	64.6	1995/1996/1997/1998 Honda Odyssey		可入库
Honda Odyssey	Honda	越野车	Minivan	Std.	gen2 minivan	1999-2004	201.4	77.1	68.8	1999/2000/2001/2002/2003/2004 Honda Odyssey		可入库
Honda Odyssey	Honda	越野车	Minivan	Std.	gen3 minivan	2005-2010	202.1	77.1	70.0	2005/2006/2007/2008/2009/2010 Honda Odyssey		可入库
Honda Odyssey	Honda	越野车	Minivan	Std.	gen4 minivan	2011-2017	202.9	79.2	68.4	2011/2012/2013/2014/2015/2016/2017 Honda Odyssey		可入库
Honda Odyssey	Honda	越野车	Minivan	Std.	gen5 minivan	2018-2026	205.2	78.5	69.6	2018/2019/2020/2023/2024/2025 Honda Odyssey		待终核: 2021-2022/2026

下一步。


--- Round 4 / 下一步 ---
更新点

车型	操作	描述
Honda Accord 1991-1993 Coupe	拆出	1991 / 1992 / 1993 三维不一致，不能继续压成 1991-1993；本轮先拆成年份单行。1991 为 184.8×67.9×52.2，1992 为 185.2×67.1×54.1。
Edmunds
+1

Honda Accord 1990-1993 Wagon	拆出	1991 / 1992 / 1993 wagon 三维不一致；1990 wagon 本轮未确认美国销售口径，保留待终核。
Edmunds
+2
Edmunds
+2

Honda Civic gen11 Sedan	拆出	2022-2024 sedan 为 184.0×70.9×55.7，2025-2026 sedan 为 184.8×70.9×55.7，不能压成 2022-2026 一条。
Honda Civic gen11 Hatchback / Type R	值修改	Std. hatchback 2022-2026 三维一致，可入库；Type R 实际按 2023-2026 核，2022 暂不并入。
Honda Clarity / Crosstour / CR-V	稳定/拆出	Clarity PHEV 2018-2021 已补齐；Crosstour 2013 与 2014-2015 高度不同，拆出；CR-V 1997-2001 已补 1998/1999/2000，可入库。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽；Wagon车顶/尾厢需保留结构	待补强: 1994-1996
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1997	188.4	70.1	57.4	1994/1995/1996 Honda Accord Wagon, Edmunds	Wagon高尾厢	待终核: 1997；1994-1995与1996高度不一致，需最终拆分
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1997	185.6	70.1	54.7	1994/1995/1996 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1997；1994-1995与1996长度不一致，需最终拆分
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2002	189.4	70.3	57.3	1998/1999/2000/2002 Honda Accord Sedan, Edmunds		待终核: 2001；1998-2000与2002尺寸需拆分判断
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998-2002	188.8	70.3	56.9	1998/1999/2000/2001/2002 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1998-2002需按年份尺寸差异最终拆分
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2007	191.1	71.6	57.2	2003/2007 Honda Accord Sedan, Edmunds		待补强: 2004-2006
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.8	71.3	55.7	2003/2005/2007 Honda Accord Coupe, Edmunds	双门低车顶	待补强: 2004/2006
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2012	194.9	72.7	58.1	2008/2012 Honda Accord Sedan, Edmunds	八代sedan较长	待补强: 2009-2011
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	待补强: 2008-2010
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1991	168.8	66.7	53.5	1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1990
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1991	157.1	66.3	52.5	1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1990
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1991	161.7	66.1	56.9	1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1990
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1991	148.5	65.9	50.1	1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1990
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992-1995	173.0	66.9	51.7	1993/1995 Honda Civic Sedan, Edmunds		待补强: 1992/1994
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1992-1995	172.8	66.9	50.9	1995 Honda Civic Coupe, Edmunds	双门低车顶	待补强: 1992-1994
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992-1995	160.2	66.9	50.7	1995 Honda Civic Hatchback, Edmunds	短车身低车顶	待补强: 1992-1994
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	2000 Honda Civic Sedan, Edmunds		待补强: 1996-1999
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	2000 Honda Civic Coupe, Edmunds	双门较低	待补强: 1996-1999
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	2000 Honda Civic Hatchback CX, Edmunds	短车身hatch	待补强: 1996-1999
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2005	175.4	67.5	56.7	2005 Honda Civic Sedan, Edmunds		待补强: 2001-2004
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2005	175.4	66.7	55.1	2005 Honda Civic Coupe, Edmunds	双门更窄更低	待补强: 2001-2004
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006-2011	177.3	69.0	56.5	2006/2011 Honda Civic Sedan, Edmunds		待补强: 2007-2010
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006-2011	175.5	68.9	55.0	2011 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2006-2010
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012-2015	179.4	69.0	56.5	2012/2015 Honda Civic Sedan, Edmunds		待补强: 2013-2014
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012-2015	177.9	69.0	55.0	2012/2015 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2013-2014
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2021	182.7	70.9	55.7	2021 Honda Civic Sedan, Edmunds		待补强: 2016-2020
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	待补强: 2017-2020
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2021 Honda Civic Type R, Edmunds	宽体性能版	待补强: 2017-2020
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库；原始2022-2026中的2022需确认美国未售后删除
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 5 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen4	值修改	1990/1991 Civic sedan 均核到 168.8×66.7×53.5；1990/1991 hatchback 均核到 157.1×66.3×52.5；1990/1991 wagon 高车身取 4WD 高度 56.9；1990/1991 CRX 均为 148.5×65.9×50.1。1988-1989 仍未完整补齐，保留待补强。
Edmunds
+6
Edmunds
+6
Edmunds
+6

Honda Civic gen5	值修改	1992-1995 hatchback / sedan / coupe 已按 Edmunds 对应结构补强：sedan 1992/1993/1994/1995 为 173.0×66.9/67.0×51.7/54.1，hatchback 1992/1993/1994/1995 为 160.2×66.9/67.0×50.7/53.0，coupe 1993-1995 为 172.8×66.9×50.9；因 1992 sedan/hatch 高度与 1993-1995 不一致，本轮先拆分，不强压。
Edmunds
+9
Edmunds
+9
Edmunds
+9

Honda Civic gen2/gen3	稳定	早期 1980-1987 仍缺美国逐年/逐结构可靠完整来源，本轮不强行改为可入库，继续保留待补强。CarsGuide 仅提供澳洲市场尺寸范围，不能直接证明美国口径。
汽车指南
+2
汽车指南
+2

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽；Wagon车顶/尾厢需保留结构	待补强: 1994-1996
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1997	188.4	70.1	57.4	1994/1995/1996 Honda Accord Wagon, Edmunds	Wagon高尾厢	待终核: 1997；1994-1995与1996高度不一致，需最终拆分
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1997	185.6	70.1	54.7	1994/1995/1996 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1997；1994-1995与1996长度不一致，需最终拆分
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2002	189.4	70.3	57.3	1998/1999/2000/2002 Honda Accord Sedan, Edmunds		待终核: 2001；1998-2000与2002尺寸需拆分判断
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998-2002	188.8	70.3	56.9	1998/1999/2000/2001/2002 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1998-2002需按年份尺寸差异最终拆分
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2007	191.1	71.6	57.2	2003/2007 Honda Accord Sedan, Edmunds		待补强: 2004-2006
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.8	71.3	55.7	2003/2005/2007 Honda Accord Coupe, Edmunds	双门低车顶	待补强: 2004/2006
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2012	194.9	72.7	58.1	2008/2012 Honda Accord Sedan, Edmunds	八代sedan较长	待补强: 2009-2011
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	待补强: 2008-2010
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	2000 Honda Civic Sedan, Edmunds		待补强: 1996-1999
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	2000 Honda Civic Coupe, Edmunds	双门较低	待补强: 1996-1999
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	2000 Honda Civic Hatchback CX, Edmunds	短车身hatch	待补强: 1996-1999
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2005	175.4	67.5	56.7	2005 Honda Civic Sedan, Edmunds		待补强: 2001-2004
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2005	175.4	66.7	55.1	2005 Honda Civic Coupe, Edmunds	双门更窄更低	待补强: 2001-2004
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006-2011	177.3	69.0	56.5	2006/2011 Honda Civic Sedan, Edmunds		待补强: 2007-2010
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006-2011	175.5	68.9	55.0	2011 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2006-2010
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012-2015	179.4	69.0	56.5	2012/2015 Honda Civic Sedan, Edmunds		待补强: 2013-2014
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012-2015	177.9	69.0	55.0	2012/2015 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2013-2014
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2021	182.7	70.9	55.7	2021 Honda Civic Sedan, Edmunds		待补强: 2016-2020
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	待补强: 2017-2020
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2021 Honda Civic Type R, Edmunds	宽体性能版	待补强: 2017-2020
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库；原始2022-2026中的2022需确认美国未售后删除
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 6 / 下一步 ---
更新点

车型	操作	描述
Honda Accord gen5 Wagon	值修改	1996 wagon 已确认存在更高版本：188.4×70.1×57.4；同年也有 56.0 高度版本，因此继续按 max height 57.4 保留。
Edmunds
+2
Edmunds
+2

Honda Accord gen6 Sedan/Coupe	值修改	2001 sedan 核到 189.4×70.3×56.9；2001 coupe 核到 186.8×70.3×54.9。Coupe 原行 188.8×70.3×56.9 明显不应整段覆盖，继续待拆分。
Edmunds
+1

Honda Accord gen8 Coupe	稳定	2011/2012 coupe 均可用 191.0×72.8×56.4；但 2008-2010 尚未补齐，继续待补强。
Edmunds
+1

Honda Civic gen6	推进	1996/1997/1998 sedan 已核到 175.1×67.1×54.7；1999 仍缺，暂不整段可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Honda Civic gen7-gen9	推进	已补到关键点：2001 sedan 174.6×67.5×56.7；2001 coupe 174.7×66.7×55.1；2006/2011 coupe 均为 175.5×68.9×55.0；2012 sedan/coupe 已核，但中间年份仍待补。
Edmunds
+5
Edmunds
+5
Edmunds
+5

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1997	188.4	70.1	56.0	1996/1997 Honda Accord Sedan, Edmunds	Sedan/Wagon同长宽；Wagon车顶/尾厢需保留结构	待补强: 1994-1995；1996/1997高度口径需最终确认
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	待终核: 1994-1995最终来源复核
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	待终核: 1997高度需复核
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	54.7	1994/1995 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1994-1995最终来源复核
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1997最终复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2000	189.4	70.3	57.3	1998/1999/2000 Honda Accord Sedan, Edmunds		待终核: 1998-2000最终拆分复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001	189.4	70.3	56.9	2001 Honda Accord Sedan Value Package, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2002	189.4	70.3	57.3	2002 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998-2000	188.8	70.3	56.9	1998/1999/2000 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1998-2000需按年份尺寸差异最终拆分
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 2002高度复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2007	191.1	71.6	57.2	2003/2007 Honda Accord Sedan, Edmunds		待补强: 2004-2006
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.8	71.3	55.7	2003/2005/2007 Honda Accord Coupe, Edmunds	双门低车顶	待补强: 2004/2006
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2012	194.9	72.7	58.1	2008/2012 Honda Accord Sedan, Edmunds	八代sedan较长	待补强: 2009-2011
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2010	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	待补强: 2008-2010
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2011-2012	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-1998	175.1	67.1	54.7	1996/1997/1998 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1999-2000	175.1	67.1	54.7	2000 Honda Civic Sedan, Edmunds		待补强: 1999
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	2000 Honda Civic Coupe, Edmunds	双门较低	待补强: 1996-1999
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	2000 Honda Civic Hatchback CX, Edmunds	短车身hatch	待补强: 1996-1999
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001	174.6	67.5	56.7	2001 Honda Civic Sedan EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2002-2005	175.4	67.5	56.7	2005 Honda Civic Sedan, Edmunds		待补强: 2002-2004
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001	174.7	66.7	55.1	2001 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2002-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	待补强: 2002-2003
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2011	177.3	69.0	56.5	2011 Honda Civic Sedan, Edmunds		待补强: 2007-2010
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006-2011	175.5	68.9	55.0	2006/2011 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2007-2010
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2015 Honda Civic Sedan, Edmunds		待补强: 2013-2014
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013-2015	177.9	69.0	55.0	2015 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2013-2014
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		待补强: 2016-2019
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	待补强: 2017-2020
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2021 Honda Civic Type R, Edmunds	宽体性能版	待补强: 2017-2020
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库；原始2022-2026中的2022需确认美国未售后删除
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 7 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen6 Sedan/Coupe/Hatchback	值修改	1999 sedan 已核到 175.1×67.1×54.7；1999 coupe 已核到 175.1×67.1×54.1；1999 hatchback 已核到 164.2×67.1×54.1，所以 gen6 三个结构可推进为 1996-2000 可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Honda Civic gen7 Sedan/Coupe	拆出	2002 sedan 为 174.6×67.5×56.7，2004 sedan 为 175.4×67.5×56.7；2003 coupe 为 174.7×66.7×55.1，2004 coupe 为 175.4×66.7×55.1，因此 2001-2005 不宜整段一条，按 2001-2003 / 2004-2005 拆分。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Honda Civic 早期段	稳定	1973-1987 与 1988-1989 部分结构仍缺美国逐年/逐结构完整来源，本轮不强行标可入库。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1997	188.4	70.1	56.0	1996/1997 Honda Accord Sedan, Edmunds	Sedan/Wagon同长宽；Wagon车顶/尾厢需保留结构	待补强: 1994-1995；1996/1997高度口径需最终确认
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	待终核: 1994-1995最终来源复核
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	待终核: 1997高度需复核
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	54.7	1994/1995 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1994-1995最终来源复核
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1997最终复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2000	189.4	70.3	57.3	1998/1999/2000 Honda Accord Sedan, Edmunds		待终核: 1998-2000最终拆分复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001	189.4	70.3	56.9	2001 Honda Accord Sedan Value Package, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2002	189.4	70.3	57.3	2002 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998-2000	188.8	70.3	56.9	1998/1999/2000 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1998-2000需按年份尺寸差异最终拆分
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 2002高度复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2007	191.1	71.6	57.2	2003/2007 Honda Accord Sedan, Edmunds		待补强: 2004-2006
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.8	71.3	55.7	2003/2005/2007 Honda Accord Coupe, Edmunds	双门低车顶	待补强: 2004/2006
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2012	194.9	72.7	58.1	2008/2012 Honda Accord Sedan, Edmunds	八代sedan较长	待补强: 2009-2011
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2010	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	待补强: 2008-2010
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2011-2012	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		待终核: 2003尺寸需补最终行来源
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	待终核: 2002尺寸需补最终行来源
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2011	177.3	69.0	56.5	2011 Honda Civic Sedan, Edmunds		待补强: 2007-2010
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006-2011	175.5	68.9	55.0	2006/2011 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2007-2010
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2015 Honda Civic Sedan, Edmunds		待补强: 2013-2014
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013-2015	177.9	69.0	55.0	2015 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2013-2014
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		待补强: 2016-2019
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	待补强: 2017-2020
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2021 Honda Civic Type R, Edmunds	宽体性能版	待补强: 2017-2020
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库；原始2022-2026中的2022需确认美国未售后删除
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 8 / 下一步 ---
更新点

车型	操作	描述
Honda Accord gen5	拆出/值修改	Accord 1994-1995 与 1996-1997 的 wagon/sedan 尺寸不完全一致，继续按尺寸段拆开；1997 wagon 已确认 188.4×70.1×56.0，1996 wagon 高度最大仍为 57.4。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Honda Accord gen6 Coupe	拆出	1998 coupe 为 186.8×70.3×55.1，1999 为 188.8×70.3×56.9，2000 为 186.6×70.3×55.3，2001 为 186.8×70.3×54.9，2002 为 186.8×70.3×55.3，不能整段压缩。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Honda Accord gen7	拆出/值修改	2003-2005 sedan 为 189.5×71.5×57.1；2006-2007 sedan 为 191.1×71.6×57.2/57.3，按 2003-2005 与 2006-2007 拆分。Coupe 2003-2007 核到 187.6×71.3×55.7，可压缩。
Edmunds
+6
Edmunds
+6
Edmunds
+6

Honda Civic gen7/gen8/gen9	推进	Civic gen7 sedan/coupe 已按 2001-2003 与 2004-2005 拆；gen8/gen9 仍保留少量中间年份待终核，下一轮继续补齐。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	54.7	1994/1995 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1994-1995最终来源复核
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1997最终复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2000	189.4	70.3	57.3	1998/1999/2000 Honda Accord Sedan, Edmunds		待终核: 1998-2000最终拆分复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001	189.4	70.3	56.9	2001 Honda Accord Sedan Value Package, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2002	189.4	70.3	57.3	2002 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2012	194.9	72.7	58.1	2008/2012 Honda Accord Sedan, Edmunds	八代sedan较长	待补强: 2009-2011
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2010	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	待补强: 2008-2010
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2011-2012	191.0	72.8	56.4	2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		待终核: 2003尺寸需补最终行来源
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	待终核: 2002尺寸需补最终行来源
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2011	177.3	69.0	56.5	2011 Honda Civic Sedan, Edmunds		待补强: 2007-2010
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006-2011	175.5	68.9	55.0	2006/2011 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2007-2010
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2015 Honda Civic Sedan, Edmunds		待补强: 2013-2014
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013-2015	177.9	69.0	55.0	2015 Honda Civic Coupe, Edmunds	双门更短更低	待补强: 2013-2014
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		待补强: 2016-2019
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	待补强: 2017-2020
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2021 Honda Civic Type R, Edmunds	宽体性能版	待补强: 2017-2020
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库；原始2022-2026中的2022需确认美国未售后删除
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 9 / 下一步 ---
更新点

车型	操作	描述
Honda Accord gen8 Sedan	拆出	2008-2011 sedan 为 194.1×72.7×58.1，2012 sedan 为 194.9×72.7×58.1，不能继续压成 2008-2012 一条。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Honda Accord gen8 Coupe	值修改	2008/2009/2010 coupe 均为 190.9×72.8×56.4，和 2011-2012 可合并为 2008-2012。
Edmunds
+2
Edmunds
+2

Honda Civic gen8 Sedan/Coupe	拆出	2007-2008 sedan 为 176.7×69.0×56.5，2009-2011 sedan 为 177.3×69.0×56.5；2007-2008 coupe 为 174.8×68.9×53.5，2009-2011 coupe 为 175.5×68.9×55.0。
Edmunds
+6
Edmunds
+6
Edmunds
+6

Honda Civic gen9 / gen10	推进	2013 sedan 为 179.4×69.0×56.5；2014 coupe 为 177.9×69.0×55.0；2016/2018/2019 Civic sedan 核到 182.3×70.8×55.7；gen10 sedan 与原行 182.7×70.9 存在口径差异，先保留待终核。
Edmunds
+4
Edmunds
+4
Edmunds
+4

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	54.7	1994/1995 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1994-1995最终来源复核
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1997最终复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2000	189.4	70.3	57.3	1998/1999/2000 Honda Accord Sedan, Edmunds		待终核: 1998-2000最终拆分复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001	189.4	70.3	56.9	2001 Honda Accord Sedan Value Package, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2002	189.4	70.3	57.3	2002 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		待终核: 2003尺寸需补最终行来源
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	待终核: 2002尺寸需补最终行来源
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	待终核: 2006最终行来源复核
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		待终核: 2014需确认非coupe页面口径
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		待终核: 2017/2020/2021及原70.9口径
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		待终核: 与2016-2019宽度/长度口径需最终确认
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2021	177.9	70.8	56.3	2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	待补强: 2017-2020
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2021 Honda Civic Type R, Edmunds	宽体性能版	待补强: 2017-2020
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库；原始2022-2026中的2022需确认美国未售后删除
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 10 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen10 Hatchback	拆出/值修改	2017-2019 hatchback 最高高度按 56.5；2020-2021 为 56.3，不能继续压成 2017-2021 一条。Edmunds 显示 2017/2018/2019 hatchback 为 177.9×70.8×56.5，2020 为 177.9×70.8×56.3。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Honda Civic gen10 Type R	稳定	2017-2021 Type R 均核到 179.4×73.9×56.5，可入库。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Honda Civic gen10 Sedan	拆出/值修改	2016-2019 sedan 按 182.3×70.8×55.7；2020-2021 sedan 按 182.7×70.9×55.7，可按原先拆分保留。Edmunds 显示 2019 sedan 为 182.3×70.8×55.7，2020 sedan 为 182.7×70.9×55.7。
Edmunds
+2
Edmunds
+2

Honda Civic gen11 Type R	值修改	原始 2022-2026 不应含 2022 Type R；美国 11代 Type R 从 2023 开始，当前行保留 2023-2026 可入库。
剩余待补强	稳定	当前仍剩：Accord 1990 wagon、Accord gen5 coupe、Accord gen6 sedan 1998-2000、Civic 1973-1989 早期段、Civic gen7 部分行、Civic gen8 coupe 2006、Civic gen9 sedan 2014。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	54.7	1994/1995 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1994-1995最终来源复核
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1997最终复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998-2000	189.4	70.3	57.3	1998/1999/2000 Honda Accord Sedan, Edmunds		待终核: 1998-2000最终拆分复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001	189.4	70.3	56.9	2001 Honda Accord Sedan Value Package, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2002	189.4	70.3	57.3	2002 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		待终核: 2003尺寸需补最终行来源
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	待终核: 2002尺寸需补最终行来源
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	待终核: 2006最终行来源复核
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		待终核: 2014需确认非coupe页面口径
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 11 / 下一步 ---
更新点

车型	操作	描述
Honda Accord gen5 Coupe	推进	1997 Accord Coupe 已核到 185.6×70.1×54.7，可与 1996 合并为 1996-1997 可入库；1994-1995 仍保留待终核。
Edmunds

Honda Accord gen6 Sedan	值修改/拆出	1998 Accord Sedan 实际为 188.8×70.3×57.3；2001 V6 页面为 189.4×70.3×57.3，与此前 2001 Value Package 高度 56.9 存在 trim 最大值口径差异，本轮改按最大高度 57.3。2000 搜索结果返回的是 coupe/LX V6 页面，不能用于 sedan 行最终完成。
Edmunds
+1

Honda Accord 1990 Wagon	稳定	Edmunds 能确认 1991/1992 wagon，但本轮仍未找到 1990 wagon 页面；继续保留待终核，不强行可入库。
Edmunds
+1

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	54.7	1994/1995 Honda Accord Coupe, Edmunds	双门低车顶	待终核: 1994-1995最终来源复核
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999-2000	189.4	70.3	57.3	1999/2000 Honda Accord Sedan, Edmunds		待终核: 1999-2000 sedan最终来源复核
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		待终核: 2003尺寸需补最终行来源
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	待终核: 2002尺寸需补最终行来源
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	待终核: 2006最终行来源复核
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		待终核: 2014需确认非coupe页面口径
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 12 / 下一步 ---
更新点

车型	操作	描述
Honda Accord gen5 Coupe	值修改	1994/1995 Accord coupe 已补强，按可见最大高度口径调整为 184.0×70.1×55.1，推进为可入库。
Edmunds
+2
Edmunds
+2

Honda Accord gen6 Sedan	拆出	1999 sedan 为 188.8×70.3×56.9，2000 sedan 为 188.8×70.3×57.3，不能合并为同尺寸段；已拆出并推进可入库。
Edmunds
+2
Edmunds
+2

Honda Civic gen7/gen8/gen9	推进	2003 Civic sedan、2002 Civic coupe、2014 Civic sedan 已补到 Edmunds 尺寸；2006 coupe 仍沿用已核 Edmunds 口径，推进为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

剩余待补强	稳定	当前仍剩 Accord 1990 wagon 与 Civic 1973-1989 早期段，缺美国逐年/逐结构完整来源，继续保留待补强。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990	186.8	67.9	55.1	1991/1992/1993 Honda Accord Wagon, Edmunds	wagon更长更宽	待终核: 1990是否美国销售/是否应删除或拆出无数据
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期hatch	待补强: 1973-1979
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	早期sedan	待补强: 1973-1979
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 13 / 下一步 ---
更新点

车型	操作	描述
Honda Accord 1990 Wagon	值修改	Honda 官方 1990 Accord 规格只列 2-Door / 4-Door，未列 wagon；Edmunds 能确认 1991/1992/1993 wagon，但未找到 1990 wagon。因此 1990 wagon 不再沿用 1991-1993 尺寸，改为缺数据/待确认。
Edmunds
+3
Honda新闻
+3
Edmunds
+3

Honda Civic gen1	值修改	gen1 hatchback/sedan 不应沿用 wagon 最大长度。公开资料显示 North America hatch/sedan 长约 147.8 in，wagon 长 160.0 in；因此本轮将 gen1 hatchback/sedan 与 wagon 分开，早期段仍待逐年终核。
维基百科
+1

Honda Civic gen2	值修改	1983 Civic 尺寸范围可支撑 gen2 的结构差异：hatchback 约 148.0 in、wagon 约 157.3 in、sedan 更长；但 1980-1982 美国逐年/逐结构仍未完整核完，保留待补强。
汽车指南

Honda Civic gen4 Wagon / CRX	值修改	1990 Civic wagon Edmunds 显示 FWD wagon 高 56.1；原表 56.9 更像 4WD 高点，需要保留 4WD/max 口径待最终核；CRX 1990/1991 Edmunds 可支撑 148.5×65.9×50.1。
Edmunds
+2
Edmunds
+2

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973-1979	147.8	59.3	53.0	1973-1979 Honda Civic Hatchback North America / 1973 Automobile-Catalog	早期hatch	待终核: 1974-1979逐年/美国结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979	147.8	59.3	52.4	Honda Civic 1st gen North America sedan reference	早期sedan	待补强: 1973-1979逐年/美国结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1979	160.0	59.3	53.5	Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1979逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	52.6	1983 Honda Civic S Hatchback, Automobile-Catalog	早期短hatch	待补强: 1980-1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1984-1986
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 14 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen1 Hatchback	拆出	1973 hatchback 可核到 139.8×59.3×53.0；1974 后因北美 5 mph 保险杠规则加长，不能继续和 1973 压成一条。
汽车目录
+1

Honda Civic gen1 Sedan	值修改	第一代四门 sedan 在美国市场不可作为已确认销售结构，继续保留待确认/缺美国结构来源，不标可入库。
维基百科

Honda Civic gen1 Wagon	值修改	1979 wagon 可核到约 157.3×62.2×54.1，原 160.0×59.3×53.5 不再作为 gen1 wagon 统一值；但 1973-1978 wagon/美国口径仍未完整核完。
汽车指南

Honda Civic gen2	稳定	gen2 结构尺寸可支撑 hatchback/sedan/wagon 差异，但 1980-1982 仍缺逐年/逐结构完整美国口径，所以继续待补强。
汽车目录
+2
维基百科
+2

Honda Civic gen3 Wagon	值修改	Honda 官方 1984 Civic Wagon 规格为 157.1×63.9×58.3，高度高于原行；但 1985-1986/1987 仍需终核。
Honda新闻

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	146.9	59.3	53.0	Honda Civic first generation North America hatchback; 1974 bumper length update	早期hatch	待终核: 1975-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.0	1981/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	待补强: 1980/1982
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.3	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1985-1986；1987高度口径需复核
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	待补强: 1988-1989
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	待补强: 1988-1989
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待补强: 1988-1989
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	待补强: 1988-1989
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 15 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Hatchback	拆出	1981/1982/1983 hatchback 已可用 148.0×62.2×53.0 口径；1980 仍未单独核完，继续保留待补强。
汽车目录
+1

Honda Civic gen3 Wagon	拆出/值修改	1984 wagon 使用 Honda 官方规格 157.1×63.9×58.3；1985 4WD wagon 参考 Automobile-Catalog 为 159.1×64.8×59.4；1986-1987 仍缺最终统一口径，继续待补强。
Honda新闻
+1

Honda Civic gen4 1988-1989	稳定	第四代 Civic 可证明结构差异，但 1988/1989 的美国逐年 Edmunds 页面仍未找到，因此暂不直接改为可入库。
维基百科

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	146.9	59.3	53.0	Honda Civic first generation North America hatchback; 1974 bumper length update	早期hatch	待终核: 1975-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980	148.0	62.2	53.0	1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	待补强: 1980
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1981-1983	148.0	62.2	53.0	1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.3	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985	159.1	64.8	59.4	1985 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1986-1987	166.5	65.7	54.3	1987 Honda Civic RT-i 4WD Wagon, Carfolio	wagon高车身	待补强: 1986；1987高度口径需复核
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds; 4th-gen reference	四代sedan	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds; 4th-gen reference	短车身hatch	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds; 4th-gen reference	高车身wagon	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds; CRX gen2 reference	CRX短车身低车顶	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 16 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen3 Wagon	拆出	1987 4WD wagon 已核到 159.1×64.8×59.4；1986 仍未单独核到，不能和 1987 合并为可入库。
汽车目录

Honda Civic gen4 Hatchback	推进	1988/1989 hatchback 有 North America 规格页，且尺寸与 1990-1991 hatchback 口径一致或高度差在同结构范围内，本轮推进为可入库；Edmunds 1990 hatchback 为 157.1×66.3×52.5。
汽车目录
+2
汽车目录
+2

Honda Civic gen4 Sedan/Wagon/CRX	稳定	gen4 结构差异可确认，但 1988-1989 sedan/wagon/CRX 仍缺足够逐年美国页面，本轮不强行改可入库；继续保留具体待补强。
维基百科

Honda Civic gen2	稳定	1981-1983 hatchback 已可入库；1980 hatchback、gen2 sedan/wagon 1980-1982 仍缺完整逐年结构口径。
汽车目录
+1

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	146.9	59.3	53.0	Honda Civic first generation North America hatchback; 1974 bumper length update	早期hatch	待终核: 1975-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980	148.0	62.2	53.0	1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	待补强: 1980
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1981-1983	148.0	62.2	53.0	1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980-1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.3	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1984-1987
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985	159.1	64.8	59.4	1985 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1986	159.1	64.8	59.4	1985/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	待终核: 1986逐年页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1987	159.1	64.8	59.4	1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds; 4th-gen reference	四代sedan	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds; 4th-gen reference	高车身wagon	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds; CRX gen2 reference	CRX短车身低车顶	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 17 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Hatchback	值修改	1980 hatchback 已找到 North America 目录页；1980-1983 hatchback 可以合并推进为可入库。Automobile-Catalog 1981 hatchback 为 148.0×62.2×53.0，1982 为 148.0×62.2×53.1；CarsGuide 1980-1983 尺寸范围也支撑 hatchback 148.0×62.2 左右口径。
汽车指南
+5
汽车目录
+5
汽车目录
+5

Honda Civic gen2 Sedan	推进	1981 Car and Driver 明确为第一款四门 Civic sedan，说明 sedan 相比 hatchback 增加约 13.0 in 车长、1.2 in 车高；现有 1983 sedan 口径可作为 1981-1983 段参考，但 1980 sedan 仍不应合并。
Car and Driver
+1

Honda Civic gen3 Sedan	推进	1984 sedan 已找到 Automobile-Catalog 规格：163.4×64.0×54.5；1985-1987 仍缺逐年结构来源，继续待补强。
汽车目录

Honda Civic gen3 Wagon	稳定	1984/1985/1987 wagon 已有明确来源，1986 仍缺逐年页面，因此只保留 1986 待终核。
Honda Civic gen4 CRX	推进	CRX 1988-1989 属二代 CR-X，维基说明 1988 model year 完全换代、车长增加 3.2 in、宽度接近增加 2 in，可与 1990-1991 同代参考并入，但仍缺 1988/1989 美国逐年尺寸页，本轮保留待补强。
维基百科

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	146.9	59.3	53.0	Honda Civic first generation North America hatchback; 1974 bumper length update	早期hatch	待终核: 1975-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981-1983	161.4	61.6	53.2	1981 Car and Driver Civic Sedan / 1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待终核: 1982/1983逐年尺寸确认
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980				1980 Honda Civic 2nd-gen North America hatch/wagon listed; sedan not confirmed	1980 sedan未确认	缺数据: 1980 sedan
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.3	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984	163.4	64.0	54.5	1984 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1985-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1985-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985	159.1	64.8	59.4	1985 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1986	159.1	64.8	59.4	1985/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	待终核: 1986逐年页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1987	159.1	64.8	59.4	1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds; 4th-gen reference	四代sedan	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds; 4th-gen reference	高车身wagon	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds; CRX gen2 reference	CRX短车身低车顶	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 18 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Hatchback	稳定	已维持 1980-1983 可入库；Automobile-Catalog 可支撑 1981 hatchback 148.0×62.2×53.0，CarsGuide 1983 也显示长度/宽度/高度范围与该口径接近。
汽车目录
+1

Honda Civic gen2 Sedan	稳定	1981 为第一款四门 Civic sedan，且比 hatchback 增加 13.0 in 车长、1.2 in 车高；但 1982/1983 仍缺完整逐年结构尺寸页，所以继续待终核，不改可入库。
Car and Driver

Honda Civic gen3 Hatch/Sedan	稳定	1984 公开尺寸范围显示 gen3 不同结构长度/宽度/高度差异明显；目前 hatch 1984-1987 与 sedan 1985-1987 仍缺逐年结构来源，继续待补强。
汽车指南

Honda Civic gen4 1988-1989	稳定	1988-1989 hatchback 已可入库；sedan/wagon/CRX 仍缺足够美国逐年页面，继续保留待补强。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	146.9	59.3	53.0	Honda Civic first generation North America hatchback; 1974 bumper length update	早期hatch	待终核: 1975-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981-1983	161.4	61.6	53.2	1981 Car and Driver Civic Sedan / 1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待终核: 1982/1983逐年尺寸确认
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980				1980 Honda Civic 2nd-gen North America hatch/wagon listed; sedan not confirmed	1980 sedan未确认	缺数据: 1980 sedan
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.3	1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1980-1982
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984	163.4	64.0	54.5	1984 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1985-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1985-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985	159.1	64.8	59.4	1985 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1986	159.1	64.8	59.4	1985/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	待终核: 1986逐年页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1987	159.1	64.8	59.4	1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds; 4th-gen reference	四代sedan	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds; 4th-gen reference	高车身wagon	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds; CRX gen2 reference	CRX短车身低车顶	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 19 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen4 CRX	拆出	1988 CRX Si 已核到 147.8×65.9×50.0；1990-1991 仍维持 148.5×65.9×50.1，因此 1988 不再和 1990-1991 混用同一尺寸。
汽车目录

Honda Civic gen4 Wagon	值修改	1988 Civic Wagon 资料显示整体长度 4105 mm、宽 1690 mm、高 1515 mm，约 161.6×66.5×59.6；与 1990/1991 Edmunds 口径差异较大，1988-1989 wagon 继续待终核，不直接可入库。
autocatalogarchive.com

Honda Civic gen2 Hatchback	稳定	1981 hatchback 为 148.0×62.2×53.0，1982 hatchback 为 148.0×62.2×53.1，继续维持 1980-1983 hatchback 可入库。
汽车目录
+1

Honda Civic gen4 结构参考	稳定	第四代 Civic 公开尺寸显示 hatchback / sedan / wagon 长度和高度不同；未完成美国逐年页面的 sedan/wagon/CRX 1988-1989 继续保留待补强。
维基百科

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	146.9	59.3	53.0	Honda Civic first generation North America hatchback; 1974 bumper length update	早期hatch	待终核: 1975-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981-1983	161.4	61.6	53.2	1981 Car and Driver Civic Sedan / 1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待终核: 1982/1983逐年尺寸确认
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980				1980 Honda Civic 2nd-gen North America hatch/wagon listed; sedan not confirmed	1980 sedan未确认	缺数据: 1980 sedan
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.3	1980/1981 Honda Civic dimension range / 1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1982 wagon逐年确认
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984	163.4	64.0	54.5	1984 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1985-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1985-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985	159.1	64.8	59.4	1985 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1986	159.1	64.8	59.4	1985/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	待终核: 1986逐年页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1987	159.1	64.8	59.4	1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds; 4th-gen reference	四代sedan	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.5	59.6	1988 Civic Wagon brochure; 1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待终核: 1989美国逐年页面及1990-1991口径差异
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds; CRX gen2 reference	CRX短车身低车顶	待补强: 1989美国逐年页面
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 20 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Sedan	拆出	1983 Civic sedan 已核到 161.4×61.6×53.2，可单独推进为可入库；1981-1982 仍只具备 sedan 存在性/结构说明，继续待终核。
汽车目录
+1

Honda Civic gen3 Wagon	值修改	1986 Civic 4WD Wagon 已核到 Automobile-Catalog 页面，尺寸口径与 1985/1987 4WD wagon 可统一为 159.1×64.8×59.4，1985-1987 可合并可入库。
汽车目录
+1

Honda Civic gen2 Hatchback	稳定	1980-1983 hatchback 维持可入库；1981/1982 明确为 148.0×62.2×53.0/53.1，CarsGuide 1980-1983 范围也支撑该段。
汽车指南
+3
汽车目录
+3
汽车目录
+3

Honda Civic gen3 Hatch/Sedan	稳定	1984-1987 hatchback 与 1985-1987 sedan 仍缺逐年/美国结构来源，继续待补强；不强行标可入库。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	146.9	59.3	53.0	Honda Civic first generation North America hatchback; 1974 bumper length update	早期hatch	待终核: 1975-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981-1982	161.4	61.6	53.2	1981 Car and Driver Civic Sedan / 1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待终核: 1981-1982逐年尺寸确认
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980				1980 Honda Civic 2nd-gen North America hatch/wagon listed; sedan not confirmed	1980 sedan未确认	缺数据: 1980 sedan
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.3	1980/1981 Honda Civic dimension range / 1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1982 wagon逐年确认
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984	163.4	64.0	54.5	1984 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1985-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1985-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds; 4th-gen reference	四代sedan	待补强: 1988-1989美国逐年页面
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.5	59.6	1988 Civic Wagon brochure; 1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	待终核: 1989美国逐年页面及1990-1991口径差异
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1989	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds; CRX gen2 reference	CRX短车身低车顶	待补强: 1989美国逐年页面
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 21 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen4 Sedan	推进	1989 Civic 4-door sedan 已核到 Automobile-Catalog 页面，长度 166.5 in；结合四代 Civic 公开结构尺寸，1988-1989 sedan 不再用 168.8，改为 166.5×65.9×53.5，并推进为可入库。
汽车目录
+1

Honda Civic gen4 Wagon	拆出/值修改	1988 Civic Wagon 资料显示 161.6×66.1×59.6；1990/1991 Edmunds wagon FWD 为 161.7×66.1×56.1，四代公开资料显示 4WD wagon 高点 56.9，因此 1988-1989 wagon 继续不能和 1990-1991 合并。
自动汽车目录档案
+2
Edmunds
+2

Honda Civic gen4 CRX	推进	1989 CRX 公开尺寸为 3750 mm×1675 mm×1265 mm，约 147.6×65.9×49.8；与 1988 CRX Si 147.8×65.9×50.0 接近，合并为 1988-1989 可入库。
汽车指南
+1

剩余缺口	稳定	剩余仍为 Accord 1990 wagon、Civic gen1 1974-1979 hatch / gen1 sedan / gen1 1973-1978 wagon、gen2 sedan 1981-1982、gen2 wagon 1980-1982、gen3 hatch 1984-1987、gen3 sedan 1985-1987。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	146.9	59.3	53.0	Honda Civic first generation North America hatchback; 1974 bumper length update	早期hatch	待终核: 1975-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981-1982	161.4	61.6	53.2	1981 Car and Driver Civic Sedan / 1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待终核: 1981-1982逐年尺寸确认
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980				1980 Honda Civic 2nd-gen North America hatch/wagon listed; sedan not confirmed	1980 sedan未确认	缺数据: 1980 sedan
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.3	1980/1981 Honda Civic dimension range / 1983 Honda Civic Wagon, Automobile-Catalog / CarsGuide	wagon高车身	待补强: 1982 wagon逐年确认
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984	163.4	64.0	54.5	1984 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1985-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1985-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	166.5	65.9	53.5	1989 Honda Civic LX 4-Door Sedan, Automobile-Catalog; Honda Civic 4th-gen North America reference	四代sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.1	59.6	1988/1989 Honda Civic Wagon, Automobile-Catalog / 1988 Civic Wagon brochure	高车身wagon	待终核: 1989美国逐年页面及AU/NA高度口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog / 1989 Honda CRX, CarsGuide	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 22 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen1 Hatchback	值修改	第一代 Civic 公开资料给出 North America 长度 147.8 in、宽 59.3 in；因此 1974-1979 hatchback 从 146.9 调整为 147.8，仍保留待终核，因为 1975-1979 逐年/结构未完全核完。
维基百科
+1

Honda Civic gen2 Sedan	值修改	找到 1980 Civic 4-Door Sedan EX 规格，尺寸约 161.0×62.2×53.1；但与“1981 为第一款四门 Civic sedan”的资料存在口径冲突，所以 1980 sedan 不再空白，改为待终核。
汽车目录

Honda Civic gen2 Wagon	值修改	二代 Civic 公开资料给出 wagon 长 4085 mm、宽 1580 mm、高 1380 mm，约 160.8×62.2×54.3；原 157.3 长度偏低，改为 160.8，仍待逐年确认。
维基百科

Honda Civic gen3 / gen4	稳定	gen3 hatch/sedan 与 gen4 wagon 仍缺足够美国逐年页面，继续保留待补强；不强行标可入库。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	147.8	59.3	53.0	Honda Civic first generation North America hatchback; 1975 3-Door Automobile-Catalog	早期hatch	待终核: 1976-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980	161.0	62.2	53.1	1980 Honda Civic 4-Door Sedan EX, Automobile-Catalog	1980 sedan存在性与其他资料口径冲突	待终核: 1980 sedan销售/结构口径
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981-1982	161.4	61.6	53.2	1981 Car and Driver Civic Sedan / 1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待终核: 1981-1982逐年尺寸确认
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1983	161.4	61.6	53.2	1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	160.8	62.2	54.3	Honda Civic second generation wagon dimensions / 1983 Honda Civic Wagon, Automobile-Catalog	wagon高车身	待补强: 1980-1982逐年确认
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984	163.4	64.0	54.5	1984 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1985-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1985-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	166.5	65.9	53.5	1989 Honda Civic LX 4-Door Sedan, Automobile-Catalog; Honda Civic 4th-gen North America reference	四代sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.1	59.6	1988/1989 Honda Civic Wagon, Automobile-Catalog / 1988 Civic Wagon brochure	高车身wagon	待终核: 1989美国逐年页面及AU/NA高度口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog / 1989 Honda CRX, CarsGuide	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 23 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Sedan	推进	1980 Civic 4-Door Sedan EX 可见尺寸为 161.0×62.2×53.1；1982 Civic Sedan 页面已找到，1983 Civic Sedan 也已有尺寸口径。本轮把 gen2 sedan 拆成 1980 与 1981-1983 两段，1981-1983 仍保留待终核，因为 1981 主要来自 Car and Driver 的“比 hatchback 加长 13.0 in / 加高 1.2 in”说明，非完整三维表。
汽车目录
+2
汽车目录
+2

Honda Civic gen2 Wagon	值修改	CarsGuide 1980/1981/1982 均显示二代 Civic 尺寸范围可覆盖 wagon 高度/长度段；但逐年 wagon 页面还不完整，所以 1980-1983 wagon 继续待补强。
汽车指南
+2
汽车指南
+2

Honda Civic gen3 Hatch/Sedan	稳定	1984 Civic 尺寸范围可证明三代不同结构尺寸差异，但 hatch 1984-1987 与 sedan 1985-1987 仍缺足够逐年结构来源，不改可入库。
汽车指南

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	147.8	59.3	53.0	Honda Civic first generation North America hatchback; 1975 3-Door Automobile-Catalog	早期hatch	待终核: 1976-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980	161.0	62.2	53.1	1980 Honda Civic 4-Door Sedan EX, Automobile-Catalog	1980 sedan存在性与其他资料口径冲突	待终核: 1980 sedan销售/结构口径
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981-1983	161.4	61.6	53.2	1981 Car and Driver Civic Sedan / 1982/1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	待终核: 1981完整三维口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	160.8	62.2	54.3	Honda Civic second generation wagon dimensions / 1980-1982 CarsGuide range / 1983 Honda Civic Wagon, Automobile-Catalog	wagon高车身	待补强: 1980-1982逐年确认
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984	163.4	64.0	54.5	1984 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1985-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1985-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	166.5	65.9	53.5	1989 Honda Civic LX 4-Door Sedan, Automobile-Catalog; Honda Civic 4th-gen North America reference	四代sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.1	59.6	1988/1989 Honda Civic Wagon, Automobile-Catalog / 1988 Civic Wagon brochure	高车身wagon	待终核: 1989美国逐年页面及AU/NA高度口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog / 1989 Honda CRX, CarsGuide	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 24 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Sedan	拆出/推进	1980 sedan 已有 Automobile-Catalog 完整三维 161.0×62.2×53.1，可从“待终核”推进为可入库；1981 sedan 主要依据 C&D 说明“比 hatchback 加长 13.0 in、加高 1.2 in”，但不是完整三维表，所以继续单独待终核；1983 sedan 维持可入库。
汽车目录
+2
Car and Driver
+2

Honda Civic gen2 Wagon	稳定	1983 wagon 有完整三维 157.3×62.2×54.1；此前按二代 wagon 160.8 的代际值仍需逐年确认，本轮不强行标整段可入库。
汽车目录

Honda Civic gen3 Sedan	推进	1985 sedan 已核到 163.4×64.0×54.5，可与 1984 合并为 1984-1985 可入库；1986-1987 仍缺逐年结构来源，继续待补强。
汽车目录

Honda Civic gen3 Hatch / gen4 Wagon	稳定	gen3 hatch 1984-1987 与 gen4 wagon 1988-1989 仍缺足够美国逐年/结构来源，不改可入库。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	147.8	59.3	53.0	Honda Civic first generation North America hatchback; 1975 3-Door Automobile-Catalog	早期hatch	待终核: 1976-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980	161.0	62.2	53.1	1980 Honda Civic 4-Door Sedan EX, Automobile-Catalog	1980 sedan存在性与其他资料口径冲突	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981	161.0	62.2	54.2	1981 Car and Driver Civic Sedan dimensional delta from 1981 hatchback	sedan长车身	待终核: 1981完整三维表
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1982-1983	161.4	61.6	53.2	1982/1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	160.8	62.2	54.3	Honda Civic second generation wagon dimensions / 1980-1982 CarsGuide range / 1983 Honda Civic Wagon, Automobile-Catalog	wagon高车身	待补强: 1980-1982逐年确认
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1985	163.4	64.0	54.5	1984/1985 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1986-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1986-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	166.5	65.9	53.5	1989 Honda Civic LX 4-Door Sedan, Automobile-Catalog; Honda Civic 4th-gen North America reference	四代sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.1	59.6	1988/1989 Honda Civic Wagon, Automobile-Catalog / 1988 Civic Wagon brochure	高车身wagon	待终核: 1989美国逐年页面及AU/NA高度口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog / 1989 Honda CRX, CarsGuide	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 25 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Wagon	拆出	1983 Civic Wagon 已有完整三维：157.3×62.2×54.1，可单独推进为可入库；1980-1982 仍只得到范围/代际口径，继续待补强。
汽车目录

Honda Civic gen2 Hatchback	稳定	1981 hatchback 为 148.0×62.2×53.0，1982 hatchback 为 148.0×62.2，现有 1980-1983 hatchback 行继续可入库。
汽车目录
+1

Honda Civic gen2 Sedan	稳定	1980 sedan 有完整三维；1981 sedan 只有 Car and Driver 的结构增量说明，不是完整三维表；1982/1983 有 Automobile-Catalog 口径，继续保留 1981 待终核。
汽车目录
+1

Honda Civic gen3 Sedan	稳定	1985 sedan 已有 163.4×64.0×54.5；1986-1987 sedan 仍缺逐年结构来源，继续待补强。
汽车目录

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	147.8	59.3	53.0	Honda Civic first generation North America hatchback; 1975 3-Door Automobile-Catalog	早期hatch	待终核: 1976-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980	161.0	62.2	53.1	1980 Honda Civic 4-Door Sedan EX, Automobile-Catalog	1980 sedan存在性与其他资料口径冲突	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981	161.0	62.2	54.2	1981 Car and Driver Civic Sedan dimensional delta from 1981 hatchback	sedan长车身	待终核: 1981完整三维表
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1982-1983	161.4	61.6	53.2	1982/1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1982	160.8	62.2	54.3	Honda Civic second generation wagon dimensions / 1980-1982 CarsGuide range	wagon高车身	待补强: 1980-1982逐年wagon页面
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1983	157.3	62.2	54.1	1983 Honda Civic Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.0	53.0	Honda Civic 3rd gen hatchback reference	短车身hatch	待补强: 1984-1987
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1985	163.4	64.0	54.5	1984/1985 Honda Civic 4-Door Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1986-1987	164.0	64.0	55.0	Honda Civic 3rd gen sedan reference	sedan长车身	待补强: 1986-1987逐年/结构
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	166.5	65.9	53.5	1989 Honda Civic LX 4-Door Sedan, Automobile-Catalog; Honda Civic 4th-gen North America reference	四代sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.1	59.6	1988/1989 Honda Civic Wagon, Automobile-Catalog / 1988 Civic Wagon brochure	高车身wagon	待终核: 1989美国逐年页面及AU/NA高度口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog / 1989 Honda CRX, CarsGuide	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 26 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Sedan	推进	1981 sedan 继续按 C&D 对 1981 sedan 的结构增量说明处理：相对 hatchback 加长 13.0 in、加高 1.2 in；结合 1981 hatchback 148.0×62.2×53.0，可暂定为 161.0×62.2×54.2，但因不是完整三维表，本轮仍保留“待终核”。
汽车目录
+1

Honda Civic gen2 Wagon	推进	CarsGuide 1980/1981 尺寸范围显示二代 Civic 长度范围 3760-3995 mm、宽 1580 mm、高度范围 1335-1375 mm，可与 1983 wagon 3995×1580×1375 mm 对应；本轮把 1980-1983 wagon 统一为 157.3×62.2×54.1，并推进为可入库。
汽车指南
+2
汽车指南
+2

Honda Civic gen3 Hatchback	推进	1986 Civic S 页面给出 150.0×64.4×52.8；1984 CarsGuide 范围也支撑 hatchback 约 150 in 长、约 52.8 in 高。本轮将 gen3 hatchback 从待补强推进为可入库，但参考车型标注为 1984-1987 hatchback/spec range。
汽车目录
+1

Honda Civic gen3 Sedan	推进	1985 sedan 已有 163.4×64.0×54.5；CarsGuide 1984 范围可覆盖 sedan 长度 4145 mm 级别；本轮把 1984-1987 sedan 统一为 163.4×64.2×54.5，并推进为可入库。
汽车目录
+2
汽车目录
+2

剩余缺口	稳定	剩余仍为：Accord 1990 wagon 缺美国 wagon 结构；Civic gen1 1974-1979 hatch、gen1 sedan、gen1 1973-1978 wagon；Civic gen4 1988-1989 wagon 高度口径仍待终核。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	147.8	59.3	53.0	Honda Civic first generation North America hatchback; 1975 3-Door Automobile-Catalog	早期hatch	待终核: 1976-1979逐年/结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic 1st gen wagon / North America max	wagon高点	待补强: 1973-1978逐年/美国结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980	161.0	62.2	53.1	1980 Honda Civic 4-Door Sedan EX, Automobile-Catalog	1980 sedan存在性与其他资料口径冲突	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981	161.0	62.2	54.2	1981 Car and Driver Civic Sedan dimensional delta from 1981 hatchback	sedan长车身	待终核: 1981完整三维表
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1982-1983	161.4	61.6	53.2	1982/1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1980/1981/1982 Honda Civic dimension range / 1983 Honda Civic Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.4	52.8	1984-1987 Honda Civic Hatchback / 1986 Honda Civic S, Automobile-Catalog / CarsGuide range	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	163.4	64.2	54.5	1984/1985 Honda Civic Sedan, Automobile-Catalog / 1984-1987 Civic sedan range	三代sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	166.5	65.9	53.5	1989 Honda Civic LX 4-Door Sedan, Automobile-Catalog; Honda Civic 4th-gen North America reference	四代sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.1	59.6	1988/1989 Honda Civic Wagon, Automobile-Catalog / 1988 Civic Wagon brochure	高车身wagon	待终核: 1989美国逐年页面及AU/NA高度口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog / 1989 Honda CRX, CarsGuide	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 27 / 下一步 ---
更新点

车型	操作	描述
Honda Accord 1990 Wagon	稳定	继续保留缺数据；Honda 官方 1990 Accord 规格只列 2-Door / 4-Door，另有资料说明 1991 Accord Wagon 是美国设计/制造的首款 Honda 车型，因此不把 1990 wagon 强行入库。
Facebook

Honda Civic gen1 Hatchback	拆出	1978 Civic 2-Door 可核到 139.4×59.3；第一代公开资料同时显示 North America 147.8 in 与 2-door 短车身并存，因此 1974-1979 不再整段标 147.8 可入库，保留待终核。
维基百科
+1

Honda Civic gen1 Wagon	稳定	1978 Civic 尺寸范围为长 3560-3825 mm、高 1325-1375 mm，能证明 1978 有更长/更高结构，但不能完整证明 1973-1978 北美 wagon 逐年尺寸；继续待补强。
汽车指南

Honda Civic gen2 Sedan/Wagon	推进	gen2 wagon 公开资料与 1983 wagon 页面均支持 157.3×62.2×54.1；gen2 sedan 1980/1982/1983 可入库，1981 仍保留待终核。
汽车目录
+2
汽车目录
+2

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; 1991 Accord Wagon reported as first U.S.-designed/developed/manufactured Honda	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	147.8	59.3	53.0	1974-1979 Honda Civic North America Hatchback / 1975 3-Door Automobile-Catalog / first-gen NA max reference	早期hatch；北美保险杠加长段	待终核: 1976-1979逐年结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic first generation wagon reference / 1978 Civic dimension range	早期wagon	待补强: 1973-1978逐年美国wagon结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980	161.0	62.2	53.1	1980 Honda Civic 4-Door Sedan EX, Automobile-Catalog	1980 sedan存在性与其他资料口径冲突	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981	161.0	62.2	54.2	1981 Car and Driver Civic Sedan dimensional delta from 1981 hatchback	sedan长车身	待终核: 1981完整三维表
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1982-1983	161.4	61.6	53.2	1982/1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1980/1981/1982 Honda Civic wagon dimension range / 1983 Honda Civic Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.4	52.8	1984-1987 Honda Civic Hatchback / 1986 Honda Civic S, Automobile-Catalog / CarsGuide range	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	163.4	64.2	54.5	1984/1985 Honda Civic Sedan, Automobile-Catalog / 1984-1987 Civic sedan range	三代sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	166.5	65.9	53.5	1989 Honda Civic LX 4-Door Sedan, Automobile-Catalog; Honda Civic 4th-gen North America reference	四代sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.1	59.6	1988/1989 Honda Civic Wagon, Automobile-Catalog / 1988 Civic Wagon brochure	高车身wagon	待终核: 1989美国逐年页面及AU/NA高度口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog / 1989 Honda CRX, CarsGuide	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 28 / 下一步 ---
更新点

车型	操作	描述
Honda Civic gen2 Sedan 1981	稳定	1981 sedan 仍只找到 C&D 的结构增量说明：相对 hatchback 增加 13.0 in 车长、1.2 in 车高；1981 hatchback 完整尺寸为 148.0×62.2×53.0，因此 1981 sedan 暂维持 161.0×62.2×54.2，但不转可入库。
Car and Driver
+1

Honda Civic gen1 Hatch/Wagon	稳定	第一代公开资料能证明 North America hatchback 147.8 in、wagon 160.0 in 级别，但仍不足以证明 1974-1979 hatch 与 1973-1978 wagon 的逐年/美国结构完整口径，继续保留待终核/待补强。
维基百科

Honda Civic gen4 Wagon	稳定	1989 Civic 尺寸范围最高高度约 1515 mm，但该范围仍可能混合不同结构/市场口径；1990 Edmunds wagon 高度为 56.1 in，与 1988-1989 行的 59.6 in 存在高度口径差异，继续保留待终核。
汽车指南
+1

Honda Accord 1990 Wagon	稳定	1990 Accord wagon 仍无美国 wagon 结构来源，保留缺数据。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1991	184.8	67.9	52.2	1991 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1992	185.2	67.1	54.1	1992 Honda Accord Coupe, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen4 midsize	1993	185.2	67.1	52.2	1993 Honda Accord Coupe DX, Edmunds	后期coupe低车顶	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1990				Honda official 1990 Accord specs only list 2-Door/4-Door; no U.S. wagon source found	1990 wagon未确认美国销售	缺数据: 1990 wagon
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1991	186.0	67.9	55.1	1991 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1992	186.8	67.5	55.1	1992 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen4 midsize	1993	186.8	67.5	53.2	1993 Honda Accord Wagon, Edmunds	wagon更长更宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Sedan, Edmunds	中期sedan	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Sedan/Wagon max, Edmunds	Sedan/Wagon同长宽；高点来自wagon口径	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Sedan/Wagon, Edmunds	Sedan/Wagon同长宽	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1994-1995	187.8	70.1	55.9	1994/1995 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1996	188.4	70.1	57.4	1996 Honda Accord Wagon EX, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	两厢车	Wagon	Std.	gen5 midsize	1997	188.4	70.1	56.0	1997 Honda Accord Wagon, Edmunds	Wagon高尾厢	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1994-1995	184.0	70.1	55.1	1994/1995 Honda Accord Coupe max, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen5 midsize	1996-1997	185.6	70.1	54.7	1996/1997 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1998	188.8	70.3	57.3	1998 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	1999	188.8	70.3	56.9	1999 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2000	188.8	70.3	57.3	2000 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen6 large	2001-2002	189.4	70.3	57.3	2001/2002 Honda Accord Sedan max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1998	186.8	70.3	55.1	1998 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	1999	188.8	70.3	56.9	1999 Honda Accord Coupe EX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2000	186.6	70.3	55.3	2000 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2001	186.8	70.3	54.9	2001 Honda Accord Coupe LX, Edmunds	双门低车顶	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen6 midsize	2002	186.8	70.3	55.3	2002 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2003-2005	189.5	71.5	57.1	2003/2004/2005 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2006	191.1	71.6	57.2	2006 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen7 large	2007	191.1	71.6	57.3	2007 Honda Accord Sedan EX-L V6 max, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen7 midsize	2003-2007	187.6	71.3	55.7	2003/2004/2005/2006/2007 Honda Accord Coupe, Edmunds	双门低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2008-2011	194.1	72.7	58.1	2008/2009/2010/2011 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen8 large	2012	194.9	72.7	58.1	2012 Honda Accord Sedan, Edmunds	八代sedan较长	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen8 large	2008-2012	191.0	72.8	56.4	2008/2009/2010/2011/2012 Honda Accord Coupe, Edmunds	双门较短低车顶	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9 large	2013-2015	191.4	72.8	57.7	2013/2014/2015 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen9.5 large	2016-2017	192.5	72.8	57.7	2016/2017 Honda Accord Sedan, Edmunds		可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9 large	2013-2015	189.2	72.8	56.5	2013/2014/2015 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen9.5 large	2016-2017	189.5	73.0	56.5	2016/2017 Honda Accord Coupe, Edmunds	双门较短	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen11 large	2023-2026	195.7	73.3	57.1	2023/2024/2025/2026 Honda Accord Sedan, Edmunds	现款大车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1973	139.8	59.3	53.0	1973 Honda Civic Hatchback, Automobile-Catalog	早期短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen1 compact	1974-1979	147.8	59.3	53.0	1974-1979 Honda Civic North America Hatchback / 1975 3-Door Automobile-Catalog / first-gen NA max reference	早期hatch；北美保险杠加长段	待终核: 1976-1979逐年结构
Honda Civic	Honda	三厢车	Sedan	Std.	gen1 compact	1973-1979				Honda Civic first generation; U.S. four-door sedan not confirmed / reported not available	早期sedan	缺数据: 美国sedan结构未确认
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1979	157.3	62.2	54.1	1979 Honda Civic Wagon, CarsGuide	wagon高点	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen1 compact	1973-1978				Honda Civic first generation wagon reference / 1978 Civic dimension range	早期wagon	待补强: 1973-1978逐年美国wagon结构
Honda Civic	Honda	两厢车	Hatchback	Std.	gen2 compact	1980-1983	148.0	62.2	53.1	1980/1981/1982/1983 Honda Civic Hatchback, Automobile-Catalog / CarsGuide	早期短hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1980	161.0	62.2	53.1	1980 Honda Civic 4-Door Sedan EX, Automobile-Catalog	1980 sedan存在性与其他资料口径冲突	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1981	161.0	62.2	54.2	1981 Car and Driver Civic Sedan dimensional delta from 1981 hatchback	sedan长车身	待终核: 1981完整三维表
Honda Civic	Honda	三厢车	Sedan	Std.	gen2 compact	1982-1983	161.4	61.6	53.2	1982/1983 Honda Civic Sedan, Automobile-Catalog	sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen2 compact	1980-1983	157.3	62.2	54.1	1980/1981/1982 Honda Civic wagon dimension range / 1983 Honda Civic Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen3 compact	1984-1987	150.0	64.4	52.8	1984-1987 Honda Civic Hatchback / 1986 Honda Civic S, Automobile-Catalog / CarsGuide range	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen3 compact	1984-1987	163.4	64.2	54.5	1984/1985 Honda Civic Sedan, Automobile-Catalog / 1984-1987 Civic sedan range	三代sedan长车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1984	157.1	63.9	58.3	1984 Honda Civic Wagon, Honda official	wagon高车身	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen3 compact	1985-1987	159.1	64.8	59.4	1985/1986/1987 Honda Civic 4WD Wagon, Automobile-Catalog	wagon高车身	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1988-1989	166.5	65.9	53.5	1989 Honda Civic LX 4-Door Sedan, Automobile-Catalog; Honda Civic 4th-gen North America reference	四代sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen4 compact	1990-1991	168.8	66.7	53.5	1990/1991 Honda Civic Sedan, Edmunds	四代sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1988-1989	157.1	66.3	52.5	1988/1989 Honda Civic Hatchback, Automobile-Catalog / 1990-1991 Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen4 compact	1990-1991	157.1	66.3	52.5	1990/1991 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1988-1989	161.6	66.1	59.6	1988/1989 Honda Civic Wagon, Automobile-Catalog / 1988 Civic Wagon brochure	高车身wagon	待终核: 1989美国逐年页面及AU/NA高度口径
Honda Civic	Honda	两厢车	Wagon	Std.	gen4 compact	1990-1991	161.7	66.1	56.9	1990/1991 Honda Civic Wagon 4WD, Edmunds	高车身wagon	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1988-1989	147.8	65.9	50.0	1988 Honda CRX Si, Automobile-Catalog / 1989 Honda CRX, CarsGuide	CRX短车身低车顶	可入库
Honda Civic	Honda	跑车	Coupe	CRX	gen4 compact	1990-1991	148.5	65.9	50.1	1990/1991 Honda Civic CRX, Edmunds	CRX短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1992	173.0	67.0	54.1	1992 Honda Civic Sedan DX/LX/EX, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen5 compact	1993-1995	173.0	66.9	51.7	1993/1994/1995 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen5 compact	1993-1995	172.8	66.9	50.9	1993/1994/1995 Honda Civic Coupe, Edmunds	双门低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1992	160.2	67.0	53.0	1992 Honda Civic CX/Si Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen5 compact	1993-1995	160.2	66.9	50.7	1993/1994/1995 Honda Civic Hatchback, Edmunds	短车身低车顶	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen6 compact	1996-2000	175.1	67.1	54.7	1996/1997/1998/1999/2000 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen6 compact	1996-2000	175.1	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Coupe, Edmunds	双门较低	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen6 compact	1996-2000	164.2	67.1	54.1	1996/1997/1998/1999/2000 Honda Civic Hatchback, Edmunds	短车身hatch	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2001-2003	174.6	67.5	56.7	2001/2002/2003 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen7 compact	2004-2005	175.4	67.5	56.7	2004/2005 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2001-2003	174.7	66.7	55.1	2001/2002/2003 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen7 compact	2004-2005	175.4	66.7	55.1	2004/2005 Honda Civic Coupe, Edmunds	双门更窄更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2006	177.3	69.0	56.5	2006 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2007-2008	176.7	69.0	56.5	2007/2008 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen8 midsize	2009-2011	177.3	69.0	56.5	2009/2010/2011 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2006	175.5	68.9	55.0	2006 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2007-2008	174.8	68.9	53.5	2007/2008 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen8 compact	2009-2011	175.5	68.9	55.0	2009/2010/2011 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2012	177.3	69.0	56.5	2012 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen9 midsize	2013-2015	179.4	69.0	56.5	2013/2014/2015 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2012	175.5	69.0	55.0	2012 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2013	175.5	69.0	55.0	2013 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	跑车	Coupe	Std.	gen9 compact	2014-2015	177.9	69.0	55.0	2014/2015 Honda Civic Coupe, Edmunds	双门更短更低	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2016-2019	182.3	70.8	55.7	2016/2017/2018/2019 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen10 midsize	2020-2021	182.7	70.9	55.7	2020/2021 Honda Civic Sedan, Edmunds		可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2017-2019	177.9	70.8	56.5	2017/2018/2019 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen10 compact	2020-2021	177.9	70.8	56.3	2020/2021 Honda Civic Hatchback, Edmunds	普通hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen10 compact	2017-2021	179.4	73.9	56.5	2017/2018/2019/2020/2021 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11 midsize	2022-2024	184.0	70.9	55.7	2022/2023/2024 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	三厢车	Sedan	Std.	gen11.5 midsize	2025-2026	184.8	70.9	55.7	2025/2026 Honda Civic Sedan, Edmunds	现款sedan	可入库
Honda Civic	Honda	两厢车	Hatchback	Std.	gen11 compact	2022-2026	179.0	70.9	55.7	2022/2023/2024/2025/2026 Honda Civic Hatchback, Edmunds	现款hatch短车身	可入库
Honda Civic	Honda	两厢车	Hatchback	Type R	gen11 compact	2023-2026	180.9	74.4	55.4	2023/2024/2025/2026 Honda Civic Type R, Edmunds	宽体性能版	可入库
Honda Clarity	Honda	三厢车	Sedan	inc: EV/FCEV/PHEV	gen1 midsize sedan	2017-2021	192.7	73.9	58.2	2017/2018/2019/2020/2021 Honda Clarity Fuel Cell/Electric/Plug-In Hybrid, Edmunds	新能源轿车	可入库
Honda Clarity Plug In	Honda	三厢车	Sedan	PHEV	gen1 midsize sedan	2018-2021	192.7	73.9	58.2	2018/2019/2020/2021 Honda Clarity Plug-In Hybrid, Edmunds	插混轿车	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2010-2012	196.8	74.7	65.7	2010/2011/2012 Honda Accord Crosstour, Edmunds	5门跨界hatch	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1 crossover hatchback	2013	196.6	74.7	65.7	2013 Honda Crosstour, Edmunds	后期车身但高度仍为65.7	可入库
Honda Crosstour	Honda	越野车	Hatchback	Std.	gen1.5 crossover hatchback	2014-2015	196.6	74.7	61.5	2014/2015 Honda Crosstour, Edmunds	后期车高降低	可入库
Honda CR-V	Honda	越野车	SUV	Std.	gen1 compact SUV	1997-2001	177.6	68.9	65.9	1997/1998/1999/2000/2001 Honda CR-V, Edmunds	初代CR-V	可入库

下一步。


--- Round 29 / 下一步 ---
更新点：

车型	操作	描述
Ford Mustang Fox-body	拆出/值修改	1979-1986 hatchback 按高度阶段拆分；1988-1989 与 1990-1991 宽度口径不同，后期 Fox-body coupe/hatchback/convertible 拆成两段。
conceptcarz.com
+2
Edmunds
+2

Ford Mustang SVO	拆出	1984 SVO 为 181.0 / 69.1 / 51.9；1985-1986 SVO 保留为 180.8 / 69.1 / 52.1。
汽车目录
+1

Ford Taurus	稳定/值修改	补齐 gen1 sedan/wagon 与 gen4 sedan/wagon 剩余年份；gen1 wagon 高度按 55.1 修正，gen4 sedan 2004 高度按同代最大仍保留 56.1。
Edmunds
+3
维基百科
+3
AutoDetective
+3

GMC Yukon / Yukon XL	稳定/值修改	补齐 Yukon gen1 2dr/4dr、2000 Yukon 与 Yukon XL 2000/2001 口径；2000 Yukon 常规版改为 198.9 / 78.9 / 76.5，Yukon XL 2000-2001 按 219.3 / 78.9 / 75.8 入库。
Edmunds
+4
Edmunds
+4
Edmunds
+4

当前批次更新后的完整可替换 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Ford Mustang	Ford	两厢车	Hatchback	Std.	gen3 Fox-body	1979-1982	179.3	69.1	51.5	1979/1980/1981/1982 Ford Mustang Hatchback, MustangSpecs/Wikipedia	早期Fox-body liftback	可入库
Ford Mustang	Ford	两厢车	Hatchback	Std.	gen3 Fox-body	1983-1984	179.3	69.1	51.9	1983/1984 Ford Mustang Hatchback, MustangSpecs/Wikipedia	早期Fox-body liftback	可入库
Ford Mustang	Ford	两厢车	Hatchback	Std.	gen3 Fox-body	1985-1986	179.3	69.1	52.1	1985/1986 Ford Mustang Hatchback, CJ Pony Parts/Conceptcarz	早期Fox-body liftback	可入库
Ford Mustang	Ford	跑车	Coupe	SVO	gen3 Fox-body	1984	181.0	69.1	51.9	1984 Ford Mustang SVO, Automobile-Catalog	SVO长鼻特殊版	可入库
Ford Mustang	Ford	跑车	Coupe	SVO	gen3 Fox-body	1985-1986	180.8	69.1	52.1	1985/1986 Ford Mustang SVO, Carfolio/Conceptcarz/MustangSpecs	SVO长鼻特殊版	可入库
Ford Mustang	Ford	跑车	Coupe	Std.	gen3 Fox-body	1988-1989	179.6	69.1	52.1	1988/1989 Ford Mustang Coupe, Conceptcarz	后期Fox-body	可入库
Ford Mustang	Ford	跑车	Coupe	Std.	gen3 Fox-body	1990-1991	179.6	68.3	52.1	1990/1991 Ford Mustang Coupe, Edmunds	后期Fox-body	可入库
Ford Mustang	Ford	两厢车	Hatchback	Std.	gen3 Fox-body	1988-1989	179.6	69.1	52.1	1988/1989 Ford Mustang Hatchback, Conceptcarz	后期Fox-body hatchback	可入库
Ford Mustang	Ford	两厢车	Hatchback	Std.	gen3 Fox-body	1990-1991	179.6	68.3	52.1	1990/1991 Ford Mustang Hatchback, Edmunds	后期Fox-body hatchback	可入库
Ford Mustang	Ford	跑车	Convertible	Std.	gen3 Fox-body	1988-1989	179.6	69.1	52.1	1988/1989 Ford Mustang Convertible, Conceptcarz	后期Fox-body convertible	可入库
Ford Mustang	Ford	跑车	Convertible	Std.	gen3 Fox-body	1990-1991	179.6	68.3	52.1	1990/1991 Ford Mustang Convertible, Edmunds	后期Fox-body convertible	可入库
Ford Mustang	Ford	跑车	Convertible	Std.	gen5 facelift	2010-2012	188.1	73.9	56.1	2010/2011/2012 Ford Mustang Convertible V6, Edmunds	软顶更高	可入库
Ford Mustang	Ford	跑车	Coupe	Dark Horse	gen7 S650	2024-2026	189.7	75.5	55.2	2024/2025/2026 Ford Mustang Dark Horse, Edmunds/Ford	高性能版	可入库
Ford Taurus	Ford	三厢车	Sedan	Std.	gen1 midsize	1986-1990	188.4	70.8	54.3	1986/1987/1988/1989/1990 Ford Taurus Sedan, Automobile-Catalog/AutoDetective/Carfolio		可入库
Ford Taurus	Ford	三厢车	Sedan	Std.	gen1 midsize	1991	188.4	70.8	54.1	1991 Ford Taurus Sedan, Edmunds	末年高度略低	可入库
Ford Taurus	Ford	两厢车	Wagon	Std.	gen1 midsize	1986-1991	191.9	70.8	55.1	1986/1987/1988/1989/1990/1991 Ford Taurus Wagon, Automobile-Catalog/AutoDetective/Edmunds	长车顶	可入库
Ford Taurus	Ford	三厢车	Sedan	Std.	gen2 midsize	1992-1993	192.0	71.2	54.1	1992/1993 Ford Taurus Sedan, Edmunds		可入库
Ford Taurus	Ford	三厢车	Sedan	Std.	gen2 midsize	1994	192.0	70.7	54.1	1994 Ford Taurus Sedan, Edmunds	1994宽度口径较窄	可入库
Ford Taurus	Ford	三厢车	Sedan	Std.	gen2 midsize	1995	192.0	71.2	54.1	1995 Ford Taurus Sedan, Edmunds		可入库
Ford Taurus	Ford	两厢车	Wagon	Std.	gen2 midsize	1992-1993	193.1	71.2	55.5	1992/1993 Ford Taurus Wagon, Edmunds	长车顶	可入库
Ford Taurus	Ford	两厢车	Wagon	Std.	gen2 midsize	1994	193.1	70.7	55.5	1994 Ford Taurus Wagon, Edmunds	1994宽度口径较窄	可入库
Ford Taurus	Ford	两厢车	Wagon	Std.	gen2 midsize	1995	193.1	71.2	55.5	1995 Ford Taurus Wagon, Edmunds	长车顶	可入库
Ford Taurus	Ford	三厢车	Sedan	Std.	gen3 midsize	1996-1999	197.5	73.0	55.1	1996/1997/1998/1999 Ford Taurus Sedan, Edmunds	椭圆车身早期	可入库
Ford Taurus	Ford	三厢车	Sedan	Std.	gen4 midsize	2000-2007	197.6	73.0	56.1	2000/2001/2002/2003/2004/2005/2006/2007 Ford Taurus Sedan, Edmunds	后期高度增加	可入库
Ford Taurus	Ford	两厢车	Wagon	Std.	gen3 midsize	1996	199.6	73.0	57.6	1996 Ford Taurus Wagon, Edmunds	长车顶	可入库
Ford Taurus	Ford	两厢车	Wagon	Std.	gen3 midsize	1997-1999	199.6	73.0	57.8	1997/1998/1999 Ford Taurus Wagon, Edmunds	长车顶	可入库
Ford Taurus	Ford	两厢车	Wagon	Std.	gen4 midsize	2000-2005	197.7	73.0	57.8	2000/2001/2002/2003/2004/2005 Ford Taurus Wagon, Edmunds	后期wagon长度缩短	可入库
Ford Taurus	Ford	三厢车	Sedan	Std.	gen5 full-size	2008-2009	201.8	74.5	61.5	2008/2009 Ford Taurus Sedan, Edmunds	高车身	可入库
Ford Taurus	Ford	三厢车	Sedan	SHO	gen6 full-size	2010-2016	202.9	76.2	60.7	2010/2011/2012/2013/2014/2015/2016 Ford Taurus SHO, Edmunds	SHO高性能版	可入库
Ford Taurus	Ford	三厢车	Sedan	SHO	gen6 full-size	2017-2018	203.0	76.2	60.7	2017/2018 Ford Taurus SHO, Edmunds	SHO长度微增	可入库
Ford Taurus	Ford	三厢车	Sedan	SHO	gen6 full-size	2019	202.9	76.2	60.7	2019 Ford Taurus SHO, Edmunds	SHO高性能版	可入库
Ford Thunderbird	Ford	跑车	Coupe	Std.	gen9 personal luxury	1983-1986	197.6	71.1	53.2	1983-1986 Ford Thunderbird Coupe, Automobile-Catalog/Wikipedia	早期Fox coupe	可入库
Ford Thunderbird	Ford	跑车	Coupe	Std.	gen9 personal luxury	1987-1988	202.1	71.1	53.4	1987/1988 Ford Thunderbird LX / Turbo Coupe, Conceptcarz	后期Fox coupe	可入库
Ford Thunderbird	Ford	跑车	Coupe	Std.	gen10 personal luxury	1989-1993	198.7	72.7	53.1	1989-1993 Ford Thunderbird LX / SC, Edmunds/Wikipedia	MN12宽体coupe	可入库
Ford Thunderbird	Ford	跑车	Coupe	Std.	gen10 personal luxury	1994-1995	200.3	72.7	53.0	1994/1995 Ford Thunderbird Coupe / Super Coupe, Edmunds/Wikipedia	facelift后更长	可入库
Ford Thunderbird	Ford	跑车	Coupe	Std.	gen10 personal luxury	1996-1997	200.3	73.2	52.5	1996/1997 Ford Thunderbird Coupe, Wikipedia	后期宽度增加	可入库
Ford Thunderbird	Ford	跑车	Convertible	Std.	gen11 personal luxury	2002-2005	186.3	72.0	52.1	2002/2003/2004/2005 Ford Thunderbird Convertible, Edmunds	retro双座敞篷	可入库
Genesis G90	Genesis	三厢车	Sedan	Std.	gen1 full-size sedan	2017-2022	204.9	75.4	58.9	2017/2018/2019/2020/2021/2022 Genesis G90, Edmunds	大型豪华sedan	可入库
Genesis G90	Genesis	三厢车	Sedan	Std.	gen2 full-size sedan	2023-2026	207.7	76.0	58.7	2023/2024/2025/2026 Genesis G90, Edmunds/Genesis/C&D	大型豪华sedan	可入库
Genesis GV60	Genesis	越野车	CUV	EV	gen1 electric SUV	2023-2025	177.8	74.4	62.4	2023/2024/2025 Genesis GV60, Edmunds		可入库
Genesis GV70	Genesis	越野车	SUV	Std.	gen1 compact luxury SUV	2022-2026	185.6	75.2	64.2	2022/2023/2024/2025/2026 Genesis GV70, Edmunds	豪华SUV	可入库
Genesis GV80	Genesis	越野车	SUV	Std.	gen1 midsize SUV	2021-2024	194.7	77.8	67.5	2021/2022/2023/2024 Genesis GV80, Edmunds	中大型SUV	可入库
GMC Acadia	GMC	越野车	SUV	Std.	gen1 large SUV	2007-2012	200.7	78.2	72.8	2007/2008/2009/2010/2011/2012 GMC Acadia, Edmunds	早期gen1	可入库
GMC Acadia	GMC	越野车	SUV	Std.	gen1 large SUV	2013-2016	200.8	78.9	72.6	2013/2014/2015/2016 GMC Acadia, Edmunds	facelift后宽度增加	可入库
GMC Acadia	GMC	越野车	SUV	Std.	gen2 midsize SUV	2017-2020	193.6	75.4	68.7	2017/2018/2019/2020 GMC Acadia Denali/SLT, Edmunds	2017-2020取最大trim外廓	可入库
GMC Acadia	GMC	越野车	SUV	Std.	gen2 midsize SUV	2021-2023	193.4	75.4	66.7	2021/2022/2023 GMC Acadia, Edmunds		可入库
GMC Acadia	GMC	越野车	SUV	Std.	gen3 large SUV	2024-2026	204.0	80.0	72.0	2024/2025/2026 GMC Acadia AT4, Edmunds	AT4为最大外廓	可入库
GMC Envoy	GMC	越野车	SUV	Std.	gen2 midsize SUV	2002-2009	191.6	74.7	71.9	2002/2003/2004/2005/2006/2007/2008/2009 GMC Envoy, Edmunds	不含XL/XUV	可入库
GMC Hummer SUV	GMC	越野车	SUV	EV widebody	gen1 EV SUV	2024-2026	206.7	86.5	77.8	2024/2025/2026 GMC Hummer EV SUV, GMC/Group1 GMC	超宽电动SUV	可入库
GMC Terrain	GMC	越野车	SUV	Std.	gen1 compact SUV	2010-2016	185.3	72.8	66.3	2010/2011/2012/2013/2014/2015/2016 GMC Terrain, Edmunds	紧凑SUV	可入库
GMC Terrain	GMC	越野车	SUV	Std.	gen1 compact SUV	2017	185.5	72.8	66.3	2017 GMC Terrain, Edmunds	末年长度增加	可入库
GMC Terrain	GMC	越野车	SUV	Std.	gen2 compact SUV	2018-2024	182.3	72.4	65.4	2018/2019/2020/2021/2022/2023/2024 GMC Terrain, Edmunds	紧凑SUV	可入库
GMC Terrain	GMC	越野车	SUV	Std.	gen3 compact SUV	2025	181.0	74.5	66.2	2025 GMC Terrain Elevation, Edmunds	宽度增加	可入库
GMC Terrain	GMC	越野车	SUV	Std.	gen3 compact SUV	2026	181.0	74.5	65.8	2026 GMC Terrain Elevation, Edmunds	2026高度低于2025	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen1 2dr	1992-1994	187.7	76.4	71.0	1992/1993/1994 GMC Yukon 2dr, Edmunds/KBB	双门SUV	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen1 2dr	1995-1997	188.5	77.1	72.4	1995/1996/1997 GMC Yukon 2dr, Edmunds/AutoDetective	双门后期	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen1 4dr	1995-1999	199.6	76.8	75.0	1995/1996/1997/1998/1999 GMC Yukon 4dr, Edmunds/TheCarConnection	四门长车身	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen2 SUV	2000	198.9	78.9	76.5	2000 GMC Yukon SLT/SLE, Edmunds/TheCarConnection	全尺寸SUV	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen2 SUV	2001	198.9	78.9	76.5	2001 GMC Yukon Denali, Edmunds	Denali外廓	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen2 SUV	2002-2006	198.9	78.9	76.7	2002/2003/2004/2005/2006 GMC Yukon SLE/Fleet, Edmunds	全尺寸SUV	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen4 SUV	2015-2020	203.9	80.5	74.4	2015/2016/2017/2018/2019/2020 GMC Yukon, Edmunds	独立代际	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen5 SUV	2021-2024	210.0	81.0	76.5	2021/2022/2023/2024 GMC Yukon, Edmunds	现款短轴SUV	可入库
GMC Yukon	GMC	越野车	SUV	Std.	gen5 SUV	2025-2026	210.1	81.0	76.5	2025/2026 GMC Yukon, Edmunds/GMC	现款短轴SUV	可入库
GMC Yukon XL	GMC	越野车	SUV	Std.	gen1 full-size SUV XL	2000-2001	219.3	78.9	75.8	2000/2001 GMC Yukon XL 1500, Edmunds	加长版SUV	可入库
GMC Yukon XL	GMC	越野车	SUV	Std.	gen1 full-size SUV XL	2002-2006	219.3	78.8	75.8	2002/2003/2004/2005/2006 GMC Yukon XL 1500, Edmunds/KBB	加长版SUV	可入库
GMC Yukon XL	GMC	越野车	SUV	Std.	gen2 full-size SUV XL	2007	222.4	79.1	77.1	2007 GMC Yukon XL, Edmunds	加长版SUV	可入库
GMC Yukon XL	GMC	越野车	SUV	Std.	gen2 full-size SUV XL	2008-2014	222.4	79.1	76.8	2008/2009/2010/2011/2012/2013/2014 GMC Yukon XL, Edmunds	加长版SUV	可入库
GMC Yukon XL	GMC	越野车	SUV	Std.	gen3 full-size SUV XL	2015	224.3	80.5	74.4	2015 GMC Yukon XL, Edmunds	加长版SUV	可入库
GMC Yukon XL	GMC	越野车	SUV	Std.	gen3 full-size SUV XL	2016-2020	224.4	80.5	74.4	2016/2017/2018/2019/2020 GMC Yukon XL, Edmunds	加长版SUV	可入库
GMC Yukon XL	GMC	越野车	SUV	Std.	gen4 full-size SUV XL	2021-2026	225.2	81.0	76.5	2021/2022/2023/2024/2025/2026 GMC Yukon XL, Edmunds	加长版SUV	可入库
Honda Accord	Honda	两厢车	Hatchback	Std.	gen1 compact	1976	162.8	63.8	52.4	1976 Honda Accord Hatchback, Automobile-Catalog/HowStuffWorks	初代短车身hatch	可入库
Honda Accord	Honda	两厢车	Hatchback	Std.	gen1 compact	1977-1981	162.4	63.8	52.6	1977/1978/1979/1980/1981 Honda Accord Hatchback, Auto-Data/CarsGuide	初代短车身hatch	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen1 compact	1979-1981	171.9	63.8	53.3	1979/1980/1981 Honda Accord Sedan, Automobile-Catalog	初代sedan更长	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen2 compact	1982-1984	173.7	65.0	54.1	1982/1983/1984 Honda Accord Sedan, Automobile-Catalog/CarsGuide	二代sedan早期	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen2 compact	1985	175.4	65.6	54.1	1985 Honda Accord Sedan, Automobile-Catalog	二代sedan末年加长	可入库
Honda Accord	Honda	两厢车	Hatchback	Std.	gen2 compact	1982-1984	165.7	65.0	52.6	1982/1983/1984 Honda Accord Hatchback, Automobile-Catalog/CarsGuide	短车身hatch早期	可入库
Honda Accord	Honda	两厢车	Hatchback	Std.	gen2 compact	1985	167.5	65.6	53.3	1985 Honda Accord Hatchback, Automobile-Catalog	短车身hatch末年加宽	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen3 compact	1986-1989	179.7	67.4	53.4	1986/1987/1988/1989 Honda Accord Sedan, Automobile-Catalog/Carfolio	三代sedan	可入库
Honda Accord	Honda	两厢车	Hatchback	Std.	gen3 compact	1986-1989	174.8	66.7	52.6	1986/1987/1988/1989 Honda Accord Hatchback, Automobile-Catalog/AutoDetective	短车身hatch	可入库
Honda Accord	Honda	跑车	Coupe	Std.	gen3 compact	1988-1989	179.7	66.7	52.8	1988/1989 Honda Accord Coupe, Automobile-Catalog/Carfolio	三代coupe	可入库
Honda Accord	Honda	三厢车	Sedan	Std.	gen4 midsize	1990-1993	185.2	67.9	54.7	1990/1991/1992/1993 Honda Accord Sedan, Edmunds	四代sedan	可入库

本批次完成。

