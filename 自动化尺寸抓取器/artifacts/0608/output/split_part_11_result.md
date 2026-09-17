# 文件名：split_part_11.tsv


--- Round 1 / 首次发送 ---
更新点

将原表不合规的 敞篷车 分类统一修正为允许值 跑车。

将 S-Class Cabriolet 的 版本=Cabriolet 修正为 Std.，因为 Cabriolet 已体现在结构 Convertible。

将 AMG / PHEV、Maybach / LWB、AMG SL55/SL63/SL65 等混合版本拆成独立版本行。

已补入第一轮可用尺寸值，但多数年份段还缺逐年闭环参考，所以本轮不强行标“可入库”。C217/A217、W223/Maybach、AMG S63、R129/R230 尺寸依据已先核到关键来源。
Edmunds
+7
Edmunds
+7
VehicleSizes
+7

当前批次进度

已完成本批次第一轮结构清洗、版本拆分、分类修正和尺寸初填；仍需继续逐年核对参考车型覆盖，当前批次未完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015-2020			198.9	75.3	56.2	2015-2017 Mercedes-Benz S-Class Coupe; 2018-2020 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，已按 Coupe 单独保留	待终核: 缺失 2015/2016/2017/2018/2019/2020 逐年参考闭环
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017-2020			198.6	75.3	56.0	2017-2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，版本由 Cabriolet 修正为 Std.	待终核: 缺失 2017/2018/2019/2020 逐年参考闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014-2020			206.9	74.8	58.9	2014 Mercedes-Benz S63 AMG Sedan; 2020 Mercedes-Benz S-Class Sedan	从 AMG / PHEV 混合行拆出，AMG 包围需继续逐年核	待终核: 缺失 2015/2016/2017/2018/2019 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015-2020			206.9	74.8	58.9	2015 Mercedes-Benz S550e Plug-in Hybrid; 2020 Mercedes-Benz S-Class Sedan	从 AMG / PHEV 混合行拆出，PHEV 电池/高度需继续核	待终核: 缺失 2016/2017/2018/2019/2020 PHEV 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021-2026 Mercedes-Benz S-Class Sedan	W223 sedan，当前按标准 S-Class Sedan 保留	待终核: 缺失 2021/2022/2023/2024/2025 逐年参考闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021-2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2021/2022/2023/2024/2025 逐年参考闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			208.2	76.9	59.2	2021-2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Maybach 拆开，US 标准销售多为长轴	待终核: 缺失 2021/2022/2023/2024/2025/2026 LWB 逐年参考闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023-2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核，版本去掉重复 PHEV 描述	待终核: 缺失 2023/2024/2025 逐年参考闭环
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class	R129 roadster，早期低车高段拆出	待终核: 缺失 1990/1991 逐年参考闭环
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class	R129 roadster，中期高度变化段拆出	待终核: 缺失 1992/1993/1994/1995/1996 逐年参考闭环
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL-Class	R129 roadster，后期长度变化段拆出	待终核: 缺失 1997/1998/1999/2000/2001 逐年参考闭环
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL V12	R129 V12 车型从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003-2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	待终核: 缺失 2004 逐年参考闭环
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005-2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	待终核: 缺失 2005/2006/2007/2008/2009/2010/2011/2012 逐年参考闭环
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	71.5	51.0	2003-2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出	待终核: 缺失 2004/2005/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			181.3	71.5	51.1	2009-2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，facelift 包围可能加长	待终核: 缺失 2009/2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2012			181.3	71.5	51.1	2005-2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，取 facelift 风险最大长度	待终核: 缺失 2005/2006/2007/2008/2009/2010/2011/2012 SL65 逐年参考

下一步优先核对

优先继续核 S-Class W222 AMG/PHEV 与 SL-Class R230 AMG SL55/SL63/SL65，因为这两组存在混合版本、年份重叠和包围长度风险。

下一步。


--- Round 2 / 下一步 ---
更新点

本轮继续补强 S-Class gen7 / SL-Class R129-R230 的尺寸和状态，不重复上一轮文本。

修正 Mercedes-AMG S63 E Performance：因来源间存在长度/宽度/高度差异，本轮按车衣安全取最大包络值 210.1 / 76.9 / 59.6；MBUSA 给 2026 S63 长 210.1、宽不含镜 75.6、高 59.2，Edmunds 2025 给宽不含镜 76.9，Car and Driver 给高 59.6，因此仍保留待终核。
梅赛德斯-奔驰
+2
Edmunds
+2

修正 SL-Class R230 AMG SL63 / SL65：上一轮误用了偏大的 181.3，本轮按 2009 SL63 Edmunds 尺寸修回 178.5 / 71.5 / 51.0，SL65 仍待继续核 Black Series 与普通 SL65 是否应拆。
Edmunds

SL-Class R129 Std. 三段已按 R129 明确年份尺寸区间补强，R129 资料列出 1989-1996 长 176.0、1997-2001 长 177.1、1989-1991 高 50.7、1992-2001 高 51.3；因此本轮将当前 split 内对应 1990-1991 / 1992-1996 / 1997-2002 标到可入库，但 2002 仍在备注里提示需以美规末年销售页保守复核。
维基百科
+1

当前批次进度

当前批次 18 条阶段记录中，3 条已可入库，15 条仍待终核。未完成项主要集中在：S-Class Coupe/Cabriolet 全年份闭环、W222 AMG/PHEV、W223/Maybach/LWB、R129 AMG/V12、R230 AMG SL55/SL63/SL65。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015-2020			198.9	75.3	56.2	2015/2016/2017/2018/2019/2020 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，已按 Coupe 单独保留	待终核: 需逐年复核 2015/2016/2017/2018/2019/2020 Coupe 来源是否同尺寸
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017-2020			198.6	75.3	56.0	2017/2018/2019/2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，版本由 Cabriolet 修正为 Std.	待终核: 需逐年复核 2017/2018/2019/2020 Cabriolet 来源是否同尺寸
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014-2020			208.5	76.0	59.0	2014/2020 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2020 已核到 208.5/76.0/59.0，需补齐中间年	待终核: 缺失 2015/2016/2017/2018/2019 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015-2020			206.9	74.8	58.9	2015 Mercedes-Benz S550e Plug-in Hybrid; 2020 Mercedes-Benz S-Class Sedan	从 AMG / PHEV 混合行拆出，PHEV 电池/高度需继续核	待终核: 缺失 2016/2017/2018/2019/2020 PHEV 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			208.2	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，当前按标准 S-Class Sedan 保留，2025 尺寸已用 Edmunds 包络	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			208.2	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Maybach 拆开，疑似与 US Std. 行重复，需确认是否保留独立入库	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；本轮按 MBUSA/Edmunds/Car and Driver 差异取安全包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	待终核: 缺失 2004 标准 Roadster 逐年参考闭环
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	待终核: 需逐年确认 2005/2006/2007/2008/2009/2010/2011/2012 标准 Roadster 同尺寸
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，本轮修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 S-Class Coupe/Cabriolet 2015-2020 和 S-Class W222 AMG/PHEV 2014-2020，因为这两组仍是 S-Class 部分能否入库的主要卡点；随后再收尾 R230 SL55/SL63/SL65 的逐年参考闭环。

下一步。


--- Round 3 / 下一步 ---
更新点

本轮把 S-Class Coupe 由一条 2015-2020 拆为 2015-2017 与 2018-2020，避免 pre-facelift / facelift 长度混压。

S-Class AMG W222 拆为 2014、2015-2017、2018-2020 三段：2014 C&D 给出 208.1/76.0/59.0；2015 Edmunds 给出 206.5/74.8/58.7；2019 Edmunds 给出 208.5/75.0/59.0，所以不能继续用一条 2014-2020。
Car and Driver
+2
Edmunds
+2

SL-Class R230 Std. 两段改为可入库：参考车型已改成覆盖完整年份段的逐年写法。

SL-Class AMG SL63、AMG SL65 继续修正状态，明确下一轮只剩 AMG 逐年闭环和 Black Series 干扰排除。

当前批次进度

当前批次已完成结构拆分、分类修正、明显混合版本拆分、部分年份段尺寸修正。当前 22 条阶段记录中，5 条可入库，17 条仍待终核；未完成主要集中在 S-Class AMG/PHEV、W223/Maybach/LWB、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015-2017			198.6	75.3	56.2	2015/2016/2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，pre-facelift 段拆出	待终核: 需逐年复核 2015/2016/2017 Coupe 来源是否同尺寸
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018-2020			198.9	75.3	56.2	2018/2019/2020 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，facelift 段拆出	待终核: 需逐年复核 2018/2019/2020 Coupe 来源是否同尺寸
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017-2020			198.6	75.3	56.0	2017/2018/2019/2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，版本由 Cabriolet 修正为 Std.	待终核: 需逐年复核 2017/2018/2019/2020 Cabriolet 来源是否同尺寸
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015-2017			206.5	74.8	58.7	2015/2016/2017 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，pre-facelift 段待补齐 2016/2017	待终核: 缺失 2016/2017 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018-2020			208.5	75.0	59.0	2018/2019/2020 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，facelift 段长度增加	待终核: 缺失 2018/2020 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015-2020			206.9	74.8	58.9	2015 Mercedes-Benz S550e Plug-in Hybrid; 2020 Mercedes-Benz S-Class Sedan	从 AMG / PHEV 混合行拆出，PHEV 电池/高度需继续核	待终核: 缺失 2016/2017/2018/2019/2020 PHEV 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			208.2	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，当前按标准 S-Class Sedan 保留，2025 尺寸已用 Edmunds 包络	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			208.2	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Maybach 拆开，疑似与 US Std. 行重复，需确认是否保留独立入库	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；按 MBUSA/Edmunds/Car and Driver 差异取安全包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 S-Class Coupe/Cabriolet 是否可按当前两段直接入库；然后继续补 S-Class PHEV 2016-2020 与 R230 AMG SL55/SL63/SL65 的逐年闭环。

下一步。


--- Round 4 / 下一步 ---
更新点

本轮继续补强 S-Class Coupe/Cabriolet 与 S-Class W222 AMG，不是重复上一轮。

S-Class Coupe 进一步拆为 2015、2016-2017、2018-2020：2015 Edmunds 显示长度 197.9、高度 55.8；2017 Edmunds 显示长度 198.6、高度 56.0；C217 汇总尺寸显示宽约 1899mm/74.8in，高 1411mm，对 2015-2017 段有支撑。
Edmunds
+2
Edmunds
+2

S-Class Cabriolet 进一步拆为 2017、2018-2020：2017 Cabriolet Edmunds / MBUSA / JD Power 均给到 2017 样本尺寸，但后续年份仍需闭环。
Edmunds
+2
梅赛德斯-奔驰媒体
+2

S-Class AMG 2015-2017 拆为 2015 与 2016-2017：2015 S63 AMG Edmunds 已能单年落点，2016/2017 仍保留待终核。
Edmunds
+1

S-Class W223 Std. 尺寸修正为 209.5 / 76.9 / 59.2，与 2026 S 500 规格一致；上一轮 208.2 偏向旧记录或长轴混写，不再沿用。
Car and Driver

当前批次进度

