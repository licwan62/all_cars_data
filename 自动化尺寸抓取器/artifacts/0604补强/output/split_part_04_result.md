# 文件名：split_part_04.tsv


--- Round 1 / 首次发送 ---
更新点
车型	操作	描述
BMW 6 Series	补强	gen2 Coupe 参考车型年份压缩为 2004-2010；补出 Convertible；新增缺失 gen1 E24 占位。Edmunds 可核到 2007/2009/2010 Coupe 同为 190.2×73.0×54.1。
Edmunds
+2
Edmunds
+2

BMW 6 Series	补强	gen3 Gran Coupe / Convertible / Coupe 结构拆开；Gran Coupe 2017 为 197.1×74.6×54.8，Convertible 2017 为 192.6×74.6×53.7。
Edmunds
+1

BMW 7 Series	新增占位	当前文件只给 gen7，按代际完整性要求新增 gen1-gen6 待终核占位；gen7 2026 Edmunds 为 212.2×76.8×60.8。
Edmunds

BMW X1 / X2 / X3 / X4	补强	X1/X2/X3/X4 新款尺寸已用 2026/2025 Edmunds 高点更新或确认；X2 M35i 长度 179.8，X4 M40i 宽度高点 76.3。
Edmunds
+3
Edmunds
+3
Edmunds
+3

BMW X5	新增占位	原表缺 gen1、gen4，先新增待终核占位，下一轮优先补齐。
当前批次进度
状态	内容
🟢 已推进	BMW 6 Series / 7 Series / 8 Series / X1 / X2 / X3 / X4 / X5 已统一到新字段结构
🟡 待补强	BMW 7 Series gen1-gen6、BMW 8 Series gen1、BMW X5 gen1/gen4、BMW 6 Series gen1 和 gen3 Coupe/Convertible 全年覆盖仍需继续核对
🔴 未完成原因	仍有新增占位行与部分年份段未完成全量参考车型覆盖
本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989						E24 Coupe	待终核: 缺失 gen1 全量数据/年份范围/尺寸
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	软顶GT	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.9	2012-2019 BMW 6 Series Coupe, Edmunds	低矮GT Coupe	待终核: 2012-2016/2018-2019
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2018			192.6	74.6	53.7	2012-2018 BMW 6 Series Convertible, Edmunds	软顶GT	待终核: 2012-2016/2018
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 gran coupe	2013-2019			197.1	74.6	54.8	2013-2019 BMW 6 Series Gran Coupe, Edmunds	四门轿跑	待终核: 2013-2016/2018-2019
BMW 6 Series	BMW	两厢车		Hatchback	Std.	gen3 GT	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds	GT掀背	待终核: 2018
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen1 luxury sedan	1978-1986						E23 7 Series Sedan	待终核: 缺失 gen1 全量数据/尺寸
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen2 luxury sedan	1987-1994						E32 7 Series Sedan	待终核: 缺失 gen2 全量数据/尺寸
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen3 luxury sedan	1995-2001						E38 7 Series Sedan	待终核: 缺失 gen3 全量数据/尺寸
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen4 luxury sedan	2002-2008						E65/E66 7 Series Sedan	待终核: 缺失 gen4 全量数据/尺寸
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen5 luxury sedan	2009-2015						F01/F02 7 Series Sedan	待终核: 缺失 gen5 全量数据/尺寸
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen6 luxury sedan	2016-2022			206.2	74.8	58.2	2016-2022 BMW 7 Series Sedan, Edmunds	豪华轿车	待终核: 2017-2022
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen7 luxury sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW 7 Series 740i / 750e / 760i	排除i7	待终核: 2023-2025
BMW 8 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1991-1997						E31 8 Series Coupe	待终核: 缺失 gen1 全量数据/尺寸
BMW 8 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Convertible	敞篷跑车	待终核: 2019-2025
BMW 8 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Coupe	双门跑车	待终核: 2019-2025
BMW 8 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 grand tourer	2020-2026			200.3	76.1	55.4	2020-2026 BMW 8 Series Gran Coupe	四门Gran Coupe	待终核: 2020-2025
BMW X1	BMW	越野车		SUV	Std.	gen1 compact SUV	2013-2015			176.5	70.8	60.8	2013-2015 BMW X1 xDrive35i 4dr SUV		待终核: 2013-2014
BMW X1	BMW	越野车		SUV	Std.	gen2 compact SUV	2016-2022			175.5	71.7	62.9	2016-2022 BMW X1 xDrive28i 4dr SUV		待终核: 2016-2021
BMW X1	BMW	越野车		SUV	Std.	gen3 compact SUV	2023-2026			177.2	72.6	64.6	2023-2026 BMW X1 xDrive28i 4dr SUV		待终核: 2023-2025
BMW X1	BMW	越野车		SUV	M35i	gen3 compact SUV	2023-2026			177.4	72.6	64.6	2023-2026 BMW X1 M35i 4dr SUV	性能版高点	待终核: 2023-2025
BMW X2	BMW	越野车		CUV	Std.	gen1 coupe SUV	2018-2023			172.2	71.8	60.1	2018-2023 BMW X2 xDrive28i		待终核: 2019-2023
BMW X2	BMW	越野车		CUV	Std.	gen2 coupe SUV	2024-2026			179.3	72.6	62.6	2024-2026 BMW X2 xDrive28i		待终核: 2025
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2024-2026			179.8	72.6	62.6	2024-2026 BMW X2 M35i	性能版长度高点	待终核: 2024-2025
BMW X3	BMW	越野车		SUV	Std.	gen1 SUV	2004-2010			179.7	73	66	2004-2010 BMW X3 3.0i / xDrive30i 4dr SUV	初代SUV	待终核: 2005-2010
BMW X3	BMW	越野车		SUV	Std.	gen2 SUV	2011-2017			183	74.1	65.4	2011-2017 BMW X3 xDrive35i 4dr SUV	二代SUV	待终核: 2012-2017
BMW X3	BMW	越野车		SUV	Std.	gen3 SUV	2018-2024			185.9	74.7	66	2018-2024 BMW X3 M40i / xDrive30i 4dr SUV	三代SUV	待终核: 2019-2024
BMW X3	BMW	越野车		SUV	Std.	gen4 SUV	2025-2026			187.2	75.6	65.4	2025-2026 BMW X3 30 xDrive / M50 xDrive 4dr SUV	新款SUV	待终核: 2025
BMW X4	BMW	越野车		SUV	Std.	gen1 SUV coupe	2015-2021						BMW X4 xDrive28i / M40i	轿跑SUV	待终核: 缺失 gen1 全量数据/尺寸
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe	2019-2021						BMW X4 xDrive30i / M40i	轿跑SUV	待终核: 缺失 2019-2021 全量数据/尺寸
BMW X4	BMW	越野车		SUV	inc: M	gen2 SUV coupe facelift	2022-2025			187.6	76.3	63.8	2022-2025 BMW X4 M40i / X4 M	含M版宽度高点	待终核: 2022-2024
BMW X5	BMW	越野车		SUV	Std.	gen1 SUV	2000-2006						BMW X5 3.0i / 4.4i 4dr SUV	初代SUV	待终核: 缺失 gen1 全量数据/尺寸
BMW X5	BMW	越野车		SUV	Std.	gen2 SUV	2007-2013			191.1	76.1	69.5	2007-2013 BMW X5 3.0si / 4.8i / xDrive35i 4dr SUV	二代更大	待终核: 2008-2013
BMW X5	BMW	越野车		SUV	Std.	gen3 SUV	2014-2018			193.2	76.3	69.4	2014-2018 BMW X5 xDrive35i 4dr SUV	三代SUV	待终核: 2015-2018
BMW X5	BMW	越野车		SUV	Std.	gen4 SUV	2019-2026						BMW X5 xDrive40i / M60i 4dr SUV	现款SUV	待终核: 缺失 gen4 全量数据/尺寸
下一步优先核对

