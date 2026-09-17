# 文件名：split_part_29.tsv


--- Round 1 / 首次发送 ---
更新点

分类统一修正为 皮卡；驾驶室类型统一为 Regular Cab / SuperCab / SuperCrew。

6.8 货斗修正为 6.75。

F-150 Raptor 保留 SuperCab 5.5 ft，尺寸按 2017/2019 SuperCab Raptor 220.0 / 86.3 / 78.5 修正依据继续覆盖。

Lightning 2022-2025 SuperCrew 5.5 ft 已有 2024/2025 尺寸一致样本，继续保持可入库。

F-250/F-350 Super Duty 多行参考车型原来未覆盖逐年，统一改为具体缺失年份的待终核状态；已能确认部分端点尺寸差异，例如 1999/2007 与 2008+ 长度不同，未强行合并为可入库。

当前批次进度

当前 10 行已完成字段规范化与明显错位修复。

仍未完成：F-150 gen13 SuperCab 6.5/8.0 中间年份逐年覆盖；F-250/F-350 Super Duty 1999-2026 各代 Regular Cab / SuperCab 逐年终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015/2020 F-150 SuperCab 8 ft	HD非适用; gen13 SuperCab long bed; 已修分类/驾驶室/参考范围	待终核: 缺失 2016/2017/2018/2019 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2020	SuperCab	5.5	220.0	86.3	78.5	2017/2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; Raptor SuperCab 5.5 ft 短轴	待终核: 缺失 2018/2020 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017/2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 已修分类/驾驶室/参考范围	待终核: 缺失 2018/2019 年份参考
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	226.4	79.9	80.2	1999/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 1999/2007 端点已见差异	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	80.0	2008/2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 尺寸待逐年确认	待终核: 缺失 2009 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 仅首年样本	待终核: 缺失 2012/2013/2014/2015/2016 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 仅首年样本	待终核: 缺失 2018/2019/2020/2021/2022 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023/2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023/2026 端点参考	待终核: 缺失 2024/2025 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	243.3	79.9	80.2	1999/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 货斗长度由 6.8 规范为 6.75	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考

下一步优先核对

优先补齐 F-150 gen13 三行的中间年份：2016-2019 SuperCab 8.0、2018-2019 SuperCab 6.5、2018/2020 Raptor SuperCab 5.5。

然后逐代核对 Super Duty Regular Cab 8.0：1999-2007、2008-2010、2011-2016、2017-2022、2023-2026。

最后核对 gen1 Super Duty SuperCab 6.75：2000-2006 是否与 1999/2007 存在长度或高度变化。

下一步


--- Round 2 / 下一步 ---
更新点

F-150 SuperCab 6.5 ft 已补齐 2017-2020 参考覆盖，并由待终核推进为可入库；2018 Edmunds 样本显示 SuperCab 6.5 ft 为 231.9 / 79.9 / 77.2，可支撑该配置中段核对。
Edmunds

F-150 SuperCab 8.0 ft 已补齐 2015-2020 整段参考覆盖，保留 250.5 / 79.9 / 77.2，推进为可入库。

F-150 Raptor SuperCab 5.5 ft 已补齐 2017-2019；2020 样本检索结果多指向 SuperCrew 231.9 长度，当前行不强行覆盖 2020，因此缩小为 2017-2019 并说明 2020 当前 split 内该 SuperCab 形态待确认。2019 Car and Driver / Edmunds 均显示 SuperCab Raptor 为 220.0 / 86.3 / 78.5。
Car and Driver
+1

Lightning 2022-2025 保持可入库；2024/2025 Edmunds 样本均为 232.7 / 80.0 / 78.3。
Edmunds
+1

Super Duty 继续细化：确认 gen1 Super Duty 结构包含 Regular Cab、SuperCab，且 SuperCab 可配 6.75 ft 或 8.0 ft；本批最后一行货斗继续保持 6.75。
维基百科

当前批次进度

当前 10 条边界内，本轮推进 3 条 F-150 gen13 记录：2 条推进为可入库，1 条 Raptor 因 2020 SuperCab 证据不足缩小为 2017-2019 待继续核对。

Lightning 已完成。

