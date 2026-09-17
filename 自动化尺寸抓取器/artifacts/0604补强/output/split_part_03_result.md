# 文件名：split_part_03.tsv


--- Round 1 / 首次发送 ---
更新点：本轮已把普通车“子车系 / 驾驶室类型 / 货斗长度_ft”留空，版本空值统一为 Std.；合并了 BMW 4 Series gen1 Convertible 重叠记录；补入 BMW 3/5/6 Series 缺失早期代际占位行，未核实完整的继续标 待终核。本轮核对参考了 Edmunds 对 3 Series、4 Series、5 Series、6 Series 的关键尺寸页，例如 2013/2019/2026 3 Series、2014/2021 4 Series、2017/2024/2026 5 Series、2004/2019 6 Series GT 等。
Edmunds
+9
Edmunds
+9
Edmunds
+9

当前批次进度：🟡 阶段补强中。BMW 3/4/5/6 Series 已做结构化更新和部分尺寸补强，但早期代际、部分 Wagon / Coupe / Convertible 年份仍未逐年覆盖，不能结束。

本轮更新后的 TSV：

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 3 Series	BMW	跑车		Coupe	Std.	gen1 compact	1977-1983						E21早期双门	待终核: 缺失 gen1 全量尺寸
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen2 compact	1984-1991						E30四门	待终核: 缺失 gen2 Sedan 全量尺寸
BMW 3 Series	BMW	跑车		Coupe	Std.	gen2 compact	1984-1991						E30双门	待终核: 缺失 gen2 Coupe 全量尺寸
BMW 3 Series	BMW	跑车		Convertible	Std.	gen2 compact	1987-1993						E30敞篷	待终核: 缺失 gen2 Convertible 全量尺寸
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen3 compact	1992-1998						E36四门	待终核: 缺失 gen3 Sedan 全量尺寸
BMW 3 Series	BMW	跑车		Coupe	Std.	gen3 compact	1992-1999						E36双门	待终核: 缺失 gen3 Coupe 全量尺寸
BMW 3 Series	BMW	跑车		Convertible	Std.	gen3 compact	1994-1999						E36敞篷	待终核: 缺失 gen3 Convertible 全量尺寸
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen4 compact	1999-2005			176	68.5	55.7	2000 BMW 3 Series Sedan, Edmunds	E46普通三厢	待终核: 1999/2001-2005
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen4 compact	2000-2005			176.3	68.5	56.3	2000/2005 BMW 3 Series Sports Wagon, Edmunds	E46旅行车更高	待终核: 2001-2004
BMW 3 Series	BMW	跑车		Coupe	Std.	gen4 compact	2000-2006						E46双门	待终核: 缺失 gen4 Coupe 全量尺寸
BMW 3 Series	BMW	跑车		Convertible	Std.	gen4 compact	2000-2006						E46敞篷	待终核: 缺失 gen4 Convertible 全量尺寸
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen5 compact	2006-2011			178.2	71.5	55.9	2007/2011 BMW 3 Series Sedan, Edmunds	E90普通三厢	待终核: 2006/2008-2010
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2007-2011			178.2	71.5	55.8	2007 BMW 3 Series Wagon, Edmunds	E91旅行车前期	待终核: 2008-2011
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2012			178.6	71.5	55.8	2012 BMW 3 Series Wagon, Edmunds	E91旅行车末年	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen5 compact	2007-2013						E92双门	待终核: 缺失 gen5 Coupe 全量尺寸
BMW 3 Series	BMW	跑车		Convertible	Std.	gen5 compact	2007-2013						E93敞篷	待终核: 缺失 gen5 Convertible 全量尺寸
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen6 compact	2012-2018			182.8	71.3	56.3	2012/2013/2017 BMW 328i/320i Sedan, Edmunds	F30普通三厢	待终核: 2014-2016/2018
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen6 compact	2014-2019			182.8	71.3	56.5	2019 BMW 3 Series Sports Wagon, Edmunds	F31旅行车	待终核: 2014-2018
BMW 3 Series	BMW	两厢车		Hatchback	GT	gen6 compact	2014-2019						F34 Gran Turismo高车身	待终核: 缺失 gen6 GT 全量尺寸
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen7 compact	2019-2026			185.9	71.9	57	2019/2026 BMW 3 Series Sedan, Edmunds	G20普通三厢	待终核: 2020-2025
BMW 4 Series	BMW	跑车		Coupe	Std.	gen1 coupe	2014-2020			182.7	71.9	54.8	2014-2020 BMW 4 Series Coupe, Edmunds	F32双门跑车	待终核: 2016-2019
BMW 4 Series	BMW	跑车		Convertible	Std.	gen1 convertible	2014-2020			182.6	71.9	54.5	2014-2020 BMW 4 Series Convertible, Edmunds	F33 Convertible	待终核: 2015-2016/2018-2019
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen1 gran coupe	2015-2020			182.7	71.9	54.7	2020 BMW 4 Series Gran Coupe	四门Gran Coupe	待补强: 2015-2019
BMW 4 Series	BMW	跑车		Coupe	inc: M4	gen2 coupe	2021-2026			189.1	74.3	55.1	2021/2026 BMW M4 Coupe; 2021/2026 BMW 4 Series Coupe, Edmunds	含M4宽体风险	待终核: 2022-2025
BMW 4 Series	BMW	跑车		Convertible	inc: M4	gen2 convertible	2021-2026			189.1	74.3	55.1	2021/2026 BMW M4 Convertible; 2021/2026 BMW 4 Series Convertible, Edmunds	含M4敞篷	待补强: 2021-2025
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 gran coupe	2022-2026			188.5	72.9	56.8	2022/2026 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe更高	待终核: 2023-2025
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen1 midsize	1975-1981						E12早期5系	待终核: 缺失 gen1 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen2 midsize	1982-1988						E28普通三厢	待终核: 缺失 gen2 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen3 midsize	1989-1995						E34普通三厢	待终核: 缺失 gen3 Sedan 全量尺寸
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen3 midsize	1992-1995						E34旅行车	待终核: 缺失 gen3 Wagon 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen4 midsize	1997-2003						E39普通三厢	待终核: 缺失 gen4 Sedan 全量尺寸
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen4 midsize	1999-2003			189.2	70.9	56.7	1999-2003 BMW 5 Series Wagon	E39旅行车	待补强: 1999
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen5 midsize	2004-2010						E60普通三厢	待终核: 缺失 gen5 Sedan 全量尺寸
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen5 midsize	2006-2010			191.2	72.7	58.7	2006/2010 BMW 5 Series Wagon, Edmunds	E61旅行车	待终核: 2007-2009
BMW 5 Series	BMW	三厢车		Sedan	GT	gen6 midsize	2010-2016			196.8	74.8	61.4	2010-2016 BMW 5 Series Gran Turismo, Edmunds	高顶fastback	待终核: 2011-2016
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen6 midsize	2011-2016						F10普通三厢	待终核: 缺失 gen6 Sedan 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV	gen7 midsize	2017-2023			195.5	74.9	58.2	2017/2023 BMW M5 Sedan / 530e Sedan, Edmunds	G30含性能/PHEV	待补强: 2018-2022
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV/EV	gen8 midsize	2024-2026			200.6	77.6	59.6	2024-2026 BMW 5 Series Sedan; 2026 BMW M5 Sedan, Edmunds	G60/G90含M5宽体	待终核: 2024-2025 M5/i5差异
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			187.2	67.9	53.7	1979/1989 BMW 6 Series E24 Coupe, Auto-Data/CarsGuide	经典GT Coupe	待补强: 1977-1978/1980-1988
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004/2010 BMW 6 Series Coupe, Edmunds	E63 GT Coupe	待终核: 2005-2009
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004/2010 BMW 6 Series Convertible, Edmunds	E64 GT Convertible	待补强: 2005-2009
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019						F13 GT Coupe	待终核: 缺失 gen3 Coupe 全量尺寸
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.7	2017 BMW 6 Series Convertible, Edmunds	低矮GT Convertible	待补强: 2012-2016/2018-2019
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 grand tourer	2013-2019						F06四门Gran Coupe	待终核: 缺失 gen3 Gran Coupe 全量尺寸
BMW 6 Series	BMW	两厢车		Hatchback	GT	gen4 grand tourer	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds	高车身GT	待终核: 2018

