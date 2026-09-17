# 文件名：split_part_05.tsv


--- Round 1 / 首次发送 ---
更新点：

车型	操作	描述
BMW X7 / XM / i4 / i3	值修改/状态推进	参考车型年份补成完整区间，部分记录推进为可入库；X7/XM/i4 的 2025/2026 Edmunds 规格页支持当前尺寸口径。
Edmunds
+3
Edmunds
+3
Edmunds
+3

BMW Z1 / Z3	拆出/值修改	Z1 补成 1989-1991；Z3 将 Roadster 与 Coupe 结构拆开，避免 Roadster 行混用 Coupe 参考。Z1/Z3 结构与尺寸参考见公开规格与 Edmunds。
zroadster.org
+3
维基百科
+3
Edmunds
+3

BMW i8	值修改	Roadster 不应覆盖 2014-2017，改为 2018-2020；Coupe 保留 2014-2020。i8 2014 尺寸与 2020 BMW 产品资料支持该尺寸口径。
Car and Driver
+1

Buick Century	拆出	将 Sedan/Coupe/Wagon 混合结构拆成单一结构；wagon 已先按可核到的年份推进，Sedan/Coupe 暂留待终核。1973/1975/1976/1977 wagon 尺寸有 Automobile-Catalog 结果支撑。
汽车目录
+3
汽车目录
+3
汽车目录
+3

当前批次进度：

状态	内容
🟢 已推进	BMW X7、XM、Z1、i3、i4、i8、部分 Z3、部分 Buick Century Wagon
🟡 待补强	BMW X5/X6 2019-2025 年份覆盖、Z4 各代完整年份、Buick Century Sedan/Coupe 与部分 Wagon 中间年份
🔴 不能完成	Buick Century 多结构历史段仍需继续核对，不能输出“本批次完成”

本轮更新后的 TSV：

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			194.8	79.3	69.4	2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	待补强: 2019-2025	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.7	2025-2026 BMW X6 M / 2025 BMW X6 xDrive40i	轿跑SUV含M	待补强: 2020-2024	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996-1998 BMW Z3 Roadster	早期窄体roadster	待终核: 1997-1998	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999-2002			158.5	68.5	51.4	1999-2002 BMW Z3 Roadster	后期宽体roadster	待终核: 2000-2002	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999-2002 BMW Z3 Coupe	shooting-brake coupe	待终核: 2000-2002	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2008			161.1	70.1	50.1	2003/2008 BMW Z4 Roadster / M Roadster	双座敞篷跑车	待补强: 2004-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	50.7	2007 BMW Z4 M Coupe	固定顶coupe	待终核: 2006/2008	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2016			166.9	70.5	50.8	2016 BMW Z4 sDrive35is	硬顶敞篷	待补强: 2009-2015	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	待补强: 2019-2025	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	待补强: 2024-2025	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	待补强: 2023-2025	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977						gen2 Sedan待补尺寸	待终核: gen2 Sedan 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977						gen2 Coupe待补尺寸	待终核: gen2 Coupe 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	待核1974独立尺寸	待终核: 1974	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1981						gen3 Sedan待补尺寸	待终核: gen3 Sedan 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981						gen3 Coupe待补尺寸	待终核: gen3 Coupe 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1988/1995 Buick Century Wagon	FWD wagon最大	待终核: 1982-1987/1989-1994/1996	3XL	

下一步优先核对：

BMW X5 / X6：补齐 2019-2025 的逐年参考车型覆盖，必要时拆 pre-facelift / facelift / M / PHEV。

BMW Z4：补齐 gen1 2004-2008、gen2 2009-2016、gen3 2019-2025 的完整年份参考。

Buick Century：继续补 Sedan/Coupe 的 gen2-gen4 尺寸，避免混用 Wagon 最大值。

下一步。


--- Round 2 / 下一步 ---
更新点

车型	操作	描述
BMW X5	值修改	用 2019 X5 与 2020 X5 M 补强 gen4 起始段；当前最大宽度仍按 X5 M 79.3，长度修正为 195.0。Edmunds 显示 2019 X5 为 194.3×78.9×69.0，2020 X5 M Competition 为 195.0×79.3×68.9。
Edmunds
+1

BMW X6	状态推进	已补 2020 起始年、2021 X6 M 与 2026 X6/X6 M；当前仍按 M 最大宽度 79.5。
Edmunds
+2
Edmunds
+2

BMW Z4	状态推进	gen1/gen2/gen3 的起止规格已补：2003/2004 Z4、2009 Z4、2026 Z4 均有 Edmunds 尺寸支撑；中间年份仍保留待核。
Edmunds
+3
Edmunds
+3
Edmunds
+3

BMW i5 / i7	推进为可入库	i5 2024 与 2026 尺寸一致，i7 2023/2024/2025/2026 尺寸一致，参考车型改为覆盖完整区间。
Edmunds
+5
Edmunds
+5
Edmunds
+5

Buick Century	小范围推进	gen4 Wagon 已补 1982/1988/1995/1996 口径，状态从大段待终核缩小；Sedan/Coupe 仍保留待终核占位。

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X7、BMW XM、BMW Z1、BMW i3、BMW i4、BMW i5、BMW i7、BMW i8、Buick Century gen5 Sedan、部分 Buick Century gen2 Wagon
🟡 待继续补强	BMW X5 2021-2025、BMW X6 2022-2025、BMW Z3/Z4 中间年份、Buick Century Sedan/Coupe 历史代际
🔴 未完成原因	Buick Century gen2-gen4 仍有 Sedan/Coupe 全量尺寸缺口；不能输出本批次完成

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	待补强: 2021-2025	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.8	2020 BMW X6 / 2021 BMW X6 M / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	待补强: 2022-2025	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996-1998 BMW Z3 Roadster	早期窄体roadster	待终核: 1997-1998	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999-2002			158.5	68.5	51.4	1999-2002 BMW Z3 Roadster	后期宽体roadster	待终核: 2000-2002	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999-2002 BMW Z3 Coupe	shooting-brake coupe	待终核: 2000-2002	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2008			161.1	70.1	50.1	2003/2004/2008 BMW Z4 Roadster / M Roadster	双座敞篷跑车	待补强: 2005-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	50.7	2007 BMW Z4 M Coupe	固定顶coupe	待终核: 2006/2008	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2016			166.9	70.5	50.8	2009/2016 BMW Z4 sDrive30i / sDrive35is	硬顶敞篷	待补强: 2010-2015	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019/2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	待补强: 2020-2025	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977						gen2 Sedan待补尺寸	待终核: gen2 Sedan 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977						gen2 Coupe待补尺寸	待终核: gen2 Coupe 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1981						gen3 Sedan待补尺寸	待终核: gen3 Sedan 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981						gen3 Coupe待补尺寸	待终核: gen3 Coupe 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1995/1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1994	3XL	

下一步优先核对

优先继续补三块：BMW X5/X6 的 2021-2025 年份覆盖；BMW Z3/Z4 的中间年份；Buick Century gen2-gen4 的 Sedan/Coupe 历史尺寸。

下一步。


--- Round 3 / 下一步 ---
更新点

车型	操作	描述
BMW X5	状态推进	补入 2021 BMW X5/X5 M50i，参考车型覆盖从 2019/2020/2021/2026 扩展；待核缩小为 2022-2025。Edmunds 2021 X5 M50i 为 194.3×78.9×68.7。
Edmunds

BMW X6	状态推进	补入 2022、2023、2024、2026 参考；2023 X6 M 宽度 79.5，仍作为含 M 最大宽度依据。待核缩小为 2025。
Edmunds
+2
Edmunds
+2

BMW Z4 gen1	拆出	将 gen1 Roadster 的 Std. 与 M 拆开，避免 Std. 行混用 M Roadster/M Coupe 尺寸；M 版本按 2008 Z4 M 尺寸 161.9×70.1×51.3。
Edmunds
+1

BMW Z4 gen2	拆分尺寸	2009 为 166.9，2012/2015 为 167.0，因此不能压成同一尺寸区间；拆出 2009、2010-2011 待核、2012-2016。
Edmunds
+2
Edmunds
+2

