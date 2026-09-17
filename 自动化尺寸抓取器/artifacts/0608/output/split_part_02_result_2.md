# 文件名：split_part_02.tsv


--- Round 1 / 首次发送 ---
更新点

已补入本轮可核到的 Kia Optima / Rio 三维尺寸。

已将 Kia Optima Hybrid / PHEV 拆成 Hybrid 与 PHEV，并单独拆出 2016 Hybrid carryover。

已修正 Kia Rio Wagon 的分类：原 旅行车 不符合本批字段规则，改为 两厢车，结构仍保留 Wagon。

已把 5-door wagon / 5-door 规范为 5dr。

目前仍有多行只核到首尾或部分年份，不能判可入库；已在 迭代状态 写明缺失年份。

当前批次进度

已处理：Kia Optima、Kia Rio 当前 10 条原始记录。

已拆分后当前输出：12 条。

仍未完成：年份范围内中间年份参考未逐年覆盖的行仍需终核。尺寸依据本轮主要来自 Edmunds/Kia Media/KBB/Cars.com 等结果，其中 2002 Optima、2006/2007/2010 Optima、2011/2015/2016/2020 Optima、2005/2006/2009 Rio 等尺寸页已提供本轮尺寸支撑。
Edmunds
+7
Edmunds
+7
Edmunds
+7

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen1 midsize	2001-2006			186.2	71.7	55.5	2002/2006 Kia Optima Sedan	第一代 Optima sedan；2006 存在新旧车身重叠，当前行仅保留原 gen1 范围内样本	待终核: 缺失 2001/2003/2004/2005 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen2 midsize	2006-2010			189.0	71.1	58.3	2006/2007/2010 Kia Optima Sedan	第二代 Optima sedan；2010 长度较大，取当前已核最大值	待终核: 缺失 2008/2009 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen3 midsize	2011-2015			190.7	72.1	57.3	2011/2015 Kia Optima Sedan	第三代 sedan；2011 高度 57.3，2015 高度 57.1，取当前已核最大值	待终核: 缺失 2012/2013/2014 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen3 midsize	2011-2015			190.7	72.1	57.3	2011 Kia Optima Hybrid	混动版需确认 2012-2015 外形/高度是否同 2011 Hybrid	待终核: 缺失 2012/2013/2014/2015 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen4 midsize	2016-2020			191.1	73.2	57.7	2016/2020 Kia Optima Sedan	第四代 sedan；2021 起 K5 替代	待终核: 缺失 2017/2018/2019 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen3 midsize carryover	2016			190.7	72.1	57.1	2016 Kia Optima Hybrid	2016 Hybrid 为旧车身 carryover，不能并入 2017-2020 gen4 Hybrid	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen4 midsize	2017-2020			191.1	73.2	57.5	2020 Kia Optima Hybrid	Hybrid 新车身需继续补齐 2017-2019	待终核: 缺失 2017/2018/2019 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	PHEV	gen4 midsize	2017-2020			191.1	73.2	57.5	2020 Kia Optima Plug-In Hybrid	PHEV 未按 2016 处理；当前仅核到 2020 样本	待终核: 缺失 2017/2018/2019 年份参考
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen1 subcompact	2001-2005			166.9	66.1	56.7	2005 Kia Rio Sedan	第一代 sedan；当前先以 2005 sedan 样本补尺寸	待终核: 缺失 2001/2002/2003/2004 年份参考
Kia Rio	两厢车	Kia	Rio	Wagon	5dr	gen1 subcompact	2001-2005			166.9	66.1	56.7	2005 Kia Rio Cinco/Wagon	早期 wagon/5-door 后部结构不同；分类由旅行车修正为两厢车	待终核: 缺失 2001/2002/2003/2004 年份参考
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen2 subcompact	2006-2011			166.9	66.7	57.9	2006/2009 Kia Rio Sedan	第二代 sedan；当前已核 2006/2009，取当前已核最大值	待终核: 缺失 2007/2008/2010/2011 年份参考
Kia Rio	两厢车	Kia	Rio	Hatchback	5dr	gen2 subcompact	2006-2011			158.1	66.7	57.9	2006 Kia Rio5 Hatchback	五门 hatchback 后部结构不同；长度与 sedan 不同	待终核: 缺失 2007/2008/2009/2010/2011 年份参考

