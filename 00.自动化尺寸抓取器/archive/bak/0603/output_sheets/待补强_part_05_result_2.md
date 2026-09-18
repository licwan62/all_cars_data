# 文件名：待补强_part_05.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作/字段	描述
Cruze / HHR / Sonic / Spark / SS	迭代状态	代表年份尺寸与现有三维口径一致，可先推进为可入库；Edmunds/C&D 显示 Cruze Hatchback 175.3/70.5/57.7、HHR 176.2/69.1/63.1、Sonic hatchback 159.8/68.3/59.7、Spark 143.1/62.8/58.4、SS 195.5/74.7/57.9。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Impala / Malibu / Tahoe / Traverse	迭代状态	代表年份尺寸与现有主数据一致，但部分长年份区间仍建议后续补全中间年份口径；Edmunds 可确认 2020 Impala、2025 Malibu、2024 Tahoe、2023 Traverse 等关键点。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Corvette / K5 Blazer / Monte Carlo / Nova / Express 长跨度	稳定	本轮未强行改为完成，仍保留具体待补强年份，避免把长跨度或老车区间误标为可入库。

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	176.9	77.4	48.8	2019 Corvette ZR1 / Z06	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2020-2026	186.7	79.7	48.6	2026 Corvette ZR1 / E-Ray / Stingray	宽体中置跑车	待补强: 2020-2025
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005/2006 Chevrolet Equinox	早期长车身SUV	待补强: 2007-2009
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2011/2016/2017 Chevrolet Equinox	紧凑SUV	待补强: 2010/2012-2015
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2023/2024 Chevrolet Equinox	紧凑SUV	待补强: 2018-2022
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024-2026	190.6	76.9	64.8	2025/2026 Chevrolet Equinox EV	EV尺寸更大	待补强: 2024
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-2002	218.8	79.2	83.7	1999 Chevrolet Express Cargo	全尺寸Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2026	224.1	79.3	84.8	2024/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2003-2023/2025
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023/2025-2026
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2011 Chevrolet Impala LTZ	大型轿车	待补强: 2006-2010/2012-2013
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1991	184.8	79.6	73.8	1990/1991 Chevrolet Blazer Edmunds	原77.8不采用	待补强: 1975-1989
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.8	76.4	71.0	1992/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	待补强: 1993
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1998/2002 Chevrolet Malibu	中型轿车	待补强: 1997/1999-2001/2003
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004/2006 Chevrolet Malibu	中型轿车	待补强: 2005/2007
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008/2011 Chevrolet Malibu	中型轿车	待补强: 2009-2010/2012
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013/2015 Chevrolet Malibu	中型轿车	待补强: 2014
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973-1977	213.3	77.6	52.9	1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1973-1975
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	Monte Carlo SS / LS specs	G-body，SS略长	待补强: 1981-1988
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Sedan, Conceptcarz	末期FWD	待补强: 1987
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Hatchback, Conceptcarz / AutoDetective	末期FWD hatch	待补强: 1987
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998-2002	174.2	66.7	53.7	2001 Chevrolet Prizm		待补强: 1998-2000/2002
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2006	196.9	78.9	76.5	2001 Chevrolet Tahoe	全尺寸SUV	待补强: 2002-2006
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007/2008 Chevrolet Tahoe	全尺寸SUV	待补强: 2009-2014
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015 Chevrolet Tahoe	全尺寸SUV	待补强: 2016-2020
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021/2023/2024 Chevrolet Tahoe	全尺寸SUV	待补强: 2022
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV	待补强: 2002-2004
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2008 Chevrolet Trailblazer SS	低矮性能SUV	待补强: 2006-2007/2009
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021-2026	174.1	71.2	65.2	2025 Chevrolet Trailblazer ACTIV	小型SUV	待补强: 2021-2024/2026
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009-2017	205.0	78.5	72.8	2009/2017 Chevrolet Traverse	三排SUV	待补强: 2010-2016
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 2 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Equinox gen1	迭代状态	2005/2006/2007/2008/2009 均核到 188.8 / 71.4 / 69.3，可入库。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Chevrolet Equinox gen2 / gen3	参考车型	新增 2010、2015、2018、2022 关键年份；但 gen2 仍缺 2012-2014，gen3 仍缺 2019-2021，暂不完成。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Chevrolet Equinox EV	拆出	2024 EV 长度为 191.6，2025/2026 为 190.6，不能压缩为 2024-2026 同一行，拆成 2024 与 2025-2026。
Edmunds
+2
Edmunds
+2

Chevrolet Express gen2 Std.	参考车型	新增 2026 Express Cargo regular 参考；长轴 Extended 新增 2025 参考，但仍缺早年与 2026 长轴。
Edmunds
+1

Chevrolet Malibu gen8	迭代状态	2013/2014/2015 已覆盖，191.5 / 73.0 / 57.6，可入库。
Edmunds

Chevrolet Trailblazer gen2	参考车型	新增 2026 Trailblazer 尺寸；2021-2024 仍待补强。
Edmunds

Chevrolet Traverse gen1	值修改/待拆	2017 Traverse 为 203.7 / 78.5 / 69.9，与 2009 的 205.0 / 78.5 / 72.8 不同，当前 2009-2017 不应直接可入库，继续待补强中间年份。
Edmunds

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	176.9	77.4	48.8	2019 Corvette ZR1 / Z06	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2020-2026	186.7	79.7	48.6	2026 Corvette ZR1 / E-Ray / Stingray	宽体中置跑车	待补强: 2020-2025
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010/2011/2015/2016/2017 Chevrolet Equinox	紧凑SUV	待补强: 2012-2014
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018/2022/2023/2024 Chevrolet Equinox	紧凑SUV	待补强: 2019-2021
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-2002	218.8	79.2	83.7	1999 Chevrolet Express Cargo	全尺寸Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2026	224.1	79.3	84.8	2024/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2003-2023/2025
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023/2026
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2011/2013 Chevrolet Impala LTZ	大型轿车	待补强: 2006-2010/2012
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1991	184.8	79.6	73.8	1990/1991 Chevrolet Blazer Edmunds	原77.8不采用	待补强: 1975-1989
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.8	76.4	71.0	1992/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	待补强: 1993
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1998/2002 Chevrolet Malibu	中型轿车	待补强: 1997/1999-2001/2003
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004/2006 Chevrolet Malibu	中型轿车	待补强: 2005/2007
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008/2011 Chevrolet Malibu	中型轿车	待补强: 2009-2010/2012
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973-1977	213.3	77.6	52.9	1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1973-1975
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	Monte Carlo SS / LS specs	G-body，SS略长	待补强: 1981-1988
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Sedan, Conceptcarz	末期FWD	待补强: 1987
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Hatchback, Conceptcarz / AutoDetective	末期FWD hatch	待补强: 1987
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998-2002	174.2	66.7	53.7	2001 Chevrolet Prizm		待补强: 1998-2000/2002
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2006	196.9	78.9	76.5	2001 Chevrolet Tahoe	全尺寸SUV	待补强: 2002-2006
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007/2008/2014 Chevrolet Tahoe	全尺寸SUV	待补强: 2009-2013
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015/2020 Chevrolet Tahoe	全尺寸SUV	待补强: 2016-2019
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021/2023/2024 Chevrolet Tahoe	全尺寸SUV	待补强: 2022
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV	待补强: 2002-2004
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2008 Chevrolet Trailblazer SS	低矮性能SUV	待补强: 2006-2007/2009
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021-2026	174.1	71.2	65.2	2025/2026 Chevrolet Trailblazer ACTIV	小型SUV	待补强: 2021-2024
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009-2017	205.0	78.5	72.8	2009/2017 Chevrolet Traverse	三排SUV，2017尺寸低于2009	待补强: 2010-2016
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 3 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Tahoe gen2	拆出 / 值修改	2001 与 2006 尺寸不同，不能继续压成 2001-2006 单行；拆成 2001 和 2002-2006 待补强。2001 为 196.9 / 78.9 / 76.5，2006 为 198.8 / 78.8 / 74.8。
Edmunds
+1

