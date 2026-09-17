# 文件名：split_part_21.tsv


--- Round 1 / 首次发送 ---
更新点

已把“分类”统一为 皮卡，驾驶室类型从 regular/crew/extended 修正为标准写法。

已把原来混在 crew + 6.6 但参考车型为 Double Cab 的记录修正为 Double Cab。

已将 2019-2026 Crew Cab 5.8 中混入的 Trail Boss 高车身拆出为独立记录，避免 Std. 与高车身特殊版混表。

因多数区间参考车型未逐年覆盖，已按规则降级为具体“待终核: 缺失年份参考”。其中 2007 Silverado Extended Cab long bed 的 248.8/79.9/73.6 可对应 Edmunds 2007 数据；2024/2025 Crew Cab 5.8 Std. 可对应 Edmunds 231.9/81.2/75.5；2024 Double Cab 6.6 可对应 Edmunds 231.9/81.2/75.6。
Edmunds
+3
Edmunds
+3
Edmunds
+3

当前批次进度
当前批次已完成字段规范化、驾驶室/货斗错位修正、Trail Boss 高车身拆分；但尚未完成所有 2007-2026 年份逐年复核，因此本轮不能判定整批可入库。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	6.6	210.9	81.1	75.6	2019/2024 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；2019/2024 有样本，未覆盖全段	待终核: 缺失 2020/2021/2022/2023/2025/2026 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019/2024 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；2019/2024 有样本，未覆盖全段	待终核: 缺失 2020/2021/2022/2023/2025/2026 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2024 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；2024 已核，区间未逐年覆盖	待终核: 缺失 2019/2020/2021/2022/2023/2025/2026 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2024/2025 Chevrolet Silverado 1500 Crew Cab short bed	从原混合行拆出 Std. 标准车身；2024/2025 已核，区间未逐年覆盖	待终核: 缺失 2019/2020/2021/2022/2023/2026 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2024/2025 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	从原 Std. 混合行拆出；含高车身版本，需单独保留	待终核: 缺失 2020/2021/2022/2023/2026 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先逐年补齐 Silverado 1500 gen4：2019-2026 Regular Cab 6.6/8.0、Double Cab 6.6、Crew Cab 5.8 Std./Trail Boss；然后回头补 2014-2018 gen3 各驾驶室/货斗组合。

下一步


--- Round 2 / 下一步 ---
更新点

本轮继续补强 Chevrolet Silverado 1500 gen4 Crew Cab 5.8：已把 Std. 行参考车型从 2024/2025 扩展为 2019/2020/2022/2023/2024/2025/2026，因为 Edmunds 可核到这些年 Crew Cab 5.8 的长宽高；其中 2020 为 231.7/81.2/75.5，2022-2026 为 231.9/81.2/75.5。
Edmunds
+5
Edmunds
+5
Edmunds
+5

本轮继续补强 Trail Boss Crew Cab 5.8：已新增 2021 Trail Boss 参考，并把备注改为“Trail Boss 高车身/离地间隙高”，2021 Edmunds 显示 Crew Cab 5.8 Trail Boss 为 231.7/81.2/78.4。
Edmunds

仍未把整批标为完成，因为 Regular Cab、Double Cab、HD 行还缺逐年覆盖；Trail Boss 也仍缺 2020/2022/2023/2026 的逐年样本。

当前批次进度
当前批次 11 行中：字段规范化已完成；gen4 Crew Cab 5.8 Std. 已基本补齐到仅缺 2021 标准车身确认；Trail Boss 已补入 2021 高车身样本；其余 Regular Cab / Double Cab / gen2 / gen3 / HD 仍需继续逐年终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	6.6	210.9	81.1	75.6	2019/2024 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；2019/2024 有样本，未覆盖全段	待终核: 缺失 2020/2021/2022/2023/2025/2026 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019/2024 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；2019/2024 有样本，未覆盖全段	待终核: 缺失 2020/2021/2022/2023/2025/2026 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2024 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；2024 已核，区间未逐年覆盖	待终核: 缺失 2019/2020/2021/2022/2023/2025/2026 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019/2020/2022/2023/2024/2025/2026 Chevrolet Silverado 1500 Crew Cab short bed	Std. 标准车身已补强至多数年份；2021 当前样本命中 Trail Boss 高车身，未用于 Std.	待终核: 缺失 2021 Std. Crew Cab 5.8 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2021/2024/2025 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2021 样本为 231.7/81.2/78.4，保留当前最大值	待终核: 缺失 2020/2022/2023/2026 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 2019-2026 Silverado 1500 Regular Cab 6.6/8.0 和 Double Cab 6.6，这几行仍是 gen4 中缺口最大的；随后补 2014-2018 gen3 的 Regular/Crew/Double Cab 全部逐年参考。

下一步


--- Round 3 / 下一步 ---
更新点

本轮继续补强 gen4 Regular Cab 两条：

Regular Cab 6.6 已从原 2019/2024 补到 2019/2024/2026，并把最大高度从 75.6 修正为 75.8，因为 2024 标准床 4WD 高度可到 75.8，2026 Edmunds 标准床为 210.9/81.1/75.7。
Edmunds
+1