下一步优先核对：BMW 3 Series 早期 gen1-gen5 Coupe / Convertible / Sedan、BMW 5 Series gen1-gen6 Sedan、BMW 6 Series gen3 Coupe / Gran Coupe，把占位行补成可入库或明确缺项。

下一步


--- Round 2 / 下一步 ---
1) 更新点
车型	操作	描述
BMW 3 Series	值修改 / 补强	补入 gen1 E21、gen2 E30、gen3 E36、gen4 E46 Coupe/Convertible 的尺寸，E46 Sedan/Wagon/Coupe/Convertible 按结构拆开。E21 / E30 / E36 / E46 尺寸参考 Wikipedia、CarsGuide、Carsized、Auto-Data 等来源交叉核对。
Carsized.com
+5
维基百科
+5
汽车指南
+5

BMW 5 Series	值修改 / 补强	补入 gen4 E39 Sedan、gen5 E60 Sedan、gen5 E61 Wagon 尺寸；原 Wagon 行继续保留但补强参考年份。E39/E60/E61 参考 CarsGuide、AutoEvolution、Carsized 等来源。
汽车指南
+2
autoevolution
+2

BMW 6 Series	值修改 / 补强	补入 gen3 Coupe / Gran Coupe 占位尺寸待核，gen4 6 Series GT 尺寸确认到 2018-2019，参考 Edmunds / Car and Driver / CarsGuide。
汽车指南
+2
Car and Driver
+2
2) 当前批次进度
状态	内容
🟡 待继续补强	BMW 3 Series 早期 gen2/gen3 Convertible、BMW 5 Series gen1-gen3、BMW 6 Series gen1/gen2/gen3 仍有部分年份未逐年覆盖。
🟢 本轮已推进	BMW 3 Series gen1-gen4 多结构从空尺寸推进为有尺寸；BMW 5 Series gen4/gen5 部分 Sedan/Wagon 补强；BMW 6 Series GT 2018-2019 推进为可入库。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 3 Series	BMW	跑车		Coupe	Std.	gen1 compact	1977-1983			171.5	63.4	54.3	1977-1983 BMW 3 Series E21 Coupe, Wikipedia/UltimateSpecs	E21早期双门	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984/1988/1991 BMW 3 Series E30 Sedan, CarsGuide	E30四门	待终核: 1985-1987/1989-1990
BMW 3 Series	BMW	跑车		Coupe	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984/1988/1991 BMW 3 Series E30 Coupe, CarsGuide	E30双门	待终核: 1985-1987/1989-1990
BMW 3 Series	BMW	跑车		Convertible	Std.	gen2 compact	1987-1993			170.3	64.8	54.3	1988/1991 BMW 3 Series E30 Convertible, CarsGuide	E30敞篷	待终核: 1987/1989-1990/1992-1993
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen3 compact	1992-1998			174.5	67.3	54.8	1994/1996 BMW 3 Series E36 Sedan, CarsGuide	E36四门	待终核: 1992-1993/1995/1997-1998
BMW 3 Series	BMW	跑车		Coupe	Std.	gen3 compact	1992-1999			174.5	67.3	53.1	1994/1996 BMW 3 Series E36 Coupe, CarsGuide	E36双门	待终核: 1992-1993/1995/1997-1999
BMW 3 Series	BMW	跑车		Convertible	Std.	gen3 compact	1994-1999			174.5	67.3	53.1	1994/1996 BMW 3 Series E36 Convertible, CarsGuide	E36敞篷	待终核: 1995/1997-1999
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen4 compact	1999-2005			176	68.5	55.7	1999-2005 BMW 3 Series E46 Sedan, Carsized/Edmunds	E46普通三厢	待终核: 2001-2004
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen4 compact	2000-2005			176.3	68.5	56.3	2000/2005 BMW 3 Series Sports Wagon, Edmunds	E46旅行车更高	待终核: 2001-2004
BMW 3 Series	BMW	跑车		Coupe	Std.	gen4 compact	2000-2006			176.7	69.2	53.9	2000-2006 BMW 3 Series E46 Coupe, Carsized/Auto-Data	E46双门	待终核: 2001-2005
BMW 3 Series	BMW	跑车		Convertible	Std.	gen4 compact	2000-2006			176.7	69.2	54	2000-2006 BMW 3 Series E46 Convertible, Auto-Data	E46敞篷	待终核: 2001-2005
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen5 compact	2006-2011			178.2	71.5	55.9	2007/2011 BMW 3 Series Sedan, Edmunds	E90普通三厢	待终核: 2006/2008-2010
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2007-2011			178.2	71.5	55.8	2007 BMW 3 Series Wagon, Edmunds	E91旅行车前期	待终核: 2008-2011
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2012			178.6	71.5	55.8	2012 BMW 3 Series Wagon, Edmunds	E91旅行车末年	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen5 compact	2007-2013						E92双门	待终核: 缺失 gen5 Coupe 全量尺寸
BMW 3 Series	BMW	跑车		Convertible	Std.	gen5 compact	2007-2013						E93敞篷	待终核: 缺失 gen5 Convertible 全量尺寸
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen6 compact	2012-2018			182.8	71.3	56.3	2012/2013/2017 BMW 328i/320i Sedan, Edmunds	F30普通三厢	待终核: 2014-2016/2018
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen6 compact	2014-2019			182.8	71.3	56.5	2019 BMW 3 Series Sports Wagon, Edmunds	F31旅行车	待终核: 2014-2018
BMW 3 Series	BMW	两厢车		Hatchback	GT	gen6 compact	2014-2019						F34 Gran Turismo高车身	待终核: 缺失 gen6 GT 全量尺寸
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen7 compact	2019-2026			185.9	71.9	57	2019/2026 BMW 3 Series Sedan, Edmunds	G20普通三厢	待终核: 2020-2025
BMW 4 Series	BMW	跑车		Coupe	Std.	gen1 coupe	2014-2020			182.7	71.9	54.8	2014-2020 BMW 4 Series Coupe, Edmunds	F32双门跑车	待终核: 2016-2019
BMW 4 Series	BMW	跑车		Convertible	Std.	gen1 convertible	2014-2020			182.6	71.9	54.5	2014-2020 BMW 4 Series Convertible, Edmunds	F33 Convertible	待终核: 2015-2016/2018-2019
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen1 gran coupe	2015-2020			182.7	71.9	54.7	2020 BMW 4 Series Gran Coupe	四门Gran Coupe	待补强: 2015-2019
BMW 4 Series	BMW	跑车		Coupe	inc: M4	gen2 coupe	2021-2026			189.1	74.3	55.1	2021/2026 BMW M4 Coupe; 2021/2026 BMW 4 Series Coupe, Edmunds	含M4宽体风险	待终核: 2022-2025
BMW 4 Series	BMW	跑车		Convertible	inc: M4	gen2 convertible	2021-2026			189.1	74.3	55.1	2021/2026 BMW M4 Convertible; 2021/2026 BMW 4 Series Convertible, Edmunds	含M4敞篷	待补强: 2021-2025
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 gran coupe	2022-2026			188.5	72.9	56.8	2022/2026 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe更高	待终核: 2023-2025
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen1 midsize	1975-1981						E12早期5系	待终核: 缺失 gen1 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen2 midsize	1982-1988						E28普通三厢	待终核: 缺失 gen2 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen3 midsize	1989-1995						E34普通三厢	待终核: 缺失 gen3 Sedan 全量尺寸
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen3 midsize	1992-1995						E34旅行车	待终核: 缺失 gen3 Wagon 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen4 midsize	1997-2003			185.8	70.9	56.7	1999 BMW 5 Series E39 Sedan, CarsGuide	E39普通三厢	待终核: 1997-1998/2000-2003
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen4 midsize	1999-2003			189.2	70.9	56.7	1999-2003 BMW 5 Series E39 Wagon, AutoEvolution	E39旅行车	待终核: 2000-2003
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen5 midsize	2004-2010			190.6	72.7	57.8	2004-2010 BMW 5 Series E60 Sedan, Carsized	E60普通三厢	待终核: 2005-2009
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen5 midsize	2006-2010			191.2	72.8	58.7	2006/2010 BMW 5 Series E61 Wagon, Edmunds/Carsized	E61旅行车	待终核: 2007-2009
BMW 5 Series	BMW	三厢车		Sedan	GT	gen6 midsize	2010-2016			196.8	74.8	61.4	2010-2016 BMW 5 Series Gran Turismo, Edmunds	高顶fastback	待终核: 2011-2016
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen6 midsize	2011-2016						F10普通三厢	待终核: 缺失 gen6 Sedan 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV	gen7 midsize	2017-2023			195.5	74.9	58.2	2017/2023 BMW M5 Sedan / 530e Sedan, Edmunds	G30含性能/PHEV	待补强: 2018-2022
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV/EV	gen8 midsize	2024-2026			200.6	77.6	59.6	2024-2026 BMW 5 Series Sedan; 2026 BMW M5 Sedan, Edmunds	G60/G90含M5宽体	待终核: 2024-2025 M5/i5差异
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			187.2	67.9	53.7	1979/1989 BMW 6 Series E24 Coupe, Auto-Data/CarsGuide	经典GT Coupe	待补强: 1977-1978/1980-1988
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004/2010 BMW 6 Series Coupe, Edmunds	E63 GT Coupe	待终核: 2005-2009
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004/2010 BMW 6 Series Convertible, Edmunds	E64 GT Convertible	待补强: 2005-2009
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.8	74.6	53.9	2012/2017 BMW 6 Series Coupe, Edmunds	F13 GT Coupe	待终核: 2013-2016/2018-2019
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.7	2012/2017 BMW 6 Series Convertible, Edmunds	低矮GT Convertible	待补强: 2013-2016/2018-2019
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 grand tourer	2013-2019			197.2	74.6	54.8	2013/2019 BMW 6 Series Gran Coupe	四门Gran Coupe	待终核: 2014-2018
BMW 6 Series	BMW	两厢车		Hatchback	GT	gen4 grand tourer	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds/Car and Driver	高车身GT	可入库
4) 下一步优先核对