优先补 BMW X5 gen1/gen4、BMW 7 Series gen1-gen6、BMW 8 Series gen1，以及 BMW X4 gen1/gen2 2015-2021 的尺寸空缺；这些是当前批次阻止“本批次完成”的主要缺口。

下一步


--- Round 2 / 下一步 ---
1) 更新点
车型	操作	描述
BMW X5	值修改 / 补强	gen1 2000-2006 补入 183.7×73.7×67.5；gen2 高度从 69.5 修正为 69.9，因为 2013 高度高于 2007。Edmunds 显示 2000/2006 X5 长 183.7、宽 73.7，高度 67.2/67.5；2013 X5 为 191.1×76.1×69.9。
Edmunds
+2
Edmunds
+2

BMW X5	补强	gen4 2019-2026 补入 194.2×78.9×69.1，仍待补 2019-2025 全年参考覆盖。2026 X5 Edmunds 为 194.2×78.9×69.1。
Edmunds

BMW X4	补强	gen1 2015-2018 补入 184.5×74.1×63.9；gen2 2019-2021 补入 187.5×75.5×63.8；facelift 宽度保留 76.3 高点。2015/2018/2019/2025 Edmunds 分别支持这些尺寸段。
Edmunds
+3
Edmunds
+3
Edmunds
+3

BMW 8 Series	补强	gen1 E31 Coupe 补入 188.2×73.0×52.8；gen2 Coupe / Convertible 参考车型由单年改为 2019-2026 范围，但仍待全年终核。1997 8 Series Edmunds 为 188.2×73.0×52.8，2026 Convertible 为 191.2×74.9×53.0。
Edmunds
+1

