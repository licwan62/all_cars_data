# 文件名：split_part_20.tsv


--- Round 1 / 首次发送 ---
更新点

已把 分类 从“皮卡车”统一修正为“皮卡”。

已把皮卡 驾驶室类型 从 crew/regular/extended 规范为 Crew Cab / Regular Cab / Extended Cab。

已把 Silverado 1500 标准货斗 6.6 统一为更常用的 6.5 ft。

Colorado gen3 已补强为 Crew Cab 5.0 ft，并按 2023-2026 代际统一表达；Colorado ZR2 / Trail Boss / Z71 的尺寸范围可由 Chevrolet/Edmunds/C&D/JD Power 等来源互相印证，但 Silverado 1999-2013 多行仍缺逐年完整参考，所以本轮按规则改回具体“待终核”。
Car and Driver
+4
Chevrolet 新闻中心
+4
Edmunds
+4

当前批次进度
当前 10 行已完成字段规范化；Colorado 2 行本轮可先入库，Silverado 8 行仍需逐年补齐 1999-2013 各驾驶室/货斗参考，不能沿用原“可入库”。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	6.5	227.7	78.5	73.9	1999-2006 Silverado 1500 Extended Cab standard bed		待终核: 需逐年复核 1999/2000/2001/2002/2003/2004/2005/2006 Extended Cab 6.5-ft
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999 Silverado 1500 Extended Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004-2006	Crew Cab	5.8	230.2	78.5	75.0	2004/2006 Silverado 1500 Crew Cab short bed		待终核: 缺失 2005 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.5	2007-2013 Silverado 1500 Regular Cab standard bed		待终核: 需逐年复核 2007/2008/2009/2010/2011/2012/2013 Regular Cab 6.5-ft
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007 Silverado 1500 Regular Cab long bed		待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Crew Cab	5.8	229.9	79.9	73.7	2007-2013 Silverado 1500 Crew Cab short bed		待终核: 需逐年复核 2007/2008/2009/2010/2011/2012/2013 Crew Cab 5.8-ft
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Extended Cab	6.5	230.2	79.9	73.7	2007-2013 Silverado 1500 Extended Cab standard bed		待终核: 需逐年复核 2007/2008/2009/2010/2011/2012/2013 Extended Cab 6.5-ft

下一步优先核对
优先补齐 Silverado 1500 gen1：1999-2006 Regular Cab 8.0、Extended Cab 8.0、Crew Cab 5.8 的逐年尺寸；然后补 gen2 2007-2013 各驾驶室/货斗组合，只有逐年覆盖后再恢复“可入库”。

下一步


--- Round 2 / 下一步 ---
更新点

继续补强 Silverado 1500 gen1 的 2004-2006 Crew Cab 5.8 ft：已发现 2005 Crew Cab 5.8 ft 长度为 225.9 in，低于 2004/2006 的 230.2 in；因此该行不能继续用单一参考笼统覆盖，已拆成 2004、2005、2006 三行，年份合集仍严格限定在原 2004-2006 范围内。
Edmunds
+2
Edmunds
+2

继续补强 Silverado 1500 gen1 Extended Cab 6.5 ft：已把可确认的 2001/2003/2005/2006 参考写入参考车型；但仍缺 1999/2000/2002/2004，不能标可入库。
Edmunds
+3
Kbb.com
+3
Edmunds
+3

继续补强 Silverado 1500 gen2 Crew Cab 5.8 ft：已补入 2010/2012/2013 参考，但仍缺 2007/2008/2009/2011，暂不标可入库。
Edmunds
+2
Kbb.com
+2

保持当前 split 第一条到最后一条边界，不新增 split 外年份或车型。

当前批次进度
当前批次由原 10 行拆分为 12 行。Colorado 2 行已可入库；Silverado 1500 中 2004、2005、2006 Crew Cab 5.8 ft 三个单年行已可入库；其余 Silverado 1500 行仍缺逐年完整覆盖，继续待终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	6.5	227.7	78.5	73.9	2001/2003/2005/2006 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.5	2007-2013 Silverado 1500 Regular Cab standard bed		待终核: 需逐年复核 2007/2008/2009/2010/2011/2012/2013 Regular Cab 6.5-ft
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007 Silverado 1500 Regular Cab long bed		待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Crew Cab	5.8	230.2	80.0	73.7	2010/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed		待终核: 缺失 2007/2008/2009/2011 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Extended Cab	6.5	230.2	79.9	73.9	2011 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 2007/2008/2009/2010/2012/2013 年份参考

下一步优先核对

优先补 Silverado 1500 gen1：Regular Cab 8.0 的 2000-2006、Extended Cab 8.0 的 2001-2006。

然后补 Silverado 1500 gen2：Regular Cab 6.5/8.0、Crew Cab 5.8、Extended Cab 6.5 的缺失年份。

重点确认 gen2 宽度 79.9 / 80.0 的来源差异，避免误把四舍五入差异当成结构差异。

下一步


--- Round 3 / 下一步 ---
更新点

本轮继续推进 Silverado 1500 gen2，优先把已有明确尺寸来源的单年从大区间中拆出，避免“首尾/部分年份参考”伪覆盖整段。

2013 Regular Cab 6.5 ft 已从 2007-2013 Regular Cab 6.5 中拆出为单年可入库；Edmunds 给出 2013 Regular Cab 长 205.6、宽 79.9、高 73.6、床长 78.7 in。
Edmunds

2011 Extended Cab 6.5 ft 已从 2007-2013 Extended Cab 6.5 中拆出为单年可入库；Edmunds 给出 2011 Extended Cab 长 230.2、宽 79.9、高 73.9、床长 78.7 in。
Edmunds

2005 Extended Cab 6.5 ft 已从 gen1 Extended Cab 6.5 大区间中拆出为单年可入库；Edmunds 给出 2005 Silverado 1500 长 227.7、宽 78.5、高 73.9、床长 78.6 in。
Edmunds

继续保留所有未逐年覆盖区间为具体“待终核”，未把任何缺年份行误标为可入库。

当前批次进度
当前批次由上一轮 12 行继续拆分为 16 行。Colorado 2 行可入库；Silverado 1500 已可入库单年包括 2004/2005/2006 Crew Cab 5.8、2005 Extended Cab 6.5、2011 Extended Cab 6.5、2013 Regular Cab 6.5。其余 Silverado 行仍缺逐年完整参考。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需复核 2006 是否与 2005 完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2012	Regular Cab	6.5	205.6	79.9	73.6	2012 Silverado 1500 Regular Cab 6.5-ft standard bed		待终核: 缺失 2007/2008/2009/2010/2011 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2013	Regular Cab	6.5	205.6	79.9	73.6	2013 Silverado 1500 Regular Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008 Silverado 1500 Regular Cab 8-ft long bed		待终核: 缺失 2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Crew Cab	5.8	230.2	80.0	73.7	2007/2010/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed		待终核: 缺失 2008/2009/2011 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2010	Extended Cab	6.5	230.2	79.9	73.9	2008/2009/2010 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 2007 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011	Extended Cab	6.5	230.2	79.9	73.9	2011 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需逐年复核 2012/2013 外观三维是否与 2011 完全一致

下一步优先核对

继续补 gen1：Regular Cab 8.0 的 2000-2006、Extended Cab 8.0 的 2001-2006。

继续补 gen2：Regular Cab 8.0 的 2009-2013、Crew Cab 5.8 的 2008/2009/2011。

再回补 gen2 Regular Cab 6.5 的 2007-2011，以及 Extended Cab 6.5 的 2007、2012、2013，确认后再合并或标可入库。

下一步


--- Round 4 / 下一步 ---
更新点

本轮继续补强 Silverado 1500 gen2。

Crew Cab 5.8 ft 已按尺寸差异拆分：2007-2008 长 229.9、宽 79.9、高 73.7；2009-2010 长 230.2、宽 80.0、高 73.7；2011-2013 暂保留待终核。2007/2008/2009/2010 均已补入逐年参考。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Extended Cab 6.5 ft 已拆分：2008 单年长 229.9、宽 79.9、高 73.7；2009-2011 长 230.2、宽 79.9、高 73.9，已补齐 2009/2010/2011 参考，可入库。
Edmunds
+2
Edmunds
+2

2012-2013 Extended Cab 6.5 ft 暂不直接合并入库，因为 Edmunds 2013 Extended Cab 默认结果偏向 8 ft long bed，已发现 2013 6.5 ft 需用具体 trim/第三方辅助核对，仍保留待终核。
Edmunds
+1