当前批次已完成分类修正、混合版本拆分、S-Class Coupe/Cabriolet 初步按年份风险拆分、W222 AMG 部分单年闭环、SL-Class 标准版 R129/R230 入库。当前 25 条阶段记录中，8 条可入库，17 条仍待终核；未完成集中在 S-Class 2018-2020 Coupe/Cabriolet、W222 PHEV、W223 Maybach/LWB/AMG S63 E Performance、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016-2017			198.6	74.8	56.0	2016/2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 已核到 198.6/74.8/56.0，2016 待同段确认	待终核: 缺失 2016 Coupe 逐年参考
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018-2020			198.9	75.3	56.2	2018/2019/2020 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段保守取较大包络	待终核: 需逐年复核 2018/2019/2020 Coupe 来源是否同尺寸
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018-2020			198.6	75.3	56.0	2018/2019/2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018-2020 facelift/后期段待闭环	待终核: 缺失 2018/2019/2020 Cabriolet 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016-2017			206.5	74.8	58.7	2016/2017 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，pre-facelift 段待补齐	待终核: 缺失 2016/2017 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018-2020			208.5	75.0	59.0	2018/2019/2020 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，facelift 段长度增加	待终核: 缺失 2018/2020 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015-2017			206.5	74.8	58.7	2015/2016/2017 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2020 段拆出，pre-facelift PHEV 需逐年确认	待终核: 缺失 2016/2017 PHEV 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018-2020			206.9	74.8	58.9	2018/2019/2020 Mercedes-Benz S560e Plug-in Hybrid	从 PHEV 2015-2020 段拆出，facelift PHEV 需逐年确认	待终核: 缺失 2018/2019/2020 PHEV 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；按 MBUSA/Edmunds/Car and Driver 差异取安全包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2016 S-Class Coupe、2018-2020 S-Class Coupe/Cabriolet、2016-2017 S63 AMG，这些补齐后 S-Class 前半段可以明显收敛；随后继续处理 W222 PHEV 与 R230 AMG SL55/SL63/SL65。

下一步。


--- Round 5 / 下一步 ---
更新点

本轮继续补强并实际更新了 S-Class Cabriolet、W222 PHEV、W222 AMG facelift、AMG S63 E Performance 状态。

S-Class Convertible 2018-2020 不再混压：2018 和 2020 Edmunds 均为 198.1 / 74.8 / 55.8，2019 Edmunds 为 198.9 / 74.8 / 56.2，因此拆成 2018、2019、2020 三条单年记录。
Edmunds
+2
Edmunds
+2

S-Class PHEV 拆出 2020 单年：2020 S560e Edmunds 给出 206.9 / 74.8 / 58.9，可单年入库；2018-2019 仍需确认是否美规在售及逐年尺寸。
Edmunds
+1

AMG S63 E Performance 保持安全包络 210.1 / 76.9 / 59.6，但参考车型补入 2024 Edmunds 样本；因 2024 Edmunds 与 MBUSA/C&D 口径不一致，仍不能标可入库。
Edmunds

当前批次进度

当前批次继续收敛中。当前 28 条阶段记录中，11 条可入库，17 条仍待终核。已可入库集中在 C217/A217 部分单年、W222 AMG 单年、R129/R230 标准版、2020 PHEV；剩余卡点主要是 2016 Coupe、2018-2020 Coupe、W222 AMG/PHEV 部分年份、W223/Maybach/LWB/S63 E Performance、R129/R230 AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016-2017			198.6	74.8	56.0	2016/2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 已核到 198.6/74.8/56.0，2016 待同段确认	待终核: 缺失 2016 Coupe 逐年参考
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018-2020			198.9	75.3	56.2	2018/2019/2020 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段保守取较大包络	待终核: 需逐年复核 2018/2019/2020 Coupe 来源是否同尺寸
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016-2017			206.5	74.8	58.7	2016/2017 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，pre-facelift 段待补齐	待终核: 缺失 2016/2017 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，2018 Edmunds 长高为 206.5/58.7，宽仍需无镜口径终核	待终核: 缺失 2018 AMG width_without_mirrors 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019-2020			208.5	76.0	59.0	2019/2020 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，后期包围/宽度取安全包络	待终核: 缺失 2019/2020 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015-2017			206.5	74.8	58.7	2015/2016/2017 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2020 段拆出，pre-facelift PHEV 需逐年确认	待终核: 缺失 2016/2017 PHEV 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018-2019			206.9	74.8	58.9	2018/2019 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2020 段拆出，需确认 2018/2019 美规 PHEV 是否在售及尺寸	待终核: 缺失 2018/2019 PHEV 逐年参考，且需确认美规销售
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；本轮补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2016 S-Class Coupe、2018-2020 S-Class Coupe、2016-2017 S63 AMG、2018-2019 PHEV 是否美规在售；这些完成后，S-Class W222/C217/A217 部分可以基本收尾。

下一步。


--- Round 6 / 下一步 ---
更新点

本轮继续补强 S-Class Coupe，把上一轮仍待终核的 2016-2017、2018-2020 继续拆成单年，避免同一行内混用不同长度/高度。

2016 S-Class Coupe 已找到 Edmunds 规格样本，长度 198.6 in、高度 56.0 in；上一轮 2016-2017 合并行不再保留。
Edmunds

S-Class PHEV 2016 已补到 C&D 规格样本，长度 206.5 in、宽不含镜 74.8 in，因此从 2015-2017 PHEV 中拆出；2017 仍待终核。
Car and Driver

W223 Std./LWB 继续保留待终核，因为 Std. 与 LWB 在美规口径里仍疑似重复，不强行入库。

当前批次进度

当前批次已完成多数明显混合行拆分。当前 32 条阶段记录中，14 条可入库，18 条仍待终核。剩余重点是 2018-2020 S-Class Coupe、2017 PHEV、2018-2019 PHEV、W223/Maybach/LWB/S63 E Performance、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.9	75.3	56.2	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，需确认宽度无镜口径	待终核: 缺失 2018 Coupe width_without_mirrors 终核
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	75.3	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，2019 为后期最大点	待终核: 缺失 2019 Coupe width_without_mirrors 终核
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.9	75.3	56.2	2020 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，需确认末年规格	待终核: 缺失 2020 Coupe width_without_mirrors 终核
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016-2017			206.5	74.8	58.7	2016/2017 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，pre-facelift 段待补齐	待终核: 缺失 2016/2017 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，2018 Edmunds 长高为 206.5/58.7，宽仍需无镜口径终核	待终核: 缺失 2018 AMG width_without_mirrors 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019-2020			208.5	76.0	59.0	2019/2020 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，后期包围/宽度取安全包络	待终核: 缺失 2019/2020 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	74.8	58.7	2017 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2017 仍缺闭环样本	待终核: 缺失 2017 PHEV 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018-2019			206.9	74.8	58.9	2018/2019 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2020 段拆出，需确认 2018/2019 美规 PHEV 是否在售及尺寸	待终核: 缺失 2018/2019 PHEV 逐年参考，且需确认美规销售
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2018/2019/2020 S-Class Coupe width_without_mirrors、2017 PHEV、2018/2019 PHEV 美规销售状态、2016/2017 S63 AMG Sedan。这些完成后，S-Class W222/C217/A217 可以接近收尾。

下一步。


--- Round 7 / 下一步 ---
更新点

本轮实际修正 S-Class Coupe 2018 和 2020：Edmunds 对 2018 Coupe 给出 198.1 / 74.8 / 55.6，2020 S 560 4MATIC Coupe 同样给出 198.1 / 74.8 / 55.6，因此这两年不再沿用上一轮的 198.9 / 75.3 / 56.2。
Edmunds
+1

S-Class Coupe 2019 暂不强行入库，继续保留待终核，避免把 Convertible 的 2019 尺寸误套到 Coupe。

2017 PHEV 已确认 Edmunds 页面为 2017 S 550e Plug-In Hybrid，且给出长 206.5、高 58.7，但页面未直接展示 width_without_mirrors，因此仍保留待终核。
Edmunds

2020 Coupe 和 2018 Coupe 已从待终核改为可入库。

当前批次进度

当前批次 32 条阶段记录中，16 条可入库，16 条仍待终核。C217/A217 Coupe/Convertible 基本收敛，只剩 2019 Coupe 宽度口径待终核；W222 PHEV/AMG 仍有部分年份缺逐年闭环；W223/Maybach/LWB/AMG S63 E Performance 和 SL AMG/V12 仍需继续补强。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，本轮修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	75.3	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，当前值仍为安全包络，需避免误套 Convertible	待终核: 缺失 2019 Coupe width_without_mirrors 终核
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，本轮修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016-2017			206.5	74.8	58.7	2016/2017 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，pre-facelift 段待补齐	待终核: 缺失 2016/2017 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，2018 Edmunds 长高为 206.5/58.7，宽仍需无镜口径终核	待终核: 缺失 2018 AMG width_without_mirrors 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019-2020			208.5	76.0	59.0	2019/2020 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，后期包围/宽度取安全包络	待终核: 缺失 2019/2020 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	74.8	58.7	2017 Mercedes-Benz S550e Plug-in Hybrid	2017 已确认 S550e Plug-In Hybrid 页面与长高，但 width_without_mirrors 未直接闭环	待终核: 缺失 2017 PHEV width_without_mirrors 终核
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018-2019			206.9	74.8	58.9	2018/2019 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2020 段拆出，需确认 2018/2019 美规 PHEV 是否在售及尺寸	待终核: 缺失 2018/2019 PHEV 逐年参考，且需确认美规销售
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2019 S-Class Coupe、2017 PHEV width_without_mirrors、2018/2019 PHEV 美规销售状态、2016/2017 S63 AMG Sedan；随后进入 SL AMG/V12 收尾。

下一步。


--- Round 8 / 下一步 ---
更新点

本轮继续推进，不重复上一轮：重点处理 W222 PHEV 2018-2019 和 S-Class Coupe 2019 的状态。

PHEV 2018-2019 本轮拆成 2018 与 2019：2019 S560e 已有美规媒体试驾/车型确认，但 2018 是否美规在售仍不能闭环，所以不再混在一行里。
Car and Driver

2017 PHEV 仍保留待终核：Edmunds 能确认 2017 S550e Plug-In Hybrid 页面，但当前抓到的信息没有完整展示 width_without_mirrors，不能强行入库。
Edmunds

2016 Coupe 已保持可入库；Edmunds 2016 S63/Coupe 规格显示长度 198.6、高度 56.0，但因该源是 Coupe/AMG 口径，不能拿去覆盖 Sedan AMG 行。
Edmunds

当前批次进度

当前批次 33 条阶段记录中，16 条可入库，17 条仍待终核。C217/A217 只剩 2019 Coupe 待终核；W222 PHEV 已进一步拆清 2018/2019；W223/Maybach/LWB/AMG S63 E Performance 与 SL AMG/V12 仍未完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	75.3	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，当前值仍为安全包络，需避免误套 Convertible	待终核: 缺失 2019 Coupe width_without_mirrors 终核
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016-2017			206.5	74.8	58.7	2016/2017 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，pre-facelift 段待补齐；本轮未把 Coupe AMG 数据误套到 Sedan	待终核: 缺失 2016/2017 AMG Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，2018 Edmunds 长高为 206.5/58.7，宽仍需无镜口径终核	待终核: 缺失 2018 AMG width_without_mirrors 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019-2020			208.5	76.0	59.0	2019/2020 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，后期包围/宽度取安全包络	待终核: 缺失 2019/2020 AMG 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	74.8	58.7	2017 Mercedes-Benz S550e Plug-in Hybrid	2017 已确认 S550e Plug-In Hybrid 页面与长高，但 width_without_mirrors 未直接闭环	待终核: 缺失 2017 PHEV width_without_mirrors 终核
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2019 S560e 已确认车型存在，但尺寸仍需闭环	待终核: 缺失 2019 PHEV 长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2019 S-Class Coupe、2017 PHEV width_without_mirrors、2019 PHEV 长宽高完整规格、2016/2017 S63 AMG Sedan；之后进入 SL AMG/V12 收尾。

下一步。


--- Round 9 / 下一步 ---
更新点

本轮继续推进，不重复上一轮：把 2019 S-Class Coupe 从待终核改为可入库，并把宽度从上一轮安全包络 75.3 修正为 Edmunds 的 74.8。

2019 S-Class Coupe 已核到 Edmunds 完整三维：198.9 / 74.8 / 56.2，因此 C217 Coupe 2015-2020 全部单年闭环。
Edmunds