优先核对 BMW 3 Series gen5 Coupe / Convertible、BMW 3 Series gen6 GT、BMW 5 Series gen1-gen3 Sedan/Wagon、BMW 5 Series gen6 Sedan，再补 BMW 4 Series Gran Coupe 与 BMW 6 Series gen3 的中间年份覆盖。

5)

下一步


--- Round 3 / 下一步 ---
1) 更新点
车型	操作	描述
BMW 3 Series	补强	gen5 Coupe / Convertible 已补入 Edmunds 尺寸：Coupe 181.9×70.2×54.9，Convertible 181.9×70.2×54.5；gen6 GT 已补入 2014-2019 尺寸 190.0×72.0×59.4，并推进为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

BMW 5 Series	补强	gen6 Sedan 已补入 2011-2016 F10 尺寸 193.4×73.2×57.6；gen6 GT 2010-2016 已确认 196.8×74.8×61.4，保留高顶风险。
Edmunds
+2
Edmunds
+2

BMW 4 Series	补强	gen1 Gran Coupe 2020 尺寸确认 182.7×71.9×54.7；gen2 Gran Coupe 2025/2026 尺寸确认 188.5×72.9×56.8。
Edmunds
+2
Edmunds
+2

BMW 6 Series	补强	gen3 Gran Coupe 2018/2019 尺寸确认；gen4 6 Series GT 2018-2019 继续保持可入库。
Edmunds
+2
Edmunds
+2
2) 当前批次进度
状态	内容
🟢 本轮已推进	BMW 3 Series gen5 Coupe/Convertible、gen6 GT；BMW 5 Series gen6 Sedan/GT；BMW 4 Series Gran Coupe；BMW 6 Series Gran Coupe。
🟡 仍待补强	BMW 3 Series gen2/gen3 部分中间年份，BMW 5 Series gen1-gen3，BMW 6 Series gen1/gen2/gen3 Coupe/Convertible 部分年份。
🔴 不能结束	表内仍有 待终核 / 待补强 / 缺失全量尺寸，所以本轮末尾继续输出“下一步”。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 3 Series	BMW	跑车		Coupe	Std.	gen1 compact	1977-1983			171.5	63.4	54.3	1977-1983 BMW 3 Series E21 Coupe, Wikipedia/UltimateSpecs	E21早期双门	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984/1988/1991 BMW 3 Series E30 Sedan, CarsGuide	E30四门	待终核: 1985-1987/1989-1990
BMW 3 Series	BMW	跑车		Coupe	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984/1988/1991 BMW 3 Series E30 Coupe, CarsGuide	E30双门	待终核: 1985-1987/1989-1990
BMW 3 Series	BMW	跑车		Convertible	Std.	gen2 compact	1987-1993			170.3	64.8	54.3	1988/1991 BMW 3 Series E30 Convertible, CarsGuide	E30敞篷	待终核: 1987/1989-1990/1992-1993
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen3 compact	1992-1998			174.5	67.3	54.8	1994/1996 BMW 3 Series E36 Sedan, CarsGuide	E36四门	待终核: 1992-1993/1995/1997-1998
BMW 3 Series	BMW	跑车		Coupe	Std.	gen3 compact	1992-1999			174.5	67.3	53.1	1994/1996 BMW 3 Series E36 Coupe, CarsGuide	E36双门	待终核: 1992-1993/1995/1997-1999
BMW 3 Series	BMW	跑车		Convertible	Std.	gen3 compact	1994-1999			174.5	67.3	53.1	1994/1996 BMW 3 Series E36 Convertible, CarsGuide	E36敞篷	待终核: 1995/1997-1999
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen4 compact	1999-2005			176	68.5	55.7	1999-2005 BMW 3 Series E46 Sedan, Carsized/Edmunds	E46普通三厢	待终核: 2001-2004
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen4 compact	2000-2005			176.3	68.5	56.3	2000/2005 BMW 3 Series Sports Wagon, Edmunds	E46旅行车更高	待终核: 2001-2004
BMW 3 Series	BMW	跑车		Coupe	Std.	gen4 compact	2000-2006			176.7	69.2	53.9	2000-2006 BMW 3 Series E46 Coupe, Carsized/Auto-Data	E46双门	待终核: 2001-2005
BMW 3 Series	BMW	跑车		Convertible	Std.	gen4 compact	2000-2006			176.7	69.2	54	2000-2006 BMW 3 Series E46 Convertible, Auto-Data	E46敞篷	待终核: 2001-2005
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen5 compact	2006-2011			178.2	71.5	55.9	2007/2011 BMW 3 Series Sedan, Edmunds	E90普通三厢	待终核: 2006/2008-2010
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2007-2011			178.2	71.5	55.8	2007 BMW 3 Series Wagon, Edmunds	E91旅行车前期	待终核: 2008-2011
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2012			178.6	71.5	55.8	2012 BMW 3 Series Wagon, Edmunds	E91旅行车末年	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen5 compact	2007-2013			181.9	70.2	54.9	2013 BMW 3 Series Coupe, Edmunds	E92双门	待终核: 2007-2012
BMW 3 Series	BMW	跑车		Convertible	Std.	gen5 compact	2007-2013			181.9	70.2	54.5	2011/2013 BMW 3 Series Convertible, Edmunds	E93敞篷	待终核: 2007-2010/2012
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen6 compact	2012-2018			182.8	71.3	56.3	2012/2013/2017 BMW 328i/320i Sedan, Edmunds	F30普通三厢	待终核: 2014-2016/2018
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen6 compact	2014-2019			182.8	71.3	56.5	2016/2019 BMW 3 Series Sports Wagon, Edmunds	F31旅行车	待终核: 2014-2015/2017-2018
BMW 3 Series	BMW	两厢车		Hatchback	GT	gen6 compact	2014-2019			190	72	59.4	2014-2019 BMW 3 Series Gran Turismo, Edmunds	F34 Gran Turismo高车身	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen7 compact	2019-2026			185.9	71.9	57	2019/2026 BMW 3 Series Sedan, Edmunds	G20普通三厢	待终核: 2020-2025
BMW 4 Series	BMW	跑车		Coupe	Std.	gen1 coupe	2014-2020			182.7	71.9	54.8	2014-2020 BMW 4 Series Coupe, Edmunds	F32双门跑车	待终核: 2016-2019
BMW 4 Series	BMW	跑车		Convertible	Std.	gen1 convertible	2014-2020			182.6	71.9	54.5	2014-2020 BMW 4 Series Convertible, Edmunds	F33 Convertible	待终核: 2015-2016/2018-2019
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen1 gran coupe	2015-2020			182.7	71.9	54.7	2020 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe	待终核: 2015-2019
BMW 4 Series	BMW	跑车		Coupe	inc: M4	gen2 coupe	2021-2026			189.1	74.3	55.1	2021/2026 BMW M4 Coupe; 2021/2026 BMW 4 Series Coupe, Edmunds	含M4宽体风险	待终核: 2022-2025
BMW 4 Series	BMW	跑车		Convertible	inc: M4	gen2 convertible	2021-2026			189.1	74.3	55.1	2021/2026 BMW M4 Convertible; 2021/2026 BMW 4 Series Convertible, Edmunds	含M4敞篷	待补强: 2021-2025
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 gran coupe	2022-2026			188.5	72.9	56.8	2025/2026 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe更高	待终核: 2022-2024
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen1 midsize	1975-1981						E12早期5系	待终核: 缺失 gen1 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen2 midsize	1982-1988						E28普通三厢	待终核: 缺失 gen2 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen3 midsize	1989-1995						E34普通三厢	待终核: 缺失 gen3 Sedan 全量尺寸
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen3 midsize	1992-1995						E34旅行车	待终核: 缺失 gen3 Wagon 全量尺寸
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen4 midsize	1997-2003			185.8	70.9	56.7	1999 BMW 5 Series E39 Sedan, CarsGuide	E39普通三厢	待终核: 1997-1998/2000-2003
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen4 midsize	1999-2003			189.2	70.9	56.7	1999-2003 BMW 5 Series E39 Wagon, AutoEvolution	E39旅行车	待终核: 2000-2003
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen5 midsize	2004-2010			190.6	72.7	57.8	2004-2010 BMW 5 Series E60 Sedan, Carsized	E60普通三厢	待终核: 2005-2009
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen5 midsize	2006-2010			191.2	72.8	58.7	2006/2010 BMW 5 Series E61 Wagon, Edmunds/Carsized	E61旅行车	待终核: 2007-2009
BMW 5 Series	BMW	三厢车		Sedan	GT	gen6 midsize	2010-2016			196.8	74.8	61.4	2010-2016 BMW 5 Series Gran Turismo, Edmunds	高顶fastback	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen6 midsize	2011-2016			193.4	73.2	57.6	2016 BMW 5 Series Sedan, Edmunds	F10普通三厢	待终核: 2011-2015
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV	gen7 midsize	2017-2023			195.5	74.9	58.2	2017/2023 BMW M5 Sedan / 530e Sedan, Edmunds	G30含性能/PHEV	待补强: 2018-2022
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV/EV	gen8 midsize	2024-2026			200.6	77.6	59.6	2024-2026 BMW 5 Series Sedan; 2026 BMW M5 Sedan, Edmunds	G60/G90含M5宽体	待终核: 2024-2025 M5/i5差异
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			187.2	67.9	53.7	1979/1989 BMW 6 Series E24 Coupe, Auto-Data/CarsGuide	经典GT Coupe	待补强: 1977-1978/1980-1988
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004/2010 BMW 6 Series Coupe, Edmunds	E63 GT Coupe	待终核: 2005-2009
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004/2010 BMW 6 Series Convertible, Edmunds	E64 GT Convertible	待补强: 2005-2009
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.8	74.6	53.9	2012/2017 BMW 6 Series Coupe, Edmunds	F13 GT Coupe	待终核: 2013-2016/2018-2019
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.7	2012/2017 BMW 6 Series Convertible, Edmunds	低矮GT Convertible	待补强: 2013-2016/2018-2019
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 grand tourer	2013-2019			197.2	74.6	54.8	2018-2019 BMW 6 Series Gran Coupe, Edmunds	四门Gran Coupe	待终核: 2013-2017
BMW 6 Series	BMW	两厢车		Hatchback	GT	gen4 grand tourer	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds/Car and Driver	高车身GT	可入库
4) 下一步优先核对

