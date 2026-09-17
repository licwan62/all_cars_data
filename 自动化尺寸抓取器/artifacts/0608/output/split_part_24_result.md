# 文件名：split_part_24.tsv


--- Round 1 / 首次发送 ---
更新点

已把“分类”从 皮卡车 统一修正为规则允许值 皮卡。

已把 crew / regular 标准化为 Crew Cab / Regular Cab，皮卡结构统一保留 Pickup。

Silverado HD 2024-2026 Crew/Double Cab 标准床参考可支持 6'10" 标准床、250.0 in Crew Cab 记录；但部分行仍未覆盖每一年或子车系，状态改为具体“待终核”。2026 2500HD Double Cab 标准床官方规格显示 overall length 约 240.51 in、width w/o mirrors 约 81.85 in、height 约 79.95 in。
雪佛兰加拿大
+1

Ford F-150 1992-1996 Regular Cab 8.0 ft 原 219.1 实际更像 Extended Cab 参考，已先按 1992 Regular Cab 8.0 ft 可见值修为 213.3，但 1993-1996 仍需逐年终核。
Edmunds
+1

当前批次进度

本轮已完成字段标准化：10/10 行。

已修正明显错误参考/状态：10/10 行。

仍未全部可入库：DRW 历史代际与 F-150 1992-1996 需要逐年补齐参考。

本轮更新后的 TSV：

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen4 HD pickup facelift	2024-2026	Crew Cab	6.8	250	81.9	80.9	2024/2025 Silverado 3500HD Crew Cab standard bed SRW; 2024 Silverado 2500HD Crew Cab standard bed	HD SRW; 分类/驾驶室字段已标准化；原合并子车系需继续按 2500HD/3500HD 逐年拆核	待终核: 缺失 2026 Crew Cab standard bed SRW 对应 2500HD/3500HD 全子车系参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen4 HD pickup facelift	2026	Double Cab	6.8	240.5	81.9	80.0	2026 Silverado 2500HD Double Cab standard bed SRW	HD SRW; 原 crew 已修为 Double Cab；尺寸按 2026 Double Cab standard bed 先修正	待终核: 原记录含 3500HD/Double Cab 覆盖关系未确认
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2001-2007	Crew Cab	8.0	266	96.8	80.7	2007 Silverado 3500HD Crew Cab long bed; 2026 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 分类/驾驶室字段已标准化；当前尺寸仍主要来自后代 DRW 参考	待终核: 缺失 2001-2006 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen2 HD pickup	2008-2014	Crew Cab	8.0	266	96.8	80.7	2026 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 分类/驾驶室字段已标准化；当前参考车型不属于本代	待终核: 缺失 2008-2014 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2015-2019	Crew Cab	8.0	266	96.8	80.7	2015 Silverado 3500HD Crew Cab long bed sample; 2026 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 分类/驾驶室字段已标准化；2015 样本未完全确认 DRW 宽体配置	待终核: 缺失 2015-2019 Crew Cab DRW long bed 逐年宽体尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup	2020-2023	Crew Cab	8.0	266	96.8	80.0	2020 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 2020 DRW long bed 尺寸已修正高度为 80.0；仍需补齐后续年份	待终核: 缺失 2021-2023 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup facelift	2024-2026	Crew Cab	8.0	266	96.8	80.7	2026 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 分类/驾驶室字段已标准化；2026 参考不能覆盖完整区间	待终核: 缺失 2024-2025 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado EV	皮卡	Chevrolet	Silverado EV	Pickup	Std.	EV pickup	2024-2026	Crew Cab	5.9	233.1	83.8	78.7	2024-2026 Silverado EV Crew Cab EV pickup	EV; 分类/驾驶室字段已标准化	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	6.5	197.1	79	70.8	1996 Ford F-150 Regular Cab short bed	分类/驾驶室字段已标准化；短床尺寸待逐年确认	待终核: 缺失 1992-1995 Regular Cab 6.5 ft 逐年尺寸参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	8.0	213.3	79	70.8	1992 Ford F-150 Regular Cab long bed	分类/驾驶室字段已标准化；原 219.1 更接近 Extended Cab，已按 Regular Cab long bed 先修为 213.3	待终核: 缺失 1993-1996 Regular Cab 8.0 ft 逐年尺寸参考

下一步优先核对

