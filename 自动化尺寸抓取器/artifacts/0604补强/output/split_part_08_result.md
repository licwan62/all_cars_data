# 文件名：split_part_08.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作	描述
全表	字段修正	按新版统一字段输出；普通车“子车系/驾驶室类型/货斗长度_ft”留空，版本不留空
Cadillac Escalade	新增	补入缺失 gen1 1999-2000 短轴 SUV，Edmunds 1999/2000 尺寸一致：201.2×77.0×74.3 
Edmunds
+1

Cadillac Escalade Std gen2	补强	增加 2003 参考点，2003 Edmunds 为 198.9×78.9×76.5 
Edmunds

Cadillac ATS Sedan	补强	增加 2013 参考点，2013 ATS Sedan 高度存在 trim 差异，最大高度 56.4 
Edmunds
+1

Cadillac ATS Coupe	补强	增加 2018/2019 普通 Coupe 参考点，普通 Coupe 为 183.6×72.5×54.8；原行含 ATS-V，仍需继续核 ATS-V 年份 
Edmunds
+1

Cadillac CTS	补强	CTS gen1 2007、gen3 2019 有 Edmunds 尺寸点；Wagon 2013 有 C&D 尺寸点，仍需补剩余年份 
Edmunds
+2
Edmunds
+2

当前批次进度

状态	数量	说明
🟢 可入库	1	本轮新增 Escalade gen1 已覆盖 1999-2000
🟡 待补强	20	原有记录多数仍需逐年补齐参考车型覆盖
🔴 未完成	1	Escalade EXT / 部分 Cadillac 代际完整性仍需继续检查

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015/2018/2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	待补强: 2016-2017 ATS-V Coupe / 2016-2017普通Coupe
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2019			182.8	71.1	56.4	2013/2014/2016 Cadillac ATS Sedan	紧凑轿车	待补强: 2015/2017-2019
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011-2015			189.3	74.1	56	2011/2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	待补强: 2012-2014
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003/2007 Cadillac CTS Sedan	中型轿车	待补强: 2004-2006
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2013			191.6	72.5	58	2008/2013 Cadillac CTS Sedan AWD	中型轿车	待补强: 2009-2012
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014/2019 Cadillac CTS / CTS-V Sedan	中型轿车	待补强: 2015-2018
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010-2014			192	72.5	58	2012/2013 Cadillac CTS Wagon / CTS-V Wagon	旅行车	待补强: 2010-2011/2014
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003/2006 Cadillac Escalade ESV	长轴ESV	待补强: 2004-2005
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2014			222.9	79.1	75.5	2007/2014 Cadillac Escalade ESV	长轴ESV	待补强: 2008-2013
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015/2020 Cadillac Escalade ESV	长轴ESV	待补强: 2016-2019
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021/2026 Cadillac Escalade ESV	长轴ESV	待补强: 2022-2025
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002/2003/2006 Cadillac Escalade	短轴全尺寸SUV	待补强: 2004-2005
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2007-2014			202.5	79	75.9	2007/2014 Cadillac Escalade	短轴全尺寸SUV	待补强: 2008-2013
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015/2020 Cadillac Escalade	短轴全尺寸SUV	待补强: 2016-2019

下一步优先核对

先补 Cadillac Escalade gen5 Std 2021-2026、Escalade ESV 各代中间年份，再补 CT4/CT5/CTS 的缺失年份；同时检查 Escalade EXT 是否需要作为当前车型口径新增。

下一步


--- Round 2 / 下一步 ---
更新点

车型	操作	描述
Cadillac Escalade	新增	补入缺失 gen5 Std 2021-2026 短轴 SUV，尺寸 211.9×81.1×76.7，参考车型覆盖 2021-2026。Edmunds 2021/2025/2026 短轴 Escalade 均为该尺寸。
Edmunds
+2
Edmunds
+2

Cadillac Escalade ESV gen5	值确认	2021-2026 ESV 尺寸确认 227×81.1×76.4，参考车型覆盖整段，推进为可入库。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Cadillac Escalade Std gen4	补强	增加 2016 参考点；2015/2016/2020 短轴 Escalade 尺寸一致，仍缺 2017-2019。
Edmunds
+1

Cadillac Escalade ESV gen4	补强	增加 2018/2019 参考点；2015/2018/2019/2020 ESV 尺寸一致，仍缺 2016-2017。
Edmunds
+1

Cadillac Escalade Std gen3	补强	增加 2012/2013/2014 参考点；短轴 gen3 202.5×79.0×75.9 已确认部分年份。
Edmunds
+2
Edmunds
+2

Cadillac Escalade ESV gen3	补强	增加 2008/2009/2010/2014 参考点；2012 ESV 高度来源显示 73.1，与原 75.5 不一致，先保留待终核拆分风险。
Edmunds
+4
Edmunds
+4
Edmunds
+4

当前批次进度

状态	数量	说明
🟢 可入库	3	Escalade gen1 Std、Escalade gen5 Std、Escalade gen5 ESV
🟡 待补强	20	CTS / CT 系列 / ATS / ELR / Catera / Escalade gen2-gen4 仍有缺失年份
🔴 待拆分风险	1	Escalade ESV gen3 的 2012 高度与同代其它年份不一致，下一轮优先核对是否需拆行

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015/2018/2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	待补强: 2016-2017 ATS-V Coupe / 2016-2017普通Coupe
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2019			182.8	71.1	56.4	2013/2014/2016 Cadillac ATS Sedan	紧凑轿车	待补强: 2015/2017-2019
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011-2015			189.3	74.1	56	2011/2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	待补强: 2012-2014
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003/2007 Cadillac CTS Sedan	中型轿车	待补强: 2004-2006
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2013			191.6	72.5	58	2008/2013 Cadillac CTS Sedan AWD	中型轿车	待补强: 2009-2012
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014/2019 Cadillac CTS / CTS-V Sedan	中型轿车	待补强: 2015-2018
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010-2014			192	72.5	58	2012/2013 Cadillac CTS Wagon / CTS-V Wagon	旅行车	待补强: 2010-2011/2014
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003/2005/2006 Cadillac Escalade ESV	长轴ESV	待补强: 2004
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2014			222.9	79.1	75.5	2007-2010/2014 Cadillac Escalade ESV	长轴ESV	待终核: 2011/2012/2013；2012高度疑似需拆分
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015/2018-2020 Cadillac Escalade ESV	长轴ESV	待补强: 2016-2017
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002/2003/2006 Cadillac Escalade	短轴全尺寸SUV	待补强: 2004-2005
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2007-2014			202.5	79	75.9	2007/2012-2014 Cadillac Escalade	短轴全尺寸SUV	待补强: 2008-2011
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015/2016/2020 Cadillac Escalade	短轴全尺寸SUV	待补强: 2017-2019
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库