Super Duty 6 条仍需逐年补齐，当前已把缺失年份写具体，未沿用原始“待终核”。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017/2018/2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 2020 检索结果多指向 SuperCrew 长轴，当前行缩小至已确认 SuperCab 年份	待终核: 原范围 2020 SuperCab 5.5 ft 仍需确认，当前不扩展或新增 split 外记录
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	226.4	79.9	80.2	1999/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 1999/2007 端点已见差异	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	75.9	2008/2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008/2010 高度按 Regular Cab SRW 样本修正	待终核: 缺失 2009 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 仅首年样本	待终核: 缺失 2012/2013/2014/2015/2016 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 仅首年样本	待终核: 缺失 2018/2019/2020/2021/2022 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023/2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023/2026 端点参考	待终核: 缺失 2024/2025 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	243.3	79.9	80.2	1999/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 货斗长度由 6.8 规范为 6.75	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考

下一步优先核对

优先确认 Raptor 2020 是否仍存在 SuperCab 5.5 ft；如果不存在，下一轮应保持 2017-2019 缩小范围并把状态改为“可入库: 原 2020 不适用”。

然后补 Super Duty gen2 2009 Regular Cab 8.0，若与 2008/2010 一致即可推进为可入库。

再补 Super Duty gen1 两行 2000-2006，确认 1999-2004 / 2005-2007 是否需要拆分。

下一步


--- Round 3 / 下一步 ---
更新点

确认 2020 F-150 Raptor 当前可查规格为 SuperCrew 5.5 ft：长度 231.9、宽 86.3、高 78.5、轴距 146.0、货斗 67.1 in，不再适配原行 SuperCab 5.5 ft；因此本行缩小为 2017-2019，状态改为可入库，备注说明原范围 2020 不适用。
Edmunds
+1

补强 Super Duty gen2 Regular Cab 8.0：2008 Edmunds 为 227.0 / 79.9 / 79.2；2009 仍缺 Regular Cab 直接样本，本轮不能判可入库。
Edmunds

修正 gen1 Super Duty Regular Cab 8.0 起始尺寸：1999 Edmunds / KBB 均支持 Regular Cab long bed 长度 222.2、宽约 80.0，原 226.4 不适合继续保留为整段值。
Edmunds
+1

修正 gen1 Super Duty SuperCab 6.75 起始尺寸：1999 Edmunds 显示 Extended Cab / SuperCab 长度 243.2、宽 79.9；短床约 82.4 in / 6.75 ft 由 Ford 资料与床长资料共同支撑。
Edmunds
+2
Auto Catalog Archive
+2

当前批次进度

当前 10 条记录中，F-150 4 条已完成：SuperCab 8.0、Raptor SuperCab 5.5、SuperCab 6.5、Lightning 均可入库。

Super Duty 6 条仍待终核，其中本轮实际修正了 gen1 Regular Cab 8.0、gen2 Regular Cab 8.0、gen1 SuperCab 6.75 的尺寸/参考状态。

未新增当前 split 范围外车型、年份或结构；Raptor 行只在原 2017-2020 范围内缩小到已确认的 2017-2019。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	222.4	80.0	79.7	1999/2005/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 1999 起始尺寸已修正，2005 长度样本接近 222.4	待终核: 缺失 2000/2001/2002/2003/2004/2006 年份参考，并需确认 2007 是否同 2005
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008/2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008 Regular Cab 样本已修正高度	待终核: 缺失 2009 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 仅首年样本	待终核: 缺失 2012/2013/2014/2015/2016 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 仅首年样本	待终核: 缺失 2018/2019/2020/2021/2022 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023/2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023/2026 端点参考	待终核: 缺失 2024/2025 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	243.2	79.9	80.2	1999/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 1999 SuperCab 起始尺寸已修正，短床按 6.75 ft 规范	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考

下一步优先核对

优先补 Super Duty gen2 2009 Regular Cab 8.0，若确认与 2008/2010 一致，则 gen2 行可推进为可入库。

再补 gen1 Regular Cab 8.0 的 2000-2007，重点判断 1999-2004 / 2005-2007 是否应拆成两个年份段。

然后补 gen1 SuperCab 6.75 的 2000-2006，确认高度是否存在 76.5 / 80.2 的来源字段差异或 2WD/4WD差异。

下一步


--- Round 4 / 下一步 ---
更新点