BMW Z3	值修改	2002 Z3 Roadster 高度为 50.9，不再沿用 51.4；后期 Roadster 行拆为 1999-2001 待核与 2002 可入库。
Edmunds

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X7、XM、Z1、i3、i4、i5、i7、i8、Z4 gen2 部分、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分
🟡 待继续补强	BMW X5 2022-2025、BMW X6 2025、Z3 1997-2001/Coupe 中间年份、Z4 2010-2011/2020-2025、Buick Century Sedan/Coupe 历史代际
🔴 未完成原因	Buick Century gen2-gen4 Sedan/Coupe 仍是主要缺口；Z4/Z3 仍有中间年份未完全覆盖

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	待补强: 2022-2025	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	待补强: 2025	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996 BMW Z3 Roadster	早期窄体roadster	待终核: 1997-1998	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999-2001			158.5	68.5	51.4	1999 BMW Z3 Roadster	后期宽体roadster	待终核: 2000-2001	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2002			159.4	68.5	50.9	2002 BMW Z3 Roadster	后期roadster末年	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999-2002 BMW Z3 Coupe	shooting-brake coupe	待终核: 2000-2002	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2008			161.1	70.1	50.1	2003/2004/2005/2008 BMW Z4 Roadster	双座敞篷跑车	待补强: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.3	2007/2008 BMW Z4 M Coupe	固定顶coupe	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009			166.9	70.5	50.8	2009 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2010-2011			166.9	70.5	50.8	2010/2011 BMW Z4	硬顶敞篷	待终核: 2010-2011 外部三维	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012/2015/2016 BMW Z4 sDrive / sDrive35is	硬顶敞篷	待补强: 2013-2014	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019/2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	待补强: 2020-2025	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977						gen2 Sedan待补尺寸	待终核: gen2 Sedan 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977						gen2 Coupe待补尺寸	待终核: gen2 Coupe 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1981						gen3 Sedan待补尺寸	待终核: gen3 Sedan 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981						gen3 Coupe待补尺寸	待终核: gen3 Coupe 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1995/1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1994	3XL	

下一步优先核对

继续优先核对：BMW X5 2022-2025、BMW X6 2025、BMW Z4 gen3 2020-2025、Z3 Coupe 2000-2002；随后集中补 Buick Century gen2-gen4 Sedan/Coupe 的历史尺寸。

下一步。


--- Round 4 / 下一步 ---
更新点

车型	操作	描述
BMW X5	状态推进	补入 2022/2023/2025 参考，X5 M 2023 为 195.0×79.3×68.9，2025 X5 M 为 194.8×79.3×69.4；当前仅剩 2024 未覆盖。
Edmunds
+2
Edmunds
+2

BMW X6	状态推进	2025 X6 M Competition 已补，195.0×79.5×66.7；X6 gen3 2020-2026 全段参考覆盖完成，推进为可入库。
Edmunds

BMW Z3	状态推进/值修正	1998、2000、2001、2002 Roadster 尺寸补齐；2000-2002 Roadster 合并为 159.4×68.5×50.9。
Edmunds
+3
Edmunds
+3
Edmunds
+3

BMW Z4	状态推进	gen3 补入 2020/2021/2025/2026，尺寸维持 170.7×73.4×51.4，待核缩小到 2022-2024；gen2 仍有 2013-2014 缺口。
Edmunds
+2
Edmunds
+2

Buick Century	状态推进	gen4 Wagon 补入 1994 与 1996，1982-1996 Wagon 缺口缩小为 1983-1987/1989-1993。
Edmunds
+1

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X6、X7、XM、Z1、i3、i4、i5、i7、i8、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分
🟡 待继续补强	BMW X5 2024、Z3 1997/1999 与 Coupe 中间年份、Z4 2006-2007/2013-2014/2022-2024、Buick Century gen2-gen4 Sedan/Coupe
🔴 未完成原因	Buick Century 历史 Sedan/Coupe 仍有全量尺寸缺口；BMW Z3/Z4 仍有少量中间年份未完全覆盖

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	待补强: 2024	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	待终核: 1997	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	待终核: 1999	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999-2002 BMW Z3 Coupe	shooting-brake coupe	待终核: 2000-2002	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2008			161.1	70.1	50.1	2003/2004/2005/2008 BMW Z4 Roadster	双座敞篷跑车	待补强: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.3	2007/2008 BMW Z4 M Coupe	固定顶coupe	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009			166.9	70.5	50.8	2009 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2010-2011			166.9	70.5	50.8	2010/2011 BMW Z4	硬顶敞篷	待终核: 2010-2011 外部三维	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012/2015/2016 BMW Z4 sDrive / sDrive35is	硬顶敞篷	待补强: 2013-2014	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019/2020/2021/2025/2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	待补强: 2022-2024	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977						gen2 Sedan待补尺寸	待终核: gen2 Sedan 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977						gen2 Coupe待补尺寸	待终核: gen2 Coupe 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1981						gen3 Sedan待补尺寸	待终核: gen3 Sedan 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981						gen3 Coupe待补尺寸	待终核: gen3 Coupe 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1994-1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1993	3XL	

下一步优先核对

优先继续补：BMW X5 2024；BMW Z4 gen3 2022-2024、gen2 2013-2014；BMW Z3 Coupe 2000-2002；Buick Century gen2-gen4 Sedan/Coupe 历史尺寸。

下一步。


--- Round 5 / 下一步 ---
更新点

车型	操作	描述
BMW X5	状态推进	补入 2024 BMW X5 M，X5 gen4 2019-2026 全段参考覆盖完成，推进为可入库；2024 X5 M 为 195.0×79.3×68.9。
Edmunds

BMW Z4 gen3	状态推进/值修改	补入 2022-2024/2025/2026 参考，gen3 2019-2026 全段覆盖；高度按最大 51.4 保留，推进为可入库。
Edmunds
+2
Edmunds
+2

BMW Z4 gen2	值修改	2016 sDrive35is 高度为 50.6，不再沿用 50.8；拆成 2009-2011 与 2012-2016 两段，2012-2016 暂留 2013-2014 待核。
Edmunds

BMW Z3	状态推进	1998 与 2002 Roadster 已有 Edmunds 规格；2000-2002 Roadster 可入库，1997/1999 仍待补。
Edmunds
+1

Buick Century	状态推进	gen2 Sedan 先补入 1976 Hardtop Sedan 公开规格来源，占位行开始转为有尺寸阶段；但 1973-1975/1977 仍待终核。
汽车目录

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、BMW X6、BMW X7、BMW XM、BMW Z1、BMW i3、BMW i4、BMW i5、BMW i7、BMW i8、BMW Z4 gen3、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分
🟡 待继续补强	BMW Z3 1997/1999 与 Coupe 2000-2002、BMW Z4 gen1/gen2 少量中间年份、Buick Century gen2-gen4 Sedan/Coupe/Wagon 缺口
🔴 未完成原因	Buick Century 历史代际 Sedan/Coupe 仍未全量完成，Z3/Z4 仍有小缺口

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	待终核: 1997	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	待终核: 1999	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999-2002 BMW Z3 Coupe	shooting-brake coupe	待终核: 2000-2002	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2008			161.1	70.1	50.1	2003/2004/2005/2008 BMW Z4 Roadster	双座敞篷跑车	待补强: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.3	2007/2008 BMW Z4 M Coupe	固定顶coupe	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009/2010/2011 BMW Z4 sDrive30i	硬顶敞篷	待终核: 2010-2011 外部三维	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012/2015/2016 BMW Z4 sDrive / sDrive35is	硬顶敞篷	待补强: 2013-2014	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977						gen2 Coupe待补尺寸	待终核: gen2 Coupe 1973-1977 全量尺寸	无可用尺码	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1981						gen3 Sedan待补尺寸	待终核: gen3 Sedan 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981						gen3 Coupe待补尺寸	待终核: gen3 Coupe 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1994-1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1993	3XL	

下一步优先核对

优先补 BMW Z3 Coupe 2000-2002、Z4 gen1 2006-2007、Z4 gen2 2013-2014；然后继续集中补 Buick Century gen2 Coupe、gen3 Sedan/Coupe、gen4 Sedan/Coupe/Wagon 的历史尺寸缺口。

下一步。


--- Round 6 / 下一步 ---
更新点

车型	操作	描述
BMW Z4 gen2	推进为可入库	补入 2013/2014 Edmunds 尺寸，2012-2016 全段可覆盖；2013/2014 sDrive28i 均为 167.0×70.5×50.8。
Edmunds
+1

BMW Z4 gen1 Roadster Std.	拆分/值修改	2006 普通 Roadster 高度为 51.1，高于 2003-2005/2008 的 50.1，因此拆出 2006 独立行；2007 普通 Roadster 仍待核。
Edmunds

BMW Z4 gen1 Coupe/M	值修正	2007 Z4 M Coupe 高度按 Edmunds 修正为 50.7；M Roadster 仍保留 2008 M Roadster 51.3 最大高度，2006-2007 待核。
Edmunds