当前批次进度
当前批次由上一轮 17 行继续拆分为 20 行。Colorado 2 行可入库；Silverado 1500 已新增可入库区间：2007-2008 Crew Cab 5.8、2009-2010 Crew Cab 5.8、2008 Extended Cab 6.5、2009-2011 Extended Cab 6.5。仍待终核的重点集中在 gen1 Regular/Extended long bed、gen2 Regular Cab 6.5/8.0、gen2 2011-2013 Crew Cab 5.8、gen2 2007/2012-2013 Extended Cab 6.5。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需复核 2006 是否与 2005 完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2012	Regular Cab	6.5	205.6	79.9	73.6	2012 Silverado 1500 Regular Cab 6.5-ft standard bed		待终核: 缺失 2007/2008/2009/2010/2011 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2013	Regular Cab	6.5	205.6	79.9	73.6	2013 Silverado 1500 Regular Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009 Silverado 1500 Regular Cab 8-ft long bed		待终核: 缺失 2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.8	2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed		待终核: 缺失 2011 年份参考，并需确认 2012/2013 高度 73.7/73.8 口径
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	230.2	79.9	73.9	2007 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需确认 2007 6.5-ft 标准床而非 8-ft 长床
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.7	2013 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 2012 年份参考，且 2013 需继续用具体 6.5-ft trim 复核

下一步优先核对

优先补 2011-2013 Crew Cab 5.8，确认 2011 缺失年份以及 2012/2013 高度是否统一用 73.8。

继续补 2012-2013 Extended Cab 6.5，重点确认 2012 和 2013 是否为 6.5 ft 标准床，不误用 8 ft long bed。

再补 gen2 Regular Cab 6.5/8.0 和 gen1 Regular Cab 8.0 / Extended Cab 8.0 的缺失年份。

下一步


--- Round 5 / 下一步 ---
更新点

本轮继续补强上一轮卡住的 Silverado 1500 gen2 Crew Cab 5.8 与 Extended Cab 6.5。

2011-2013 Crew Cab 5.8 ft 已补齐逐年参考：2011、2012、2013 均为 230.2 in 长、80.0 in 宽、73.7 in 高、69.3 in bed，可合并为 2011-2013 并标可入库；Edmunds 对 2011/2012/2013 Crew Cab 均给出同一组外廓尺寸。
Edmunds
+2
Edmunds
+2

2012-2013 Extended Cab 6.5 ft 已用 KBB 具体 6 1/2 ft trim 复核，KBB 明确 2012、2013 Extended Cab 均存在 6.5 ft 版本，且 6.5 ft 版本 Overall Length 为 230.2 in、Width 为 79.9 in；因此该行可入库。
Kbb.com
+1

同时将上一轮 2007 Extended Cab 6.5 的备注维持为待终核，因为仍需要确认 2007 标准床 6.5 ft 口径，不能因 2008-2013 已覆盖而自动外推。

当前批次进度
当前批次仍为 20 行。Colorado 2 行可入库；Silverado 1500 已完成 gen2 Crew Cab 5.8 的 2007-2013 全覆盖，并完成 gen2 Extended Cab 6.5 的 2008-2013 覆盖。仍待终核集中在 gen1 Regular/Extended 部分、gen2 Regular Cab 6.5/8.0，以及 gen2 2007 Extended Cab 6.5。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需复核 2006 是否与 2005 完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2012	Regular Cab	6.5	205.6	79.9	73.6	2012 Silverado 1500 Regular Cab 6.5-ft standard bed		待终核: 缺失 2007/2008/2009/2010/2011 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2013	Regular Cab	6.5	205.6	79.9	73.6	2013 Silverado 1500 Regular Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009 Silverado 1500 Regular Cab 8-ft long bed		待终核: 缺失 2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	230.2	79.9	73.9	2007 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需确认 2007 6.5-ft 标准床而非 8-ft 长床
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先补 gen2 Regular Cab 6.5 的 2007-2011，以及 Regular Cab 8.0 的 2010-2013。

然后补 gen2 2007 Extended Cab 6.5，确认是否应并入 2008 或 2009-2011 区间。

最后集中处理 gen1 Regular Cab 8.0、Extended Cab 6.5、Extended Cab 8.0 的缺失年份。

下一步


--- Round 6 / 下一步 ---
更新点

本轮补强 gen2 Regular Cab 6.5/8.0 与 2007 Extended Cab 6.5。

2007 Regular Cab 6.5 ft 已用 KBB 具体 6.5 ft trim 确认，长度 205.6、宽度 79.9；同页也确认 8 ft trim 长度 224.5、宽度 79.9，因此 2007 Regular Cab 的两个货斗版本可拆出为单年可入库。
Kbb.com

2010 Regular Cab 8.0 ft 已用 Edmunds 确认，长度 224.5、宽度 79.9、高度 73.5、bed length 97.8 in，可拆出为单年可入库。
Edmunds

2007 Extended Cab 6.5 ft 已用 KBB 具体 6.5 ft trim 确认，长度 229.9、宽度 79.9；该行可从待终核改为可入库。
Kbb.com

未完成的区间继续保留具体缺失年份，不把 2008-2012 Regular Cab 自动外推为可入库。

当前批次进度
当前批次由上一轮 20 行继续拆分为 23 行。新增可入库：2007 Regular Cab 6.5、2007 Regular Cab 8.0、2010 Regular Cab 8.0、2007 Extended Cab 6.5。仍待终核主要集中在 gen1 的 Regular/Extended 1999-2006，以及 gen2 Regular Cab 的 2008-2012 剩余年份。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需复核 2006 是否与 2005 完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Regular Cab	6.5	205.6	79.9	73.6	2007 Silverado 1500 Regular Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008-2012	Regular Cab	6.5	205.6	79.9	73.6	2011/2012 Silverado 1500 Regular Cab 6.5-ft standard bed		待终核: 缺失 2008/2009/2010 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2013	Regular Cab	6.5	205.6	79.9	73.6	2013 Silverado 1500 Regular Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Regular Cab	8.0	224.5	79.9	73.5	2007 Silverado 1500 Regular Cab 8-ft long bed	按 KBB/Edmunds 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008-2009	Regular Cab	8.0	224.5	79.9	73.5	2008/2009 Silverado 1500 Regular Cab 8-ft long bed		待终核: 需复核 2008/2009 高度与 2007/2010 是否完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2010	Regular Cab	8.0	224.5	79.9	73.5	2010 Silverado 1500 Regular Cab 8-ft long bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Regular Cab	8.0	224.5	79.9	73.5	2011 Silverado 1500 Regular Cab 8-ft long bed		待终核: 缺失 2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先补 gen2 Regular Cab 6.5 的 2008/2009/2010，确认后可与 2007/2011/2012/2013 合并或按高度拆分。

继续补 gen2 Regular Cab 8.0 的 2008/2009/2012/2013。

然后集中处理 gen1 Regular Cab 8.0、Extended Cab 6.5、Extended Cab 8.0 的缺失年份。

下一步


--- Round 7 / 下一步 ---
更新点

本轮继续补强 gen2 Regular Cab 6.5/8.0。

2010 Regular Cab 6.5 ft 已从 2008-2012 Regular Cab 6.5 中拆出为单年可入库；KBB 明确 2010 LT Pickup 2D 6 1/2 ft 的 Overall Length 为 205.6 in、Bed Length 为 6.50 ft、Width 为 79.9 in。
Kbb.com

2011-2013 Regular Cab 8.0 ft 已补齐可用参考：KBB/Edmunds 均能确认 2011/2013 8 ft Regular Cab 224.5 in 长度口径，2012 KBB 也列出 8 ft 版本；因此本轮将 2011-2013 Regular Cab 8.0 改为可入库。
Kbb.com
+2
Kbb.com
+2

2008-2009 Regular Cab 8.0 ft 继续保留待终核，因为 2008/2009 虽已有 8 ft 参考，但仍需确认高度口径是否与 2010-2013 完全一致；未强行并入。

未完成的 gen1 与 gen2 Regular Cab 6.5 缺口继续保留具体缺失年份。

