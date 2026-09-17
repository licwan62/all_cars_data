# 文件名：split_part_03.tsv


--- Round 1 / 首次发送 ---
更新点

已补齐当前 10 条记录的三维尺寸；Rio、Stinger、A-Class/A35 的核心尺寸来自 Edmunds / Kia Media / Mercedes-Benz USA / Car and Driver 等规格页。Rio 2018/2023 sedan 与 hatchback尺寸分别确认，Stinger 2022/2023 各 trim 规格一致，A-Class Std. 2019/2020/2022 尺寸一致；A35 存在 2020/2021 高度来源差异，需要保守待终核。
梅赛德斯-奔驰媒体
+10
Edmunds
+10
Edmunds
+10

修正 Kia Stinger 的 分类：原表写“掀背车”不符合本任务允许值，已改为“跑车”；结构仍保留 Liftback，避免把 5-door fastback 简化为 Sedan。

对未逐年覆盖的区间，未强行判“可入库”，统一写明缺失年份。

当前批次进度

已补尺寸：10/10

可入库：2/10

待终核：8/10

本批次尚未完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen3 subcompact	2012-2017			171.9	67.7	57.3	2012 Kia Rio Sedan, Edmunds	第三代 sedan；已先按已核样本补尺寸	待终核: 缺失 2013/2014/2015/2016/2017 年份参考逐年覆盖
Kia Rio	两厢车	Kia	Rio	Hatchback	5-door	gen3 subcompact	2012-2017			159.4	67.7	57.3	2017 Kia Rio Hatchback, Edmunds	五门 hatchback，需独立；已先按已核样本补尺寸	待终核: 缺失 2012/2013/2014/2015/2016 年份参考逐年覆盖
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen4 subcompact	2018-2023			172.6	67.9	57.1	2018/2022/2023 Kia Rio Sedan, Edmunds	第四代 sedan；美国 2023 后停用	待终核: 缺失 2019/2020/2021 年份参考逐年覆盖
Kia Rio	两厢车	Kia	Rio	Hatchback	5-door	gen4 subcompact	2018-2023			160.0	67.9	57.1	2018/2022/2023 Kia Rio Hatchback, Edmunds	五门 hatchback，需独立	待终核: 缺失 2019/2020/2021 年份参考逐年覆盖
Kia Stinger	跑车	Kia	Stinger	Liftback	Std.	gen1 midsize fastback	2018-2021			190.2	73.6	55.1	2018/2021 Kia Stinger, Edmunds	5-door liftback/fastback，不能按 sedan 简化；分类由掀背车修正为跑车	待终核: 缺失 2019/2020 年份参考逐年覆盖
Kia Stinger	跑车	Kia	Stinger	Liftback	GT / GT1 / GT2	gen1 midsize fastback	2018-2021			190.2	73.6	55.1	2018/2021 Kia Stinger GT/GT2, Edmunds/Kia Media	性能版外观/轮胎/高度已按已核样本未见三维增量；分类由掀背车修正为跑车	待终核: 缺失 2019/2020 年份参考逐年覆盖
Kia Stinger	跑车	Kia	Stinger	Liftback	Std. facelift	gen1 facelift midsize fastback	2022-2023			190.2	73.6	55.1	2022/2023 Kia Stinger GT-Line, Edmunds/Kia Media	2022 改款；外观与动力更新；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Scorpion / GT facelift	gen1 facelift midsize fastback	2022-2023			190.2	73.6	55.1	2022/2023 Kia Stinger GT/GT2, Edmunds/Kia Media	特殊外观套件未见三维增量；分类由掀背车修正为跑车	可入库
Mercedes-Benz A-Class	三厢车	Mercedes-Benz	A-Class	Sedan	Std.	gen4 compact luxury	2019-2022			179.1	70.7	56.9	2019/2020/2022 Mercedes-Benz A 220 Sedan, Edmunds/MBUSA	美国只保留 A-Class Sedan；欧洲 hatchback 不入库	待终核: 缺失 2021 年份参考逐年覆盖
Mercedes-Benz A-Class	三厢车	Mercedes-Benz	A-Class	Sedan	AMG A35	gen4 compact luxury	2020-2022			179.5	70.7	56.9	2020/2021 Mercedes-AMG A35 Sedan, Edmunds/MBUSA/Car and Driver	AMG 前后包围长度略增；高度来源存在 55.6/56.9 差异，车罩取保守最大值 56.9	待终核: 缺失 2022 美国年份参考；2020/2021 高度来源差异需终核

下一步优先核对
优先补 Rio 2012-2017 / 2018-2023 的中间年份，再补 Stinger 2019/2020，最后核 Mercedes-Benz A-Class 2021 与 AMG A35 2022 美国规格及高度冲突。