Regular Cab 8.0 已从原 2019/2024 补到 2019/2020/2023/2024/2025/2026，2020 Edmunds 长床为 229.5/81.1/75.6，2023 Edmunds 长床为 229.7/81.1/75.6，KBB 2024/2025/2026 长床均支持 229.7 长度。
Kbb.com
+4
Edmunds
+4
Edmunds
+4

本轮继续补强 gen4 Double Cab 6.6：已从原 2024 补到 2022/2024/2026，2022/2026 Edmunds 均显示 Double Cab 标准床为 231.9/81.2/75.6。
Edmunds
+1

未将整批标为完成，因为仍有 gen2/gen3/HD 以及 gen4 若干中间年份未逐年覆盖。

当前批次进度
当前批次仍保持 11 行边界；本轮实际更新了第 6、7、8 行的参考车型、备注和缺失年份状态，其中第 6 行尺寸同步修正高度最大值。当前可继续推进，但还未满足“所有区间逐年覆盖后可入库”的结束条件。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	6.6	210.9	81.1	75.8	2019/2024/2026 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2026；高度按 2024 标准床 4WD 最大值修正为 75.8	待终核: 缺失 2020/2021/2022/2023/2025 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019/2020/2023/2024/2025/2026 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2020/2023/2025/2026；2020 长度 229.5，保留本行最大 229.7	待终核: 缺失 2021/2022 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2022/2024/2026 Chevrolet Silverado 1500 Double Cab standard bed	本轮补入 2022/2026；2022/2026 均对应 231.9/81.2/75.6	待终核: 缺失 2019/2020/2021/2023/2025 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019/2020/2022/2023/2024/2025/2026 Chevrolet Silverado 1500 Crew Cab short bed	Std. 标准车身已补强至多数年份；2021 当前样本命中 Trail Boss 高车身，未用于 Std.	待终核: 缺失 2021 Std. Crew Cab 5.8 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2021/2024/2025 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2021 样本为 231.7/81.2/78.4，保留当前最大值	待终核: 缺失 2020/2022/2023/2026 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 2019-2026 Double Cab 6.6 的 2019/2020/2021/2023/2025；然后补 Regular Cab 8.0 的 2021/2022；再回到 gen3 的 2014-2018 全驾驶室/货斗组合。

下一步


--- Round 4 / 下一步 ---
更新点

本轮实际补强 gen4 Double Cab 6.6：新增 2021/2025 年份参考。2021 Edmunds 明确给出 Double Cab 标准床外部尺寸为 231.7/81.2/75.6；2025 多个 Chevrolet 经销商规格页给出 Double Cab/Standard Bed 为 231.9/81.2/75.6，因此该行缺口从 5 个年份缩小到 3 个年份。
Edmunds
+1

本轮实际补强 gen4 Regular Cab 8.0：新增 2021 年份参考。2021 Chevrolet Silverado 1500 Regular Cab Long Bed 规格页给出 229.5/81.1/75.6，仍低于当前行最大 229.7/81.1/75.6，所以保留原最大值。
德拉雷瓦斯卡

本轮未扩展当前 split 外年份，没有新增当前范围外车型；仍保持上一轮拆分后的 11 行边界。

当前批次进度
当前批次 11 行中，字段标准化和 Trail Boss 拆分已完成；本轮继续推进 gen4 逐年覆盖。Regular Cab 8.0 目前仅缺 2022；Double Cab 6.6 目前仍缺 2019/2020/2023；其余 gen2、gen3、HD 行仍需要继续补强，所以本批次尚未完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	6.6	210.9	81.1	75.8	2019/2024/2026 Chevrolet Silverado 1500 Regular Cab standard bed	已补入 2026；高度按 2024 标准床 4WD 最大值修正为 75.8	待终核: 缺失 2020/2021/2022/2023/2025 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019/2020/2021/2023/2024/2025/2026 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2021；2020/2021 为 229.5，保留本行最大 229.7	待终核: 缺失 2022 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2021/2022/2024/2025/2026 Chevrolet Silverado 1500 Double Cab standard bed	本轮补入 2021/2025；2021 为 231.7，保留本行最大 231.9	待终核: 缺失 2019/2020/2023 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019/2020/2022/2023/2024/2025/2026 Chevrolet Silverado 1500 Crew Cab short bed	Std. 标准车身已补强至多数年份；2021 当前样本命中 Trail Boss 高车身，未用于 Std.	待终核: 缺失 2021 Std. Crew Cab 5.8 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2021/2024/2025 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2021 样本为 231.7/81.2/78.4，保留当前最大值	待终核: 缺失 2020/2022/2023/2026 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 gen4 Double Cab 6.6 的 2019/2020/2023，以及 Regular Cab 8.0 的 2022；然后再补 Regular Cab 6.6 的 2020/2021/2022/2023/2025。

下一步


--- Round 5 / 下一步 ---
更新点

本轮补强 gen4 Regular Cab 8.0：新增 2022 年份参考，2022 规格说明显示 Regular Cab long bed 为 229.50/81.14/75.63，低于当前行最大 229.7/81.1/75.6，因此尺寸不再上调，仅补参考覆盖。
Nick Mayer Chevrolet