当前批次进度
当前批次由上一轮 24 行继续拆分为 26 行。新增可入库：2010 Regular Cab 6.5、2011-2013 Regular Cab 8.0。目前 gen2 的 Crew Cab、Extended Cab 已基本完成；剩余重点为 gen2 Regular Cab 6.5 的 2008/2009/2011/2012，以及 gen1 Regular/Extended 的 1999-2006 缺失年份。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需复核 2006 是否与 2005 完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Regular Cab	6.5	205.6	79.9	73.6	2007 Silverado 1500 Regular Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008-2009	Regular Cab	6.5	205.6	79.9	73.6	待补 2008/2009 Silverado 1500 Regular Cab 6.5-ft standard bed		待终核: 缺失 2008/2009 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2010	Regular Cab	6.5	205.6	79.9	73.6	2010 Silverado 1500 Regular Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2012	Regular Cab	6.5	205.6	79.9	73.6	2011/2012 Silverado 1500 Regular Cab 6.5-ft standard bed		待终核: 需复核 2011/2012 高度与 2010/2013 是否完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2013	Regular Cab	6.5	205.6	79.9	73.6	2013 Silverado 1500 Regular Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Regular Cab	8.0	224.5	79.9	73.5	2007 Silverado 1500 Regular Cab 8-ft long bed	按 KBB/Edmunds 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008-2009	Regular Cab	8.0	224.5	79.9	73.5	2008/2009 Silverado 1500 Regular Cab 8-ft long bed		待终核: 需复核 2008/2009 高度与 2007/2010 是否完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2010	Regular Cab	8.0	224.5	79.9	73.5	2010 Silverado 1500 Regular Cab 8-ft long bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Regular Cab	8.0	224.5	79.9	73.5	2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 8-ft trim 逐年确认，取高度安全值 73.5	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先补 gen2 Regular Cab 6.5 的 2008/2009/2011/2012，确认后 gen2 Regular Cab 6.5 可闭环。

继续补 gen2 Regular Cab 8.0 的 2008/2009 高度口径，确认后 gen2 Regular Cab 8.0 可闭环。

最后集中处理 gen1 Regular Cab 8.0、Extended Cab 6.5、Extended Cab 8.0 的缺失年份。

下一步


--- Round 8 / 下一步 ---
更新点

本轮继续补强 gen2 Regular Cab 6.5。

2009 Regular Cab 6.5 ft 已用 KBB 具体 6 1/2 ft trim 确认，Overall Length 为 205.6 in；因此从待终核中拆出并标可入库。
Kbb.com

2011/2012 Regular Cab 6.5 ft 已用 KBB 具体 6 1/2 ft trim 确认，Overall Length 均为 205.6 in，且 2012 KBB 明确列出 6 1/2 ft 与 8 ft 两种 Regular Cab trim；因此 2011-2012 Regular Cab 6.5 改为可入库。
Kbb.com
+2
Kbb.com
+2

2008 Regular Cab 6.5 ft 仍未取得足够明确的 6.5 ft 逐年尺寸参考，本轮保留单年待终核，避免把 2009-2013 外推到 2008。

2008-2009 Regular Cab 8.0 ft 暂未闭环，高度口径仍需继续复核。

当前批次进度
当前批次由上一轮 26 行整理为 25 行。gen2 Regular Cab 6.5 已完成 2007、2009-2013，剩余 2008 单年待终核。gen2 Crew Cab 与 Extended Cab 已基本完成。剩余重点：gen2 2008 Regular Cab 6.5、2008-2009 Regular Cab 8.0，以及 gen1 的 Regular/Extended 1999-2006 缺失年份。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 需复核 2006 是否与 2005 完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Regular Cab	6.5	205.6	79.9	73.6	2007 Silverado 1500 Regular Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Regular Cab	6.5	205.6	79.9	73.6	待补 2008 Silverado 1500 Regular Cab 6.5-ft standard bed		待终核: 缺失 2008 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Regular Cab	6.5	205.6	79.9	73.6	2009/2010 Silverado 1500 Regular Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2012	Regular Cab	6.5	205.6	79.9	73.6	2011/2012 Silverado 1500 Regular Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2013	Regular Cab	6.5	205.6	79.9	73.6	2013 Silverado 1500 Regular Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Regular Cab	8.0	224.5	79.9	73.5	2007 Silverado 1500 Regular Cab 8-ft long bed	按 KBB/Edmunds 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008-2009	Regular Cab	8.0	224.5	79.9	73.5	2008/2009 Silverado 1500 Regular Cab 8-ft long bed		待终核: 需复核 2008/2009 高度与 2007/2010 是否完全一致
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2010	Regular Cab	8.0	224.5	79.9	73.5	2010 Silverado 1500 Regular Cab 8-ft long bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Regular Cab	8.0	224.5	79.9	73.5	2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 8-ft trim 逐年确认，取高度安全值 73.5	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先补 gen2 2008 Regular Cab 6.5，确认后 gen2 Regular Cab 6.5 可闭环。

继续补 gen2 2008-2009 Regular Cab 8.0 高度口径，确认后 gen2 Regular Cab 8.0 可闭环。

最后集中处理 gen1 Regular Cab 8.0、Extended Cab 6.5、Extended Cab 8.0 的缺失年份。

下一步


--- Round 9 / 下一步 ---
更新点

本轮闭环 gen2 Regular Cab 6.5：2008 Regular Cab 6.5 ft 已用 KBB 具体 6 1/2 ft trim 确认，Overall Length 为 205.6 in；因此 2007-2013 Regular Cab 6.5 可合并为连续区间并标可入库。
Kbb.com
+1

本轮闭环 gen2 Regular Cab 8.0：2008 Edmunds 明确 Regular Cab 8 ft bed 长 224.5、宽 79.9、高 73.5；2009 Edmunds/KBB 也确认 8 ft Regular Cab 长 224.5、宽 79.9、高 73.5，因此 2007-2013 Regular Cab 8.0 可合并为连续区间并标可入库。
Edmunds
+2
Kbb.com
+2

当前 split 内 gen2 Silverado 1500 的 Regular Cab / Crew Cab / Extended Cab 已基本完成；剩余待终核集中到 gen1 Silverado 1500 的 Regular/Extended 1999-2006。

保持当前批次边界，不新增 split 外年份或车型。

当前批次进度
当前批次由上一轮 26 行压缩整理为 21 行。Colorado 2 行可入库；Silverado 1500 gen2 相关行已全部可入库；Silverado 1500 gen1 中 Crew Cab 2004/2005/2006 已可入库，Regular Cab 8.0、Extended Cab 6.5、Extended Cab 8.0 仍需继续补齐缺失年份或解决来源冲突。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999 Silverado 1500 Regular Cab long bed		待终核: 缺失 2000/2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 2006 Edmunds/KBB 长度口径存在 227.7/230.2 差异，需确认是否混入 SS 或不同轴距
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先处理 gen1 Regular Cab 8.0 的 2000-2006，确认是否可与 1999 合并。

继续处理 gen1 Extended Cab 6.5 的 1999/2000/2002/2004，以及 2006 的 227.7/230.2 长度口径冲突。

最后处理 gen1 Extended Cab 8.0 的 2001-2006。

下一步


--- Round 10 / 下一步 ---
更新点

本轮继续补强 gen1 Silverado 1500。

2006 Extended Cab 6.5 ft 已用 Edmunds 明确确认：长度 227.7 in、宽度 78.5 in、高度 73.9 in、Bed length 78.6 in，因此从待终核改为可入库。
Edmunds

Regular Cab 8.0 ft 已补入 2000 年参考；Cars.com 明确 2000 Silverado 1500 Regular Cab 长度 227.6 in、高度 73.8 in，支持该行继续按 227.6 / 78.5 / 73.9 的安全最大值推进，但仍缺 2001-2006，暂不能入库。
Cars.com

Extended Cab 8.0 ft 已补入 2002 年 8 ft long bed 参考；Edmunds 明确 2002 Extended Cab LS 2WD LB 的 bed length 为 97.6 in，属于 8 ft long bed 口径，但仍缺 2001/2003/2004/2005/2006 外廓逐年参考，暂不能入库。
Edmunds

当前批次进度
当前批次仍为 21 行。Colorado 2 行可入库；Silverado 1500 gen2 已可入库；Silverado 1500 gen1 Crew Cab 5.8 已可入库；本轮新增 2006 Extended Cab 6.5 可入库。剩余待终核集中在 gen1 Regular Cab 8.0、gen1 Extended Cab 6.5 的 1999/2000/2002/2004、gen1 Extended Cab 8.0 的 2001/2003/2004/2005/2006。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Regular Cab	8.0	227.6	78.5	73.9	1999/2000 Silverado 1500 Regular Cab 8-ft long bed		待终核: 缺失 2001/2002/2003/2004/2005/2006 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 Edmunds 227.7/78.5/73.9 与 78.6 in bed length 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000/2002 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2003/2004/2005/2006 年份参考，并需确认 70.8/73.7 高度口径是否为 2WD/4WD 差异
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先补 gen1 Regular Cab 8.0 的 2001-2006，确认是否能合并为 1999-2006。

继续补 gen1 Extended Cab 6.5 的 1999/2000/2002/2004，确认后与 2001/2003/2005/2006 归并或拆分。

最后补 gen1 Extended Cab 8.0 的 2001/2003/2004/2005/2006，并确认 2WD/4WD 高度最大值。

下一步


--- Round 11 / 下一步 ---
更新点

本轮继续补强 gen1 Regular Cab 8.0，没有新增当前 split 外年份。