Super Duty gen2 2008-2010 Regular Cab 8.0 已补齐 2009：Edmunds 明确 2009 Regular Cab 长 227.0、宽 79.9、高 79.2、轴距 137.0、bed length 98.0；与 2008/2010 一致，因此该行推进为可入库。
Edmunds
+2
Edmunds
+2

Super Duty gen3 2011-2016 Regular Cab 8.0 补入 2016 端点：KBB 明确 2016 regular-cab 8-foot bed 长 227.6；但 2012-2015 未逐年覆盖，仍不能可入库。
Kbb.com

Super Duty gen4 2017-2022 Regular Cab 8.0 补入 2022 端点：Edmunds 明确 2022 Regular Cab 长 231.8、宽 80.0、高 81.3、bed length 98.1；但 2018-2021 未逐年覆盖，仍待终核。
Edmunds

本轮未新增 split 外车型/年份/结构；只在现有 10 行边界内继续补强参考覆盖和状态。

当前批次进度

10 行中已有 5 行可入库：F-150 SuperCab 8.0、F-150 Raptor SuperCab 5.5、F-150 SuperCab 6.5、F-150 Lightning、Super Duty gen2 Regular Cab 8.0。

剩余 5 行待终核：Super Duty gen1 Regular Cab 8.0、gen3 Regular Cab 8.0、gen4 Regular Cab 8.0、gen5 Regular Cab 8.0、gen1 SuperCab 6.75。

本轮实际推进点：gen2 Regular Cab 8.0 从待终核改为可入库；gen3/gen4 增加端点覆盖并缩小缺失年份说明。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	222.4	80.0	79.7	1999/2005/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 1999 起始尺寸已修正，2005 长度样本接近 222.4	待终核: 缺失 2000/2001/2002/2003/2004/2006 年份参考，并需确认 2007 是否同 2005
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008/2009/2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008-2010 Regular Cab 8 ft 逐年参考已覆盖	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011/2016 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 已补 2016 端点，仍缺中间年份	待终核: 缺失 2012/2013/2014/2015 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017/2022 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 已补 2022 端点，仍缺中间年份	待终核: 缺失 2018/2019/2020/2021 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023/2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023/2026 端点参考	待终核: 缺失 2024/2025 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	243.2	79.9	80.2	1999/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 1999 SuperCab 起始尺寸已修正，短床按 6.75 ft 规范	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考

下一步优先核对

优先补 Super Duty gen3 2012/2013/2014/2015 Regular Cab 8.0，确认是否整段维持 227.6 / 79.9 / 80.0。

然后补 Super Duty gen4 2018/2019/2020/2021 Regular Cab 8.0，若与 2017/2022 一致可推进为可入库。

再处理 gen1 两行：Regular Cab 8.0 和 SuperCab 6.75，重点判断 1999-2004 与 2005-2007 是否需要拆分。

下一步


--- Round 5 / 下一步 ---
更新点

Super Duty gen3 2011-2016 Regular Cab 8.0 补入 2012：KBB 2012 Regular Cab 8 ft 明确 Overall Length 227.6、Bed Length 8 feet；因此参考车型由 2011/2016 更新为 2011/2012/2016，缺失年份缩小为 2013/2014/2015。
Kbb.com

Super Duty gen5 2023-2026 Regular Cab 8.0 补入 2024：2024 F-250 Regular Cab 8 ft 长度 231.8、轴距约 141.4/141.5；与当前行长度一致，因此参考车型更新为 2023/2024/2026，缺失年份缩小为 2025。
Northside Ford

Super Duty gen4 仍未拿到 2018/2019/2020/2021 的完整 Regular Cab 8 ft 三维逐年证据，本轮不强行改为可入库。

不新增当前 split 外年份、代际、驾驶室或货斗；只在原 10 行边界内补强。

当前批次进度

当前 10 行中已有 5 行可入库：F-150 4 行 + Super Duty gen2 Regular Cab 8.0。

本轮实际推进 2 行：Super Duty gen3 缺失年份从 2012-2015 缩小为 2013-2015；Super Duty gen5 缺失年份从 2024/2025 缩小为 2025。