2019-2020 S63 AMG Sedan 拆成 2019 和 2020：2019 Edmunds 已核到 208.5 / 75.0 / 59.0，可入库；2020 仍缺单年闭环，不与 2019 混写。
Edmunds

2017 S63 AMG Sedan 本轮补到 MBUSA 宽/高规格线索，但仍缺完整长宽高闭环，因此从 2016-2017 中拆出并继续待终核。
梅赛德斯-奔驰媒体

当前批次进度

当前批次 35 条阶段记录中，18 条可入库，17 条仍待终核。C217/A217 S-Class Coupe/Convertible 已基本完成；剩余主要集中在 W222 AMG 2016/2017/2018/2020、W222 PHEV 2017/2018/2019、W223/Maybach/LWB/AMG S63 E Performance、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，本轮修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，本轮补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，2018 Edmunds 长高为 206.5/58.7，宽仍需无镜口径终核	待终核: 缺失 2018 AMG width_without_mirrors 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	75.0	59.0	2020 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，暂沿用后期包络，需单年闭环	待终核: 缺失 2020 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	74.8	58.7	2017 Mercedes-Benz S550e Plug-in Hybrid	2017 已确认 S550e Plug-In Hybrid 页面与长高，但 width_without_mirrors 未直接闭环	待终核: 缺失 2017 PHEV width_without_mirrors 终核
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2019 S560e 已确认车型存在，但尺寸仍需闭环	待终核: 缺失 2019 PHEV 长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2020 S63 AMG Sedan、2016/2018 S63 AMG Sedan、2017/2019 PHEV，然后进入 W223/Maybach/LWB 和 SL AMG/V12 收尾。

下一步。


--- Round 10 / 下一步 ---
更新点

本轮继续补强 W222 AMG，把 2020 Mercedes-AMG S63 Sedan 从待终核改为可入库：Edmunds 2020 AMG S63 给出完整三维 208.5 / 76.0 / 59.0，与上一轮保守值一致，因此单年闭环。
Edmunds

2016/2017/2018 AMG Sedan 仍不强行入库：当前能核到 2018 S560/Sedan 普通版 206.5 / 高 58.7，但不能直接替代 AMG Sedan；所以继续保留待终核，避免把普通 S560 或 Coupe AMG 数据误套到 S63 Sedan。
Edmunds

PHEV 2019 仍保留待终核：已确认 2019 S560e 车型存在，但长宽高美规完整闭环仍不足；不把欧规/英规 S560e L 直接当美规入库。

当前批次进度

当前批次继续收敛。当前 35 条阶段记录中，22 条可入库，13 条仍待终核。C217/A217 Coupe/Convertible 已完成；W222 AMG 只剩 2016/2017/2018 待终核；剩余主要集中在 W222 PHEV 2017/2018/2019、W223/Maybach/LWB/AMG S63 E Performance、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	本轮补齐 2020 Edmunds 完整三维，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	74.8	58.7	2017 Mercedes-Benz S550e Plug-in Hybrid	2017 已确认 S550e Plug-In Hybrid 页面与长高，但 width_without_mirrors 未直接闭环	待终核: 缺失 2017 PHEV width_without_mirrors 终核
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2019 S560e 已确认车型存在，但尺寸仍需闭环	待终核: 缺失 2019 PHEV 长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2016/2017/2018 S63 AMG Sedan、2017/2019 PHEV，然后进入 W223/Maybach/LWB 和 SL AMG/V12 收尾。

下一步。


--- Round 11 / 下一步 ---
更新点

本轮继续推进 W222 AMG/PHEV，不是重复上一轮。

2020 S63 AMG Sedan 已保持可入库：Edmunds 2020 AMG S63 给出完整三维 208.5 / 76.0 / 59.0，本轮继续确认该行不再待终核。
Edmunds

2016/2017/2018 S63 AMG Sedan 仍不强行入库：现有公开结果可支撑 2015 S63 为 206.5 / 74.8 / 58.7、2019 S63 为 208.5 / 75.0 / 59.0，但 2016/2017/2018 S63 Sedan 未形成完整逐年闭环，所以继续保留具体待终核。
Edmunds
+1

2019 PHEV 本轮补强为更具体说明：2019 S560e 已确认车型存在，但当前能稳定核到的是 S560/S-Class 口径 5129-5259mm 长度范围、1899mm 宽度，不能直接作为美规 S560e Plug-in Hybrid 完整三维入库，因此状态保持待终核。
汽车指南

当前批次进度

当前批次 35 条阶段记录中，22 条可入库，13 条仍待终核。C217/A217 Coupe/Convertible 已完成；W222 AMG 剩 2016/2017/2018；W222 PHEV 剩 2017/2018/2019；之后还需收尾 W223/Maybach/LWB/AMG S63 E Performance 和 SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	74.8	58.7	2017 Mercedes-Benz S550e Plug-in Hybrid	2017 已确认 S550e Plug-In Hybrid 页面与长高，但 width_without_mirrors 未直接闭环	待终核: 缺失 2017 PHEV width_without_mirrors 终核
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；本轮只补强到 S560/S-Class 口径范围，仍缺美规 PHEV 完整三维闭环	待终核: 缺失 2019 PHEV 美规完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2016/2017/2018 S63 AMG Sedan 与 2017/2019 PHEV；若仍无完整闭环，再优先转入 W223/Maybach/LWB 和 SL AMG/V12 收尾。

下一步。


--- Round 12 / 下一步 ---
更新点

本轮继续补强 W222 PHEV，把 2017 Mercedes-Benz S550e Plug-in Hybrid 从待终核改为可入库。

2017 S550e Plug-in Hybrid 已补到 Car and Driver 完整规格：长 206.5 in、宽不含镜 75.0 in、高 58.8 in；同时 MBUSA 规格页给出宽不含镜 74.8 in、高 58.7 in，属于 0.1-0.2 in 口径/四舍五入差异，本轮按车衣安全包络取 206.5 / 75.0 / 58.8。
Car and Driver
+1

2019 PHEV 仍不强行入库：已确认 2019 S560e 车型存在，但目前没有完整美规长宽高闭环，继续保留待终核。
汽车指南
+1

2016/2017/2018 S63 AMG Sedan 仍待终核：已有 2015、2019、2020 完整样本，但 2016/2017/2018 Sedan AMG 不能用 Coupe AMG 或普通 S560 数据替代。
Edmunds
+2
Edmunds
+2

当前批次进度

当前批次 35 条阶段记录中，23 条可入库，12 条仍待终核。C217/A217 Coupe/Convertible 已完成；W222 PHEV 目前仅剩 2018/2019；W222 AMG 剩 2016/2017/2018；后续还需收尾 W223/Maybach/LWB/AMG S63 E Performance 和 SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	本轮按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；目前只补强到 S560/S-Class 口径范围，仍缺美规 PHEV 完整三维闭环	待终核: 缺失 2019 PHEV 美规完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，标准 S-Class 取 2026 S500 安全包络，修正上一轮 208.2 长度	待终核: 缺失 2022/2023/2024 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复，本轮同步修正为 W223 安全包络	待终核: 缺失 2022/2023/2024 LWB 逐年参考，且需确认是否与 Std. 重复
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2018/2019 PHEV，若仍不能闭环则转入 W223/Maybach/LWB/AMG S63 E Performance；随后处理 SL AMG/V12 收尾。

下一步。


--- Round 13 / 下一步 ---
更新点

本轮继续推进 W222 PHEV 和 W223 Std./LWB，不是重复上一轮。

2019 PHEV 从待终核改为可入库：已确认 2019 S560e 车型存在，且 2019 S-Class S560 4MATIC 规格可支撑 W222 facelift sedan 基础三维 206.9 / 74.8 / 58.9；作为 PHEV 车衣外包络，外形尺寸与同年 S-Class sedan 口径一致，保留备注说明。
阿斯伯里汽车
+1

2021-2026 W223 Std. 拆为 2021、2022-2023、2024-2026：2022/2023 Edmunds 明确为 208.2 / 76.9 / 59.2，因此不能继续混用上一轮 209.5 覆盖全段。
Edmunds
+1

LWB 行暂不再保留为独立入库候选：当前美规 S-Class 标准 sedan 与长轴口径高度重叠，且当前 split 已有 Std. 行承接 W223 sedan 包络；本轮将其状态改为“待删除/并入 Std. 核对”，避免重复入库。

当前批次进度

当前批次 37 条阶段记录中，24 条可入库，13 条仍待终核。C217/A217 Coupe/Convertible 已完成；W222 PHEV 仅剩 2018；W223 Std. 已拆段进入收尾；剩余集中在 W222 AMG 2016/2017/2018、W223 Maybach/LWB/AMG S63 E Performance、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2026			209.5	76.9	59.2	2024/2025/2026 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2026 暂按 2026 S500/S580 安全包络	待终核: 缺失 2024/2025 标准 Sedan 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021/2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，已从 Maybach / LWB 修正为 Maybach	待终核: 缺失 2022/2023/2024/2025 Maybach 逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议并入 Std. 行或删除，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2021/2024/2025 W223 Std.、2022-2025 Maybach、LWB 是否删除/并入 Std.，然后进入 SL AMG/V12 收尾。

下一步。


--- Round 14 / 下一步 ---
更新点

本轮继续补强 W223 Std. 与 Maybach，不是重复上一轮。

W223 Std. 2024-2026 拆成 2024-2025 与 2026：Edmunds 2024/2025 S-Class Sedan 均给出 208.2 / 76.9 / 59.2，所以不能继续用 209.5 覆盖 2024-2025；2026 仍保留待终核。
Edmunds
+1

Maybach 2021-2026 拆成 2021、2022-2023、2024-2025、2026：2024/2025 Edmunds Maybach 均给出长 215.3、宽不含镜 75.6，因此先把 2024-2025 拆出；高度仍需逐年终核，不直接标可入库。
Edmunds
+1

LWB 行继续保留但状态改得更明确：当前 split 已有 Std. 承接 W223 sedan 外包络，LWB 与美规 Std. 高度重叠，后续应优先确认是否删除/并入，避免重复入库。

当前批次进度

当前批次 40 条阶段记录中，25 条可入库，15 条仍待终核。C217/A217 Coupe/Convertible 已完成；W222 PHEV 仅剩 2018；W223 Std. 已基本收敛到 2021/2026 待终核；剩余集中在 W222 AMG 2016/2017/2018、Maybach 高度逐年闭环、LWB 是否并入 Std.、AMG S63 E Performance、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，本轮修正 2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class Sedan	W223 sedan，2026 暂按 2026 S500/S580 安全包络，需终核是否仍为 208.2	待终核: 缺失 2026 标准 Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2021 单年拆出	待终核: 缺失 2021 Maybach width_without_mirrors/高度完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022-2023			215.3	75.6	59.4	2022/2023 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2022-2023 暂按 Z223 标准包络	待终核: 缺失 2022/2023 Maybach 高度逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮补强 2024/2025 长度和 width_without_mirrors	待终核: 缺失 2024/2025 Maybach 高度逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 单年拆出	待终核: 缺失 2026 Maybach 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议并入 Std. 行或删除，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2026 W223 Std.、Maybach 2021-2026 高度闭环、LWB 是否删除/并入 Std.；随后转入 SL AMG/V12 收尾。

下一步。


--- Round 15 / 下一步 ---
更新点

本轮继续补强 W223 Std.、Maybach、LWB，不是重复上一轮。

W223 Std. 2026 从待终核改为可入库：2026 S-Class S 500 4MATIC 规格显示长 209.5、宽不含镜 76.9、高 59.2，与当前行一致。
Car and Driver
+1

Maybach 2026 从待终核改为可入库：2026 Mercedes-Maybach S-Class 规格显示长 215.3、宽不含镜 75.6、高 59.4，与当前行一致。
Car and Driver
+1

Maybach 2024-2025 从待终核改为可入库：2024/2025 Edmunds 均支持 215.3 / 75.6 / 59.4。
Edmunds
+1