下一步优先核对

优先处理 Escalade gen3 ESV 的 2011/2012/2013 高度异常，看是否需要拆成 2007-2011 / 2012 / 2013-2014；然后补 Escalade gen2/gen4 剩余年份，最后推进 CTS、ATS、CT4/CT5 的缺失年份。

下一步


--- Round 3 / 下一步 ---
更新点

车型	操作	描述
Cadillac Escalade ESV gen3	拆出	原 2007-2014 ESV 高度不一致：2007-2010/2013-2014 为 75.5；2011-2012 为 73.1，因此拆成两条记录。
Edmunds
+5
Edmunds
+5
Edmunds
+5

Cadillac Escalade ESV gen3	可入库推进	2007-2010/2013-2014 已覆盖参考车型；2011-2012 也单独覆盖，均可入库。
Edmunds
+2
Edmunds
+2

Cadillac Escalade Std gen2	可入库推进	补齐 2004/2005，2002-2006 短轴 Escalade 尺寸 198.9×78.9×76.5，推进为可入库。
Edmunds
+1

Cadillac Escalade ESV gen4	可入库推进	补齐 2016/2017，2015-2020 ESV 尺寸 224.3×80.5×74.0，推进为可入库。
Edmunds
+1

Cadillac Escalade EXT	新增占位	当前 Escalade 口径客观存在 EXT 皮卡型；先新增 gen2/gen3 EXT 占位行，待按皮卡字段继续核对。

当前批次进度

状态	数量	说明
🟢 可入库	8	Escalade gen1 Std、gen2 Std、gen3 ESV 两段、gen4 ESV、gen5 Std/ESV 等已推进
🟡 待补强	17	ATS / CT4 / CT5 / CT6 / CTS / Catera / ELR / Escalade 部分 gen2-gen4 Std/ESV
🔴 待终核占位	2	Escalade EXT gen2/gen3 需按皮卡字段核对尺寸

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015/2018/2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	待补强: 2016-2017 ATS-V Coupe / 2016-2017普通Coupe
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2019			182.8	71.1	56.4	2013/2014/2016 Cadillac ATS Sedan	紧凑轿车	待补强: 2015/2017-2019
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011-2015			189.3	74.1	56	2011/2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	待补强: 2012-2014
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003/2007 Cadillac CTS Sedan	中型轿车	待补强: 2004-2006
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2013			191.6	72.5	58	2008/2013 Cadillac CTS Sedan AWD	中型轿车	待补强: 2009-2012
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014/2019 Cadillac CTS / CTS-V Sedan	中型轿车	待补强: 2015-2018
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010-2014			192	72.5	58	2012/2013 Cadillac CTS Wagon / CTS-V Wagon	旅行车	待补强: 2010-2011/2014
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003/2005/2006 Cadillac Escalade ESV	长轴ESV	待补强: 2004
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2007-2014			202.5	79	75.9	2007/2011-2014 Cadillac Escalade	短轴全尺寸SUV	待补强: 2008-2010
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015/2016/2020 Cadillac Escalade	短轴全尺寸SUV	待补强: 2017-2019
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006		5.25					Escalade EXT皮卡型	待终核: gen2 EXT 全量尺寸/驾驶室/货斗字段
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013		5.25					Escalade EXT皮卡型	待终核: gen3 EXT 全量尺寸/驾驶室/货斗字段

下一步优先核对

下一轮优先补 Cadillac Escalade EXT 的 gen2/gen3 皮卡尺寸，并把驾驶室类型统一为 Crew Cab；然后补 Escalade Std gen3 的 2008-2010、Std gen4 的 2017-2019、ESV gen2 的 2004，尽量收完 Escalade 口径。

下一步


--- Round 4 / 下一步 ---
更新点

车型	操作	描述
Cadillac Escalade EXT gen2	值修改	2002-2006 EXT 由占位推进为实值：221.4×79.5×75.6；驾驶室类型补为 Crew Cab，货斗长度按 63 in≈5.25 ft 保留 5.25。Edmunds 2003/2004/2006 尺寸一致。
Edmunds
+2
Edmunds
+2

Cadillac Escalade EXT gen3	值修改	2007-2013 EXT 由占位推进为实值：222.0×79.1×74.5；驾驶室类型补为 Crew Cab，货斗长度按 53.0/63.3 in 折算后统一保留 5.25，备注标注可变货斗。
Edmunds
+2
Edmunds
+2

Cadillac Escalade ESV gen2	可入库推进	补齐 2004，2003-2006 ESV 尺寸 221.4×79.5×75.7，推进为可入库。
Edmunds
+2
Edmunds
+2

Cadillac Escalade Std gen3	拆出	2007-2008 短轴高度 74.3，2010/2014 高度 75.9；为避免同区间混压，拆成 2007-2008 与 2010-2014 两段，2009 继续待终核。
Edmunds
+3
Edmunds
+3
Edmunds
+3

当前批次进度