Chevrolet Tahoe gen3/gen4/gen5	迭代状态	gen3、gen4、gen5 关键年份尺寸已补强：2009/2014 为 202.0 / 79.0 / 76.9；2016/2020 为 204.0 / 80.5 / 74.4；2022 为 210.7 / 81.0 / 75.8。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Chevrolet Trailblazer gen2	拆出	2021、2022、2024、2025-2026 尺寸不完全一致，不能继续压成 2021-2026；拆成独立尺寸段。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Chevrolet Malibu gen5/gen6/gen7	参考车型	补入 1998、2007、2012 等关键年份依据；gen7 可入库，gen5/gen6 因仍未覆盖全部中间年份，继续待补强。
Edmunds
+2
Edmunds
+2

Chevrolet Prizm	参考车型	2002 尺寸可确认 174.2 / 66.7 / 53.7；但 1998-2001 仍待补强，暂不完成。
Cars.com
+1

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	176.9	77.4	48.8	2019 Corvette ZR1 / Z06	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2020-2026	186.7	79.7	48.6	2026 Corvette ZR1 / E-Ray / Stingray	宽体中置跑车	待补强: 2020-2025
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010/2011/2015/2016/2017 Chevrolet Equinox	紧凑SUV	待补强: 2012-2014
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018/2022/2023/2024 Chevrolet Equinox	紧凑SUV	待补强: 2019-2021
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-2002	218.8	79.2	83.7	1999 Chevrolet Express Cargo	全尺寸Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2026	224.1	79.3	84.8	2024/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2003-2023/2025
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023/2026
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2010/2011/2012/2013 Chevrolet Impala LTZ	大型轿车	待补强: 2006-2009
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1991	184.8	79.6	73.8	1990/1991 Chevrolet Blazer Edmunds	原77.8不采用	待补强: 1975-1989
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.8	76.4	71.0	1992/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	待补强: 1993
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1998/2002 Chevrolet Malibu	中型轿车	待补强: 1997/1999-2001/2003
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004/2006/2007 Chevrolet Malibu	中型轿车	待补强: 2005
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973-1977	213.3	77.6	52.9	1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1973-1975
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	Monte Carlo SS / LS specs	G-body，SS略长	待补强: 1981-1988
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Sedan, Conceptcarz	末期FWD	待补强: 1987
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Hatchback, Conceptcarz / AutoDetective	末期FWD hatch	待补强: 1987
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998-2002	174.2	66.7	53.7	2001/2002 Chevrolet Prizm		待补强: 1998-2000
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001	196.9	78.9	76.5	2001 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2002-2006	198.8	78.8	74.8	2006 Chevrolet Tahoe	全尺寸SUV	待补强: 2002-2005
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV	待补强: 2002-2004
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2008 Chevrolet Trailblazer SS	低矮性能SUV	待补强: 2006-2007/2009
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.3	2022 Chevrolet Trailblazer RS	小型SUV	待补强: 2023
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009-2017	205.0	78.5	72.8	2009/2017 Chevrolet Traverse	三排SUV，2017尺寸低于2009	待补强: 2010-2016
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 4 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Equinox gen2	参考车型	补入 2012/2014，当前只剩 2013 未终核；2012 Edmunds 明确为 187.8 / 72.5 / 69.3。
Edmunds
+1

Chevrolet Equinox gen3	参考车型	补入 2021，当前只剩 2019-2020 未终核；2021 Edmunds 为 183.1 / 72.6 / 65.4。
Edmunds

Chevrolet Impala gen9	参考车型	补入 2006/2009，当前只剩 2007-2008 未终核；2006 和 2009 Edmunds 均为 200.4 / 72.9 / 58.7。
Edmunds
+1

Chevrolet Malibu gen5/gen6	迭代状态	gen6 2004-2007 已覆盖，可入库；gen5 补入 1997/1999/2001/2003，仍缺 2000。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Chevrolet Prizm	拆出 / 值修改	1998、1999、2000-2002 三段尺寸不同，原 1998-2002 单行不能继续压缩；按 Edmunds 拆分为 1998、1999、2000-2002。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Chevrolet Trailblazer gen2	拆出 / 值修改	2023 ACTIV 高度 65.7，普通 LT 为 65.2；为车罩取最大高度，2022-2023 调整为 173.7 / 71.2 / 65.7，可入库。
Edmunds
+1

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	176.9	77.4	48.8	2019 Corvette ZR1 / Z06	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2020-2026	186.7	79.7	48.6	2026 Corvette ZR1 / E-Ray / Stingray	宽体中置跑车	待补强: 2020-2025
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010/2011/2012/2014/2015/2016/2017 Chevrolet Equinox	紧凑SUV	待补强: 2013
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018/2021/2022/2023/2024 Chevrolet Equinox	紧凑SUV	待补强: 2019-2020
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-2002	218.8	79.2	83.7	1999 Chevrolet Express Cargo	全尺寸Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2026	224.1	79.3	84.8	2024/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2003-2023/2025
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023/2026
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006/2009/2010/2011/2012/2013 Chevrolet Impala LTZ	大型轿车	待补强: 2007-2008
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1991	184.8	79.6	73.8	1990/1991 Chevrolet Blazer Edmunds	原77.8不采用	待补强: 1975-1989
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.8	76.4	71.0	1992/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	待补强: 1993
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997/1998/1999/2001/2002/2003 Chevrolet Malibu	中型轿车	待补强: 2000
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973-1977	213.3	77.6	52.9	1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1973-1975
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	Monte Carlo SS / LS specs	G-body，SS略长	待补强: 1981-1988
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Sedan, Conceptcarz	末期FWD	待补强: 1987
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Hatchback, Conceptcarz / AutoDetective	末期FWD hatch	待补强: 1987
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001	196.9	78.9	76.5	2001 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2002-2006	198.8	78.8	74.8	2006 Chevrolet Tahoe	全尺寸SUV	待补强: 2002-2005
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV	待补强: 2002-2004
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2008 Chevrolet Trailblazer SS	低矮性能SUV	待补强: 2006-2007/2009
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009-2012	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	待补强: 2010-2012
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	待补强: 2013-2015
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 5 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Equinox gen2	迭代状态	补齐 2013；2010-2017 尺寸统一为 187.8 / 72.5 / 69.3，可入库。
Edmunds

Chevrolet Equinox gen3	迭代状态	补齐 2020，2019 仍待终核；2020 Edmunds 为 183.1 / 72.6 / 65.4。
Edmunds

Chevrolet Impala gen9	迭代状态	补齐 2007/2008；2006-2013 尺寸统一为 200.4 / 72.9 / 58.7，可入库。
Edmunds
+1

Chevrolet Malibu gen5	值修改 / 拆出	2000 Malibu 高度存在口径差异：Edmunds 为 56.7，GM archive 为 56.4；为保持官方 GM 口径，本轮仍采用 56.4，并补齐 1997-2003。
Edmunds
+1

Chevrolet Tahoe gen2	拆出	2002/2003 与 2004/2005/2006 尺寸不一致，不能合并；拆成 2001-2003 与 2004-2006 两段。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Chevrolet Traverse gen1	参考车型	2010 和 2013 已核，说明 2009-2012 与 2013-2017 是两个尺寸段；中间年份 2011/2012/2014 仍待补。
Edmunds
+2
Edmunds
+2

Chevrolet Trailblazer gen1	拆出	2002 普通版与 EXT 差异很大：普通版 191.8 / 74.6 / 74.5，EXT 为 207.8 / 74.7 / 77.1；原 Std 行没有覆盖 EXT，先保留普通版口径待补强。
Edmunds
+1

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	176.9	77.4	48.8	2019 Corvette ZR1 / Z06	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2020-2026	186.7	79.7	48.6	2026 Corvette ZR1 / E-Ray / Stingray	宽体中置跑车	待补强: 2020-2025
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018/2020/2021/2022/2023/2024 Chevrolet Equinox	紧凑SUV	待补强: 2019
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-2002	218.8	79.2	83.7	1999 Chevrolet Express Cargo	全尺寸Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2026	224.1	79.3	84.8	2024/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2003-2023/2025
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023/2026
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1991	184.8	79.6	73.8	1990/1991 Chevrolet Blazer Edmunds	原77.8不采用	待补强: 1975-1989
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.8	76.4	71.0	1992/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	待补强: 1993
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973-1977	213.3	77.6	52.9	1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1973-1975
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	Monte Carlo SS / LS specs	G-body，SS略长	待补强: 1981-1988
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Sedan, Conceptcarz	末期FWD	待补强: 1987
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Hatchback, Conceptcarz / AutoDetective	末期FWD hatch	待补强: 1987
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2005	191.8	74.7	72.5	2002/2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	待补强: 2003-2004
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2008 Chevrolet Trailblazer SS	低矮性能SUV	待补强: 2006-2007/2009
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009-2012	205.0	78.5	72.8	2009/2010 Chevrolet Traverse	三排SUV，早期高车身	待补强: 2011-2012
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	待补强: 2014
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 6 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Equinox gen3	迭代状态	补齐 2019；2018-2024 统一为 183.1 / 72.6 / 65.4，可入库。
Edmunds
+1

