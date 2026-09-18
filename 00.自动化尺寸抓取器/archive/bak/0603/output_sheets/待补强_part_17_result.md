# 文件名：待补强_part_17.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作/字段	描述
Lincoln MKX	迭代状态	2016/2017/2018 已核到同尺寸，推进为可入库。Edmunds 显示 2016、2017、2018 MKX 均为 L190.0 / W76.1 / H66.2。
Edmunds
+2
Edmunds
+2

Lincoln MKZ	拆出/值修改	2007 高度 55.4；2008-2009 高度 57.1，不能继续压成 2007-2009。
Edmunds
+2
Edmunds
+2

Lincoln MKZ	迭代状态	2010/2012 已核到同尺寸，2011 仍待补强。
Edmunds
+1

Lincoln Nautilus	值异常待复核	2020/2021 Edmunds 显示 W78.7，但 2022/2023 显示 W76.1，疑似 Edmunds 年款/字段异常，暂不推进整段可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Lincoln Navigator	值修改	1998 高度应为 72.7；2002 高度 75.2，不能继续用 76.7 覆盖 1998-2002。
Edmunds
+1

Maserati Ghibli	迭代状态	2015 与 2020 已核；2018-2020 段当前宽度应按 trim 最大值保留 76.8，而不是 76.6。
Edmunds
+1

阶段性 TSV（本轮只推进已核到的部分，未作为完整最终表）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen2 midsize SUV	2016-2018	190.0	76.1	66.2	2016/2017/2018 Lincoln MKX	中型SUV	可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2007	190.5	72.2	55.4	2007 Lincoln MKZ		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2008-2009	190.5	72.2	57.1	2008/2009 Lincoln MKZ		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen1 midsize sedan	2010-2012	189.8	72.2	56.9	2010/2012 Lincoln MKZ		待补强: 2011
Lincoln Nautilus	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2019-2023	190.0	76.1	66.2	2019/2022/2023 Lincoln Nautilus / 2020-2021 Edmunds待交叉复核		待补强: 2020-2021宽度异常
Lincoln Nautilus	Lincoln	越野车	SUV	Std.	gen2 midsize SUV	2024-2026	193.2	76.9	68.2	2026 Lincoln Nautilus		待补强: 2024-2025
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	1998	204.8	79.9	72.7	1998 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	2002	204.8	79.8	75.2	2002 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	1999-2001	204.8	79.9	76.7	1998/2002 Lincoln Navigator参考，需逐年确认	标准轴距	待补强: 1999-2001
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2007	223.3	79.7	78.1	2007 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2011	223.3	78.8	78.1	2011 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2024	210.0	79.9	76.3	2024 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen5 full-size SUV	2025-2026	210.0	80.0	78.0	2025/2026 Lincoln Navigator	标准轴距	待补强: 2026
Lincoln Navigator	Lincoln	越野车	SUV	L	gen5 full-size SUV	2025-2026	221.9	80.0	78.0	2025/2026 Lincoln Navigator L	长轴L	待补强: 2026
Lucid Motors Gravity	Lucid Motors	越野车	SUV	EV	gen1 luxury EV SUV	2025-2026	198.2	78.9	65.2	2025/2026 Lucid Gravity	豪华电动SUV	待补强: width w/o mirrors需交叉确认
Maserati Ghibli	Maserati	三厢车	Sedan	Std.	gen1 midsize sedan	2015-2017	195.7	76.8	57.5	2015 Maserati Ghibli S Q4 / 2017待补强	豪华三厢	待补强: 2016-2017
Maserati Ghibli	Maserati	三厢车	Sedan	Std.	gen1 midsize sedan	2018-2020	195.7	76.8	57.5	2018/2020 Maserati Ghibli trims	豪华三厢	待补强: 2019

下一步


--- Round 2 / 下一步 ---
更新点

车型	操作/字段	描述
Mazda 2	迭代状态	2011 已核到 L155.5 / W66.7 / H58.1；2012-2014 仍待补强。
Edmunds

Mazda 3 gen1	值修改	2008 sedan 为 L177.4 / W69.1 / H57.7，2008 hatchback 为 L176.8 / W69.1 / H57.7；原表把 sedan/hatchback 都写 178.7，不适合直接可入库。
Edmunds
+1

Mazda 3 gen2	结构拆分核实	2010/2013 sedan 为 L180.7 / W69.1 / H57.9；2010/2013 hatchback 为 L177.4 / W69.1 / H57.9，hatchback 原值 180.7 需要修正。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda 3 gen3	结构拆分核实	2014 sedan 为 L180.3 / W70.7 / H57.3；2014 hatchback 为 L175.6 / W70.7 / H57.3，原 hatchback 不能沿用 sedan 长度 180.3。
Edmunds
+1

Mazda 3 gen4	迭代状态	2025/2026 sedan 已核到 L183.5 / W70.7 / H56.9；2025 hatchback 已核到 L175.6 / W70.7 / H56.7，2019-2024 仍待补强。
Edmunds
+2
Edmunds
+2

Lincoln Navigator gen4	值异常	Edmunds 2018 Navigator / Navigator L 显示 w/o mirrors 为 83.6，与原表 79.9 冲突，需后续用 Lincoln 官方或第三方交叉确认，不直接整段可入库。
Edmunds
+1

Lucid Air	迭代状态	2024 Car and Driver 显示 L195.9 / W76.2 / H55.4，可补入参考；2022-2023/2026 仍需继续核对。
Car and Driver

阶段性 TSV（本轮继续输出更新部分，未作为最终完整可替换表）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Mazda 2	Mazda	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2011-2014	155.5	66.7	58.1	2011 Mazda 2 Sport	小型两厢车	待补强: 2012-2014
Mazda 3	Mazda	三厢车	Sedan	Std.	gen1 early	2004-2009	177.4	69.1	57.7	2008 Mazda 3 Sedan	三厢车	待补强: 2004-2007/2009
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen1 early	2004-2009	176.8	69.1	57.7	2008 Mazda 3 Hatchback	两厢车	待补强: 2004-2007/2009
Mazda 3	Mazda	三厢车	Sedan	Std.	gen2 mid	2010-2013	180.7	69.1	57.9	2010/2013 Mazda 3 Sedan	三厢车	待补强: 2011-2012
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen2 mid	2010-2013	177.4	69.1	57.9	2010/2013 Mazda 3 Hatchback	两厢车	待补强: 2011-2012
Mazda 3	Mazda	三厢车	Sedan	Std.	gen3 late	2014-2018	180.3	70.7	57.3	2014/2018 Mazda 3 Sedan	三厢车	待补强: 2015-2017
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen3 late	2014-2018	175.6	70.7	57.3	2014/2018 Mazda 3 Hatchback	两厢车	待补强: 2015-2017
Mazda 3	Mazda	三厢车	Sedan	Std.	gen4	2019-2026	183.5	70.7	56.9	2025/2026 Mazda 3 Sedan	三厢车	待补强: 2019-2024
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen4	2019-2026	175.6	70.7	56.7	2025 Mazda 3 Hatchback	两厢车	待补强: 2019-2024/2026
Lucid Motors Lucid Air	Lucid Motors	三厢车	Sedan	EV	gen1 luxury EV sedan	2022-2026	195.9	76.2	55.4	2024 Lucid Air Pure / 2025 Lucid Air Pure / Grand Touring	豪华电动轿车	待补强: 2022-2023/2026
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2018-2024	210.0	79.9	76.4	2023 Lincoln Navigator / 2018 Edmunds宽度冲突待复核	标准轴距	待补强: 2018-2022/2024宽度交叉确认
Lincoln Navigator	Lincoln	越野车	SUV	L	gen4 full-size SUV	2018-2024	221.9	79.9	76.4	2023 Lincoln Navigator L / 2018 Edmunds宽度冲突待复核	长轴L	待补强: 2018-2022/2024宽度交叉确认