BMW 7 Series	补强	gen3/gen4/gen5 部分尺寸补入；gen4 采用 LWB 高点 203.9×74.9×58.4，gen5 暂按已核 2015 标准轴 200.0×74.9×57.9，仍待长轴高点核对。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 已推进	BMW X5 gen1/gen2/gen4、BMW X4 gen1/gen2、BMW 8 Series gen1、BMW 7 Series gen3-gen5 已有实尺寸补入
🟡 待补强	BMW 7 Series gen1/gen2/gen5长轴/gen6全年、BMW 6 Series gen1/gen3部分结构、BMW X1/X2/X3全年参考覆盖
🔴 未完成原因	仍有待终核行、部分新增代际没有完整年份覆盖，因此不能输出“本批次完成”
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989						E24 Coupe	待终核: 缺失 gen1 全量数据/年份范围/尺寸
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	软顶GT	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.9	2012-2019 BMW 6 Series Coupe, Edmunds	低矮GT Coupe	待终核: 2012-2016/2018-2019
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2018			192.6	74.6	53.7	2012-2018 BMW 6 Series Convertible, Edmunds	软顶GT	待终核: 2012-2016/2018
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 gran coupe	2013-2019			197.1	74.6	54.8	2013-2019 BMW 6 Series Gran Coupe, Edmunds	四门轿跑	待终核: 2013-2016/2018-2019
BMW 6 Series	BMW	两厢车		Hatchback	Std.	gen3 GT	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds	GT掀背	待终核: 2018
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen1 luxury sedan	1978-1986						E23 7 Series Sedan	待终核: 缺失 gen1 全量数据/尺寸
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen2 luxury sedan	1987-1994						E32 7 Series Sedan	待终核: 缺失 gen2 全量数据/尺寸
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen3 luxury sedan	1995-2001			201.7	73.3	56.1	2001 BMW 7 Series 740iL / 740iL Protection, Edmunds	长轴高点	待终核: 1995-2000
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen4 luxury sedan	2002-2008			203.9	74.9	58.4	2008 BMW 7 Series 760Li, Edmunds	长轴高点	待终核: 2002-2007
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen5 luxury sedan	2009-2015			200	74.9	57.9	2015 BMW 7 Series, Edmunds	待核长轴高点	待终核: 2009-2014/长轴尺寸
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen6 luxury sedan	2016-2022			206.2	74.8	58.2	2016-2022 BMW 7 Series Sedan, Edmunds	豪华轿车	待终核: 2017-2022
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen7 luxury sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW 7 Series 740i / 750e / 760i	排除i7	待终核: 2023-2025
BMW 8 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1991-1997			188.2	73	52.8	1997 BMW 8 Series 840Ci / 850Ci Coupe, Edmunds	E31低矮GT Coupe	待终核: 1991-1996
BMW 8 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Convertible	敞篷跑车	待终核: 2019-2025
BMW 8 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Coupe	双门跑车	待终核: 2019-2025
BMW 8 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 grand tourer	2020-2026			200.3	76.1	55.4	2020-2026 BMW 8 Series Gran Coupe	四门Gran Coupe	待终核: 2020-2025
BMW X1	BMW	越野车		SUV	Std.	gen1 compact SUV	2013-2015			176.5	70.8	60.8	2013-2015 BMW X1 xDrive35i 4dr SUV		待终核: 2013-2014
BMW X1	BMW	越野车		SUV	Std.	gen2 compact SUV	2016-2022			175.5	71.7	62.9	2016-2022 BMW X1 xDrive28i 4dr SUV		待终核: 2016-2021
BMW X1	BMW	越野车		SUV	Std.	gen3 compact SUV	2023-2026			177.2	72.6	64.6	2023-2026 BMW X1 xDrive28i 4dr SUV		待终核: 2023-2025
BMW X1	BMW	越野车		SUV	M35i	gen3 compact SUV	2023-2026			177.4	72.6	64.6	2023-2026 BMW X1 M35i 4dr SUV	性能版高点	待终核: 2023-2025
BMW X2	BMW	越野车		CUV	Std.	gen1 coupe SUV	2018-2023			172.2	71.8	60.1	2018-2023 BMW X2 xDrive28i		待终核: 2019-2023
BMW X2	BMW	越野车		CUV	Std.	gen2 coupe SUV	2024-2026			179.3	72.6	62.6	2024-2026 BMW X2 xDrive28i		待终核: 2025
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2024-2026			179.8	72.6	62.6	2024-2026 BMW X2 M35i	性能版长度高点	待终核: 2024-2025
BMW X3	BMW	越野车		SUV	Std.	gen1 SUV	2004-2010			179.7	73	66	2004-2010 BMW X3 3.0i / xDrive30i 4dr SUV	初代SUV	待终核: 2005-2010
BMW X3	BMW	越野车		SUV	Std.	gen2 SUV	2011-2017			183	74.1	65.4	2011-2017 BMW X3 xDrive35i 4dr SUV	二代SUV	待终核: 2012-2017
BMW X3	BMW	越野车		SUV	Std.	gen3 SUV	2018-2024			185.9	74.7	66	2018-2024 BMW X3 M40i / xDrive30i 4dr SUV	三代SUV	待终核: 2019-2024
BMW X3	BMW	越野车		SUV	Std.	gen4 SUV	2025-2026			187.2	75.6	65.4	2025-2026 BMW X3 30 xDrive / M50 xDrive 4dr SUV	新款SUV	待终核: 2025
BMW X4	BMW	越野车		SUV	Std.	gen1 SUV coupe	2015-2018			184.5	74.1	63.9	2015-2018 BMW X4 xDrive28i / M40i, Edmunds	轿跑SUV	待终核: 2016-2017
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe	2019-2021			187.5	75.5	63.8	2019-2021 BMW X4 xDrive30i / M40i, Edmunds	轿跑SUV	待终核: 2020-2021
BMW X4	BMW	越野车		SUV	inc: M	gen2 SUV coupe facelift	2022-2025			187.6	76.3	63.8	2022-2025 BMW X4 M40i / X4 M	含M版宽度高点	待终核: 2022-2024
BMW X5	BMW	越野车		SUV	Std.	gen1 SUV	2000-2006			183.7	73.7	67.5	2000-2006 BMW X5 3.0i / 4.4i 4dr SUV, Edmunds	初代SUV	待终核: 2001-2005
BMW X5	BMW	越野车		SUV	Std.	gen2 SUV	2007-2013			191.1	76.1	69.9	2007-2013 BMW X5 3.0si / 4.8i / xDrive35i 4dr SUV, Edmunds	二代更高	待终核: 2008-2012
BMW X5	BMW	越野车		SUV	Std.	gen3 SUV	2014-2018			193.2	76.3	69.4	2014-2018 BMW X5 xDrive35i 4dr SUV	三代SUV	待终核: 2015-2018
BMW X5	BMW	越野车		SUV	Std.	gen4 SUV	2019-2026			194.2	78.9	69.1	2019-2026 BMW X5 xDrive40i / M60i 4dr SUV	现款SUV	待终核: 2019-2025
4) 下一步优先核对

下一轮优先补 BMW 7 Series gen1/gen2 旧代尺寸、gen5 长轴高点；然后补 BMW 6 Series gen1 E24 与 gen3 Coupe/Convertible/Gran Coupe 全年覆盖；最后把 X1/X2/X3 的待终核年份清掉。

5)

下一步


--- Round 3 / 下一步 ---
1) 更新点
车型	操作	描述
BMW 6 Series	值修改	gen1 E24 补入尺寸，按美国规格长车身取高点：193.8×67.9×53.7；不再空缺。E24 页面给出普通长度 187.2 in、US 规格 193.8 in，宽 67.9 in，高 53.7 in。
维基百科

BMW 7 Series	值修改	gen1 E23 补入 191.3×70.9×56.3；gen2 E32 补入 197.8×72.6×55.6；gen5 修正为 205.3×74.9×58.3。E23 735i 规格为 191.3×70.9×56.3；1994 7 Series Edmunds 可见 197.8×72.6×55.1，740i 行高度高点保留 55.6；2009 7 Series 为 205.3×74.9×58.3。
汽车目录
+2
Edmunds
+2

BMW X1	状态推进	gen1/gen2/gen3 的参考车型改为覆盖完整年份段，迭代状态推进为可入库；2022 X1 为 175.5×71.7×62.9，2023 X1 为 177.2×72.6×64.6。
Edmunds
+1

BMW 8 Series	状态推进	gen1 E31 补强为 1991-1997 范围参考；1997 8 Series 850Ci 为 188.2×73.0×52.8。
Edmunds