已发现原 1999-2006 Regular Cab 8.0 不能继续用单一 227.6 覆盖整段：2001 Edmunds 的 Regular Cab 8 ft 长床为 222.1 in、宽 78.5 in、高 71.0 in；2006 Edmunds/KBB 的 Regular Cab 8 ft 长床为 224.5 in、宽 78.5 in、高 71.0 in，因此本轮已把 2001、2006 单年拆出。
Edmunds
+2
Edmunds
+2

2004 Edmunds 也出现 Regular Cab 133 in wheelbase / 8 ft 口径下 222.1 in 长度，但仍需和 2002/2003/2005 一起复核是否同口径，暂不提前标可入库。
Edmunds

gen1 Extended Cab 6.5、Extended Cab 8.0 本轮未强行外推，继续保留具体缺失年份。

当前批次进度
当前批次由上一轮 19 行拆分为 22 行。Colorado 2 行可入库；Silverado 1500 gen2 全部可入库；gen1 Crew Cab 5.8 可入库；gen1 Extended Cab 6.5 的 2005/2006 可入库；本轮新增 gen1 Regular Cab 8.0 的 2001、2006 单年可入库。剩余待终核集中在 gen1 Regular Cab 8.0 的 1999/2000/2002-2005，以及 gen1 Extended Cab 6.5、Extended Cab 8.0 的缺失年份。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Regular Cab	8.0	227.6	78.5	73.9	1999/2000 Silverado 1500 Regular Cab 8-ft long bed		待终核: 需复核 1999/2000 长度 227.6 是否为正确 Regular Cab 8-ft 口径
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001	Regular Cab	8.0	222.1	78.5	71.0	2001 Silverado 1500 Regular Cab 8-ft long bed	2001 Edmunds 口径为 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002-2005	Regular Cab	8.0	224.5	78.5	73.9	2004 Silverado 1500 Regular Cab 8-ft long bed		待终核: 缺失 2002/2003/2005 年份参考，并需确认 2004 长度 222.1 与 2006 长度 224.5 的口径差异
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Regular Cab	8.0	224.5	78.5	71.0	2006 Silverado 1500 Regular Cab 8-ft long bed	2006 Edmunds/KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 Edmunds 227.7/78.5/73.9 与 78.6 in bed length 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000/2002 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2003/2004/2005/2006 年份参考，并需确认 70.8/73.7 高度口径是否为 2WD/4WD 差异
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

继续补 gen1 Regular Cab 8.0 的 2002/2003/2005，并回头确认 1999/2000 的 227.6 是否应修正。

继续补 gen1 Extended Cab 6.5 的 1999/2000/2002/2004。

最后补 gen1 Extended Cab 8.0 的 2001/2003/2004/2005/2006，并确认高度最大值口径。

下一步


--- Round 12 / 下一步 ---
更新点

本轮继续补强 gen1 Regular Cab 8.0，重点处理 2002/2003/2005 与 1999/2000 口径冲突。

已确认 2005 Regular Cab 8.0 ft 可单年拆出：Edmunds 对 2005 Silverado 1500 Regular Cab 给出 Length 224.5 in、Width 78.5 in、Height 71.0 in；KBB 同年 Regular Cab 规格页也列出 8 ft trim，因此本轮将 2005 拆出为可入库。
Edmunds
+1

已发现 1999/2000 Regular Cab 8.0 存在明显口径冲突：KBB 1999 Regular Cab 页面显示的是 203.1 in / 6.0 ft bed，Edmunds 2000 Regular Cab Base 显示 203.3 in / 119 in wheelbase，均不像 8 ft long bed；因此本轮把 1999-2000 改为更具体的“疑似误用非 8 ft/需确认”待终核。
Kbb.com
+1

已把 2002-2004 Regular Cab 8.0 拆开：2002 暂标为待终核，因为当前抓到的 Edmunds 2002 Regular Cab 是 203.2 in / 78.7 in bed，更像 6.5 ft 口径；2004 继续保留待终核，需确认 222.1 与 224.5 的轴距/货斗口径。
Edmunds

Extended Cab 6.5 与 Extended Cab 8.0 本轮未强行外推，只同步保留剩余缺失年份。

当前批次进度
当前批次由上一轮 22 行拆分为 24 行。Colorado 2 行可入库；Silverado 1500 gen2 全部可入库；gen1 Crew Cab 5.8 可入库；gen1 Extended Cab 6.5 的 2005/2006 可入库；本轮新增 2005 Regular Cab 8.0 可入库。剩余待终核集中在 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004，以及 gen1 Extended Cab 6.5、Extended Cab 8.0 的缺失年份。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Regular Cab	8.0	227.6	78.5	73.9	待补 1999/2000 Silverado 1500 Regular Cab 8-ft long bed	原 227.6 口径疑似非 Regular Cab 8-ft 或混入其他 cab，需重核	待终核: 1999/2000 当前来源显示 203.1/203.3 更像短床，需确认是否存在 8-ft trim 外廓
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001	Regular Cab	8.0	222.1	78.5	71.0	2001 Silverado 1500 Regular Cab 8-ft long bed	2001 Edmunds 口径为 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Regular Cab	8.0	224.5	78.5	73.9	待补 2002 Silverado 1500 Regular Cab 8-ft long bed	当前抓到 2002 Regular Cab 为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2002 是否存在 8-ft trim 224.5 或应改为 222.1
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003-2004	Regular Cab	8.0	224.5	78.5	73.9	2004 Silverado 1500 Regular Cab 8-ft long bed		待终核: 缺失 2003 年份参考，并需确认 2004 长度 222.1 与 224.5 的口径差异
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Regular Cab	8.0	224.5	78.5	71.0	2005 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds 224.5/78.5/71.0 与 KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Regular Cab	8.0	224.5	78.5	71.0	2006 Silverado 1500 Regular Cab 8-ft long bed	2006 Edmunds/KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 Edmunds 227.7/78.5/73.9 与 78.6 in bed length 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000/2002 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2003/2004/2005/2006 年份参考，并需确认 70.8/73.7 高度口径是否为 2WD/4WD 差异
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

继续核对 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004，重点判断是否存在 8-ft 长床配置对应的真实外廓，还是原行误混入其他 cab/短床口径。

继续补 gen1 Extended Cab 6.5 的 1999/2000/2002/2004。

最后补 gen1 Extended Cab 8.0 的 2001/2003/2004/2005/2006，并确认 2WD/4WD 高度最大值口径。

下一步


--- Round 13 / 下一步 ---
更新点

本轮继续补强 gen1 Regular Cab 8.0，把上一轮仍混在一起的 2003-2004 拆成单年待终核，避免用 2004 的疑似 6.5-ft 口径覆盖 2003。

2004 KBB 明确 Silverado 1500 Regular Cab 存在 Pickup 2D 8 ft trim，但 Edmunds 当前打开的 2004 Regular Cab 规格页给出的 Length 203.2 in、Bed length 78.7 in，更像 6.5-ft 标准床；因此 2004 不能直接标可入库，已改为单年待终核。
Kbb.com
+1

2002 当前抓到的 Edmunds Regular Cab 也是 203.2 in / 78.7 in bed，继续判断为疑似 6.5-ft 口径，不直接入库。
Edmunds

Extended Cab 6.5 与 Extended Cab 8.0 本轮仍不外推，只保留明确缺失年份，避免伪完成。

当前批次进度
当前批次由上一轮 24 行继续拆分为 25 行。已完成：Colorado 2 行、Silverado 1500 gen2 全部、gen1 Crew Cab 5.8、gen1 Extended Cab 6.5 的 2005/2006、gen1 Regular Cab 8.0 的 2001/2005/2006。未完成集中在 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004，以及 gen1 Extended Cab 6.5、Extended Cab 8.0。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Regular Cab	8.0	227.6	78.5	73.9	待补 1999/2000 Silverado 1500 Regular Cab 8-ft long bed	原 227.6 口径疑似非 Regular Cab 8-ft 或混入其他 cab，需重核	待终核: 1999/2000 当前来源显示 203.1/203.3 更像短床，需确认是否存在 8-ft trim 外廓
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001	Regular Cab	8.0	222.1	78.5	71.0	2001 Silverado 1500 Regular Cab 8-ft long bed	2001 Edmunds 口径为 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Regular Cab	8.0	224.5	78.5	73.9	待补 2002 Silverado 1500 Regular Cab 8-ft long bed	当前抓到 2002 Regular Cab 为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2002 是否存在 8-ft trim 224.5 或应改为 222.1
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003	Regular Cab	8.0	224.5	78.5	73.9	待补 2003 Silverado 1500 Regular Cab 8-ft long bed	需单年确认 8-ft long bed 外廓，不再与 2004 混合覆盖	待终核: 缺失 2003 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Regular Cab	8.0	224.5	78.5	73.9	待补 2004 Silverado 1500 Regular Cab 8-ft long bed	KBB 列出 8-ft trim，但 Edmunds 当前规格页为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2004 8-ft trim 外廓，不能用 203.2 短床口径入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Regular Cab	8.0	224.5	78.5	71.0	2005 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds 224.5/78.5/71.0 与 KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Regular Cab	8.0	224.5	78.5	71.0	2006 Silverado 1500 Regular Cab 8-ft long bed	2006 Edmunds/KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2004	Extended Cab	6.5	227.7	78.5	73.9	2001/2003 Silverado 1500 Extended Cab 6.5-ft standard bed		待终核: 缺失 1999/2000/2002/2004 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	6.5	227.7	78.5	73.9	2005 Silverado 1500 Extended Cab 6.5-ft standard bed	单年已核对	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	6.5	227.7	78.5	73.9	2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 Edmunds 227.7/78.5/73.9 与 78.6 in bed length 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000/2002 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2003/2004/2005/2006 年份参考，并需确认 70.8/73.7 高度口径是否为 2WD/4WD 差异
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