Chevrolet Silverado 3500HD DRW：按 2001-2007、2008-2014、2015-2019、2020-2023、2024-2026 分代逐年核对 Crew Cab 8.0/8.2 ft DRW long bed。

Ford F-150 gen9：补齐 1992-1996 Regular Cab 6.5 ft 与 8.0 ft 每一年参考，避免 Extended Cab 尺寸串入 Regular Cab。

Silverado HD 2024-2026：确认 2500HD/3500HD、Crew Cab/Double Cab、SRW 标准床是否应继续拆成子车系独立行。

下一步


--- Round 2 / 下一步 ---
更新点

继续补强当前 10 行，没有新增当前 TSV 范围外车型或年份。

将第 2 行从混合 Silverado 2500HD/3500HD 缩小为 Silverado 2500HD，因为 2026 Double Cab standard bed 更明确对应 2500HD；不再让 3500HD 混入 Double Cab 行。

将 Silverado 3500HD DRW 老代际不再沿用 2026 尺寸作为主参考，已按能确认的本代样本补入参考车型；仍未逐年完整覆盖的保持具体“待终核”。

将 2024-2026 Silverado 3500HD Crew Cab DRW long bed 的参考覆盖补强为 2024/2025/2026，该行本轮更新为“可入库”。

Ford F-150 两行继续保留为 Regular Cab，8.0 ft 行已维持 213.3，避免混入 SuperCab 的 219.1。

当前批次进度

当前批次字段标准化：10/10 已完成。

当前批次已有明确可入库：2/10。

当前批次仍待终核：8/10，主要集中在 Silverado 3500HD DRW 历史代际逐年参考、F-150 1992-1996 Regular Cab 两种货斗逐年参考、以及 Silverado 2500HD/3500HD 合并行的子车系覆盖。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen4 HD pickup facelift	2024-2026	Crew Cab	6.8	250	81.9	80.9	2024 Silverado 2500HD Crew Cab standard bed; 2024/2025/2026 Silverado 3500HD Crew Cab standard bed SRW	HD SRW; 分类/驾驶室字段已标准化；2500HD 与 3500HD Crew Cab standard bed 高度取最大 3500HD	待终核: 缺失 2025-2026 Silverado 2500HD Crew Cab standard bed 逐年参考
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen4 HD pickup facelift	2026	Double Cab	6.8	240.5	81.9	80.0	2026 Silverado 2500HD Double Cab standard bed SRW	HD SRW; 原混合 2500HD/3500HD 行已缩小为 2500HD，避免 3500HD Double Cab 混入	待终核: 需确认 2026 Silverado 2500HD Double Cab standard bed 全配置高度是否存在更高值
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2001-2007	Crew Cab	8.0	258.7	96.1	80.7	2001 Silverado 3500 Crew Cab long bed; 2007 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 已加入本代首末样本，2007 新旧车身可能存在过渡	待终核: 缺失 2002-2006 Crew Cab DRW long bed 逐年尺寸参考，且 2007 Classic/New Body 需终核
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen2 HD pickup	2008-2014	Crew Cab	8.0	258.7	95.9	76.0	2008 Silverado 3500HD Crew Cab long bed DRW; 2014 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 不再沿用 2026 尺寸，先按本代 GMT900 DRW 样本修正	待终核: 缺失 2009-2013 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2015-2019	Crew Cab	8.0	258.4	96.0	78.1	2015 Silverado 3500HD Crew Cab long bed DRW; 2018 Silverado 3500HD Crew Cab long bed; 2019 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 已用本代样本替换 2026 后代参考，尺寸按 2015-2019 本代最大值暂定	待终核: 缺失 2016-2017 Crew Cab DRW long bed 逐年尺寸参考，且 2018 样本需确认是否 DRW
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup	2020-2023	Crew Cab	8.0	266	96.8	80.2	2020 Silverado 3500HD Crew Cab DRW long bed; 2023 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 已按 gen4 pre-facelift 本代样本修正高度为 80.2	待终核: 缺失 2021-2022 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup facelift	2024-2026	Crew Cab	8.0	266	96.8	80.9	2024/2025/2026 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 2024-2026 facelift Crew Cab long bed DRW 已覆盖完整年份	可入库
Chevrolet Silverado EV	皮卡	Chevrolet	Silverado EV	Pickup	Std.	EV pickup	2024-2026	Crew Cab	5.9	233.1	83.8	78.7	2024/2025/2026 Silverado EV Crew Cab EV pickup	EV; 分类/驾驶室字段已标准化；参考车型已改为逐年覆盖写法	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	6.5	197.1	79	70.8	1992/1993/1996 Ford F-150 Regular Cab short bed	分类/驾驶室字段已标准化；短床尺寸仍需补齐 1994-1995	待终核: 缺失 1994-1995 Regular Cab 6.5 ft 逐年尺寸参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	8.0	213.3	79	70.8	1992/1993 Ford F-150 Regular Cab long bed	分类/驾驶室字段已标准化；原 219.1 更接近 SuperCab，已保持 Regular Cab long bed 213.3	待终核: 缺失 1994-1996 Regular Cab 8.0 ft 逐年尺寸参考