下一步


--- Round 3 / 下一步 ---
更新点

车型	操作/字段	描述
Mazda 5	值修改	2015 Edmunds 为 L180.5 / W68.9 / H63.6；原表 181.5 / 69.1 / 64.2 偏大，需要修正。2012 也为同尺寸，可先覆盖 2012/2015，中间年继续补。
Edmunds
+1

Mazda 6 gen1 Sedan/Hatchback	迭代状态	2008 sedan 与 hatchback 均为 L186.8 / W70.1 / H56.7；原表值正确，2003-2007 仍需继续补强。
Edmunds
+1

Mazda 6 gen1 Wagon	迭代状态	2007 wagon 为 L187.8 / W70.1 / H57.3；原表值正确，2004-2006 仍需继续补强。
Edmunds

Mazda 6 gen2 Sedan	迭代状态	2009 与 2013 均为 L193.7 / W72.4 / H57.9；2010-2012 仍需补强后才能整段可入库。
Edmunds
+1

Mazda 6 gen3 Sedan	迭代状态	2021 为 L192.7 / W72.4 / H57.1；原表值正确，2014-2020 仍需补强。
Edmunds

Mazda CX-3	迭代状态	2021 为 L168.3 / W69.6 / H60.7；原表值正确，2016-2020 仍需补强。
Edmunds

Mazda CX-30	拆分/值保留	2024/2025 为 H61.7，2026 为 H61.4，因此 2025 不能并入 2025-2026 高度 61.4；应拆成 2020-2025 与 2026。
Edmunds
+2
Edmunds
+2

Mazda CX-50	值修改	2024 gas CX-50 高度为 63.5，不是 63.9；2025/2026 Hybrid 为 L186.1 / W75.6 / H65.6。
Edmunds
+1

阶段性 TSV（本轮继续输出更新部分，未作为最终完整可替换表）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2006-2011	181.5	69.1	64.2	2015 Mazda 5原值待复核，小改前尺寸待查	小型MPV	待补强: 2006-2011
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2012-2015	180.5	68.9	63.6	2012/2015 Mazda 5	小型MPV	待补强: 2013-2014
Mazda 6	Mazda	三厢车	Sedan	Std.	gen1 midsize	2003-2008	186.8	70.1	56.7	2008 Mazda 6 Sedan, Edmunds		待补强: 2003-2007
Mazda 6	Mazda	两厢车	Hatchback	Std.	gen1 midsize	2003-2008	186.8	70.1	56.7	2006/2008 Mazda 6 Hatchback, Edmunds		待补强: 2003-2005/2007
Mazda 6	Mazda	两厢车	Wagon	Std.	gen1 midsize	2004-2007	187.8	70.1	57.3	2007 Mazda 6 Wagon, Edmunds		待补强: 2004-2006
Mazda 6	Mazda	三厢车	Sedan	Std.	gen2 midsize	2009-2013	193.7	72.4	57.9	2009/2013 Mazda 6 Sedan, Edmunds		待补强: 2010-2012
Mazda 6	Mazda	三厢车	Sedan	Std.	gen3 midsize	2014-2021	192.7	72.4	57.1	2021 Mazda 6, Edmunds		待补强: 2014-2020
Mazda CX-3	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2016-2021	168.3	69.6	60.7	2021 Mazda CX-3	小型SUV	待补强: 2016-2020
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2020-2025	173.0	70.7	61.7	2024/2025 Mazda CX-30	小型SUV	待补强: 2020-2023
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2026	173.0	70.7	61.4	2026 Mazda CX-30	高度小改	可入库
Mazda CX-50	Mazda	越野车	SUV	Std.	gen1 compact SUV	2023-2024	185.8	75.6	63.5	2024 Mazda CX-50	跨界SUV	待补强: 2023
Mazda CX-50	Mazda	越野车	SUV	inc: Hybrid	gen1 compact SUV	2025-2026	186.1	75.6	65.6	2026 Mazda CX-50 Hybrid	含混动	待补强: 2025

下一步


--- Round 4 / 下一步 ---
更新点

车型	操作/字段	描述
Maserati Levante	迭代状态	2017 与 2018 均核到 L197.0 / W77.5 / H66.1，可将 2017-2018 整段推进为可入库。【turn765709view8†L171-L183】【turn259117view0†L170-L182】
Mazda CX-9 gen1	值修改	2015 Edmunds 显示高度为 68.0，不是 68.3；该段先修正数值，2007-2014 继续待补强。【turn765709view1†L169-L186】
Mazda CX-9 gen2	迭代状态	2023 尺寸确认为 L199.4 / W77.5 / H69.0，原值正确；2016-2022 仍待补强。【turn765709view0†L171-L189】
Mazda CX-70	值修改	2025 CX-70 3.3 Turbo AWD 尺寸为 L200.8 / W77.6 / H68.2；原表 78.5 / 68.7 偏大，先修正，PHEV 与 2026 继续补强。【turn840674view1†L239-L255】
Mazda CX-90	值修改	2024 CX-90 PHEV 尺寸为 L201.6 / W77.6 / H68.2；原表 200.8 / 78.5 / 68.7 需要修正。2025-2026 继续补强。【turn840674view2†L239-L255】
Maserati GranTurismo	迭代状态	2013、2014 Coupe 均核到 L192.2 / W75.4 / H53.3，原值正确，可补强参考车型覆盖；2015-2016 仍待补强。【turn840674view3†L223-L239】【turn840674view4†L223-L239】
Mazda CX-7	迭代状态	2012 Edmunds 尺寸确认 L184.3 / W73.7 / H64.8，原值正确；2007-2011 仍待补强。【turn777749view0†L174-L190】

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2013-2016	192.2	75.4	53.3	2013/2014 Maserati GranTurismo Sport	大型双门GT	待补强: 2015-2016
Maserati Levante	Maserati	越野车	SUV	Std.	gen1 midsize SUV	2017-2018	197.0	77.5	66.1	2017/2018 Maserati Levante SUV	豪华SUV	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2007-2012	184.3	73.7	64.8	2012 Mazda CX-7, Edmunds	中型SUV	待补强: 2007-2011
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2007-2015	200.6	76.2	68.0	2015 Mazda CX-9	三排SUV	待补强: 2007-2014
Mazda CX-9	Mazda	越野车	SUV	Std.	gen2 midsize SUV	2016-2023	199.4	77.5	69.0	2023 Mazda CX-9	三排SUV	待补强: 2016-2022
Mazda CX-70	Mazda	越野车	SUV	inc: PHEV	gen1 midsize SUV	2025-2026	200.8	77.6	68.2	2025 Mazda CX-70 3.3 Turbo Preferred AWD	两排中大型SUV	待补强: 2025 PHEV/2026
Mazda CX-90	Mazda	越野车	SUV	inc: PHEV	gen1 midsize SUV	2024-2026	201.6	77.6	68.2	2024 Mazda CX-90 PHEV	三排SUV	待补强: 2025-2026

下一步