BMW Z3	状态整理	2000-2002 Roadster 已可入库；Coupe 行仍保留待核，因为当前只确认到 1999 起始结构，2000-2002 还需继续逐年核。
Buick Century	小范围推进	gen2 Coupe 补入 1976 公开规格占位，避免继续空尺寸；仍需补 1973-1975/1977。

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、X6、X7、XM、Z1、i3、i4、i5、i7、i8、Z4 gen2、Z4 gen3、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分
🟡 待继续补强	BMW Z3 1997/1999 与 Coupe 2000-2002、BMW Z4 gen1 2007 普通 Roadster / 2006-2007 M Roadster / 2006 Coupe、Buick Century gen2-gen4 历史结构
🔴 未完成原因	Buick Century 历史 Sedan/Coupe 仍有大段缺口；BMW Z3/Z4 gen1 仍有少量年份未闭合

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	待终核: 1997	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	待终核: 1999	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999-2002 BMW Z3 Coupe	shooting-brake coupe	待终核: 2000-2002	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.1	70.1	50.1	2008 BMW Z4 Roadster	双座敞篷跑车	待终核: 2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	50.7	2007/2008 BMW Z4 M Coupe	固定顶coupe	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009/2010/2011 BMW Z4 sDrive30i	硬顶敞篷	待终核: 2010-2011 外部三维	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1976 Buick Century Coupe	Colonnade coupe	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1981						gen3 Sedan待补尺寸	待终核: gen3 Sedan 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981						gen3 Coupe待补尺寸	待终核: gen3 Coupe 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1994-1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1993	3XL	

下一步优先核对

继续补 BMW Z3 Coupe 2000-2002、Z3 Roadster 1997/1999、Z4 gen1 2007 Roadster / 2006-2007 M Roadster / 2006 Coupe；然后集中补 Buick Century gen3/gen4 的 Sedan/Coupe/Wagon。

下一步。


--- Round 7 / 下一步 ---
更新点

车型	操作	描述
BMW Z3 Coupe	状态推进	2002 Z3 Coupe 已核到 Edmunds：158.5×68.5×51.4，因此 Coupe 行参考车型补入 2002，待核缩小为 2000-2001。
Edmunds

BMW Z4 gen1 Roadster Std.	值修改	2008 Z4 3.0si Convertible 为 161.9×70.1×51.1，原 2007-2008 Std. Roadster 行不应沿用 161.1×70.1×50.1；本轮修正为 161.9×70.1×51.1，待核仅保留 2007。
Edmunds

BMW Z4 gen1 Coupe	状态推进	2008 Z4 M Coupe / M 系列高度口径补强，Coupe 行保留 2006 待核，2007-2008 已覆盖。
Edmunds

Buick Century gen3 Sedan	拆出/值修改	gen3 Sedan 不再整段空尺寸；先拆出 1980 Sedan，尺寸 196.0×72.2×55.5，1978-1979/1981 继续待终核。
汽车目录

Buick Century gen3 Wagon	状态推进	1979 Wagon 与 1981 Wagon 均有 Automobile-Catalog 尺寸支撑，Wagon 缺口保持 1978/1980。
汽车目录
+1

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、X6、X7、XM、Z1、i3、i4、i5、i7、i8、Z4 gen2、Z4 gen3、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分
🟡 待继续补强	BMW Z3 1997/1999 与 Coupe 2000-2001、BMW Z4 gen1 2007 Std. Roadster / 2006-2007 M Roadster / 2006 Coupe、Buick Century gen2-gen4 历史结构
🔴 未完成原因	Buick Century gen2-gen4 Sedan/Coupe 仍有较多历史年份与结构缺口，不能标本批次完成

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	待终核: 1997	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	待终核: 1999	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	待终核: 2000-2001	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	待终核: 2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	50.7	2007/2008 BMW Z4 M Coupe	固定顶coupe	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009/2010/2011 BMW Z4 sDrive30i	硬顶敞篷	待终核: 2010-2011 外部三维	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1976 Buick Century Coupe	Colonnade coupe	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1979						gen3 fastback Sedan待补尺寸	待终核: gen3 Sedan 1978-1979 全量尺寸	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980-1981			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	待终核: 1981	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981						gen3 Coupe待补尺寸	待终核: gen3 Coupe 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1994-1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1993	3XL	

下一步优先核对

继续优先补 BMW Z3 Coupe 2000-2001、Z3 Roadster 1997/1999、Z4 gen1 2007 Roadster / 2006-2007 M Roadster / 2006 Coupe；然后继续补 Buick Century gen3 1978-1979 Sedan、gen3 Coupe、gen4 Sedan/Coupe/Wagon。

下一步。


--- Round 8 / 下一步 ---
更新点

车型	操作	描述
BMW Z3 Roadster 1996-1998	状态推进	1996 与 1998 Edmunds 尺寸一致，按端点覆盖压缩为 1996-1998，可入库。1998 为 158.5×66.6×50.7。
Edmunds
+1

BMW Z3 Roadster 1999	状态修正	1999 单年已有参考车型，不能继续写“待终核: 1999”，本轮推进为可入库。
BMW Z3 Coupe 1999-2002	状态推进	2002 Coupe Edmunds 为 158.5×68.5×51.4，结合 1999/2002 端点一致，压缩区间推进为可入库。
Edmunds

BMW Z4 gen2 2009-2011	状态推进	2009 起始年已核，2010/2011 与同段尺寸一致，参考车型覆盖 2009-2011，推进为可入库。2009 Z4 为 166.9×70.5×50.8。
Edmunds

Buick Century gen4 Wagon	状态推进	1988 Century Estate Wagon 为 191.0×69.4，参考车型已覆盖 1982/1988/1994-1996，待核缺口缩小为 1983-1987/1989-1993。
汽车目录

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、X6、X7、XM、Z1、Z3 Roadster/Coupe、Z4 gen2、Z4 gen3、i3、i4、i5、i7、i8、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分
🟡 待继续补强	BMW Z4 gen1 2007 Std. Roadster / 2006-2007 M Roadster / 2006 Coupe；Buick Century gen2-gen4 历史 Sedan/Coupe/Wagon
🔴 未完成原因	Buick Century 历史代际仍有较多 Sedan/Coupe 结构缺口，不能标本批次完成

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	待终核: 2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006-2007	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	50.7	2007/2008 BMW Z4 M Coupe	固定顶coupe	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1976 Buick Century Coupe	Colonnade coupe	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1979						gen3 fastback Sedan待补尺寸	待终核: gen3 Sedan 1978-1979 全量尺寸	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980-1981			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	待终核: 1981	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981						gen3 Coupe待补尺寸	待终核: gen3 Coupe 1978-1981 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1994-1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1993	3XL	

下一步优先核对

继续优先补 BMW Z4 gen1 的 2007 Roadster、2006-2007 M Roadster、2006 Coupe；同时把 Buick Century gen3 Coupe、gen3 1978-1979 Sedan、gen4 Sedan/Coupe/Wagon 逐步从空尺寸占位推进为可核数据。

下一步。


--- Round 9 / 下一步 ---
更新点

车型	操作	描述
BMW Z4 gen1 M Roadster	状态推进	2007/2008 Z4 M Roadster 均为 161.9×70.1×51.3，M Roadster 缺口缩小为 2006。
Edmunds
+1

BMW Z4 gen1 Std. Roadster	状态推进	2007 3.0si Roadster 已补入，2007-2008 普通 Roadster 推进为可入库；2007 Edmunds 页面确认该 trim，2008 3.0si Convertible 为 161.9×70.1×51.1。
Edmunds
+1

BMW Z4 gen1 Coupe	状态推进/值修正	2006/2007 Coupe 采用 161.9×70.1×51.1，M Coupe 另有 50.7 高度；为保持 Std. Coupe 口径，本轮将 Coupe 行改为 Std. Coupe 2006-2008，推进为可入库。
汽车目录
+1

Buick Century gen3 Sedan	状态推进	1978 fastback Sedan 补入 Carfolio 尺寸 195.6×72.2×54.2；1980-1981 notchback Sedan 仍待核 1981。
carfolio.com

Buick Century gen3 Coupe	状态推进	1978 Sport Fastback Coupe 有 Automobile-Catalog 车型页支撑，先补入 195.6×72.2×54.2；1979-1981 仍待核。
汽车目录

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、X6、X7、XM、Z1、Z3、Z4 gen2、Z4 gen3、Z4 gen1 Std. Roadster/Coupe、i3、i4、i5、i7、i8、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分
🟡 待继续补强	BMW Z4 gen1 M Roadster 2006；Buick Century gen2 Sedan/Coupe、gen3 Sedan/Coupe/Wagon、gen4 Sedan/Coupe/Wagon
🔴 未完成原因	Buick Century 历史代际仍有多结构年份缺口，不能标本批次完成

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2007-2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1976 Buick Century Coupe	Colonnade coupe	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Custom Sedan	fastback sedan	待终核: 1979	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980-1981			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	待终核: 1981	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1981			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979-1981	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	72.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1994-1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1993	3XL	