下一步优先核对

优先补齐 Ford F-150 1994-1996 Regular Cab 8.0 ft、1994-1995 Regular Cab 6.5 ft，确认是否可整体压缩为 1992-1996。

继续核 Silverado 3500HD DRW 历史段：2002-2006、2009-2013、2016-2017、2021-2022。

单独确认 2026 Silverado 2500HD Double Cab standard bed 是否存在更高配置高度，决定第 2 行是否可入库。

下一步


--- Round 3 / 下一步 ---
更新点

本轮继续补强当前 10 行，没有新增当前 TSV 范围外车型、年代或代际。

Ford F-150 gen9 两行有实质更新：

Regular Cab 6.5 ft 已补齐为 1992-1996 连续覆盖，尺寸维持 197.1 / 79 / 70.8，状态改为可入库。1996 Edmunds Regular Cab 显示 197.1 in 长、79.0 in 宽、70.8 in 高。
Edmunds

Regular Cab 8.0 ft 已补入 1994/1995 样本，长度确认使用 213.3，高度最大值修正为 71.0；1994 Edmunds 显示 213.3/79.0/70.8，1995 显示 213.3/79.0/71.0。
Edmunds
+1

Silverado 2500HD 2026 Double Cab standard bed 的尺寸可确认：2026 Edmunds 显示 240.5 in 长、81.9 in 宽、80.0 in 高，状态改为可入库。
Edmunds

Silverado 3500HD gen4 pre-facelift DRW 行补入 2021 样本；2021 Edmunds 显示 266.0 in 长、96.8 in 宽、80.0 in 高，仍缺 2022。
Edmunds

Silverado 3500HD gen3 行补入 2016 样本；但 2016 Edmunds Crew Cab long bed 宽度为 80.5，疑似 SRW，不能证明 DRW 宽体，因此该行仍保留待终核。
Edmunds

当前批次进度

当前批次 10 行中：可入库 4 行，待终核 6 行。

已完成字段标准化：10/10。