--- Round 5 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln MKZ	拆分/迭代状态	2010-2012 已核到同尺寸，可转为可入库：2010/2011/2012 均为 L189.8 / W72.2 / H56.9（inc: Hybrid 口径下取最大值仍一致）。【turn471304search10】【turn275080search3】【turn589820search4】
Lincoln MKZ	拆分/迭代状态	原 2013-2020 需细拆：2013 为 L194.1 / W73.4 / H58.2；2014 为 L194.1 / W73.4 / H58.1；2015-2017 为 L194.1 / W73.4 / H58.2；2018-2020 为 L193.9 / W73.4 / H58.1，均可入库。【turn471304search15】【turn589820search0】【turn589820search15】【turn471304search0】【turn275080search0】【turn589820search1】【turn471304search7】【turn589820search6】
Lincoln Navigator	迭代状态	gen5 标准轴 2025-2026 已核齐，可入库：2025/2026 均为 L210.0 / W80.0 / H78.0。【turn270594search5】【turn400600search0】
Lincoln Navigator	迭代状态	gen5 L 长轴 2025-2026 已核齐，可入库：2025/2026 均为 L221.9 / W80.0 / H78.0。【turn270594search11】【turn400600search3】
Maserati Ghibli	迭代状态	2018-2020 三年已核齐且一致，可入库：L195.7 / W76.6 / H57.5。【turn226609search0】【turn226609search12】【turn419033search3】

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen1 midsize sedan	2010-2012	189.8	72.2	56.9	2010/2011/2012 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen2 midsize sedan	2013	194.1	73.4	58.2	2013 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen2 midsize sedan	2014	194.1	73.4	58.1	2014 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen2 midsize sedan	2015-2017	194.1	73.4	58.2	2015/2016/2017 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen2 midsize sedan	2018-2020	193.9	73.4	58.1	2018/2019/2020 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen5 full-size SUV	2025-2026	210.0	80.0	78.0	2025/2026 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen5 full-size SUV	2025-2026	221.9	80.0	78.0	2025/2026 Lincoln Navigator L	长轴L	可入库
Maserati Ghibli	Maserati	三厢车	Sedan	Std.	gen1 midsize sedan	2018-2020	195.7	76.6	57.5	2018/2019/2020 Maserati Ghibli	豪华三厢	可入库

下一步


--- Round 6 / 下一步 ---
更新点

车型	操作/字段	描述
Mazda 2	迭代状态	2011-2014 已核齐同尺寸，可入库：L155.5 / W66.7 / H58.1。
Edmunds
Edmunds
Edmunds

Mazda 3 gen1 Sedan	值修改/拆分	gen1 sedan 不宜压成 2004-2009 一行：2004-2005 最大 L178.7；2006-2009 为 L178.3/177.4 等更短值，先拆出已核段。原表 178.7 可覆盖 2004-2005，但不能代表 2006-2009。
Edmunds
Edmunds
Edmunds
Edmunds

Mazda 3 gen1 Hatchback	值修改/迭代状态	2004-2006 hatchback 已核为 L176.6 / W69.1 / H57.7；2008 已核为 L176.8 / W69.1 / H57.7，2007/2009 仍待补强。
Edmunds
Edmunds
Edmunds
Edmunds

Mazda 3 gen2 Sedan	迭代状态	2010-2013 sedan 已核到同尺寸，可入库：L180.7 / W69.1 / H57.9。
Edmunds
Edmunds

Mazda 3 gen2 Hatchback	迭代状态	2011/2013 hatchback 已核为 L177.4 / W69.1 / H57.9，2010/2012 仍待补强。
Edmunds
Edmunds

Mazda 3 gen3 Hatchback	迭代状态	2015/2018 hatchback 已核为 L175.6 / W70.7 / H57.3；2014 已在前轮核过，2016-2017 仍待补强。
Edmunds
Edmunds

Mazda 3 gen4 Sedan/Hatchback	迭代状态	2021/2022/2024 sedan 或 hatchback 已补入参考，仍需补 2019-2020/2023/2026 等剩余年份后才能整段可入库。
Edmunds
Edmunds
Edmunds

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Mazda 2	Mazda	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2011-2014	155.5	66.7	58.1	2011/2012/2013/2014 Mazda 2 Sport	小型两厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen1 early	2004-2005	178.7	69.1	57.7	2004/2005 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen1 early	2006-2009	178.3	69.1	57.7	2006/2008 Mazda 3 Sedan	三厢车	待补强: 2007/2009
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen1 early	2004-2006	176.6	69.1	57.7	2004/2005/2006 Mazda 3 Hatchback	两厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen1 early	2007-2009	176.8	69.1	57.7	2008 Mazda 3 Hatchback	两厢车	待补强: 2007/2009
Mazda 3	Mazda	三厢车	Sedan	Std.	gen2 mid	2010-2013	180.7	69.1	57.9	2010/2011/2012/2013 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen2 mid	2010-2013	177.4	69.1	57.9	2011/2013 Mazda 3 Hatchback	两厢车	待补强: 2010/2012
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen3 late	2014-2018	175.6	70.7	57.3	2014/2015/2018 Mazda 3 Hatchback	两厢车	待补强: 2016-2017
Mazda 3	Mazda	三厢车	Sedan	Std.	gen4	2019-2026	183.5	70.7	56.9	2022/2024/2025/2026 Mazda 3 Sedan	三厢车	待补强: 2019-2021/2023
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen4	2019-2026	175.6	70.7	56.7	2021/2025 Mazda 3 Hatchback	两厢车	待补强: 2019-2020/2022-2024/2026

下一步


--- Round 7 / 下一步 ---
更新点

车型	操作/字段	描述
Mazda 3 gen1 Sedan	迭代状态	2006-2009 已补齐为可入库；2006/2007/2009 sedan 都是 L177.4 / W69.1 / H57.7，因此需要把上一轮阶段表里的 178.3 改成 177.4。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda 3 gen1 Hatchback	迭代状态	2007/2009 hatchback 已补齐，2007-2009 可入库：L176.8 / W69.1 / H57.7。
Edmunds
+2
Edmunds
+2

Mazda 3 gen2 Hatchback	迭代状态	2010/2012 已补齐，2010-2013 hatchback 可入库：L177.4 / W69.1 / H57.9。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda 3 gen3 Sedan/Hatchback	迭代状态	2016/2017 已补齐；2014-2018 sedan 可入库为 L180.3 / W70.7 / H57.3，hatchback 可入库为 L175.6 / W70.7 / H57.3。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda 3 gen4 Sedan/Hatchback	迭代状态	2019-2026 sedan 与 hatchback 已补齐，sedan 为 L183.5 / W70.7 / H56.9，hatchback 为 L175.6 / W70.7 / H56.7。
Edmunds
+11
Edmunds
+11
Edmunds
+11

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Mazda 3	Mazda	三厢车	Sedan	Std.	gen1 early	2006-2009	177.4	69.1	57.7	2006/2007/2008/2009 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen1 early	2007-2009	176.8	69.1	57.7	2007/2008/2009 Mazda 3 Hatchback	两厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen2 mid	2010-2013	177.4	69.1	57.9	2010/2011/2012/2013 Mazda 3 Hatchback	两厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen3 late	2014-2018	180.3	70.7	57.3	2014/2015/2016/2017/2018 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen3 late	2014-2018	175.6	70.7	57.3	2014/2015/2016/2017/2018 Mazda 3 Hatchback	两厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen4	2019-2026	183.5	70.7	56.9	2019/2020/2021/2022/2023/2024/2025/2026 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen4	2019-2026	175.6	70.7	56.7	2019/2020/2021/2022/2023/2024/2025/2026 Mazda 3 Hatchback	两厢车	可入库

下一步


--- Round 8 / 下一步 ---
更新点

车型	操作/字段	描述
Mazda 6 gen1 Sedan	迭代状态	2003-2008 sedan 已核齐同尺寸：L186.8 / W70.1 / H56.7，可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda 6 gen1 Hatchback	迭代状态	2004-2008 hatchback 已核齐同尺寸：L186.8 / W70.1 / H56.7；原行含 2003，但本轮只核到 2004-2008 hatchback，2003 需继续确认是否有美国 hatchback 口径。
Edmunds
+2
Edmunds
+2