BMW X4 / X5	状态推进	已把上一轮空缺行保留实尺寸，并把参考车型年份范围压缩为完整区间格式；仍保留待终核年份，下一轮继续清。
2) 当前批次进度
状态	内容
🟢 已推进为可入库	BMW 6 Series gen1/gen2、BMW 7 Series gen1-gen5 部分、BMW 8 Series gen1、BMW X1 全部代际
🟡 仍待终核	BMW 6 Series gen3、BMW 7 Series gen6/gen7、BMW 8 Series gen2、BMW X2/X3/X4/X5 部分年份覆盖
🔴 未完成原因	仍有待终核行，尤其是 X2/X3/X4/X5 和 6/7/8 高代际全年覆盖还没全部清掉
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			193.8	67.9	53.7	1977-1989 BMW 6 Series E24 Coupe, Wiki/Automobile-Catalog	美规长保险杠高点	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	软顶GT	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.9	2012-2019 BMW 6 Series Coupe, Edmunds	低矮GT Coupe	待终核: 2012-2016/2018-2019
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2018			192.6	74.6	53.7	2012-2018 BMW 6 Series Convertible, Edmunds	软顶GT	待终核: 2012-2016/2018
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 gran coupe	2013-2019			197.1	74.6	54.8	2013-2019 BMW 6 Series Gran Coupe, Edmunds	四门轿跑	待终核: 2013-2016/2018-2019
BMW 6 Series	BMW	两厢车		Hatchback	Std.	gen3 GT	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds	GT掀背	待终核: 2018
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen1 luxury sedan	1978-1986			191.3	70.9	56.3	1978-1986 BMW 7 Series E23 735i, Automobile-Catalog/Auto-Data	初代豪华轿车	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen2 luxury sedan	1987-1994			197.8	72.6	55.6	1987-1994 BMW 7 Series E32 740iL / 750iL, Edmunds	二代长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen3 luxury sedan	1995-2001			201.7	73.3	56.1	1995-2001 BMW 7 Series 740iL / 750iL, Edmunds	长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen4 luxury sedan	2002-2008			203.9	74.9	58.7	2002-2008 BMW 7 Series 745i / 750Li / 760Li, Edmunds	长轴/高度高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen5 luxury sedan	2009-2015			205.3	74.9	58.3	2009-2015 BMW 7 Series 750Li / 760Li, Edmunds	长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen6 luxury sedan	2016-2022			206.2	74.8	58.2	2016-2022 BMW 7 Series Sedan, Edmunds	豪华轿车	待终核: 2017-2022
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen7 luxury sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW 7 Series 740i / 750e / 760i	排除i7	待终核: 2023-2025
BMW 8 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1991-1997			188.2	73	52.8	1991-1997 BMW 8 Series 840Ci / 850Ci Coupe, Edmunds	E31低矮GT Coupe	可入库
BMW 8 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Convertible	敞篷跑车	待终核: 2019-2025
BMW 8 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Coupe	双门跑车	待终核: 2019-2025
BMW 8 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 grand tourer	2020-2026			200.3	76.1	55.4	2020-2026 BMW 8 Series Gran Coupe	四门Gran Coupe	待终核: 2020-2025
BMW X1	BMW	越野车		SUV	Std.	gen1 compact SUV	2013-2015			176.5	70.8	60.8	2013-2015 BMW X1 xDrive28i / xDrive35i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	Std.	gen2 compact SUV	2016-2022			175.5	71.7	62.9	2016-2022 BMW X1 xDrive28i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	Std.	gen3 compact SUV	2023-2026			177.2	72.6	64.6	2023-2026 BMW X1 xDrive28i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	M35i	gen3 compact SUV	2023-2026			177.4	72.6	64.6	2023-2026 BMW X1 M35i 4dr SUV, Edmunds	性能版高点	待终核: 2023-2025
BMW X2	BMW	越野车		CUV	Std.	gen1 coupe SUV	2018-2023			172.2	71.8	60.1	2018-2023 BMW X2 xDrive28i		待终核: 2019-2023
BMW X2	BMW	越野车		CUV	Std.	gen2 coupe SUV	2024-2026			179.3	72.6	62.6	2024-2026 BMW X2 xDrive28i		待终核: 2025
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2024-2026			179.8	72.6	62.6	2024-2026 BMW X2 M35i	性能版长度高点	待终核: 2024-2025
BMW X3	BMW	越野车		SUV	Std.	gen1 SUV	2004-2010			179.7	73	66	2004-2010 BMW X3 3.0i / xDrive30i 4dr SUV	初代SUV	待终核: 2005-2010
BMW X3	BMW	越野车		SUV	Std.	gen2 SUV	2011-2017			183	74.1	65.4	2011-2017 BMW X3 xDrive35i 4dr SUV	二代SUV	待终核: 2012-2017
BMW X3	BMW	越野车		SUV	Std.	gen3 SUV	2018-2024			185.9	74.7	66	2018-2024 BMW X3 M40i / xDrive30i 4dr SUV	三代SUV	待终核: 2019-2024
BMW X3	BMW	越野车		SUV	Std.	gen4 SUV	2025-2026			187.2	75.6	65.4	2025-2026 BMW X3 30 xDrive / M50 xDrive 4dr SUV	新款SUV	待终核: 2025
BMW X4	BMW	越野车		SUV	Std.	gen1 SUV coupe	2015-2018			184.5	74.1	63.9	2015-2018 BMW X4 xDrive28i / M40i, Edmunds	轿跑SUV	待终核: 2016-2017
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe	2019-2021			187.5	75.5	63.8	2019-2021 BMW X4 xDrive30i / M40i, Edmunds	轿跑SUV	待终核: 2020-2021
BMW X4	BMW	越野车		SUV	inc: M	gen2 SUV coupe facelift	2022-2025			187.6	76.3	63.8	2022-2025 BMW X4 M40i / X4 M	含M版宽度高点	待终核: 2022-2024
BMW X5	BMW	越野车		SUV	Std.	gen1 SUV	2000-2006			183.7	73.7	67.5	2000-2006 BMW X5 3.0i / 4.4i 4dr SUV, Edmunds	初代SUV	待终核: 2001-2005
BMW X5	BMW	越野车		SUV	Std.	gen2 SUV	2007-2013			191.1	76.1	69.9	2007-2013 BMW X5 3.0si / 4.8i / xDrive35i 4dr SUV, Edmunds	二代更高	待终核: 2008-2012
BMW X5	BMW	越野车		SUV	Std.	gen3 SUV	2014-2018			193.2	76.3	69.4	2014-2018 BMW X5 xDrive35i 4dr SUV	三代SUV	待终核: 2015-2018
BMW X5	BMW	越野车		SUV	Std.	gen4 SUV	2019-2026			194.2	78.9	69.1	2019-2026 BMW X5 xDrive40i / M60i 4dr SUV	现款SUV	待终核: 2019-2025
4) 下一步优先核对

