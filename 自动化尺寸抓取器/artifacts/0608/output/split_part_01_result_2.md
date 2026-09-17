# 文件名：split_part_01.tsv


--- Round 1 / 首次发送 ---
更新点

已补入 9 行尺寸字段；Kia 官方资料显示 2014 Forte sedan 高度 56.5，2015-2018 sedan 为 56.3，所以该区间取最大高度 56.5。
Kia Media
+4
Kia Media
+4
Kia Media
+4

Forte5 已确认 2014-2017 为 171.3 / 70.1 / 57.1，但 2018 Forte5 本轮未找到逐年独立尺寸页，所以保留待终核。
Edmunds
+3
Kia Media
+3
Kia Media
+3

K5 2021-2026 官方规格均为 193.1 / 73.2 / 56.9，Std. 与 GT / GT-Line 主三维一致；2025-2026 改款行也已补齐。
Kia Media
+5
Kia Media
+5
Kia Media
+5

当前批次进度

已补尺寸：9/9

可入库：4/9

待终核：5/9，主要缺 Forte Koup 2015、Forte5 2018、Forte 2021、Forte GT/GT-Line 部分逐年独立参考。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Forte	三厢车	Kia	Forte	Sedan	Std.	gen2 compact	2014-2018			179.5	70.1	56.5	2014/2015/2016/2017/2018 Kia Forte Sedan	第二代 sedan；2014高度56.5，2015-2018高度56.3，取区间最大	可入库
Kia Forte	跑车	Kia	Forte	Coupe	Koup	gen2 compact	2014-2016			178.3	70.1	55.5	2014/2016 Kia Forte Koup	双门 Koup，结构独立；本轮已补尺寸但缺2015逐年参考	待终核: 缺失2015 Koup尺寸参考
Kia Forte	两厢车	Kia	Forte	Hatchback	Forte5	gen2 compact	2014-2018			171.3	70.1	57.1	2014/2015/2016/2017 Kia Forte5	五门 hatchback，后舱不同；本轮缺2018 Forte5逐年参考	待终核: 缺失2018 Forte5尺寸参考
Kia Forte	三厢车	Kia	Forte	Sedan	Std.	gen3 compact	2019-2024			182.7	70.9	56.5	2019/2020/2022/2023/2024 Kia Forte Sedan	第三代 sedan；2025 起由 K4 替代，本批不自动新增 K4；缺2021逐年参考	待终核: 缺失2021 Sedan尺寸参考
Kia Forte	三厢车	Kia	Forte	Sedan	GT / GT-Line	gen3 compact	2020-2024			182.7	70.9	56.5	2020/2022/2024 Kia Forte GT / GT-Line	运动包围本轮未发现主三维大于 Std.；仍缺部分逐年独立参考	待终核: 缺失2021/2023 GT或GT-Line逐年尺寸参考
Kia K5	三厢车	Kia	K5	Sedan	Std.	gen1 midsize	2021-2024			193.1	73.2	56.9	2021/2022/2023/2024 Kia K5	美国 2021 起替代 Optima；2021-2024主三维一致	可入库
Kia K5	三厢车	Kia	K5	Sedan	GT / GT-Line	gen1 midsize	2021-2024			193.1	73.2	56.9	2021/2022/2023/2024 Kia K5 GT / GT-Line	运动前后包围未导致主三维大于 Std.；2021-2024主三维一致	可入库
Kia K5	三厢车	Kia	K5	Sedan	Std.	gen1 facelift midsize	2025-2026			193.1	73.2	56.9	2025/2026 Kia K5	2025 改款；2025-2026主三维一致	可入库
Kia K5	三厢车	Kia	K5	Sedan	GT / GT-Line	gen1 facelift midsize	2025-2026			193.1	73.2	56.9	2025/2026 Kia K5 GT / GT-Line	改款运动版包围未导致主三维大于 Std.；2025-2026主三维一致	可入库