下一步优先核对

Optima：补齐 2001/2003-2005、2008-2009、2012-2014、2017-2019。

Optima Hybrid/PHEV：重点确认 2017-2019 Hybrid 与 PHEV 是否全为 191.1 / 73.2 / 57.5。

Rio：补齐 gen1 2001-2004 sedan/wagon，以及 gen2 2007-2011 sedan/hatchback。

下一步


--- Round 2 / 下一步 ---
更新点

本轮新增补齐：2017/2018/2019/2020 Kia Optima Sedan Std. 已覆盖完整年份，状态改为可入库。

本轮新增补齐：2017/2018/2019/2020 Kia Optima Hybrid 与 2017/2018/2019/2020 Kia Optima PHEV 已覆盖完整年份，状态改为可入库。

本轮新增补强：2007/2009/2011 Kia Rio Sedan 与 2007/2009 Kia Rio5 Hatchback，Rio gen2 缺失年份范围缩小。

修正 Rio gen2 Hatchback 长度：此前 158.1 适合 Rio5，美国 2007 Rio5 为 158.1 in；部分非美/资料源出现 157.1，不覆盖本批美国口径，暂保留 158.1。

当前批次进度

当前批次原始 10 行，拆分后 12 行。

已可入库：4 行。

仍待终核：8 行，主要集中在 Optima 早期年份、Optima gen3 中间年份、Rio gen1、Rio gen2 的 2008/2010 或 2001-2004 逐年覆盖。

本轮关键尺寸依据：2017/2019/2020 Optima 标准版 Kia Media 均为 191.1 / 73.2 / 57.7；2017/2018/2019/2020 Optima Hybrid/PHEV Kia Media 均为 191.1 / 73.2 / 57.5；2007/2009/2011 Rio sedan 为 166.9 / 66.7 / 57.9，2007 Rio5 为 158.1 / 66.7 / 57.9。
Edmunds
+12
Kia Media
+12
Kia Media
+12

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen1 midsize	2001-2006			186.2	71.7	55.5	2002/2006 Kia Optima Sedan	第一代 Optima sedan；2006 存在新旧车身重叠，当前行仅保留原 gen1 范围内样本	待终核: 缺失 2001/2003/2004/2005 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen2 midsize	2006-2010			189.0	71.1	58.3	2006/2007/2010 Kia Optima Sedan	第二代 Optima sedan；2010 长度较大，取当前已核最大值	待终核: 缺失 2008/2009 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen3 midsize	2011-2015			190.7	72.1	57.3	2011/2012/2013/2014/2015 Kia Optima Sedan	第三代 sedan；2011 高度 57.3，2014-2015 高度 57.1，取当前已核最大值	待终核: 2012/2013 仍需补充外部尺寸明细页复核
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen3 midsize	2011-2015			190.7	72.1	57.3	2011/2012/2013/2014 Kia Optima Hybrid	混动版需确认 2015 外形/高度是否同 2011-2014 Hybrid	待终核: 缺失 2015 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen4 midsize	2016-2020			191.1	73.2	57.7	2016/2017/2018/2019/2020 Kia Optima Sedan	第四代 sedan；2021 起 K5 替代	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen3 midsize carryover	2016			190.7	72.1	57.1	2016 Kia Optima Hybrid	2016 Hybrid 为旧车身 carryover，不能并入 2017-2020 gen4 Hybrid	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen4 midsize	2017-2020			191.1	73.2	57.5	2017/2018/2019/2020 Kia Optima Hybrid	Hybrid 新车身；2017-2020 已逐年覆盖	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	PHEV	gen4 midsize	2017-2020			191.1	73.2	57.5	2017/2018/2019/2020 Kia Optima Plug-In Hybrid	PHEV 新车身；2017-2020 已逐年覆盖	可入库
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen1 subcompact	2001-2005			166.9	66.1	56.7	2005 Kia Rio Sedan	第一代 sedan；当前先以 2005 sedan 样本补尺寸	待终核: 缺失 2001/2002/2003/2004 年份参考
Kia Rio	两厢车	Kia	Rio	Wagon	5dr	gen1 subcompact	2001-2005			166.9	66.1	56.7	2005 Kia Rio Cinco/Wagon	早期 wagon/5-door 后部结构不同；分类由旅行车修正为两厢车	待终核: 缺失 2001/2002/2003/2004 年份参考
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen2 subcompact	2006-2011			166.9	66.7	57.9	2006/2007/2009/2011 Kia Rio Sedan	第二代 sedan；当前已核 2006/2007/2009/2011，尺寸稳定	待终核: 缺失 2008/2010 年份参考
Kia Rio	两厢车	Kia	Rio	Hatchback	5dr	gen2 subcompact	2006-2011			158.1	66.7	57.9	2006/2007/2009 Kia Rio5 Hatchback	五门 hatchback 后部结构不同；美国 Rio5 长度按 158.1 in 口径	待终核: 缺失 2008/2010/2011 年份参考