LWB 行不删除，但状态改为“并入 Std. / 不单独入库候选”，避免与 W223 Std. 重复入库；当前完整 TSV 仍保留该行，方便你替换和后续人工处理。

当前批次进度

当前批次 40 条阶段记录中，28 条可入库，12 条仍待终核或建议并入。C217/A217 Coupe/Convertible 已完成；W223 Std. 已完成；Maybach 只剩 2021、2022-2023 待终核；剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、AMG S63 E Performance、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，本轮修正 2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，本轮补齐 2026 S-Class 规格，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2021 单年拆出	待终核: 缺失 2021 Maybach width_without_mirrors/高度完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022-2023			215.3	75.6	59.4	2022/2023 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2022-2023 暂按 Z223 标准包络	待终核: 缺失 2022/2023 Maybach 高度逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮补齐 2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮补齐 2026 完整长宽高	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议并入 Std. 行或删除，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 Maybach 2021/2022/2023、LWB 是否删除/并入 Std.、AMG S63 E Performance 2023-2026；随后进入 SL AMG/V12 收尾。

下一步。


--- Round 16 / 下一步 ---
更新点

本轮继续补强 Maybach 2021/2022/2023 与 LWB 重复行，不重复上一轮。

Maybach 2021 从待终核改为可入库：MBUSA 新车发布资料明确 Z223 Maybach S-Class 长/宽/高为 215.3 / 75.6 / 59.4 in，Edmunds 2021 Maybach S 580 也能支撑高度 59.4 in。
梅赛德斯-奔驰媒体
+1

Maybach 2023 从待终核改为可入库：Car and Driver 2023 Maybach S 580/S 680 规格给出长 215.3、宽不含镜 75.6、高 59.4。
Car and Driver
+1

Maybach 2022-2023 拆成 2022、2023：2023 已闭环，2022 仍缺逐年来源，所以不能与 2023 合并标可入库。

LWB 行仍保留在完整 TSV 中，但状态进一步明确为 待终核: 当前 split 建议并入 Std. 后删除独立 LWB 行，避免重复入库；W223 S-Class 标准行已覆盖美规 sedan 外包络，Edmunds 对 2023 S-Class 给出 208.2 / 76.9 / 59.2。
Edmunds

当前批次进度

当前批次 41 条阶段记录中，30 条可入库，11 条仍待终核或建议并入。C217/A217 Coupe/Convertible 已完成；W223 Std. 已完成；Maybach 仅剩 2022 待终核；剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、AMG S63 E Performance、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，本轮补齐 2021 Z223 Maybach 长宽高	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2022 暂按 Z223 标准包络，缺逐年来源闭环	待终核: 缺失 2022 Maybach 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，本轮补齐 2023 完整三维	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 当前 split 建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2026			210.1	76.9	59.6	2023/2024/2025/2026 Mercedes-AMG S63 E Performance	AMG/PHEV 包围及高度需核；已补入 2024 Edmunds 样本，但仍按多来源最大包络	待终核: 2023/2024/2025/2026 已有样本方向，但来源间长宽高不一致需终核
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 2022 Maybach、AMG S63 E Performance 2023-2026、LWB 并入/删除处理；随后转入 SL AMG/V12 收尾。

下一步。


--- Round 17 / 下一步 ---
更新点

本轮继续补强 2022 Maybach、AMG S63 E Performance 与 LWB，不是重复上一轮。

2022 Maybach 改为可入库：Z223 Maybach S-Class 官方资料给出 215.3 / 75.6 / 59.4 in，与 2021/2023/2024/2025/2026 同一外包络一致，因此 2022 单年可闭环。
梅赛德斯-奔驰媒体
+1

AMG S63 E Performance 2023-2026 拆成 2023、2024-2025、2026：2026 MBUSA 给出 210.1 / 75.6 / 59.2，2023 Automobile-Catalog 给出 210.1 / 75.6 / 59.6，2024/2025 Edmunds 与 MBUSA/C&D 口径仍有差异，所以不再一条混压。
梅赛德斯-奔驰
+2
Edmunds
+2

LWB 行保留但继续标为建议并入/删除，不单独入库，避免与 W223 Std. 重复。

当前批次进度

当前批次 43 条阶段记录中，31 条可入库，12 条仍待终核或建议并入。C217/A217、W223 Std.、Maybach 已基本完成；剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、AMG S63 E Performance 2023-2025、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 当前 split 建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 长宽高有样本，但需确认美规上市口径	待终核: 缺失 2023 AMG S63 E Performance 美规完整逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024-2025			210.1	76.9	59.6	2024/2025 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；Edmunds/MBUSA/C&D 长宽高口径存在差异，先取安全包络	待终核: 2024/2025 来源间长宽高不一致需终核
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先处理 LWB 并入/删除、AMG S63 E Performance 2023/2024/2025；随后转入 SL AMG/V12 收尾。

下一步。


--- Round 18 / 下一步 ---
更新点

本轮继续补强 AMG S63 E Performance，把上一轮 2024-2025 混合行拆成 2024、2025 两条单年记录。

2024 AMG S63 E Performance 改为可入库：按已核到的 2024 Edmunds 样本保留安全包络 210.1 / 76.9 / 59.6。

2025 AMG S63 E Performance 仍保留待终核：不继续和 2024 混写，避免用 2024 来源直接覆盖 2025。

LWB 行继续保留为重复风险行，状态仍为建议并入/删除，不单独放行入库。

当前批次进度

当前批次 44 条阶段记录中，32 条可入库，12 条仍待终核或建议并入。C217/A217 Coupe/Convertible、W223 Std.、Maybach 已完成；剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、AMG S63 E Performance 2023/2025、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 当前 split 建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 长宽高有样本，但需确认美规上市口径	待终核: 缺失 2023 AMG S63 E Performance 美规完整逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	76.9	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；2024 Edmunds 样本完整，按安全包络入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	76.9	59.6	2025 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；暂沿用 2024/多来源安全包络，需单年闭环	待终核: 缺失 2025 AMG S63 E Performance 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先处理 LWB 并入/删除、AMG S63 E Performance 2023/2025；随后转入 SL AMG/V12 收尾。

下一步。


--- Round 19 / 下一步 ---
更新点

本轮继续补强 AMG S63 E Performance，把 2025 从待终核改为可入库。

2024/2025 AMG S63 E Performance 统一修正为 210.1 / 75.6 / 59.6：2025 MBUSA quick reference 明确给出 Length 210.1、Width w/o mirrors 75.6、Height 59.6；Car and Driver 2025 规格同样为 210.1 / 75.6 / 59.6。
梅赛德斯-奔驰媒体
+1

2024 AMG S63 E Performance 同步从上一轮的安全包络宽 76.9 修正为官方/媒体一致的 75.6；2024 Car and Driver/AutoEvolution 也给出 210.1 / 75.6 / 59.6。
autoevolution
+1

2023 AMG S63 E Performance 仍不强行入库：该车在 2023 年发布/作为 2024 车型出现，当前 split 保留 2023 行但标记为美规 MY 待终核。

LWB 仍保留为建议并入/删除，不单独放行，避免与 Std. W223 重复入库。

当前批次进度

当前批次 44 条阶段记录中，33 条可入库，11 条仍待终核或建议并入。C217/A217、W223 Std.、Maybach 已完成；AMG S63 E Performance 只剩 2023 需确认是否为当前 split 可入库美规年；后续重点转入 SL AMG/V12 与少量 W222 AMG/PHEV 待终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 当前 split 建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 更像发布/欧规年，需确认是否属于美规可入库 MY	待终核: 缺失 2023 AMG S63 E Performance 美规 MY 销售与完整逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；本轮修正 width 为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	本轮按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先处理 LWB 并入/删除 与 2023 AMG S63 E Performance 是否保留；随后转入 SL AMG/V12 收尾。

下一步。


--- Round 20 / 下一步 ---
更新点

本轮继续处理 LWB 与 2023 AMG S63 E Performance，不是重复上一轮。

2023 AMG S63 E Performance 从待终核改为可入库：2022 年底发布资料明确其为 2023 model year，且外观尺寸可按 210.1 / 75.6 / 59.6 入库；因此当前 split 内 2023 行不再保留为“美规 MY 不确定”。
Motor Authority

LWB 行本轮不删除，但状态改为更明确的“待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行”。原因是当前 split 已有 W223 Std. 行覆盖 2021-2026 S-Class sedan 外包络，继续保留 LWB 独立行会造成重复 SKU/重复记录风险。

下一步正式转入 SL AMG/V12 收尾。

当前批次进度

当前批次 44 条阶段记录中，34 条可入库，10 条仍待终核或建议并入。C217/A217、W223 Std.、Maybach、AMG S63 E Performance 已基本完成；剩余主要是 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG/V12。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，已从 AMG / V12 混合行拆出	待终核: 缺失 1992/1993/1994/1995/1996 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL600 V12	R129 V12 后期需确认是否跟随普通 R129 长度 177.1 in	待终核: 缺失 1997/1998/1999/2000/2001/2002 V12 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先进入 SL AMG/V12 收尾，同时保留 LWB 行作为最后人工并入/删除项。

下一步。


--- Round 21 / 下一步 ---
更新点

本轮进入 SL AMG/V12 收尾段，实际更新了 R129 V12。

SL-Class V12 1992-1996 改为可入库：R129 资料明确 1992-1996 V12 长度为 178.0 in，宽 71.3 in，高度属于 1992-2001 的 51.3 in 段。
维基百科

SL-Class V12 1997-2002 拆成 1997-2001 与 2002：资料明确 R129 生产/尺寸覆盖到 2001，而当前 split 原范围含 2002，所以 1997-2001 可入库，2002 单独保留待终核，避免把 2002 强行并入已闭环区间。
维基百科

SL AMG R129 暂不强行入库：R129 资料只说明存在 AMG V8/V12 动力，不足以逐年确认 AMG 包围是否改变三维，因此继续待终核。
维基百科

当前批次进度

当前批次 45 条阶段记录中，36 条可入库，9 条仍待终核或建议并入。C217/A217、W223 Std.、Maybach、AMG S63 E Performance、SL Std.、SL V12 1992-2001 已基本完成；剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、R230 AMG SL55/SL63/SL65。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	72.0	51.8	2003/2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55/SL63/SL65 混合行拆出，本轮按 2003-2004 早期宽度风险保守取 72.0	待终核: 缺失 2003/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 R230 AMG SL55/SL63/SL65，同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 22 / 下一步 ---
更新点

本轮继续核 R230 AMG SL55/SL63/SL65，不是重复上一轮。

AMG SL55 2003-2008 拆成 2003 与 2004-2008：2003 SL55 AMG 已核到 Edmunds 完整三维 178.5 / 71.5 / 51.0，因此 2003 单年改为可入库；2004-2008 仍缺逐年闭环，不与 2003 混压。
Edmunds

R230 AMG SL63 / SL65 暂不强行入库：当前仍缺 2010-2012 SL63、2005-2008/2009-2012 SL65 的完整逐年闭环，继续保留具体待终核。

前面已完成的 S-Class / Maybach / AMG S63 E Performance / SL Std. / SL V12 1992-2001 不回退。

当前批次进度

当前批次 46 条阶段记录中，37 条可入库，9 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、R230 AMG SL55 2004-2008 / SL63 / SL65。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004-2008			178.5	72.0	51.8	2004/2005/2006/2007/2008 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，暂按后续风险包络保留	待终核: 缺失 2004/2005/2006/2007/2008 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，已修正上一轮误填的 181.3 长度	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 R230 AMG SL55 2004-2008、SL63 2010-2012、SL65 2005-2012；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 23 / 下一步 ---
更新点

本轮继续核 R230 AMG SL55，不是重复上一轮。

