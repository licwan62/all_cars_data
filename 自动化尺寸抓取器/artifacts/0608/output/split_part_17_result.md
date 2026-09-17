# 文件名：split_part_17.tsv


--- Round 1 / 首次发送 ---
更新点

已把分类修正为规则允许值：Panamera/Taycan Sedan/Liftback 归入“三厢车”，Wagon 归入“两厢车”。

补齐 Panamera Sport Turismo、Taycan Sedan、Taycan Cross Turismo、Taycan Sport Turismo 的尺寸。

修正 2024-2026 Panamera 标准款长度为 198.9；2024 高度保留 56.1 作为当前区间最大值。Edmunds 2024/2025/2026 Panamera 标准款尺寸分别支持 198.9 长、76.3 宽，2024 高 56.1、2025/2026 高 56.0。
Edmunds
+2
Edmunds
+2

Taycan 2025-2026 Cross Turismo 更新为区间最大 195.9 / 77.4 / 55.6，因 2025 Turbo Cross Turismo 高度/长度更大，2026 普通 Cross Turismo 为 195.8 / 77.4 / 55.5。
Edmunds
+1

仍保留 Panamera gen3 Executive LWB 为待终核，因为美国 2024-2026 Executive LWB 销售/尺寸未能闭环确认。

当前批次进度

10 条原始记录均已处理并输出。

本轮已补齐 8 条关键尺寸；1 条 gen3 Executive LWB 仍缺尺寸/美国销售确认；Taycan 2020-2024 Sedan、2021-2024 Cross Turismo 的 2021 年仍需单年补证，因此未全部完成。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Std.	gen2 full-size luxury	2017-2023			198.8	76.3	56.0	2017/2018/2019/2020/2021/2022/2023 Porsche Panamera, Edmunds	二代标准 Liftback；取整段普通款最大值	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Executive LWB	gen2 full-size luxury	2017-2023			204.7	76.3	56.2	2017/2018/2019/2020/2021/2022/2023 Porsche Panamera Executive, Edmunds	二代 Executive 长轴；长宽高独立于标准轴距	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Wagon	Sport Turismo	gen2 full-size luxury	2018-2023			198.8	76.3	56.2	2018/2019/2020/2021/2022/2023 Porsche Panamera Sport Turismo, Edmunds/Porsche spec	二代 Sport Turismo wagon；高于标准 Liftback，第三代不延展	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Std.	gen3 full-size luxury	2024-2026			198.9	76.3	56.1	2024/2025/2026 Porsche Panamera, Edmunds	三代标准 Liftback；2024 高 56.1 为区间最大，Sport Turismo 不延展	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Executive LWB	gen3 full-size luxury	2024-2026					2024/2025/2026 Porsche Panamera Executive	第三代美国 Executive LWB 销售/尺寸未闭环；不合并标准轴距	待终核: 缺失 2024/2025/2026 美国 Executive LWB 尺寸参考
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	EV	gen1 electric sport sedan	2020-2024			195.4	77.5	54.9	2020/2022/2023/2024 Porsche Taycan Sedan, Edmunds	前期 Taycan Sedan；2022-2024 基础款高度 54.9 为区间最大	待终核: 缺失 2021 年 Taycan Sedan 尺寸参考
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Cross Turismo	gen1 electric sport wagon	2021-2024			195.8	77.4	55.6	2022/2023/2024 Porsche Taycan Cross Turismo, Edmunds	Cross Turismo 加高；2024 Turbo Cross Turismo 高 55.6 为区间最大	待终核: 缺失 2021 年 Cross Turismo 尺寸参考
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo	gen1 electric sport wagon	2022-2024			195.4	77.5	55.5	2022/2023/2024 Porsche Taycan Sport Turismo, Edmunds	Sport Turismo 低于 Cross Turismo；2022 GTS 高 55.5 为区间最大	可入库
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	EV facelift	gen1 facelift electric sport sedan	2025-2026			195.4	77.4	54.3	2025/2026 Porsche Taycan Sedan, Edmunds	普通 Taycan facelift Sedan；Turbo GT 宽体不并入本行	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Cross Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.9	77.4	55.6	2025/2026 Porsche Taycan Cross Turismo, Edmunds	Cross Turismo facelift 加高；2025 Turbo Cross Turismo 长/高为区间最大	可入库