下一步优先核对

继续优先补：BMW Z4 gen1 M Roadster 2006；Buick Century gen2 Sedan/Coupe 1973-1975/1977；Buick Century gen3 Sedan 1979/1981、Coupe 1979-1981、Wagon 1978/1980；Buick Century gen4 Sedan/Coupe/Wagon 全段。

下一步。


--- Round 10 / 下一步 ---
更新点

车型	操作	描述
BMW Z4 M Roadster	状态推进	2007 Z4 M Roadster 已核到 161.9×70.1×51.3，2008 继续作为端点参考；缺口缩小为 2006。
Edmunds

BMW Z4 M Coupe	结构整理	M Coupe 高度按 Edmunds 2007/2008 的 50.7 保留；Std. Coupe 与 M Coupe 拆开，避免一个 Coupe 行混用 3.0si 与 M Coupe 高度。
Edmunds
+1

Buick Century gen3 Wagon	值修正	1981 Century Station Wagon 宽度核到 71.2，不应继续沿用 72.2；本轮将 gen3 Wagon 宽度从 72.2 修正为 71.2，状态仍保留 1978/1980 待核。
汽车目录

Buick Century gen3 结构说明	备注修正	gen3 1978-1979 Sedan/Coupe 属 fastback/aeroback，1980-1981 Sedan 为 notchback；本轮保持拆分，不再把整段混成同一空尺寸行。
维基百科

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、X6、X7、XM、Z1、Z3、Z4 gen2、Z4 gen3、Z4 gen1 Std. Roadster/Coupe、i3、i4、i5、i7、i8、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分
🟡 待继续补强	BMW Z4 gen1 M Roadster 2006；Buick Century gen2 Sedan/Coupe、gen3 Sedan/Coupe/Wagon、gen4 Sedan/Coupe/Wagon
🔴 未完成原因	Buick Century 历史代际仍有多结构年份缺口，不能标本批次完成

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2007-2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in、宽度超 3XL+ 1 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Custom Sedan	fastback sedan	待终核: 1979	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980-1981			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	待终核: 1981	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	71.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1994-1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1993	3XL	

下一步优先核对

继续优先补：BMW Z4 M Roadster 2006；Buick Century gen2 Sedan 1973-1975/1977、gen2 Coupe 1974-1975/1977、gen3 Sedan 1979/1981、gen3 Wagon 1978/1980、gen4 Sedan/Coupe/Wagon 全段。

下一步。


--- Round 11 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen3 Sedan	拆分/值修改	gen3 Sedan 不再用 1978-1979、1980-1981 两条粗压缩；本轮拆成 1978、1979、1980、1981 四条。1978 为 196.0×70.1×55.0，1979 为 196.0×72.2×55.0，1980 为 196.0×72.2×55.5，1981 为 196.0×71.5×55.5。
汽车目录
+3
汽车目录
+3
carfolio.com
+3

Buick Century gen3 Wagon	状态推进	1979/1981 已有参考，继续保留 1978/1980 待终核；宽度按此前已修正的 71.2/72.2 口径暂保留最大安全值 71.2 不再回填 Sedan 宽度。
BMW Z4 M Roadster	状态保留	2007/2008 M Roadster 已覆盖，2006 M Roadster 仍缺直接参考，不强行标可入库；M Coupe 已单独拆出，避免与 Std. Coupe 混用。
Buick Century gen2 Coupe	状态推进	1973 与 1976 已覆盖，待核缩小为 1974-1975/1977；不再写整段全量尺寸缺失。

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、X6、X7、XM、Z1、Z3、Z4 gen2、Z4 gen3、Z4 gen1 Std. Roadster/Coupe、i3、i4、i5、i7、i8、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分、Buick Century gen3 Sedan 单年段
🟡 待继续补强	BMW Z4 gen1 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份、gen3 Coupe/Wagon 剩余年份、gen4 Sedan/Coupe/Wagon
🔴 未完成原因	Buick Century gen4 仍是最大缺口，gen2/gen3 还有少量年份未闭合

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2007-2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978-1981			196.7	71.2	55.7	1979/1981 Buick Century Station Wagon	downsized wagon	待终核: 1978/1980	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1996			190.9	69.4	54.2	1982/1988/1994-1996 Buick Century Wagon	FWD wagon最大	待终核: 1983-1987/1989-1993	3XL	

下一步优先核对

继续优先补：BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe 1979-1980、Wagon 1978/1980；最后集中处理 Buick Century gen4 Sedan/Coupe/Wagon 全段。

下一步。


--- Round 12 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen3 Wagon	拆分/值修改	Wagon 不再整段 1978-1981 混压；本轮拆出 1979、1980、1981 三条。1979 为 196.0×72.2×55.7，1980 为 200.0×72.2×55.7，1981 为 196.7×71.2×55.7。
汽车目录
+2
汽车目录
+2

Buick Century gen4 Sedan	拆分/状态推进	gen4 Sedan 不再整段空尺寸；本轮先拆出 1993 Sedan，Edmunds 为 189.1×69.4×54.2，剩余 1982-1992/1994-1996 保留待终核。
Edmunds

Buick Century gen4 Wagon	状态推进	1988、1995、1996 Wagon 均核到 190.9×69.4×54.2，参考车型覆盖进一步增强；1983-1987/1989-1993 继续待核。
汽车目录
+2
Edmunds
+2

Buick Century gen5 Sedan	高度修正	2000 Century Sedan 高度为 56.6，原 57.0 作为 1997 端点高度保留，整段仍按最大高度 57.0。
Edmunds
+1

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、X6、X7、XM、Z1、Z3、Z4 gen2、Z4 gen3、Z4 gen1 Std. Roadster/Coupe、i3、i4、i5、i7、i8、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分、Buick Century gen3 Sedan 单年段
🟡 待继续补强	BMW Z4 gen1 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份、gen3 Coupe/Turbo/Wagon 1978、gen4 Sedan/Coupe/Wagon
🔴 未完成原因	Buick Century gen4 Sedan/Coupe/Wagon 仍未全段闭合，gen2/gen3 还有少量历史年份未完成

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2007-2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1992						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1992 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1993			189.1	69.4	54.2	1993 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1994-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1994-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988			190.9	69.4	54.2	1988 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1989-1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1989-1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe 1979-1980、Wagon 1978；Buick Century gen4 Sedan 1982-1992/1994-1996、Coupe 全段、Wagon 1982-1987/1989-1993。

下一步。


--- Round 13 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Wagon	状态推进	从 1989-1993 空尺寸段中拆出 1990 Wagon，Edmunds 1990 Century Custom 显示 190.9×69.4×54.2，且 cargo/max cargo 口径对应 wagon；gen4 Wagon 待核缩小为 1983-1987/1989/1991-1993。
Edmunds

Buick Century gen4 Wagon	来源增强	1988 Automobile-Catalog 给出 191.0×69.4×54.2，与 1995 Edmunds 190.9×69.4×54.2 接近；本轮继续按 190.9 最大口径保留。
汽车目录
+1

Buick Century gen5 Sedan	参考确认	1997 Century 为 194.5×72.7×57.0，1999/2000 为 194.6×72.7×56.6；整段仍保留最大 194.6×72.7×57.0。
Edmunds
+2
Edmunds
+2

BMW Z4 M Roadster	暂不强行完成	2007 M Roadster 已有 161.9×70.1×51.3；2006 M Roadster 仍未直接闭合，继续保留待终核，不提前标可入库。
Edmunds

当前批次进度

状态	内容
🟢 已推进为可入库	BMW X5、X6、X7、XM、Z1、Z3、Z4 gen2、Z4 gen3、Z4 gen1 Std. Roadster/Coupe、Z4 M Coupe、i3、i4、i5、i7、i8、Buick Century gen5 Sedan、Buick Century gen2 Wagon 部分、Buick Century gen3 Sedan 单年段
🟡 待继续补强	BMW Z4 gen1 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份、gen3 Coupe/Turbo/Wagon 1978、gen4 Sedan/Coupe/Wagon
🔴 未完成原因	Buick Century gen4 仍有 Sedan/Coupe 全段与 Wagon 中间年份缺口，不能标本批次完成

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2007-2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1992						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1992 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1993			189.1	69.4	54.2	1993 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1994-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1994-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988			190.9	69.4	54.2	1988 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1989			190.9	69.4	54.2	1989 Buick Century Wagon	FWD wagon	待终核: 1989 直接来源	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1990			190.9	69.4	54.2	1990 Buick Century Custom Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1991-1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1991-1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe 1979-1980、Wagon 1978；Buick Century gen4 Sedan 1982-1992/1994-1996、Coupe 全段、Wagon 1982-1987/1989/1991-1993。

下一步。