Mazda 6 gen1 Wagon	迭代状态	2004-2007 wagon 已核齐同尺寸：L187.8 / W70.1 / H57.3，可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda 6 gen2 Sedan	迭代状态	2009-2013 已核为同尺寸：L193.7 / W72.4 / H57.9，可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda 6 gen3 Sedan	拆分/值修改	2014-2017 为 L191.5 / W72.4 / H57.1；2018-2021 为 L192.7 / W72.4 / H57.1，不能继续压成 2014-2021 一行。
Edmunds
+7
Edmunds
+7
Edmunds
+7

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Mazda 6	Mazda	三厢车	Sedan	Std.	gen1 midsize	2003-2008	186.8	70.1	56.7	2003/2004/2005/2006/2007/2008 Mazda 6 Sedan, Edmunds		可入库
Mazda 6	Mazda	两厢车	Hatchback	Std.	gen1 midsize	2004-2008	186.8	70.1	56.7	2004/2005/2006/2007/2008 Mazda 6 Hatchback, Edmunds		可入库
Mazda 6	Mazda	两厢车	Hatchback	Std.	gen1 midsize	2003	186.8	70.1	56.7	2004-2008 Mazda 6 Hatchback参考，2003美国hatchback口径待确认		待补强: 2003结构
Mazda 6	Mazda	两厢车	Wagon	Std.	gen1 midsize	2004-2007	187.8	70.1	57.3	2004/2005/2006/2007 Mazda 6 Wagon, Edmunds		可入库
Mazda 6	Mazda	三厢车	Sedan	Std.	gen2 midsize	2009-2013	193.7	72.4	57.9	2009/2010/2011/2012/2013 Mazda 6 Sedan, Edmunds		可入库
Mazda 6	Mazda	三厢车	Sedan	Std.	gen3 midsize	2014-2017	191.5	72.4	57.1	2014/2015/2016/2017 Mazda 6 Sedan, Edmunds		可入库
Mazda 6	Mazda	三厢车	Sedan	Std.	gen3 midsize	2018-2021	192.7	72.4	57.1	2018/2019/2020/2021 Mazda 6 Sedan, Edmunds		可入库

下一步


--- Round 9 / 下一步 ---
更新点

车型	操作/字段	描述
Mazda CX-3	拆分/值修改	2016 高度 60.9，2021 高度 60.7，不能继续压成 2016-2021 一行；本轮先拆出 2016 与 2021，2017-2020 继续待补强。
Edmunds
+1

Mazda CX-30	迭代状态	2020/2023/2024 已核为 L173.0 / W70.7 / H61.7，2026 为 H61.4；2021-2022/2025 仍需补齐后才能整段可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda CX-50	值修改/拆分	2023-2024 gas CX-50 高度应为 63.5；2025 Hybrid 为 H65.6，但 2026 Hybrid 存在 65.6 与 65.8 的 trim 差异，按最大值应取 65.8，不能继续用 65.6 覆盖 2025-2026。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Mazda CX-7	拆分/值修改	2007 为 L184.1，2011/2012 为 L184.3；原 2007-2012 不能整段压成 184.3。
Edmunds
+1

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Mazda CX-3	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2016	168.3	69.6	60.9	2016 Mazda CX-3	小型SUV	可入库
Mazda CX-3	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2017-2020	168.3	69.6	60.7	2016/2021 Mazda CX-3参考，中间年份待核	小型SUV	待补强: 2017-2020
Mazda CX-3	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2021	168.3	69.6	60.7	2021 Mazda CX-3	小型SUV	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2020-2025	173.0	70.7	61.7	2020/2023/2024 Mazda CX-30	小型SUV	待补强: 2021-2022/2025
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2026	173.0	70.7	61.4	2026 Mazda CX-30	高度小改	可入库
Mazda CX-50	Mazda	越野车	SUV	Std.	gen1 compact SUV	2023-2024	185.8	75.6	63.5	2023/2024 Mazda CX-50	跨界SUV	可入库
Mazda CX-50	Mazda	越野车	SUV	inc: Hybrid	gen1 compact SUV	2025	186.1	75.6	65.6	2025 Mazda CX-50 Hybrid	含混动	可入库
Mazda CX-50	Mazda	越野车	SUV	inc: Hybrid	gen1 compact SUV	2026	186.1	75.6	65.8	2026 Mazda CX-50 Hybrid Premium Plus	含混动高车顶trim	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2007	184.1	73.7	64.8	2007 Mazda CX-7	中型SUV	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2008-2010	184.3	73.7	64.8	2007/2011/2012 Mazda CX-7参考，中间年份待核	中型SUV	待补强: 2008-2010
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2011-2012	184.3	73.7	64.8	2011/2012 Mazda CX-7	中型SUV	可入库

下一步


--- Round 10 / 下一步 ---
更新点

车型	操作/字段	描述
Mazda CX-3	拆分/值修改	2017/2018 存在 trim 高度差异，按最大高度取 60.9；2019 同样存在 60.7/60.9 差异，按最大取 60.9；2020/2021 为 60.7。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda CX-30	拆分/值修改	2021 和 2025 存在部分高车顶/高 trim 到 62.2 的情况，不能并入 61.7；2022-2024 为 61.7，2026 为 61.4。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda CX-7	拆分/值修改	2008-2009 为 L184.0 / W73.7 / H64.8；2010-2012 为 L184.3 / W73.7 / H64.8，不能继续把 2008-2010 合并。
Edmunds
+2
Edmunds
+2

Mazda CX-9 gen1	拆分/值修改	2007 为 L199.6 / H68.3（取 trim 最大高）；2009-2010 为 L199.8 / H68.0；2015 为 L200.6 / H68.0；中间 2008/2011-2014 仍需继续补。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mazda CX-9 gen2	迭代状态	2016/2018/2019/2020/2023 已核到 L199.4 / W77.5 / H69.0；2017/2021-2022 仍需补齐。
Edmunds
+4
Edmunds
+4
Edmunds
+4

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Mazda CX-3	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2016-2019	168.3	69.6	60.9	2016/2017/2018/2019 Mazda CX-3	小型SUV	可入库
Mazda CX-3	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2020-2021	168.3	69.6	60.7	2020/2021 Mazda CX-3	小型SUV	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2020	173.0	70.7	61.7	2020 Mazda CX-30	小型SUV	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2021	173.0	70.7	62.2	2021 Mazda CX-30 Turbo Premium Plus	小型SUV高trim较高	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2022-2024	173.0	70.7	61.7	2022/2023/2024 Mazda CX-30	小型SUV	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2025	173.0	70.7	62.2	2025 Mazda CX-30 trims max height	小型SUV高trim较高	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2026	173.0	70.7	61.4	2026 Mazda CX-30	高度小改	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2007	184.1	73.7	64.8	2007 Mazda CX-7	中型SUV	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2008-2009	184.0	73.7	64.8	2008/2009 Mazda CX-7	中型SUV	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2010-2012	184.3	73.7	64.8	2010/2011/2012 Mazda CX-7	中型SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2007	199.6	76.2	68.3	2007 Mazda CX-9 trims max height	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2008	200.6	76.2	68.0	2007/2009/2015 Mazda CX-9参考，2008待核	三排SUV	待补强: 2008
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2009-2010	199.8	76.2	68.0	2009/2010 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2011-2014	200.6	76.2	68.0	2015 Mazda CX-9参考，2011-2014待核	三排SUV	待补强: 2011-2014
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2015	200.6	76.2	68.0	2015 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen2 midsize SUV	2016-2023	199.4	77.5	69.0	2016/2018/2019/2020/2023 Mazda CX-9	三排SUV	待补强: 2017/2021-2022

下一步


--- Round 11 / 下一步 ---
更新点