状态	数量	说明
🟢 可入库	12	Escalade gen1/gen2 Std、gen2 ESV、gen3 ESV 拆分段、gen4 ESV、gen5 Std/ESV、EXT gen2/gen3 已推进
🟡 待补强	17	ATS / CT4 / CT5 / CT6 / CTS / Catera / ELR / Escalade Std gen3/gen4 仍有缺失年份
🔴 需继续核对	2	Escalade Std gen3 2009；Escalade Std gen4 2017-2019

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015/2018/2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	待补强: 2016-2017 ATS-V Coupe / 2016-2017普通Coupe
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2019			182.8	71.1	56.4	2013/2014/2016 Cadillac ATS Sedan	紧凑轿车	待补强: 2015/2017-2019
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011-2015			189.3	74.1	56	2011/2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	待补强: 2012-2014
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003/2007 Cadillac CTS Sedan	中型轿车	待补强: 2004-2006
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2013			191.6	72.5	58	2008/2013 Cadillac CTS Sedan AWD	中型轿车	待补强: 2009-2012
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014/2019 Cadillac CTS / CTS-V Sedan	中型轿车	待补强: 2015-2018
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010-2014			192	72.5	58	2012/2013 Cadillac CTS Wagon / CTS-V Wagon	旅行车	待补强: 2010-2011/2014
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2010-2014			202.5	79	75.9	2010/2014 Cadillac Escalade	短轴全尺寸SUV	待补强: 2011-2013
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009			202.5	79			短轴全尺寸SUV	待终核: 2009高度
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015/2016/2020 Cadillac Escalade	短轴全尺寸SUV	待补强: 2017-2019
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2003/2004/2006 Cadillac Escalade EXT	Crew Cab短货斗	待补强: 2002/2005
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮优先收尾 Escalade：补 EXT gen2 的 2002/2005，补 Std gen3 的 2009/2011-2013 高度覆盖，再补 Std gen4 的 2017-2019。Escalade 完成后再转 ATS / CTS / CT4 / CT5 / CT6 / Catera / ELR。

下一步


--- Round 5 / 下一步 ---
更新点

车型	操作	描述
Cadillac Escalade EXT gen2	补强	增加 2002 参考点；2002 EXT 长 221.4、高 75.6，Edmunds/Cars.com 可确认，仍缺 2005。
Edmunds
+1

Cadillac Escalade Std gen3	补强/拆行	补入 2009、2011；2009/2011 短轴 Escalade 均为 202.5×79.0×75.9，因此从原待核行中拆出可入库段，2012 仍单独待终核。
Edmunds
+1

Cadillac Escalade Std gen4	补强/拆行	补入 2018/2019；2018/2019 短轴 Escalade 均为 203.9×80.5×74.4，2017 仍单独待终核。
Edmunds
+1

Cadillac Escalade	进度推进	Escalade 主体仅剩 Std gen3 2012、Std gen4 2017、EXT gen2 2005 三个缺口。

当前批次进度

状态	数量	说明
🟢 可入库	15	Escalade 大部分长短轴 SUV 与 EXT gen3 已可入库
🟡 待补强	16	ATS / CT4 / CT5 / CT6 / CTS / Catera / ELR 仍未进入集中补强
🔴 关键缺口	3	Escalade Std gen3 2012、Std gen4 2017、EXT gen2 2005

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015/2018/2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	待补强: 2016-2017 ATS-V Coupe / 2016-2017普通Coupe
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2019			182.8	71.1	56.4	2013/2014/2016 Cadillac ATS Sedan	紧凑轿车	待补强: 2015/2017-2019
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011-2015			189.3	74.1	56	2011/2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	待补强: 2012-2014
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003/2007 Cadillac CTS Sedan	中型轿车	待补强: 2004-2006
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2013			191.6	72.5	58	2008/2013 Cadillac CTS Sedan AWD	中型轿车	待补强: 2009-2012
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014/2019 Cadillac CTS / CTS-V Sedan	中型轿车	待补强: 2015-2018
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010-2014			192	72.5	58	2012/2013 Cadillac CTS Wagon / CTS-V Wagon	旅行车	待补强: 2010-2011/2014
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2011			202.5	79	75.9	2009-2011 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2012			202.5	79			短轴全尺寸SUV	待终核: 2012高度
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2013-2014			202.5	79	75.9	2013-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2016			203.9	80.5	74.4	2015-2016 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2017			203.9	80.5			短轴全尺寸SUV	待终核: 2017高度
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2018-2020			203.9	80.5	74.4	2018-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2004	Crew Cab	5.25	221.4	79.5	75.6	2002-2004 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2005	Crew Cab	5.25	221.4	79.5			Crew Cab短货斗	待终核: 2005高度
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2006	Crew Cab	5.25	221.4	79.5	75.6	2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮先收尾 Escalade 最后三个缺口：Std gen3 2012、Std gen4 2017、EXT gen2 2005；若这三条确认后，Escalade 口径即可整体可入库。随后转 ATS Sedan/Coupe、CTS Sedan/Coupe/Wagon、CT4/CT5/CT6、Catera、ELR。

下一步


--- Round 6 / 下一步 ---
更新点

车型	操作	描述
Cadillac Escalade Std gen3	合并/可入库	2012 短轴 Escalade 确认为 202.5×79.0×75.9，因此 2009-2014 可合并为同尺寸区间并推进可入库。
Edmunds
+1

Cadillac Escalade Std gen4	合并/可入库	2017 短轴 Escalade 确认为 203.9×80.5×74.4，因此 2015-2020 可合并为同尺寸区间并推进可入库。
Edmunds
+1

Cadillac Escalade EXT gen2	合并/可入库	2005 EXT 确认为 221.4×79.5×75.6；结合 2003/2004/2006 同尺寸，2002-2006 EXT 可合并并推进可入库。
Edmunds
+2
Edmunds
+2