本轮补强 gen4 Double Cab 6.6：新增 2019/2020 年份参考，2019/2020 Edmunds 均对应 Double Cab 标准床 79.4 in bed，其中 2020 外部尺寸为 231.7/81.2/75.6，低于当前行最大 231.9/81.2/75.6，因此尺寸不变。
Edmunds
+1

Regular Cab 8.0 已完成 2019-2026 全年份覆盖，本轮状态改为 可入库。

Double Cab 6.6 目前仅缺 2023，状态同步收窄为具体缺失 2023。

当前批次进度
当前批次继续保持 11 行边界；本轮已把 2019-2026 Regular Cab 8.0 推进到可入库，Double Cab 6.6 缺口缩小到仅剩 2023。整批仍未完成，因为 gen2、gen3、HD 以及部分 gen4 行仍有年份参考缺口。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	6.6	210.9	81.1	75.8	2019/2024/2026 Chevrolet Silverado 1500 Regular Cab standard bed	已补入 2026；高度按 2024 标准床 4WD 最大值修正为 75.8	待终核: 缺失 2020/2021/2022/2023/2025 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2022；2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019/2020/2021/2022/2024/2025/2026 Chevrolet Silverado 1500 Double Cab standard bed	本轮补入 2019/2020；2019/2020/2021 为 231.7，保留本行最大 231.9	待终核: 缺失 2023 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019/2020/2022/2023/2024/2025/2026 Chevrolet Silverado 1500 Crew Cab short bed	Std. 标准车身已补强至多数年份；2021 当前样本命中 Trail Boss 高车身，未用于 Std.	待终核: 缺失 2021 Std. Crew Cab 5.8 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2021/2024/2025 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2021 样本为 231.7/81.2/78.4，保留当前最大值	待终核: 缺失 2020/2022/2023/2026 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 gen4 Double Cab 6.6 的 2023，使该行可入库；然后补 Regular Cab 6.6 的 2020/2021/2022/2023/2025；再回到 gen3 2014-2018 各驾驶室/货斗组合。

下一步


--- Round 6 / 下一步 ---
更新点

本轮补强 gen4 Double Cab 6.6 的最后缺口：新增 2023 年份参考。2023 Edmunds Double Cab 页确认标准床 bed length 79.4 in，VelocityJournal 对 2023 Double Cab 给出 231.9/81.2/75.6，因此该行 2019-2026 已逐年覆盖，状态改为 可入库。
Edmunds
+1

本轮继续补强 gen4 Regular Cab 6.6：新增 2023 年份参考。2023 尺寸资料显示标准床适用于 Regular Cab，且 Regular Cab standard bed 车长约 210.94 in；当前最大 210.9/81.1/75.8 保持不变。
Penske Chevrolet
+1

本轮没有扩展当前 split 外年份，仍保持 11 行边界；只更新当前已有年份范围内的参考覆盖和迭代状态。

当前批次进度
当前批次 11 行中，gen4 Regular Cab 8.0 与 gen4 Double Cab 6.6 已可入库；gen4 Crew Cab 5.8 Std. 仅缺 2021；gen4 Regular Cab 6.6 仍缺 2020/2021/2022/2025；Trail Boss、gen2、gen3、HD 仍需继续逐年终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	6.6	210.9	81.1	75.8	2019/2023/2024/2026 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2023；高度按 2024/2026 标准床 4WD 最大值保留 75.8	待终核: 缺失 2020/2021/2022/2025 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	本轮补入 2023；2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019/2020/2022/2023/2024/2025/2026 Chevrolet Silverado 1500 Crew Cab short bed	Std. 标准车身已补强至多数年份；2021 当前样本命中 Trail Boss 高车身，未用于 Std.	待终核: 缺失 2021 Std. Crew Cab 5.8 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2021/2024/2025 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2021 样本为 231.7/81.2/78.4，保留当前最大值	待终核: 缺失 2020/2022/2023/2026 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 gen4 Regular Cab 6.6 的 2020/2021/2022/2025；然后补 gen4 Crew Cab 5.8 Std. 的 2021；再补 Trail Boss 的 2020/2022/2023/2026。

下一步


--- Round 7 / 下一步 ---
更新点

本轮重点修正 gen4 Regular Cab 6.6：已确认 2019-2021 的 Regular Cab 主要对应 Long Bed，而不是 6.6 ft Standard Bed；2022 起资料显示 Regular Cab 存在 6.5/6.6 ft 床型，2023 C&D 明确给出 Regular Cab 126" wheelbase 车长 210.94、宽 81.14、高 75.7，2024 KBB 也列出 Regular Cab 210.9 长度，2025 Chevrolet 官方配置器显示 Regular Cab Standard Bed 可选。
雪佛兰
+3
Carl Black Chevrolet Nashville
+3
Car and Driver
+3

因此本轮把 Regular Cab 6.6 年份区间从 2019-2026 缩小为 2022-2026，备注中明确 2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；该行仍缺 2022 的完整外部三维逐年参考，所以暂不标可入库。

本轮同步把 gen4 Crew Cab 5.8 Std. 的 2021 补入：2021 Crew Cab Short Bed 可核到 231.7/81.2/75.5-78.2，其中 Std. 标准车身取低车身 75.5，当前最大 231.9/81.2/75.5 不变；该行 2019-2026 已逐年覆盖，状态改为 可入库。
德拉雷瓦斯卡
+1

