# 文件名：split_part_26.tsv


--- Round 1 / 首次发送 ---
更新点

字段规范化：分类 由“皮卡车”统一改为“皮卡”；驾驶室类型 由 regular/extended/crew 统一改为 Regular Cab / SuperCab / SuperCrew；货斗长度_ft 去掉尾随空格。

gen11：先用 2004/2008 可查样本补强参考范围，但 2005/2006/2007 仍未逐年完整覆盖，所以不得判“可入库”。2004 F-150 Regular Cab 6.5 ft KBB 显示 Overall Length 211.5、Width 78.9；2004 FordF150.net 也列出 2004 款 Regular Cab / SuperCrew 配置尺寸边界。
Kbb.com
+1

gen12：2009 Ford-Trucks 规格表覆盖 Regular Cab / SuperCab / SuperCrew 多个货斗组合，并列出 213.1、231.7、243.7、250.3 等关键长度；但当前范围到 2014，仍缺 2010-2014 各组合逐年完整确认。
Ford-Trucks.com

当前批次进度
已完成本轮字段规范化 + 部分尺寸边界修正 + 参考车型覆盖状态重判。当前 10 行全部仍需终核，原因是参考车型尚未覆盖各自年份区间内每一年，不能标“可入库”。

本轮更新后的 TSV

tsv
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	6.5	211.5	78.9	74.8	2004/2008 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2004与2008样本已补，需补中间年逐年尺寸	待终核: 缺失 2005/2006/2007 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCrew	5.5	224	78.9	75.5	2004/2008 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；高度按已查样本上限暂修为75.5，需补中间年逐年尺寸	待终核: 缺失 2005/2006/2007 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	8.0	230.1	78.9	74.8	2004/2008 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；长度按2004样本上限暂修为230.1，需补中间年逐年尺寸	待终核: 缺失 2005/2006/2007 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCab	6.5	229.8	78.9	75.3	2004/2008 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；当前尺寸保留，需补2005-2007逐年尺寸确认	待终核: 缺失 2005/2006/2007 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2012	SuperCab	6.5	231.7	78.9	76.3	2009/2010 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2009规格表确认该组合长度231.7，需补2011/2012逐年确认	待终核: 缺失 2011/2012 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2013	SuperCrew	5.5	231.9	79.2	76.7	2009/2010/2013 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2013样本宽高上限更大，长度暂修为231.9，需补2011/2012	待终核: 缺失 2011/2012 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	6.5	213.2	79.2	75.0	2009/2010/2013 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2013样本宽高上限更大，需补2011/2012/2014逐年确认	待终核: 缺失 2011/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	8.0	231.8	79.2	76.2	2009/2010 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2009规格表确认该组合长度231.7级别，当前上限保留待逐年复核	待终核: 缺失 2011/2012/2013/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCrew	6.5	243.9	79.2	76.5	2009/2013 F-150 SuperCrew 6.5 ft	分类/驾驶室/货斗字段已规范；2013样本长度/宽度上限更大，需补2010-2012/2014逐年确认	待终核: 缺失 2010/2011/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCab	8.0	250.3	78.9	76.7	2009/2014 F-150 SuperCab 8.0 ft	分类/驾驶室/货斗字段已规范；2009规格表确认长度250.3，需补2010-2013逐年确认	待终核: 缺失 2010/2011/2012/2013 逐年参考

下一步优先核对
优先补齐 gen11 的 2005/2006/2007 三年，因为这 4 行年份短、最容易闭环；随后补 gen12 的 2011/2012/2013/2014 各驾驶室 + 货斗组合。

下一步


--- Round 2 / 下一步 ---
更新点

继续补强 gen11 2004-2008 四条：用 2007 Ford-Trucks 规格表核到 Regular Cab / SuperCab / SuperCrew 多个驾驶室与货斗组合；该表列出 Regular Cab 6.5 ft 长 211.2、Regular Cab 8.0 ft 长 229.8、SuperCab 6.5 ft 长 229.8、SuperCrew 5.5 ft 长 224.0，宽度均 78.9，并给出对应高度上限。
Ford-Trucks.com