下一步


--- Round 2 / 下一步 ---
更新点

本轮继续补强中间年份覆盖：Kia Stinger 2018/2019/2020/2021 已补齐逐年参考，Std. 与 GT/GT1/GT2 均可入库；Edmunds 对 2018、2019、2020、2021 Stinger 均给出 190.2 / 73.6 / 55.1 in。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Mercedes-Benz A-Class Std. 2021 已补齐，2019-2022 可完整覆盖；2021/2022 A 220 均为 179.1 / 70.7 / 56.9 in。
Edmunds
+1

Kia Rio gen3 sedan 已补强 2012/2013/2014/2015/2017，发现 2017 长度为 172.0，比 2012-2015 的 171.9 略大，取最大值 172.0；但 2016 sedan 仍缺，因此不能判可入库。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Kia Rio gen3 hatchback 本轮确认到 2016 hatchback 为 159.4 / 67.7 / 57.3；仍缺多个年份。
Edmunds

当前批次进度

总记录：10 条

已补尺寸：10/10

可入库：5/10

待终核：5/10

本轮实际推进：Stinger 2018-2021 两条由“待终核”推进为“可入库”；A-Class Std. 由“待终核”推进为“可入库”；Rio gen3 sedan 尺寸由 171.9 修正为 172.0。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen3 subcompact	2012-2017			172.0	67.7	57.3	2012/2013/2014/2015/2017 Kia Rio Sedan, Edmunds	第三代 sedan；2017 长度 172.0，车罩取本区间最大值	待终核: 缺失 2016 年份参考逐年覆盖
Kia Rio	两厢车	Kia	Rio	Hatchback	5-door	gen3 subcompact	2012-2017			159.4	67.7	57.3	2016/2017 Kia Rio Hatchback, Edmunds	五门 hatchback，需独立；已先按已核样本补尺寸	待终核: 缺失 2012/2013/2014/2015 年份参考逐年覆盖
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen4 subcompact	2018-2023			172.6	67.9	57.1	2018/2022/2023 Kia Rio Sedan, Edmunds	第四代 sedan；美国 2023 后停用	待终核: 缺失 2019/2020/2021 年份参考逐年覆盖
Kia Rio	两厢车	Kia	Rio	Hatchback	5-door	gen4 subcompact	2018-2023			160.0	67.9	57.1	2018/2022/2023 Kia Rio Hatchback, Edmunds	五门 hatchback，需独立	待终核: 缺失 2019/2020/2021 年份参考逐年覆盖
Kia Stinger	跑车	Kia	Stinger	Liftback	Std.	gen1 midsize fastback	2018-2021			190.2	73.6	55.1	2018/2019/2020/2021 Kia Stinger GT-Line/Base, Edmunds	5-door liftback/fastback，不能按 sedan 简化；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	GT / GT1 / GT2	gen1 midsize fastback	2018-2021			190.2	73.6	55.1	2018/2019/2020/2021 Kia Stinger GT/GT1/GT2, Edmunds	性能版外观/轮胎/高度已按逐年样本确认未见三维增量；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Std. facelift	gen1 facelift midsize fastback	2022-2023			190.2	73.6	55.1	2022/2023 Kia Stinger GT-Line, Edmunds/Kia Media	2022 改款；外观与动力更新；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Scorpion / GT facelift	gen1 facelift midsize fastback	2022-2023			190.2	73.6	55.1	2022/2023 Kia Stinger GT/GT2, Edmunds/Kia Media	特殊外观套件未见三维增量；分类由掀背车修正为跑车	可入库
Mercedes-Benz A-Class	三厢车	Mercedes-Benz	A-Class	Sedan	Std.	gen4 compact luxury	2019-2022			179.1	70.7	56.9	2019/2020/2021/2022 Mercedes-Benz A 220 Sedan, Edmunds/MBUSA	美国只保留 A-Class Sedan；欧洲 hatchback 不入库	可入库
Mercedes-Benz A-Class	三厢车	Mercedes-Benz	A-Class	Sedan	AMG A35	gen4 compact luxury	2020-2022			179.5	70.7	56.9	2020/2021 Mercedes-AMG A35 Sedan, Edmunds/MBUSA/Car and Driver	AMG 前后包围长度略增；高度来源存在 55.6/56.9 差异，车罩取保守最大值 56.9	待终核: 缺失 2022 美国年份参考；2020/2021 高度来源差异需终核

下一步优先核对

Kia Rio gen3：补 2016 Sedan，以及 2012/2013/2014/2015 Hatchback。

Kia Rio gen4：补 2019/2020/2021 Sedan 与 Hatchback。