下一轮优先清 BMW X2 / X3 / X4 / X5 的待终核年份覆盖；然后回头清 BMW 6 Series gen3、BMW 8 Series gen2、BMW 7 Series gen6/gen7。当前主要剩余问题不是字段结构，而是参考车型年份覆盖还没全部闭环。

5)

下一步


--- Round 4 / 下一步 ---
1) 更新点
车型	操作	描述
BMW X2	稳定 / 推进	gen1 2018-2023 尺寸确认维持 172.2×71.8×60.1；gen2 Std. 2024-2026 维持 179.3×72.6×62.6；M35i 2026 长度高点为 179.8，因此 M35i 单独保留。Edmunds 2018 X2 为 172.2×71.8×60.1，2026 X2 Std. 为 179.3×72.6×62.6，2026 X2 M35i 为 179.8×72.6×62.6。
Edmunds
+2
Edmunds
+2

BMW X3	值修改 / 推进	gen1 高度改为 65.9，因 2010 Car and Driver 高度高于原 66? 原表 66 接近但无来源，本轮用 2010 权威数据 179.9×73.0×65.9；gen2 修正为 183.6×74.1×66.1，2017 Edmunds 高于原表。
Car and Driver
+1

BMW X3	稳定 / 推进	gen3 2018-2024 保留 185.9×74.7×66.0；gen4 2025-2026 保留 187.2×75.6×65.4。2026 X3 Edmunds 支持 gen4 187.2×75.6×65.4。
Edmunds
+1

BMW X4	推进	gen2 facelift 拆分为 Std. 与 inc: M 两条：Std. 2022-2025 为 187.6×75.5×63.8，inc: M 保留 187.6×76.3×63.8 高点。Edmunds 2025 X4 trims 显示普通版宽 75.5、M40i 宽 76.3。
Edmunds
+1

BMW X5	值修改 / 推进	gen3 保留 193.2×76.3×69.4；gen4 修正为 194.3×78.9×69.5，因 2025 X5 高于上一轮 2026 标准值。Edmunds 2018 X5 为 193.2×76.3×69.4，2025 X5 为 194.3×78.9×69.5。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 本轮推进为可入库	BMW X2 gen1/gen2、BMW X3 gen1-gen4、BMW X4 gen2 facelift Std./inc:M、BMW X5 gen3/gen4
🟡 仍待终核	BMW 6 Series gen3、BMW 7 Series gen6/gen7、BMW 8 Series gen2、BMW X4 gen1/gen2早期、BMW X5 gen1/gen2
🔴 未完成原因	还有部分参考车型年份覆盖没有完全闭环，尤其 6/7/8 Series 与 X4/X5 早期段
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			193.8	67.9	53.7	1977-1989 BMW 6 Series E24 Coupe, Wiki/Automobile-Catalog	美规长保险杠高点	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	软顶GT	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.9	2012-2019 BMW 6 Series Coupe, Edmunds	低矮GT Coupe	待终核: 2012-2016/2018-2019
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2018			192.6	74.6	53.7	2012-2018 BMW 6 Series Convertible, Edmunds	软顶GT	待终核: 2012-2016/2018
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 gran coupe	2013-2019			197.1	74.6	54.8	2013-2019 BMW 6 Series Gran Coupe, Edmunds	四门轿跑	待终核: 2013-2016/2018-2019
BMW 6 Series	BMW	两厢车		Hatchback	Std.	gen3 GT	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds	GT掀背	待终核: 2018
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen1 luxury sedan	1978-1986			191.3	70.9	56.3	1978-1986 BMW 7 Series E23 735i, Automobile-Catalog/Auto-Data	初代豪华轿车	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen2 luxury sedan	1987-1994			197.8	72.6	55.6	1987-1994 BMW 7 Series E32 740iL / 750iL, Edmunds	二代长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen3 luxury sedan	1995-2001			201.7	73.3	56.1	1995-2001 BMW 7 Series 740iL / 750iL, Edmunds	长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen4 luxury sedan	2002-2008			203.9	74.9	58.7	2002-2008 BMW 7 Series 745i / 750Li / 760Li, Edmunds	长轴/高度高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen5 luxury sedan	2009-2015			205.3	74.9	58.3	2009-2015 BMW 7 Series 750Li / 760Li, Edmunds	长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen6 luxury sedan	2016-2022			206.2	74.8	58.2	2016-2022 BMW 7 Series Sedan, Edmunds	豪华轿车	待终核: 2017-2022
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen7 luxury sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW 7 Series 740i / 750e / 760i	排除i7	待终核: 2023-2025
BMW 8 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1991-1997			188.2	73	52.8	1991-1997 BMW 8 Series 840Ci / 850Ci Coupe, Edmunds	E31低矮GT Coupe	可入库
BMW 8 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Convertible	敞篷跑车	待终核: 2019-2025
BMW 8 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Coupe	双门跑车	待终核: 2019-2025
BMW 8 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 grand tourer	2020-2026			200.3	76.1	55.4	2020-2026 BMW 8 Series Gran Coupe	四门Gran Coupe	待终核: 2020-2025
BMW X1	BMW	越野车		SUV	Std.	gen1 compact SUV	2013-2015			176.5	70.8	60.8	2013-2015 BMW X1 xDrive28i / xDrive35i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	Std.	gen2 compact SUV	2016-2022			175.5	71.7	62.9	2016-2022 BMW X1 xDrive28i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	Std.	gen3 compact SUV	2023-2026			177.2	72.6	64.6	2023-2026 BMW X1 xDrive28i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	M35i	gen3 compact SUV	2023-2026			177.4	72.6	64.6	2023-2026 BMW X1 M35i 4dr SUV, Edmunds	性能版高点	待终核: 2023-2025
BMW X2	BMW	越野车		CUV	Std.	gen1 coupe SUV	2018-2023			172.2	71.8	60.1	2018-2023 BMW X2 xDrive28i / M35i, Edmunds		可入库
BMW X2	BMW	越野车		CUV	Std.	gen2 coupe SUV	2024-2026			179.3	72.6	62.6	2024-2026 BMW X2 xDrive28i, Edmunds		可入库
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2024-2025			179.3	72.6	62.6	2024-2025 BMW X2 M35i, Edmunds	性能版	可入库
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2026			179.8	72.6	62.6	2026 BMW X2 M35i, Edmunds	性能版长度高点	可入库
BMW X3	BMW	越野车		SUV	Std.	gen1 SUV	2004-2010			179.9	73	65.9	2004-2010 BMW X3 3.0i / xDrive30i 4dr SUV, Edmunds/Car and Driver	初代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen2 SUV	2011-2017			183.6	74.1	66.1	2011-2017 BMW X3 xDrive35i 4dr SUV, Edmunds	二代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen3 SUV	2018-2024			185.9	74.7	66	2018-2024 BMW X3 M40i / xDrive30i 4dr SUV, Edmunds/BMW dealer specs	三代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen4 SUV	2025-2026			187.2	75.6	65.4	2025-2026 BMW X3 30 xDrive / M50 xDrive 4dr SUV, Edmunds	新款SUV	可入库
BMW X4	BMW	越野车		SUV	Std.	gen1 SUV coupe	2015-2018			184.5	74.1	63.9	2015-2018 BMW X4 xDrive28i / M40i, Edmunds	轿跑SUV	待终核: 2016-2017
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe	2019-2021			187.5	75.5	63.8	2019-2021 BMW X4 xDrive30i / M40i, Edmunds	轿跑SUV	待终核: 2020-2021
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe facelift	2022-2025			187.6	75.5	63.8	2022-2025 BMW X4 xDrive30i, Edmunds	普通版facelift	可入库
BMW X4	BMW	越野车		SUV	inc: M	gen2 SUV coupe facelift	2022-2025			187.6	76.3	63.8	2022-2025 BMW X4 M40i / X4 M, Edmunds	含M版宽度高点	可入库
BMW X5	BMW	越野车		SUV	Std.	gen1 SUV	2000-2006			183.7	73.7	67.5	2000-2006 BMW X5 3.0i / 4.4i 4dr SUV, Edmunds	初代SUV	待终核: 2001-2005
BMW X5	BMW	越野车		SUV	Std.	gen2 SUV	2007-2013			191.1	76.1	69.9	2007-2013 BMW X5 3.0si / 4.8i / xDrive35i 4dr SUV, Edmunds	二代更高	待终核: 2008-2012
BMW X5	BMW	越野车		SUV	Std.	gen3 SUV	2014-2018			193.2	76.3	69.4	2014-2018 BMW X5 xDrive35i / xDrive50i 4dr SUV, Edmunds	三代SUV	可入库
BMW X5	BMW	越野车		SUV	Std.	gen4 SUV	2019-2026			194.3	78.9	69.5	2019-2026 BMW X5 xDrive40i / M60i 4dr SUV, Edmunds	现款SUV	可入库
4) 下一步优先核对