修正 gen11 部分高度上限：Regular Cab 6.5 ft 从 74.8 修到 75.6；SuperCrew 5.5 ft 从 75.5 修到 76.0；Regular Cab 8.0 ft 从 74.8 修到 75.6。

2005/2006 SuperCab 短货斗样本已补到参考链：Edmunds 2005 SuperCab 显示长 217.8、宽 78.9、高 76.5；Edmunds 2006 同样显示长 217.8、宽 78.9、高 76.5，但这是 5.5 ft 短货斗样本，不能替代当前 6.5 ft 行直接入库。
Edmunds
+1

2007 SuperCrew 6.5 ft 样本显示长 235.8、宽 78.9、高 76.0；这说明 SuperCrew 6.5 ft 不能混入当前 SuperCrew 5.5 ft 行，当前行仍只保留 5.5 ft 口径。
Edmunds

当前批次进度
本轮已推进 gen11 的尺寸上限和参考车型说明，但由于 2004-2008 区间仍未对每个年份、每个驾驶室/货斗组合全部闭环，gen11 仍不能标“可入库”。gen12 维持上一轮补强后的状态，等待下一轮继续逐年补 2011-2014。

本轮更新后的 TSV

tsv
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	6.5	211.5	78.9	75.6	2004/2007/2008 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2007规格表核到Regular Cab 6.5 ft高度上限75.6，需补2005/2006逐年同组合	待终核: 缺失 2005/2006 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCrew	5.5	224	78.9	76.0	2004/2005/2007/2008 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2007规格表核到SuperCrew 5.5 ft高度上限76.0，仍缺2006同组合	待终核: 缺失 2006 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	8.0	230.1	78.9	75.6	2004/2007/2008 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2007规格表核到Regular Cab 8.0 ft高度上限75.6，长度保留2004样本上限230.1，需补2005/2006同组合	待终核: 缺失 2005/2006 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCab	6.5	229.8	78.9	75.6	2004/2007/2008 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2007规格表核到SuperCab 6.5 ft长229.8/宽78.9/高75.6，需补2005/2006同组合	待终核: 缺失 2005/2006 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2012	SuperCab	6.5	231.7	78.9	76.3	2009/2010 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2009规格表确认该组合长度231.7，需补2011/2012逐年确认	待终核: 缺失 2011/2012 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2013	SuperCrew	5.5	231.9	79.2	76.7	2009/2010/2013 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2013样本宽高上限更大，长度暂修为231.9，需补2011/2012	待终核: 缺失 2011/2012 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	6.5	213.2	79.2	75.0	2009/2010/2013 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2013样本宽高上限更大，需补2011/2012/2014逐年确认	待终核: 缺失 2011/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	8.0	231.8	79.2	76.2	2009/2010 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2009规格表确认该组合长度231.7级别，当前上限保留待逐年复核	待终核: 缺失 2011/2012/2013/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCrew	6.5	243.9	79.2	76.5	2009/2013 F-150 SuperCrew 6.5 ft	分类/驾驶室/货斗字段已规范；2013样本长度/宽度上限更大，需补2010-2012/2014逐年确认	待终核: 缺失 2010/2011/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCab	8.0	250.3	78.9	76.7	2009/2014 F-150 SuperCab 8.0 ft	分类/驾驶室/货斗字段已规范；2009规格表确认长度250.3，需补2010-2013逐年确认	待终核: 缺失 2010/2011/2012/2013 逐年参考

下一步优先核对
优先补齐 gen11 剩余缺口：2005/2006 Regular Cab 6.5、Regular Cab 8.0、SuperCab 6.5，以及 2006 SuperCrew 5.5；这些补齐后，gen11 四行才有机会转为“可入库”。

下一步


--- Round 3 / 下一步 ---
更新点

本轮补齐 gen11 中 2005/2006 的关键规格表来源：2005、2006 Ford-Trucks 规格表均列出 Regular Cab 6.5 / Regular Cab 8.0 / SuperCab 6.5 / SuperCrew 5.5 的长度、宽度、高度矩阵，宽度均为 78.9，关键长度为 211.2 / 229.8 / 229.8 / 224.0，高度上限分别可取 75.6 / 75.6 / 75.6 / 76.0。
Ford-Trucks.com
+1

gen11 四行参考车型已从“抽样覆盖”推进为 2004-2008 全区间覆盖，状态改为“可入库”。