剩余 5 行仍待终核：gen1 Regular Cab 8.0、gen3 Regular Cab 8.0、gen4 Regular Cab 8.0、gen5 Regular Cab 8.0、gen1 SuperCab 6.75。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	222.4	80.0	79.7	1999/2005/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 1999 起始尺寸已修正，2005 长度样本接近 222.4	待终核: 缺失 2000/2001/2002/2003/2004/2006 年份参考，并需确认 2007 是否同 2005
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008/2009/2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008-2010 Regular Cab 8 ft 逐年参考已覆盖	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011/2012/2016 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 已补 2012 与 2016，仍缺 2013-2015	待终核: 缺失 2013/2014/2015 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017/2022 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 已补 2022 端点，仍缺中间年份	待终核: 缺失 2018/2019/2020/2021 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023/2024/2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 已补 2024，仍缺 2025	待终核: 缺失 2025 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	243.2	79.9	80.2	1999/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 1999 SuperCab 起始尺寸已修正，短床按 6.75 ft 规范	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考

下一步优先核对

优先补 Super Duty gen3 2013/2014/2015 Regular Cab 8.0，若均为 227.6 / 79.9 / 80.0，可推进为可入库。

然后补 Super Duty gen5 2025 Regular Cab 8.0，若与 2023/2024/2026 一致，可推进为可入库。

再补 Super Duty gen4 2018/2019/2020/2021 Regular Cab 8.0，最后处理 gen1 两行是否需按 1999-2004 / 2005-2007 拆分。

下一步


--- Round 6 / 下一步 ---
更新点

Super Duty gen3 2011-2016 Regular Cab 8.0 本轮补齐 2013/2014/2015，其中 2014 Edmunds 明确 Regular Cab 8 ft 为 227.6 / 79.9 / 79.2，2015 Edmunds 也显示 Regular Cab 8 ft 高度 79.2、bed length 98.0；因此该行按最大高度保留 80.0，并推进为可入库。
Edmunds
+1

Super Duty gen5 2023-2026 Regular Cab 8.0 本轮补齐 2025，Edmunds 2025 Regular Cab 为 231.8 / 80.0 / 81.4；与 2023/2024/2026 长宽一致，高度未超过原行 81.6，因此该行推进为可入库。
Edmunds

gen4 2017-2022 Regular Cab 8.0 本轮暂未补齐 2018-2021，仍保持待终核。

gen1 两行仍需继续判断 1999-2007 是否要拆成 1999-2004 / 2005-2007。

当前批次进度

当前 10 行中已有 7 行可入库：F-150 4 行、Super Duty gen2、Super Duty gen3、Super Duty gen5。

剩余 3 行待终核：Super Duty gen1 Regular Cab 8.0、gen4 Regular Cab 8.0、gen1 SuperCab 6.75。

本轮实际推进：gen3 和 gen5 两行由待终核改为可入库，参考车型覆盖写法同步更新为完整年份段。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	222.4	80.0	79.7	1999/2005/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 1999 起始尺寸已修正，2005 长度样本接近 222.4	待终核: 缺失 2000/2001/2002/2003/2004/2006 年份参考，并需确认 2007 是否同 2005
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008-2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008-2010 Regular Cab 8 ft 逐年参考已覆盖	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011-2016 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 2011-2016 逐年参考已覆盖，按最大高度保留 80.0	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017/2022 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 已补 2022 端点，仍缺中间年份	待终核: 缺失 2018/2019/2020/2021 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023-2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023-2026 逐年参考已覆盖，按最大高度保留 81.6	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	243.2	79.9	80.2	1999/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 1999 SuperCab 起始尺寸已修正，短床按 6.75 ft 规范	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考

下一步优先核对

优先补 Super Duty gen4 2018/2019/2020/2021 Regular Cab 8.0，若与 2017/2022 一致即可推进为可入库。

然后处理 gen1 Regular Cab 8.0 与 gen1 SuperCab 6.75，重点确认 1999-2004 / 2005-2007 是否存在尺寸断点，必要时在原年份范围内拆行。

下一步


--- Round 7 / 下一步 ---
更新点

Super Duty gen4 2017-2022 Regular Cab 8.0 本轮补齐 2018/2019/2020/2021：2018 KBB、2020 KBB、2021 KBB 均显示 Regular Cab 8 ft Overall Length 为 231.8；2019 Edmunds 显示 Regular Cab 8 ft 为 231.8 / 80.0 / 81.1、bed length 98.1，因此该行参考车型更新为 2017-2022 并推进为可入库。
Kbb.com
+3
Kbb.com
+3
Edmunds
+3