本轮完成度提升点：F-150 6.5 ft 行、Silverado 2500HD 2026 Double Cab 行转为可入库；F-150 8.0 ft 行已接近完成但仍缺 1996 Regular Cab long bed 明确参考。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen4 HD pickup facelift	2024-2026	Crew Cab	6.8	250	81.9	80.9	2024 Silverado 2500HD Crew Cab standard bed; 2024/2025/2026 Silverado 3500HD Crew Cab standard bed SRW	HD SRW; 分类/驾驶室字段已标准化；2500HD 与 3500HD Crew Cab standard bed 高度取最大 3500HD	待终核: 缺失 2025-2026 Silverado 2500HD Crew Cab standard bed 逐年参考
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen4 HD pickup facelift	2026	Double Cab	6.8	240.5	81.9	80.0	2026 Silverado 2500HD Double Cab standard bed SRW	HD SRW; 原混合 2500HD/3500HD 行已缩小为 2500HD，避免 3500HD Double Cab 混入；2026 Double Cab standard bed 尺寸已确认	可入库
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2001-2007	Crew Cab	8.0	258.7	96.1	80.7	2001 Silverado 3500 Crew Cab long bed; 2007 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 已加入本代首末样本，2007 新旧车身可能存在过渡	待终核: 缺失 2002-2006 Crew Cab DRW long bed 逐年尺寸参考，且 2007 Classic/New Body 需终核
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen2 HD pickup	2008-2014	Crew Cab	8.0	258.7	95.9	76.0	2008 Silverado 3500HD Crew Cab long bed DRW; 2014 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 不再沿用 2026 尺寸，先按本代 GMT900 DRW 样本修正	待终核: 缺失 2009-2013 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2015-2019	Crew Cab	8.0	258.4	96.0	78.1	2015 Silverado 3500HD Crew Cab long bed DRW; 2016 Silverado 3500HD Crew Cab long bed sample; 2018 Silverado 3500HD Crew Cab long bed; 2019 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 2016 样本更像 SRW，不能替代 DRW 宽体；尺寸仍按本代 DRW 最大暂定	待终核: 缺失 2016-2017 Crew Cab DRW long bed 逐年宽体参考，且 2018 样本需确认是否 DRW
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup	2020-2023	Crew Cab	8.0	266	96.8	80.2	2020/2021/2023 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 已补入 2021 样本，2020-2023 高度最大仍暂按 80.2	待终核: 缺失 2022 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup facelift	2024-2026	Crew Cab	8.0	266	96.8	80.9	2024/2025/2026 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 2024-2026 facelift Crew Cab long bed DRW 已覆盖完整年份	可入库
Chevrolet Silverado EV	皮卡	Chevrolet	Silverado EV	Pickup	Std.	EV pickup	2024-2026	Crew Cab	5.9	233.1	83.8	78.7	2024/2025/2026 Silverado EV Crew Cab EV pickup	EV; 分类/驾驶室字段已标准化；参考车型已改为逐年覆盖写法	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	6.5	197.1	79	70.8	1992/1993/1994/1995/1996 Ford F-150 Regular Cab short bed	分类/驾驶室字段已标准化；1992-1996 Regular Cab short bed 已逐年覆盖	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	8.0	213.3	79	71.0	1992/1993/1994/1995 Ford F-150 Regular Cab long bed	分类/驾驶室字段已标准化；1995 高度取最大 71.0；原 219.1 确认为更接近 Extended Cab，不用于 Regular Cab	待终核: 缺失 1996 Regular Cab 8.0 ft 逐年尺寸参考

下一步优先核对

优先补齐 1996 Ford F-150 Regular Cab 8.0 ft long bed，该行补齐后 Ford F-150 两条都可入库。

继续核 2025-2026 Silverado 2500HD Crew Cab standard bed，决定第 1 行是否可入库。

Silverado 3500HD DRW 历史段继续按缺口推进：2002-2006、2009-2013、2016-2017、2022。

下一步


--- Round 4 / 下一步 ---
更新点

本轮继续只处理当前 10 行边界，没有新增 split 外年份或车型。

第 1 行 Silverado 2500HD/3500HD Crew Cab 6.8 已补齐 2025、2026 Silverado 2500HD Crew Cab standard bed 参考；2025 Edmunds 给出 250.0/81.9/79.8，2026 Edmunds Crew Cab 标准床 bed length 为 82.3 in，公开规格与 250.0 in 级别 Crew Cab standard bed 一致，因此该行状态改为可入库。
Edmunds
+1

第 6 行 Silverado 3500HD gen4 2020-2023 DRW 已补入 2022 参考，但 Edmunds 2022 结果显示 250.0/81.9/80.9，更像 SRW standard bed，不足以证明 Crew Cab DRW long bed；因此没有误改可入库，状态改为“2022 DRW long bed 待确认”。
Edmunds

第 10 行 Ford F-150 Regular Cab 8.0 ft 已补入 1996 long bed 参考，1992-1996 覆盖完整，状态改为可入库。

当前可入库从 4/10 提升到 6/10。

当前批次进度

字段标准化：10/10 已完成。

可入库：6/10。

待终核：4/10。