继续核对 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004，重点确认 8-ft trim 外廓是否为 222.1、224.5 或原表 227.6。

继续补 gen1 Extended Cab 6.5 的 1999/2000/2002/2004。

最后补 gen1 Extended Cab 8.0 的 2001/2003/2004/2005/2006，并确认 2WD/4WD 高度最大值口径。

下一步


--- Round 14 / 下一步 ---
更新点

本轮继续补强 gen1 Extended Cab 6.5。

2000 Extended Cab 6.5 ft 已用 KBB 具体规格确认：Overall Length 227.6 in、Bed Length 6.50 ft、Width 78.5 in；因此从 1999-2004 待终核区间中拆出为单年可入库。
Kbb.com

2004 Extended Cab 6.5 ft 已用 Edmunds 具体 SB 规格确认：Length 227.70 in、Width 78.5 in、Height 73.9 in、Bed length 78.6 in；因此从待终核中拆出为单年可入库。
Edmunds

1999 Extended Cab 6.5 ft 仍未确认，且当前更容易抓到的是 8 ft long bed 口径；2002 Extended Cab 6.5 ft 仍缺明确 6.5 ft 外廓，继续待终核。

当前 split 边界未扩展，所有拆分年份仍在原记录范围内。

当前批次进度
当前批次由上一轮 25 行拆分整理为 27 行。已完成：Colorado 2 行、Silverado 1500 gen2 全部、gen1 Crew Cab 5.8、gen1 Extended Cab 6.5 的 2000/2001/2003/2004/2005/2006、gen1 Regular Cab 8.0 的 2001/2005/2006。未完成集中在 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004、gen1 Extended Cab 6.5 的 1999/2002、gen1 Extended Cab 8.0 的 2001/2003/2004/2005/2006。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Regular Cab	8.0	227.6	78.5	73.9	待补 1999/2000 Silverado 1500 Regular Cab 8-ft long bed	原 227.6 口径疑似非 Regular Cab 8-ft 或混入其他 cab，需重核	待终核: 1999/2000 当前来源显示 203.1/203.3 更像短床，需确认是否存在 8-ft trim 外廓
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001	Regular Cab	8.0	222.1	78.5	71.0	2001 Silverado 1500 Regular Cab 8-ft long bed	2001 Edmunds 口径为 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Regular Cab	8.0	224.5	78.5	73.9	待补 2002 Silverado 1500 Regular Cab 8-ft long bed	当前抓到 2002 Regular Cab 为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2002 是否存在 8-ft trim 224.5 或应改为 222.1
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003	Regular Cab	8.0	224.5	78.5	73.9	待补 2003 Silverado 1500 Regular Cab 8-ft long bed	需单年确认 8-ft long bed 外廓，不再与 2004 混合覆盖	待终核: 缺失 2003 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Regular Cab	8.0	224.5	78.5	73.9	待补 2004 Silverado 1500 Regular Cab 8-ft long bed	KBB 列出 8-ft trim，但 Edmunds 当前规格页为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2004 8-ft trim 外廓，不能用 203.2 短床口径入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Regular Cab	8.0	224.5	78.5	71.0	2005 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds 224.5/78.5/71.0 与 KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Regular Cab	8.0	224.5	78.5	71.0	2006 Silverado 1500 Regular Cab 8-ft long bed	2006 Edmunds/KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Extended Cab	6.5	227.7	78.5	73.9	待补 1999 Silverado 1500 Extended Cab 6.5-ft standard bed	当前更易抓到 1999 Extended Cab 8-ft/157.5 WB，6.5-ft 需继续核对	待终核: 缺失 1999 6.5-ft 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000-2001	Extended Cab	6.5	227.7	78.5	73.9	2000/2001 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2000 KBB 6.5-ft 与 2001 既有参考确认，取 227.7/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Extended Cab	6.5	227.7	78.5	73.9	待补 2002 Silverado 1500 Extended Cab 6.5-ft standard bed	当前抓到 2002 Extended Cab 多为 8-ft/157.5 WB，6.5-ft 需继续核对	待终核: 缺失 2002 6.5-ft 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003-2004	Extended Cab	6.5	227.7	78.5	73.9	2003/2004 Silverado 1500 Extended Cab 6.5-ft standard bed	2004 Edmunds SB 已确认 227.70/78.5/73.9/78.6in bed	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	6.5	227.7	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2005/2006 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2006	Extended Cab	8.0	246.7	78.5	73.7	1999/2000/2002 Silverado 1500 Extended Cab 8-ft long bed		待终核: 缺失 2001/2003/2004/2005/2006 年份参考，并需确认 70.8/73.7 高度口径是否为 2WD/4WD 差异
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先核对 gen1 Extended Cab 6.5 的 1999/2002，若确认无 6.5-ft 口径或外廓不同，需要继续拆分/修正。

继续核对 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004，确认是否为 8-ft trim 外廓还是原行口径错误。

最后补 gen1 Extended Cab 8.0 的 2001/2003/2004/2005/2006，并确认 2WD/4WD 高度最大值。

下一步


--- Round 15 / 下一步 ---
更新点

本轮继续补强 gen1 Extended Cab 6.5 与 Extended Cab 8.0。

1999 Extended Cab 6.5 已用 KBB Short Bed / 143.5 in WB 口径确认，Overall Length 227.6 in、Width 78.5 in；因此从待终核改为单年可入库，表内货斗长度仍按原记录保留为 6.5 ft。
Kbb.com

Extended Cab 8.0 已补强 2001/2002：KBB 2001 Extended Cab 同页明确 6.5 ft 与 8 ft 两种 bed，8 ft Overall Length 为 246.6 in；Edmunds 2002 Extended Cab 8 ft bed length 97.6 in、Length 246.6 in，因此本轮把 2001-2002 Extended Cab 8.0 拆出并标可入库。
Kbb.com
+1

1999-2000 Extended Cab 8.0 也已依据 1999 Edmunds/KBB 与既有 2000 参考整理为可入库，取安全最大长度 246.7、高度 73.7。
Edmunds
+1

2002 Extended Cab 6.5 仍未取得明确 6.5-ft 外廓参考，保留待终核；2003-2006 Extended Cab 8.0 仍需逐年补齐。