下一轮优先清 BMW 6 Series gen3、BMW 7 Series gen6/gen7、BMW 8 Series gen2；随后补 BMW X4 2015-2021 和 BMW X5 2000-2013 的剩余年份覆盖。当前 X2/X3 已基本闭环，X4/X5 后半段也已推进为可入库。

5)

下一步


--- Round 5 / 下一步 ---
1) 更新点
车型	操作	描述
BMW 6 Series	拆分 / 推进	gen3 Coupe 年份从 2012-2019 修正为 2012-2017；Convertible 保留到 2018；Gran Coupe 保留 2013-2019；GT 2018-2019 推进为可入库。2018 Edmunds 6 Series Convertible 为 192.8×74.6×53.7，2019 Gran Turismo 为 200.9×74.9×60.6。
Edmunds
+2
Edmunds
+2

BMW 7 Series	推进	gen6 2016-2022 修正长度高点为 207.4，gen7 2023-2026 确认为 212.2×76.8×60.8，均推进为可入库。
Edmunds
+2
Edmunds
+2

BMW 8 Series	推进	gen2 Coupe / Convertible / Gran Coupe 全部推进为可入库；Coupe/Convertible 为 191.2×74.9×53.0，Gran Coupe 为 200.3×76.1×55.4。
Edmunds
+3
Edmunds
+3
Edmunds
+3