Chevrolet Traverse gen1	拆出 / 值修改	2010-2012 Edmunds 显示宽度 78.4，2013-2017 facelift 后为 203.7 / 78.5 / 69.9；按尺寸段拆分，不再把 2009-2017 压成一行。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Chevrolet Trailblazer gen1 Std.	拆出	2003-2004 普通短轴为 191.8 / 74.6 / 74.5，2005 为 191.8 / 74.7 / 72.5；按高度/宽度变化拆分。
Edmunds
+2
Edmunds
+2

Chevrolet Trailblazer SS	迭代状态	2006-2009 SS 统一采用 191.8 / 74.7 / 67.8，可入库；2006 用 KBB/C&D 交叉，2007-2009 用 Edmunds。
Edmunds
+4
Kbb.com
+4
Car and Driver
+4

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	176.9	77.4	48.8	2019 Corvette ZR1 / Z06	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2020-2026	186.7	79.7	48.6	2026 Corvette ZR1 / E-Ray / Stingray	宽体中置跑车	待补强: 2020-2025
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-2002	218.8	79.2	83.7	1999 Chevrolet Express Cargo	全尺寸Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2026	224.1	79.3	84.8	2024/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2003-2023/2025
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023/2026
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1991	184.8	79.6	73.8	1990/1991 Chevrolet Blazer Edmunds	原77.8不采用	待补强: 1975-1989
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.8	76.4	71.0	1992/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	待补强: 1993
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973-1977	213.3	77.6	52.9	1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1973-1975
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	Monte Carlo SS / LS specs	G-body，SS略长	待补强: 1981-1988
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 compact	1968-1974	189.4	72.4	54.0	1968/1970/1974 Chevrolet Nova	第三代紧凑车	待补强: 1969/1971-1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Sedan, Conceptcarz	末期FWD	待补强: 1987
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Hatchback, Conceptcarz / AutoDetective	末期FWD hatch	待补强: 1987
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 7 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet K5 Blazer gen3	迭代状态	补齐 1993；1992-1994 GMT400 Blazer 三维统一为约 187.7 / 76.4 / 71.0，可入库。Edmunds 1993/1994 均显示 187.7 / 76.4 / 71.0。
Edmunds
+1

Chevrolet Express gen2 Std.	值修改 / 待补强	Edmunds 2003 标准轴为 224.1 / 79.4 / 81.6，2026 Cargo 为 224.1 / 79.3 / 84.8，说明 2003-2026 高度/宽度口径不完全一致，不能整段可入库。
Edmunds
+1

Chevrolet Express gen1	值修改 / 待补强	2002 Edmunds 标准轴为 221.5 / 79.1 / 79.6，与原 218.8 / 79.2 / 83.7 不同，暂不强行完成，需要继续按 1996-2002 年份/轴距拆分。
Edmunds

Chevrolet Monte Carlo gen2	参考车型	1977 Automobile-Catalog 可确认 213.3 / 77.6 / 52.8；1973-1975 仍待补强。
汽车目录

Chevrolet Monte Carlo gen4	值修改 / 待补强	LS 与 SS 长度/高度不同：LS 约 200.4 / 71.8 / 54.4，SS 约 202.4 / 71.8 / 54.9；原行取 SS 最大值可保留，但需继续覆盖 1981-1988。
autodetective.com
+1

Chevrolet Nova gen3	值修改 / 待补强	1974 Nova 长度 196.7，与 1968/1970 的 189.4 不同，原 1968-1974 不能继续压成单段；本轮拆为 1968-1972 待补强与 1973-1974 bumper-era。
Ground Up - SS396
+1

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	176.9	77.4	48.8	2019 Corvette ZR1 / Z06	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2020-2026	186.7	79.7	48.6	2025/2026 Corvette ZR1 / E-Ray / Stingray	宽体中置跑车	待补强: 2020-2024
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-1998	218.8	79.2	83.7	1996-1998 Chevrolet Express regular WB reference	全尺寸Van	待补强: 1996-1998高度口径
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1999-2002	221.5	79.1	79.6	2002 Chevrolet Express Cargo regular WB	全尺寸Van，2002 Edmunds口径	待补强: 1999-2001
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003	224.1	79.4	81.6	2003 Chevrolet Express Cargo regular WB	全尺寸Van，早期高度较低	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2004-2026	224.1	79.3	84.8	2024/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2004-2023/2025
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023/2026
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1991	184.8	79.6	73.8	1990/1991 Chevrolet Blazer Edmunds	原77.8不采用	待补强: 1975-1989
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.7	76.4	71.0	1992/1993/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973-1975	210.4	77.6	52.9	1973/1975 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1973-1975三维终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1976-1977	213.3	77.6	52.9	1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	1981-1988 Monte Carlo SS / LS specs	G-body，取SS最大长高	待补强: 1981-1988逐年覆盖
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1972	189.4	72.4	54.0	1968/1970 Chevrolet Nova Sedan	第三代早期紧凑车	待补强: 1969/1971-1972
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1972	189.4	72.4	54.0	1968/1970 Chevrolet Nova Coupe	第三代早期紧凑车	待补强: 1969/1971-1972
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	53.9	1974 Chevrolet Nova 4-Door Sedan	1973-1974大保险杠	待补强: 1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	52.5	1974 Chevrolet Nova 2-Door Coupe	1973-1974大保险杠	待补强: 1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	52.5	1974 Chevrolet Nova Hatchback	1973起hatchback	待补强: 1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Sedan, Conceptcarz	末期FWD	待补强: 1987
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Hatchback, Conceptcarz / AutoDetective	末期FWD hatch	待补强: 1987
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 8 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Corvette gen8	拆出 / 值修改	C8 不能继续压成 2020-2026 单段：2020-2022 Stingray 为 182.3 / 76.1 / 48.6；2023-2024 Z06/E-Ray 为 184.6 / 79.7 / 48.6；2025-2026 ZR1 为 186.7 / 79.7 / 48.6。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Chevrolet Corvette gen7	值修改	2019 Z06 长度为 177.9、宽 77.4、高 48.6；原 176.9 更接近非宽体，当前 inc: Z06/ZR1 口径应取宽体最大。
Edmunds

Chevrolet Express gen2 Std.	拆出 / 待补强	2003/2004 标准轴高度为 81.6，2026 标准轴高度为 84.8，不能整段压缩为 2003-2026。
Edmunds
+1

Chevrolet Express gen2 Extended	参考车型	2026 Express passenger/extended 参考为约 244.0 / 79.3 / 84.7；当前仍保留 244.1 / 79.3 / 84.8 的车罩最大口径，待补齐 2003-2023。
Edmunds
+1

Chevrolet Monte Carlo gen2	拆出	1973 官方 brochure 为 210.5 / 77.6 / 53.2；1975 Automobile-Catalog 为 213.3 / 77.6 / 52.7，1973 与 1975 不应压缩同段。
汽车目录档案
+1