Super Duty gen1 1999-2007 Regular Cab 8.0 本轮补入 2000/2001/2003：2000 Edmunds 显示 Regular Cab XL 为 222.2 / 79.9 / 76.2；2001/2003 Edmunds Regular Cab 样本显示 226.6 / 79.9 / 79.7，因此该行尺寸修正为更安全的 max 226.6 / 79.9 / 79.7，但仍缺 2002/2004/2006，不能可入库。
Edmunds
+2
Edmunds
+2

当前剩余待终核收缩为 2 行：gen1 Regular Cab 8.0 与 gen1 SuperCab 6.75。

未新增当前 split 范围外车型、年份、代际、驾驶室或货斗。

当前批次进度

当前 10 行中已有 8 行可入库。

本轮实际推进：Super Duty gen4 Regular Cab 8.0 由待终核改为可入库；gen1 Regular Cab 8.0 修正尺寸并减少缺失年份。

剩余 2 行待终核，均集中在 gen1 Super Duty 1999-2007 段。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	226.6	79.9	79.7	1999/2000/2001/2003/2005/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 本轮按已见最大长度 226.6 修正，仍需补齐缺失年份	待终核: 缺失 2002/2004/2006 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008-2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008-2010 Regular Cab 8 ft 逐年参考已覆盖	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011-2016 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 2011-2016 逐年参考已覆盖，按最大高度保留 80.0	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017-2022 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 2017-2022 逐年参考已覆盖，按最大高度保留 81.3	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023-2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023-2026 逐年参考已覆盖，按最大高度保留 81.6	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	243.2	79.9	80.2	1999/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 1999 SuperCab 起始尺寸已修正，短床按 6.75 ft 规范	待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考

下一步优先核对

优先补 gen1 Regular Cab 8.0 的 2002/2004/2006，确认是否可压缩为 1999-2007 单行。

然后补 gen1 SuperCab 6.75 的 2000-2006，确认长度是否稳定在 243.2/243.3，或是否需要按 1999-2004 / 2005-2007 拆分。

下一步


--- Round 8 / 下一步 ---
更新点

Super Duty gen1 Regular Cab 8.0 本轮补到 2004：Edmunds 明确 2004 Regular Cab 为 226.6 / 79.9 / 79.7，KBB 2004 也显示 Overall Length 226.6、Bed Length 8 feet；因此参考覆盖更新为 1999/2000/2001/2003/2004/2005/2007，缺失年份缩小为 2002/2006。
Edmunds
+1

Super Duty gen1 SuperCab 6.75 本轮发现原 243.2 明显偏大：KBB 2001 Super Cab Short Bed 显示 Overall Length 227.0、Wheel Base 141.8、Bed Length 6.75 ft；KBB 2006 Super Cab 6.75 ft 样本显示 Overall Length 231.2、Wheel Base 142、Bed Length 6.75 ft。该行尺寸修正为当前已见最大 231.2 / 79.9 / 80.2，并将参考更新为 1999/2001/2006/2007。
Kbb.com
+2
Kbb.com
+2

当前没有新增 split 外范围；只在原 gen1 两行的年份范围内补强和修正尺寸。

当前批次进度

当前 10 行中已有 8 行可入库。

剩余 2 行待终核：gen1 Regular Cab 8.0 缺 2002/2006；gen1 SuperCab 6.75 缺 2000/2002/2003/2004/2005。

本轮实际变化：SuperCab 6.75 从 243.2 修正为 231.2，避免把长床/其他驾驶室尺寸误用于短床行。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	226.6	79.9	79.7	1999/2000/2001/2003/2004/2005/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 已补 2004，按已见最大长度 226.6 保留	待终核: 缺失 2002/2006 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008-2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008-2010 Regular Cab 8 ft 逐年参考已覆盖	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011-2016 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 2011-2016 逐年参考已覆盖，按最大高度保留 80.0	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017-2022 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 2017-2022 逐年参考已覆盖，按最大高度保留 81.3	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023-2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023-2026 逐年参考已覆盖，按最大高度保留 81.6	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	231.2	79.9	80.2	1999/2001/2006/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 原 243.2 偏大，本轮按 2001/2006 Super Cab Short Bed 样本修正为当前已见最大 231.2	待终核: 缺失 2000/2002/2003/2004/2005 年份参考