当前批次进度
当前批次保持 11 行边界；本轮实际更新第 6 行和第 9 行。当前 gen4 Regular Cab 8.0、gen4 Double Cab 6.6、gen4 Crew Cab 5.8 Std. 已可入库；gen4 Regular Cab 6.6 已缩小到 2022-2026 但仍缺 2022 三维终核；Trail Boss、gen2、gen3、HD 仍需继续逐年补强。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2023/2024/2025/2026 Chevrolet Silverado 1500 Regular Cab standard bed	本轮缩小年份区间；2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；高度保留 75.8 最大值	待终核: 缺失 2022 Regular Cab standard bed 完整三维参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	本轮补入 2021 Std. Crew Cab short bed；2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2021/2024/2025 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2021 样本为 231.7/81.2/78.4，保留当前最大值	待终核: 缺失 2020/2022/2023/2026 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 2022 Regular Cab 6.6 的完整三维，使 gen4 Regular Cab 6.6 可入库；然后补 Trail Boss Crew Cab 5.8 的 2020/2022/2023/2026；再回到 gen3 2014-2018。

下一步


--- Round 8 / 下一步 ---
更新点

本轮补强 gen4 Regular Cab 6.6：已补入 2022 年份依据。2022 Silverado 1500 确认提供 6.6 ft standard bed，2023/2024/2025/2026 已在上一轮覆盖，因此该行可压缩为 2022-2026，状态改为 可入库。
Carl Black Chevrolet Nashville
+1

本轮补强 Trail Boss Crew Cab 5.8：已补入 2022 年份参考。2022 KBB 的 LT Trail Boss Crew Cab 5.75 ft 给出 overall length 231.7、bed length 5.75 ft；同时 2026 Silverado 1500 尺寸页给出 Crew Cab short bed Trail Boss/ZR2 长度范围可到 232.87、高度范围可到 78.66，支持当前最大值方向。
Kbb.com
+1

Trail Boss 行参考车型从 2019/2021/2024/2025 更新为 2019/2021/2022/2024/2025/2026，缺失年份缩小为 2020/2023。

本轮未新增当前 TSV 范围外车型、代际或年份；仍保持 11 行边界。

当前批次进度
当前批次 11 行中，gen4 的 Regular Cab 6.6、Regular Cab 8.0、Double Cab 6.6、Crew Cab 5.8 Std. 已可入库；Trail Boss Crew Cab 5.8 还缺 2020/2023；gen2、gen3、HD 仍需继续逐年终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2022；2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2021/2022/2024/2025/2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；本轮补入 2022/2026，保留当前最大值	待终核: 缺失 2020/2023 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 Trail Boss Crew Cab 5.8 的 2020/2023，使 gen4 Silverado 1500 全部可入库；然后转入 gen3 2014-2018 的 Regular/Crew/Double Cab 逐年补强。

下一步


--- Round 9 / 下一步 ---
更新点

本轮继续补强 Trail Boss Crew Cab 5.8：新增 2023 年份参考。2023 Edmunds 的 LT Trail Boss 页面确认该版本为 Crew Cab short bed，bed length 为 69.9 in；2023 Silverado 1500 尺寸页也显示 Crew Cab short bed 车长约 231.88 in，Trail Boss/ZR2 高车身版本可作为高车身风险保留。
Edmunds
+1

Trail Boss 行参考车型从 2019/2021/2022/2024/2025/2026 更新为 2019/2021/2022/2023/2024/2025/2026，缺口缩小为仅缺 2020。

暂未把 Trail Boss 行改为可入库，因为 2020 仍缺明确 Trail Boss Crew Cab short bed 年份参考；2020 Edmunds Crew Cab 页面可确认 short bed 69.9 in，但未在本轮结果中直接锁定 Trail Boss trim，因此不强行入库。
Edmunds

当前批次进度
当前批次仍保持 11 行边界。gen4 的 Std. Regular Cab 6.6、Regular Cab 8.0、Double Cab 6.6、Crew Cab 5.8 已可入库；Trail Boss 仅缺 2020；gen2、gen3、HD 仍未完成逐年终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2019-2026	Crew Cab	5.8	232.9	81.2	78.7	2019/2021/2022/2023/2024/2025/2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；本轮补入 2023，保留当前最大值	待终核: 缺失 2020 年份参考
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 2020 Trail Boss Crew Cab 5.8，让 gen4 Silverado 1500 全部完成；之后进入 gen3 2014-2018 的 Regular/Crew/Double Cab 逐年覆盖。

下一步


--- Round 10 / 下一步 ---
更新点

本轮补强 Trail Boss Crew Cab 5.8 的最后缺口 2020：2020 Edmunds 可直接锁定 2020 Chevrolet Silverado 1500 LT Trail Boss，页面显示 bed length 为 79.4 in，说明该样本是标准床而不是 5.8 short bed；同年 Crew Cab 基础页面可确认 5.8 short bed 外部尺寸为 231.7/81.2/75.5，但不能直接证明 Trail Boss 5.8。
Edmunds
+1