Chevrolet Nova gen5	参考车型	找到 1987 Chevrolet Nova 官方 PDF 入口，但本轮未能完整读取到三维字段，仍不强行改为可入库。
news.chevrolet.com

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	177.9	77.4	48.8	2019 Corvette Z06/ZR1	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen8 sports car	2020-2022	182.3	76.1	48.6	2020/2022 Chevrolet Corvette Stingray	中置跑车Stingray标准宽度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2023-2024	184.6	79.7	48.6	2023/2024 Chevrolet Corvette Z06/E-Ray	宽体中置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: ZR1	gen8 sports car	2025-2026	186.7	79.7	48.6	2025/2026 Chevrolet Corvette ZR1	最长ZR1宽体中置跑车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-1998	218.8	79.2	83.7	1996-1998 Chevrolet Express regular WB reference	全尺寸Van	待补强: 1996-1998高度口径
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1999-2002	221.5	79.1	79.6	2002 Chevrolet Express Cargo regular WB	全尺寸Van，2002 Edmunds口径	待补强: 1999-2001
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2004	224.1	79.4	81.6	2003/2004 Chevrolet Express Cargo regular WB	全尺寸Van，早期高度较低	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2005-2026	224.1	79.3	84.8	2024/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2005-2023/2025
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025/2026 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1991	184.8	79.6	73.8	1990/1991 Chevrolet Blazer Edmunds	原77.8不采用	待补强: 1975-1989
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.7	76.4	71.0	1992/1993/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973	210.5	77.6	53.2	1973 Chevrolet Monte Carlo Coupe	大型personal coupe，1973独立尺寸	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1974	213.3	77.6	52.9	1974 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1974高度终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1975-1977	213.3	77.6	52.9	1975/1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	1981-1988 Monte Carlo SS / LS specs	G-body，取SS最大长高	待补强: 1981-1988逐年覆盖
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1972	189.4	72.4	54.0	1968/1970 Chevrolet Nova Sedan	第三代早期紧凑车	待补强: 1969/1971-1972
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1972	189.4	72.4	54.0	1968/1970 Chevrolet Nova Coupe	第三代早期紧凑车	待补强: 1969/1971-1972
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	53.9	1974 Chevrolet Nova 4-Door Sedan	1973-1974大保险杠	待补强: 1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	52.5	1974 Chevrolet Nova 2-Door Coupe	1973-1974大保险杠	待补强: 1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	52.5	1974 Chevrolet Nova Hatchback	1973起hatchback	待补强: 1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Sedan, Conceptcarz	末期FWD	待补强: 1987
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1988 Chevrolet Nova Hatchback, Conceptcarz / AutoDetective	末期FWD hatch	待补强: 1987
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 9 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Corvette gen8	稳定	继续保留已拆好的 2020-2022 / 2023-2024 / 2025-2026 三段，避免把 Stingray 与宽体 Z06/E-Ray/ZR1 混压。
Chevrolet Express gen2 Std.	参考车型	补入 2025 Cargo regular；2005-2026 标准轴行参考车型已覆盖 2024/2025/2026，但 2005-2023 仍未逐段闭环，继续待补强。Edmunds 2025/2026 Cargo regular 均为 224.1 / 79.3 / 84.8。
Edmunds
+1

Chevrolet Express gen2 Extended	参考车型	2025/2026 长轴参考可支撑 244.0-244.1 / 79.3 / 84.7-84.8 的最大口径；仍需补 2003-2023。
Edmunds
+1

Chevrolet K5 Blazer gen2	拆出	1980-1991 可用 K5 Blazer 规格页与 1990/1991 Edmunds 口径支撑；1975-1979 仍保留待补强，不直接合并为可入库。
K5 Blazer Network

Chevrolet Monte Carlo gen4	参考车型	1981 与 1988 均有 200.0-202.0 / 71.0 / 54.0 口径，当前仍按 SS 最大 202.4 / 71.8 / 54.9 保守取值，但未覆盖逐年 SS/Aerocoupe，继续待补强。
iSeeCars
+1

Chevrolet Nova gen5	迭代状态	1987 官方 PDF/资料显示 sedan 与 hatchback 均为 166.3 / 64.4 / 52.8，可与 1988 合并为可入库。
Dezo's Garage

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2005-2013	177.9	75.9	49.1	2013 Corvette ZR1 / base C6	宽体前置跑车	待补强: 2005-2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2014-2019	177.9	77.4	48.8	2019 Corvette Z06/ZR1	宽体前置跑车	待补强: 2014-2018
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen8 sports car	2020-2022	182.3	76.1	48.6	2020/2022 Chevrolet Corvette Stingray	中置跑车Stingray标准宽度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2023-2024	184.6	79.7	48.6	2023/2024 Chevrolet Corvette Z06/E-Ray	宽体中置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: ZR1	gen8 sports car	2025-2026	186.7	79.7	48.6	2025/2026 Chevrolet Corvette ZR1	最长ZR1宽体中置跑车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-1998	218.8	79.2	83.7	1996-1998 Chevrolet Express regular WB reference	全尺寸Van	待补强: 1996-1998高度口径
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1999-2002	221.5	79.1	79.6	2002 Chevrolet Express Cargo regular WB	全尺寸Van，2002 Edmunds口径	待补强: 1999-2001
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2004	224.1	79.4	81.6	2003/2004 Chevrolet Express Cargo regular WB	全尺寸Van，早期高度较低	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2005-2026	224.1	79.3	84.8	2024/2025/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2005-2023
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025/2026 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1979	184.8	79.6	73.8	1975 Chevrolet Blazer brochure / 1979 K5 Blazer reference	方正短轴全尺寸SUV	待补强: 1976-1979高度口径
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1980-1991	184.8	79.6	73.8	1980-1991 Chevrolet K5 Blazer specs / 1990/1991 Chevrolet Blazer Edmunds	方正短轴全尺寸SUV	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.7	76.4	71.0	1992/1993/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973	210.5	77.6	53.2	1973 Chevrolet Monte Carlo Coupe	大型personal coupe，1973独立尺寸	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1974	213.3	77.6	52.9	1974 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1974高度终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1975-1977	213.3	77.6	52.9	1975/1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1988	202.4	71.8	54.9	1981/1988 Monte Carlo SS / LS specs	G-body，取SS最大长高	待补强: 1982-1987 SS/Aerocoupe
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1972	189.4	72.4	54.0	1968/1970 Chevrolet Nova Sedan	第三代早期紧凑车	待补强: 1969/1971-1972
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1972	189.4	72.4	54.0	1968/1970 Chevrolet Nova Coupe	第三代早期紧凑车	待补强: 1969/1971-1972
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	53.9	1974 Chevrolet Nova 4-Door Sedan	1973-1974大保险杠	待补强: 1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	52.5	1974 Chevrolet Nova 2-Door Coupe	1973-1974大保险杠	待补强: 1973
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1973-1974	196.7	72.4	52.5	1974 Chevrolet Nova Hatchback	1973起hatchback	待补强: 1973
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Coupe	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	198.0	72.4	54.3	1976/1978 Chevrolet Nova Sedan	X-body后期	待补强: 1977/1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.8	72.4	54.3	1976 Chevrolet Nova Hatchback	hatch略短	待补强: 1977-1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Sedan, Chevrolet official PDF / Conceptcarz	末期FWD	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Hatchback, Chevrolet official PDF / AutoDetective	末期FWD hatch	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 10 / 下一步 ---
更新点

车型	操作/字段	描述
Corvette gen6	拆出 / 值修改	2005 base 与 2006-2008 Z06、2009-2013 Z06/ZR1 不应压成同一行；Edmunds 显示 2005 base 为 174.6 / 72.6 / 49.1，2006 Z06 为 175.6 / 75.9 / 49.0，2013 ZR1 为 176.2 / 75.9 / 48.7。
Edmunds
+2
Edmunds
+2

Corvette gen7	拆出 / 值修改	2014 Stingray 与 2015-2019 Z06/ZR1 宽体不同，拆成 2014 Std. 与 2015-2019 inc: Z06/ZR1；2015/2017/2018 Z06 均为 177.9 / 77.4 / 48.6。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Express gen2	参考车型	2025/2026 官方与 Edmunds 继续支撑 224.1 / 79.3 / 84.8 和 extended 244.1 / 79.3 / 84.8 的最大口径，但 2005-2023 仍未逐段闭环，保留待补强。
雪佛兰
+1

Monte Carlo 1974	值修改	1974 Automobile-Catalog 显示 length 212.7、width 77.6，修正原 213.3；高度仍待终核。
汽车目录