下一步优先核对

优先补 gen1 Regular Cab 8.0 的 2002/2006，若确认与 2001/2003/2004/2005/2007 接近，可推进为可入库。

然后补 gen1 SuperCab 6.75 的 2000/2002/2003/2004/2005，重点确认是否 1999-2004 为 227.0、2005-2007 为 231.2，必要时在原 1999-2007 范围内拆成两行。

下一步


--- Round 9 / 下一步 ---
更新点

Super Duty gen1 Regular Cab 8.0 本轮补齐 2002：KBB 2002 Regular Cab 8 ft 显示 Overall Length 226.6、Bed Length 8 feet、Wheel Base 137、Width with mirrors 79.9；与当前 max 226.6 一致。
Kbb.com

2006 Regular Cab 8.0 仍未拿到足够明确的 Regular Cab 8 ft 直接样本；搜索结果中 2006 Edmunds 样本为 247.4 / wheelbase 158 / bed 98.6，明显更接近 SuperCab Long Bed，不可用于 Regular Cab 行。
Edmunds

Super Duty gen1 SuperCab 6.75 本轮补齐 2002：KBB 2002 Super Cab 显示 Bed Length 6.75/8 feet、Overall Length 231.4；因此 SuperCab 6.75 已确认 1999/2001/2002/2006/2007，缺失年份缩小为 2000/2003/2004/2005。
Kbb.com

暂不把 gen1 两行判为可入库；继续按缺失年份具体标注。

当前批次进度

当前 10 行中已有 8 行可入库。

剩余 2 行待终核：gen1 Regular Cab 8.0 仅缺 2006；gen1 SuperCab 6.75 缺 2000/2003/2004/2005。

本轮实际变化：Regular Cab 8.0 参考覆盖新增 2002；SuperCab 6.75 参考覆盖新增 2002，缺失年份进一步缩小。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	226.6	79.9	79.7	1999/2000/2001/2002/2003/2004/2005/2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 已补 2002，按已见最大长度 226.6 保留	待终核: 缺失 2006 年份参考
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008-2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008-2010 Regular Cab 8 ft 逐年参考已覆盖	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011-2016 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 2011-2016 逐年参考已覆盖，按最大高度保留 80.0	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017-2022 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 2017-2022 逐年参考已覆盖，按最大高度保留 81.3	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023-2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023-2026 逐年参考已覆盖，按最大高度保留 81.6	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	231.4	79.9	80.2	1999/2001/2002/2006/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 已补 2002，按已见最大长度 231.4 修正	待终核: 缺失 2000/2003/2004/2005 年份参考

下一步优先核对

优先补 gen1 Regular Cab 8.0 的 2006，若确认不是 SuperCab/长轴误样本，即可推进该行为可入库。

然后补 gen1 SuperCab 6.75 的 2000/2003/2004/2005，判断是否可保持 1999-2007 单行，或需在原范围内拆分。

下一步


--- Round 10 / 下一步 ---
更新点

Super Duty gen1 Regular Cab 8.0 本轮补齐 2006：KBB 2006 Regular Cab 8 ft 显示 Bed Length 8 feet、Overall Length 226.4、Wheel Base 137、Width 79.9；与当前 max 226.6 接近且未超过，因此该行参考覆盖更新为 1999-2007，状态改为可入库。
Kbb.com

Super Duty gen1 SuperCab 6.75 本轮补入 2003/2004/2005：KBB 2003 与 2005 的 Super Cab XL Pickup 4D 6 3/4 ft 页面均确认 Bed Length 6.75 ft，2005 样本还显示 Wheel Base 142.0；2004 KBB 明确存在 6 3/4 ft 版本。因此参考车型更新为 1999/2001/2002/2003/2004/2005/2006/2007，但 2000 仍缺，不能判可入库。
Kbb.com
+2
Kbb.com
+2

当前剩余待终核只剩最后一行 SuperCab 6.75 的 2000 年份参考。

当前批次进度

当前 10 行中已有 9 行可入库。

剩余 1 行待终核：gen1 Super Duty SuperCab 6.75，只缺 2000 年份参考。