Cadillac Escalade	状态推进	Escalade / Escalade ESV / Escalade EXT 当前口径已全部补到可入库。
Cadillac ATS Coupe	补强	增加 2016 普通 Coupe / ATS-V 参考点；2016 普通 Coupe 宽 72.5、高 55.3，2018 ATS-V Coupe 长 184.7、宽 72.5，高 54.5，原最大值暂保留。
Edmunds
+1

当前批次进度

状态	数量	说明
🟢 可入库	17	Escalade 全口径已可入库；其余车型尚未全部完成
🟡 待补强	13	ATS / CT4 / CT5 / CT6 / CTS / Catera / ELR 仍有缺失年份
🔴 关键缺口	0	Escalade 三个关键缺口已收完

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015/2016/2018/2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	待补强: 2017 ATS Coupe / ATS-V Coupe
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2019			182.8	71.1	56.4	2013/2014/2016 Cadillac ATS Sedan	紧凑轿车	待补强: 2015/2017-2019
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011-2015			189.3	74.1	56	2011/2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	待补强: 2012-2014
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003/2007 Cadillac CTS Sedan	中型轿车	待补强: 2004-2006
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2013			191.6	72.5	58	2008/2013 Cadillac CTS Sedan AWD	中型轿车	待补强: 2009-2012
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014/2019 Cadillac CTS / CTS-V Sedan	中型轿车	待补强: 2015-2018
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010-2014			192	72.5	58	2012/2013 Cadillac CTS Wagon / CTS-V Wagon	旅行车	待补强: 2010-2011/2014
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2014			202.5	79	75.9	2009-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2002-2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮转入普通车部分：优先补 ATS Sedan/Coupe 剩余年份，然后推进 CTS Sedan/Coupe/Wagon；再处理 CT4、CT5、CT6、Catera、ELR。

下一步


--- Round 7 / 下一步 ---
更新点

车型	操作	描述
Cadillac ATS Coupe	补强/可入库	补齐 2017 ATS Coupe / ATS-V Coupe；普通 Coupe 2017 为 183.6×72.5×54.8，ATS-V Coupe 2016/2018/2019 为 184.7×72.5×54.5，因此原 inc: ATS-V 行按最大长宽高保留 184.7×72.5×55.3，并推进可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Cadillac ATS Sedan	拆出	原 Sedan Std. 行不应覆盖 ATS-V Sedan；新增 inc: ATS-V Sedan 2016-2019，尺寸 184.0×71.3×55.7。
Edmunds
+1

Cadillac ATS Sedan Std.	补强/修正年份	ATS Sedan 普通版美国市场 2013-2018；2019 美国市场只剩 Coupe，Sedan 行从 2013-2019 修正为 2013-2018，并推进可入库。2015 为 182.8×71.1×56.4，2016/2017/2018 为 182.8×71.1×55.9；按区间最大高度保留 56.4。
Cars.com
+3
Edmunds
+3
Edmunds
+3

Cadillac ATS	代际完整性	ATS 当前 Sedan / Coupe / ATS-V Sedan / ATS-V Coupe 口径已补齐到停产年。

当前批次进度

状态	数量	说明
🟢 可入库	20	Escalade 全口径、ATS Coupe、ATS Sedan Std、ATS-V Sedan 已可入库
🟡 待补强	10	CT4 / CT5 / CT6 / CTS / Catera / ELR 仍有缺失年份
🔴 关键缺口	0	当前无无法落值的空字段行

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015-2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2018			182.8	71.1	56.4	2013-2018 Cadillac ATS Sedan	紧凑轿车	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	inc: ATS-V	gen1 compact sport sedan	2016-2019			184	71.3	55.7	2016-2019 Cadillac ATS-V Sedan	高性能紧凑轿车	可入库
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011-2015			189.3	74.1	56	2011/2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	待补强: 2012-2014
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003/2007 Cadillac CTS Sedan	中型轿车	待补强: 2004-2006
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2013			191.6	72.5	58	2008/2013 Cadillac CTS Sedan AWD	中型轿车	待补强: 2009-2012
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014/2019 Cadillac CTS / CTS-V Sedan	中型轿车	待补强: 2015-2018
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010-2014			192	72.5	58	2012/2013 Cadillac CTS Wagon / CTS-V Wagon	旅行车	待补强: 2010-2011/2014
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2014			202.5	79	75.9	2009-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2002-2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮优先推进 CTS：先补 CTS gen1/gen2/gen3 Sedan，再补 CTS Coupe / Wagon / CTS-V；之后处理 CT4、CT5、CT6、Catera、ELR。

下一步


--- Round 8 / 下一步 ---
更新点

车型	操作	描述
Cadillac CTS Sedan gen1 Std.	可入库推进	2003/2004/2005/2007 Edmunds 显示普通 CTS Sedan 为 190.1×70.6×56.7；本轮将 2003-2007 普通 Sedan 推进为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Cadillac CTS Sedan gen1 CTS-V	拆出	2004 CTS-V Sedan 外尺寸为 191.5×70.6×57.3，明显不同于普通 CTS Sedan，因此新增 inc: CTS-V 2004-2007 行，避免混入 Std.。
Edmunds

Cadillac CTS Sedan gen2 Std.	拆分	2008 为 191.6×72.5×58.0；2011-2013 为 191.3×72.5×58.0，长度不同，拆为 2008 / 2009-2010待核 / 2011-2013 三段。
Edmunds
+2
Edmunds
+2

Cadillac CTS Coupe gen2	补强	2012 CTS Coupe 为 188.5×74.1×56.0；2015 CTS-V Coupe 也是 188.5×74.1×56.0，原 189.3 长度需继续核对 2011/2013/2014。
Edmunds
+1

Cadillac CTS Wagon gen2	拆分	2010 CTS Wagon 为 191.6×72.6×59.1；2012/2014 Wagon 为 192.0×72.5×58.0，因此拆出 2010 单年，2011 继续待核，2012-2014 推进可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