下一步优先核对

优先补 Kia Rio gen2：2008/2010 Sedan，2008/2010/2011 Rio5 Hatchback。

其次补 Kia Optima gen1/gen2：2001/2003/2004/2005、2008/2009。

最后补 Kia Optima gen3 Hybrid：2015 Hybrid；以及 gen3 Std. 的 2012/2013 外部尺寸明细页确认。

下一步


--- Round 3 / 下一步 ---
更新点

本轮补齐 Kia Optima gen2 Std. 的 2008/2009，状态改为可入库；但发现 2008 为 186.4 in、2009/2010 为 189.0 in，所以该行最大长度仍取 189.0。

本轮补齐 Kia Optima gen3 Std. 的 2012/2013 明细，状态改为可入库；2011-2015 全段已覆盖。

本轮补齐 Kia Optima gen3 Hybrid 的 2015，状态改为可入库。

本轮补齐 Kia Rio gen2 Sedan 的 2008/2010，状态改为可入库；发现 2010 sedan 长度为 167.3 in，高于 166.9，因此 max_length_in 更新为 167.3。

本轮补齐 Kia Rio gen2 Hatchback/Rio5 的 2010/2011；发现 2010 Rio5 长度 158.5 in，高于 158.1，因此 max_length_in 更新为 158.5；仍缺 2008 Rio5 年份参考，暂不能入库。

尺寸补强依据包括 Edmunds、Kia Media、Car and Driver、KBB/Cars.com 等公开规格页；例如 2008 Optima 为 186.4/71.1/58.3，2009 Optima 为 189.0/71.1/58.3，2013 Optima 为 190.7/72.1/57.3，2015 Optima Hybrid 为 190.7/72.1/57.1，2011 Rio5 为 158.1/66.7/57.9。
Car and Driver
+4
Edmunds
+4
Car and Driver
+4

当前批次进度

当前批次原始 10 行，拆分后 12 行。

已可入库：8 行。

仍待终核：4 行。