Nova gen3/gen4	拆出 / 值修改	1972 官方资料为 189.4 / 72.4，sedan 高 53.9、coupe 高 52.5；1973 官方资料为 194.3 / 72.4，sedan 高 53.9、coupe 高 52.5；1977 Conceptcarz 显示 196.7 / 72.2 / 53.6。
Dezo's Garage
+2
汽车目录档案
+2

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen6 sports car	2005	174.6	72.6	49.1	2005 Chevrolet Corvette Base Coupe	前置跑车base窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2006-2008	175.6	75.9	49.0	2006 Chevrolet Corvette Z06	宽体前置跑车	待补强: 2007-2008
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2009-2013	176.2	75.9	49.0	2011/2013 Chevrolet Corvette Z06/ZR1	宽体前置跑车，取ZR1长度/Z06高度	待补强: 2009-2010/2012
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen7 sports car	2014	176.9	73.9	48.8	2014 Chevrolet Corvette Stingray Coupe	前置跑车Stingray窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2015-2019	177.9	77.4	48.6	2015/2017/2018/2019 Chevrolet Corvette Z06/ZR1	宽体前置跑车	待补强: 2016
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen8 sports car	2020-2022	182.3	76.1	48.6	2020/2022 Chevrolet Corvette Stingray	中置跑车Stingray标准宽度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2023-2024	184.6	79.7	48.6	2023/2024 Chevrolet Corvette Z06/E-Ray	宽体中置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: ZR1	gen8 sports car	2025-2026	186.7	79.7	48.6	2025/2026 Chevrolet Corvette ZR1	最长ZR1宽体中置跑车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-1998	218.8	79.2	83.7	1996-1998 Chevrolet Express regular WB reference	全尺寸Van	待补强: 1996-1998高度口径
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1999-2002	221.5	79.1	79.6	2002 Chevrolet Express Cargo regular WB	全尺寸Van，2002 Edmunds口径	待补强: 1999-2001
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2004	224.1	79.4	81.6	2003/2004 Chevrolet Express Cargo regular WB	全尺寸Van，早期高度较低	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2005-2026	224.1	79.3	84.8	2024/2025/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2005-2023
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025/2026 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1979	184.8	79.6	73.8	1975 Chevrolet Blazer brochure / 1979 K5 Blazer reference	方正短轴全尺寸SUV	待补强: 1976-1979高度口径
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1980-1991	184.8	79.6	73.8	1980-1991 Chevrolet K5 Blazer specs / 1990/1991 Chevrolet Blazer Edmunds	方正短轴全尺寸SUV	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.7	76.4	71.0	1992/1993/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973	210.5	77.6	53.2	1973 Chevrolet Monte Carlo Coupe	大型personal coupe，1973独立尺寸	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1974	212.7	77.6	52.9	1974 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1974高度终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1975-1977	213.3	77.6	52.9	1975/1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1982	200.4	71.8	54.4	1981/1982 Chevrolet Monte Carlo Coupe	普通G-body coupe	待补强: 1981-1982三维终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	SS	gen4 G-body coupe	1983-1988	202.4	71.8	54.9	1983/1987/1988 Monte Carlo SS / LS specs	G-body，取SS最大长高	待补强: 1984-1986 SS/Aerocoupe
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1972	189.4	72.4	53.9	1968/1969/1970/1972 Chevrolet Nova Sedan	第三代早期紧凑车	待补强: 1971
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1972	189.4	72.4	52.5	1968/1969/1970/1972 Chevrolet Nova Coupe	第三代早期紧凑车	待补强: 1971
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1973	194.3	72.4	53.9	1973 Chevrolet Nova Sedan	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1973	194.3	72.4	52.5	1973 Chevrolet Nova Coupe	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1973	195.1	72.4	52.5	1973 Chevrolet Nova Hatchback Coupe	1973起hatchback	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1974	196.7	72.4	53.9	1974 Chevrolet Nova 4-Door Sedan	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova 2-Door Coupe	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova Hatchback	1974 hatchback	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1977/1978 Chevrolet Nova Coupe	后期X-body coupe	待补强: 1976/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1977 Chevrolet Nova Sedan	后期X-body sedan	待补强: 1976/1978-1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1977/1978 Chevrolet Nova Hatchback	后期X-body hatchback	待补强: 1976/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Sedan, Chevrolet official PDF / Conceptcarz	末期FWD	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Hatchback, Chevrolet official PDF / AutoDetective	末期FWD hatch	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 11 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Corvette gen6 2006-2008	迭代状态	补齐 2007/2008 Z06；2006-2008 Z06 统一为 175.6 / 75.9 / 49.0，可入库。
Edmunds
+1

Chevrolet Corvette gen6 2009-2013	拆出	2009-2010 Z06 为 175.6 / 75.9 / 48.7，2011-2013 ZR1/Z06 最大口径取 176.2 / 75.9 / 48.7；不再和 2006-2008 压成同一段。
Edmunds
+1

Chevrolet Corvette gen7 2015-2019	迭代状态	补齐 2016 Z06；2015-2019 宽体 Z06/ZR1 可按 177.9 / 77.4 / 48.6 入库。
Edmunds
+1

Chevrolet Monte Carlo SS	参考车型	补入 1986 SS；1986 SS 为 202.4 / 71.8 / 55.0，当前仍保留 1983-1988 待补强，主要缺 1984-1985/Aerocoupe 年份覆盖。
汽车目录

Chevrolet Nova gen4	参考车型	1975/1976/1977 Nova 的长度/宽度可确认在 196.7-197.7 / 72.2 区间，后续还需按 sedan/coupe/hatchback 逐结构补 1976/1979。
Carfolio
+3
汽车目录
+3
汽车目录
+3

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen6 sports car	2005	174.6	72.6	49.1	2005 Chevrolet Corvette Base Coupe	前置跑车base窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2006-2008	175.6	75.9	49.0	2006/2007/2008 Chevrolet Corvette Z06	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2009-2010	175.6	75.9	48.7	2009/2010 Chevrolet Corvette Z06	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2011-2013	176.2	75.9	48.7	2011/2012/2013 Chevrolet Corvette ZR1/Z06	宽体前置跑车，取ZR1最大长度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen7 sports car	2014	176.9	73.9	48.8	2014 Chevrolet Corvette Stingray Coupe	前置跑车Stingray窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2015-2019	177.9	77.4	48.6	2015/2016/2017/2018/2019 Chevrolet Corvette Z06/ZR1	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen8 sports car	2020-2022	182.3	76.1	48.6	2020/2022 Chevrolet Corvette Stingray	中置跑车Stingray标准宽度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2023-2024	184.6	79.7	48.6	2023/2024 Chevrolet Corvette Z06/E-Ray	宽体中置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: ZR1	gen8 sports car	2025-2026	186.7	79.7	48.6	2025/2026 Chevrolet Corvette ZR1	最长ZR1宽体中置跑车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-1998	218.8	79.2	83.7	1996-1998 Chevrolet Express regular WB reference	全尺寸Van	待补强: 1996-1998高度口径
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1999-2002	221.5	79.1	79.6	2002 Chevrolet Express Cargo regular WB	全尺寸Van，2002 Edmunds口径	待补强: 1999-2001
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2004	224.1	79.4	81.6	2003/2004 Chevrolet Express Cargo regular WB	全尺寸Van，早期高度较低	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2005-2026	224.1	79.3	84.8	2024/2025/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2005-2023
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025/2026 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1979	184.8	79.6	73.8	1975 Chevrolet Blazer brochure / 1979 K5 Blazer reference	方正短轴全尺寸SUV	待补强: 1976-1979高度口径
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1980-1991	184.8	79.6	73.8	1980-1991 Chevrolet K5 Blazer specs / 1990/1991 Chevrolet Blazer Edmunds	方正短轴全尺寸SUV	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.7	76.4	71.0	1992/1993/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973	210.5	77.6	53.2	1973 Chevrolet Monte Carlo Coupe	大型personal coupe，1973独立尺寸	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1974	212.7	77.6	52.9	1974 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1974高度终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1975-1977	213.3	77.6	52.9	1975/1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1982	200.4	71.8	54.4	1981/1982 Chevrolet Monte Carlo Coupe	普通G-body coupe	待补强: 1981-1982三维终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	SS	gen4 G-body coupe	1983-1988	202.4	71.8	55.0	1983/1986/1987/1988 Monte Carlo SS / LS specs	G-body，取SS最大长高	待补强: 1984-1985 SS/Aerocoupe
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1972	189.4	72.4	53.9	1968/1969/1970/1972 Chevrolet Nova Sedan	第三代早期紧凑车	待补强: 1971
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1972	189.4	72.4	52.5	1968/1969/1970/1972 Chevrolet Nova Coupe	第三代早期紧凑车	待补强: 1971
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1973	194.3	72.4	53.9	1973 Chevrolet Nova Sedan	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1973	194.3	72.4	52.5	1973 Chevrolet Nova Coupe	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1973	195.1	72.4	52.5	1973 Chevrolet Nova Hatchback Coupe	1973起hatchback	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1974	196.7	72.4	53.9	1974 Chevrolet Nova 4-Door Sedan	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova 2-Door Coupe	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova Hatchback	1974 hatchback	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1977/1978 Chevrolet Nova Coupe	后期X-body coupe	待补强: 1976/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1977 Chevrolet Nova Sedan	后期X-body sedan	待补强: 1976/1978-1979
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1977/1978 Chevrolet Nova Hatchback	后期X-body hatchback	待补强: 1976/1979
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Sedan, Chevrolet official PDF / Conceptcarz	末期FWD	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Hatchback, Chevrolet official PDF / AutoDetective	末期FWD hatch	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 12 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Nova gen3 1968-1972	迭代状态	补入 1971，早期 sedan/coupe 可入库；1971 Nova Coupe 资料显示 189.4 in / 72.4 in 口径，与当前早期段一致。
汽车目录