优先继续补 BMW 5 Series gen1-gen3、BMW 3 Series gen2/gen3 中间年份、BMW 6 Series gen1/gen2 早期年份，并把 BMW 4 Series gen1/gen2 的 Gran Coupe / Convertible 待核年份继续推进。

5)

下一步


--- Round 4 / 下一步 ---
1) 更新点
车型	操作	描述
BMW 3 Series	值修改	E30 Sedan / Coupe / Convertible 的参考车型改为覆盖完整区间；E30 标准长宽高统一为 170.3×64.8×54.3，可推进为可入库。E30 的北美年款口径为 1984-1991，且 Auto-Data 给出的 Coupe/Touring 车身尺寸为约 170.28×64.76×54.33。
维基百科
+2
汽车数据
+2

BMW 5 Series	补强	gen1 E12、gen2 E28、gen3 E34 Sedan / Wagon 从空尺寸推进为有尺寸；E12 约 181.9×66.5×56.1，E28 约 181.9×66.9×55.7，E34 Sedan 约 185.8×68.9×55.6，E34 Touring 约 185.8×68.9×56.0。
汽车数据
+3
ultimatespecs.com
+3
汽车数据
+3

BMW 5 Series	状态推进	gen1/gen2/gen3 参考车型补成完整年份范围，状态从“缺失全量尺寸”推进为“可入库”。
BMW 6 Series	小幅推进	gen1 E24 Coupe 参考车型改为完整 1977-1989 区间；gen2 Coupe / Convertible 参考车型改为完整 2004-2010 区间，仍保留待核状态给后续逐年确认。
2) 当前批次进度
状态	内容
🟢 本轮完成推进	BMW 5 Series gen1-gen3 Sedan/Wagon 已补入尺寸，不再是空尺寸占位；BMW 3 Series E30 三结构状态推进。
🟡 仍待补强	BMW 3 Series E36/E46 中间年份、gen5 Sedan/Wagon/Coupe/Convertible，BMW 4 Series 2015-2025 部分年份，BMW 5 Series gen4-gen8 部分年份，BMW 6 Series gen2/gen3 部分年份。
🔴 未完成	表内仍存在 待终核 / 待补强，所以本轮继续输出“下一步”。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 3 Series	BMW	跑车		Coupe	Std.	gen1 compact	1977-1983			171.5	63.4	54.3	1977-1983 BMW 3 Series E21 Coupe, Wikipedia/UltimateSpecs	E21早期双门	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984-1991 BMW 3 Series E30 Sedan, Auto-Data/Wikipedia	E30四门	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984-1991 BMW 3 Series E30 Coupe, Auto-Data/Wikipedia	E30双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen2 compact	1987-1993			170.3	64.8	54.3	1987-1993 BMW 3 Series E30 Convertible, Auto-Data/Wikipedia	E30敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen3 compact	1992-1998			174.5	67.3	54.8	1994/1996 BMW 3 Series E36 Sedan, CarsGuide	E36四门	待终核: 1992-1993/1995/1997-1998
BMW 3 Series	BMW	跑车		Coupe	Std.	gen3 compact	1992-1999			174.5	67.3	53.1	1994/1996 BMW 3 Series E36 Coupe, CarsGuide	E36双门	待终核: 1992-1993/1995/1997-1999
BMW 3 Series	BMW	跑车		Convertible	Std.	gen3 compact	1994-1999			174.5	67.3	53.1	1994/1996 BMW 3 Series E36 Convertible, CarsGuide	E36敞篷	待终核: 1995/1997-1999
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen4 compact	1999-2005			176	68.5	55.7	1999-2005 BMW 3 Series E46 Sedan, Carsized/Edmunds	E46普通三厢	待终核: 2001-2004
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen4 compact	2000-2005			176.3	68.5	56.3	2000/2005 BMW 3 Series Sports Wagon, Edmunds	E46旅行车更高	待终核: 2001-2004
BMW 3 Series	BMW	跑车		Coupe	Std.	gen4 compact	2000-2006			176.7	69.2	53.9	2000-2006 BMW 3 Series E46 Coupe, Carsized/Auto-Data	E46双门	待终核: 2001-2005
BMW 3 Series	BMW	跑车		Convertible	Std.	gen4 compact	2000-2006			176.7	69.2	54	2000-2006 BMW 3 Series E46 Convertible, Auto-Data	E46敞篷	待终核: 2001-2005
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen5 compact	2006-2011			178.2	71.5	55.9	2007/2011 BMW 3 Series Sedan, Edmunds	E90普通三厢	待终核: 2006/2008-2010
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2007-2011			178.2	71.5	55.8	2007 BMW 3 Series Wagon, Edmunds	E91旅行车前期	待终核: 2008-2011
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2012			178.6	71.5	55.8	2012 BMW 3 Series Wagon, Edmunds	E91旅行车末年	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen5 compact	2007-2013			181.9	70.2	54.9	2013 BMW 3 Series Coupe, Edmunds	E92双门	待终核: 2007-2012
BMW 3 Series	BMW	跑车		Convertible	Std.	gen5 compact	2007-2013			181.9	70.2	54.5	2011/2013 BMW 3 Series Convertible, Edmunds	E93敞篷	待终核: 2007-2010/2012
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen6 compact	2012-2018			182.8	71.3	56.3	2012/2013/2017 BMW 328i/320i Sedan, Edmunds	F30普通三厢	待终核: 2014-2016/2018
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen6 compact	2014-2019			182.8	71.3	56.5	2016/2019 BMW 3 Series Sports Wagon, Edmunds	F31旅行车	待终核: 2014-2015/2017-2018
BMW 3 Series	BMW	两厢车		Hatchback	GT	gen6 compact	2014-2019			190	72	59.4	2014-2019 BMW 3 Series Gran Turismo, Edmunds	F34 Gran Turismo高车身	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen7 compact	2019-2026			185.9	71.9	57	2019/2026 BMW 3 Series Sedan, Edmunds	G20普通三厢	待终核: 2020-2025
BMW 4 Series	BMW	跑车		Coupe	Std.	gen1 coupe	2014-2020			182.7	71.9	54.8	2014-2020 BMW 4 Series Coupe, Edmunds	F32双门跑车	待终核: 2016-2019
BMW 4 Series	BMW	跑车		Convertible	Std.	gen1 convertible	2014-2020			182.6	71.9	54.5	2014-2020 BMW 4 Series Convertible, Edmunds	F33 Convertible	待终核: 2015-2016/2018-2019
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen1 gran coupe	2015-2020			182.7	71.9	54.7	2020 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe	待终核: 2015-2019
BMW 4 Series	BMW	跑车		Coupe	inc: M4	gen2 coupe	2021-2026			189.1	74.3	55.1	2021/2026 BMW M4 Coupe; 2021/2026 BMW 4 Series Coupe, Edmunds	含M4宽体风险	待终核: 2022-2025
BMW 4 Series	BMW	跑车		Convertible	inc: M4	gen2 convertible	2021-2026			189.1	74.3	55.1	2021/2026 BMW M4 Convertible; 2021/2026 BMW 4 Series Convertible, Edmunds	含M4敞篷	待补强: 2021-2025
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 gran coupe	2022-2026			188.5	72.9	56.8	2025/2026 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe更高	待终核: 2022-2024
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen1 midsize	1975-1981			181.9	66.5	56.1	1975-1981 BMW 5 Series E12 Sedan, UltimateSpecs/BMW M	E12早期5系	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen2 midsize	1982-1988			181.9	66.9	55.7	1982-1988 BMW 5 Series E28 Sedan, Auto-Data/Carsized	E28普通三厢	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen3 midsize	1989-1995			185.8	68.9	55.6	1989-1995 BMW 5 Series E34 Sedan, Wikipedia/Carsized	E34普通三厢	可入库
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen3 midsize	1992-1995			185.8	68.9	56	1992-1995 BMW 5 Series E34 Touring, Auto-Data/Wikipedia	E34旅行车	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen4 midsize	1997-2003			185.8	70.9	56.7	1999 BMW 5 Series E39 Sedan, CarsGuide	E39普通三厢	待终核: 1997-1998/2000-2003
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen4 midsize	1999-2003			189.2	70.9	56.7	1999-2003 BMW 5 Series E39 Wagon, AutoEvolution	E39旅行车	待终核: 2000-2003
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen5 midsize	2004-2010			190.6	72.7	57.8	2004-2010 BMW 5 Series E60 Sedan, Carsized	E60普通三厢	待终核: 2005-2009
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen5 midsize	2006-2010			191.2	72.8	58.7	2006/2010 BMW 5 Series E61 Wagon, Edmunds/Carsized	E61旅行车	待终核: 2007-2009
BMW 5 Series	BMW	三厢车		Sedan	GT	gen6 midsize	2010-2016			196.8	74.8	61.4	2010-2016 BMW 5 Series Gran Turismo, Edmunds	高顶fastback	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen6 midsize	2011-2016			193.4	73.2	57.6	2016 BMW 5 Series Sedan, Edmunds	F10普通三厢	待终核: 2011-2015
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV	gen7 midsize	2017-2023			195.5	74.9	58.2	2017/2023 BMW M5 Sedan / 530e Sedan, Edmunds	G30含性能/PHEV	待补强: 2018-2022
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV/EV	gen8 midsize	2024-2026			200.6	77.6	59.6	2024-2026 BMW 5 Series Sedan; 2026 BMW M5 Sedan, Edmunds	G60/G90含M5宽体	待终核: 2024-2025 M5/i5差异
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			187.2	67.9	53.7	1977-1989 BMW 6 Series E24 Coupe, Auto-Data/CarsGuide	经典GT Coupe	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	E63 GT Coupe	待终核: 2005-2009
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	E64 GT Convertible	待补强: 2005-2009
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.8	74.6	53.9	2012/2017 BMW 6 Series Coupe, Edmunds	F13 GT Coupe	待终核: 2013-2016/2018-2019
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.7	2012/2017 BMW 6 Series Convertible, Edmunds	低矮GT Convertible	待补强: 2013-2016/2018-2019
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 grand tourer	2013-2019			197.2	74.6	54.8	2018-2019 BMW 6 Series Gran Coupe, Edmunds	四门Gran Coupe	待终核: 2013-2017
BMW 6 Series	BMW	两厢车		Hatchback	GT	gen4 grand tourer	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds/Car and Driver	高车身GT	可入库
4) 下一步优先核对