Mercedes-AMG A35：确认 2022 美国是否仍销售 AMG A35 Sedan；若 2022 无美国 A35，应把年份区间缩小为 2020-2021 或在状态中明确当前原范围含无售年。

下一步


--- Round 3 / 下一步 ---
更新点

Kia Rio gen3 Sedan 已补齐 2016 年份，2012-2017 可完整覆盖；2016 Rio Sedan 为 172.0 / 67.7 / 57.3 in，因此该行从“待终核”推进为“可入库”。
Edmunds

Kia Rio gen3 Hatchback 本轮新增 2015 年份参考，2015 Hatchback 为 159.3 / 67.7 / 57.3 in；该行仍缺 2012/2013/2014，不判可入库。
Edmunds

Kia Rio gen4 Sedan / Hatchback 已补齐 2019/2020/2021 中间年份；Kia Media 与 Edmunds 均显示 gen4 Sedan 为 172.6 / 67.9 / 57.1 in，5-Door 为 160.0 / 67.9 / 57.1 in，因此两条从“待终核”推进为“可入库”。
Kia Media
+6
Edmunds
+6
Edmunds
+6

Mercedes-AMG A35 仍未补到 2022 美国 A35 Sedan 明确规格；当前保持待终核，不强行判可入库。

当前批次进度

总记录：10 条

已补尺寸：10/10

可入库：8/10

待终核：2/10

本轮实际推进：Rio gen3 Sedan、Rio gen4 Sedan、Rio gen4 Hatchback 共 3 条推进为可入库；Rio gen3 Hatchback 参考年份从 2016/2017 扩展为 2015/2016/2017。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen3 subcompact	2012-2017			172.0	67.7	57.3	2012/2013/2014/2015/2016/2017 Kia Rio Sedan, Edmunds	第三代 sedan；2016/2017 长度 172.0，车罩取本区间最大值	可入库
Kia Rio	两厢车	Kia	Rio	Hatchback	5-door	gen3 subcompact	2012-2017			159.4	67.7	57.3	2015/2016/2017 Kia Rio Hatchback, Edmunds	五门 hatchback，需独立；2016/2017 长度 159.4，车罩取本区间最大值	待终核: 缺失 2012/2013/2014 年份参考逐年覆盖
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen4 subcompact	2018-2023			172.6	67.9	57.1	2018/2019/2020/2021/2022/2023 Kia Rio Sedan, Edmunds/Kia Media	第四代 sedan；美国 2023 后停用	可入库
Kia Rio	两厢车	Kia	Rio	Hatchback	5-door	gen4 subcompact	2018-2023			160.0	67.9	57.1	2018/2019/2020/2021/2022/2023 Kia Rio Hatchback/5-Door, Edmunds/Kia Media	五门 hatchback，需独立	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Std.	gen1 midsize fastback	2018-2021			190.2	73.6	55.1	2018/2019/2020/2021 Kia Stinger GT-Line/Base, Edmunds	5-door liftback/fastback，不能按 sedan 简化；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	GT / GT1 / GT2	gen1 midsize fastback	2018-2021			190.2	73.6	55.1	2018/2019/2020/2021 Kia Stinger GT/GT1/GT2, Edmunds	性能版外观/轮胎/高度已按逐年样本确认未见三维增量；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Std. facelift	gen1 facelift midsize fastback	2022-2023			190.2	73.6	55.1	2022/2023 Kia Stinger GT-Line, Edmunds/Kia Media	2022 改款；外观与动力更新；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Scorpion / GT facelift	gen1 facelift midsize fastback	2022-2023			190.2	73.6	55.1	2022/2023 Kia Stinger GT/GT2, Edmunds/Kia Media	特殊外观套件未见三维增量；分类由掀背车修正为跑车	可入库
Mercedes-Benz A-Class	三厢车	Mercedes-Benz	A-Class	Sedan	Std.	gen4 compact luxury	2019-2022			179.1	70.7	56.9	2019/2020/2021/2022 Mercedes-Benz A 220 Sedan, Edmunds/MBUSA	美国只保留 A-Class Sedan；欧洲 hatchback 不入库	可入库
Mercedes-Benz A-Class	三厢车	Mercedes-Benz	A-Class	Sedan	AMG A35	gen4 compact luxury	2020-2022			179.5	70.7	56.9	2020/2021 Mercedes-AMG A35 Sedan, Edmunds/MBUSA/Car and Driver	AMG 前后包围长度略增；高度来源存在 55.6/56.9 差异，车罩取保守最大值 56.9	待终核: 缺失 2022 美国年份参考；2020/2021 高度来源差异需终核

下一步优先核对

Kia Rio gen3 Hatchback：补 2012/2013/2014 三个年份；若均为 159.3 或 159.4 / 67.7 / 57.3，可推进为可入库。