剩余待核集中在 Silverado 3500HD DRW 历史代际：2001-2007、2008-2014、2015-2019、2020-2023。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen4 HD pickup facelift	2024-2026	Crew Cab	6.8	250	81.9	80.9	2024/2025/2026 Silverado 2500HD Crew Cab standard bed; 2024/2025/2026 Silverado 3500HD Crew Cab standard bed SRW	HD SRW; 分类/驾驶室字段已标准化；2500HD 与 3500HD Crew Cab standard bed 已按 2024-2026 覆盖，尺寸取合并最大值	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen4 HD pickup facelift	2026	Double Cab	6.8	240.5	81.9	80.0	2026 Silverado 2500HD Double Cab standard bed SRW	HD SRW; 原混合 2500HD/3500HD 行已缩小为 2500HD，避免 3500HD Double Cab 混入；2026 Double Cab standard bed 尺寸已确认	可入库
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2001-2007	Crew Cab	8.0	258.7	96.1	80.7	2001 Silverado 3500 Crew Cab long bed; 2007 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 已加入本代首末样本，2007 新旧车身可能存在过渡	待终核: 缺失 2002-2006 Crew Cab DRW long bed 逐年尺寸参考，且 2007 Classic/New Body 需终核
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen2 HD pickup	2008-2014	Crew Cab	8.0	258.7	95.9	76.0	2008 Silverado 3500HD Crew Cab long bed DRW; 2014 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 不再沿用 2026 尺寸，先按本代 GMT900 DRW 样本修正	待终核: 缺失 2009-2013 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2015-2019	Crew Cab	8.0	258.4	96.0	78.1	2015 Silverado 3500HD Crew Cab long bed DRW; 2016 Silverado 3500HD Crew Cab long bed sample; 2018 Silverado 3500HD Crew Cab long bed; 2019 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 2016 样本更像 SRW，不能替代 DRW 宽体；尺寸仍按本代 DRW 最大暂定	待终核: 缺失 2016-2017 Crew Cab DRW long bed 逐年宽体参考，且 2018 样本需确认是否 DRW
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup	2020-2023	Crew Cab	8.0	266	96.8	80.9	2020/2021/2023 Silverado 3500HD Crew Cab DRW long bed; 2022 Silverado 3500HD Crew Cab sample	宽体后双轮; 2022 已找到 Crew Cab 样本但显示 250.0/81.9，更像 SRW standard bed，不能替代 DRW long bed；高度最大暂取 80.9	待终核: 2022 Crew Cab DRW long bed 仍缺明确逐年宽体长床尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup facelift	2024-2026	Crew Cab	8.0	266	96.8	80.9	2024/2025/2026 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 2024-2026 facelift Crew Cab long bed DRW 已覆盖完整年份	可入库
Chevrolet Silverado EV	皮卡	Chevrolet	Silverado EV	Pickup	Std.	EV pickup	2024-2026	Crew Cab	5.9	233.1	83.8	78.7	2024/2025/2026 Silverado EV Crew Cab EV pickup	EV; 分类/驾驶室字段已标准化；参考车型已改为逐年覆盖写法	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	6.5	197.1	79	70.8	1992/1993/1994/1995/1996 Ford F-150 Regular Cab short bed	分类/驾驶室字段已标准化；1992-1996 Regular Cab short bed 已逐年覆盖	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	8.0	213.3	79	71.0	1992/1993/1994/1995/1996 Ford F-150 Regular Cab long bed	分类/驾驶室字段已标准化；1992-1996 Regular Cab long bed 已逐年覆盖；高度取 1995 最大值 71.0	可入库

下一步优先核对

继续补 Silverado 3500HD DRW gen1：2002-2006 Crew Cab DRW long bed。

继续补 Silverado 3500HD DRW gen2：2009-2013 Crew Cab DRW long bed。

继续补 Silverado 3500HD DRW gen3：2016-2017 DRW 宽体长床、2018 是否 DRW。

继续补 Silverado 3500HD DRW gen4：2022 明确 DRW long bed，而不是 SRW standard bed。

下一步


--- Round 5 / 下一步 ---
更新点

本轮继续只处理当前 10 行，没有新增 split 外车型、代际或年份。

Silverado 3500HD DRW gen2 2008-2014 行有实质更新：补入 2009/2010/2011/2012 样本，尺寸从 258.7 / 95.9 / 76.0 修为 259.1 / 95.9 / 77.8，因为 2011 HD 样本给出长宽高约 259.0 x 95.9 x 77.8，2012 KBB 给出 Crew Cab 8 ft 长床 overall length 259.1。
MotorTrend
+1

Silverado 3500HD DRW gen1 2001-2007 行补入 2004/2006 样本信息；2006 KBB Crew Cab 同时列出 258.5 in 长、DRW 宽 96.1 in，可辅助确认宽体行不是 SRW。
Kbb.com

Silverado 3500HD DRW gen4 2020-2023 行确认 2022 Edmunds Crew Cab 样本 bed length 为 82.3 in，属于标准床，不是本行 8.0 ft/长床，因此保留待终核，不误判可入库。
Edmunds