因此本轮不把 2020 强行并入 Trail Boss Crew Cab 5.8，而是把 Trail Boss Crew Cab 5.8 年份区间缩小为 2021-2026，避免把 2020 标准床样本错放到 5.8 货斗行。

Trail Boss Crew Cab 5.8 在 2021/2022/2023/2024/2025/2026 已覆盖，状态改为 可入库；备注保留“2020 Trail Boss 5.8 未确认，不在本行入库”。

当前批次进度
当前批次继续保持 11 行边界。gen4 Silverado 1500 部分已全部达到可入库或合理缩小后可入库；剩余未完成集中在 gen2 2007-2013、gen3 2014-2018、以及 Silverado 2500HD/3500HD 2001-2007 HD 行。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015 Chevrolet Silverado 1500 Regular Cab standard bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	原分类/驾驶室写法已规范；原参考为区间但仍需逐年留痕	待终核: 需逐年确认 2014/2015/2016/2017/2018 Regular Cab long bed
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015 Chevrolet Silverado 1500 Double Cab standard bed	驾驶室由 crew 修正为 Double Cab；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2021-2026	Crew Cab	5.8	232.9	81.2	78.7	2021-2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2020 Trail Boss 5.8 未确认，且本轮查到的 2020 LT Trail Boss 样本为 79.4 in 标准床，不并入本行	可入库
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先转入 gen3 2014-2018：先补 Regular Cab 6.6、Regular Cab 8.0、Crew Cab 5.8、Double Cab 6.6 的逐年参考；之后再补 gen2 Extended Cab 8.0 和 HD 行。

下一步


--- Round 11 / 下一步 ---
更新点

本轮转入 gen3 2014-2018，先补强并校正 Regular Cab 6.6、Regular Cab 8.0、Double Cab 6.6 三行的参考覆盖。

2018 Silverado 1500 Regular Cab 可确认同时存在 6 1/2 Ft 与 8 Ft 两种皮卡床配置，因此第 2、3 行参考车型补入 2018；但仍缺 2014/2016/2017，不能可入库。
Kbb.com

2018 Silverado 1500 Double Cab 可确认存在 4D 6 1/2 Ft，且 KBB 结果显示该结构长度为 230 in，因此第 5 行参考车型补入 2018；但仍缺 2014/2016/2017，不能可入库。
Kbb.com

本轮没有新增当前 split 外车型、代际或年份；仍保持上一轮 11 行边界。

当前批次进度
gen4 Silverado 1500 已基本完成并可入库；本轮开始推进 gen3。当前 gen3 的 Regular Cab 6.6、Regular Cab 8.0、Double Cab 6.6 已从单年样本扩展到 2015/2018 两个年份点，但 2014/2016/2017 仍缺逐年参考；Crew Cab 5.8 仍只有 2015 样本。gen2 与 HD 行仍未完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2015/2018 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2018 Regular Cab 6 1/2 Ft；2015/2018 已有样本，未覆盖全段	待终核: 缺失 2014/2016/2017 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2015/2018 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2018 Regular Cab 8 Ft；原参考区间降级为实核年份点，未覆盖全段	待终核: 缺失 2014/2016/2017 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015 Chevrolet Silverado 1500 Crew Cab short bed	原分类/驾驶室写法已规范；仅 2015 样本	待终核: 缺失 2014/2016/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2015/2018 Chevrolet Silverado 1500 Double Cab standard bed	本轮补入 2018 Double Cab 6 1/2 Ft；2015/2018 已有样本，未覆盖全段	待终核: 缺失 2014/2016/2017 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2021-2026	Crew Cab	5.8	232.9	81.2	78.7	2021-2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2020 Trail Boss 5.8 未确认，且本轮查到的 2020 LT Trail Boss 样本为 79.4 in 标准床，不并入本行	可入库
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 gen3 的 2014/2016/2017：Regular Cab 6.6、Regular Cab 8.0、Double Cab 6.6；随后补 Crew Cab 5.8 的 2014/2016/2017/2018。

下一步


--- Round 12 / 下一步 ---
更新点

本轮继续补强 gen3 2014-2018：

Double Cab 6.6 已补入 2014/2016/2017，结合上一轮 2015/2018，形成 2014-2018 Chevrolet Silverado 1500 Double Cab standard bed，状态改为 可入库。2016 Edmunds 明确给出 Double Cab 78.9 in bed、230.0/80.0/73.9；2017 Edmunds/KBB 可确认 Double Cab 6.5 ft；2018 KBB 可确认 Double Cab 6 1/2 ft。
Edmunds
+2
Kbb.com
+2

Crew Cab 5.8 已补入 2016，2016 Edmunds 明确给出 Crew Cab short bed 69.3 in、230.0/80.0/74.2；但 2014/2017/2018 仍缺逐年参考，暂不入库。
Edmunds

Regular Cab 8.0 已补入 2014/2017，2014 Edmunds 可确认 Regular Cab long bed 97.8 in；2017 KBB 可确认 Regular Cab 规格页存在 8 ft 与 6.5 ft 配置；但 2016 仍缺明确逐年参考，暂不入库。
Edmunds
+1

Regular Cab 6.6 已补入 2014/2017，2014/2017 KBB 均可确认 Regular Cab 存在 6.5 ft 配置；但 2016 仍缺逐年参考，暂不入库。
Kbb.com
+1