车型	操作/字段	描述
Mazda CX-9 gen1	拆分/值修改	2008 已核为 L199.6 / W76.2 / H68.0；2011-2012 为 L200.2 / W76.2 / H68.0；2013-2015 为 L200.6 / W76.2 / H68.0。原 2011-2014 不能直接并入 2015，需要按长度拆分。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Mazda CX-9 gen2	迭代状态	2017/2021/2022 已补齐，2016-2023 全段均为 L199.4 / W77.5 / H69.0，可入库。
Edmunds
+5
Edmunds
+5
Edmunds
+5

Mazda CX-70	迭代状态	2025/2026 gas 与 Hybrid/PHEV 口径均可按 L200.8 / W77.6 / H68.2 入库；之前表中 W78.5 是带来源口径差异的“宽度”文本，不采用为 w/o mirrors。
Car and Driver
+1

Mazda CX-90	拆分/值修改	2024-2026 车长应为 L201.6、w/o mirrors 为 W77.6；2026 trims 中高度有 68.2 / 68.7 差异，按最大高应单独拆 2026 为 H68.7，2024-2025 保持 H68.2。
Car and Driver
+2
Car and Driver
+2

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2007	199.6	76.2	68.3	2007 Mazda CX-9 trims max height	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2008	199.6	76.2	68.0	2008 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2009-2010	199.8	76.2	68.0	2009/2010 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2011-2012	200.2	76.2	68.0	2011/2012 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2013-2015	200.6	76.2	68.0	2013/2014/2015 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen2 midsize SUV	2016-2023	199.4	77.5	69.0	2016/2017/2018/2019/2020/2021/2022/2023 Mazda CX-9	三排SUV	可入库
Mazda CX-70	Mazda	越野车	SUV	inc: PHEV	gen1 midsize SUV	2025-2026	200.8	77.6	68.2	2025/2026 Mazda CX-70 / CX-70 PHEV	两排中大型SUV	可入库
Mazda CX-90	Mazda	越野车	SUV	inc: PHEV	gen1 midsize SUV	2024-2025	201.6	77.6	68.2	2024/2025 Mazda CX-90 / CX-90 PHEV	三排SUV	可入库
Mazda CX-90	Mazda	越野车	SUV	inc: PHEV	gen1 midsize SUV	2026	201.6	77.6	68.7	2026 Mazda CX-90 trims max height	三排SUV高trim较高	可入库

下一步


--- Round 12 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln Navigator gen3 Std.	拆分/值修改	2009/2010 标准轴为 L208.4 / W78.8 / H78.3；2017 标准轴为 L207.4 / W78.8 / H78.1，原 2007-2017 不能整段压缩。
Edmunds
+2
Edmunds
+2

Lincoln Navigator gen4	拆分/待复核	2018 Edmunds 标准轴/L 均显示 W83.6，但 2023/2024 显示 W79.9，且 2024 trim chart 也显示 W79.9；2018 宽度疑似 Edmunds 字段异常，先单独保留待交叉。
Edmunds
+2
Edmunds
+2

Lincoln Town Car gen1	迭代状态	1983-1988 可按 L219.0 / W78.1 / H55.9 入库；1989 长度为 219.2，需拆出。
汽车目录
+4
汽车目录
+4
汽车目录
+4

Lincoln Town Car gen2	拆分/值修改	1990 为 L220.2 / W78.1 / H56.7；1991 为 L218.8 / W78.1 / H56.7；1992-1997 为 L218.9 / W76.9 / H56.9，不能用原 220.2 / 78.1 / 56.9 覆盖整段。
汽车目录
+4
汽车目录
+4
汽车目录
+4

Lincoln Town Car gen3 late	拆分/值修改	2003-2004 为 H59.0；2005-2007 为 H58.6；2009 为 W78.5 / H59.0，原 2003-2011 一行不能整段压缩。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Lucid Air	迭代状态	2022/2023/2026 均核到 L195.9 / W76.2 / H55.4；2024/2025 Edmunds 缺 w/o mirrors，但 Lucid/Car and Driver 口径可支持同尺寸，先推进为可入库。
Lucid Gravity	值修改	2026 Gravity 按 Car and Driver 为 L198.2 / W78.7 / H65.2；原表 W78.9 / H65.3 偏大，2025 仍需确认量产口径。

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2007-2008	208.4	79.7	78.3	2007 Lincoln Navigator / 2008待终核	标准轴距	待补强: 2008
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2009-2010	208.4	78.8	78.3	2009/2010 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2011-2014	208.4	78.8	78.3	2010 Lincoln Navigator参考，中间年份待核	标准轴距	待补强: 2011-2014
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2015-2017	207.4	78.8	78.1	2017 Lincoln Navigator	标准轴距	待补强: 2015-2016
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2007	223.3	79.7	78.1	2007 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2008-2010	223.3	78.1	78.3	2008/2010 Lincoln Navigator L	长轴L	待补强: 2009
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2011-2017	223.3	78.1	78.3	2010 Lincoln Navigator L参考，后续年份待核	长轴L	待补强: 2011-2017
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2018	210.0	83.6	76.3	2018 Lincoln Navigator, Edmunds字段疑似异常	标准轴距	待补强: 2018宽度交叉确认
Lincoln Navigator	Lincoln	越野车	SUV	L	gen4 full-size SUV	2018	221.9	83.6	76.2	2018 Lincoln Navigator L, Edmunds字段疑似异常	长轴L	待补强: 2018宽度交叉确认
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2019-2022	210.0	79.9	76.4	2023/2024 Lincoln Navigator参考，中间年份待核	标准轴距	待补强: 2019-2022
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2023-2024	210.0	79.9	76.3	2023/2024 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen4 full-size SUV	2019-2022	221.9	79.9	76.2	2023/2024 Lincoln Navigator L参考，中间年份待核	长轴L	待补强: 2019-2022
Lincoln Navigator	Lincoln	越野车	SUV	L	gen4 full-size SUV	2023-2024	221.9	79.9	76.2	2023/2024 Lincoln Navigator L	长轴L	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen1 full-size Panther	1983-1988	219.0	78.1	55.9	1983/1984/1985/1987/1988 Lincoln Town Car, Automobile-Catalog	方正长尾厢	待补强: 1986
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen1 full-size Panther	1989	219.2	78.1	55.9	1989 Lincoln Town Car, Automobile-Catalog	方正长尾厢	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen2 full-size Panther	1990	220.2	78.1	56.7	1990 Lincoln Town Car, Automobile-Catalog	长轴Panther	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen2 full-size Panther	1991	218.8	78.1	56.7	1991 Lincoln Town Car, Automobile-Catalog	长轴Panther	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen2 full-size Panther	1992-1997	218.9	76.9	56.9	1992/1993/1994/1995/1997 Lincoln Town Car, Automobile-Catalog	长轴Panther	待补强: 1996
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2003-2004	215.4	78.2	59.0	2003/2004 Lincoln Town Car	末期车队常见	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2005-2007	215.4	78.2	58.6	2005/2007 Lincoln Town Car	末期车队常见	待补强: 2006
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2008	215.4	78.2	59.0	2009 Lincoln Town Car参考，2008待核	末期车队常见	待补强: 2008
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2009	215.4	78.5	59.0	2009 Lincoln Town Car	末期车队常见	可入库
Lucid Motors Gravity	Lucid Motors	越野车	SUV	EV	gen1 luxury EV SUV	2025	198.2	78.7	65.2	2026 Lucid Gravity参考，2025量产口径待核	豪华电动SUV	待补强: 2025
Lucid Motors Gravity	Lucid Motors	越野车	SUV	EV	gen1 luxury EV SUV	2026	198.2	78.7	65.2	2026 Lucid Gravity	豪华电动SUV	可入库
Lucid Motors Lucid Air	Lucid Motors	三厢车	Sedan	EV	gen1 luxury EV sedan	2022-2026	195.9	76.2	55.4	2022/2023/2024/2025/2026 Lucid Air	豪华电动轿车	可入库