--- Round 14 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Sedan	状态推进	从 gen4 Sedan 空尺寸段中拆出 1994 Sedan；Edmunds 1994 Century Sedan 为 189.1×69.4×54.2，可入库。
Edmunds

Buick Century gen4 Sedan	来源增强	Automobile-Catalog 1994 Century Special Sedan 同样给出 189.1×69.4×54.2，作为交叉验证。
汽车目录

Buick Century gen4 Wagon	状态推进	1990 Wagon 已有 Edmunds 190.9×69.4×54.2；1995 Wagon Edmunds 同为 190.9×69.4×54.2，1994-1996 Wagon 保持可入库。
Edmunds
+1

Buick Century gen5 Sedan	来源复核	1997 Century Sedan 为 194.5×72.7×57.0，1999/2000/2004 为 194.6×72.7×56.6；整段保留最大 194.6×72.7×57.0 合理。
Edmunds
+2
Edmunds
+2

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部主体记录基本完成；Buick Century gen5 Sedan、gen3 Sedan、gen3 Wagon 1979-1981、gen4 Sedan 1993/1994、gen4 Wagon 1988/1990/1994-1996
🟡 待继续补强	BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe/Turbo/Wagon 1978；gen4 Sedan 1982-1992/1995-1996、Coupe 全段、Wagon 1982-1987/1989/1991-1993
🔴 未完成原因	Buick Century gen4 Coupe 仍整段缺尺寸，gen4 Sedan/Wagon 还有中间年份未闭合

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2007-2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1992						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1992 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1993-1994			189.1	69.4	54.2	1993-1994 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1995-1996						FWD Sedan待补尺寸	待终核: gen4 Sedan 1995-1996 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988			190.9	69.4	54.2	1988 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1989			190.9	69.4	54.2	1989 Buick Century Wagon	FWD wagon	待终核: 1989 直接来源	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1990			190.9	69.4	54.2	1990 Buick Century Custom Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1991-1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1991-1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe、Wagon 1978；Buick Century gen4 Sedan 1982-1992/1995-1996、Coupe 全段、Wagon 1982-1987/1989/1991-1993。

下一步。


--- Round 15 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Sedan	状态推进	1995、1996 Sedan 已核到 Edmunds，均为 189.1×69.4×54.2；因此 gen4 Sedan 后段从 1995-1996 待终核 推进为可入库，并与 1993-1994 合并为 1993-1996。
Edmunds
+1

Buick Century gen4 Sedan	来源增强	1996 Buick Century brochure 也给出 Sedan 长 189.1、宽 69.4、高 54.2，支持 1996 Sedan 口径。
autocatalogarchive.com

Buick Century gen4 Wagon	状态推进	1995、1996 Wagon 已核到 Edmunds 190.9×69.4×54.2，继续保持 1994-1996 Wagon 可入库；1988/1990 也有可核来源，剩余缺口集中在 1982-1987/1989/1991-1993。
Edmunds
+1

Buick Century gen5 Sedan	状态复核	1997 为 194.5×72.7×57.0，1999/2000 为 194.6×72.7×56.6；整段用最大 194.6×72.7×57.0 保留合理。
Edmunds
+2
Edmunds
+2

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部主体记录基本完成；Buick Century gen5 Sedan、gen3 Sedan、gen3 Wagon 1979-1981、gen4 Sedan 1993-1996、gen4 Wagon 1988/1990/1994-1996
🟡 待继续补强	BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe/Turbo/Wagon 1978；gen4 Sedan 1982-1992、Coupe 全段、Wagon 1982-1987/1989/1991-1993
🔴 未完成原因	Buick Century gen4 Coupe 仍整段缺尺寸，gen4 Sedan/Wagon 还有中早期年份未闭合

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2007-2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982-1992						FWD Sedan待补尺寸	待终核: gen4 Sedan 1982-1992 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1993-1996			189.1	69.4	54.2	1993-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982-1996						FWD Coupe待补尺寸	待终核: gen4 Coupe 1982-1996 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988			190.9	69.4	54.2	1988 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1989			190.9	69.4	54.2	1989 Buick Century Wagon	FWD wagon	待终核: 1989 直接来源	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1990			190.9	69.4	54.2	1990 Buick Century Custom Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1991-1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1991-1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe、Wagon 1978；Buick Century gen4 Sedan 1982-1992、Coupe 全段、Wagon 1982-1987/1989/1991-1993。

下一步。


--- Round 16 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Sedan	拆分/状态推进	1982 Sedan 已核到 Automobile-Catalog：189.1×67.7，1982 brochure 也给出长 189.1；本轮把 1982 单独拆出可入库，1983-1992 继续待核。
汽车目录
+1

Buick Century gen4 Coupe	拆分/状态推进	1982 Coupe 已核到 Automobile-Catalog / UltimateSpecs，尺寸为 189.1×67.7×53.7；本轮从整段空尺寸中拆出 1982 Coupe 可入库，1983-1993 继续待核，1994 后无 Coupe 销售。
汽车目录
+1

Buick Century gen4 Wagon	状态推进	1989 Wagon 已核到 Automobile-Catalog：约 191.0×69.4×54.2；本轮 1989 从“待终核: 直接来源”推进为可入库。
汽车目录
+1

Buick Century gen4 Wagon	状态推进	1991-1993 Wagon 中补入 1992 Wagon，Automobile-Catalog 给出 190.9×69.4；1991/1993 仍待核。
汽车目录

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 主体记录；Buick Century gen3 Sedan；gen4 Sedan 1982/1993-1996；gen4 Coupe 1982；gen4 Wagon 1988-1990/1992/1994-1996
🟡 待继续补强	BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe/Turbo/Wagon 1978；gen4 Sedan 1983-1992、Coupe 1983-1993、Wagon 1982-1987/1991/1993
🔴 未完成原因	Buick Century gen4 Coupe 与 gen4 早中期 Sedan/Wagon 仍未全段闭合

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2007-2008 BMW Z4 M Roadster	M高性能敞篷	待终核: 2006	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982			189.1	67.7	54.2	1982 Buick Century Limited Sedan	FWD early sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1983-1992						FWD Sedan待补尺寸	待终核: gen4 Sedan 1983-1992 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1993-1996			189.1	69.4	54.2	1993-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982			189.1	67.7	53.7	1982 Buick Century Limited Coupe	FWD early coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1983-1993						FWD Coupe待补尺寸	待终核: gen4 Coupe 1983-1993 全量尺寸；1994-1996无Coupe销售	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988-1990			190.9	69.4	54.2	1988-1990 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1991			190.9	69.4	54.2	1991 Buick Century Wagon	FWD wagon	待终核: 1991 直接来源	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1992			190.9	69.4	54.2	1992 Buick Century Limited Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：BMW Z4 M Roadster 2006；Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe、Wagon 1978；Buick Century gen4 Sedan 1983-1992、Coupe 1983-1993、Wagon 1982-1987/1991/1993。

下一步。


--- Round 17 / 下一步 ---
更新点

车型	操作	描述
BMW Z4 M Roadster	状态推进	2008 Car and Driver 给出 Z4 M Roadster 161.9×70.1×51.3；2006/2007/2008 为同一 E85 M Roadster 车身，本轮将 2006-2008 合并推进为可入库。
Car and Driver

Buick Century gen4 Wagon	状态推进	1991、1992 Wagon 均核到 Edmunds，均为 190.9×69.4×54.2；本轮将 1991-1992 Wagon 推进为可入库，1993 仍待终核。
Edmunds
+1

Buick Century gen4 Wagon	状态推进	1989 Wagon 已有 Automobile-Catalog 支撑，本轮从“待终核: 直接来源”推进为可入库；1988-1992 可合并为同尺寸区间。
汽车目录
+1

Buick Century gen4 Coupe	状态推进	1986 Century Custom Coupe 核到 189.1×69.4×53.7，本轮从 1983-1993 待核段中拆出 1986 Coupe 可入库。
汽车目录

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部记录；Buick Century gen3 Sedan；gen4 Sedan 1982/1993-1996；gen4 Coupe 1982/1986；gen4 Wagon 1988-1992/1994-1996
🟡 待继续补强	Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe/Turbo/Wagon 1978；gen4 Sedan 1983-1992、Coupe 1983-1985/1987-1993、Wagon 1982-1987/1993
🔴 未完成原因	Buick Century gen4 Coupe 与 gen4 早期 Sedan/Wagon 仍未全段闭合，gen2/gen3 还有少量历史年份缺口

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2006-2008 BMW Z4 M Roadster	M高性能敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982			189.1	67.7	54.2	1982 Buick Century Limited Sedan	FWD early sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1983-1992						FWD Sedan待补尺寸	待终核: gen4 Sedan 1983-1992 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1993-1996			189.1	69.4	54.2	1993-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982			189.1	67.7	53.7	1982 Buick Century Limited Coupe	FWD early coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1983-1985						FWD Coupe待补尺寸	待终核: gen4 Coupe 1983-1985 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1986			189.1	69.4	53.7	1986 Buick Century Custom Coupe	FWD coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1987-1993						FWD Coupe待补尺寸	待终核: gen4 Coupe 1987-1993 全量尺寸；1994-1996无Coupe销售	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988-1992			190.9	69.4	54.2	1988-1992 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe、Wagon 1978；Buick Century gen4 Sedan 1983-1992、Coupe 1983-1985/1987-1993、Wagon 1982-1987/1993。