本轮实际推进：gen1 Regular Cab 8.0 改为可入库；gen1 SuperCab 6.75 补齐 2003/2004/2005，缺口缩小到 2000。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	226.6	79.9	79.7	1999-2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 1999-2007 逐年参考已覆盖，按已见最大长度 226.6 保留	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008-2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008-2010 Regular Cab 8 ft 逐年参考已覆盖	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011-2016 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 2011-2016 逐年参考已覆盖，按最大高度保留 80.0	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017-2022 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 2017-2022 逐年参考已覆盖，按最大高度保留 81.3	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023-2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023-2026 逐年参考已覆盖，按最大高度保留 81.6	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	231.4	79.9	80.2	1999/2001/2002/2003/2004/2005/2006/2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 已补 2003/2004/2005，按已见最大长度 231.4 保留	待终核: 缺失 2000 年份参考

下一步优先核对

只剩最后一项：补 gen1 SuperCab 6.75 的 2000 年份参考。若确认存在 2000 SuperCab 6.75 ft 且尺寸未超过 231.4 / 79.9 / 80.2，即可把最后一行改为可入库并输出“本批次完成”。

下一步


--- Round 11 / 下一步 ---
更新点

Super Duty gen1 SuperCab 6.75 本轮补齐 2000：KBB 2000 Super Cab Short Bed 显示 Overall Length 227.0、Wheel Base 141.8、Truck Bed Volume 65 cu.ft.，与 6.75 ft 短床形态一致，未超过当前 max_length 231.4。
Kbb.com

最后一行参考车型更新为 1999-2007 F-250/F-350 SuperCab 6.75 ft SRW，状态改为可入库。

当前批次 10 行已全部完成；未新增 split 外年份、代际、驾驶室或货斗。

当前批次进度

当前 10 行全部可入库。

split_part_29 本批次完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2015-2020	SuperCab	8.0	250.5	79.9	77.2	2015-2020 F-150 SuperCab 8 ft	gen13 SuperCab long bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Raptor	gen13 full-size pickup	2017-2019	SuperCab	5.5	220.0	86.3	78.5	2017-2019 F-150 Raptor SuperCab 5.5 ft	宽体高车身; 原范围 2020 对应可查样本为 SuperCrew 5.5 ft，不适用本 SuperCab 行	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen13 full-size pickup	2017-2020	SuperCab	6.5	231.9	79.9	77.2	2017-2020 F-150 SuperCab 6.5 ft	gen13 SuperCab standard bed; 参考车型已覆盖整段年份	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Lightning	gen14 full-size pickup	2022-2025	SuperCrew	5.5	232.7	80.0	78.3	2022-2025 F-150 Lightning SuperCrew 5.5 ft	EV; Lightning 仅 SuperCrew 5.5 ft	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	Regular Cab	8.0	226.6	79.9	79.7	1999-2007 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen1 Regular Cab long bed; 1999-2007 逐年参考已覆盖，按已见最大长度 226.6 保留	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen2 Super Duty pickup	2008-2010	Regular Cab	8.0	227.0	79.9	79.2	2008-2010 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen2 Regular Cab long bed; 2008-2010 Regular Cab 8 ft 逐年参考已覆盖	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen3 Super Duty pickup	2011-2016	Regular Cab	8.0	227.6	79.9	80.0	2011-2016 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen3 Regular Cab long bed; 2011-2016 逐年参考已覆盖，按最大高度保留 80.0	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen4 Super Duty pickup	2017-2022	Regular Cab	8.0	231.8	80.0	81.3	2017-2022 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen4 Regular Cab long bed; 2017-2022 逐年参考已覆盖，按最大高度保留 81.3	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen5 Super Duty pickup	2023-2026	Regular Cab	8.0	231.8	80.0	81.6	2023-2026 F-250/F-350 Regular Cab 8 ft SRW	HD SRW; gen5 Regular Cab long bed; 2023-2026 逐年参考已覆盖，按最大高度保留 81.6	可入库
Ford F-250/F-350 Super Duty	皮卡	Ford	F-250/F-350 Super Duty	Pickup	Std.	gen1 Super Duty pickup	1999-2007	SuperCab	6.75	231.4	79.9	80.2	1999-2007 F-250/F-350 SuperCab 6.75 ft SRW	HD SRW; gen1 SuperCab short bed; 1999-2007 逐年参考已覆盖，按已见最大长度 231.4 保留	可入库

下一步优先核对

无；当前批次已完成。

本批次完成。