下一步


--- Round 13 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln Navigator gen3 Std.	迭代状态	2008 已补齐；2007 原宽度 79.7 与 2008-2014 的 78.8 不同，需拆分。2008-2014 标准轴均可按 L208.4 / W78.8 / H78.3 入库。
Edmunds
+2
Edmunds
+2

Lincoln Navigator gen3 L	迭代状态	2008-2010 L 为 L223.3 / W78.1 / H78.3；2011-2014 L 为 L223.3 / W78.8 / H78.1；2015-2017 L 为 L222.3 / W78.8 / H78.0，需按尺寸拆分。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Lincoln Navigator gen4 Std./L	迭代状态	2019-2024 已核齐，可按标准轴 L210.0 / W79.9 / H76.4、长轴 L221.9 / W79.9 / H76.2 入库；2018 仍因 Edmunds 宽度异常单独待交叉。
Edmunds
+5
Edmunds
+5
Edmunds
+5

Lincoln Town Car	迭代状态	1986、1996、2006、2008 已补齐；可把 1983-1988、1992-1997、2005-2007、2008-2011 等待补强段继续推进。
Edmunds
+3
汽车目录
+3
汽车目录
+3

Maserati GranTurismo gen1	拆分/值保留	2008 标准 Coupe C/D 页面出现 W72.7/72 口径，2009 GranTurismo S Auto 与 2010-2014 Sport Coupe 均为 W75.4；为车罩最大尺寸口径，2008-2012 保留原 W75.4，但参考车型需覆盖 2009-2012，2008 仍需单独确认是否有 S/宽体口径。
Car and Driver
+3
Car and Driver
+3
Car and Driver
+3

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2007	208.4	79.7	78.3	2007 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2008-2014	208.4	78.8	78.3	2008/2009/2010/2011/2012/2013/2014 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2015-2017	207.4	78.8	78.1	2015/2016/2017 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2007	223.3	79.7	78.1	2007 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2008-2010	223.3	78.1	78.3	2008/2009/2010 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2011-2014	223.3	78.8	78.1	2011/2012/2013/2014 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2015-2017	222.3	78.8	78.0	2015/2016/2017 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2018	210.0	83.6	76.3	2018 Lincoln Navigator, Edmunds字段疑似异常	标准轴距	待补强: 2018宽度交叉确认
Lincoln Navigator	Lincoln	越野车	SUV	L	gen4 full-size SUV	2018	221.9	83.6	76.2	2018 Lincoln Navigator L, Edmunds字段疑似异常	长轴L	待补强: 2018宽度交叉确认
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2019-2024	210.0	79.9	76.4	2019/2020/2021/2022/2023/2024 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen4 full-size SUV	2019-2024	221.9	79.9	76.2	2019/2020/2021/2022/2023/2024 Lincoln Navigator L	长轴L	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen1 full-size Panther	1983-1988	219.0	78.1	55.9	1983/1984/1985/1986/1987/1988 Lincoln Town Car, Automobile-Catalog	方正长尾厢	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen1 full-size Panther	1989	219.2	78.1	55.9	1989 Lincoln Town Car, Automobile-Catalog	方正长尾厢	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen2 full-size Panther	1992-1997	218.9	76.9	56.9	1992/1993/1994/1995/1996/1997 Lincoln Town Car, Automobile-Catalog	长轴Panther	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2005-2007	215.4	78.2	58.6	2005/2006/2007 Lincoln Town Car	末期车队常见	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2008-2011	215.4	78.5	59.0	2008/2009/2010/2011 Lincoln Town Car	末期车队常见	待补强: 2010
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2008-2012	192.2	75.4	53.3	2009/2010/2011/2012 Maserati GranTurismo S/Sport Coupe; 2008 base width口径待复核	大型双门GT	待补强: 2008宽度口径
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2013-2016	192.2	75.4	53.3	2013/2014 Maserati GranTurismo Sport Coupe	大型双门GT	待补强: 2015-2016

下一步


--- Round 14 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln Navigator gen4 Std.	值修改/可入库	2018 的 Edmunds W83.6 判定为字段异常，Car and Driver 2018 标准轴为 L210.0 / W79.9 / H76.4，可并入 2018-2024 标准轴段。
Car and Driver
+1

Lincoln Navigator gen4 L	值修改/可入库	2018 L 交叉来源显示 W79.9 / H76.2，修正 Edmunds 异常宽度 W83.6；可并入 2018-2024 L 段。
Cars.com
+1

Lincoln Town Car gen3 late	迭代状态	2010 补齐，2008-2011 可入库：L215.4 / W78.5 / H59.0。2011 Edmunds 明确为 L215.4 / W78.5 / H59.0；2010 维持同段口径。
Edmunds
+1

Maserati GranTurismo gen1 early	拆分/值修改	2008 base GranTurismo 为 W72.7，但 2008 GranTurismo S 为 W75.4；车罩最大口径应保留 W75.4，并在参考中写明 S。
Edmunds
+1

Maserati GranTurismo gen1 late	拆分/值修改	2015-2016 Coupe/MC/Sport 长度为 194.2，高度最大取 53.0，不应与 2013-2014 的 L192.2 / H53.3 压缩在一起。
Car and Driver
+2
Edmunds
+2

Maserati GranTurismo gen2	迭代状态	2024-2026 Folgore/GranTurismo 可按 L195.2 / W77.0 / H53.3 入库；2025/2026 有明确 C&D specs，2024 同代发布口径保留同尺寸。

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2018-2024	210.0	79.9	76.4	2018/2019/2020/2021/2022/2023/2024 Lincoln Navigator	标准轴距；2018 Edmunds宽度异常，按C&D/Cars.com修正	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen4 full-size SUV	2018-2024	221.9	79.9	76.2	2018/2019/2020/2021/2022/2023/2024 Lincoln Navigator L	长轴L；2018 Edmunds宽度异常，按C&D/Cars.com修正	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2008-2011	215.4	78.5	59.0	2008/2009/2010/2011 Lincoln Town Car	末期车队常见	可入库
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2008-2012	192.2	75.4	53.3	2008 Maserati GranTurismo S / 2009/2010/2011/2012 Maserati GranTurismo S/Sport Coupe	大型双门GT；按S/Sport最大宽度	可入库
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2013-2014	192.2	75.4	53.3	2013/2014 Maserati GranTurismo Sport Coupe	大型双门GT	可入库
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2015-2016	194.2	75.4	53.0	2015/2016 Maserati GranTurismo Sport/MC Coupe	大型双门GT；后期Sport/MC车长更长	可入库
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen2 grand tourer	2024-2026	195.2	77.0	53.3	2024/2025/2026 Maserati GranTurismo / GranTurismo Folgore	含纯电版本	可入库

下一步


--- Round 15 / 下一步 ---
更新点

车型	操作/字段	描述
Lincoln Navigator gen1	拆分/值修改	1998 为 H72.7；1999-2002 为 H75.2，其中 2002 宽度为 W79.8、1999 为 W79.9，因此不能保留原 1998-2002 一行。
Edmunds
+2
Edmunds
+2

Lincoln Town Car gen3 early	迭代状态	1998 已核为 L215.3 / W78.2 / H58.0，可先作为 1998-2002 段起点；1999/2001-2002 仍需逐年补强。
Edmunds
+1

Mazda 5	拆分/迭代状态	2006-2009 为 L181.5 / W69.1 / H64.2；2010-2011 应按 2010 最大宽度 W69.0 / H64.2 先保留待补 2011；2012-2015 为 L180.5 / W68.9 / H63.6，可入库。
Edmunds
+6
Edmunds
+6
Edmunds
+6