当前批次进度

状态	数量	说明
🟢 可入库	25	Escalade 全口径、ATS 全口径、CTS gen1 Std/CTS-V、CTS Wagon 2010 与 2012-2014 等已推进
🟡 待补强	9	CTS Coupe、CTS gen2 2009-2010、CTS gen3 2014-2019、CT4/CT5/CT6/Catera/ELR
🔴 关键缺口	4	CTS Coupe 2011/2013/2014、CTS Sedan gen2 2009-2010、CTS gen3 2015-2018、CTS Wagon 2011

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015-2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2018			182.8	71.1	56.4	2013-2018 Cadillac ATS Sedan	紧凑轿车	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	inc: ATS-V	gen1 compact sport sedan	2016-2019			184	71.3	55.7	2016-2019 Cadillac ATS-V Sedan	高性能紧凑轿车	可入库
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011-2015			189.3	74.1	56	2011/2012/2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	待补强: 2013-2014；2011长度需复核
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003-2007 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen1 midsize sport sedan	2004-2007			191.5	70.6	57.3	2004-2007 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008			191.6	72.5	58	2008 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2009-2010			191.6	72.5	58		中型轿车	待终核: 2009-2010
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2011-2013			191.3	72.5	58	2011-2013 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2009-2013			191.3	72.5	57.3	2012 Cadillac CTS-V Sedan	高性能中型轿车	待补强: 2009-2011/2013
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014/2015/2016/2019 Cadillac CTS / CTS-V Sedan	中型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010			191.6	72.6	59.1	2010 Cadillac CTS Wagon	旅行车高车身	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2011			192	72.5			旅行车	待终核: 2011高度/宽度
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2012-2014			192	72.5	58	2012-2014 Cadillac CTS Wagon / CTS-V Wagon	旅行车	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2014			202.5	79	75.9	2009-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2002-2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮继续收 CTS：补 CTS Coupe 2013-2014、CTS Wagon 2011、CTS Sedan gen2 2009-2010、CTS-V Sedan gen2 2009-2011/2013、CTS gen3 2017-2018。CTS 完成后再处理 CT4 / CT5 / CT6 / Catera / ELR。

下一步


--- Round 9 / 下一步 ---
更新点

车型	操作	描述
Cadillac CTS Coupe gen2	拆分/可入库	2011 Coupe 长度为 189.3；2012-2014 Coupe / CTS-V Coupe 为 188.5×74.1×56.0，因此拆成 2011 与 2012-2015 两段，避免混压。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Cadillac CTS Wagon gen2	合并/可入库	2011 Wagon 确认为 192.0×72.5×58.0，可与 2012-2014 合并；2010 因 191.6×72.6×59.1 继续单独保留。
Edmunds
+2
Edmunds
+2

Cadillac CTS Sedan gen2 Std.	拆分	2009 为 191.6×72.5×58.0；2010 为 191.6×72.5×59.2；2011-2013 为 191.3×72.5×58.0，因此拆成 2008-2009 / 2010 / 2011-2013。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Cadillac CTS gen3 Sedan inc: CTS-V	可入库推进	2017/2018 CTS-V 为 197.6×72.2×57.2，覆盖原 inc: CTS-V 最大尺寸逻辑；2014-2019 推进为可入库。
Edmunds
+2
Edmunds
+2

Cadillac CTS-V Sedan gen2	部分推进	2009 CTS-V Sedan 为 191.6×72.5×57.3，2013 CTS-V Sedan 为 191.3×72.5×57.3；中间 2010-2012 仍保留待补强。
Edmunds
+1

当前批次进度

状态	数量	说明
🟢 可入库	30	Escalade 全口径、ATS 全口径、CTS 大部分 Sedan/Coupe/Wagon 已推进
🟡 待补强	7	CT4 / CT5 / CT6 / Catera / ELR / CTS-V Sedan gen2 中间年份
🔴 关键缺口	1	CTS-V Sedan gen2 2010-2012 仍需补齐后才能合并或拆分定稿

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015-2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2018			182.8	71.1	56.4	2013-2018 Cadillac ATS Sedan	紧凑轿车	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	inc: ATS-V	gen1 compact sport sedan	2016-2019			184	71.3	55.7	2016-2019 Cadillac ATS-V Sedan	高性能紧凑轿车	可入库
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021/2024/2025/2026 Cadillac CT4 / CT4-V Blackwing	紧凑轿车	待补强: 2020/2022-2023
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011			189.3	74.1	56	2011 Cadillac CTS Coupe	双门轿跑长车身	可入库
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2012-2015			188.5	74.1	56	2012-2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003-2007 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen1 midsize sport sedan	2004-2007			191.5	70.6	57.3	2004-2007 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2009			191.6	72.5	58	2008-2009 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2010			191.6	72.5	59.2	2010 Cadillac CTS Sedan	中型轿车高车身	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2011-2013			191.3	72.5	58	2011-2013 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2009			191.6	72.5	57.3	2009 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2010-2012			191.6	72.5	57.3		高性能中型轿车	待补强: 2010-2012
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2013			191.3	72.5	57.3	2013 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014-2019 Cadillac CTS / CTS-V Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010			191.6	72.6	59.1	2010 Cadillac CTS Wagon	旅行车高车身	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2011-2014			192	72.5	58	2011-2014 Cadillac CTS Wagon / CTS-V Wagon	旅行车	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2014			202.5	79	75.9	2009-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2002-2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮先补 CTS-V Sedan gen2 的 2010-2012；如果确认与 2009 或 2013 一致，就把 CTS 口径整体收尾。之后进入 CT4 / CT5 / CT6 / Catera / ELR。

下一步


--- Round 10 / 下一步 ---
更新点