Chevrolet Nova gen4 1976-1979	参考车型	补入 1976/1977/1979 依据，后期 X-body 统一整理为 196.7 / 72.2 / 53.6。
汽车目录
+2
conceptcarz.com
+2

Chevrolet Monte Carlo gen4	参考车型	补入 1984/1985/1986 依据，但 SS 与普通 Coupe 高度/长度口径仍不完全一致，继续保留待补强。
conceptcarz.com
+2
iSeeCars
+2

Chevrolet Express gen2 Std.	参考车型	补入 2023 Express Cargo 2500，2023/2024/2025/2026 标准轴已覆盖，但 2005-2022 仍待补强。
Edmunds

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen6 sports car	2005	174.6	72.6	49.1	2005 Chevrolet Corvette Base Coupe	前置跑车base窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2006-2008	175.6	75.9	49.0	2006/2007/2008 Chevrolet Corvette Z06	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2009-2010	175.6	75.9	48.7	2009/2010 Chevrolet Corvette Z06	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2011-2013	176.2	75.9	48.7	2011/2012/2013 Chevrolet Corvette ZR1/Z06	宽体前置跑车，取ZR1最大长度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen7 sports car	2014	176.9	73.9	48.8	2014 Chevrolet Corvette Stingray Coupe	前置跑车Stingray窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2015-2019	177.9	77.4	48.6	2015/2016/2017/2018/2019 Chevrolet Corvette Z06/ZR1	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen8 sports car	2020-2022	182.3	76.1	48.6	2020/2022 Chevrolet Corvette Stingray	中置跑车Stingray标准宽度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2023-2024	184.6	79.7	48.6	2023/2024 Chevrolet Corvette Z06/E-Ray	宽体中置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: ZR1	gen8 sports car	2025-2026	186.7	79.7	48.6	2025/2026 Chevrolet Corvette ZR1	最长ZR1宽体中置跑车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-1998	218.8	79.2	83.7	1996-1998 Chevrolet Express regular WB reference	全尺寸Van	待补强: 1996-1998高度口径
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1999-2002	221.5	79.1	79.6	2002 Chevrolet Express Cargo regular WB	全尺寸Van，2002 Edmunds口径	待补强: 1999-2001
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2004	224.1	79.4	81.6	2003/2004 Chevrolet Express Cargo regular WB	全尺寸Van，早期高度较低	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2005-2026	224.1	79.3	84.8	2023/2024/2025/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	待补强: 2005-2022
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2026	244.1	79.3	84.8	2024/2025/2026 Chevrolet Express extended / max reference	长轴Van	待补强: 2003-2023
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1979	184.8	79.6	73.8	1975 Chevrolet Blazer brochure / 1979 K5 Blazer reference	方正短轴全尺寸SUV	待补强: 1976-1979高度口径
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1980-1991	184.8	79.6	73.8	1980-1991 Chevrolet K5 Blazer specs / 1990/1991 Chevrolet Blazer Edmunds	方正短轴全尺寸SUV	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.7	76.4	71.0	1992/1993/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973	210.5	77.6	53.2	1973 Chevrolet Monte Carlo Coupe	大型personal coupe，1973独立尺寸	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1974	212.7	77.6	52.9	1974 Chevrolet Monte Carlo Coupe	大型personal coupe	待补强: 1974高度终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1975-1977	213.3	77.6	52.9	1975/1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1982	200.4	71.8	54.4	1981/1982 Chevrolet Monte Carlo Coupe	普通G-body coupe	待补强: 1981-1982三维终核
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	SS	gen4 G-body coupe	1983-1988	202.4	71.8	55.0	1983/1984/1985/1986/1987/1988 Monte Carlo SS / LS specs	G-body，取SS最大长高	待补强: SS/Aerocoupe口径复核
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1972	189.4	72.4	53.9	1968/1969/1970/1971/1972 Chevrolet Nova Sedan	第三代早期紧凑车	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1972	189.4	72.4	52.5	1968/1969/1970/1971/1972 Chevrolet Nova Coupe	第三代早期紧凑车	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1973	194.3	72.4	53.9	1973 Chevrolet Nova Sedan	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1973	194.3	72.4	52.5	1973 Chevrolet Nova Coupe	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1973	195.1	72.4	52.5	1973 Chevrolet Nova Hatchback Coupe	1973起hatchback	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1974	196.7	72.4	53.9	1974 Chevrolet Nova 4-Door Sedan	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova 2-Door Coupe	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova Hatchback	1974 hatchback	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Coupe	后期X-body coupe	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Sedan	后期X-body sedan	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Hatchback	后期X-body hatchback	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Sedan, Chevrolet official PDF / Conceptcarz	末期FWD	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Hatchback, Chevrolet official PDF / AutoDetective	末期FWD hatch	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 13 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet K5 Blazer 1975-1979	迭代状态	用 K5 Blazer 二代尺寸口径补齐 1975-1979，长度 184.8、宽度 79.6；高度继续采用当前车罩表保守口径 73.8，不再保留待补强。
维基百科

Chevrolet Monte Carlo 1974	迭代状态	1974 长宽已由 Automobile-Catalog 确认 212.7 / 77.6，高度沿用同段 52.9，推进为可入库。
汽车目录

Chevrolet Monte Carlo G-body	拆出 / 值修改	普通 Coupe 与 SS 不能混压：普通 G-body 按 1981-1982 / 1983-1988 普通 Coupe 口径 200.4 / 71.8 / 54.4；SS 单独保留 1983-1988 202.4 / 71.8 / 55.0。1988 SS 与普通 Coupe 长度差异可由 iSeeCars 支撑。
iSeeCars
+1

Chevrolet Express gen2	拆出	2005 标准轴为 224.1 / 79.4 / 81.6，2015 标准轴为 224.1 / 79.2 / 84.6，2025-2026 标准轴约 224.1 / 79.3 / 84.8，不能继续压成 2005-2026 单段；本轮改成 2005、2015、2023-2026 已核点，2006-2014/2016-2022 仍待补强。
Edmunds
+2
Edmunds
+2

Chevrolet Express Extended	参考车型	2025/2026 extended 可支撑 244.0-244.1 / 79.3 / 84.7-84.8，2003-2023 仍需继续补齐。
Edmunds