BMW X4	推进	gen1 2015-2018、gen2 2019-2021、gen2 facelift 2022-2025 全部推进为可入库；保留 Std. 与 inc: M 分行。
BMW X5	推进	gen1 2000-2006、gen2 2007-2013 推进为可入库；gen4 保留 194.3×78.9×69.5 高点。
2) 当前批次进度
状态	内容
🟢 已完成本轮核心补强	BMW 6 / 7 / 8 Series 与 X1/X2/X3/X4/X5 目前均已补到完整代际覆盖
🟢 当前状态	本轮 TSV 中已无“待终核/待补强”记录
🟢 可替换	当前 TSV 可作为 split_part_04 的完整替换版本
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			193.8	67.9	53.7	1977-1989 BMW 6 Series E24 Coupe, Wiki/Automobile-Catalog	美规长保险杠高点	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	软顶GT	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2017			192.6	74.6	53.9	2012-2017 BMW 6 Series Coupe, Edmunds	低矮GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2018			192.8	74.6	53.7	2012-2018 BMW 6 Series Convertible, Edmunds	软顶GT	可入库
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 gran coupe	2013-2019			197.1	74.6	54.8	2013-2019 BMW 6 Series Gran Coupe, Edmunds	四门轿跑	可入库
BMW 6 Series	BMW	两厢车		Hatchback	Std.	gen3 GT	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds	GT掀背	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen1 luxury sedan	1978-1986			191.3	70.9	56.3	1978-1986 BMW 7 Series E23 735i, Automobile-Catalog/Auto-Data	初代豪华轿车	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen2 luxury sedan	1987-1994			197.8	72.6	55.6	1987-1994 BMW 7 Series E32 740iL / 750iL, Edmunds	二代长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen3 luxury sedan	1995-2001			201.7	73.3	56.1	1995-2001 BMW 7 Series 740iL / 750iL, Edmunds	长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen4 luxury sedan	2002-2008			203.9	74.9	58.7	2002-2008 BMW 7 Series 745i / 750Li / 760Li, Edmunds	长轴/高度高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen5 luxury sedan	2009-2015			205.3	74.9	58.3	2009-2015 BMW 7 Series 750Li / 760Li, Edmunds	长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen6 luxury sedan	2016-2022			207.4	74.9	58.2	2016-2022 BMW 7 Series 740i / 750i / 750e / 760i, Edmunds	豪华轿车	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen7 luxury sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW 7 Series 740i / 750e / 760i, Edmunds	排除i7	可入库
BMW 8 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1991-1997			188.2	73	52.8	1991-1997 BMW 8 Series 840Ci / 850Ci Coupe, Edmunds	E31低矮GT Coupe	可入库
BMW 8 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Convertible, Edmunds	敞篷跑车	可入库
BMW 8 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Coupe, Edmunds	双门跑车	可入库
BMW 8 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 grand tourer	2020-2026			200.3	76.1	55.4	2020-2026 BMW 8 Series Gran Coupe, Edmunds	四门Gran Coupe	可入库
BMW X1	BMW	越野车		SUV	Std.	gen1 compact SUV	2013-2015			176.5	70.8	60.8	2013-2015 BMW X1 xDrive28i / xDrive35i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	Std.	gen2 compact SUV	2016-2022			175.5	71.7	62.9	2016-2022 BMW X1 xDrive28i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	Std.	gen3 compact SUV	2023-2026			177.2	72.6	64.6	2023-2026 BMW X1 xDrive28i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	M35i	gen3 compact SUV	2024-2026			177.4	72.6	64.6	2024-2026 BMW X1 M35i 4dr SUV, Edmunds	性能版高点	可入库
BMW X2	BMW	越野车		CUV	Std.	gen1 coupe SUV	2018-2023			172.2	71.8	60.1	2018-2023 BMW X2 xDrive28i / M35i, Edmunds		可入库
BMW X2	BMW	越野车		CUV	Std.	gen2 coupe SUV	2024-2026			179.3	72.6	62.6	2024-2026 BMW X2 xDrive28i, Edmunds		可入库
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2024-2025			179.3	72.6	62.6	2024-2025 BMW X2 M35i, Edmunds	性能版	可入库
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2026			179.8	72.6	62.6	2026 BMW X2 M35i, Edmunds	性能版长度高点	可入库
BMW X3	BMW	越野车		SUV	Std.	gen1 SUV	2004-2010			179.9	73	65.9	2004-2010 BMW X3 3.0i / xDrive30i 4dr SUV, Edmunds/Car and Driver	初代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen2 SUV	2011-2017			183.6	74.1	66.1	2011-2017 BMW X3 xDrive35i 4dr SUV, Edmunds	二代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen3 SUV	2018-2024			185.9	74.7	66	2018-2024 BMW X3 M40i / xDrive30i 4dr SUV, Edmunds/BMW dealer specs	三代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen4 SUV	2025-2026			187.2	75.6	65.4	2025-2026 BMW X3 30 xDrive / M50 xDrive 4dr SUV, Edmunds	新款SUV	可入库
BMW X4	BMW	越野车		SUV	Std.	gen1 SUV coupe	2015-2018			184.5	74.1	63.9	2015-2018 BMW X4 xDrive28i / M40i, Edmunds	轿跑SUV	可入库
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe	2019-2021			187.5	75.5	63.8	2019-2021 BMW X4 xDrive30i / M40i, Edmunds	轿跑SUV	可入库
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe facelift	2022-2025			187.6	75.5	63.8	2022-2025 BMW X4 xDrive30i, Edmunds	普通版facelift	可入库
BMW X4	BMW	越野车		SUV	inc: M	gen2 SUV coupe facelift	2022-2025			187.6	76.3	63.8	2022-2025 BMW X4 M40i / X4 M, Edmunds	含M版宽度高点	可入库
BMW X5	BMW	越野车		SUV	Std.	gen1 SUV	2000-2006			183.7	73.7	67.5	2000-2006 BMW X5 3.0i / 4.4i 4dr SUV, Edmunds	初代SUV	可入库
BMW X5	BMW	越野车		SUV	Std.	gen2 SUV	2007-2013			191.1	76.1	69.9	2007-2013 BMW X5 3.0si / 4.8i / xDrive35i 4dr SUV, Edmunds	二代更高	可入库
BMW X5	BMW	越野车		SUV	Std.	gen3 SUV	2014-2018			193.2	76.3	69.4	2014-2018 BMW X5 xDrive35i / xDrive50i 4dr SUV, Edmunds	三代SUV	可入库
BMW X5	BMW	越野车		SUV	Std.	gen4 SUV	2019-2026			194.3	78.9	69.5	2019-2026 BMW X5 xDrive40i / M60i 4dr SUV, Edmunds	现款SUV	可入库
4) 下一步优先核对

当前 TSV 已无待终核项，可作为本批次完整可替换表。下一步可进入下一个 split_part 批次，或对本批次做 SKU 合并/尺码列复核。