剩余缺口集中在：Optima gen1 的 2001/2003/2004/2005，Rio gen1 的 2001-2004 sedan/wagon，Rio gen2 Hatchback 的 2008 Rio5。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen1 midsize	2001-2006			186.2	71.7	55.5	2002/2006 Kia Optima Sedan	第一代 Optima sedan；2006 存在新旧车身重叠，当前行仅保留原 gen1 范围内样本	待终核: 缺失 2001/2003/2004/2005 年份参考
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen2 midsize	2006-2010			189.0	71.1	58.3	2006/2007/2008/2009/2010 Kia Optima Sedan	第二代 Optima sedan；2008 为 186.4 in，2009-2010 为 189.0 in，取当前全段最大值	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen3 midsize	2011-2015			190.7	72.1	57.3	2011/2012/2013/2014/2015 Kia Optima Sedan	第三代 sedan；2011-2013 高度 57.3，2014-2015 高度 57.1，取全段最大值	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen3 midsize	2011-2015			190.7	72.1	57.3	2011/2012/2013/2014/2015 Kia Optima Hybrid	混动版；2015 Kia Media 宽 72.1，Edmunds/KBB 有 72.0 口径，按最大安全值 72.1	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen4 midsize	2016-2020			191.1	73.2	57.7	2016/2017/2018/2019/2020 Kia Optima Sedan	第四代 sedan；2021 起 K5 替代	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen3 midsize carryover	2016			190.7	72.1	57.1	2016 Kia Optima Hybrid	2016 Hybrid 为旧车身 carryover，不能并入 2017-2020 gen4 Hybrid	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen4 midsize	2017-2020			191.1	73.2	57.5	2017/2018/2019/2020 Kia Optima Hybrid	Hybrid 新车身；2017-2020 已逐年覆盖	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	PHEV	gen4 midsize	2017-2020			191.1	73.2	57.5	2017/2018/2019/2020 Kia Optima Plug-In Hybrid	PHEV 新车身；2017-2020 已逐年覆盖	可入库
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen1 subcompact	2001-2005			166.9	66.1	56.7	2005 Kia Rio Sedan	第一代 sedan；当前先以 2005 sedan 样本补尺寸	待终核: 缺失 2001/2002/2003/2004 年份参考
Kia Rio	两厢车	Kia	Rio	Wagon	5dr	gen1 subcompact	2001-2005			166.9	66.1	56.7	2005 Kia Rio Cinco/Wagon	早期 wagon/5-door 后部结构不同；分类由旅行车修正为两厢车	待终核: 缺失 2001/2002/2003/2004 年份参考
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen2 subcompact	2006-2011			167.3	66.7	57.9	2006/2007/2008/2009/2010/2011 Kia Rio Sedan	第二代 sedan；2010 长度 167.3 in，高于其余已核年份 166.9 in，取全段最大值	可入库
Kia Rio	两厢车	Kia	Rio	Hatchback	5dr	gen2 subcompact	2006-2011			158.5	66.7	57.9	2006/2007/2009/2010/2011 Kia Rio5 Hatchback	五门 hatchback 后部结构不同；2010 Rio5 长度 158.5 in，2011 Rio5 长度 158.1 in，取当前已核最大值	待终核: 缺失 2008 年份参考

下一步优先核对

优先补 Kia Rio gen2 Hatchback 2008 Rio5，该行补齐后可入库。

继续补 Kia Optima gen1 Std. 的 2001/2003/2004/2005。

继续补 Kia Rio gen1 Sedan/Wagon 的 2001/2002/2003/2004。

下一步


--- Round 4 / 下一步 ---
更新点

本轮补齐 Kia Optima gen1 Std. 的 2001/2003/2004/2005 缺口，状态改为可入库。

Kia Optima gen1 Std. 尺寸从 186.2 / 71.7 / 55.5 更新为更安全的最大口径 186.8 / 72.0 / 55.9；原因是 2001-2005 资料存在 185.8/186.2/186.8、71.5/71.7/72.0、55.5/55.9 多口径，按车罩安全最大值取值。2001 Cars.com 给出约 186/72/56，2004 Edmunds 给出 185.8/71.5/55.5，2003-2006 AutoEvolution 给出 186.2/71.7/55.5，iFixit 2001-2005 汇总给出 186.8/72.0/55.9。
iFixit
+3
Cars.com
+3
Edmunds
+3

本轮补齐 Kia Rio gen1 Sedan/Wagon 的 2001/2002/2003/2004 缺口，状态改为可入库。