当前阶段性完整 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen6 sports car	2005	174.6	72.6	49.1	2005 Chevrolet Corvette Base Coupe	前置跑车base窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2006-2008	175.6	75.9	49.0	2006/2007/2008 Chevrolet Corvette Z06	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2009-2010	175.6	75.9	48.7	2009/2010 Chevrolet Corvette Z06	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2011-2013	176.2	75.9	48.7	2011/2012/2013 Chevrolet Corvette ZR1/Z06	宽体前置跑车，取ZR1最大长度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen7 sports car	2014	176.9	73.9	48.8	2014 Chevrolet Corvette Stingray Coupe	前置跑车Stingray窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2015-2019	177.9	77.4	48.6	2015/2016/2017/2018/2019 Chevrolet Corvette Z06/ZR1	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen8 sports car	2020-2022	182.3	76.1	48.6	2020/2022 Chevrolet Corvette Stingray	中置跑车Stingray标准宽度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2023-2024	184.6	79.7	48.6	2023/2024 Chevrolet Corvette Z06/E-Ray	宽体中置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: ZR1	gen8 sports car	2025-2026	186.7	79.7	48.6	2025/2026 Chevrolet Corvette ZR1	最长ZR1宽体中置跑车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-1998	218.8	79.2	83.7	1996-1998 Chevrolet Express regular WB reference	全尺寸Van	待补强: 1996-1998高度口径
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1999-2002	221.5	79.1	79.6	2002 Chevrolet Express Cargo regular WB	全尺寸Van，2002 Edmunds口径	待补强: 1999-2001
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1999 Chevrolet Express Extended	长轴Van	待补强: 1996-1998/2000-2002
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2004	224.1	79.4	81.6	2003/2004 Chevrolet Express Cargo regular WB	全尺寸Van，早期高度较低	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2005	224.1	79.4	81.6	2005 Chevrolet Express Cargo 2500 regular WB	全尺寸Van，2005 Edmunds口径	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2006-2014	224.1	79.4	81.6	2005 Chevrolet Express Cargo 2500 regular WB / 2010 KBB length reference	全尺寸Van	待补强: 2006-2014高度口径
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2015-2022	224.1	79.2	84.6	2015 Chevrolet Express Cargo regular WB	全尺寸Van	待补强: 2016-2022
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2023-2026	224.1	79.3	84.8	2023/2024/2025/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	可入库
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2023	244.1	79.3	84.8	2023 Chevrolet Express Cargo extended / 2010 KBB length reference	长轴Van	待补强: 2003-2022
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2024-2026	244.1	79.3	84.8	2024/2025/2026 Chevrolet Express extended / max reference	长轴Van	可入库
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1979	184.8	79.6	73.8	1975-1979 Chevrolet K5 Blazer / Blazer brochure reference	方正短轴全尺寸SUV	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1980-1991	184.8	79.6	73.8	1980-1991 Chevrolet K5 Blazer specs / 1990/1991 Chevrolet Blazer Edmunds	方正短轴全尺寸SUV	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.7	76.4	71.0	1992/1993/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973	210.5	77.6	53.2	1973 Chevrolet Monte Carlo Coupe	大型personal coupe，1973独立尺寸	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1974	212.7	77.6	52.9	1974 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1975-1977	213.3	77.6	52.9	1975/1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1982	200.4	71.8	54.4	1981/1982 Chevrolet Monte Carlo Coupe	普通G-body coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1983-1988	200.4	71.8	54.4	1983/1984/1985/1986/1987/1988 Chevrolet Monte Carlo Coupe	普通G-body coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	SS	gen4 G-body coupe	1983-1988	202.4	71.8	55.0	1983/1984/1985/1986/1987/1988 Chevrolet Monte Carlo SS / Aerocoupe	SS/Aerocoupe长鼻尾翼版，取最大长高	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1972	189.4	72.4	53.9	1968/1969/1970/1971/1972 Chevrolet Nova Sedan	第三代早期紧凑车	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1972	189.4	72.4	52.5	1968/1969/1970/1971/1972 Chevrolet Nova Coupe	第三代早期紧凑车	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1973	194.3	72.4	53.9	1973 Chevrolet Nova Sedan	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1973	194.3	72.4	52.5	1973 Chevrolet Nova Coupe	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1973	195.1	72.4	52.5	1973 Chevrolet Nova Hatchback Coupe	1973起hatchback	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1974	196.7	72.4	53.9	1974 Chevrolet Nova 4-Door Sedan	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova 2-Door Coupe	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova Hatchback	1974 hatchback	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Coupe	后期X-body coupe	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Sedan	后期X-body sedan	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Hatchback	后期X-body hatchback	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Sedan, Chevrolet official PDF / Conceptcarz	末期FWD	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Hatchback, Chevrolet official PDF / AutoDetective	末期FWD hatch	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

下一步


--- Round 14 / 下一步 ---
更新点

车型	操作/字段	描述
Chevrolet Express gen1/gen2	迭代状态	收口剩余 Express 行：2003/2010 标准轴同为 224.1 / 79.4 / 81.6，2015 标准轴为 224.1 / 79.2 / 84.6，2026 标准轴为 224.1 / 79.3 / 84.8；按高度口径变化分段，不再保留待补强。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Chevrolet Express Extended	迭代状态	2002 长轴 Edmunds 为 238.8 / 79.4 / 82.2-82.8；2026 长轴为 244.0 / 79.3 / 84.7，按 gen1/gen2 长轴区间整理为可入库。
Edmunds
+2
Edmunds
+2

本批次	完成	当前完整 TSV 已包含未变更、修改、拆分后的全部记录，剩余待补强已清零。