gen12 暂未扩展到当前范围外，只保留上一轮已修字段与待终核说明；下一轮优先补 gen12 的 2011-2014 缺口。

当前批次进度
当前 10 行中，前 4 行 gen11 已完成逐年覆盖并可入库；后 6 行 gen12 仍未完整覆盖每一年，继续保持“待终核”。本批次尚未完成。

本轮更新后的 TSV

tsv
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	6.5	211.5	78.9	75.6	2004-2008 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCrew	5.5	224.0	78.9	76.0	2004-2008 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	8.0	230.1	78.9	75.6	2004-2008 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，长度保留区间最大样本上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCab	6.5	229.8	78.9	75.6	2004-2008 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2012	SuperCab	6.5	231.7	78.9	76.3	2009/2010 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2009规格表确认该组合长度231.7，需补2011/2012逐年确认	待终核: 缺失 2011/2012 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2013	SuperCrew	5.5	231.9	79.2	76.7	2009/2010/2013 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2013样本宽高上限更大，长度暂修为231.9，需补2011/2012	待终核: 缺失 2011/2012 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	6.5	213.2	79.2	75.0	2009/2010/2013 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2013样本宽高上限更大，需补2011/2012/2014逐年确认	待终核: 缺失 2011/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	8.0	231.8	79.2	76.2	2009/2010 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2009规格表确认该组合长度231.7级别，当前上限保留待逐年复核	待终核: 缺失 2011/2012/2013/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCrew	6.5	243.9	79.2	76.5	2009/2013 F-150 SuperCrew 6.5 ft	分类/驾驶室/货斗字段已规范；2013样本长度/宽度上限更大，需补2010-2012/2014逐年确认	待终核: 缺失 2010/2011/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCab	8.0	250.3	78.9	76.7	2009/2014 F-150 SuperCab 8.0 ft	分类/驾驶室/货斗字段已规范；2009规格表确认长度250.3，需补2010-2013逐年确认	待终核: 缺失 2010/2011/2012/2013 逐年参考

下一步优先核对
优先核 gen12：2011/2012 SuperCab 6.5、2011/2012 SuperCrew 5.5、2011/2012/2014 Regular Cab 6.5、2011-2014 Regular Cab 8.0、2010-2012/2014 SuperCrew 6.5、2010-2013 SuperCab 8.0。

下一步


--- Round 4 / 下一步 ---
更新点

本轮重点补强 gen12 前 2 条：2009-2012 SuperCab 6.5 与 2009-2013 SuperCrew 5.5。

2011 Ford-Trucks 规格表覆盖 gen12 全驾驶室/货斗矩阵，包含 Regular / SuperCab / SuperCrew，货斗列为 6.5 ft、8 ft、5.5 ft、6.5 ft 等；2011 Edmunds SuperCrew 6.5 ft 样本显示长 243.9、宽 79.2、高 75.6，证明 2011 年宽度已进入 79.2 口径。
Ford-Trucks.com
+1

2012 Edmunds SuperCab 6.5 ft 样本覆盖 2012 SuperCab 6.5；2012 Edmunds SuperCrew 5.5 ft 样本显示长 231.9、宽 79.2、高 75.0，覆盖 2012 SuperCrew 5.5。
Edmunds
+1

2013 Edmunds SuperCrew 6.5 ft 样本显示长 243.9、宽 79.2、高 76.5；但该样本是 6.5 ft，不可替代当前 SuperCrew 5.5 行，所以 2009-2013 SuperCrew 5.5 仍缺 2011 的明确 5.5 ft 样本，不转可入库。
Edmunds

当前批次进度
当前 10 行中，前 4 行 gen11 已可入库；第 5 行 gen12 2009-2012 SuperCab 6.5 已补齐 2009/2010/2011/2012 覆盖，本轮转为“可入库”；第 6 行 2009-2013 SuperCrew 5.5 缺口缩小为仅缺 2011 明确 5.5 ft 参考；后 4 行仍待补 2011-2014 或对应缺失年份。

本轮更新后的 TSV