当前批次进度
当前批次继续保持 11 行边界。gen4 Silverado 1500 已全部可入库；gen3 本轮新增 1 行可入库：Double Cab 6.6 2014-2018。gen3 仍剩 Regular Cab 6.6、Regular Cab 8.0、Crew Cab 5.8 未完成；gen2 Extended Cab 8.0 与 HD 行仍待逐年终核。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2014/2015/2017/2018 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2014/2017 Regular Cab 6.5 ft；2016 未逐年覆盖	待终核: 缺失 2016 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014/2015/2017/2018 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2014/2017 Regular Cab 8 ft；2016 未逐年覆盖	待终核: 缺失 2016 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2015/2016 Chevrolet Silverado 1500 Crew Cab short bed	本轮补入 2016 Crew Cab short bed；仍未覆盖全段	待终核: 缺失 2014/2017/2018 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2014-2018 Chevrolet Silverado 1500 Double Cab standard bed	本轮补入 2014/2016/2017；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2021-2026	Crew Cab	5.8	232.9	81.2	78.7	2021-2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2020 Trail Boss 5.8 未确认，且本轮查到的 2020 LT Trail Boss 样本为 79.4 in 标准床，不并入本行	可入库
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补 gen3 的 Regular Cab 6.6 与 Regular Cab 8.0 的 2016，使两行可入库；然后补 Crew Cab 5.8 的 2014/2017/2018。

下一步


--- Round 13 / 下一步 ---
更新点

本轮补强 gen3 Regular Cab 6.6 的 2016：GM 2016 Silverado 1500 规格 PDF 明确列出 Regular Cab with 6'6" box，整体长度 205.6、宽度 80；KBB 2016 Regular Cab 规格也列出 205.6 in 长度，因此该行 2014-2018 已逐年覆盖，状态改为 可入库。
通用汽车新闻
+1

本轮补强 gen3 Regular Cab 8.0 的 2016：Edmunds 2016 Regular Cab 页面明确给出 bed length 97.8 in、长度 224.4、宽度 80、高度 73.5，结合 2014/2015/2017/2018 已覆盖，状态改为 可入库。
Edmunds

本轮补强 gen3 Crew Cab 5.8 的 2014/2017/2018：2014 Edmunds LTZ Crew Cab short bed 为 230.0/80.0/74.2，2017/2018 Edmunds Crew Cab short bed 为 230.0/80.0/74.0，结合已有 2015/2016，该行 2014-2018 已逐年覆盖，状态改为 可入库。
Edmunds
+2
Edmunds
+2

当前批次进度
当前批次保持 11 行边界。gen3 与 gen4 Silverado 1500 目前均已可入库；剩余未完成集中在第 1 行 gen2 Extended Cab 8.0 2007-2013 和最后一行 Silverado 2500HD/3500HD gen1 HD pickup 2001-2007 Crew Cab 6.8 SRW。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007 Chevrolet Silverado 1500 Extended Cab long bed	原分类/驾驶室写法已规范；2007 已核，区间未逐年覆盖	待终核: 缺失 2008/2009/2010/2011/2012/2013 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2014-2018 Chevrolet Silverado 1500 Crew Cab short bed	本轮补入 2014/2017/2018；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2014-2018 Chevrolet Silverado 1500 Double Cab standard bed	2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2021-2026	Crew Cab	5.8	232.9	81.2	78.7	2021-2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2020 Trail Boss 5.8 未确认，且已查到的 2020 LT Trail Boss 样本为 79.4 in 标准床，不并入本行	可入库
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补第 1 行 2007-2013 Silverado 1500 Extended Cab 8.0 的 2008-2013；然后补最后一行 HD 的 2001-2007 Crew Cab 6.8 SRW。

下一步


--- Round 14 / 下一步 ---
更新点

本轮继续补强第 1 行 gen2 Extended Cab 8.0：已补入 2010/2011/2013 年份参考。2010 Edmunds 明确给出 Extended Cab LT long bed 的 bed length 为 97.8 in；2011 KBB 明确列出 Extended Cab LT Pickup 4D 8 ft；2013 KBB 明确 Silverado 1500 Extended Cab 覆盖到 LTZ Pickup 4D 8 ft。
Edmunds
+2
Kbb.com
+2

第 1 行参考车型从仅 2007 更新为 2007/2010/2011/2013，缺口从 2008-2013 缩小为 2008/2009/2012。

本轮未扩展当前 split 外车型、代际或年份；仍保持当前 11 行边界。

当前批次进度
当前批次 11 行中，Silverado 1500 gen3 与 gen4 已全部可入库；本轮推进 gen2 Extended Cab 8.0，但仍缺 2008/2009/2012 逐年参考。最后一行 Silverado 2500HD/3500HD HD 仍未完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007/2010/2011/2013 Chevrolet Silverado 1500 Extended Cab long bed	本轮补入 2010/2011/2013；均为 Extended Cab 8 ft/97.8 in long bed；区间仍未逐年覆盖	待终核: 缺失 2008/2009/2012 年份参考
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2014-2018 Chevrolet Silverado 1500 Crew Cab short bed	本轮补入 2014/2017/2018；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2014-2018 Chevrolet Silverado 1500 Double Cab standard bed	2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2021-2026	Crew Cab	5.8	232.9	81.2	78.7	2021-2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2020 Trail Boss 5.8 未确认，且已查到的 2020 LT Trail Boss 样本为 79.4 in 标准床，不并入本行	可入库
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补第 1 行 2008/2009/2012 Silverado 1500 Extended Cab 8.0，使 Silverado 1500 部分完全收尾；随后处理最后一行 HD 的 2001-2007 Crew Cab 6.8 SRW。