下一步优先核对

Kia Forte Koup：补 2015 Koup 独立尺寸页。

Kia Forte5：补 2018 Forte5 独立尺寸页。

Kia Forte gen3：补 2021 Sedan 与 2021/2023 GT 或 GT-Line 独立尺寸页。

下一步


--- Round 2 / 下一步 ---
更新点

补齐上一轮缺口：2015 Forte Koup、2018 Forte5、2021 Forte Sedan、2023 Forte GT-Line 均已补到逐年参考。2015 Forte Koup 尺寸为 178.3 / 70.1 / 55.5；2018 Forte5 尺寸为 171.3 / 70.1 / 57.1。
Edmunds
+1

Forte gen3 2020、2021、2023、2024 主三维均为 182.7 / 70.9 / 56.5；2020-2024 Std. 与 GT / GT-Line 主三维可并入同一尺寸值。
Edmunds
+3
Kia Media
+3
Kia Media
+3

本轮将 Forte Koup、Forte5、Forte gen3 Std.、Forte gen3 GT / GT-Line 的迭代状态由“待终核”推进为“可入库”。

当前批次进度

当前批次记录：9 行

已补尺寸：9/9

已逐年覆盖参考：9/9

可入库：9/9

待终核：0/9

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Kia Forte	三厢车	Kia	Forte	Sedan	Std.	gen2 compact	2014-2018			179.5	70.1	56.5	2014/2015/2016/2017/2018 Kia Forte Sedan	第二代 sedan；2014高度56.5，2015-2018高度56.3，取区间最大	可入库
Kia Forte	跑车	Kia	Forte	Coupe	Koup	gen2 compact	2014-2016			178.3	70.1	55.5	2014/2015/2016 Kia Forte Koup	双门 Koup，结构独立；2014-2016主三维一致	可入库
Kia Forte	两厢车	Kia	Forte	Hatchback	Forte5	gen2 compact	2014-2018			171.3	70.1	57.1	2014/2015/2016/2017/2018 Kia Forte5	五门 hatchback，后舱不同；2014-2018主三维一致	可入库
Kia Forte	三厢车	Kia	Forte	Sedan	Std.	gen3 compact	2019-2024			182.7	70.9	56.5	2019/2020/2021/2022/2023/2024 Kia Forte Sedan	第三代 sedan；2025 起由 K4 替代，本批不自动新增 K4；2019-2024主三维一致	可入库
Kia Forte	三厢车	Kia	Forte	Sedan	GT / GT-Line	gen3 compact	2020-2024			182.7	70.9	56.5	2020/2021/2022/2023/2024 Kia Forte GT / GT-Line	运动包围未导致主三维大于 Std.；2020-2024主三维一致	可入库
Kia K5	三厢车	Kia	K5	Sedan	Std.	gen1 midsize	2021-2024			193.1	73.2	56.9	2021/2022/2023/2024 Kia K5	美国 2021 起替代 Optima；2021-2024主三维一致	可入库
Kia K5	三厢车	Kia	K5	Sedan	GT / GT-Line	gen1 midsize	2021-2024			193.1	73.2	56.9	2021/2022/2023/2024 Kia K5 GT / GT-Line	运动前后包围未导致主三维大于 Std.；2021-2024主三维一致	可入库
Kia K5	三厢车	Kia	K5	Sedan	Std.	gen1 facelift midsize	2025-2026			193.1	73.2	56.9	2025/2026 Kia K5	2025 改款；2025-2026主三维一致	可入库
Kia K5	三厢车	Kia	K5	Sedan	GT / GT-Line	gen1 facelift midsize	2025-2026			193.1	73.2	56.9	2025/2026 Kia K5 GT / GT-Line	改款运动版包围未导致主三维大于 Std.；2025-2026主三维一致	可入库

下一步优先核对
无；当前 split_part_01 已全部可入库。

本批次完成。