车型	操作	描述
Cadillac CTS-V Sedan gen2	拆分/可入库	2010 CTS-V Sedan 为 191.6×72.5×57.3；2011/2012/2013 CTS-V Sedan 为 191.3×72.5×57.3，因此拆成 2009-2010 与 2011-2013 两段，CTS 口径整体收尾。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Cadillac CT4	补强	2022/2023 CT4 普通版为 187.2×71.4×56.0；原行含 CT4-V Blackwing 的最大长度 187.6，继续保留 inc: V/Blackwing 最大值逻辑。
Edmunds
+1

Cadillac CT4	状态推进	参考车型补入 2022/2023 后，CT4 当前只剩 2020 待补强。
Cadillac CTS	状态推进	CTS Sedan / Coupe / Wagon / CTS-V Sedan 当前全部可入库。

当前批次进度

状态	数量	说明
🟢 可入库	32	Escalade、ATS、CTS 全口径已可入库
🟡 待补强	5	CT4、CT5、CT6、Catera、ELR
🔴 关键缺口	1	CT4 2020 仍需补齐；CT5/CT6/Catera/ELR 还未收尾

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015-2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2018			182.8	71.1	56.4	2013-2018 Cadillac ATS Sedan	紧凑轿车	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	inc: ATS-V	gen1 compact sport sedan	2016-2019			184	71.3	55.7	2016-2019 Cadillac ATS-V Sedan	高性能紧凑轿车	可入库
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2021-2026 Cadillac CT4 / CT4-V / CT4-V Blackwing	紧凑轿车	待补强: 2020
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020/2023/2024 Cadillac CT5	中型轿车	待补强: 2021-2022
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			194.9	74.1	57.2	2026 Cadillac CT5 / CT5-V Blackwing	中型轿车	待补强: 2025
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011			189.3	74.1	56	2011 Cadillac CTS Coupe	双门轿跑长车身	可入库
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2012-2015			188.5	74.1	56	2012-2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003-2007 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen1 midsize sport sedan	2004-2007			191.5	70.6	57.3	2004-2007 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2009			191.6	72.5	58	2008-2009 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2010			191.6	72.5	59.2	2010 Cadillac CTS Sedan	中型轿车高车身	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2011-2013			191.3	72.5	58	2011-2013 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2009-2010			191.6	72.5	57.3	2009-2010 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2011-2013			191.3	72.5	57.3	2011-2013 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014-2019 Cadillac CTS / CTS-V Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010			191.6	72.6	59.1	2010 Cadillac CTS Wagon	旅行车高车身	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2011-2014			192	72.5	58	2011-2014 Cadillac CTS Wagon / CTS-V Wagon	旅行车	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2014			202.5	79	75.9	2009-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2002-2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮优先补 CT4 2020，并同步推进 CT5 2021-2022 / 2025；随后收 CT6、Catera、ELR 三个短区间车型。

下一步


--- Round 11 / 下一步 ---
更新点

车型	操作	描述
Cadillac CT4	可入库推进	补齐 2020；2020 CT4 为 187.2×71.4×56.0，2025 CT4-V Blackwing 为 187.6×71.4×56.0，因此 inc: V/Blackwing 行按最大长度 187.6 保留，2020-2026 推进为可入库。
Edmunds
+1

Cadillac CT5 Std. gen1	可入库推进	补齐 2021-2022；2020-2024 CT5 普通/V 非 Blackwing 尺寸为 193.8×74.1×57.2，推进为可入库。
Edmunds
+1

Cadillac CT5 facelift	拆分/补强	2025-2026 普通/V 为 193.8×74.1×57.2；2025-2026 CT5-V Blackwing 为 194.9×74.1×56.5，因此原 facelift 行拆成 Std. 与 Blackwing 两条，避免用 Blackwing 长度覆盖普通版。
Edmunds
+1

当前批次	进度推进	CT4、CT5 当前口径已补齐到 2026，进入可入库；剩余集中在 CT6、Catera、ELR。

当前批次进度

状态	数量	说明
🟢 可入库	35	Escalade、ATS、CTS、CT4、CT5 已可入库
🟡 待补强	3	CT6、Catera、ELR
🔴 关键缺口	0	暂无空尺寸关键行

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015-2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2018			182.8	71.1	56.4	2013-2018 Cadillac ATS Sedan	紧凑轿车	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	inc: ATS-V	gen1 compact sport sedan	2016-2019			184	71.3	55.7	2016-2019 Cadillac ATS-V Sedan	高性能紧凑轿车	可入库
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2020-2026 Cadillac CT4 / CT4-V / CT4-V Blackwing	紧凑轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020-2024 Cadillac CT5 / CT5-V	中型轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			193.8	74.1	57.2	2025-2026 Cadillac CT5 / CT5-V	中型轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Blackwing	gen1 midsize sport sedan facelift	2025-2026			194.9	74.1	56.5	2025-2026 Cadillac CT5-V Blackwing	高性能中型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2016-2018			204.1	74	58	2016 Cadillac CT6 / CT6 PHEV	大型轿车	待补强: 2017-2018
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011			189.3	74.1	56	2011 Cadillac CTS Coupe	双门轿跑长车身	可入库
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2012-2015			188.5	74.1	56	2012-2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003-2007 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen1 midsize sport sedan	2004-2007			191.5	70.6	57.3	2004-2007 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2009			191.6	72.5	58	2008-2009 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2010			191.6	72.5	59.2	2010 Cadillac CTS Sedan	中型轿车高车身	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2011-2013			191.3	72.5	58	2011-2013 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2009-2010			191.6	72.5	57.3	2009-2010 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2011-2013			191.3	72.5	57.3	2011-2013 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014-2019 Cadillac CTS / CTS-V Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010			191.6	72.6	59.1	2010 Cadillac CTS Wagon	旅行车高车身	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2011-2014			192	72.5	58	2011-2014 Cadillac CTS Wagon / CTS-V Wagon	旅行车	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-2001			194	70.3	56.3	1998 Cadillac Catera	中型sedan	待补强: 1997/1999-2001
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2014			202.5	79	75.9	2009-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2002-2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮收尾 CT6、Catera、ELR：先补 CT6 2017-2018，再补 ELR 2015，最后补 Catera 1997/1999-2001。若全部确认，下一轮可输出完整可替换 TSV 并给“本批次完成”。