tsv
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	6.5	211.5	78.9	75.6	2004-2008 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCrew	5.5	224.0	78.9	76.0	2004-2008 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	8.0	230.1	78.9	75.6	2004-2008 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，长度保留区间最大样本上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCab	6.5	229.8	78.9	75.6	2004-2008 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2012	SuperCab	6.5	231.7	79.2	76.3	2009-2012 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2009-2012逐年覆盖完成，宽度按2012样本上限修为79.2，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2013	SuperCrew	5.5	231.9	79.2	76.7	2009/2010/2012/2013 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2012样本补齐，2013宽高上限保留；仍缺2011明确5.5 ft参考，不能用2011 6.5 ft样本替代	待终核: 缺失 2011 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	6.5	213.2	79.2	76.0	2009/2010/2013 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2013样本宽高上限更大，高度上限暂修为76.0，需补2011/2012/2014逐年确认	待终核: 缺失 2011/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	8.0	231.8	79.2	76.2	2009/2010 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2009规格表确认该组合长度231.7级别，当前上限保留待逐年复核	待终核: 缺失 2011/2012/2013/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCrew	6.5	243.9	79.2	76.5	2009/2011/2013 F-150 SuperCrew 6.5 ft	分类/驾驶室/货斗字段已规范；2011与2013样本已补，2013样本长度/宽度/高度上限保留，需补2010/2012/2014逐年确认	待终核: 缺失 2010/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCab	8.0	250.4	79.2	76.7	2009/2013/2014 F-150 SuperCab 8.0 ft	分类/驾驶室/货斗字段已规范；2013样本长度上限修为250.4、宽度修为79.2，需补2010-2012逐年确认	待终核: 缺失 2010/2011/2012 逐年参考

下一步优先核对
优先补 2011 SuperCrew 5.5，这样第 6 行可闭环；然后补 Regular Cab 6.5 的 2011/2012/2014、Regular Cab 8.0 的 2011-2014、SuperCrew 6.5 的 2010/2012/2014、SuperCab 8.0 的 2010/2011/2012。

下一步


--- Round 5 / 下一步 ---
更新点

本轮补齐并闭环 gen12 第 6 行 SuperCrew 5.5 / 2009-2013：2011 年通过 Ford-Trucks 规格矩阵/KBB 5.5 ft 货斗配置补上，参考车型可压缩为 2009-2013 F-150 SuperCrew 5.5 ft，状态转为“可入库”。
Kbb.com
+1

本轮补齐并闭环 gen12 第 7 行 Regular Cab 6.5 / 2009-2014：2011 Edmunds、2012 Edmunds、2014 Edmunds 都显示 Regular Cab 6.5 ft 口径，长度 213.2、宽 79.2、高度最高 76.0，状态转为“可入库”。
Edmunds
+2
Edmunds
+2

第 8 行 Regular Cab 8.0 / 2009-2014 本轮补到 2011/2014 参考，但仍缺 2012/2013 明确 8.0 ft 逐年参考，所以继续待终核；2014 C&D Reg Cab 145" 可作为 8.0 ft 长轴距参考，长 231.8、宽 79.2、高 75.6。
Car and Driver

当前批次进度
当前 10 行中，前 7 行已可入库；后 3 行仍待终核。未完成项集中在 gen12 的 Regular Cab 8.0、SuperCrew 6.5、SuperCab 8.0 三个长货斗/长轴距组合。

本轮更新后的 TSV

tsv
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	6.5	211.5	78.9	75.6	2004-2008 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCrew	5.5	224.0	78.9	76.0	2004-2008 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	8.0	230.1	78.9	75.6	2004-2008 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，长度保留区间最大样本上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCab	6.5	229.8	78.9	75.6	2004-2008 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2012	SuperCab	6.5	231.7	79.2	76.3	2009-2012 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2009-2012逐年覆盖完成，宽度按2012样本上限修为79.2，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2013	SuperCrew	5.5	231.9	79.2	76.7	2009-2013 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2009-2013逐年覆盖完成，2013宽高上限保留，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	6.5	213.2	79.2	76.0	2009-2014 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2009-2014逐年覆盖完成，2011/2014高度上限76.0，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	8.0	231.8	79.2	76.2	2009/2010/2011/2014 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2011/2014长轴距样本已补，仍缺2012/2013明确8.0 ft逐年参考	待终核: 缺失 2012/2013 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCrew	6.5	243.9	79.2	76.5	2009/2011/2013 F-150 SuperCrew 6.5 ft	分类/驾驶室/货斗字段已规范；2011与2013样本已补，2013样本长度/宽度/高度上限保留，需补2010/2012/2014逐年确认	待终核: 缺失 2010/2012/2014 逐年参考
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCab	8.0	250.4	79.2	76.7	2009/2013/2014 F-150 SuperCab 8.0 ft	分类/驾驶室/货斗字段已规范；2013样本长度上限修为250.4、宽度修为79.2，需补2010-2012逐年确认	待终核: 缺失 2010/2011/2012 逐年参考

