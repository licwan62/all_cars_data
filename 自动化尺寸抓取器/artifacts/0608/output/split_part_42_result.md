# 文件名：split_part_42.tsv


--- Round 1 / 首次发送 ---
更新点：

拆分所有 HD pickup 年份范围中的驾驶室/货斗组合，确保每条记录独立对应具体年份段，参考车型覆盖完整。

修正迭代状态：当前 TSV 内参考车型未覆盖中间年份的均标记为“待终核: 缺失年份范围”。

保留原备注、代际修正信息。

本轮更新后的 TSV：

主车型 分类 品牌 车型名 结构 版本 代际 年份区间 驾驶室类型 货斗长度_ft max_length_in max_width_in max_height_in 参考车型 备注 迭代状态
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen2 HD pickup 1994-2002 crew 8.0 260.8 79.4 78.5 Ram HD Crew Cab 8 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen3 HD pickup 2003-2005 crew 8.0 260.8 79.4 78.5 Ram HD Crew Cab 8 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen3 HD pickup 2006-2009 crew 8.0 260.8 79.4 78.5 Ram HD Crew Cab 8 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen4 HD pickup 2010-2018 crew 8.0 260.8 79.4 78.5 Ram HD Crew Cab 8 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen5 HD pickup 2019-2026 crew 8.0 260.8 79.4 78.5 Ram HD Crew Cab 8 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen3 HD pickup 2006-2009 crew 6.4 249.9 79.4 78.5 Ram HD Mega Cab 6.4 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen4 HD pickup 2010-2018 crew 6.4 249.9 79.4 78.5 Ram HD Mega Cab 6.4 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen5 HD pickup 2019-2026 crew 6.4 249.9 79.4 78.5 Ram HD Mega Cab 6.4 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen4 HD pickup 2010-2018 crew 6.4 237.4 79.4 78.5 Ram HD Crew Cab 6.4 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 2500/3500 皮卡 Ram 2500/3500 Pickup Std. gen5 HD pickup 2019-2026 crew 6.4 237.4 79.4 78.5 Ram HD Crew Cab 6.4 ft SRW HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围
Ram 3500 皮卡 Ram 3500 Pickup DRW gen2 HD pickup 1994-2002 crew 8.0 260.8 96.5 79.3 2026 Stellantis Fleet Ram 3500 Crew Cab 8' Box DRW 宽体后双轮; 代际已修；尺寸待按本代/驾驶室/货斗终核 待终核: 缺失年份范围

下一步优先核对：

Ram 2500/3500 各代 Mega Cab 与 Crew Cab 6.4 / 8.0 ft 参考车型是否完整覆盖 2006-2026 年间每一年

Ram 3500 DRW 参考车型覆盖 1994-2002 是否逐年核对

核对 max_length_in、max_width_in、max_height_in 是否与实际每代 HD / Crew / Mega Cab / DRW 对应

下一步


--- Round 2 / 下一步 ---
更新点

已按当前 split 原始边界顺序恢复输出，不再把 gen2 行提前。

分类 统一修正为规则要求的 皮卡。

驾驶室类型 从笼统 crew 拆正为 Crew Cab / Mega Cab。

参考车型从泛称补强为带年份段、车型、驾驶室、货斗、SRW/DRW 的格式。

对仍未逐年完整覆盖的区间，迭代状态改为具体缺失年份范围。

2019-2026 Crew Cab 6.4 ft 行尺寸按当前代 Crew Cab 6'4" Box 逻辑修正为 238.8 长度；2019-2026 Crew Cab 8.0 ft 保持 260.8；Mega Cab 6.4 ft 保持 249.9。

当前批次进度

当前 10 条记录均已字段规范化。

本轮完成：分类、驾驶室类型、参考车型格式、迭代状态具体化。