下一步


--- Round 12 / 下一步 ---
更新点

车型	操作	描述
Cadillac CT6	拆分/补全代际	原 CT6 只覆盖 2016-2018 PHEV，不完整；本轮按美国市场完整补为 2016、2017-2018、2019-2020 三段。2016 为 204.0×74.0×57.9；2017-2018 为 204.1×74.0×58.0；2019-2020 facelift 为 205.8×74.0×58.0。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Cadillac CT6 PHEV	修正年份	PHEV 实际单独覆盖 2017-2018；2017/2018 PHEV 均为 204.1×74.0×58.0，推进为可入库。
Edmunds
+1

Cadillac CT6-V	新增	补入 2019-2020 CT6-V / Blackwing，尺寸 205.8×74.0×58.0，补齐 CT6 高性能版本。
Edmunds
+1

Cadillac ELR	可入库推进	2014/2016 Edmunds 均为 186.0×72.7×55.9；2015 未单独抓到 Edmunds 尺寸页，本轮按同代连续规格保留 2014-2016，并仍标待补强 2015，下一轮再终核。
Edmunds
+1

Cadillac Catera	拆分	1997/1998 为 194.0×70.3×56.3；2000/2001 为 192.2×70.3×56.4。1999 仍需单独确认，因此拆成 1997-1998、1999待核、2000-2001。
Edmunds
+2
Edmunds
+2

当前批次进度

状态	数量	说明
🟢 可入库	39	Escalade、ATS、CTS、CT4、CT5、CT6 大部分已可入库
🟡 待补强	2	Catera 1999、ELR 2015 仍需终核
🔴 关键缺口	0	暂无空尺寸关键行；剩余是年份终核

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015-2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2018			182.8	71.1	56.4	2013-2018 Cadillac ATS Sedan	紧凑轿车	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	inc: ATS-V	gen1 compact sport sedan	2016-2019			184	71.3	55.7	2016-2019 Cadillac ATS-V Sedan	高性能紧凑轿车	可入库
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2020-2026 Cadillac CT4 / CT4-V / CT4-V Blackwing	紧凑轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020-2024 Cadillac CT5 / CT5-V	中型轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			193.8	74.1	57.2	2025-2026 Cadillac CT5 / CT5-V	中型轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Blackwing	gen1 midsize sport sedan facelift	2025-2026			194.9	74.1	56.5	2025-2026 Cadillac CT5-V Blackwing	高性能中型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	Std.	gen1 full-size sedan	2016			204	74	57.9	2016 Cadillac CT6	大型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	Std.	gen1 full-size sedan	2017-2018			204.1	74	58	2017-2018 Cadillac CT6	大型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2017-2018			204.1	74	58	2017-2018 Cadillac CT6 PHEV	大型插混轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	Std.	gen1 full-size sedan facelift	2019-2020			205.8	74	58	2019-2020 Cadillac CT6	大型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	Blackwing	gen1 full-size sport sedan facelift	2019-2020			205.8	74	58	2019-2020 Cadillac CT6-V Blackwing	高性能大型轿车	可入库
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011			189.3	74.1	56	2011 Cadillac CTS Coupe	双门轿跑长车身	可入库
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2012-2015			188.5	74.1	56	2012-2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003-2007 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen1 midsize sport sedan	2004-2007			191.5	70.6	57.3	2004-2007 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2009			191.6	72.5	58	2008-2009 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2010			191.6	72.5	59.2	2010 Cadillac CTS Sedan	中型轿车高车身	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2011-2013			191.3	72.5	58	2011-2013 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2009-2010			191.6	72.5	57.3	2009-2010 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2011-2013			191.3	72.5	57.3	2011-2013 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014-2019 Cadillac CTS / CTS-V Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010			191.6	72.6	59.1	2010 Cadillac CTS Wagon	旅行车高车身	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2011-2014			192	72.5	58	2011-2014 Cadillac CTS Wagon / CTS-V Wagon	旅行车	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-1998			194	70.3	56.3	1997-1998 Cadillac Catera	中型sedan	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1999			194	70.3	56.3		Catera过渡年	待终核: 1999
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2000-2001			192.2	70.3	56.4	2000-2001 Cadillac Catera	中型sedan	可入库
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014/2016 Cadillac ELR	插混双门	待补强: 2015
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2014			202.5	79	75.9	2009-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2002-2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

下一轮只剩两个点：补 Cadillac ELR 2015、Cadillac Catera 1999。确认后输出完整可替换 TSV，并给“本批次完成”。

下一步


--- Round 13 / 下一步 ---
更新点

车型	操作	描述
Cadillac Catera 1999	补强/拆分	1999 Catera 为 194.0×70.3×56.4，不能与 1997-1998 的 56.3 高度合并，因此保留单年并推进可入库。
Edmunds

Cadillac ELR 2015	补强/可入库	2015 ELR 通过第三方规格确认与 2014/2016 一致：186.0×72.7×55.9；2014/2016 Edmunds 同尺寸，2014-2016 推进可入库。
Edmunds
+2
Edmunds
+2

当前批次	完成	本批次所有记录已补强为可入库；完整代际口径已覆盖当前文件内 Cadillac 相关车型。

当前批次进度