下一步优先核对
优先补齐 3 个缺口：2024-2026 Panamera gen3 Executive LWB 是否美国销售及尺寸；2021 Taycan Sedan；2021 Taycan Cross Turismo。

下一步


--- Round 2 / 下一步 ---
更新点

补齐 2021 Taycan Sedan 尺寸参考：2021 Edmunds Taycan Sedan 为 195.4 / 77.5 / 54.3，可覆盖 2020-2024 Sedan 区间缺口。
Edmunds

补齐 2021 Taycan Cross Turismo 尺寸参考：2021 Edmunds 4 Cross Turismo 为 195.8 / 77.4 / 55.5；2021 KBB 也给出 195.8 长、55.5 高，可覆盖 2021 缺口。
Edmunds
+1

将 Taycan 2020-2024 Sedan、2021-2024 Cross Turismo 两行从“待终核”推进为“可入库”。

Panamera gen3 Executive LWB 继续保留待终核：2024 Edmunds 美国 Panamera launch trims 只列 Panamera / Panamera 4 / Turbo E-Hybrid，未见 Executive；Porsche USA 当前 Panamera 页面也未显示 Executive LWB 作为美国在售车型。
Edmunds
+1

当前批次进度

当前批次 10 条记录中，9 条已可入库。

仅剩 1 条未完成：Porsche Panamera / gen3 / Executive LWB / 2024-2026，当前判断为美国市场疑似无对应 Executive LWB，需要最终确认是否删除或保留为非美国/当前 split 不入库。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Std.	gen2 full-size luxury	2017-2023			198.8	76.3	56.0	2017/2018/2019/2020/2021/2022/2023 Porsche Panamera, Edmunds	二代标准 Liftback；取整段普通款最大值	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Executive LWB	gen2 full-size luxury	2017-2023			204.7	76.3	56.2	2017/2018/2019/2020/2021/2022/2023 Porsche Panamera Executive, Edmunds	二代 Executive 长轴；长宽高独立于标准轴距	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Wagon	Sport Turismo	gen2 full-size luxury	2018-2023			198.8	76.3	56.2	2018/2019/2020/2021/2022/2023 Porsche Panamera Sport Turismo, Edmunds/Porsche spec	二代 Sport Turismo wagon；高于标准 Liftback，第三代不延展	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Std.	gen3 full-size luxury	2024-2026			198.9	76.3	56.1	2024/2025/2026 Porsche Panamera, Edmunds	三代标准 Liftback；2024 高 56.1 为区间最大，Sport Turismo 不延展	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Executive LWB	gen3 full-size luxury	2024-2026					2024 Edmunds Panamera trims / 2025-2026 Porsche USA Panamera lineup	第三代美国市场未见 Executive LWB 明确在售；疑似当前行应删除或标为非美国不入库	待终核: 2024/2025/2026 美国 Executive LWB 销售与尺寸未确认
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	EV	gen1 electric sport sedan	2020-2024			195.4	77.5	54.9	2020/2021/2022/2023/2024 Porsche Taycan Sedan, Edmunds	前期 Taycan Sedan；2022-2024 基础款高度 54.9 为区间最大	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Cross Turismo	gen1 electric sport wagon	2021-2024			195.8	77.4	55.6	2021/2022/2023/2024 Porsche Taycan Cross Turismo, Edmunds/KBB	前期 Cross Turismo 加高；2024 Turbo Cross Turismo 高 55.6 为区间最大	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo	gen1 electric sport wagon	2022-2024			195.4	77.5	55.5	2022/2023/2024 Porsche Taycan Sport Turismo, Edmunds	Sport Turismo 低于 Cross Turismo；2022 GTS 高 55.5 为区间最大	可入库
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	EV facelift	gen1 facelift electric sport sedan	2025-2026			195.4	77.4	54.3	2025/2026 Porsche Taycan Sedan, Edmunds	普通 Taycan facelift Sedan；Turbo GT 宽体不并入本行	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Cross Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.9	77.4	55.6	2025/2026 Porsche Taycan Cross Turismo, Edmunds	Cross Turismo facelift 加高；2025 Turbo Cross Turismo 长/高为区间最大	可入库