Kia Rio gen1 Sedan/Wagon 宽度从 66.1 修正为 65.9，因为 66.1 更像 KBB 的 with mirrors/展示口径，Edmunds/Consumer Guide/Automobile-Catalog 的 without mirrors 或基础宽度口径为 65.9；长度保留安全最大 166.9。
Edmunds
+2
Consumer Guide Auto
+2

本轮补齐 Kia Rio gen2 Hatchback/Rio5 的 2008，状态改为可入库。

当前 12 行已全部可入库。

当前批次进度

当前批次原始 10 行，拆分后 12 行。

已可入库：12 行。

待终核：0 行。

当前批次已完成，下面 TSV 可直接替换 split_part_02 当前批次内容。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen1 midsize	2001-2006			186.8	72.0	55.9	2001/2002/2003/2004/2005/2006 Kia Optima Sedan	第一代 Optima sedan；2001-2006 存在 185.8/186.2/186.8 与 71.5/71.7/72.0 多口径，按车罩安全最大值	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen2 midsize	2006-2010			189.0	71.1	58.3	2006/2007/2008/2009/2010 Kia Optima Sedan	第二代 Optima sedan；2008 为 186.4 in，2009-2010 为 189.0 in，取当前全段最大值	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen3 midsize	2011-2015			190.7	72.1	57.3	2011/2012/2013/2014/2015 Kia Optima Sedan	第三代 sedan；2011-2013 高度 57.3，2014-2015 高度 57.1，取全段最大值	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen3 midsize	2011-2015			190.7	72.1	57.3	2011/2012/2013/2014/2015 Kia Optima Hybrid	混动版；2015 Kia Media 宽 72.1，Edmunds/KBB 有 72.0 口径，按最大安全值 72.1	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Std.	gen4 midsize	2016-2020			191.1	73.2	57.7	2016/2017/2018/2019/2020 Kia Optima Sedan	第四代 sedan；2021 起 K5 替代	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen3 midsize carryover	2016			190.7	72.1	57.1	2016 Kia Optima Hybrid	2016 Hybrid 为旧车身 carryover，不能并入 2017-2020 gen4 Hybrid	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	Hybrid	gen4 midsize	2017-2020			191.1	73.2	57.5	2017/2018/2019/2020 Kia Optima Hybrid	Hybrid 新车身；2017-2020 已逐年覆盖	可入库
Kia Optima	三厢车	Kia	Optima	Sedan	PHEV	gen4 midsize	2017-2020			191.1	73.2	57.5	2017/2018/2019/2020 Kia Optima Plug-In Hybrid	PHEV 新车身；2017-2020 已逐年覆盖	可入库
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen1 subcompact	2001-2005			166.9	65.9	56.7	2001/2002/2003/2004/2005 Kia Rio Sedan	第一代 sedan；基础尺寸多源为 165.9/65.9/56.7，部分 2004/2005 样本长度 166.9，按安全最大长度	可入库
Kia Rio	两厢车	Kia	Rio	Wagon	5dr	gen1 subcompact	2001-2005			166.9	65.9	56.7	2001/2002/2003/2004/2005 Kia Rio Cinco/Wagon	早期 wagon/5-door 后部结构不同；分类由旅行车修正为两厢车；宽度按 without mirrors 65.9	可入库
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen2 subcompact	2006-2011			167.3	66.7	57.9	2006/2007/2008/2009/2010/2011 Kia Rio Sedan	第二代 sedan；2010 长度 167.3 in，高于其余已核年份 166.9 in，取全段最大值	可入库
Kia Rio	两厢车	Kia	Rio	Hatchback	5dr	gen2 subcompact	2006-2011			158.5	66.7	57.9	2006/2007/2008/2009/2010/2011 Kia Rio5 Hatchback	五门 hatchback 后部结构不同；2010 Rio5 长度 158.5 in，2011 Rio5 长度 158.1 in，取全段最大值	可入库

下一步优先核对

无。当前 split_part_02 本批次 12 行已全部可入库。

本批次完成