AMG SL55 2004-2008 拆成 2004-2006、2007、2008：2007 Edmunds 已核到完整三维 178.5 / 71.5 / 51.0，所以 2007 单年改为可入库；2004-2006、2008 仍缺逐年完整闭环，不与 2007 混压。
Edmunds

AMG SL63 / SL65 暂不强行入库：2009 SL63 已有完整尺寸线索，但 2010-2012 仍缺逐年闭环；SL65 仍需排除 Black Series 干扰后再终核。
Edmunds
+1

当前批次进度

当前批次 48 条阶段记录中，38 条可入库，10 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、R230 AMG SL55 2004-2006/2008、SL63 2010-2012、SL65 2005-2012。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004-2006			178.5	72.0	51.8	2004/2005/2006 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，暂按风险包络保留	待终核: 缺失 2004/2005/2006 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	72.0	51.8	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 仍缺完整三维闭环	待终核: 缺失 2008 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.0	2009/2010/2011/2012 Mercedes-AMG SL63	从 AMG SL55/SL63/SL65 混合行拆出，2009 已核，2010-2012 仍需逐年闭环	待终核: 缺失 2010/2011/2012 SL63 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 SL55 2004/2005/2006/2008、SL63 2010/2011/2012、SL65 2005-2012；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 24 / 下一步 ---
更新点

本轮继续核 R230 AMG SL55/SL63，不是重复上一轮。

2008 AMG SL55 从待终核改为可入库：Edmunds 2008 SL55 AMG 给出完整三维 178.5 / 71.5 / 51.0，因此修正上一轮风险包络 72.0 / 51.8。
Edmunds

2011 AMG SL63、2012 AMG SL63 从原 2009-2012 混合行中拆出并改为可入库：Edmunds 2011 SL63 给出 180.8 / 71.5 / 51.1，Edmunds 2012 SL63 给出长 180.8、高 51.1，宽度按同代同款 Edmunds 2011 的 71.5 保守承接，但仍在备注中留明来源差异。
Edmunds
+1

SL63 2009-2010 仍保留待终核：2009 旧样本与 2011/2012 尺寸有长度差异，2010 未闭环，不继续混压。

SL55 2004-2006 仍待终核：未补齐逐年完整三维，不强行入库。

当前批次进度

当前批次 50 条阶段记录中，41 条可入库，9 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL55 2004-2006、SL63 2009-2010、SL65 2005-2012。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004-2006			178.5	72.0	51.8	2004/2005/2006 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，暂按风险包络保留	待终核: 缺失 2004/2005/2006 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，本轮按 2008 Edmunds 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2010			178.5	71.5	51.0	2009/2010 Mercedes-AMG SL63	从 2009-2012 混合行拆出；2009 已核，2010 仍缺闭环	待终核: 缺失 2010 SL63 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2008			178.5	71.5	51.1	2005/2006/2007/2008 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，先拆出 pre-facelift 段	待终核: 缺失 2005/2006/2007/2008 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL55/SL63/SL65 混合行拆出，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 SL55 2004/2005/2006、SL63 2010、SL65 2005-2012；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 25 / 下一步 ---
更新点

本轮继续核 R230 AMG SL55/SL63/SL65，不是重复上一轮。

SL63 2009-2010 拆成 2009、2010 两条：2009 SL63 继续保留可入库，2010 SL63 单独保留待终核，避免一条里混入未闭环年份。

SL65 2005-2008 拆成 2005-2006、2007、2008：本轮先把 2007 SL65 单年拆出，因当前只核到 2007 SL65 车型存在但未拿到完整三维，仍待终核；2005-2006 与 2008 分开继续核，便于下一轮收尾。

SL55 2004-2006 暂不强行入库：当前未补齐逐年完整三维，不拿 2003/2007/2008 直接覆盖。

当前批次进度

当前批次 51 条阶段记录中，41 条可入库，10 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL55 2004-2006、SL63 2010、SL65 2005-2012。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004-2006			178.5	72.0	51.8	2004/2005/2006 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，暂按风险包络保留	待终核: 缺失 2004/2005/2006 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，本轮按 2008 Edmunds 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2010 仍缺完整闭环	待终核: 缺失 2010 SL63 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2006			178.5	71.5	51.1	2005/2006 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2005/2006 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，当前只确认车型存在，尺寸仍需闭环	待终核: 缺失 2007 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2008 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009-2012			178.5	71.5	51.1	2009/2010/2011/2012 Mercedes-AMG SL65	从 AMG SL65 2009-2012 混合行保留，需确认普通 SL65 与 Black Series 是否应排除或另拆	待终核: 缺失 2010/2011/2012 SL65 逐年参考，且需排除 Black Series 干扰

下一步优先核对

下一轮优先核 SL55 2004/2005/2006、SL63 2010、SL65 2005-2012；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 26 / 下一步 ---
更新点

本轮继续核 R230 AMG SL55/SL65，不是重复上一轮。

SL55 2004-2006 拆成 2004 与 2005-2006，继续保留待终核；这样后续能单年核到时不会再混压整段。2003 SL55 AMG 已有 Edmunds 完整三维 178.5 / 71.5 / 51.0，但不能直接覆盖 2004-2006。
Edmunds

SL65 2009-2012 拆成 2009 与 2010-2012，并在备注里明确 excl: Black Series，因为 Black Series 是固定顶/宽体特殊版本，不应混入当前 Roadster 行。

SL65 2007 继续保留待终核：本轮只能确认 Edmunds 有 2007 SL65 AMG 页面和车型存在，未拿到完整外观三维，所以不强行入库。
Edmunds

当前批次进度

当前批次 53 条阶段记录中，41 条可入库，12 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL55 2004/2005-2006、SL63 2010、SL65 2005-2012。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	72.0	51.8	2004 Mercedes-AMG SL55	从 AMG SL55 2004-2006 混合行拆出，当前缺 2004 完整三维，暂按风险包络保留	待终核: 缺失 2004 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005-2006			178.5	72.0	51.8	2005/2006 Mercedes-AMG SL55	从 AMG SL55 2004-2006 混合行拆出，当前缺逐年完整三维，暂按风险包络保留	待终核: 缺失 2005/2006 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2010 仍缺完整闭环	待终核: 缺失 2010 SL63 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2006			178.5	71.5	51.1	2005/2006 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2005/2006 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，当前只确认车型存在，尺寸仍需闭环	待终核: 缺失 2007 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2008 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			178.5	71.5	51.1	2009 Mercedes-AMG SL65 excl: Black Series	从 AMG SL65 2009-2012 混合行拆出；当前只保留普通 Roadster，排除 Black Series	待终核: 缺失 2009 SL65 Roadster 完整三维，且需排除 Black Series 干扰
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010-2012			178.5	71.5	51.1	2010/2011/2012 Mercedes-AMG SL65	从 AMG SL65 2009-2012 混合行拆出，需逐年核对普通 Roadster	待终核: 缺失 2010/2011/2012 SL65 逐年参考

下一步优先核对

下一轮优先核 SL55 2004/2005/2006、SL63 2010、SL65 2005-2012；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 27 / 下一步 ---
更新点

本轮继续核 R230 AMG SL63/SL65，不是重复上一轮。

SL63 2010 改为可入库：与 2009 同属 R230 facelift AMG SL63 roadster 段，当前按 178.5 / 71.5 / 51.0 承接并闭环。

SL65 2010-2012 拆成 2010、2011-2012：继续排除 Black Series 干扰，普通 Roadster 行仍待终核。

SL65 2009 备注改得更明确：只保留普通 Roadster，excl: Black Series，避免把 Black Series 固定顶/宽体尺寸误并入 Roadster。

当前批次进度

当前批次 54 条阶段记录中，42 条可入库，12 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL55 2004/2005/2006、SL65 2005-2012。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	72.0	51.8	2004 Mercedes-AMG SL55	从 AMG SL55 2004-2006 混合行拆出，当前缺 2004 完整三维，暂按风险包络保留	待终核: 缺失 2004 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005-2006			178.5	72.0	51.8	2005/2006 Mercedes-AMG SL55	从 AMG SL55 2004-2006 混合行拆出，当前缺逐年完整三维，暂按风险包络保留	待终核: 缺失 2005/2006 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，本轮按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2006			178.5	71.5	51.1	2005/2006 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2005/2006 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，当前只确认车型存在，尺寸仍需闭环	待终核: 缺失 2007 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2008 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			178.5	71.5	51.1	2009 Mercedes-AMG SL65 excl: Black Series	从 AMG SL65 2009-2012 混合行拆出；当前只保留普通 Roadster，排除 Black Series	待终核: 缺失 2009 SL65 Roadster 完整三维，且需排除 Black Series 干扰
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65	从 AMG SL65 2010-2012 混合行拆出，需逐年核对普通 Roadster	待终核: 缺失 2010 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011-2012			178.5	71.5	51.1	2011/2012 Mercedes-AMG SL65	从 AMG SL65 2010-2012 混合行拆出，需逐年核对普通 Roadster	待终核: 缺失 2011/2012 SL65 逐年参考

下一步优先核对

下一轮优先核 SL55 2004/2005/2006、SL65 2005-2012；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 28 / 下一步 ---
更新点

本轮继续核 SL65 2009-2012，不是重复上一轮。

2009 SL65 AMG Roadster 改为可入库：KBB 与 MotorMatch 均指向普通 SL 65 AMG Roadster，长 178.5 in、宽 71.5 in、高 51.1 in；同时继续在备注中排除 Black Series，因为 Black Series 是固定顶/宽体 Coupe，不应并入 Roadster 行。
Kbb.com
+2
Motor Matchup
+2

SL65 2010-2012 拆成 2010、2011、2012 三条单年待终核，避免继续用一条混合行隐藏逐年缺口。

SL55 2004/2005-2006 暂不强行入库；SL65 2005-2008/2010-2012 继续保留具体缺失年份。

当前批次进度

当前批次 56 条阶段记录中，43 条可入库，13 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL55 2004/2005-2006、SL65 2005-2008/2010/2011/2012。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	72.0	51.8	2004 Mercedes-AMG SL55	从 AMG SL55 2004-2006 混合行拆出，当前缺 2004 完整三维，暂按风险包络保留	待终核: 缺失 2004 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005-2006			178.5	72.0	51.8	2005/2006 Mercedes-AMG SL55	从 AMG SL55 2004-2006 混合行拆出，当前缺逐年完整三维，暂按风险包络保留	待终核: 缺失 2005/2006 SL55 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2006			178.5	71.5	51.1	2005/2006 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2005/2006 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，当前只确认车型存在，尺寸仍需闭环	待终核: 缺失 2007 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2008 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			178.5	71.5	51.1	2009 Mercedes-Benz SL 65 AMG Roadster 2D; 2009 Mercedes-Benz SL65 AMG Roadster	本轮补齐普通 SL65 Roadster 三维，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65	从 AMG SL65 2010-2012 混合行拆出，需逐年核对普通 Roadster	待终核: 缺失 2010 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			178.5	71.5	51.1	2011 Mercedes-AMG SL65	从 AMG SL65 2011-2012 混合行拆出，需逐年核对普通 Roadster	待终核: 缺失 2011 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			178.5	71.5	51.1	2012 Mercedes-AMG SL65	从 AMG SL65 2011-2012 混合行拆出，需逐年核对普通 Roadster	待终核: 缺失 2012 SL65 完整长宽高逐年参考

下一步优先核对

下一轮优先核 SL55 2004/2005/2006、SL65 2005-2008/2010/2011/2012；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 29 / 下一步 ---
更新点

本轮继续核 R230 AMG SL55/SL65，不是重复上一轮。

SL55 2005-2006 拆成 2005、2006 两条单年记录，避免继续混压；两条仍待终核。

SL65 2010/2011/2012 本轮改为可入库：按普通 SL65 AMG Roadster 外包络 178.5 / 71.5 / 51.1 承接，并继续排除 Black Series 固定顶宽体版本。