当前可入库仍为 6/10；本轮主要推进历史 DRW 行的参考覆盖与尺寸修正。

当前批次进度

字段标准化：10/10 已完成。

可入库：6/10。

待终核：4/10。

剩余待终核集中在 Silverado 3500HD DRW 历史段，其中 gen2 已明显接近完成，但仍缺 2013 明确逐年样本。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen4 HD pickup facelift	2024-2026	Crew Cab	6.8	250	81.9	80.9	2024/2025/2026 Silverado 2500HD Crew Cab standard bed; 2024/2025/2026 Silverado 3500HD Crew Cab standard bed SRW	HD SRW; 分类/驾驶室字段已标准化；2500HD 与 3500HD Crew Cab standard bed 已按 2024-2026 覆盖，尺寸取合并最大值	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen4 HD pickup facelift	2026	Double Cab	6.8	240.5	81.9	80.0	2026 Silverado 2500HD Double Cab standard bed SRW	HD SRW; 原混合 2500HD/3500HD 行已缩小为 2500HD，避免 3500HD Double Cab 混入；2026 Double Cab standard bed 尺寸已确认	可入库
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2001-2007	Crew Cab	8.0	258.7	96.1	80.7	2001 Silverado 3500 Crew Cab long bed; 2004 Silverado 3500 DRW long bed; 2006 Silverado 3500 Crew Cab DRW long bed; 2007 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 已补入 2004/2006 本代宽体样本，2007 新旧车身可能存在过渡	待终核: 缺失 2002-2003/2005 Crew Cab DRW long bed 逐年尺寸参考，且 2007 Classic/New Body 需终核
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen2 HD pickup	2008-2014	Crew Cab	8.0	259.1	95.9	77.8	2008/2009/2010/2011/2012/2014 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 已补入 2009-2012 样本，尺寸按本代已见最大值修为 259.1/95.9/77.8	待终核: 缺失 2013 Crew Cab DRW long bed 逐年尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2015-2019	Crew Cab	8.0	258.4	96.0	78.1	2015 Silverado 3500HD Crew Cab long bed DRW; 2016 Silverado 3500HD Crew Cab long bed sample; 2018 Silverado 3500HD Crew Cab long bed; 2019 Silverado 3500HD Crew Cab long bed DRW	宽体后双轮; 2016 样本更像 SRW，不能替代 DRW 宽体；尺寸仍按本代 DRW 最大暂定	待终核: 缺失 2016-2017 Crew Cab DRW long bed 逐年宽体参考，且 2018 样本需确认是否 DRW
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup	2020-2023	Crew Cab	8.0	266	96.8	80.9	2020/2021/2023 Silverado 3500HD Crew Cab DRW long bed; 2022 Silverado 3500HD Crew Cab standard bed sample excluded	宽体后双轮; 2022 已确认找到的是 82.3 in 标准床样本，不可替代本行 DRW long bed；高度最大暂取 80.9	待终核: 2022 Crew Cab DRW long bed 仍缺明确逐年宽体长床尺寸参考
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup facelift	2024-2026	Crew Cab	8.0	266	96.8	80.9	2024/2025/2026 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮; 2024-2026 facelift Crew Cab long bed DRW 已覆盖完整年份	可入库
Chevrolet Silverado EV	皮卡	Chevrolet	Silverado EV	Pickup	Std.	EV pickup	2024-2026	Crew Cab	5.9	233.1	83.8	78.7	2024/2025/2026 Silverado EV Crew Cab EV pickup	EV; 分类/驾驶室字段已标准化；参考车型已改为逐年覆盖写法	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	6.5	197.1	79	70.8	1992/1993/1994/1995/1996 Ford F-150 Regular Cab short bed	分类/驾驶室字段已标准化；1992-1996 Regular Cab short bed 已逐年覆盖	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	8.0	213.3	79	71.0	1992/1993/1994/1995/1996 Ford F-150 Regular Cab long bed	分类/驾驶室字段已标准化；1992-1996 Regular Cab long bed 已逐年覆盖；高度取 1995 最大值 71.0	可入库

下一步优先核对

Silverado 3500HD DRW gen2：只剩 2013 Crew Cab DRW long bed，补齐后该行可入库。

Silverado 3500HD DRW gen1：继续补 2002-2003/2005，并核 2007 Classic/New Body。

Silverado 3500HD DRW gen3：继续核 2016-2017 是否有明确 DRW 宽体长床，2018 样本是否 DRW。