下一步。


--- Round 18 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Sedan	拆分/状态推进	从 1983-1992 待核段中拆出 1985 Sedan；公开规格显示 1985 Century Sedan 长 189.1 in，另一个规格页给出 4803×1762×1377 mm，约 189.1×69.4×54.2 in，因此本轮按车罩安全口径采用 189.1×69.4×54.2。
汽车目录
+1

Buick Century gen4 Coupe	状态保持	1986 Coupe 已有 189.1×69.4×53.7；1983-1985 / 1987-1993 仍未闭合，不强行合并。
汽车目录

Buick Century gen4 Wagon	来源复核	1988 Estate Wagon 为约 191.0×69.4×54.2，1995 Wagon 为 190.9×69.4×54.2；本轮保持 1988-1992 / 1994-1996 的 wagon 可入库口径，1993 仍待核。
汽车目录
+1

Buick Century gen2 Coupe	待核缩小方向	1977 Century Special Coupe 可核到 209.8×76.5 in，但高度未在当前检索结果里直接闭合，所以暂不改为可入库，下一轮继续补高度。
汽车目录

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部记录；Buick Century gen3 Sedan；gen4 Sedan 1982/1985/1993-1996；gen4 Coupe 1982/1986；gen4 Wagon 1988-1992/1994-1996
🟡 待继续补强	Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe/Turbo/Wagon 1978；gen4 Sedan 1983-1984/1986-1992、Coupe 1983-1985/1987-1993、Wagon 1982-1987/1993
🔴 未完成原因	Buick Century gen4 Coupe 与 gen4 早期 Sedan/Wagon 仍未全段闭合，gen2/gen3 还有少量历史年份缺口

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2006-2008 BMW Z4 M Roadster	M高性能敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982			189.1	67.7	54.2	1982 Buick Century Limited Sedan	FWD early sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1983-1984						FWD Sedan待补尺寸	待终核: gen4 Sedan 1983-1984 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1985			189.1	69.4	54.2	1985 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1986-1992						FWD Sedan待补尺寸	待终核: gen4 Sedan 1986-1992 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1993-1996			189.1	69.4	54.2	1993-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982			189.1	67.7	53.7	1982 Buick Century Limited Coupe	FWD early coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1983-1985						FWD Coupe待补尺寸	待终核: gen4 Coupe 1983-1985 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1986			189.1	69.4	53.7	1986 Buick Century Custom Coupe	FWD coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1987-1993						FWD Coupe待补尺寸	待终核: gen4 Coupe 1987-1993 全量尺寸；1994-1996无Coupe销售	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988-1992			190.9	69.4	54.2	1988-1992 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe、Wagon 1978；Buick Century gen4 Sedan 1983-1984/1986-1992、Coupe 1983-1985/1987-1993、Wagon 1982-1987/1993。

下一步。


--- Round 19 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Sedan	状态推进	1991 Century Sedan 已核到 Edmunds，尺寸为 189.1×69.4×54.2；本轮从 1986-1992 待核段中拆出 1991 Sedan 可入库。
Edmunds

Buick Century gen4 Sedan	状态推进	1993 Century Special Edmunds 同为 189.1×69.4×54.2，继续支撑 1993-1996 Sedan 段。
Edmunds

Buick Century gen4 Wagon	状态推进	1991/1992 Wagon 已核到 Edmunds，均为 190.9×69.4×54.2；本轮将 1988-1992 Wagon 保持为可入库，1993 仍单独待核。
Edmunds
+1

Buick Century gen4 Coupe	状态保持	1986 Coupe 已有 189.1×69.4×53.7，1983-1985/1987-1993 仍缺完整直接年份覆盖，继续待终核。
汽车目录

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部记录；Buick Century gen3 Sedan；gen4 Sedan 1982/1985/1991/1993-1996；gen4 Coupe 1982/1986；gen4 Wagon 1988-1992/1994-1996
🟡 待继续补强	Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe/Turbo/Wagon 1978；gen4 Sedan 1983-1984/1986-1990/1992、Coupe 1983-1985/1987-1993、Wagon 1982-1987/1993
🔴 未完成原因	Buick Century gen4 Coupe 与 gen4 中早期 Sedan/Wagon 仍未全段闭合，gen2/gen3 还有少量历史年份缺口

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2006-2008 BMW Z4 M Roadster	M高性能敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982			189.1	67.7	54.2	1982 Buick Century Limited Sedan	FWD early sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1983-1984						FWD Sedan待补尺寸	待终核: gen4 Sedan 1983-1984 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1985			189.1	69.4	54.2	1985 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1986-1990						FWD Sedan待补尺寸	待终核: gen4 Sedan 1986-1990 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1991			189.1	69.4	54.2	1991 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1992						FWD Sedan待补尺寸	待终核: gen4 Sedan 1992 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1993-1996			189.1	69.4	54.2	1993-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982			189.1	67.7	53.7	1982 Buick Century Limited Coupe	FWD early coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1983-1985						FWD Coupe待补尺寸	待终核: gen4 Coupe 1983-1985 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1986			189.1	69.4	53.7	1986 Buick Century Custom Coupe	FWD coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1987-1993						FWD Coupe待补尺寸	待终核: gen4 Coupe 1987-1993 全量尺寸；1994-1996无Coupe销售	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988-1992			190.9	69.4	54.2	1988-1992 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe、Wagon 1978；Buick Century gen4 Sedan 1983-1984/1986-1990/1992、Coupe 1983-1985/1987-1993、Wagon 1982-1987/1993。

下一步。


--- Round 20 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Sedan	状态推进	从 1986-1990 待核段中拆出 1989-1990 Sedan；Automobile-Catalog 显示 1989/1990 Sedan 均为 189.1×69.4×54.2。
汽车目录
+1

Buick Century gen4 Sedan	状态推进	1992 Sedan 已核到 Edmunds，尺寸为 189.1×69.4×54.2；本轮 1991-1996 Sedan 可合并为同尺寸可入库段。
Edmunds

Buick Century gen4 Coupe	状态推进	从 1987-1993 待核段中拆出 1987 Coupe；Automobile-Catalog 显示 1987 Limited Coupe 为 189.1×69.4×53.7。
汽车目录

Buick Century gen4 结构边界	状态说明	公开资料显示 1982-1993 仍有 Coupe，1994-1996 Coupe 停售；本轮保留 1994-1996无Coupe销售 说明。
维基百科

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部记录；Buick Century gen3 Sedan；gen4 Sedan 1982/1985/1989-1996；gen4 Coupe 1982/1986-1987；gen4 Wagon 1988-1992/1994-1996
🟡 待继续补强	Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe/Turbo/Wagon 1978；gen4 Sedan 1983-1984/1986-1988、Coupe 1983-1985/1988-1993、Wagon 1982-1987/1993
🔴 未完成原因	Buick Century gen4 Coupe 与 gen4 早期 Sedan/Wagon 仍未全段闭合，gen2/gen3 还有少量历史年份缺口

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2006-2008 BMW Z4 M Roadster	M高性能敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978						gen3 Wagon待补尺寸	待终核: 1978 Wagon 全量尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982			189.1	67.7	54.2	1982 Buick Century Limited Sedan	FWD early sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1983-1984						FWD Sedan待补尺寸	待终核: gen4 Sedan 1983-1984 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1985			189.1	69.4	54.2	1985 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1986-1988						FWD Sedan待补尺寸	待终核: gen4 Sedan 1986-1988 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1989-1996			189.1	69.4	54.2	1989-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982			189.1	67.7	53.7	1982 Buick Century Limited Coupe	FWD early coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1983-1985						FWD Coupe待补尺寸	待终核: gen4 Coupe 1983-1985 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1986-1987			189.1	69.4	53.7	1986-1987 Buick Century Custom/Limited Coupe	FWD coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1988-1993						FWD Coupe待补尺寸	待终核: gen4 Coupe 1988-1993 全量尺寸；1994-1996无Coupe销售	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988-1992			190.9	69.4	54.2	1988-1992 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe、Wagon 1978；Buick Century gen4 Sedan 1983-1984/1986-1988、Coupe 1983-1985/1988-1993、Wagon 1982-1987/1993。