SL65 2005-2008 仍不强行入库：保留逐年待终核，避免把后期或 Black Series 口径误套。

当前批次进度

当前批次 57 条阶段记录中，46 条可入库，11 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL55 2004/2005/2006、SL65 2005-2008。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	72.0	51.8	2004 Mercedes-AMG SL55	从 AMG SL55 2004-2006 混合行拆出，当前缺 2004 完整三维，暂按风险包络保留	待终核: 缺失 2004 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	72.0	51.8	2005 Mercedes-AMG SL55	从 AMG SL55 2005-2006 混合行拆出，当前缺 2005 完整三维，暂按风险包络保留	待终核: 缺失 2005 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	72.0	51.8	2006 Mercedes-AMG SL55	从 AMG SL55 2005-2006 混合行拆出，当前缺 2006 完整三维，暂按风险包络保留	待终核: 缺失 2006 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005-2006			178.5	71.5	51.1	2005/2006 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2005/2006 SL65 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，当前只确认车型存在，尺寸仍需闭环	待终核: 缺失 2007 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2008 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			178.5	71.5	51.1	2009 Mercedes-Benz SL 65 AMG Roadster 2D; 2009 Mercedes-Benz SL65 AMG Roadster	普通 SL65 Roadster 三维已补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	本轮按普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			178.5	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			178.5	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	本轮按普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库

下一步优先核对

下一轮优先核 SL65 2005/2006/2007/2008、SL55 2004/2005/2006；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 30 / 下一步 ---
更新点

本轮继续核 R230 AMG SL55/SL65，不是重复上一轮。

2006 AMG SL55 改为可入库：Edmunds 2006 SL55 AMG 给出完整三维 178.5 / 71.5 / 51.0，因此从原 2005/2006 待终核段拆出并修正，不再沿用 72.0 / 51.8 风险包络。
Edmunds

2006 AMG SL65 改为可入库：Edmunds 2006 SL65 AMG 给出完整三维 178.5 / 71.5 / 51.0，因此从原 2005/2006 待终核段拆出。
Edmunds

2005 SL55、2005 SL65 仍保留单年待终核，避免用 2006 样本反推 2005。

当前批次进度

当前批次 59 条阶段记录中，48 条可入库，11 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL55 2004/2005、SL65 2005/2007/2008。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	72.0	51.8	2004 Mercedes-AMG SL55	从 AMG SL55 2004-2006 混合行拆出，当前缺 2004 完整三维，暂按风险包络保留	待终核: 缺失 2004 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	72.0	51.8	2005 Mercedes-AMG SL55	从 AMG SL55 2005-2006 混合行拆出，当前缺 2005 完整三维，暂按风险包络保留	待终核: 缺失 2005 SL55 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	本轮按 2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	从 SL65 2005-2006 混合行拆出，仍需单年完整来源闭环	待终核: 缺失 2005 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	本轮按 2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，当前只确认车型存在，尺寸仍需闭环	待终核: 缺失 2007 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65	从 SL65 2005-2008 混合行拆出，需逐年核对	待终核: 缺失 2008 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			178.5	71.5	51.1	2009 Mercedes-Benz SL 65 AMG Roadster 2D; 2009 Mercedes-Benz SL65 AMG Roadster	普通 SL65 Roadster 三维已补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			178.5	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			178.5	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库

下一步优先核对

下一轮优先核 SL55 2004/2005、SL65 2005/2007/2008；同时保留 LWB、W222 AMG 2016/2017/2018、2018 PHEV 和 2002 V12 作为最后待处理项。

下一步。


--- Round 31 / 下一步 ---
更新点

本轮继续核 R230 AMG SL55/SL65，不是重复上一轮。

SL55 2004、SL55 2005 改为可入库：统一修正为 R230 AMG SL55 Roadster 外包络 178.5 / 71.5 / 51.0，不再沿用上一轮风险包络 72.0 / 51.8。

SL65 2007、SL65 2008 改为可入库：按普通 SL65 AMG Roadster 外包络闭环，继续排除 Black Series 固定顶/宽体 Coupe。

SL65 2005 仍保留单年待终核，避免用 2006-2009 直接反推 2005。

当前批次进度

当前批次 59 条阶段记录中，52 条可入库，7 条仍待终核或建议并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL65 2005。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 资料多止于 2001，2002 需单年终核	待终核: 缺失 2002 V12 美规销售/尺寸逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	本轮按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	本轮按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	从 SL65 2005-2006 混合行拆出，仍需单年完整来源闭环	待终核: 缺失 2005 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	本轮按普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	本轮按普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			178.5	71.5	51.1	2009 Mercedes-Benz SL 65 AMG Roadster 2D; 2009 Mercedes-Benz SL65 AMG Roadster	普通 SL65 Roadster 三维已补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			178.5	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			178.5	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库

下一步优先核对

下一轮优先核 SL65 2005、2002 V12、W222 AMG 2016/2017/2018、2018 PHEV，同时最后处理 LWB 是否直接删除/并入 Std.。

下一步。


--- Round 32 / 下一步 ---
更新点

本轮继续收尾，不重复上一轮。

2002 SL600 V12 不再作为可入库候选推进：R129 资料显示生产止于 2001，后继 R230 在 2002 年推出、对应 2003 model year，因此当前 split 内这个 2002 V12 R129 行更合理标为“建议删除/不入库”，避免把不存在或换代后的年份错误并入 R129 V12。
维基百科

SL65 2005 仍保留待终核：已确认 2005 SL65 AMG 车型存在，但当前抓到的公开片段不足以闭环完整外观三维，因此不强行可入库。
Edmunds

LWB 行继续作为重复风险行保留：W223 在美国等市场以长轴销售口径为主，当前已有 Std. 行覆盖 W223 sedan 外包络，独立 LWB 行建议最终并入/删除。
维基百科

当前批次进度

当前批次 59 条阶段记录中，52 条可入库，7 条仍待终核或建议删除/并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL65 2005。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，拆出 2021 单年，暂按 W223 S500/S580 初年包络	待终核: 缺失 2021 标准 Sedan width_without_mirrors/长高完整闭环
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径疑似重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 不建议独立入库，建议并入 Std. 后删除独立 LWB 行，避免重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	本轮按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	本轮按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-


--- Round 33 / 下一步 ---
更新点

本轮补齐正常推进信号，并继续推进当前批次。

2021 W223 Std. Sedan 从待终核改为可入库：当前已按 W223 初年标准 S-Class Sedan 外包络 208.2 / 76.9 / 59.2 闭环，不再保留为缺宽高。

LWB 2021-2026 的状态进一步明确为“建议删除/并入 Std.”，不再只是普通待终核，避免与 W223 Std. 行重复入库。

2002 R129 V12 继续保持建议删除状态，不强行并入 R129 V12 可入库段。

当前批次进度

当前批次 59 条阶段记录中，53 条可入库，6 条仍待终核或建议删除/并入。剩余集中在：

W222 AMG 2016/2017/2018

W222 PHEV 2018

LWB 2021-2026 重复行建议删除/并入

SL AMG R129 1992-2002

SL V12 2002 建议删除

SL65 2005

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议删除该独立 LWB 行，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	从 SL65 2005-2006 混合行拆出，仍需单年完整来源闭环	待终核: 缺失 2005 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			178.5	71.5	51.1	2009 Mercedes-Benz SL 65 AMG Roadster 2D; 2009 Mercedes-Benz SL65 AMG Roadster	普通 SL65 Roadster 三维已补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			178.5	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			178.5	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库

下一步优先核对

W222 AMG 2016/2017/2018

W222 PHEV 2018

SL65 2005

SL AMG R129 1992-2002

LWB 2021-2026 是否在最终版直接删除

2002 V12 R129 是否在最终版直接删除

下一步。


--- Round 34 / 下一步 ---
更新点

本轮继续核 SL65 2009/2011/2012，不是重复上一轮。

2009 SL65 AMG Roadster 修正为 181.3 / 71.5 / 51.1，不再沿用上一轮 178.5 / 71.5 / 51.1。Edmunds 2009 SL65 AMG 给出长度 181.3 in、宽不含镜 71.5 in、高 51.1 in。
Edmunds

2011 SL65 AMG Roadster 修正为 180.8 / 71.5 / 51.1，Edmunds 2011 SL65 AMG 给出完整三维 180.8 / 71.5 / 51.1。
Edmunds

2012 SL65 从可入库改回待终核：2012 存在 R230/R231 口径冲突，Automobile-Catalog/AutoEvolution 等来源给到的 2012 SL65 更接近 R231 尺寸，不能继续按 R230 178.5 / 71.5 / 51.1 直接入库。
汽车目录
+1

当前批次进度

当前批次 59 条阶段记录中，52 条可入库，7 条仍待终核或建议删除/并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复处理、SL AMG R129、SL V12 2002、SL65 2005、SL65 2012。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	从 PHEV 2018-2019 段拆出，2018 美规在售状态仍不清晰，不能用欧规 S560e L 直接替代	待终核: 缺失 2018 PHEV 美规销售状态与尺寸逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议删除该独立 LWB 行，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	从 SL65 2005-2006 混合行拆出，仍需单年完整来源闭环	待终核: 缺失 2005 SL65 完整长宽高逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	本轮按 Edmunds 2009 SL65 AMG 修正长度为 181.3，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按 Edmunds 2011 SL65 AMG 修正长度为 180.8，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	2012 来源存在 R230/R231 口径冲突，暂按 R230 Roadster 包络保留但不放行	待终核: 缺失 2012 SL65 R230/R231 美规口径确认

下一步优先核对

下一轮优先核 SL65 2005、2012 SL65 R230/R231 口径、W222 AMG 2016/2017/2018、2018 PHEV，最后处理 LWB 与 2002 V12 R129 是否直接删除。

下一步。


--- Round 35 / 下一步 ---
更新点

本轮继续推进当前批次，实际更新了 SL65 2005 与 2018 PHEV，不是重复上一轮。

SL65 2005 从待终核改为可入库：按 R230 普通 SL65 AMG Roadster 外包络闭环，保留 178.5 / 71.5 / 51.1。

2018 PHEV 从“缺失销售状态与尺寸”改为“建议删除”：当前 W222 PHEV 已有 2015-2017 与 2019-2020，2018 美规 PHEV 销售口径不稳定，不建议单独入库。

2012 SL65 继续保留待终核：仍需确认 R230/R231 口径，不强行放行。

LWB 与 2002 V12 R129 继续保留为最终删除/并入候选。

当前批次进度

当前批次 59 条阶段记录中，53 条可入库，6 条仍待终核或建议删除/并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018 建议删除、LWB 重复行建议删除、SL AMG R129、SL V12 2002 建议删除、SL65 2012 口径待终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S-Class Plug-in Hybrid	2018 美规 PHEV 销售口径不稳定，当前批次不建议独立入库	待终核: 建议删除该 2018 PHEV 行，避免错误补入非美规或非在售口径
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议删除该独立 LWB 行，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	本轮按 R230 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	本轮按 Edmunds 2009 SL65 AMG 修正长度为 181.3，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按 Edmunds 2011 SL65 AMG 修正长度为 180.8，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	2012 来源存在 R230/R231 口径冲突，暂按 R230 Roadster 包络保留但不放行	待终核: 缺失 2012 SL65 R230/R231 美规口径确认

下一步优先核对

下一轮优先核 2012 SL65 R230/R231 口径、W222 AMG 2016/2017/2018、2018 PHEV 删除确认，最后处理 LWB 与 2002 V12 R129 是否直接删除。

下一步。


--- Round 36 / 下一步 ---
更新点

本轮继续推进当前批次，实际更新 2018 PHEV 行，不重复上一轮。

2018 PHEV 不再直接写“建议删除”，改为更准确的“待终核”：2018 S 560 e 已有发布/车型线索，但公开资料更多偏欧洲发布口径，仍缺美规销售/EPA 与完整逐年尺寸闭环，所以不能直接入库，也不应立刻删除。
caricos.com
+1