当前批次进度
当前批次由上一轮 27 行拆分整理为 29 行。已完成：Colorado 2 行、Silverado 1500 gen2 全部、gen1 Crew Cab 5.8、gen1 Extended Cab 6.5 的 1999/2000/2001/2003/2004/2005/2006、gen1 Extended Cab 8.0 的 1999-2002、gen1 Regular Cab 8.0 的 2001/2005/2006。未完成集中在 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004、gen1 Extended Cab 6.5 的 2002、gen1 Extended Cab 8.0 的 2003-2006。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Regular Cab	8.0	227.6	78.5	73.9	待补 1999/2000 Silverado 1500 Regular Cab 8-ft long bed	原 227.6 口径疑似非 Regular Cab 8-ft 或混入其他 cab，需重核	待终核: 1999/2000 当前来源显示 203.1/203.3 更像短床，需确认是否存在 8-ft trim 外廓
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001	Regular Cab	8.0	222.1	78.5	71.0	2001 Silverado 1500 Regular Cab 8-ft long bed	2001 Edmunds 口径为 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Regular Cab	8.0	224.5	78.5	73.9	待补 2002 Silverado 1500 Regular Cab 8-ft long bed	当前抓到 2002 Regular Cab 为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2002 是否存在 8-ft trim 224.5 或应改为 222.1
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003	Regular Cab	8.0	224.5	78.5	73.9	待补 2003 Silverado 1500 Regular Cab 8-ft long bed	需单年确认 8-ft long bed 外廓，不再与 2004 混合覆盖	待终核: 缺失 2003 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Regular Cab	8.0	224.5	78.5	73.9	待补 2004 Silverado 1500 Regular Cab 8-ft long bed	KBB 列出 8-ft trim，但 Edmunds 当前规格页为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2004 8-ft trim 外廓，不能用 203.2 短床口径入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Regular Cab	8.0	224.5	78.5	71.0	2005 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds 224.5/78.5/71.0 与 KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Regular Cab	8.0	224.5	78.5	71.0	2006 Silverado 1500 Regular Cab 8-ft long bed	2006 Edmunds/KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Extended Cab	6.5	227.6	78.5	73.9	1999 Silverado 1500 Extended Cab short bed / 143.5-in WB	按 KBB Short Bed/143.5 WB 确认，货斗名义按表内 6.5 保留	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000-2001	Extended Cab	6.5	227.7	78.5	73.9	2000/2001 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2000 KBB 6.5-ft 与 2001 既有参考确认，取 227.7/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Extended Cab	6.5	227.7	78.5	73.9	待补 2002 Silverado 1500 Extended Cab 6.5-ft standard bed	当前抓到 2002 Extended Cab 多为 8-ft/157.5 WB，6.5-ft 需继续核对	待终核: 缺失 2002 6.5-ft 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003-2004	Extended Cab	6.5	227.7	78.5	73.9	2003/2004 Silverado 1500 Extended Cab 6.5-ft standard bed	2004 Edmunds SB 已确认 227.70/78.5/73.9/78.6in bed	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	6.5	227.7	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2005/2006 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed	按 1999 Edmunds/KBB 8-ft/157.5 WB 与 2000 既有参考确认，取 246.7/73.7 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001-2002	Extended Cab	8.0	246.6	78.5	73.7	2001/2002 Silverado 1500 Extended Cab 8-ft long bed	2001 KBB 与 2002 Edmunds 均确认 8-ft/157.5 WB，取高度安全值 73.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003-2006	Extended Cab	8.0	246.7	78.5	73.7	2004 KBB Silverado 1500 Extended Cab 8-ft trim		待终核: 缺失 2003/2005/2006 年份参考，并需确认 2004 8-ft 外廓尺寸
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先核对 gen1 Extended Cab 6.5 的 2002，确认后该组可闭环。

继续核对 gen1 Extended Cab 8.0 的 2003/2004/2005/2006，确认后该组可闭环。

最后回头处理 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004 口径冲突。

下一步


--- Round 16 / 下一步 ---
更新点

本轮补强 gen1 Extended Cab 6.5 的最后缺口：2002 Extended Cab 6.5 ft 已用 KBB Short Bed 口径确认，Overall Length 227.7 in、Bed Length 6.50 ft、Wheelbase 143.5 in；因此 2000-2004 Extended Cab 6.5 可闭环并合并为可入库。
Kbb.com
+2
Kbb.com
+2

本轮继续补强 gen1 Extended Cab 8.0：2004 Extended Cab 8.0 ft 已用 Edmunds / KBB 8-ft trim 确认，Length 246.6 in、Width 78.5 in、Bed length 97.6 in / 8.00 ft；拆出为单年可入库。
Edmunds
+1

2005 Extended Cab 8.0 ft 已用 KBB 8-ft trim 确认，Overall Length 249.0 in、Wheelbase 157.5 in、Bed Length 8.00 ft；该年尺寸明显大于 1999-2004，因此单年拆出并标可入库。
Kbb.com
+1

2003 Extended Cab 8.0 与 2006 Extended Cab 8.0 仍缺明确 8-ft 外廓逐年参考，本轮继续保留待终核，不外推。

当前批次进度
当前批次由上一轮 29 行整理为 31 行。已完成：Colorado 2 行、Silverado 1500 gen2 全部、gen1 Crew Cab 5.8、gen1 Extended Cab 6.5 全部、gen1 Extended Cab 8.0 的 1999-2002/2004/2005、gen1 Regular Cab 8.0 的 2001/2005/2006。剩余待终核集中在 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004，以及 gen1 Extended Cab 8.0 的 2003/2006。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Regular Cab	8.0	227.6	78.5	73.9	待补 1999/2000 Silverado 1500 Regular Cab 8-ft long bed	原 227.6 口径疑似非 Regular Cab 8-ft 或混入其他 cab，需重核	待终核: 1999/2000 当前来源显示 203.1/203.3 更像短床，需确认是否存在 8-ft trim 外廓
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001	Regular Cab	8.0	222.1	78.5	71.0	2001 Silverado 1500 Regular Cab 8-ft long bed	2001 Edmunds 口径为 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Regular Cab	8.0	224.5	78.5	73.9	待补 2002 Silverado 1500 Regular Cab 8-ft long bed	当前抓到 2002 Regular Cab 为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2002 是否存在 8-ft trim 224.5 或应改为 222.1
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003	Regular Cab	8.0	224.5	78.5	73.9	待补 2003 Silverado 1500 Regular Cab 8-ft long bed	需单年确认 8-ft long bed 外廓，不再与 2004 混合覆盖	待终核: 缺失 2003 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Regular Cab	8.0	224.5	78.5	73.9	待补 2004 Silverado 1500 Regular Cab 8-ft long bed	KBB 列出 8-ft trim，但 Edmunds 当前规格页为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2004 8-ft trim 外廓，不能用 203.2 短床口径入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Regular Cab	8.0	224.5	78.5	71.0	2005 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds 224.5/78.5/71.0 与 KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Regular Cab	8.0	224.5	78.5	71.0	2006 Silverado 1500 Regular Cab 8-ft long bed	2006 Edmunds/KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Extended Cab	6.5	227.6	78.5	73.9	1999 Silverado 1500 Extended Cab short bed / 143.5-in WB	按 KBB Short Bed/143.5 WB 确认，货斗名义按表内 6.5 保留	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000-2004	Extended Cab	6.5	227.7	78.5	73.9	2000/2001/2002/2003/2004 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2000-2004 6.5-ft/143.5 WB 逐年确认，取 227.7/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	6.5	227.7	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2005/2006 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed	按 1999 Edmunds/KBB 8-ft/157.5 WB 与 2000 既有参考确认，取 246.7/73.7 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001-2002	Extended Cab	8.0	246.6	78.5	73.7	2001/2002 Silverado 1500 Extended Cab 8-ft long bed	2001 KBB 与 2002 Edmunds 均确认 8-ft/157.5 WB，取高度安全值 73.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003	Extended Cab	8.0	246.7	78.5	73.7	待补 2003 Silverado 1500 Extended Cab 8-ft long bed	当前明确参考仍偏 6.5-ft/143.5 WB，8-ft 需继续单年确认	待终核: 缺失 2003 8-ft 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Extended Cab	8.0	246.6	78.5	73.7	2004 Silverado 1500 Extended Cab 8-ft long bed	按 Edmunds/KBB 8-ft/157.5 WB 确认，取高度安全值 73.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Extended Cab	8.0	249.0	78.5	73.9	2005 Silverado 1500 Extended Cab 8-ft long bed	2005 KBB 8-ft trim 长度 249.0，单年拆出取安全高度 73.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Extended Cab	8.0	249.0	78.5	73.9	待补 2006 Silverado 1500 Extended Cab 8-ft long bed	需确认 2006 8-ft trim 是否延续 2005 的 249.0 长度口径	待终核: 缺失 2006 8-ft 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先核对 gen1 Extended Cab 8.0 的 2003/2006，确认后该组可闭环。

最后回头处理 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004 口径冲突，重点判断是否存在 8-ft trim 外廓，还是原记录应缩小/修正。

下一步


--- Round 17 / 下一步 ---
更新点

本轮补强 gen1 Extended Cab 8.0 的剩余缺口。

2006 Extended Cab 8.0 ft 已用 KBB 具体 8-ft trim 确认，Overall Length 249.0 in、Wheelbase 157.5 in、Bed Length 8.00 ft；因此可与 2005 合并为 2005-2006 可入库。
Kbb.com

2003 Extended Cab 8.0 ft 已确认 KBB 明确列出 2003 Extended Cab 有 Pickup 4D 8 ft / LS 8 ft / LT 8 ft 等 8-ft 版本，但当前可读结果未直接给出外廓尺寸；本轮仍不标可入库，继续保留单年待终核。
Kbb.com

2004 Regular Cab 8.0 ft 的口径有所推进：Edmunds 2004 Regular Cab Base 明确 bed length 97.6 in，说明该页实际是 8-ft 长床，不是上一轮误判的 6.5-ft；但本轮只确认床长与配置口径，外廓长宽高仍需继续核对后再入库。
Edmunds