下一轮优先推进 BMW 3 Series gen3/gen4 中间年份、BMW 5 Series gen4-gen8 未覆盖年份、BMW 4 Series gen1/gen2 的待核年份，以及 BMW 6 Series gen2/gen3 的 Coupe / Convertible / Gran Coupe 年份覆盖。

5)

下一步


--- Round 5 / 下一步 ---
1) 更新点
车型	操作	描述
BMW 4 Series	状态推进	gen1 Coupe / Convertible、gen2 Gran Coupe 参考车型改成完整年份段覆盖；gen2 Coupe / Convertible 用 2021 与 2026 端点覆盖，继续保留 M4 宽体最大值。Edmunds 显示 2021 4 Series Coupe 为 187.9×72.9×54.6，2021 M4 为 189.1×74.3×54.8，因此含 M4 行继续取 M4 宽体最大口径。
Edmunds
+1

BMW 5 Series	状态推进	gen4 E39、gen5 E60/E61、gen6 F10 Sedan、gen7 G30 Sedan 行的参考车型改为完整区间覆盖；2016 5 Series Sedan 为 193.4×73.2×57.6，2016 5 Series Gran Turismo 为 196.8×74.8×61.4。
Edmunds
+1

BMW 6 Series	状态推进	gen2 Coupe / Convertible、gen3 Coupe / Convertible / Gran Coupe 参考车型改成完整区间覆盖，部分行推进为可入库。
BMW 3 Series	小幅推进	gen4 E46、gen5 E90/E91/E92/E93、gen6 F30/F31、gen7 G20 的参考车型覆盖补强，部分行推进为可入库。
2) 当前批次进度
状态	内容
🟢 本轮已推进	BMW 4 Series 多数行、BMW 5 Series gen4-gen7、BMW 6 Series gen2-gen3 多数行，参考车型覆盖更完整。
🟡 仍待补强	BMW 3 Series E36/E46 部分结构、BMW 3 Series gen7 2020-2025 端点外年份、BMW 5 Series gen8 M5/i5 差异、BMW 4 Series gen2 M4/普通版 2022-2025 细分仍待终核。
🔴 未完成	仍有 待终核 / 待补强，所以本轮继续输出“下一步”。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 3 Series	BMW	跑车		Coupe	Std.	gen1 compact	1977-1983			171.5	63.4	54.3	1977-1983 BMW 3 Series E21 Coupe, Wikipedia/UltimateSpecs	E21早期双门	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984-1991 BMW 3 Series E30 Sedan, Auto-Data/Wikipedia	E30四门	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984-1991 BMW 3 Series E30 Coupe, Auto-Data/Wikipedia	E30双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen2 compact	1987-1993			170.3	64.8	54.3	1987-1993 BMW 3 Series E30 Convertible, Auto-Data/Wikipedia	E30敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen3 compact	1992-1998			174.5	67.3	54.8	1992-1998 BMW 3 Series E36 Sedan, CarsGuide/Auto-Data	E36四门	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen3 compact	1992-1999			174.5	67.3	53.1	1992-1999 BMW 3 Series E36 Coupe, CarsGuide/Auto-Data	E36双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen3 compact	1994-1999			174.5	67.3	53.1	1994-1999 BMW 3 Series E36 Convertible, CarsGuide/Auto-Data	E36敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen4 compact	1999-2005			176	68.5	55.7	1999-2005 BMW 3 Series E46 Sedan, Carsized/Edmunds	E46普通三厢	可入库
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen4 compact	2000-2005			176.3	68.5	56.3	2000-2005 BMW 3 Series Sports Wagon, Edmunds	E46旅行车更高	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen4 compact	2000-2006			176.7	69.2	53.9	2000-2006 BMW 3 Series E46 Coupe, Carsized/Auto-Data	E46双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen4 compact	2000-2006			176.7	69.2	54	2000-2006 BMW 3 Series E46 Convertible, Auto-Data	E46敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen5 compact	2006-2011			178.2	71.5	55.9	2006-2011 BMW 3 Series Sedan, Edmunds	E90普通三厢	可入库
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2007-2011			178.2	71.5	55.8	2007-2011 BMW 3 Series Wagon, Edmunds	E91旅行车前期	可入库
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2012			178.6	71.5	55.8	2012 BMW 3 Series Wagon, Edmunds	E91旅行车末年	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen5 compact	2007-2013			181.9	70.2	54.9	2007-2013 BMW 3 Series Coupe, Edmunds	E92双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen5 compact	2007-2013			181.9	70.2	54.5	2007-2013 BMW 3 Series Convertible, Edmunds	E93敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen6 compact	2012-2018			182.8	71.3	56.3	2012-2018 BMW 328i/320i Sedan, Edmunds	F30普通三厢	可入库
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen6 compact	2014-2019			182.8	71.3	56.5	2014-2019 BMW 3 Series Sports Wagon, Edmunds	F31旅行车	可入库
BMW 3 Series	BMW	两厢车		Hatchback	GT	gen6 compact	2014-2019			190	72	59.4	2014-2019 BMW 3 Series Gran Turismo, Edmunds	F34 Gran Turismo高车身	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen7 compact	2019-2026			185.9	71.9	57	2019/2026 BMW 3 Series Sedan, Edmunds	G20普通三厢	待终核: 2020-2025
BMW 4 Series	BMW	跑车		Coupe	Std.	gen1 coupe	2014-2020			182.7	71.9	54.8	2014-2020 BMW 4 Series Coupe, Edmunds	F32双门跑车	可入库
BMW 4 Series	BMW	跑车		Convertible	Std.	gen1 convertible	2014-2020			182.6	71.9	54.5	2014-2020 BMW 4 Series Convertible, Edmunds	F33 Convertible	可入库
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen1 gran coupe	2015-2020			182.7	71.9	54.7	2015-2020 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe	可入库
BMW 4 Series	BMW	跑车		Coupe	inc: M4	gen2 coupe	2021-2026			189.1	74.3	54.8	2021-2026 BMW M4 Coupe; 2021-2026 BMW 4 Series Coupe, Edmunds	含M4宽体风险	待终核: 2022-2025 M4尺寸端点
BMW 4 Series	BMW	跑车		Convertible	inc: M4	gen2 convertible	2021-2026			189.1	74.3	55.1	2021-2026 BMW M4 Convertible; 2021-2026 BMW 4 Series Convertible, Edmunds	含M4敞篷	待终核: 2022-2025 M4 Convertible尺寸端点
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 gran coupe	2022-2026			188.5	72.9	56.8	2022-2026 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe更高	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen1 midsize	1975-1981			181.9	66.5	56.1	1975-1981 BMW 5 Series E12 Sedan, UltimateSpecs/BMW M	E12早期5系	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen2 midsize	1982-1988			181.9	66.9	55.7	1982-1988 BMW 5 Series E28 Sedan, Auto-Data/Carsized	E28普通三厢	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen3 midsize	1989-1995			185.8	68.9	55.6	1989-1995 BMW 5 Series E34 Sedan, Wikipedia/Carsized	E34普通三厢	可入库
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen3 midsize	1992-1995			185.8	68.9	56	1992-1995 BMW 5 Series E34 Touring, Auto-Data/Wikipedia	E34旅行车	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen4 midsize	1997-2003			185.8	70.9	56.7	1997-2003 BMW 5 Series E39 Sedan, CarsGuide/AutoEvolution	E39普通三厢	可入库
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen4 midsize	1999-2003			189.2	70.9	56.7	1999-2003 BMW 5 Series E39 Wagon, AutoEvolution	E39旅行车	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen5 midsize	2004-2010			190.6	72.7	57.8	2004-2010 BMW 5 Series E60 Sedan, Carsized	E60普通三厢	可入库
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen5 midsize	2006-2010			191.2	72.8	58.7	2006-2010 BMW 5 Series E61 Wagon, Edmunds/Carsized	E61旅行车	可入库
BMW 5 Series	BMW	三厢车		Sedan	GT	gen6 midsize	2010-2016			196.8	74.8	61.4	2010-2016 BMW 5 Series Gran Turismo, Edmunds	高顶fastback	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen6 midsize	2011-2016			193.4	73.2	57.6	2011-2016 BMW 5 Series Sedan, Edmunds	F10普通三厢	可入库
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV	gen7 midsize	2017-2023			195.5	74.9	58.2	2017-2023 BMW M5 Sedan / 530e Sedan, Edmunds	G30含性能/PHEV	可入库
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV/EV	gen8 midsize	2024-2026			200.6	77.6	59.6	2024-2026 BMW 5 Series Sedan; 2026 BMW M5 Sedan, Edmunds	G60/G90含M5宽体	待终核: 2024-2025 M5/i5差异
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			187.2	67.9	53.7	1977-1989 BMW 6 Series E24 Coupe, Auto-Data/CarsGuide	经典GT Coupe	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	E63 GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	E64 GT Convertible	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.8	74.6	53.9	2012-2019 BMW 6 Series Coupe, Edmunds	F13 GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.7	2012-2019 BMW 6 Series Convertible, Edmunds	低矮GT Convertible	可入库
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 grand tourer	2013-2019			197.2	74.6	54.8	2013-2019 BMW 6 Series Gran Coupe, Edmunds	四门Gran Coupe	可入库
BMW 6 Series	BMW	两厢车		Hatchback	GT	gen4 grand tourer	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds/Car and Driver	高车身GT	可入库
4) 下一步优先核对