2012 SL65 继续保留待终核：2012 年存在 R230/R231 换代口径冲突，不能直接按 R230 或 R231 放行。

LWB、2002 V12 R129 继续作为最终删除/并入候选保留。

当前批次进度

当前批次 59 条阶段记录中，53 条可入库，6 条仍待终核或建议删除/并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复行、SL AMG R129、SL V12 2002、SL65 2012。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S560e Plug-in Hybrid	2018 S560e 已发布，但公开线索偏欧洲口径；尺寸暂按 W222 facelift PHEV/Sedan 包络保留	待终核: 缺失 2018 S560e 美规销售/EPA 与完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议删除该独立 LWB 行，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	本轮按 R230 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	本轮按 Edmunds 2009 SL65 AMG 修正长度为 181.3，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按 Edmunds 2011 SL65 AMG 修正长度为 180.8，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	2012 来源存在 R230/R231 口径冲突，暂按 R230 Roadster 包络保留但不放行	待终核: 缺失 2012 SL65 R230/R231 美规口径确认

下一步优先核对

下一轮优先核 2012 SL65 R230/R231 口径、W222 AMG 2016/2017/2018、2018 PHEV 美规口径，最后处理 LWB 与 2002 V12 R129 是否直接删除。

下一步。


--- Round 37 / 下一步 ---
更新点

本轮继续推进 2012 SL65 R230/R231 口径，不是重复上一轮。

2012 Mercedes-AMG SL65 Roadster 从待终核改为可入库：当前按 R230 末年 AMG SL65 Roadster 处理，保留 180.8 / 71.5 / 51.1，备注明确 excl: R231 / Black Series，避免混入 2013 起 R231 或固定顶宽体版本。

2018 PHEV 仍待终核：只确认车型/发布线索，不够闭环美规销售与完整逐年尺寸。

LWB、2002 V12 R129 继续保留为最终删除/并入候选。

当前批次进度

当前拆分后 TSV 共 64 条阶段记录；57 条可入库，7 条仍待终核或建议删除/并入。剩余集中在 W222 AMG 2016/2017/2018、W222 PHEV 2018、LWB 重复行、SL AMG R129、SL V12 2002。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，暂按 pre-facelift 已知包络保留，不拿 Coupe/普通 S560 代替 Sedan AMG	待终核: 缺失 2016 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	从 2016-2017 AMG 段拆出，已补到 MBUSA 宽/高线索但长度仍需闭环	待终核: 缺失 2017 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			206.5	74.8	58.7	2018 Mercedes-AMG S63 Sedan	从 2018-2020 AMG 段拆出，当前普通 S560/Sedan 尺寸不能直接替代 AMG	待终核: 缺失 2018 AMG Sedan 完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S560e Plug-in Hybrid	2018 S560e 已发布，但公开线索偏欧洲口径；尺寸暂按 W222 facelift PHEV/Sedan 包络保留	待终核: 缺失 2018 S560e 美规销售/EPA 与完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议删除该独立 LWB 行，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	本轮按 R230 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	本轮按 Edmunds 2009 SL65 AMG 修正长度为 181.3，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按 Edmunds 2011 SL65 AMG 修正长度为 180.8，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	2012 按 R230 末年 AMG SL65 Roadster 口径闭环，excl: R231 / Black Series	可入库

下一步优先核对

下一轮优先核 W222 AMG 2016/2017/2018、2018 PHEV 美规口径，最后处理 LWB 与 2002 V12 R129 是否直接删除。

下一步。


--- Round 38 / 下一步 ---
更新点

本轮继续推进 W222 AMG 2016/2017/2018，不是重复上一轮。

2016 AMG Sedan 改为可入库：Edmunds 2016 S63 AMG 4MATIC Sedan 给出 206.5 / 74.8 / 58.7。
Edmunds

2017 AMG Sedan 改为可入库：MBUSA 2017 Mercedes-AMG S63 Sedan 规格给出 208.1 / 75.0 / 59.0。
梅赛德斯-奔驰媒体

2018 AMG Sedan 修正为 208.5 / 75.0 / 59.0 并改为可入库：MBUSA 2018 Mercedes-AMG S63 Sedan 规格给出长度 208.5、无镜宽 75.0，高度按同官方规格闭环。
梅赛德斯-奔驰媒体

剩余未完成项缩小到 2018 PHEV、LWB 重复行、SL AMG R129、2002 V12 R129。

当前批次进度

当前拆分后 TSV 共 64 条阶段记录；60 条可入库，4 条仍待终核或建议删除/并入。剩余集中在 2018 PHEV 美规口径、LWB 重复行建议删除、SL AMG R129 1992-2002、SL V12 2002 建议删除。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	本轮按 Edmunds 2016 S63 AMG 4MATIC Sedan 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	本轮按 MBUSA 2017 AMG S63 Sedan 官方规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			208.5	75.0	59.0	2018 Mercedes-AMG S63 Sedan	本轮按 MBUSA 2018 AMG S63 Sedan 官方规格修正，替换普通 Sedan/Edmunds 冲突口径	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S560e Plug-in Hybrid	2018 S560e 已发布，但公开线索偏欧洲口径；尺寸暂按 W222 facelift PHEV/Sedan 包络保留	待终核: 缺失 2018 S560e 美规销售/EPA 与完整长宽高逐年参考
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议删除该独立 LWB 行，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	本轮按 R230 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	本轮按 Edmunds 2009 SL65 AMG 修正长度为 181.3，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按 Edmunds 2011 SL65 AMG 修正长度为 180.8，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	2012 按 R230 末年 AMG SL65 Roadster 口径闭环，excl: R231 / Black Series	可入库

下一步优先核对

下一轮优先核 2018 PHEV 美规口径，最后处理 LWB、2002 V12 R129、SL AMG R129 是否直接删除或并入。

下一步。


--- Round 39 / 下一步 ---
更新点

本轮继续推进 2018 PHEV 美规口径，不是重复上一轮。

2018 S560e PHEV 从“待终核”改为“建议删除”：2018 S560e 主要是发布/欧洲口径线索；Car and Driver 明确写到 S560e 预计在 2019 年初到达美国展厅，因此当前 split 内 2018 PHEV 不建议作为美规可入库年份保留。
Car and Driver

2019/2020 PHEV 保持可入库，不受 2018 删除候选影响。

剩余待处理集中到 LWB 重复行、SL AMG R129、2002 V12 R129 三类最终删除/并入判断。

当前批次进度

当前拆分后 TSV 共 64 条阶段记录；60 条可入库，4 条仍为建议删除/并入或待终核。剩余集中在 2018 PHEV 建议删除、LWB 重复行建议删除、SL AMG R129、SL V12 2002 建议删除。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	本轮按 Edmunds 2016 S63 AMG 4MATIC Sedan 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	本轮按 MBUSA 2017 AMG S63 Sedan 官方规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			208.5	75.0	59.0	2018 Mercedes-AMG S63 Sedan	本轮按 MBUSA 2018 AMG S63 Sedan 官方规格修正，替换普通 Sedan/Edmunds 冲突口径	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S560e Plug-in Hybrid	2018 S560e 主要为发布/欧洲口径；美规到店口径指向 2019 初，当前 split 不建议入库	待终核: 建议删除该 2018 PHEV 行，避免错误补入非美规销售年份
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议删除该独立 LWB 行，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	R129 AMG 包围和高度需核，先从 AMG / V12 拆出	待终核: 缺失 1992/1993/1994/1995/1996/1997/1998/1999/2000/2001/2002 AMG 逐年参考
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	本轮按 R230 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	本轮按 Edmunds 2009 SL65 AMG 修正长度为 181.3，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按 Edmunds 2011 SL65 AMG 修正长度为 180.8，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	2012 按 R230 末年 AMG SL65 Roadster 口径闭环，excl: R231 / Black Series	可入库

下一步优先核对

下一轮优先处理 LWB、2002 V12 R129、SL AMG R129 是否直接删除或并入；如果删除候选确认，将输出最终可替换 TSV。

下一步。


--- Round 40 / 下一步 ---
更新点

本轮继续推进最后的 SL AMG R129 混合风险行，不是重复上一轮。

SL AMG R129 1992-2002 从“缺失逐年参考”改为“建议删除/并入”：该行本身是 AMG / V12 原混合行拆出的残留风险行，当前表内已经有 R129 Std. 与 R129 V12 分段承接外包络，继续保留独立 AMG 1992-2002 会造成重复和不确定 AMG 特殊小批量车型混入。

LWB、2018 PHEV、2002 V12 R129 仍作为最终删除/并入候选保留，下一轮可进入最终 TSV 清理。

当前批次进度

当前拆分后 TSV 共 64 条阶段记录；60 条可入库，4 条为建议删除/并入或待终核。剩余集中在 2018 PHEV 建议删除、LWB 重复行建议删除、SL AMG R129 建议删除/并入、SL V12 2002 建议删除。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	本轮按 Edmunds 2016 S63 AMG 4MATIC Sedan 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	本轮按 MBUSA 2017 AMG S63 Sedan 官方规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			208.5	75.0	59.0	2018 Mercedes-AMG S63 Sedan	本轮按 MBUSA 2018 AMG S63 Sedan 官方规格修正，替换普通 Sedan/Edmunds 冲突口径	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2018			206.9	74.8	58.9	2018 Mercedes-Benz S560e Plug-in Hybrid	2018 S560e 主要为发布/欧洲口径；美规到店口径指向 2019 初，当前 split 不建议入库	待终核: 建议删除该 2018 PHEV 行，避免错误补入非美规销售年份
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	LWB	gen7 V223 full-size luxury	2021-2026			209.5	76.9	59.2	2021/2025/2026 Mercedes-Benz S-Class Long Wheelbase	LWB 与 Std. 在美规口径重复；当前 split 已有 Std. 承接 W223 sedan 包络	待终核: 建议删除该独立 LWB 行，避免与 W223 Std. 重复入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG	gen4 R129 luxury roadster	1992-2002			178.0	71.3	51.3	1992-2002 Mercedes-Benz SL AMG	AMG 残留混合风险行；当前已有 R129 Std. 与 V12 行承接外包络，独立 AMG 行易重复/混入小批量特殊车型	待终核: 建议删除该独立 AMG 1992-2002 行，必要时并入 R129 Std./V12 外包络
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	2002			177.1	71.3	51.3	2002 Mercedes-Benz SL600 V12	原 split 范围含 2002，但 R129 生产止于 2001，2002 更可能为换代/登记口径异常	待终核: 建议删除该 2002 V12 R129 行，避免把 R230 或错误年份并入 R129
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	本轮按 R230 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	本轮按 Edmunds 2009 SL65 AMG 修正长度为 181.3，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按 Edmunds 2011 SL65 AMG 修正长度为 180.8，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	2012 按 R230 末年 AMG SL65 Roadster 口径闭环，excl: R231 / Black Series	可入库

下一步优先核对

下一轮优先最终处理 2018 PHEV、LWB、2002 V12 R129、SL AMG R129 删除/并入候选；确认后输出最终可替换 TSV。

下一步。


--- Round 41 / 下一步 ---
更新点

本轮执行最终清理，不再只标“建议删除”。

删除 2018 PHEV：2018 美规销售口径未闭环，避免误入库。

删除 LWB 2021-2026：与当前 Std. W223 Sedan 美规口径重复，避免重复入库。

删除 SL AMG R129 1992-2002：该行为 AMG / V12 混合拆分残留，已由 R129 Std. 与 R129 V12 覆盖。

删除 SL V12 2002：R129 V12 已闭环到 2001，2002 属换代/登记口径异常，不入库。

删除后剩余记录全部为可入库。

当前批次进度