Mercedes-AMG A35：确认 2022 美国市场是否仍有 AMG A35 Sedan；若无美国 2022 A35，应把当前行缩小为 2020-2021，并在备注写“2022 原范围无美国销售/未处理”。

下一步


--- Round 4 / 下一步 ---
更新点

Kia Rio gen3 Hatchback 已补齐 2012/2013/2014 年份参考；2012/2013/2014/2015 均为 159.3 / 67.7 / 57.3 in，2016/2017 最大长度取 159.4，因此该行推进为“可入库”。
Car and Driver
+3
Edmunds
+3
Edmunds
+3

Mercedes-AMG A35：确认美国市场 AMG A35 在 2022 model year 已退出，当前原行 2020-2022 明显含无美国销售年；按当前行原范围内缩小为 2020-2021，不扩展年份。
Car and Driver
+1

A35 尺寸终核：Edmunds / Car and Driver / JD Power 给 2020 A35 为 179.4 / 70.7 / 55.6 in，MBUSA 官方规格给高度 56.9 in；车罩表按保守最大高度 56.9，长度保留 179.4，不再用上一轮 179.5。
梅赛德斯-奔驰媒体
+3
Edmunds
+3
Car and Driver
+3

当前批次进度

总记录：10 条

已补尺寸：10/10

可入库：10/10

待终核：0/10

本轮实际推进：Rio gen3 Hatchback、Mercedes-AMG A35 两条完成终核；A35 年份区间由 2020-2022 缩小为 2020-2021。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen3 subcompact	2012-2017			172.0	67.7	57.3	2012/2013/2014/2015/2016/2017 Kia Rio Sedan, Edmunds	第三代 sedan；2016/2017 长度 172.0，车罩取本区间最大值	可入库
Kia Rio	两厢车	Kia	Rio	Hatchback	5-door	gen3 subcompact	2012-2017			159.4	67.7	57.3	2012/2013/2014/2015/2016/2017 Kia Rio Hatchback, Edmunds/Car and Driver	五门 hatchback，需独立；2016/2017 长度 159.4，车罩取本区间最大值	可入库
Kia Rio	三厢车	Kia	Rio	Sedan	Std.	gen4 subcompact	2018-2023			172.6	67.9	57.1	2018/2019/2020/2021/2022/2023 Kia Rio Sedan, Edmunds/Kia Media	第四代 sedan；美国 2023 后停用	可入库
Kia Rio	两厢车	Kia	Rio	Hatchback	5-door	gen4 subcompact	2018-2023			160.0	67.9	57.1	2018/2019/2020/2021/2022/2023 Kia Rio Hatchback/5-Door, Edmunds/Kia Media	五门 hatchback，需独立	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Std.	gen1 midsize fastback	2018-2021			190.2	73.6	55.1	2018/2019/2020/2021 Kia Stinger GT-Line/Base, Edmunds	5-door liftback/fastback，不能按 sedan 简化；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	GT / GT1 / GT2	gen1 midsize fastback	2018-2021			190.2	73.6	55.1	2018/2019/2020/2021 Kia Stinger GT/GT1/GT2, Edmunds	性能版外观/轮胎/高度已按逐年样本确认未见三维增量；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Std. facelift	gen1 facelift midsize fastback	2022-2023			190.2	73.6	55.1	2022/2023 Kia Stinger GT-Line, Edmunds/Kia Media	2022 改款；外观与动力更新；分类由掀背车修正为跑车	可入库
Kia Stinger	跑车	Kia	Stinger	Liftback	Scorpion / GT facelift	gen1 facelift midsize fastback	2022-2023			190.2	73.6	55.1	2022/2023 Kia Stinger GT/GT2, Edmunds/Kia Media	特殊外观套件未见三维增量；分类由掀背车修正为跑车	可入库
Mercedes-Benz A-Class	三厢车	Mercedes-Benz	A-Class	Sedan	Std.	gen4 compact luxury	2019-2022			179.1	70.7	56.9	2019/2020/2021/2022 Mercedes-Benz A 220 Sedan, Edmunds/MBUSA	美国只保留 A-Class Sedan；欧洲 hatchback 不入库	可入库
Mercedes-Benz A-Class	三厢车	Mercedes-Benz	A-Class	Sedan	AMG A35	gen4 compact luxury	2020-2021			179.4	70.7	56.9	2020/2021 Mercedes-AMG A35 Sedan, Edmunds/MBUSA/Car and Driver/JD Power	AMG 前后包围长度略增；2022 美国市场 AMG A35 已退出，原 2020-2022 范围缩小为 2020-2021；高度按 MBUSA 官方 56.9 保守取最大	可入库

下一步优先核对
无。当前批次 10 条均已达到可入库。

本批次完成。