下一步优先核对
只剩 Panamera gen3 Executive LWB：继续核对 2024/2025/2026 美国官方配置器、Porsche USA order guide 或可靠经销商库存，确认这行是应删除，还是保留为非美国/特殊订购长轴版本。

下一步


--- Round 3 / 下一步 ---
更新点

对唯一剩余缺口 Porsche Panamera gen3 Executive LWB 2024-2026 做了收敛：Porsche 国际站存在第三代 Panamera Executive 长轴车型，并说明车身加长 150 mm；但 Porsche USA 当前 Panamera 全车型页未列 Executive 长轴版本，搜索到的美国在售/配置页面主要为标准轴距 Panamera / Panamera 4 E-Hybrid / 4S E-Hybrid / GTS / Turbo E-Hybrid 等。
保时捷
+1

因当前任务按美国市场入库逻辑推进，本轮不再把 gen3 Executive LWB 当作“缺尺寸待补普通行”，而是明确标为“非美国/美国未确认，建议删除不入库”。

其余 9 条保持可入库状态，本轮更新点集中在第 5 行的参考车型、备注、迭代状态。

当前批次进度

当前批次 10 条记录已全部遍历。

9 条可入库。

1 条为当前 split 内原始行，但美国市场未确认：2024-2026 Porsche Panamera Executive LWB，建议最终合并时删除或放入非美国排除清单；若你要求“只保留可入库行”，下一轮可直接输出删除该行后的 9 行完整 TSV。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Std.	gen2 full-size luxury	2017-2023			198.8	76.3	56.0	2017/2018/2019/2020/2021/2022/2023 Porsche Panamera, Edmunds	二代标准 Liftback；取整段普通款最大值	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Executive LWB	gen2 full-size luxury	2017-2023			204.7	76.3	56.2	2017/2018/2019/2020/2021/2022/2023 Porsche Panamera Executive, Edmunds	二代 Executive 长轴；长宽高独立于标准轴距	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Wagon	Sport Turismo	gen2 full-size luxury	2018-2023			198.8	76.3	56.2	2018/2019/2020/2021/2022/2023 Porsche Panamera Sport Turismo, Edmunds/Porsche spec	二代 Sport Turismo wagon；高于标准 Liftback，第三代不延展	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Std.	gen3 full-size luxury	2024-2026			198.9	76.3	56.1	2024/2025/2026 Porsche Panamera, Edmunds	三代标准 Liftback；2024 高 56.1 为区间最大，Sport Turismo 不延展	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Executive LWB	gen3 full-size luxury	2024-2026					2024-2026 Porsche Panamera Executive, Porsche International / Porsche USA lineup check	第三代 Executive 长轴见于国际市场；美国市场当前未确认在售，建议删除或标为非美国不入库	待终核: 2024/2025/2026 美国 Executive LWB 未确认，建议不入库
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	EV	gen1 electric sport sedan	2020-2024			195.4	77.5	54.9	2020/2021/2022/2023/2024 Porsche Taycan Sedan, Edmunds	前期 Taycan Sedan；2022-2024 基础款高度 54.9 为区间最大	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Cross Turismo	gen1 electric sport wagon	2021-2024			195.8	77.4	55.6	2021/2022/2023/2024 Porsche Taycan Cross Turismo, Edmunds/KBB	前期 Cross Turismo 加高；2024 Turbo Cross Turismo 高 55.6 为区间最大	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo	gen1 electric sport wagon	2022-2024			195.4	77.5	55.5	2022/2023/2024 Porsche Taycan Sport Turismo, Edmunds	Sport Turismo 低于 Cross Turismo；2022 GTS 高 55.5 为区间最大	可入库
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	EV facelift	gen1 facelift electric sport sedan	2025-2026			195.4	77.4	54.3	2025/2026 Porsche Taycan Sedan, Edmunds	普通 Taycan facelift Sedan；Turbo GT 宽体不并入本行	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Cross Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.9	77.4	55.6	2025/2026 Porsche Taycan Cross Turismo, Edmunds	Cross Turismo facelift 加高；2025 Turbo Cross Turismo 长/高为区间最大	可入库