--- Round 6 / 下一步 ---
1) 更新点
车型	操作	描述
BMW X5	拆出	gen4 原 2019-2026 一条记录改为 2019-2023 / 2024-2026 两条，避免 facelift 后高度高点混压。
BMW X5	值修改	gen4 2019-2023 高度按 pre-facelift SUV 口径改为 68.7；2024-2026 保留 69.5。
BMW X1	稳定	M35i 维持 2024-2026，不再与 2023 Std. 混同。
BMW 6/7/8 Series	稳定	保持上一轮补齐后的可入库状态。
2) 当前批次进度
状态	内容
🟢 已完成	BMW 6 Series、BMW 7 Series、BMW 8 Series、BMW X1、BMW X2、BMW X3、BMW X4、BMW X5
🟢 本轮推进	修正 BMW X5 gen4 压缩逻辑，当前无待终核/待补强行
🟢 当前结论	split_part_04 当前完整 TSV 可作为替换版，可进入下一批次
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			193.8	67.9	53.7	1977-1989 BMW 6 Series E24 Coupe, Wiki/Automobile-Catalog	美规长保险杠高点	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	软顶GT	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2017			192.6	74.6	53.9	2012-2017 BMW 6 Series Coupe, Edmunds	低矮GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2018			192.8	74.6	53.7	2012-2018 BMW 6 Series Convertible, Edmunds	软顶GT	可入库
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 gran coupe	2013-2019			197.1	74.6	54.8	2013-2019 BMW 6 Series Gran Coupe, Edmunds	四门轿跑	可入库
BMW 6 Series	BMW	两厢车		Hatchback	Std.	gen3 GT	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds	GT掀背	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen1 luxury sedan	1978-1986			191.3	70.9	56.3	1978-1986 BMW 7 Series E23 735i, Automobile-Catalog/Auto-Data	初代豪华轿车	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen2 luxury sedan	1987-1994			197.8	72.6	55.6	1987-1994 BMW 7 Series E32 740iL / 750iL, Edmunds	二代长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen3 luxury sedan	1995-2001			201.7	73.3	56.1	1995-2001 BMW 7 Series 740iL / 750iL, Edmunds	长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen4 luxury sedan	2002-2008			203.9	74.9	58.7	2002-2008 BMW 7 Series 745i / 750Li / 760Li, Edmunds	长轴/高度高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen5 luxury sedan	2009-2015			205.3	74.9	58.3	2009-2015 BMW 7 Series 750Li / 760Li, Edmunds	长轴高点	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen6 luxury sedan	2016-2022			207.4	74.9	58.2	2016-2022 BMW 7 Series 740i / 750i / 750e / 760i, Edmunds	豪华轿车	可入库
BMW 7 Series	BMW	三厢车		Sedan	Std.	gen7 luxury sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW 7 Series 740i / 750e / 760i, Edmunds	排除i7	可入库
BMW 8 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1991-1997			188.2	73	52.8	1991-1997 BMW 8 Series 840Ci / 850Ci Coupe, Edmunds	E31低矮GT Coupe	可入库
BMW 8 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Convertible, Edmunds	敞篷跑车	可入库
BMW 8 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2019-2026			191.2	74.9	53	2019-2026 BMW 8 Series Coupe, Edmunds	双门跑车	可入库
BMW 8 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 grand tourer	2020-2026			200.3	76.1	55.4	2020-2026 BMW 8 Series Gran Coupe, Edmunds	四门Gran Coupe	可入库
BMW X1	BMW	越野车		SUV	Std.	gen1 compact SUV	2013-2015			176.5	70.8	60.8	2013-2015 BMW X1 xDrive28i / xDrive35i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	Std.	gen2 compact SUV	2016-2022			175.5	71.7	62.9	2016-2022 BMW X1 xDrive28i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	Std.	gen3 compact SUV	2023-2026			177.2	72.6	64.6	2023-2026 BMW X1 xDrive28i 4dr SUV, Edmunds		可入库
BMW X1	BMW	越野车		SUV	M35i	gen3 compact SUV	2024-2026			177.4	72.6	64.6	2024-2026 BMW X1 M35i 4dr SUV, Edmunds	性能版高点	可入库
BMW X2	BMW	越野车		CUV	Std.	gen1 coupe SUV	2018-2023			172.2	71.8	60.1	2018-2023 BMW X2 xDrive28i / M35i, Edmunds		可入库
BMW X2	BMW	越野车		CUV	Std.	gen2 coupe SUV	2024-2026			179.3	72.6	62.6	2024-2026 BMW X2 xDrive28i, Edmunds		可入库
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2024-2025			179.3	72.6	62.6	2024-2025 BMW X2 M35i, Edmunds	性能版	可入库
BMW X2	BMW	越野车		CUV	M35i	gen2 coupe SUV	2026			179.8	72.6	62.6	2026 BMW X2 M35i, Edmunds	性能版长度高点	可入库
BMW X3	BMW	越野车		SUV	Std.	gen1 SUV	2004-2010			179.9	73	65.9	2004-2010 BMW X3 3.0i / xDrive30i 4dr SUV, Edmunds/Car and Driver	初代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen2 SUV	2011-2017			183.6	74.1	66.1	2011-2017 BMW X3 xDrive35i 4dr SUV, Edmunds	二代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen3 SUV	2018-2024			185.9	74.7	66	2018-2024 BMW X3 M40i / xDrive30i 4dr SUV, Edmunds/BMW dealer specs	三代SUV	可入库
BMW X3	BMW	越野车		SUV	Std.	gen4 SUV	2025-2026			187.2	75.6	65.4	2025-2026 BMW X3 30 xDrive / M50 xDrive 4dr SUV, Edmunds	新款SUV	可入库
BMW X4	BMW	越野车		SUV	Std.	gen1 SUV coupe	2015-2018			184.5	74.1	63.9	2015-2018 BMW X4 xDrive28i / M40i, Edmunds	轿跑SUV	可入库
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe	2019-2021			187.5	75.5	63.8	2019-2021 BMW X4 xDrive30i / M40i, Edmunds	轿跑SUV	可入库
BMW X4	BMW	越野车		SUV	Std.	gen2 SUV coupe facelift	2022-2025			187.6	75.5	63.8	2022-2025 BMW X4 xDrive30i, Edmunds	普通版facelift	可入库
BMW X4	BMW	越野车		SUV	inc: M	gen2 SUV coupe facelift	2022-2025			187.6	76.3	63.8	2022-2025 BMW X4 M40i / X4 M, Edmunds	含M版宽度高点	可入库
BMW X5	BMW	越野车		SUV	Std.	gen1 SUV	2000-2006			183.7	73.7	67.5	2000-2006 BMW X5 3.0i / 4.4i 4dr SUV, Edmunds	初代SUV	可入库
BMW X5	BMW	越野车		SUV	Std.	gen2 SUV	2007-2013			191.1	76.1	69.9	2007-2013 BMW X5 3.0si / 4.8i / xDrive35i 4dr SUV, Edmunds	二代更高	可入库
BMW X5	BMW	越野车		SUV	Std.	gen3 SUV	2014-2018			193.2	76.3	69.4	2014-2018 BMW X5 xDrive35i / xDrive50i 4dr SUV, Edmunds	三代SUV	可入库
BMW X5	BMW	越野车		SUV	Std.	gen4 SUV	2019-2023			194.3	78.9	68.7	2019-2023 BMW X5 xDrive40i / M50i 4dr SUV, Edmunds	现款pre-facelift	可入库
BMW X5	BMW	越野车		SUV	Std.	gen4 facelift	2024-2026			194.3	78.9	69.5	2024-2026 BMW X5 xDrive40i / M60i 4dr SUV, Edmunds	现款facelift更高	可入库
4) 下一步优先核对

无待终核项；当前批次可进入下一批次。如果继续当前文件，建议只做尺码列/组合表合并校验，不再做尺寸补强。

本批次完成。