未完成：1994-2018 部分年份仍缺逐年参考；2010-2018 Crew Cab 8.0 ft 与 Mega Cab 6.4 ft 仍需逐年尺寸终核；1994-2002 DRW 不能用 2026 参考车型覆盖，已改回待终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen4 HD pickup	2010-2018	Crew Cab	6.4	237.4	79.4	78.5	2010-2018 Ram 2500/3500 Crew Cab 6.4 ft Box SRW	HD SRW; 代际已修；Crew Cab短货斗；尺寸待按2010-2018逐年终核	待终核: 缺失2011/2012/2013/2014/2015/2016/2017逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen5 HD pickup	2019-2026	Crew Cab	6.4	238.8	79.4	80.2	2019-2026 Ram 2500/3500 Crew Cab 6.4 ft Box SRW	HD SRW; 代际已修；Crew Cab短货斗；2019+外长按新一代Crew Cab短箱修正	待终核: 缺失2020/2021/2022/2023/2024/2025逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen2 HD pickup	1994-2002	Crew Cab	8.0	260.8	79.4	78.5	1994-2002 Dodge Ram 2500/3500 Crew Cab 8.0 ft Box SRW	HD SRW; 代际已修；早期Crew/Quad命名需终核；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失1994/1995/1996/1997/1998/1999/2000/2001/2002逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen3 HD pickup	2003-2009	Crew Cab	8.0	260.8	79.4	78.5	2003-2009 Dodge Ram 2500/3500 Crew Cab 8.0 ft Box SRW	HD SRW; 代际已修；2003-2009 HD长货斗；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失2004/2005/2006/2007/2008逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen4 HD pickup	2010-2018	Crew Cab	8.0	260.8	79.4	78.5	2010-2018 Ram 2500/3500 Crew Cab 8.0 ft Box SRW	HD SRW; 代际已修；Crew Cab长货斗；尺寸待按2010-2018逐年终核	待终核: 缺失2011/2012/2013/2014/2015/2016/2017逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen5 HD pickup	2019-2026	Crew Cab	8.0	260.8	79.4	78.5	2019-2026 Ram 2500/3500 Crew Cab 8.0 ft Box SRW	HD SRW; 代际已修；Crew Cab长货斗；尺寸待按2019-2026逐年终核	待终核: 缺失2020/2021/2022/2023/2024/2025逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen3 HD pickup	2006-2009	Mega Cab	6.4	249.9	79.4	78.5	2006-2009 Dodge Ram 2500/3500 Mega Cab 6.4 ft Box SRW	HD SRW; 代际已修；Mega Cab短货斗；尺寸待按2006-2009逐年终核	待终核: 缺失2007/2008逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen4 HD pickup	2010-2018	Mega Cab	6.4	249.9	79.4	78.5	2010-2018 Ram 2500/3500 Mega Cab 6.4 ft Box SRW	HD SRW; 代际已修；Mega Cab短货斗；尺寸待按2010-2018逐年终核	待终核: 缺失2011/2012/2013/2014/2015/2016/2017逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen5 HD pickup	2019-2026	Mega Cab	6.4	249.9	79.4	78.5	2019-2026 Ram 2500/3500 Mega Cab 6.4 ft Box SRW	HD SRW; 代际已修；Mega Cab短货斗；尺寸待按2019-2026逐年终核	待终核: 缺失2020/2021/2022/2023/2024/2025逐年参考确认
Ram 3500	皮卡	Ram	3500	Pickup	DRW	gen2 HD pickup	1994-2002	Crew Cab	8.0	260.8	96.5	79.3	1994-2002 Dodge Ram 3500 Crew Cab 8.0 ft Box DRW	宽体后双轮; 代际已修；原2026参考车型不能覆盖1994-2002，已改为本区间参考格式；尺寸待按本代DRW逐年终核	待终核: 缺失1994/1995/1996/1997/1998/1999/2000/2001/2002逐年DRW参考确认

下一步优先核对

优先核对 2019-2026 gen5：Crew Cab 6.4 / Crew Cab 8.0 / Mega Cab 6.4 三组逐年是否可压缩为完整区间。

再核对 2010-2018 gen4：确认 2013/2014 小改款是否影响高度或宽度。

最后核对 1994-2002 gen2 DRW：当前 260.8 很可能偏新代，需重点验证早期 Crew/Club/Quad Cab 8 ft DRW 的真实长度。

下一步


--- Round 3 / 下一步 ---
更新点

本轮重点补强 2019-2026 gen5：Crew Cab 6.4 ft 使用 2026 规格补正为 238.8 / 79.5 / 80.2；Mega Cab 6.4 ft 保持 249.9 / 79.4 / 78.5，与 2026 Edmunds 规格一致。
Peterson Chrysler Dodge Jeep Ram
+1

2010 gen4 Mega Cab 样本显示 248.4 / 79.1 / 74.1，但当前行覆盖 2010-2018，未逐年覆盖，因此暂不直接替换整段最大值，只在备注中标注 2010 样本待拆核。
Edmunds

参考车型改为“已确认样本年份 + 待补区间”写法，避免把未逐年核对的区间误写成完整覆盖。

仍保持当前 split 原始 10 条边界顺序，不新增范围外年份。

当前批次进度

已完成：字段规范、驾驶室类型规范、gen5 Crew Cab 6.4 ft 尺寸补正、Mega Cab 2026 样本确认、部分参考车型改为真实样本年份表达。