下一步优先核对
下一步只需要决定第 5 行处理方式：保留为“待终核非美国”，还是从当前可入库 TSV 中删除。按美国市场入库逻辑，我建议删除该行，当前批次即可收敛为 9 条可入库。

下一步


--- Round 4 / 下一步 ---
更新点

本轮删除原第 5 行：Porsche Panamera / gen3 / Executive LWB / 2024-2026。

删除原因：第三代 Executive LWB 属于国际市场可见版本，但美国市场 2024-2026 未确认在售；按当前全量表美国市场入库逻辑，不作为可入库记录保留。

其余 9 行均已覆盖当前 split 内年份、结构、版本与尺寸，状态统一收敛为“可入库”。

当前批次进度

当前批次已完成。

原始 10 行中：9 行保留并可入库，1 行删除不入库。

当前可替换 TSV 为 9 行。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Std.	gen2 full-size luxury	2017-2023			198.8	76.3	56.0	2017/2018/2019/2020/2021/2022/2023 Porsche Panamera, Edmunds	二代标准 Liftback；取整段普通款最大值	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Executive LWB	gen2 full-size luxury	2017-2023			204.7	76.3	56.2	2017/2018/2019/2020/2021/2022/2023 Porsche Panamera Executive, Edmunds	二代 Executive 长轴；长宽高独立于标准轴距	可入库
Porsche Panamera	两厢车	Porsche	Panamera	Wagon	Sport Turismo	gen2 full-size luxury	2018-2023			198.8	76.3	56.2	2018/2019/2020/2021/2022/2023 Porsche Panamera Sport Turismo, Edmunds/Porsche spec	二代 Sport Turismo wagon；高于标准 Liftback，第三代不延展	可入库
Porsche Panamera	三厢车	Porsche	Panamera	Liftback	Std.	gen3 full-size luxury	2024-2026			198.9	76.3	56.1	2024/2025/2026 Porsche Panamera, Edmunds	三代标准 Liftback；2024 高 56.1 为区间最大，Sport Turismo 不延展	可入库
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	EV	gen1 electric sport sedan	2020-2024			195.4	77.5	54.9	2020/2021/2022/2023/2024 Porsche Taycan Sedan, Edmunds	前期 Taycan Sedan；2022-2024 基础款高度 54.9 为区间最大	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Cross Turismo	gen1 electric sport wagon	2021-2024			195.8	77.4	55.6	2021/2022/2023/2024 Porsche Taycan Cross Turismo, Edmunds/KBB	前期 Cross Turismo 加高；2024 Turbo Cross Turismo 高 55.6 为区间最大	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo	gen1 electric sport wagon	2022-2024			195.4	77.5	55.5	2022/2023/2024 Porsche Taycan Sport Turismo, Edmunds	Sport Turismo 低于 Cross Turismo；2022 GTS 高 55.5 为区间最大	可入库
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	EV facelift	gen1 facelift electric sport sedan	2025-2026			195.4	77.4	54.3	2025/2026 Porsche Taycan Sedan, Edmunds	普通 Taycan facelift Sedan；Turbo GT 宽体不并入本行	可入库
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Cross Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.9	77.4	55.6	2025/2026 Porsche Taycan Cross Turismo, Edmunds	Cross Turismo facelift 加高；2025 Turbo Cross Turismo 长/高为区间最大	可入库

下一步优先核对
无。当前 split_part_17 已完成，可直接入库。

本批次完成。