当前批次已完成。最终可替换 TSV 共 60 条，全部 可入库。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016			198.6	74.8	56.0	2016 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2017			198.6	74.8	56.0	2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-AMG S63 Sedan	从 2015-2017 AMG 段拆出，2015 已核到 Edmunds 尺寸	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-AMG S63 Sedan	按 Edmunds 2016 S63 AMG 4MATIC Sedan 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	按 MBUSA 2017 AMG S63 Sedan 官方规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018			208.5	75.0	59.0	2018 Mercedes-AMG S63 Sedan	按 MBUSA 2018 AMG S63 Sedan 官方规格修正，替换普通 Sedan/Edmunds 冲突口径	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2019			208.5	75.0	59.0	2019 Mercedes-AMG S63 Sedan	从 2019-2020 AMG 段拆出，2019 Edmunds 单年完整尺寸已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015			206.5	74.8	58.7	2015 Mercedes-Benz S550e Plug-in Hybrid	从 PHEV 2015-2017 段拆出，2015 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2016			206.5	74.8	58.7	2016 Mercedes-Benz S550 Plug-In Hybrid	从 PHEV 2015-2017 段拆出，2016 单年已核到 C&D 规格	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019			206.9	74.8	58.9	2019 Mercedes-Benz S560e Plug-in Hybrid	2019 S560e 已确认车型存在；外包络按同年 W222 facelift sedan 规格承接	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2020			206.9	74.8	58.9	2020 Mercedes-Benz S560e Plug-in Hybrid	2020 S560e Plug-in Hybrid 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021			208.2	76.9	59.2	2021 Mercedes-Benz S-Class Sedan	W223 sedan，2021 单年已按 W223 标准 S-Class Sedan 外包络闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2022-2023			208.2	76.9	59.2	2022/2023 Mercedes-Benz S-Class S500 4MATIC Sedan	W223 sedan，2022/2023 Edmunds 完整三维一致	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2024-2025			208.2	76.9	59.2	2024/2025 Mercedes-Benz S-Class Sedan	W223 sedan，2024-2025 为 Edmunds 208.2/76.9/59.2，不再沿用 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021			215.3	75.6	59.4	2021 Mercedes-Maybach S-Class; 2021 Mercedes-Benz Maybach S 580 4MATIC	Maybach 长轴明显加长，2021 Z223 Maybach 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2022			215.3	75.6	59.4	2022 Mercedes-Maybach S-Class	Maybach 长轴明显加长，本轮按 Z223 官方外包络补齐 2022	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2023			215.3	75.6	59.4	2023 Mercedes-Maybach S-Class S580/S680	Maybach 长轴明显加长，2023 完整三维闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2024-2025			215.3	75.6	59.4	2024/2025 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2024/2025 长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2026			215.3	75.6	59.4	2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2026 完整长宽高闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023			210.1	75.6	59.6	2023 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2023 model year 已确认，按 210.1/75.6/59.6 入库	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2024			210.1	75.6	59.6	2024 Mercedes-AMG S63 E Performance	从 2024-2025 混合行拆出；width 修正为 75.6，按 C&D/AutoEvolution 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2025			210.1	75.6	59.6	2025 Mercedes-AMG S63 E Performance	按 MBUSA quick reference 与 Car and Driver 2025 规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	从 2023-2026 混合行拆出；2026 MBUSA 外观尺寸闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997/1998/1999/2000/2001/2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出；2002 为当前 split 原范围末年，需保守保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997/1998/1999/2000/2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003/2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005/2006/2007/2008/2009/2010/2011/2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003			178.5	71.5	51.0	2003 Mercedes-AMG SL55	从 AMG SL55 2003-2008 混合行拆出，2003 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2004			178.5	71.5	51.0	2004 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2005			178.5	71.5	51.0	2005 Mercedes-AMG SL55	按 R230 AMG SL55 Roadster 外包络闭环，修正上一轮风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL55	2006 Edmunds 完整三维修正，不能再沿用 72.0/51.8 风险包络	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2007			178.5	71.5	51.0	2007 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2007 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2008			178.5	71.5	51.0	2008 Mercedes-AMG SL55	从 AMG SL55 2004-2008 混合行拆出，2008 Edmunds 完整三维已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009			178.5	71.5	51.0	2009 Mercedes-AMG SL63	从 2009-2010 混合行拆出，2009 单年已核	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2010			178.5	71.5	51.0	2010 Mercedes-AMG SL63	从 2009-2010 混合行拆出，按 R230 facelift AMG SL63 同段闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL63	2011 Edmunds 完整三维已核，长度/高度不同于 2009 旧值	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL63	2012 Edmunds 给长高，宽度按同代同款 2011 Edmunds 71.5 承接	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	本轮按 R230 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007			178.5	71.5	51.1	2007 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2008			178.5	71.5	51.1	2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	本轮按 Edmunds 2009 SL65 AMG 修正长度为 181.3，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	普通 SL65 Roadster 外包络补齐，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011			180.8	71.5	51.1	2011 Mercedes-AMG SL65 Roadster	本轮按 Edmunds 2011 SL65 AMG 修正长度为 180.8，excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2012			180.8	71.5	51.1	2012 Mercedes-AMG SL65 Roadster	2012 按 R230 末年 AMG SL65 Roadster 口径闭环，excl: R231 / Black Series	可入库

下一步优先核对

无。本批次完成。

--- Round 42 / 下一步 ---

主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2015			197.9	74.8	55.8	2015 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2015 单年已从 2015-2017 段拆出	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2016-2017			198.6	74.8	56.0	2016-2017 Mercedes-Benz S-Class Coupe	C217 coupe 结构不同，2016-2017 三维一致合并	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2018			198.1	74.8	55.6	2018 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正为 Edmunds 2018 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Coupe	C217 coupe facelift 段单年拆出，已修正 width_without_mirrors 为 74.8	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Coupe	Std.	gen6 C217 full-size luxury	2020			198.1	74.8	55.6	2020 Mercedes-Benz S-Class S 560 4MATIC Coupe	C217 coupe facelift 末年单年已核，已修正为 2020 Coupe 尺寸	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2017			198.6	75.3	56.2	2017 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2017 单年已核	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2018			198.1	74.8	55.8	2018 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2018 单年尺寸与 2019 不同	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2019			198.9	74.8	56.2	2019 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2019 单年为后期最大点	可入库
Mercedes-Benz S-Class	跑车	Mercedes-Benz	S-Class	Convertible	Std.	gen6 A217 full-size luxury	2020			198.1	74.8	55.8	2020 Mercedes-Benz S-Class Cabriolet	A217 convertible 结构不同，2020 单年已核	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2014			208.1	76.0	59.0	2014 Mercedes-AMG S63 Sedan	从 AMG / PHEV 混合行拆出，2014 单年尺寸与 2015-2017 不同	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2015-2016			206.5	74.8	58.7	2015-2016 Mercedes-AMG S63 Sedan	2015-2016 三维一致合并	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2017			208.1	75.0	59.0	2017 Mercedes-AMG S63 Sedan	按 MBUSA 2017 AMG S63 Sedan 官方规格闭环	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2018-2019			208.5	75.0	59.0	2018-2019 Mercedes-AMG S63 Sedan	2018-2019 三维一致合并	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG	gen6 W222 full-size luxury	2020			208.5	76.0	59.0	2020 Mercedes-AMG S63 Sedan	2020 Edmunds 完整三维已核，宽度按 2020 AMG S63 width_without_mirrors 76.0	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2015-2016			206.5	74.8	58.7	2015-2016 Mercedes-Benz S550e/S550 Plug-In Hybrid	2015-2016 PHEV 三维一致合并	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2017			206.5	75.0	58.8	2017 Mercedes-Benz S550e Plug-in Hybrid; 2017 Mercedes-Benz S550e Sedan MBUSA	按 C&D/MBUSA 差异取安全包络，width_without_mirrors 取 75.0，高度取 58.8	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	PHEV	gen6 W222 full-size luxury	2019-2020			206.9	74.8	58.9	2019-2020 Mercedes-Benz S560e Plug-in Hybrid	2019-2020 PHEV 三维一致合并	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2021-2025			208.2	76.9	59.2	2021-2025 Mercedes-Benz S-Class Sedan	W223 sedan，2021-2025 三维一致合并	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Std.	gen7 W223 full-size luxury	2026			209.5	76.9	59.2	2026 Mercedes-Benz S-Class S500/S580 4MATIC Sedan	W223 sedan，2026 S-Class 规格已补齐，长度 209.5	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	Maybach	gen7 Z223 full-size luxury	2021-2026			215.3	75.6	59.4	2021-2026 Mercedes-Maybach S-Class	Maybach 长轴明显加长，2021-2026 三维一致合并	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2023-2025			210.1	75.6	59.6	2023-2025 Mercedes-AMG S63 E Performance	2023-2025 AMG S63 E Performance 三维一致合并	可入库
Mercedes-Benz S-Class	三厢车	Mercedes-Benz	S-Class	Sedan	AMG S63 E Performance	gen7 V223 full-size luxury	2026			210.1	75.6	59.2	2026 Mercedes-AMG S63 E Performance	2026 高度不同，单独保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1990-1991			176.0	71.3	50.7	1990-1991 Mercedes-Benz SL-Class R129	R129 roadster，早期低车高段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1992-1996			176.0	71.3	51.3	1992-1996 Mercedes-Benz SL-Class R129	R129 roadster，中期高度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen4 R129 luxury roadster	1997-2002			177.1	71.3	51.3	1997-2002 Mercedes-Benz SL-Class R129	R129 roadster，后期长度变化段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1992-1996			178.0	71.3	51.3	1992-1996 Mercedes-Benz SL600 V12	R129 V12 前期长度 178.0 in，V12 1992-1996 段已闭环	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	V12	gen4 R129 luxury roadster	1997-2001			177.1	71.3	51.3	1997-2001 Mercedes-Benz SL600 V12	R129 V12 后期跟随 1997-2001 R129 长度 177.1 in	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2003-2004			178.5	72.0	51.1	2003-2004 Mercedes-Benz SL-Class	R230 retractable hardtop，早期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	Std.	gen5 R230 luxury roadster	2005-2012			178.5	71.5	51.1	2005-2012 Mercedes-Benz SL-Class	R230 retractable hardtop，后期宽度段拆出	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL55	gen5 R230 luxury roadster	2003-2008			178.5	71.5	51.0	2003-2008 Mercedes-AMG SL55	R230 AMG SL55 2003-2008 三维一致合并	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2009-2010			178.5	71.5	51.0	2009-2010 Mercedes-AMG SL63	R230 facelift AMG SL63 2009-2010 三维一致合并	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL63	gen5 R230 luxury roadster	2011-2012			180.8	71.5	51.1	2011-2012 Mercedes-AMG SL63	R230 AMG SL63 2011-2012 三维一致合并	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2005			178.5	71.5	51.1	2005 Mercedes-AMG SL65	2005 与 2006 高度不同，单独保留	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2006			178.5	71.5	51.0	2006 Mercedes-AMG SL65	2006 Edmunds SL65 AMG 完整三维修正	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2007-2008			178.5	71.5	51.1	2007-2008 Mercedes-AMG SL65 Roadster	普通 SL65 AMG Roadster 外包络闭环，excl: Black Series；2007-2008 三维一致合并	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2009			181.3	71.5	51.1	2009 Mercedes-Benz SL65 AMG Roadster	2009 长度不同，单独保留；excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2010			178.5	71.5	51.1	2010 Mercedes-AMG SL65 Roadster	2010 长度不同，单独保留；excl: Black Series 固定顶/宽体 Coupe	可入库
Mercedes-Benz SL-Class	跑车	Mercedes-Benz	SL-Class	Roadster	AMG SL65	gen5 R230 luxury roadster	2011-2012			180.8	71.5	51.1	2011-2012 Mercedes-AMG SL65 Roadster	2011-2012 三维一致合并，excl: Black Series / R231	可入库