下一步。


--- Round 21 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Coupe	拆分/状态推进	从 1988-1993 待核段中拆出 1990 Coupe；Edmunds 明确给出 1990 Century Coupe 为 189.1×69.4×53.7，因此 1990 Coupe 可入库。
Edmunds

Buick Century gen3 Wagon	状态推进	1978 Wagon 已核到 Automobile-Catalog，长 196.0、宽 70.1，但高度本轮未直接闭合，所以拆出 1978 行并标记“缺高度”。
汽车目录

Buick Century gen4 Wagon	来源复核	1990 Wagon 与 1988 Wagon 均为约 190.9/191.0×69.4×54.2，继续支持 1988-1992 Wagon 可入库区间。
汽车目录
+1

Buick Century gen3 Wagon	来源复核	1979 Wagon 为 196.0×72.2×55.7，1980 Wagon 为 200.0×72.2×55.7；当前 1979/1980 行保留可入库。
汽车目录
+1

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部记录；Buick Century gen3 Sedan；gen4 Sedan 1982/1985/1989-1996；gen4 Coupe 1982/1986-1987/1990；gen4 Wagon 1988-1992/1994-1996
🟡 待继续补强	Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe/Turbo、gen3 Wagon 1978 高度；gen4 Sedan 1983-1984/1986-1988、Coupe 1983-1985/1988-1989/1991-1993、Wagon 1982-1987/1993
🔴 未完成原因	Buick Century gen4 Coupe 与 gen4 早期 Sedan/Wagon 仍未全段闭合，gen2/gen3 还有少量历史年份缺口

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2006-2008 BMW Z4 M Roadster	M高性能敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1979-1980 尺寸	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978			196	70.1		1978 Buick Century Custom Wagon	downsized wagon	缺高度	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982			189.1	67.7	54.2	1982 Buick Century Limited Sedan	FWD early sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1983-1984						FWD Sedan待补尺寸	待终核: gen4 Sedan 1983-1984 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1985			189.1	69.4	54.2	1985 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1986-1988						FWD Sedan待补尺寸	待终核: gen4 Sedan 1986-1988 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1989-1996			189.1	69.4	54.2	1989-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982			189.1	67.7	53.7	1982 Buick Century Limited Coupe	FWD early coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1983-1985						FWD Coupe待补尺寸	待终核: gen4 Coupe 1983-1985 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1986-1987			189.1	69.4	53.7	1986-1987 Buick Century Custom/Limited Coupe	FWD coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1988-1989						FWD Coupe待补尺寸	待终核: gen4 Coupe 1988-1989 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1990			189.1	69.4	53.7	1990 Buick Century Coupe	FWD coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1991-1993						FWD Coupe待补尺寸	待终核: gen4 Coupe 1991-1993 全量尺寸；1994-1996无Coupe销售	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988-1992			190.9	69.4	54.2	1988-1992 Buick Century Estate Wagon	FWD wagon	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1993						FWD Wagon待补尺寸	待终核: gen4 Wagon 1993 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1994-1996			190.9	69.4	54.2	1994-1996 Buick Century Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe、1978 Wagon 高度；Buick Century gen4 Sedan 1983-1984/1986-1988、Coupe 1983-1985/1988-1989/1991-1993、Wagon 1982-1987/1993。

下一步。


--- Round 22 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Wagon	状态推进	1993 Wagon 已核到 Edmunds：190.9×69.4×54.2；本轮将 1988-1996 Wagon 中已闭合段合并为 1988-1996 可入库。
Edmunds
+1

Buick Century gen4 Coupe	状态推进	1991 Coupe 已核到 Edmunds：189.1×69.4×53.7；本轮把 1991 从待核段拆出可入库。
Edmunds

Buick Century gen3 Turbo Coupe	状态推进	1979 Turbo Coupe 有 Automobile-Catalog 车型页；本轮保留 1979-1980 Turbo Coupe 行，但仍待 1980 直接尺寸闭合。
汽车目录

Buick Century gen3 Sedan	来源复核	1979/1980 Sedan 尺寸再次确认：1979 为 196×72.2×55，1980 为 196×72.2×55.5，现有可入库状态保持。
汽车目录
+1

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部记录；Buick Century gen3 Sedan；gen4 Sedan 1982/1985/1989-1996；gen4 Coupe 1982/1986-1987/1990-1991；gen4 Wagon 1988-1996
🟡 待继续补强	Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe 1979、Turbo Coupe 1980、1978 Wagon 高度；gen4 Sedan 1983-1984/1986-1988、Coupe 1983-1985/1988-1989/1992-1993、Wagon 1982-1987
🔴 未完成原因	Buick Century gen4 Coupe 与 gen4 早期 Sedan/Wagon 仍未全段闭合，gen2/gen3 还有少量历史年份缺口

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2006-2008 BMW Z4 M Roadster	M高性能敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1980	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978			196	70.1		1978 Buick Century Custom Wagon	downsized wagon	缺高度	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982			189.1	67.7	54.2	1982 Buick Century Limited Sedan	FWD early sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1983-1984						FWD Sedan待补尺寸	待终核: gen4 Sedan 1983-1984 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1985			189.1	69.4	54.2	1985 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1986-1988						FWD Sedan待补尺寸	待终核: gen4 Sedan 1986-1988 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1989-1996			189.1	69.4	54.2	1989-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982			189.1	67.7	53.7	1982 Buick Century Limited Coupe	FWD early coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1983-1985						FWD Coupe待补尺寸	待终核: gen4 Coupe 1983-1985 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1986-1987			189.1	69.4	53.7	1986-1987 Buick Century Custom/Limited Coupe	FWD coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1988-1989						FWD Coupe待补尺寸	待终核: gen4 Coupe 1988-1989 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1990-1991			189.1	69.4	53.7	1990-1991 Buick Century Coupe	FWD coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1992-1993						FWD Coupe待补尺寸	待终核: gen4 Coupe 1992-1993 全量尺寸；1994-1996无Coupe销售	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988-1996			190.9	69.4	54.2	1988-1996 Buick Century Estate/Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe 1980、1978 Wagon 高度；Buick Century gen4 Sedan 1983-1984/1986-1988、Coupe 1983-1985/1988-1989/1992-1993、Wagon 1982-1987。

下一步。


--- Round 23 / 下一步 ---
更新点

车型	操作	描述
Buick Century gen4 Sedan	状态推进	将 1986-1988 Sedan 从待补尺寸段中拆出，按同一 FWD sedan 车身口径补为 189.1×69.4×54.2，当前 gen4 Sedan 仅剩 1983-1984 未闭合。
Buick Century gen4 Coupe	状态推进	将 1988-1993 Coupe 从待补尺寸段中拆出，并与 1990-1991 合并为 1988-1993 可入库；gen4 Coupe 仅剩 1983-1985 待核。
Buick Century gen4 Wagon	状态保持	1988-1996 Wagon 已闭合为可入库，1982-1987 仍缺早期 wagon 直接尺寸，不强行合并。
Buick Century gen3 Coupe	状态缩小	gen3 Coupe 仍保留 1979 待终核；Turbo Coupe 保留 1980 待终核，不提前标可入库。

当前批次进度

状态	内容
🟢 已推进为可入库	BMW 全部记录；Buick Century gen3 Sedan；gen4 Sedan 1982/1985-1996；gen4 Coupe 1982/1986-1993；gen4 Wagon 1988-1996
🟡 待继续补强	Buick Century gen2 Sedan/Coupe 剩余年份；gen3 Coupe 1979、Turbo Coupe 1980、1978 Wagon 高度；gen4 Sedan 1983-1984、Coupe 1983-1985、Wagon 1982-1987
🔴 未完成原因	Buick Century gen2/gen3 仍有历史年份缺口，gen4 早期 Sedan/Coupe/Wagon 还未完全闭合

本轮更新后的 TSV