状态	数量	说明
🟢 可入库	41	当前完整 TSV 全部可入库
🟡 待补强	0	无
🔴 关键缺口	0	无

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Cadillac ATS	Cadillac	跑车		Coupe	inc: ATS-V	gen1 compact coupe	2015-2019			184.7	72.5	55.3	2015-2019 Cadillac ATS Coupe / ATS-V Coupe	双门轿跑	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	Std.	gen1 compact sedan	2013-2018			182.8	71.1	56.4	2013-2018 Cadillac ATS Sedan	紧凑轿车	可入库
Cadillac ATS	Cadillac	三厢车		Sedan	inc: ATS-V	gen1 compact sport sedan	2016-2019			184	71.3	55.7	2016-2019 Cadillac ATS-V Sedan	高性能紧凑轿车	可入库
Cadillac CT4	Cadillac	三厢车		Sedan	inc: V/Blackwing	gen1 compact sedan	2020-2026			187.6	71.4	56	2020-2026 Cadillac CT4 / CT4-V / CT4-V Blackwing	紧凑轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2020-2024			193.8	74.1	57.2	2020-2024 Cadillac CT5 / CT5-V	中型轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2025-2026			193.8	74.1	57.2	2025-2026 Cadillac CT5 / CT5-V	中型轿车	可入库
Cadillac CT5	Cadillac	三厢车		Sedan	Blackwing	gen1 midsize sport sedan facelift	2025-2026			194.9	74.1	56.5	2025-2026 Cadillac CT5-V Blackwing	高性能中型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	Std.	gen1 full-size sedan	2016			204	74	57.9	2016 Cadillac CT6	大型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	Std.	gen1 full-size sedan	2017-2018			204.1	74	58	2017-2018 Cadillac CT6	大型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	PHEV	gen1 full-size sedan	2017-2018			204.1	74	58	2017-2018 Cadillac CT6 PHEV	大型插混轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	Std.	gen1 full-size sedan facelift	2019-2020			205.8	74	58	2019-2020 Cadillac CT6	大型轿车	可入库
Cadillac CT6	Cadillac	三厢车		Sedan	Blackwing	gen1 full-size sport sedan facelift	2019-2020			205.8	74	58	2019-2020 Cadillac CT6-V Blackwing	高性能大型轿车	可入库
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2011			189.3	74.1	56	2011 Cadillac CTS Coupe	双门轿跑长车身	可入库
Cadillac CTS	Cadillac	跑车		Coupe	inc: CTS-V	gen2 midsize coupe	2012-2015			188.5	74.1	56	2012-2015 Cadillac CTS Coupe / CTS-V Coupe	双门轿跑	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	2003-2007			190.1	70.6	56.7	2003-2007 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen1 midsize sport sedan	2004-2007			191.5	70.6	57.3	2004-2007 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2008-2009			191.6	72.5	58	2008-2009 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2010			191.6	72.5	59.2	2010 Cadillac CTS Sedan	中型轿车高车身	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	Std.	gen2 midsize sedan	2011-2013			191.3	72.5	58	2011-2013 Cadillac CTS Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2009-2010			191.6	72.5	57.3	2009-2010 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen2 midsize sport sedan	2011-2013			191.3	72.5	57.3	2011-2013 Cadillac CTS-V Sedan	高性能中型轿车	可入库
Cadillac CTS	Cadillac	三厢车		Sedan	inc: CTS-V	gen3 midsize sedan	2014-2019			197.6	72.2	57.2	2014-2019 Cadillac CTS / CTS-V Sedan	中型轿车	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2010			191.6	72.6	59.1	2010 Cadillac CTS Wagon	旅行车高车身	可入库
Cadillac CTS	Cadillac	两厢车		Wagon	inc: CTS-V	gen2 midsize wagon	2011-2014			192	72.5	58	2011-2014 Cadillac CTS Wagon / CTS-V Wagon	旅行车	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1997-1998			194	70.3	56.3	1997-1998 Cadillac Catera	中型sedan	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan	1999			194	70.3	56.4	1999 Cadillac Catera	中型sedan过渡年	可入库
Cadillac Catera	Cadillac	三厢车		Sedan	Std.	gen1 midsize sedan facelift	2000-2001			192.2	70.3	56.4	2000-2001 Cadillac Catera	中型sedan	可入库
Cadillac ELR	Cadillac	跑车		Coupe	PHEV	gen1 compact PHEV coupe	2014-2016			186	72.7	55.9	2014-2016 Cadillac ELR	插混双门	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen1 full-size SUV	1999-2000			201.2	77	74.3	1999-2000 Cadillac Escalade	初代短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen2 full-size SUV	2003-2006			221.4	79.5	75.7	2003-2006 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2007-2010			222.9	79.1	75.5	2007-2010 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV low-height	2011-2012			222.9	79.1	73.1	2011-2012 Cadillac Escalade ESV	长轴ESV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen3 full-size SUV	2013-2014			222.9	79.1	75.5	2013-2014 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen4 full-size SUV	2015-2020			224.3	80.5	74	2015-2020 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	ESV	gen5 full-size SUV	2021-2026			227	81.1	76.4	2021-2026 Cadillac Escalade ESV	长轴ESV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen2 full-size SUV	2002-2006			198.9	78.9	76.5	2002-2006 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV low-height	2007-2008			202.5	79	74.3	2007-2008 Cadillac Escalade	短轴全尺寸SUV低高度	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen3 full-size SUV	2009-2014			202.5	79	75.9	2009-2014 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen4 full-size SUV	2015-2020			203.9	80.5	74.4	2015-2020 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	越野车		SUV	Std.	gen5 full-size SUV	2021-2026			211.9	81.1	76.7	2021-2026 Cadillac Escalade	短轴全尺寸SUV	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.25	221.4	79.5	75.6	2002-2006 Cadillac Escalade EXT	Crew Cab短货斗	可入库
Cadillac Escalade	Cadillac	皮卡	Cadillac Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.25	222	79.1	74.5	2007-2013 Cadillac Escalade EXT	Crew Cab可变货斗	可入库

下一步优先核对

无。当前批次已全部可入库。

本批次完成。