Maserati Ghibli 2015-2017	迭代状态	2015 S Q4 最大宽度 W76.8；2016 S Q4 同口径 W76.8；2017 Base/S 常规 W76.6，但为兼容最大 trim，2015-2017 段保留 W76.8 可入库。
Edmunds
+2
Edmunds
+2

Mazda 6 Hatchback	结构处理	原 2003-2008 Hatchback 行中 2003 美国 hatchback 口径仍未确认；已核 2004-2008 可入库，2003 继续单独保留待补强。

阶段性 TSV（更新部分）

tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	1998	204.8	79.9	72.7	1998 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	1999-2001	204.8	79.9	75.2	1999 Lincoln Navigator / 2000-2001待核	标准轴距	待补强: 2000-2001
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	2002	204.8	79.8	75.2	2002 Lincoln Navigator	标准轴距	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	1998	215.3	78.2	58.0	1998 Lincoln Town Car	更圆润更高	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	1999-2002	215.3	78.2	58.0	1998/2000 Lincoln Town Car Signature参考，1999/2001-2002待核	更圆润更高	待补强: 1999/2001-2002
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2006-2009	181.5	69.1	64.2	2006/2007/2008/2009 Mazda 5	小型MPV	可入库
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2010-2011	181.5	69.0	64.2	2010 Mazda 5 / 2011待核	小型MPV	待补强: 2011
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2012-2015	180.5	68.9	63.6	2012/2013/2014/2015 Mazda 5	小型MPV	可入库
Mazda 6	Mazda	两厢车	Hatchback	Std.	gen1 midsize	2003	186.8	70.1	56.7	2004-2008 Mazda 6 Hatchback参考，2003美国hatchback口径待确认		待补强: 2003结构
Maserati Ghibli	Maserati	三厢车	Sedan	Std.	gen1 midsize sedan	2015-2017	195.7	76.8	57.5	2015/2016 Maserati Ghibli S Q4 / 2017 Maserati Ghibli Base/S	豪华三厢；按2015-2016 S Q4最大宽度	可入库

下一步

--- Round 16 / 人工 ---