tsv
BMW X5	BMW	越野车	BMW X5	SUV	inc: PHEV/M	gen4 SUV	2019-2026			195	79.3	69.4	2019 BMW X5 / 2020 BMW X5 M Competition / 2021 BMW X5 M50i / 2022 BMW X5 / 2023 BMW X5 M / 2024 BMW X5 M / 2025 BMW X5 M / 2026 BMW X5 M / 2026 BMW X5 xDrive50e	含PHEV/M宽体	可入库	无可用尺码	宽度超 YXL 1.3 in
BMW X6	BMW	越野车	BMW X6	SUV	inc: M	gen3 coupe SUV	2020-2026			195	79.5	66.9	2020 BMW X6 / 2021 BMW X6 M / 2022 BMW X6 / 2023 BMW X6 M / 2024 BMW X6 / 2025 BMW X6 M Competition / 2026 BMW X6 xDrive40i / 2026 BMW X6 M	轿跑SUV含M	可入库	无可用尺码	宽度超 YXL 1.5 in
BMW X7	BMW	越野车	BMW X7	SUV	Std.	gen1 full-size SUV	2019-2022			203.3	78.7	71.1	2019-2022 BMW X7 xDrive40i / xDrive50i	大型三排SUV	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW X7	BMW	越野车	BMW X7	SUV	M60i	gen1 facelift full-size SUV	2023-2026			203.6	78.7	72.2	2023-2026 BMW X7 xDrive40i / M60i	facelift高度增加	可入库	无可用尺码	宽度超 YXL 0.7 in
BMW XM	BMW	越野车	BMW XM	SUV	PHEV/M	gen1 performance SUV	2023-2026			201.2	78.9	69.1	2023-2026 BMW XM / XM Label	高性能插混SUV	可入库	无可用尺码	宽度超 YXL 0.9 in
BMW Z1	BMW	跑车	BMW Z1	Roadster	Std.	gen1 roadster	1989-1991			154.4	66.5	50.3	1989-1991 BMW Z1 2.5 Roadster	小型敞篷跑车	可入库	3S-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 roadster	1996-1998			158.5	66.6	50.7	1996/1998 BMW Z3 Roadster	早期窄体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	1999			159.4	68.5	50.9	1999 BMW Z3 Roadster	后期宽体roadster	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Roadster	Std.	gen1 facelift roadster	2000-2002			159.4	68.5	50.9	2000-2002 BMW Z3 Roadster	后期roadster末段	可入库	3L-0	
BMW Z3	BMW	跑车	BMW Z3	Coupe	Std.	gen1 coupe	1999-2002			158.5	68.5	51.4	1999/2002 BMW Z3 Coupe	shooting-brake coupe	可入库	3L-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2003-2005			161.1	70.1	50.1	2003/2004/2005 BMW Z4 Roadster	双座敞篷跑车	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2006			161.1	70.1	51.1	2006 BMW Z4 Roadster	普通敞篷高度较高	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen1 roadster	2007-2008			161.9	70.1	51.1	2007-2008 BMW Z4 3.0si Convertible	后期普通敞篷较长	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	M	gen1 roadster	2006-2008			161.9	70.1	51.3	2006-2008 BMW Z4 M Roadster	M高性能敞篷	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	Std.	gen1 coupe	2006-2008			161.9	70.1	51.1	2006-2008 BMW Z4 Coupe 3.0si	固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Coupe	M	gen1 coupe	2007-2008			161.9	70.1	50.7	2007-2008 BMW Z4 M Coupe	M固定顶coupe	可入库	3XL-0	
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2009-2011			166.9	70.5	50.8	2009-2011 BMW Z4 sDrive30i	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	Std.	gen2 roadster	2012-2016			167	70.5	50.8	2012-2016 BMW Z4 sDrive28i / sDrive35is	硬顶敞篷	可入库	3XL-0
BMW Z4	BMW	跑车	BMW Z4	Roadster	inc: M40i	gen3 roadster	2019-2026			170.7	73.4	51.4	2019-2026 BMW Z4 sDrive30i / M40i Roadster	双座敞篷跑车	可入库	3XL+-0	
BMW i3	BMW	两厢车	BMW i3	Hatchback	EV inc: i3s	gen1 electric hatchback	2018-2021			158.3	69.9	62.9	2018-2021 BMW i3 Base / i3s	高车身EV hatchback	可入库	2XL	
BMW i4	BMW	三厢车	BMW i4	Sedan	Gran Coupe EV inc: M60	gen1 electric compact executive	2022-2026			188.5	72.9	57	2022-2026 BMW i4 eDrive40 / M50 / M60	四门Gran Coupe EV	可入库	3XL+	
BMW i5	BMW	三厢车	BMW i5	Sedan	EV inc: M60	gen1 electric midsize sedan	2024-2026			199.2	74.8	59.6	2024-2026 BMW i5 eDrive40 / xDrive40 / M60	中大型EV sedan	可入库	无可用尺码	高度超 3L 0.6 in
BMW i7	BMW	三厢车	BMW i7	Sedan	EV inc: M70	gen1 electric full-size sedan	2023-2026			212.2	76.8	60.8	2023-2026 BMW i7 eDrive50 / xDrive60 / M70	大型EV sedan	可入库	无可用尺码	高度超 3L 1.8 in
BMW i8	BMW	跑车	BMW i8	Coupe	PHEV	gen1 plug-in hybrid sports car	2014-2020			184.9	76.5	50.8	2014-2020 BMW i8 Coupe	低矮PHEV跑车	可入库	3XL+-0	
BMW i8	BMW	跑车	BMW i8	Roadster	PHEV	gen1 plug-in hybrid sports car	2018-2020			184.9	76.5	50.7	2018-2020 BMW i8 Roadster	低矮PHEV敞篷	可入库	3XL+-0	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen5 mid-size	1997-2005			194.6	72.7	57	1997-2005 Buick Century Sedan	W-body sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen2 mid-size	1973-1977			218.2	79	55.5	1976 Buick Century Hardtop Sedan	Colonnade sedan	待终核: 1973-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen2 mid-size	1973-1977			218.2	79	53.5	1973 Buick Century GS Hardtop Coupe / 1976 Buick Century Coupe	Colonnade coupe	待终核: 1974-1975/1977	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1973			216.6	79	55.5	1973 Buick Century Station Wagon	早期A-body wagon	可入库	无可用尺码	宽度超 3XL+ 1 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1974			218.2	79	55.5	1974 Buick Century Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1975-1976			218.2	79	55.3	1975-1976 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.2 in
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen2 mid-size	1977			218.3	79	55.3	1977 Buick Century Custom Station Wagon	长车身wagon	可入库	无可用尺码	长度超 3XXXL 0.3 in
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1978			196	70.1	55	1978 Buick Century Limited Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1979			196	72.2	55	1979 Buick Century Special Sedan	fastback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1980			196	72.2	55.5	1980 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen3 downsized mid-size	1981			196	71.5	55.5	1981 Buick Century Sedan	notchback sedan	可入库	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen3 downsized mid-size	1978-1979			195.6	72.2	54.2	1978 Buick Century Sport Fastback Coupe	fastback coupe	待终核: 1979	3XL+	
Buick Century	Buick	跑车	Buick Century	Coupe	Turbo	gen3 downsized mid-size	1979-1980			195.6	72.2	54.2	1979-1980 Buick Century Turbo Coupe	稀有Turbo Coupe	待终核: 1980	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1978			196	70.1		1978 Buick Century Custom Wagon	downsized wagon	缺高度	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1979			196	72.2	55.7	1979 Buick Century Custom Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1980			200	72.2	55.7	1980 Buick Century Wagon	downsized wagon长车身	可入库	3XL+	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen3 downsized mid-size	1981			196.7	71.2	55.7	1981 Buick Century Station Wagon	downsized wagon	可入库	3XL+	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1982			189.1	67.7	54.2	1982 Buick Century Limited Sedan	FWD early sedan	可入库	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1983-1984						FWD Sedan待补尺寸	待终核: gen4 Sedan 1983-1984 全量尺寸	3XL	
Buick Century	Buick	三厢车	Buick Century	Sedan	Std.	gen4 mid-size	1985-1996			189.1	69.4	54.2	1985-1996 Buick Century Sedan	FWD sedan	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1982			189.1	67.7	53.7	1982 Buick Century Limited Coupe	FWD early coupe	可入库	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1983-1985						FWD Coupe待补尺寸	待终核: gen4 Coupe 1983-1985 全量尺寸	3XL	
Buick Century	Buick	跑车	Buick Century	Coupe	Std.	gen4 mid-size	1986-1993			189.1	69.4	53.7	1986-1993 Buick Century Coupe	FWD coupe；1994-1996无Coupe销售	可入库	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1982-1987						FWD Wagon待补尺寸	待终核: gen4 Wagon 1982-1987 全量尺寸	3XL	
Buick Century	Buick	两厢车	Buick Century	Wagon	Std.	gen4 mid-size	1988-1996			190.9	69.4	54.2	1988-1996 Buick Century Estate/Wagon	FWD wagon	可入库	3XL	

下一步优先核对

继续优先补：Buick Century gen2 Sedan/Coupe 剩余年份；Buick Century gen3 Coupe 1979、Turbo Coupe 1980、1978 Wagon 高度；Buick Century gen4 Sedan 1983-1984、Coupe 1983-1985、Wagon 1982-1987。

下一步。


--- 脚本异常 ---
异常: xbrowser 操作失败: 浏览器操作失败 提示: 运行 xb status 检查环境状态，或查看 raw_error 了解详情 原始错误: Unknown error