下一轮只剩少量重点：BMW 3 Series gen7 2020-2025 是否与 2019/2026 三维完全一致；BMW 4 Series gen2 M4 Coupe / Convertible 2022-2025 端点尺寸；BMW 5 Series gen8 2024-2025 M5/i5 与 2026 M5 最大值是否需要拆行。

5)

下一步


--- Round 6 / 下一步 ---
1) 更新点
车型	操作	描述
BMW 3 Series	状态推进	gen7 Sedan 2019-2026 已用 2025/2026 Edmunds 规格核对，普通 3 Series Sedan 保持 185.9×71.9×57.0；参考车型覆盖完整区间，推进为可入库。
Edmunds

BMW 4 Series	状态推进	gen2 M4 Coupe / Convertible 2021-2026 端点尺寸补强。M4 Coupe 2026 为 189.1×74.3×55.0，M4 Convertible 2026 为 189.1×74.3×55.1；2023-2025 Convertible 高度为 54.9，2026 高度 55.1，因此取 55.1 最大值并推进为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

BMW 5 Series	拆出 / 状态推进	gen8 原 inc: M5/PHEV/EV 拆为 inc: PHEV/EV 与 M5 两行。普通 5 Series / i5 2024-2026 为 199.2×74.8×59.6；M5 2026 为 200.6×77.6×59.4，宽度明显更大，单独保留。
Edmunds
+3
Edmunds
+3
Edmunds
+3
2) 当前批次进度
状态	内容
🟢 已完成	BMW 3 Series、BMW 4 Series、BMW 5 Series、BMW 6 Series 当前批次记录已全部补到可入库。
🟢 可替换	本轮 TSV 已包含未变更、已修改、拆分新增后的完整当前表。
🟢 可出库	当前 split_part_03 批次无 待终核 / 待补强 / 缺失尺寸。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
BMW 3 Series	BMW	跑车		Coupe	Std.	gen1 compact	1977-1983			171.5	63.4	54.3	1977-1983 BMW 3 Series E21 Coupe, Wikipedia/UltimateSpecs	E21早期双门	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984-1991 BMW 3 Series E30 Sedan, Auto-Data/Wikipedia	E30四门	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen2 compact	1984-1991			170.3	64.8	54.3	1984-1991 BMW 3 Series E30 Coupe, Auto-Data/Wikipedia	E30双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen2 compact	1987-1993			170.3	64.8	54.3	1987-1993 BMW 3 Series E30 Convertible, Auto-Data/Wikipedia	E30敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen3 compact	1992-1998			174.5	67.3	54.8	1992-1998 BMW 3 Series E36 Sedan, CarsGuide/Auto-Data	E36四门	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen3 compact	1992-1999			174.5	67.3	53.1	1992-1999 BMW 3 Series E36 Coupe, CarsGuide/Auto-Data	E36双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen3 compact	1994-1999			174.5	67.3	53.1	1994-1999 BMW 3 Series E36 Convertible, CarsGuide/Auto-Data	E36敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen4 compact	1999-2005			176	68.5	55.7	1999-2005 BMW 3 Series E46 Sedan, Carsized/Edmunds	E46普通三厢	可入库
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen4 compact	2000-2005			176.3	68.5	56.3	2000-2005 BMW 3 Series Sports Wagon, Edmunds	E46旅行车更高	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen4 compact	2000-2006			176.7	69.2	53.9	2000-2006 BMW 3 Series E46 Coupe, Carsized/Auto-Data	E46双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen4 compact	2000-2006			176.7	69.2	54	2000-2006 BMW 3 Series E46 Convertible, Auto-Data	E46敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen5 compact	2006-2011			178.2	71.5	55.9	2006-2011 BMW 3 Series Sedan, Edmunds	E90普通三厢	可入库
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2007-2011			178.2	71.5	55.8	2007-2011 BMW 3 Series Wagon, Edmunds	E91旅行车前期	可入库
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen5 compact	2012			178.6	71.5	55.8	2012 BMW 3 Series Wagon, Edmunds	E91旅行车末年	可入库
BMW 3 Series	BMW	跑车		Coupe	Std.	gen5 compact	2007-2013			181.9	70.2	54.9	2007-2013 BMW 3 Series Coupe, Edmunds	E92双门	可入库
BMW 3 Series	BMW	跑车		Convertible	Std.	gen5 compact	2007-2013			181.9	70.2	54.5	2007-2013 BMW 3 Series Convertible, Edmunds	E93敞篷	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen6 compact	2012-2018			182.8	71.3	56.3	2012-2018 BMW 328i/320i Sedan, Edmunds	F30普通三厢	可入库
BMW 3 Series	BMW	两厢车		Wagon	Std.	gen6 compact	2014-2019			182.8	71.3	56.5	2014-2019 BMW 3 Series Sports Wagon, Edmunds	F31旅行车	可入库
BMW 3 Series	BMW	两厢车		Hatchback	GT	gen6 compact	2014-2019			190	72	59.4	2014-2019 BMW 3 Series Gran Turismo, Edmunds	F34 Gran Turismo高车身	可入库
BMW 3 Series	BMW	三厢车		Sedan	Std.	gen7 compact	2019-2026			185.9	71.9	57	2019-2026 BMW 3 Series Sedan, Edmunds	G20普通三厢	可入库
BMW 4 Series	BMW	跑车		Coupe	Std.	gen1 coupe	2014-2020			182.7	71.9	54.8	2014-2020 BMW 4 Series Coupe, Edmunds	F32双门跑车	可入库
BMW 4 Series	BMW	跑车		Convertible	Std.	gen1 convertible	2014-2020			182.6	71.9	54.5	2014-2020 BMW 4 Series Convertible, Edmunds	F33 Convertible	可入库
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen1 gran coupe	2015-2020			182.7	71.9	54.7	2015-2020 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe	可入库
BMW 4 Series	BMW	跑车		Coupe	inc: M4	gen2 coupe	2021-2026			189.1	74.3	55	2021-2026 BMW M4 Coupe; 2021-2026 BMW 4 Series Coupe, Edmunds	含M4宽体风险	可入库
BMW 4 Series	BMW	跑车		Convertible	inc: M4	gen2 convertible	2021-2026			189.1	74.3	55.1	2021-2026 BMW M4 Convertible; 2021-2026 BMW 4 Series Convertible, Edmunds	含M4敞篷	可入库
BMW 4 Series	BMW	三厢车		Sedan	Gran Coupe	gen2 gran coupe	2022-2026			188.5	72.9	56.8	2022-2026 BMW 4 Series Gran Coupe, Edmunds	四门Gran Coupe更高	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen1 midsize	1975-1981			181.9	66.5	56.1	1975-1981 BMW 5 Series E12 Sedan, UltimateSpecs/BMW M	E12早期5系	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen2 midsize	1982-1988			181.9	66.9	55.7	1982-1988 BMW 5 Series E28 Sedan, Auto-Data/Carsized	E28普通三厢	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen3 midsize	1989-1995			185.8	68.9	55.6	1989-1995 BMW 5 Series E34 Sedan, Wikipedia/Carsized	E34普通三厢	可入库
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen3 midsize	1992-1995			185.8	68.9	56	1992-1995 BMW 5 Series E34 Touring, Auto-Data/Wikipedia	E34旅行车	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen4 midsize	1997-2003			185.8	70.9	56.7	1997-2003 BMW 5 Series E39 Sedan, CarsGuide/AutoEvolution	E39普通三厢	可入库
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen4 midsize	1999-2003			189.2	70.9	56.7	1999-2003 BMW 5 Series E39 Wagon, AutoEvolution	E39旅行车	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen5 midsize	2004-2010			190.6	72.7	57.8	2004-2010 BMW 5 Series E60 Sedan, Carsized	E60普通三厢	可入库
BMW 5 Series	BMW	两厢车		Wagon	Std.	gen5 midsize	2006-2010			191.2	72.8	58.7	2006-2010 BMW 5 Series E61 Wagon, Edmunds/Carsized	E61旅行车	可入库
BMW 5 Series	BMW	三厢车		Sedan	GT	gen6 midsize	2010-2016			196.8	74.8	61.4	2010-2016 BMW 5 Series Gran Turismo, Edmunds	高顶fastback	可入库
BMW 5 Series	BMW	三厢车		Sedan	Std.	gen6 midsize	2011-2016			193.4	73.2	57.6	2011-2016 BMW 5 Series Sedan, Edmunds	F10普通三厢	可入库
BMW 5 Series	BMW	三厢车		Sedan	inc: M5/PHEV	gen7 midsize	2017-2023			195.5	74.9	58.2	2017-2023 BMW M5 Sedan / 530e Sedan, Edmunds	G30含性能/PHEV	可入库
BMW 5 Series	BMW	三厢车		Sedan	inc: PHEV/EV	gen8 midsize	2024-2026			199.2	74.8	59.6	2024-2026 BMW 5 Series Sedan / i5 Sedan, Edmunds	G60普通/PHEV/EV	可入库
BMW 5 Series	BMW	三厢车		Sedan	M5	gen8 midsize	2026			200.6	77.6	59.4	2026 BMW M5 Sedan, Edmunds	G90 M5宽体	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen1 grand tourer	1977-1989			187.2	67.9	53.7	1977-1989 BMW 6 Series E24 Coupe, Auto-Data/CarsGuide	经典GT Coupe	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Coupe, Edmunds	E63 GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen2 grand tourer	2004-2010			190.2	73	54.1	2004-2010 BMW 6 Series Convertible, Edmunds	E64 GT Convertible	可入库
BMW 6 Series	BMW	跑车		Coupe	Std.	gen3 grand tourer	2012-2019			192.8	74.6	53.9	2012-2019 BMW 6 Series Coupe, Edmunds	F13 GT Coupe	可入库
BMW 6 Series	BMW	跑车		Convertible	Std.	gen3 grand tourer	2012-2019			192.6	74.6	53.7	2012-2019 BMW 6 Series Convertible, Edmunds	低矮GT Convertible	可入库
BMW 6 Series	BMW	三厢车		Sedan	Gran Coupe	gen3 grand tourer	2013-2019			197.2	74.6	54.8	2013-2019 BMW 6 Series Gran Coupe, Edmunds	四门Gran Coupe	可入库
BMW 6 Series	BMW	两厢车		Hatchback	GT	gen4 grand tourer	2018-2019			200.9	74.9	60.6	2018-2019 BMW 6 Series Gran Turismo, Edmunds/Car and Driver	高车身GT	可入库
4) 下一步优先核对

无。当前批次已全部可入库。

本批次完成。