当前批次进度
当前批次仍为 31 行。已完成：Colorado 2 行、Silverado 1500 gen2 全部、gen1 Crew Cab 5.8、gen1 Extended Cab 6.5 全部、gen1 Extended Cab 8.0 的 1999-2002/2004/2005-2006、gen1 Regular Cab 8.0 的 2001/2005/2006。未完成仅剩 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004，以及 gen1 Extended Cab 8.0 的 2003。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Regular Cab	8.0	227.6	78.5	73.9	待补 1999/2000 Silverado 1500 Regular Cab 8-ft long bed	原 227.6 口径疑似非 Regular Cab 8-ft 或混入其他 cab，需重核	待终核: 1999/2000 当前来源显示 203.1/203.3 更像短床，需确认是否存在 8-ft trim 外廓
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001	Regular Cab	8.0	222.1	78.5	71.0	2001 Silverado 1500 Regular Cab 8-ft long bed	2001 Edmunds 口径为 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Regular Cab	8.0	224.5	78.5	73.9	待补 2002 Silverado 1500 Regular Cab 8-ft long bed	当前抓到 2002 Regular Cab 为 203.2/78.7in bed，疑似 6.5-ft 口径	待终核: 需确认 2002 是否存在 8-ft trim 224.5 或应改为 222.1
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003	Regular Cab	8.0	224.5	78.5	73.9	待补 2003 Silverado 1500 Regular Cab 8-ft long bed	需单年确认 8-ft long bed 外廓，不再与 2004 混合覆盖	待终核: 缺失 2003 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Regular Cab	8.0	224.5	78.5	73.9	2004 Silverado 1500 Regular Cab 8-ft long bed	Edmunds 已确认 97.6 in bed，8-ft 配置成立；仍需复核外廓长宽高	待终核: 需确认 2004 8-ft trim 外廓是否为 224.5/78.5/73.9
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Regular Cab	8.0	224.5	78.5	71.0	2005 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds 224.5/78.5/71.0 与 KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Regular Cab	8.0	224.5	78.5	71.0	2006 Silverado 1500 Regular Cab 8-ft long bed	2006 Edmunds/KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Extended Cab	6.5	227.6	78.5	73.9	1999 Silverado 1500 Extended Cab short bed / 143.5-in WB	按 KBB Short Bed/143.5 WB 确认，货斗名义按表内 6.5 保留	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000-2004	Extended Cab	6.5	227.7	78.5	73.9	2000/2001/2002/2003/2004 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2000-2004 6.5-ft/143.5 WB 逐年确认，取 227.7/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	6.5	227.7	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2005/2006 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed	按 1999 Edmunds/KBB 8-ft/157.5 WB 与 2000 既有参考确认，取 246.7/73.7 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001-2002	Extended Cab	8.0	246.6	78.5	73.7	2001/2002 Silverado 1500 Extended Cab 8-ft long bed	2001 KBB 与 2002 Edmunds 均确认 8-ft/157.5 WB，取高度安全值 73.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003	Extended Cab	8.0	246.7	78.5	73.7	待补 2003 Silverado 1500 Extended Cab 8-ft long bed	KBB 明确列出 2003 Extended Cab 8-ft 版本，但外廓尺寸仍需确认	待终核: 缺失 2003 8-ft 外廓尺寸参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Extended Cab	8.0	246.6	78.5	73.7	2004 Silverado 1500 Extended Cab 8-ft long bed	按 Edmunds/KBB 8-ft/157.5 WB 确认，取高度安全值 73.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	8.0	249.0	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 8-ft long bed	按 KBB 2005/2006 8-ft trim 确认，取 249.0/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

优先核对 gen1 Extended Cab 8.0 的 2003 外廓尺寸，确认后该组可闭环。

最后处理 gen1 Regular Cab 8.0 的 1999/2000/2002/2003/2004 口径冲突，重点确认 8-ft trim 外廓是否应修正为 222.1/224.5/227.6。

下一步


--- Round 18 / 下一步 ---
更新点

本轮补强 gen1 Extended Cab 8.0 的最后缺口：KBB 2003 Extended Cab 规格页明确 8-ft 版本 Overall Length 为 246.6 in；因此 2001-2004 Extended Cab 8.0 可合并为连续可入库区间。
Kbb.com

2005-2006 Extended Cab 8.0 继续保持独立区间，因为 2005/2006 8-ft trim 已确认长度为 249.0 in，明显大于 2001-2004。

2003 Regular Cab 8.0 已用 KBB 规格页确认 8-ft 口径 Overall Length 为 222.1 in，因此从待终核改为可入库。
Kbb.com

2002 Regular Cab 8.0 已确认 Edmunds Base trim 为 97.6 in bed，但当前可读结果未直接给出外廓长宽高，仍保留待终核。
Edmunds

1999/2000 Regular Cab 8.0 仍存在口径冲突：KBB 1999 默认 Regular Cab 显示 203.1 in / 6.0 ft bed，而 Edmunds 1999 Regular Cab 搜索结果又显示 246.7 in，疑似混入 Extended Cab 或页面口径错配，不能入库。
Kbb.com
+1

当前批次进度
当前批次由上一轮 31 行整理为 29 行。已完成：Colorado 2 行、Silverado 1500 gen2 全部、gen1 Crew Cab 5.8 全部、gen1 Extended Cab 6.5 全部、gen1 Extended Cab 8.0 全部、gen1 Regular Cab 8.0 的 2001/2003/2005/2006。剩余待终核仅集中在 gen1 Regular Cab 8.0 的 1999/2000/2002/2004 口径冲突。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Regular Cab	8.0	227.6	78.5	73.9	待补 1999/2000 Silverado 1500 Regular Cab 8-ft long bed	原 227.6 口径疑似非 Regular Cab 8-ft 或混入其他 cab，需重核	待终核: 1999/2000 当前来源显示 203.1/203.3 更像短床，另有 246.7 疑似混入 Extended Cab，需确认真实 8-ft trim 外廓
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001	Regular Cab	8.0	222.1	78.5	71.0	2001 Silverado 1500 Regular Cab 8-ft long bed	2001 Edmunds 口径为 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2002	Regular Cab	8.0	224.5	78.5	73.9	2002 Silverado 1500 Regular Cab Base 8-ft long bed	已确认 97.6 in bed；外廓长宽高仍需直接来源复核	待终核: 需确认 2002 8-ft trim 外廓是否为 222.1 或 224.5，不能只凭床长入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2003	Regular Cab	8.0	222.1	78.5	71.0	2003 Silverado 1500 Regular Cab 8-ft long bed	按 KBB 8-ft/71 cu.ft bed volume 口径确认 222.1	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Regular Cab	8.0	224.5	78.5	73.9	2004 Silverado 1500 Regular Cab 8-ft long bed	Edmunds 已确认 97.6 in bed，8-ft 配置成立；仍需复核外廓长宽高	待终核: 需确认 2004 8-ft trim 外廓是否为 222.1 或 224.5
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Regular Cab	8.0	224.5	78.5	71.0	2005 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds 224.5/78.5/71.0 与 KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Regular Cab	8.0	224.5	78.5	71.0	2006 Silverado 1500 Regular Cab 8-ft long bed	2006 Edmunds/KBB 8-ft trim 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Extended Cab	6.5	227.6	78.5	73.9	1999 Silverado 1500 Extended Cab short bed / 143.5-in WB	按 KBB Short Bed/143.5 WB 确认，货斗名义按表内 6.5 保留	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000-2004	Extended Cab	6.5	227.7	78.5	73.9	2000/2001/2002/2003/2004 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2000-2004 6.5-ft/143.5 WB 逐年确认，取 227.7/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	6.5	227.7	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2005/2006 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed	按 1999 Edmunds/KBB 8-ft/157.5 WB 与 2000 既有参考确认，取 246.7/73.7 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001-2004	Extended Cab	8.0	246.6	78.5	73.7	2001/2002/2003/2004 Silverado 1500 Extended Cab 8-ft long bed	按 2001-2004 8-ft/157.5 WB 逐年确认，取高度安全值 73.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	8.0	249.0	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 8-ft long bed	按 KBB 2005/2006 8-ft trim 确认，取 249.0/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对

最后只剩 gen1 Regular Cab 8.0：1999/2000/2002/2004 仍需确认真实 8-ft trim 外廓；2003 已可入库但暂不合并，等 2002/2004 口径确定后再决定是否合并为连续区间。

下一步


--- Round 19 / 下一步 ---
更新点

本轮继续补强最后剩余的 gen1 Regular Cab 8.0。

2000 Regular Cab 8.0 ft 已确认 133 in WB / 8 ft box 口径，长 222.2、宽 78.5、高 71.0，因此从 1999-2000 冲突行中拆出并标可入库。
Motor Matchup

2002 Regular Cab 8.0 ft 已确认 Edmunds 明确为 97.6 in bed、133 in WB，长 222.1、宽 78.5、高 71.0，因此改为可入库。
Edmunds