下一步


--- Round 15 / 下一步 ---
更新点

本轮补强第 1 行 gen2 Extended Cab 8.0 的剩余年份：

2008：KBB 2008 Extended Cab 规格页列出整体长度覆盖到 248.8 in，可对应 Extended Cab 8 ft long bed。
Kbb.com

2009：Fairfax County 的 2009 Silverado 1500 LongBed Extended Cab 示例规格显示 overall length 约 249.2 in，可确认 2009 Extended Cab LongBed 存在；与当前行 248.8 属同代同配置近似最大值口径，备注保留差异。
费尔法克斯县

2012：Edmunds 2012 Extended Cab 页面明确 bed length 97.8 in；KBB 2012 Extended Cab 规格页列出 8 ft 版本，整体长度覆盖到 249.2 in。
Edmunds
+1

第 1 行参考车型已由 2007/2010/2011/2013 更新为 2007-2013 Chevrolet Silverado 1500 Extended Cab long bed，状态改为 可入库。

本轮未新增当前范围外年份、车型或代际；仍保持 11 行边界。

当前批次进度
当前批次 11 行中，Silverado 1500 gen2/gen3/gen4 已全部可入库；剩余未完成仅最后一行 Silverado 2500HD/3500HD gen1 HD pickup 2001-2007 Crew Cab 6.8 SRW。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007-2013 Chevrolet Silverado 1500 Extended Cab long bed	本轮补入 2008/2009/2012；2009/2012 部分来源为 249.2 口径，当前行保留原最大 248.8，后续若统一 KBB 口径可上调至 249.2	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2014-2018 Chevrolet Silverado 1500 Crew Cab short bed	本轮补入 2014/2017/2018；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2014-2018 Chevrolet Silverado 1500 Double Cab standard bed	2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2021-2026	Crew Cab	5.8	232.9	81.2	78.7	2021-2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2020 Trail Boss 5.8 未确认，且已查到的 2020 LT Trail Boss 样本为 79.4 in 标准床，不并入本行	可入库
Chevrolet Silverado 2500HD/3500HD	皮卡	Chevrolet	Silverado 2500HD/3500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	Silverado HD Crew Cab standard bed SRW	HD SRW; 代际已修；尺寸待按本代/驾驶室/货斗终核	待终核: 缺失 2001/2002/2003/2004/2005/2006/2007 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先处理最后一行 Silverado 2500HD/3500HD 2001-2007 Crew Cab 6.8 SRW，需要确认是否应拆分 2500HD 与 3500HD、SRW/DRW 以及 6.8 ft 货斗对应的逐年三维。

下一步


--- Round 16 / 下一步 ---
更新点

本轮处理最后一行 HD 混合记录：原行写 Silverado 2500HD/3500HD + Crew Cab + 6.8，但核对后发现 3500/3500HD Crew Cab 在 2001 与 2007 资料中主要对应 8 ft long bed，且 2007 3500HD DRW 宽度可到 95.9，不应混入 6.8 ft SRW 行。
Kbb.com
+2
Kbb.com
+2

因此本轮把最后一行车型名从 Silverado 2500HD/3500HD 缩小为 Silverado 2500HD，版本仍为 Std.，货斗仍为 6.8，避免 3500HD/DRW 尺寸污染。

本轮补入 2001/2002/2007 的 2500HD Crew Cab short/standard bed 参考：2001/2002 Edmunds 可确认 Crew Cab 78.7 in bed；2007 Edmunds 可确认 2500HD Crew Cab 78.9 in bed，KBB 2007 也列出 Crew Cab 6.5 ft 与 8 ft 两类配置。
Kbb.com
+3
Edmunds
+3
Edmunds
+3

当前 HD 行仍未完成，因为 2003/2004/2005/2006 的 6.8 ft Crew Cab SRW 年份参考未全部锁定。

当前批次进度
当前批次 11 行中，Silverado 1500 的 gen2/gen3/gen4 已全部可入库；最后一行 HD 已完成“2500HD 与 3500HD 混合风险”修正，并开始补 2500HD Crew Cab 6.8 逐年参考，但仍缺 2003/2004/2005/2006。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007-2013 Chevrolet Silverado 1500 Extended Cab long bed	本轮补入 2008/2009/2012；2009/2012 部分来源为 249.2 口径，当前行保留原最大 248.8，后续若统一 KBB 口径可上调至 249.2	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2014-2018 Chevrolet Silverado 1500 Crew Cab short bed	本轮补入 2014/2017/2018；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2014-2018 Chevrolet Silverado 1500 Double Cab standard bed	2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2021-2026	Crew Cab	5.8	232.9	81.2	78.7	2021-2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2020 Trail Boss 5.8 未确认，且已查到的 2020 LT Trail Boss 样本为 79.4 in 标准床，不并入本行	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	250	81.9	80.9	2001/2002/2007 Chevrolet Silverado 2500HD Crew Cab standard bed SRW	本轮从 2500HD/3500HD 混合行缩小为 2500HD；3500/3500HD 主要为 8 ft/DRW 风险，不并入 6.8 ft SRW 行；尺寸待按 2003-2006 终核	待终核: 缺失 2003/2004/2005/2006 Crew Cab standard bed SRW 年份参考