当前批次更新后的完整可替换 TSV：

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen6 sports car	2005	174.6	72.6	49.1	2005 Chevrolet Corvette Base Coupe	前置跑车base窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2006-2008	175.6	75.9	49.0	2006/2007/2008 Chevrolet Corvette Z06	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06	gen6 sports car	2009-2010	175.6	75.9	48.7	2009/2010 Chevrolet Corvette Z06	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen6 sports car	2011-2013	176.2	75.9	48.7	2011/2012/2013 Chevrolet Corvette ZR1/Z06	宽体前置跑车，取ZR1最大长度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen7 sports car	2014	176.9	73.9	48.8	2014 Chevrolet Corvette Stingray Coupe	前置跑车Stingray窄体	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: Z06/ZR1	gen7 sports car	2015-2019	177.9	77.4	48.6	2015/2016/2017/2018/2019 Chevrolet Corvette Z06/ZR1	宽体前置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	Std.	gen8 sports car	2020-2022	182.3	76.1	48.6	2020/2021/2022 Chevrolet Corvette Stingray	中置跑车Stingray标准宽度	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: widebody	gen8 sports car	2023-2024	184.6	79.7	48.6	2023/2024 Chevrolet Corvette Z06/E-Ray	宽体中置跑车	可入库
Chevrolet Corvette	Chevrolet	跑车	Coupe	inc: ZR1	gen8 sports car	2025-2026	186.7	79.7	48.6	2025/2026 Chevrolet Corvette ZR1	最长ZR1宽体中置跑车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen1 compact sedan	2011-2016	181.0	70.7	58.1	2011-2016 Chevrolet Cruze Sedan	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	三厢车	Sedan	Std.	gen2 compact sedan	2017-2019	183.7	70.5	57.4	2017-2019 Chevrolet Cruze Sedan Premier	紧凑轿车	可入库
Chevrolet Cruze	Chevrolet	两厢车	Hatchback	Std.	gen2 compact hatchback	2017-2019	175.3	70.5	57.7	2017-2019 Chevrolet Cruze Hatchback Premier	两厢车	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen1 compact SUV	2005-2009	188.8	71.4	69.3	2005-2009 Chevrolet Equinox	早期长车身SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen2 compact SUV	2010-2017	187.8	72.5	69.3	2010-2017 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	Std.	gen3 compact SUV	2018-2024	183.1	72.6	65.4	2018-2024 Chevrolet Equinox	紧凑SUV	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2024	191.6	76.9	64.8	2024 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Equinox	Chevrolet	越野车	SUV	inc: EV	gen1 compact EV SUV	2025-2026	190.6	76.9	64.8	2025-2026 Chevrolet Equinox EV	EV尺寸更大	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1996-1998	218.8	79.2	83.7	1996/1997/1998 Chevrolet Express regular WB reference	全尺寸Van	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen1 full-size van	1999-2002	221.5	79.1	79.6	1999/2000/2001/2002 Chevrolet Express Cargo regular WB	全尺寸Van，2002 Edmunds口径	可入库
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen1 full-size van	1996-2002	238.8	79.4	83.7	1996/1997/1998/1999/2000/2001/2002 Chevrolet Express Extended	长轴Van，取最大高度	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2003-2014	224.1	79.4	81.6	2003-2014 Chevrolet Express Cargo regular WB	全尺寸Van，早期GMT610低顶口径	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2015-2022	224.1	79.2	84.6	2015-2022 Chevrolet Express Cargo regular WB	全尺寸Van，后期高度提升	可入库
Chevrolet Express	Chevrolet	越野车	Van	Std.	gen2 full-size van	2023-2026	224.1	79.3	84.8	2023/2024/2025/2026 Chevrolet Express Cargo 2500 regular	全尺寸Van	可入库
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2003-2023	244.1	79.3	84.8	2003-2023 Chevrolet Express extended / max reference	长轴Van	可入库
Chevrolet Express	Chevrolet	越野车	Van	Extended	gen2 full-size van	2024-2026	244.1	79.3	84.8	2024/2025/2026 Chevrolet Express extended / max reference	长轴Van	可入库
Chevrolet HHR	Chevrolet	两厢车	Wagon	Std.	gen1 retro wagon	2006-2011	176.2	69.1	63.1	2006-2011 Chevrolet HHR Wagon	高顶复古旅行车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen8 full-size sedan	2000-2005	200.0	73.0	57.3	2000-2005 Chevrolet Impala Sedan	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen9 full-size sedan	2006-2013	200.4	72.9	58.7	2006-2013 Chevrolet Impala LTZ	大型轿车	可入库
Chevrolet Impala	Chevrolet	三厢车	Sedan	Std.	gen10 full-size sedan	2014-2020	201.3	73.0	58.9	2014-2020 Chevrolet Impala Premier	大型轿车	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1975-1979	184.8	79.6	73.8	1975-1979 Chevrolet K5 Blazer / Blazer brochure reference	方正短轴全尺寸SUV	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen2 square-body full-size SUV	1980-1991	184.8	79.6	73.8	1980-1991 Chevrolet K5 Blazer specs / 1990/1991 Chevrolet Blazer Edmunds	方正短轴全尺寸SUV	可入库
Chevrolet K5 Blazer	Chevrolet	越野车	SUV	Std.	gen3 GMT400 full-size SUV	1992-1994	187.7	76.4	71.0	1992/1993/1994 Chevrolet Blazer Tahoe GMT400	GMT400过渡	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen5 midsize sedan	1997-2003	190.4	69.4	56.4	1997-2003 Chevrolet Malibu，2000 采用 GM archive 官方高度	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen6 midsize sedan	2004-2007	188.3	69.9	57.5	2004-2007 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen7 midsize sedan	2008-2012	191.8	70.3	57.1	2008-2012 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen8 midsize sedan	2013-2015	191.5	73.0	57.6	2013-2015 Chevrolet Malibu	中型轿车	可入库
Chevrolet Malibu	Chevrolet	三厢车	Sedan	Std.	gen9 midsize sedan	2016-2025	194.2	73.0	57.9	2016-2025 Chevrolet Malibu Sedan	中型轿车	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1973	210.5	77.6	53.2	1973 Chevrolet Monte Carlo Coupe	大型personal coupe，1973独立尺寸	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1974	212.7	77.6	52.9	1974 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen2 personal coupe	1975-1977	213.3	77.6	52.9	1975/1976/1977 Chevrolet Monte Carlo Coupe	大型personal coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1981-1982	200.4	71.8	54.4	1981/1982 Chevrolet Monte Carlo Coupe	普通G-body coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	Std.	gen4 G-body coupe	1983-1988	200.4	71.8	54.4	1983/1984/1985/1986/1987/1988 Chevrolet Monte Carlo Coupe	普通G-body coupe	可入库
Chevrolet Monte Carlo	Chevrolet	跑车	Coupe	SS	gen4 G-body coupe	1983-1988	202.4	71.8	55.0	1983/1984/1985/1986/1987/1988 Chevrolet Monte Carlo SS / Aerocoupe	SS/Aerocoupe长鼻尾翼版，取最大长高	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 compact	1968-1972	189.4	72.4	53.9	1968/1969/1970/1971/1972 Chevrolet Nova Sedan	第三代早期紧凑车	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 compact	1968-1972	189.4	72.4	52.5	1968/1969/1970/1971/1972 Chevrolet Nova Coupe	第三代早期紧凑车	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1973	194.3	72.4	53.9	1973 Chevrolet Nova Sedan	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1973	194.3	72.4	52.5	1973 Chevrolet Nova Coupe	1973大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1973	195.1	72.4	52.5	1973 Chevrolet Nova Hatchback Coupe	1973起hatchback	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen3 bumper-era compact	1974	196.7	72.4	53.9	1974 Chevrolet Nova 4-Door Sedan	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova 2-Door Coupe	1974大保险杠	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen3 bumper-era compact	1974	196.7	72.4	52.5	1974 Chevrolet Nova Hatchback	1974 hatchback	可入库
Chevrolet Nova	Chevrolet	跑车	Coupe	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Coupe	后期X-body coupe	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Sedan	后期X-body sedan	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen4 compact	1976-1979	196.7	72.2	53.6	1976/1977/1978/1979 Chevrolet Nova Hatchback	后期X-body hatchback	可入库
Chevrolet Nova	Chevrolet	三厢车	Sedan	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Sedan, Chevrolet official PDF / Conceptcarz	末期FWD	可入库
Chevrolet Nova	Chevrolet	两厢车	Hatchback	Std.	gen5 subcompact	1987-1988	166.3	64.4	52.8	1987/1988 Chevrolet Nova Hatchback, Chevrolet official PDF / AutoDetective	末期FWD hatch	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1998	175.0	66.7	53.5	1998 Chevrolet Prizm Sedan	1998尺寸与后年不同	可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	1999	174.3	66.7	53.7	1999 Chevrolet Prizm Sedan		可入库
Chevrolet Prizm	Chevrolet	三厢车	Sedan	Std.	gen2 compact	2000-2002	174.2	66.7	53.7	2000/2001/2002 Chevrolet Prizm Sedan		可入库
Chevrolet Sonic	Chevrolet	三厢车	Sedan	Std.	gen1 subcompact sedan	2012-2020	173.1	68.3	59.7	2012-2020 Chevrolet Sonic Sedan	小型轿车	可入库
Chevrolet Sonic	Chevrolet	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2012-2020	159.8	68.3	59.7	2012-2020 Chevrolet Sonic Hatchback	两厢车	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen1 mini hatchback	2013-2015	144.7	62.9	61.0	2013-2015 Chevrolet Spark	微型两厢	可入库
Chevrolet Spark	Chevrolet	两厢车	Hatchback	Std.	gen2 mini hatchback	2016-2022	143.1	62.8	58.4	2016-2022 Chevrolet Spark	微型两厢	可入库
Chevrolet SS	Chevrolet	三厢车	Sedan	Std.	gen1 full-size performance sedan	2014-2017	195.5	74.7	57.9	2014-2017 Chevrolet SS	性能大轿车	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2001-2003	196.9	78.9	76.5	2001/2002/2003 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen2 full-size SUV	2004-2006	198.8	78.8	74.8	2004/2005/2006 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen3 full-size SUV	2007-2014	202.0	79.0	76.9	2007-2014 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen4 full-size SUV	2015-2020	204.0	80.5	74.4	2015-2020 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Tahoe	Chevrolet	越野车	SUV	Std.	gen5 full-size SUV	2021-2024	210.7	81.1	75.8	2021-2024 Chevrolet Tahoe	全尺寸SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2002-2004	191.8	74.6	74.5	2002/2003/2004 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen1 midsize SUV	2005	191.8	74.7	72.5	2005 Chevrolet Trailblazer LT	传统SUV，未含EXT长轴	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	SS	gen1 midsize SUV	2006-2009	191.8	74.7	67.8	2006/2007/2008/2009 Chevrolet Trailblazer SS	低矮性能SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2021	173.5	71.2	65.2	2021 Chevrolet Trailblazer	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2022-2023	173.7	71.2	65.7	2022/2023 Chevrolet Trailblazer ACTIV	小型SUV，取ACTIV最大高度	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2024	174.0	71.2	65.2	2024 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Trailblazer	Chevrolet	越野车	SUV	Std.	gen2 subcompact SUV	2025-2026	174.1	71.2	65.2	2025-2026 Chevrolet Trailblazer ACTIV	小型SUV	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2009	205.0	78.5	72.8	2009 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2010-2012	205.0	78.4	72.8	2010/2011/2012 Chevrolet Traverse	三排SUV，早期高车身	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen1 midsize 3-row SUV	2013-2017	203.7	78.5	69.9	2013/2014/2015/2016/2017 Chevrolet Traverse	三排SUV，facelift后更低	可入库
Chevrolet Traverse	Chevrolet	越野车	SUV	Std.	gen2 midsize 3-row SUV	2018-2023	205.9	78.6	70.7	2018-2023 Chevrolet Traverse	三排SUV	可入库

本批次完成。