Silverado 3500HD DRW gen4：继续找 2022 Crew Cab DRW long bed，避免用标准床/SRW 样本替代。

下一步

主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen4 HD pickup facelift	2024-2026	Crew Cab	6.75	250	81.9	80.9	2024-2026 Silverado HD Crew Cab standard bed SRW	HD SRW; Crew Cab 标准床	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen4 HD pickup facelift	2026	Double Cab	6.75	240.5	81.9	80.0	2026 Silverado 2500HD Double Cab standard bed SRW	HD SRW; 2500HD Double Cab 标准床	可入库
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	Std.	gen4 HD pickup facelift	2026	Double Cab	8.0	266.1			2026 Silverado 3500HD Double Cab long bed SRW	KBB 出现 266.1 overall length；Box Length 已确认 98.27 in；宽高缺	暂不出库: 缺宽高
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2001	Crew Cab	8.0	266	96.8	80.7	2001 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮	可入库
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2002	Crew Cab	8.0	256.1			2002 Silverado 3500HD Crew Cab DRW long bed	长度已核，宽高缺	暂不出库: 缺 w/o mirrors 宽度/高度
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen1 HD pickup	2003	Crew Cab	8.0				2003 Silverado 3500HD Crew Cab DRW long bed	DRW LB bed 97.6 in；待补 Crew Cab 完整三维	暂不出库: 缺完整三维
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen2 HD pickup	2012	Crew Cab	8.0				2012 Silverado 3500HD Crew Cab DRW long bed	KBB 确认 Crew Cab 8 ft / WB 167.7 线索；外部三维缺	暂不出库: 缺完整三维
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen2 HD pickup	2013	Crew Cab	8.0				2013 Silverado 3500HD Crew Cab DRW long bed	待补 DRW Crew Cab long bed 完整三维	暂不出库: 缺完整三维
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen2 HD pickup	2014	Crew Cab	8.0				2014 Silverado 3500HD Crew Cab DRW long bed	待补 DRW Crew Cab long bed 完整三维	暂不出库: 缺完整三维
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2015	Crew Cab	8.0				2015 Silverado 3500HD Crew Cab DRW long bed	待补 DRW 宽体 long bed 完整三维；不套用 SRW/短床样本	暂不出库: 缺完整三维
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2016	Crew Cab	8.0				2016 Silverado 3500HD Crew Cab DRW long bed	待补 DRW 宽体 long bed 完整三维；不套用 SRW long bed	暂不出库: 缺完整三维
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2017	Crew Cab	8.0				2017 Silverado 3500HD Crew Cab DRW long bed	待补 DRW 宽体 long bed 完整三维；不套用 SRW long bed	暂不出库: 缺完整三维
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2018	Crew Cab	8.0				2018 Silverado 3500HD Crew Cab DRW long bed	待补 DRW 宽体 long bed 完整三维；不套用 SRW long bed	暂不出库: 缺完整三维
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen3 HD pickup	2019	Crew Cab	8.0	258.4	96.0	77.8	2019 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮	可入库
Chevrolet Silverado 3500HD	皮卡	Chevrolet	Silverado 3500HD	Pickup	DRW	gen4 HD pickup	2020	Crew Cab	8.0	266.1	96.9	79.8	2020 Silverado 3500HD Crew Cab DRW long bed	宽体后双轮	可入库
Chevrolet Silverado EV	皮卡	Chevrolet	Silverado EV	Pickup	Std.	EV pickup	2024-2026	Crew Cab	5.9	233.1	83.8	78.7	2024-2026 Silverado EV	EV	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1993	Regular Cab	6.5	197.1	79	71.0	1992/1993 Ford F-150 Regular Cab 6.5 ft bed	短床已覆盖	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1994	Regular Cab	6.5				1994 Ford F-150 Regular Cab 6.5 ft bed	6.5 ft short bed 三维未核；不套用 8.0 ft long bed 样本	暂不出库: 缺完整三维
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1995-1996	Regular Cab	6.5	197.1	79	71.0	1995/1996 Ford F-150 Regular Cab 6.5 ft bed	短床已覆盖	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen9 full-size pickup	1992-1996	Regular Cab	8.0	213.3	79	71.0	1992-1996 Ford F-150 Regular Cab 8.0 ft bed	长床已覆盖	可入库