下一步优先核对
优先补最后一行 Silverado 2500HD Crew Cab 6.8 SRW 的 2003/2004/2005/2006；若都能确认，再把 HD 行压缩为 2001-2007 并判定本批次完成。

下一步


--- Round 17 / 下一步 ---
更新点

本轮补强最后一行 Silverado 2500HD Crew Cab 6.8 SRW 的 2003/2004/2005/2006 缺口。

已确认 2003 Crew Cab 6 1/2 ft 存在，KBB 给出 overall length 237.2 in；2004 Crew Cab 6.5 ft 存在，KBB 给出 overall length 237.2 in；2005 Crew Cab 6.5 ft 可由 Edmunds Crew Cab 78.7 in bed、237.3/79.7/77.0 确认；2006 Crew Cab 6.5 ft 可由 Edmunds Crew Cab 78.7 in bed、237.3/79.7/77.0 及 KBB 6 1/2 ft trims 确认。
Edmunds
+3
Kbb.com
+3
Kbb.com
+3

最后一行尺寸从原 250 / 81.9 / 80.9 修正为 237.3 / 79.7 / 77.0，因为原尺寸更像后期/其他 HD 或 3500HD/DRW 风险口径，不适合当前 2001-2007 2500HD Crew Cab 6.8 SRW 行。

最后一行参考车型已压缩为 2001-2007 Chevrolet Silverado 2500HD Crew Cab standard bed SRW，状态改为 可入库。

当前批次进度
当前批次 11 行已全部完成：Silverado 1500 gen2/gen3/gen4 均可入库；Silverado 2500HD gen1 HD pickup 当前行也已缩小并终核为 2500HD Crew Cab 6.8 SRW，可入库。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen2	2007-2013	Extended Cab	8.0	248.8	79.9	73.6	2007-2013 Chevrolet Silverado 1500 Extended Cab long bed	本轮补入 2008/2009/2012；2009/2012 部分来源为 249.2 口径，当前行保留原最大 248.8，后续若统一 KBB 口径可上调至 249.2	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	6.6	205.6	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab standard bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Regular Cab	8.0	224.4	80	74	2014-2018 Chevrolet Silverado 1500 Regular Cab long bed	本轮补入 2016；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Crew Cab	5.8	230	80	74.2	2014-2018 Chevrolet Silverado 1500 Crew Cab short bed	本轮补入 2014/2017/2018；2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen3	2014-2018	Double Cab	6.6	230	80	73.9	2014-2018 Chevrolet Silverado 1500 Double Cab standard bed	2014-2018 已逐年覆盖，保留当前最大值	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2022-2026	Regular Cab	6.6	210.9	81.1	75.8	2022-2026 Chevrolet Silverado 1500 Regular Cab standard bed	2019-2021 Regular Cab 6.6 未确认/疑似不提供，不在本行入库；2022-2026 已覆盖，保留高度最大值 75.8	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Regular Cab	8.0	229.7	81.1	75.6	2019-2026 Chevrolet Silverado 1500 Regular Cab long bed	2019-2026 已逐年覆盖，2020/2021/2022 为 229.5 左右，保留本行最大 229.7	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Double Cab	6.6	231.9	81.2	75.6	2019-2026 Chevrolet Silverado 1500 Double Cab standard bed	2019-2026 已逐年覆盖，2019/2020/2021 为 231.7 左右，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Std.	gen4	2019-2026	Crew Cab	5.8	231.9	81.2	75.5	2019-2026 Chevrolet Silverado 1500 Crew Cab short bed	2019-2026 已逐年覆盖，2021 为 231.7/81.2/75.5，保留本行最大 231.9	可入库
Chevrolet Silverado 1500	皮卡	Chevrolet	Silverado 1500	Pickup	Trail Boss	gen4	2021-2026	Crew Cab	5.8	232.9	81.2	78.7	2021-2026 Chevrolet Silverado 1500 Crew Cab short bed Trail Boss	Trail Boss 高车身/离地间隙高；2020 Trail Boss 5.8 未确认，且已查到的 2020 LT Trail Boss 样本为 79.4 in 标准床，不并入本行	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup	Std.	gen1 HD pickup	2001-2007	Crew Cab	6.8	237.3	79.7	77.0	2001-2007 Chevrolet Silverado 2500HD Crew Cab standard bed SRW	已从 2500HD/3500HD 混合行缩小为 2500HD；3500/3500HD 及 DRW 不并入；尺寸按 2001-2007 Crew Cab 6.5/6.8 ft SRW 最大口径修正	可入库

下一步优先核对
本批次当前已完成，无需继续补强。

本批次完成