待完成：1994-2009 老 Dodge Ram HD、2010-2018 gen4、2019-2025 中间年份仍需逐年补齐，当前不能判定可入库。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen4 HD pickup	2010-2018	Crew Cab	6.4	237.4	79.4	78.5	2010/2014 Ram 2500/3500 Crew Cab 6.4 ft Box SRW	HD SRW; 代际已修；Crew Cab短货斗；2014样本长度237.4，高度77.7；整段最大高度仍待逐年终核	待终核: 缺失2011/2012/2013/2015/2016/2017/2018逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen5 HD pickup	2019-2026	Crew Cab	6.4	238.8	79.5	80.2	2019/2026 Ram 2500/3500 Crew Cab 6.4 ft Box SRW	HD SRW; 代际已修；Crew Cab短货斗；2026样本外长238.8/宽79.5/高80.2；2019样本需继续对应短箱确认	待终核: 缺失2020/2021/2022/2023/2024/2025逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen2 HD pickup	1994-2002	Crew Cab	8.0	260.8	79.4	78.5	1994-2002 Dodge Ram 2500/3500 Crew Cab 8.0 ft Box SRW	HD SRW; 代际已修；早期Crew/Club/Quad命名需终核；当前长度疑似沿用新代，待按1994-2002逐年修正	待终核: 缺失1994/1995/1996/1997/1998/1999/2000/2001/2002逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen3 HD pickup	2003-2009	Crew Cab	8.0	260.8	79.4	78.5	2003/2009 Dodge Ram 2500/3500 Crew Cab 8.0 ft Box SRW	HD SRW; 代际已修；2003-2009 HD长货斗；仅首尾样本格式占位，尺寸待逐年确认	待终核: 缺失2004/2005/2006/2007/2008逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen4 HD pickup	2010-2018	Crew Cab	8.0	260.8	79.4	78.5	2010/2018 Ram 2500/3500 Crew Cab 8.0 ft Box SRW	HD SRW; 代际已修；Crew Cab长货斗；长度260.8需按2010-2018逐年终核	待终核: 缺失2011/2012/2013/2014/2015/2016/2017逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen5 HD pickup	2019-2026	Crew Cab	8.0	260.8	79.4	78.5	2019/2026 Ram 2500/3500 Crew Cab 8.0 ft Box SRW	HD SRW; 代际已修；Crew Cab长货斗；2019样本长箱长度260.8已对齐，宽高仍待逐年确认	待终核: 缺失2020/2021/2022/2023/2024/2025逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen3 HD pickup	2006-2009	Mega Cab	6.4	249.9	79.4	78.5	2006/2009 Dodge Ram 2500/3500 Mega Cab 6.4 ft Box SRW	HD SRW; 代际已修；Mega Cab短货斗；2006-2009仍待逐年核对，避免用后代Mega Cab尺寸直接覆盖	待终核: 缺失2007/2008逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen4 HD pickup	2010-2018	Mega Cab	6.4	249.9	79.4	78.5	2010/2018 Ram 2500/3500 Mega Cab 6.4 ft Box SRW	HD SRW; 代际已修；Mega Cab短货斗；2010样本为248.4/79.1/74.1，整段最大值需继续核对2011-2018	待终核: 缺失2011/2012/2013/2014/2015/2016/2017逐年参考确认
Ram 2500/3500	皮卡	Ram	2500/3500	Pickup	Std.	gen5 HD pickup	2019-2026	Mega Cab	6.4	249.9	79.4	78.5	2019/2026 Ram 2500/3500 Mega Cab 6.4 ft Box SRW	HD SRW; 代际已修；Mega Cab短货斗；2026 Mega Cab样本为249.9/79.4/78.5，2019样本需补齐外部三维	待终核: 缺失2020/2021/2022/2023/2024/2025逐年参考确认
Ram 3500	皮卡	Ram	3500	Pickup	DRW	gen2 HD pickup	1994-2002	Crew Cab	8.0	260.8	96.5	79.3	1994-2002 Dodge Ram 3500 Crew Cab 8.0 ft Box DRW	宽体后双轮; 代际已修；原2026参考车型不能覆盖1994-2002；DRW宽度和高度需按本代逐年终核	待终核: 缺失1994/1995/1996/1997/1998/1999/2000/2001/2002逐年DRW参考确认

下一步优先核对

先核对 2019-2026 gen5 Crew Cab 8.0 ft 与 Mega Cab 6.4 ft 的 2020-2025 中间年份，确认是否可压缩为完整区间。

再核对 2010-2018 gen4 Mega Cab，因为 2010 样本明显低于当前整段最大值，可能需要拆分或修正高度。

最后核对 1994-2002 gen2 Crew Cab / DRW，当前尺寸继承风险最高。

下一步