主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Lincoln MKX	Lincoln	越野车	SUV	Std.	gen2 midsize SUV	2016-2018	190.0	76.1	66.2	2016/2017/2018 Lincoln MKX	中型SUV	可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2007	190.5	72.2	55.4	2007 Lincoln MKZ		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	Std.	gen1 midsize sedan	2008-2009	190.5	72.2	57.1	2008/2009 Lincoln MKZ		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen1 midsize sedan	2010-2012	189.8	72.2	56.9	2010/2011/2012 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen2 midsize sedan	2013	194.1	73.4	58.2	2013 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen2 midsize sedan	2014	194.1	73.4	58.1	2014 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen2 midsize sedan	2015-2017	194.1	73.4	58.2	2015/2016/2017 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln MKZ	Lincoln	三厢车	Sedan	inc: Hybrid	gen2 midsize sedan	2018-2020	193.9	73.4	58.1	2018/2019/2020 Lincoln MKZ / MKZ Hybrid		可入库
Lincoln Nautilus	Lincoln	越野车	SUV	Std.	gen1 midsize SUV	2019-2023	190.0	76.1	66.2	2019/2020/2021/2022/2023 Lincoln Nautilus	Edmunds部分年份folded width误作w/o，按Lincoln/Edmunds Base修正	可入库
Lincoln Nautilus	Lincoln	越野车	SUV	Std.	gen2 midsize SUV	2024-2026	193.2	76.9	68.2	2024/2025/2026 Lincoln Nautilus	按Lincoln官方excluding mirrors	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	1998	204.8	79.9	76.7	1998 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	1999	204.8	79.9	75.2	1999 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	2000	204.8	79.9	76.7	2000 Lincoln Navigator, Cars.com / 2000 Lincoln Navigator brochure	标准轴距；按4WD最大高度	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	2001	204.8	79.9	75.2	2001 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen1 full-size SUV	2002	204.8	79.9	76.7	2002 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2007	208.4	79.7	78.3	2007 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2008-2014	208.4	78.8	78.3	2008/2009/2010/2011/2012/2013/2014 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen3 full-size SUV	2015-2017	207.4	78.8	78.1	2015/2016/2017 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2007	223.3	79.7	78.1	2007 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2008-2010	223.3	78.1	78.3	2008/2009/2010 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2011-2014	223.3	78.8	78.1	2011/2012/2013/2014 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen3 full-size SUV	2015-2017	222.3	78.8	78.0	2015/2016/2017 Lincoln Navigator L	长轴L	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen4 full-size SUV	2018-2024	210.0	79.9	76.4	2018/2019/2020/2021/2022/2023/2024 Lincoln Navigator	标准轴距；2018 Edmunds宽度异常，按C&D/Cars.com修正	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen4 full-size SUV	2018-2024	221.9	79.9	76.2	2018/2019/2020/2021/2022/2023/2024 Lincoln Navigator L	长轴L；2018 Edmunds宽度异常，按C&D/Cars.com修正	可入库
Lincoln Navigator	Lincoln	越野车	SUV	Std.	gen5 full-size SUV	2025-2026	210.0	80.0	78.0	2025/2026 Lincoln Navigator	标准轴距	可入库
Lincoln Navigator	Lincoln	越野车	SUV	L	gen5 full-size SUV	2025-2026	221.9	80.0	78.0	2025/2026 Lincoln Navigator L	长轴L	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen1 full-size Panther	1983-1988	219.0	78.1	55.9	1983/1984/1985/1986/1987/1988 Lincoln Town Car, Automobile-Catalog	方正长尾厢	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen1 full-size Panther	1989	219.2	78.1	55.9	1989 Lincoln Town Car, Automobile-Catalog	方正长尾厢	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen2 full-size Panther	1990	220.2	78.1	56.7	1990 Lincoln Town Car, Automobile-Catalog	长轴Panther	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen2 full-size Panther	1991	218.8	78.1	56.7	1991 Lincoln Town Car, Automobile-Catalog	长轴Panther	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen2 full-size Panther	1992-1997	218.9	76.9	56.9	1992/1993/1994/1995/1996/1997 Lincoln Town Car, Automobile-Catalog	长轴Panther	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	1998-2002	215.3	78.2	58.0	1998/1999/2000/2001/2002 Lincoln Town Car	更圆润更高	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2003-2004	215.4	78.2	59.0	2003/2004 Lincoln Town Car	末期车队常见	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2005-2007	215.4	78.2	58.6	2005/2006/2007 Lincoln Town Car	末期车队常见	可入库
Lincoln Town Car	Lincoln	三厢车	Sedan	Std.	gen3 full-size Panther	2008-2011	215.4	78.5	59.0	2008/2009/2010/2011 Lincoln Town Car	末期车队常见	可入库
Lucid Motors Gravity	Lucid Motors	越野车	SUV	EV	gen1 luxury EV SUV	2025-2026	198.2	78.7	65.2	2025/2026 Lucid Gravity	豪华电动SUV	可入库
Lucid Motors Lucid Air	Lucid Motors	三厢车	Sedan	EV	gen1 luxury EV sedan	2022-2026	195.9	76.2	55.4	2022/2023/2024/2025/2026 Lucid Air	豪华电动轿车	可入库
Maserati Ghibli	Maserati	三厢车	Sedan	Std.	gen1 midsize sedan	2015-2017	195.7	76.8	57.5	2015/2016 Maserati Ghibli S Q4 / 2017 Maserati Ghibli Base/S	豪华三厢；按2015-2016 S Q4最大宽度	可入库
Maserati Ghibli	Maserati	三厢车	Sedan	Std.	gen1 midsize sedan	2018-2020	195.7	76.6	57.5	2018/2019/2020 Maserati Ghibli	豪华三厢	可入库
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2008-2012	192.2	75.4	53.3	2008 Maserati GranTurismo S / 2009/2010/2011/2012 Maserati GranTurismo S/Sport Coupe	大型双门GT；按S/Sport最大宽度	可入库
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2013-2014	192.2	75.4	53.3	2013/2014 Maserati GranTurismo Sport Coupe	大型双门GT	可入库
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen1 grand tourer	2015-2016	194.2	75.4	53.0	2015/2016 Maserati GranTurismo Sport/MC Coupe	大型双门GT；后期Sport/MC车长更长	可入库
Maserati GranTurismo	Maserati	跑车	Coupe	inc: EV	gen2 grand tourer	2024-2026	195.2	77.0	53.3	2024/2025/2026 Maserati GranTurismo / GranTurismo Folgore	含纯电版本	可入库
Maserati Levante	Maserati	越野车	SUV	Std.	gen1 midsize SUV	2017-2018	197.0	77.5	66.1	2017/2018 Maserati Levante SUV	豪华SUV	可入库
Mazda 2	Mazda	两厢车	Hatchback	Std.	gen1 subcompact hatchback	2011-2014	155.5	66.7	58.1	2011/2012/2013/2014 Mazda 2 Sport	小型两厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen1 early	2004-2005	178.7	69.1	57.7	2004/2005 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen1 early	2006-2009	177.4	69.1	57.7	2006/2007/2008/2009 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen1 early	2004-2006	176.6	69.1	57.7	2004/2005/2006 Mazda 3 Hatchback	两厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen1 early	2007-2009	176.8	69.1	57.7	2007/2008/2009 Mazda 3 Hatchback	两厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen2 mid	2010-2013	180.7	69.1	57.9	2010/2011/2012/2013 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen2 mid	2010-2013	177.4	69.1	57.9	2010/2011/2012/2013 Mazda 3 Hatchback	两厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen3 late	2014-2018	180.3	70.7	57.3	2014/2015/2016/2017/2018 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen3 late	2014-2018	175.6	70.7	57.3	2014/2015/2016/2017/2018 Mazda 3 Hatchback	两厢车	可入库
Mazda 3	Mazda	三厢车	Sedan	Std.	gen4	2019-2026	183.5	70.7	56.9	2019/2020/2021/2022/2023/2024/2025/2026 Mazda 3 Sedan	三厢车	可入库
Mazda 3	Mazda	两厢车	Hatchback	Std.	gen4	2019-2026	175.6	70.7	56.7	2019/2020/2021/2022/2023/2024/2025/2026 Mazda 3 Hatchback	两厢车	可入库
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2006-2009	181.5	69.1	64.2	2006/2007/2008/2009 Mazda 5	小型MPV	可入库
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2010	181.5	69.0	64.2	2010 Mazda 5	小型MPV	可入库
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2011				2011 Mazda5 US model year skipped / no US data	美国年款跳过，不入库	无数据: 2011美国未售/跳过
Mazda 5	Mazda	两厢车	MPV	Std.	gen1 compact MPV	2012-2015	180.5	68.9	63.6	2012/2013/2014/2015 Mazda 5	小型MPV	可入库
Mazda 6	Mazda	三厢车	Sedan	Std.	gen1 midsize	2003-2008	186.8	70.1	56.7	2003/2004/2005/2006/2007/2008 Mazda 6 Sedan, Edmunds		可入库
Mazda 6	Mazda	两厢车	Hatchback	Std.	gen1 midsize	2003				2003 Mazda 6 Sedan only; 2004 Mazda6 5-Door introduced in US	2003美国5-Door结构无明确销售页	无数据: 2003美国Hatchback未确认/不入库
Mazda 6	Mazda	两厢车	Hatchback	Std.	gen1 midsize	2004-2008	186.8	70.1	56.7	2004/2005/2006/2007/2008 Mazda 6 Hatchback, Edmunds		可入库
Mazda 6	Mazda	两厢车	Wagon	Std.	gen1 midsize	2004-2007	187.8	70.1	57.3	2004/2005/2006/2007 Mazda 6 Wagon, Edmunds		可入库
Mazda 6	Mazda	三厢车	Sedan	Std.	gen2 midsize	2009-2013	193.7	72.4	57.9	2009/2010/2011/2012/2013 Mazda 6 Sedan, Edmunds		可入库
Mazda 6	Mazda	三厢车	Sedan	Std.	gen3 midsize	2014-2017	191.5	72.4	57.1	2014/2015/2016/2017 Mazda 6 Sedan, Edmunds		可入库
Mazda 6	Mazda	三厢车	Sedan	Std.	gen3 midsize	2018-2021	192.7	72.4	57.1	2018/2019/2020/2021 Mazda 6 Sedan, Edmunds		可入库
Mazda CX-3	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2016-2019	168.3	69.6	60.9	2016/2017/2018/2019 Mazda CX-3	小型SUV	可入库
Mazda CX-3	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2020-2021	168.3	69.6	60.7	2020/2021 Mazda CX-3	小型SUV	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2020	173.0	70.7	61.7	2020 Mazda CX-30	小型SUV	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2021	173.0	70.7	62.2	2021 Mazda CX-30 Turbo Premium Plus	小型SUV高trim较高	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2022-2024	173.0	70.7	61.7	2022/2023/2024 Mazda CX-30	小型SUV	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2025	173.0	70.7	62.2	2025 Mazda CX-30 trims max height	小型SUV高trim较高	可入库
Mazda CX-30	Mazda	越野车	SUV	Std.	gen1 subcompact SUV	2026	173.0	70.7	61.4	2026 Mazda CX-30	高度小改	可入库
Mazda CX-50	Mazda	越野车	SUV	Std.	gen1 compact SUV	2023-2024	185.8	75.6	63.5	2023/2024 Mazda CX-50	跨界SUV	可入库
Mazda CX-50	Mazda	越野车	SUV	inc: Hybrid	gen1 compact SUV	2025	186.1	75.6	65.6	2025 Mazda CX-50 Hybrid	含混动	可入库
Mazda CX-50	Mazda	越野车	SUV	inc: Hybrid	gen1 compact SUV	2026	186.1	75.6	65.8	2026 Mazda CX-50 Hybrid Premium Plus	含混动高车顶trim	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2007	184.1	73.7	64.8	2007 Mazda CX-7	中型SUV	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2008-2009	184.0	73.7	64.8	2008/2009 Mazda CX-7	中型SUV	可入库
Mazda CX-7	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2010-2012	184.3	73.7	64.8	2010/2011/2012 Mazda CX-7	中型SUV	可入库
Mazda CX-70	Mazda	越野车	SUV	inc: PHEV	gen1 midsize SUV	2025-2026	200.8	77.6	68.2	2025/2026 Mazda CX-70 / CX-70 PHEV	两排中大型SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2007	199.6	76.2	68.3	2007 Mazda CX-9 trims max height	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2008	199.6	76.2	68.0	2008 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2009-2010	199.8	76.2	68.0	2009/2010 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2011-2012	200.2	76.2	68.0	2011/2012 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen1 midsize SUV	2013-2015	200.6	76.2	68.0	2013/2014/2015 Mazda CX-9	三排SUV	可入库
Mazda CX-9	Mazda	越野车	SUV	Std.	gen2 midsize SUV	2016-2023	199.4	77.5	69.0	2016/2017/2018/2019/2020/2021/2022/2023 Mazda CX-9	三排SUV	可入库
Mazda CX-90	Mazda	越野车	SUV	inc: PHEV	gen1 midsize SUV	2024-2025	201.6	77.6	68.2	2024/2025 Mazda CX-90 / CX-90 PHEV	三排SUV	可入库
Mazda CX-90	Mazda	越野车	SUV	inc: PHEV	gen1 midsize SUV	2026	201.6	77.6	68.7	2026 Mazda CX-90 trims max height	三排SUV高trim较高	可入库