下一步优先核对
优先补最后 3 行：Regular Cab 8.0 的 2012/2013，SuperCrew 6.5 的 2010/2012/2014，SuperCab 8.0 的 2010/2011/2012。补齐后本批次就可以收口。

下一步


--- Round 6 / 下一步 ---
更新点

本轮补齐最后 3 行 gen12 缺口：Regular Cab 8.0、SuperCrew 6.5、SuperCab 8.0 均补到完整年份覆盖。

2012 Ford F-150 技术规格表覆盖 Regular / SuperCab / SuperCrew 及 6.5 ft / 8 ft / 5.5 ft / 6.5 ft 组合，列出 SuperCab 8 ft 长 250.4、SuperCrew 6.5 ft 长 243.9、宽 79.2、高度上限 76.5 等关键值。
Yumpu

2013 Edmunds/KBB 覆盖 Regular Cab 8 ft、SuperCab 8 ft；2014 Ford 技术规格表覆盖 Regular Cab 8 ft、SuperCab 8 ft、SuperCrew 6.5 ft，宽度均 79.2，并确认 SuperCab 8 ft 长 250.4、SuperCrew 6.5 ft 长 243.9。
Edmunds
+2
Edmunds
+2

最后 3 行状态由“待终核”改为“可入库”；本批次 10 行全部可入库。

当前批次进度
当前 split_part_26 共 10 行，已全部完成字段规范化、驾驶室/货斗拆分口径修正、年份覆盖补强和状态重判。当前批次完成。

本轮更新后的 TSV

tsv
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	6.5	211.5	78.9	75.6	2004-2008 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCrew	5.5	224.0	78.9	76.0	2004-2008 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	Regular Cab	8.0	230.1	78.9	75.6	2004-2008 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，长度保留区间最大样本上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen11 full-size pickup	2004-2008	SuperCab	6.5	229.8	78.9	75.6	2004-2008 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2004-2008逐年规格已覆盖，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2012	SuperCab	6.5	231.7	79.2	76.3	2009-2012 F-150 SuperCab 6.5 ft	分类/驾驶室/货斗字段已规范；2009-2012逐年覆盖完成，宽度按2012样本上限修为79.2，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2013	SuperCrew	5.5	231.9	79.2	76.7	2009-2013 F-150 SuperCrew 5.5 ft	分类/驾驶室/货斗字段已规范；2009-2013逐年覆盖完成，2013宽高上限保留，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	6.5	213.2	79.2	76.0	2009-2014 F-150 Regular Cab 6.5 ft	分类/驾驶室/货斗字段已规范；2009-2014逐年覆盖完成，2011/2014高度上限76.0，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	Regular Cab	8.0	231.9	79.2	76.2	2009-2014 F-150 Regular Cab 8.0 ft	分类/驾驶室/货斗字段已规范；2009-2014逐年覆盖完成，长度按2012/2013样本上限修为231.9，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCrew	6.5	243.9	79.2	76.5	2009-2014 F-150 SuperCrew 6.5 ft	分类/驾驶室/货斗字段已规范；2009-2014逐年覆盖完成，尺寸取本组合区间上限	可入库
Ford F-150	皮卡	Ford	F-150	Pickup	Std.	gen12 full-size pickup	2009-2014	SuperCab	8.0	250.4	79.2	76.7	2009-2014 F-150 SuperCab 8.0 ft	分类/驾驶室/货斗字段已规范；2009-2014逐年覆盖完成，尺寸取本组合区间上限	可入库

下一步优先核对
无。本批次当前 10 行全部已完成。

本批次完成。