2004 Regular Cab 8.0 ft 已确认 KBB 具体 LS Pickup 2D 8 ft 页面给出 Overall Length 222.1，因此改为可入库。
Kbb.com

1999 Regular Cab 8.0 ft 仍保留待终核：KBB 默认页显示 203.1 in / 6.0 ft bed，Edmunds 另有 227.6 in 结果但口径仍需确认，不能直接入库。
Kbb.com
+1

当前批次进度
当前批次已基本完成；仅剩 1999 Chevrolet Silverado 1500 Regular Cab 8.0 ft 仍待终核。其余 Colorado、Silverado gen2、Silverado gen1 Extended Cab/Crew Cab，以及 gen1 Regular Cab 2000-2006 已可入库。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Regular Cab	8.0	227.6	78.5	73.9	待补 1999 Silverado 1500 Regular Cab 8-ft long bed	1999 KBB 默认页显示 203.1/6.0ft，Edmunds 另有 227.6 结果；需确认是否为真实 Regular Cab 8-ft 口径	待终核: 1999 8-ft trim 外廓仍有 203.1/227.6 口径冲突
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000	Regular Cab	8.0	222.2	78.5	71.0	2000 Silverado 1500 Regular Cab 8-ft long bed	按 133-in WB / 8-ft box 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001-2004	Regular Cab	8.0	222.1	78.5	71.0	2001/2002/2003/2004 Silverado 1500 Regular Cab 8-ft long bed	按 2001-2004 8-ft/133-in WB 逐年确认，取 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Regular Cab	8.0	224.5	78.5	71.0	2005/2006 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds/KBB 8-ft trim 确认，2005-2006 长度高于 2001-2004	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Extended Cab	6.5	227.6	78.5	73.9	1999 Silverado 1500 Extended Cab short bed / 143.5-in WB	按 KBB Short Bed/143.5 WB 确认，货斗名义按表内 6.5 保留	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000-2004	Extended Cab	6.5	227.7	78.5	73.9	2000/2001/2002/2003/2004 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2000-2004 6.5-ft/143.5 WB 逐年确认，取 227.7/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	6.5	227.7	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2005/2006 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed	按 1999 Edmunds/KBB 8-ft/157.5 WB 与 2000 既有参考确认，取 246.7/73.7 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001-2004	Extended Cab	8.0	246.6	78.5	73.7	2001/2002/2003/2004 Silverado 1500 Extended Cab 8-ft long bed	按 2001-2004 8-ft/157.5 WB 逐年确认，取高度安全值 73.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	8.0	249.0	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 8-ft long bed	按 KBB 2005/2006 8-ft trim 确认，取 249.0/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对
最后只剩 1999 Silverado 1500 Regular Cab 8.0：需要确认 1999 是否存在可直接入库的 Regular Cab 8-ft 外廓，或应保守修正为 203.1 短床口径/删除该 8-ft 判断。

下一步


--- Round 20 / 下一步 ---
更新点

本轮处理最后剩余的 1999 Silverado 1500 Regular Cab 8.0。

已确认 1999 KBB 的 Regular Cab Long Bed 口径为 8.00 ft bed、133.0 in wheelbase、Overall Length 222.0 in；因此原表 227.6 更像 1999 Extended Cab short bed / 143.5 in WB 口径，不应继续用于 Regular Cab 8.0。
Kbb.com

1999 Edmunds 的 Regular Cab Base 也给出 227.6 / 143.5 in WB，说明其页面口径与 KBB Long Bed 的 133 in WB 不一致；本轮按更明确的 KBB Long Bed / 8.00 ft 口径修正为 222.0、78.5、71.0，并标可入库。
Edmunds
+1

至此当前批次全部行均已达到“可入库”，不再保留“下一步”。

当前批次进度
当前批次已完成。所有记录均在当前 split 原始年份范围内拆分/修正，未新增 split 外车型、代际或年份；最终 TSV 从 Chevrolet Colorado 开始，到 Chevrolet Silverado 1500 gen2 Extended Cab 结束，保持当前 split 边界。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	ZR2	gen3 midsize pickup	2023-2026	Crew Cab	5.0	212.7	78.1	81.8	2023/2024/2025/2026 Chevrolet Colorado ZR2 Crew Cab 5-ft bed	高车身	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	78.1	79.8	2023/2024/2025/2026 Chevrolet Colorado Trail Boss / Z71 Crew Cab 5-ft bed	含 Trail Boss / Z71 高车身版本	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Regular Cab	8.0	222.0	78.5	71.0	1999 Silverado 1500 Regular Cab 8-ft long bed	按 KBB Long Bed/133-in WB/8.00-ft bed 修正；原 227.6 更像 Extended Cab short bed 口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000	Regular Cab	8.0	222.2	78.5	71.0	2000 Silverado 1500 Regular Cab 8-ft long bed	按 133-in WB / 8-ft box 确认	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001-2004	Regular Cab	8.0	222.1	78.5	71.0	2001/2002/2003/2004 Silverado 1500 Regular Cab 8-ft long bed	按 2001-2004 8-ft/133-in WB 逐年确认，取 222.1/78.5/71.0	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Regular Cab	8.0	224.5	78.5	71.0	2005/2006 Silverado 1500 Regular Cab 8-ft long bed	按 Edmunds/KBB 8-ft trim 确认，2005-2006 长度高于 2001-2004	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999	Extended Cab	6.5	227.6	78.5	73.9	1999 Silverado 1500 Extended Cab short bed / 143.5-in WB	按 KBB Short Bed/143.5 WB 确认，货斗名义按表内 6.5 保留	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2000-2004	Extended Cab	6.5	227.7	78.5	73.9	2000/2001/2002/2003/2004 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2000-2004 6.5-ft/143.5 WB 逐年确认，取 227.7/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	6.5	227.7	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2005/2006 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	1999-2000	Extended Cab	8.0	246.7	78.5	73.7	1999/2000 Silverado 1500 Extended Cab 8-ft long bed	按 1999 Edmunds/KBB 8-ft/157.5 WB 与 2000 既有参考确认，取 246.7/73.7 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2001-2004	Extended Cab	8.0	246.6	78.5	73.7	2001/2002/2003/2004 Silverado 1500 Extended Cab 8-ft long bed	按 2001-2004 8-ft/157.5 WB 逐年确认，取高度安全值 73.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005-2006	Extended Cab	8.0	249.0	78.5	73.9	2005/2006 Silverado 1500 Extended Cab 8-ft long bed	按 KBB 2005/2006 8-ft trim 确认，取 249.0/73.9 安全值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2004	Crew Cab	5.8	230.2	78.5	75.0	2004 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2005	Crew Cab	5.8	225.9	78.5	75.0	2005 Silverado 1500 Crew Cab 5.8-ft short bed	2005 长度低于 2004/2006，单年拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen1 full-size pickup	2006	Crew Cab	5.8	230.2	78.5	75.0	2006 Silverado 1500 Crew Cab 5.8-ft short bed		可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	6.5	205.6	79.9	73.6	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 6.5-ft standard bed	按 2007-2013 6.5-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2013	Regular Cab	8.0	224.5	79.9	73.5	2007/2008/2009/2010/2011/2012/2013 Silverado 1500 Regular Cab 8-ft long bed	按 2007-2013 8-ft trim 逐年确认后合并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007-2008	Crew Cab	5.8	229.9	79.9	73.7	2007/2008 Silverado 1500 Crew Cab 5.8-ft short bed	按 2007-2008 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2010	Crew Cab	5.8	230.2	80.0	73.7	2009/2010 Silverado 1500 Crew Cab 5.8-ft short bed	按 2009-2010 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2011-2013	Crew Cab	5.8	230.2	80.0	73.7	2011/2012/2013 Silverado 1500 Crew Cab 5.8-ft short bed	按 2011-2013 尺寸一致拆分	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2007	Extended Cab	6.5	229.9	79.9	73.7	2007 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6.5-ft trim 确认，归入 2007/2008 尺寸口径	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2008	Extended Cab	6.5	229.9	79.9	73.7	2008 Silverado 1500 Extended Cab 6.5-ft standard bed	2008 单年尺寸低于 2009-2011，单独拆出	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2009-2011	Extended Cab	6.5	230.2	79.9	73.9	2009/2010/2011 Silverado 1500 Extended Cab 6.5-ft standard bed	按 2009-2011 最大高度 73.9 归并	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2 full-size pickup	2012-2013	Extended Cab	6.5	230.2	79.9	73.9	2012/2013 Silverado 1500 Extended Cab 6.5-ft standard bed	按 KBB 6 1/2 ft 版本确认，取高度安全值 73.9	可入库

下一步优先核对
无。当前批次已完成。

本批次完成。

