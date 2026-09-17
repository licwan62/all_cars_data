# 文件名：split_part_03.tsv


--- Round 1 / 首次发送 ---
更新点
车型	操作	描述
Chevrolet Camaro	值修改	ZL1 高度由 52.6 修正为 52.9；Edmunds ZL1 规格显示 Length 190.2 / Width 75.0 / Height 52.9。
Edmunds
+1

Chevrolet Caprice	拆出	Coupe/Convertible 拆成 Coupe 与 Convertible 两条，结构字段保持单一结构。
全表	格式修复	补齐统一 16 字段；普通车驾驶室类型、货斗长度_ft 留空；版本空缺风险统一检查。
当前批次进度
状态	说明
🟡 待补强	Camaro 已推进；Caprice 仍有 1971-1973 Coupe/Convertible height、1967 Wagon 待终核。
本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.9	2017 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds / 2019 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1 exact trim
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966-1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive / 1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	可入库; 待终核: 1967 Wagon
下一步优先核对

优先补 Caprice：1971 Convertible / Coupe 高度、1972 Coupe 高度、1973 Coupe 高度、1967 Wagon 是否与 1966 同尺寸；然后再把 Camaro 2019 ZL1 Convertible exact trim 终核。

下一步


--- Round 2 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Camaro	值修改	2017 与 2019 ZL1 Convertible 均核到 Edmunds：190.2 / 75.0 / 52.6，因此恢复高度 52.6，并把 2019 exact trim 补入参考。
Edmunds
+1

Chevrolet Caprice	值修改	1971 Coupe 高度由 proxy 56.7 修正为 53.5；1972 Coupe 高度修正为 53.5。
汽车目录
+1

Chevrolet Caprice	值修改	1973 Coupe 长度由 222.9 修正为 221.9；宽度 79.5 保持；高度按 1973 Chevrolet full-size brochure 的 coupe/sedan loaded height 口径暂取 54.5。
Dezo's Garage

Chevrolet Caprice	值修改	1966 Wagon 已核到 full-size wagon 口径：212.4 / 79.6 / 56.7；1967 仍缺独立年份终核。
Over-Drive Magazine
2) 当前批次进度
状态	说明
🟡 待补强	Camaro 已可入库；Caprice Coupe 1971/1972 已推进；1971 Convertible、1973 Coupe height 口径、1967 Wagon 仍建议继续终核。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.6	2017/2019 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds proxy	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	53.5	1971 Chevrolet Caprice Custom Coupe 400 V-8, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	53.5	1972 Chevrolet Caprice Custom Coupe 454-4 V-8, Automobile-Catalog / 1972 Chevrolet Caprice brochure coupe dimensions	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			221.9	79.5	54.5	1973 Chevrolet Caprice/Impala/Bel Air brochure coupe dimensions	非wagon全尺寸	待终核: 1973 Coupe exact trim height
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966-1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / 1966 Chevrolet full-size fact sheet, Over-Drive	wagon高车身	可入库; 待终核: 1967 Wagon
4) 下一步优先核对

优先补 3 个缺口：1971 Caprice Convertible height、1973 Caprice Coupe exact trim height、1967 Caprice/Kingswood Estate Wagon 是否沿用 1966 wagon 三维。

下一步


--- Round 3 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Caprice	值修改	1973 Coupe 已核到 Automobile-Catalog：221.9 / 79.5 / 53.7，上一轮暂用 54.5 属于 sedan loaded height 口径，本轮改回 Coupe 精确高度 53.7。
汽车目录

Chevrolet Caprice	值修改	1973 Convertible 同源可参考为 221.9 / 79.5 / 53.7，但当前 TSV 没有 1973 Convertible 行，不新增 split 外结构行，只用于确认 1973 Coupe 不应沿用 sedan 高度。
汽车目录

Chevrolet Caprice	稳定	1971 Coupe 保持 216.8 / 79.5 / 53.5，Automobile-Catalog 可核到该 Coupe 三维。
汽车目录

Chevrolet Caprice	稳定	1971 Convertible 仍未核到当前行对应的独立 convertible 三维页面，继续保留待终核，不强行改为 Coupe 数据。
Chevrolet Caprice	稳定	1966-1967 Wagon 仍只确认 1966 来源覆盖，1967 未完成整段参考覆盖，继续保留待终核。
2) 当前批次进度
状态	说明
🟡 待补强	Camaro、1971 Coupe、1972 Coupe、1973 Coupe 已推进为可入库；剩余 1971 Convertible height、1967 Wagon 两个缺口。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.6	2017/2019 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds proxy	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	53.5	1971 Chevrolet Caprice Custom Coupe 400 V-8 Turbo-Jet, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	53.5	1972 Chevrolet Caprice Custom Coupe 454-4 V-8, Automobile-Catalog / 1972 Chevrolet Caprice brochure coupe dimensions	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			221.9	79.5	53.7	1973 Chevrolet Caprice Classic Coupe 454-4 V-8, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966-1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / 1966 Chevrolet full-size fact sheet, Over-Drive	wagon高车身	可入库; 待终核: 1967 Wagon
4) 下一步优先核对

优先只剩两项：1971 Chevrolet Caprice Convertible height；1967 Chevrolet Caprice/Kingswood Estate Wagon 是否与 1966 wagon 三维一致并能覆盖整段参考。

下一步


--- Round 4 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Caprice Wagon	拆出	1966-1967 拆为 1966 与 1967，因为当前只核到 1966 wagon 数据，1967 不能跟随整段标可入库。1966 full-size wagon 来源可支撑 212.4 / 79.6 / 56.7。
维基百科

Chevrolet Caprice Convertible	稳定	1971 Convertible 仍未找到独立 convertible 高度来源；不强行沿用 Coupe 高度，继续保留待终核。
Chevrolet Caprice Coupe	稳定	1971 Coupe 仍按 Automobile-Catalog 的 216.8 / 79.5 / 53.5 保持可入库。
汽车目录

Chevrolet Caprice Coupe	稳定	1973 Coupe 继续保持 221.9 / 79.5 / 53.7；同年 convertible 搜索结果也显示 221.9 / 79.5 / 53.7，但当前 split 不新增 1973 Convertible 行。
汽车目录
2) 当前批次进度
状态	说明
🟡 待补强	已把 1966 Wagon 单独推进为可入库；剩余 1971 Convertible height、1967 Wagon 两个待终核点。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.6	2017/2019 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds proxy	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	53.5	1971 Chevrolet Caprice Custom Coupe 400 V-8 Turbo-Jet, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	53.5	1972 Chevrolet Caprice Custom Coupe 454-4 V-8, Automobile-Catalog / 1972 Chevrolet Caprice brochure coupe dimensions	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			221.9	79.5	53.7	1973 Chevrolet Caprice Classic Coupe 454-4 V-8, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / 1966 Chevrolet full-size fact sheet, Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1967 Chevrolet Caprice/Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
4) 下一步优先核对

继续只补两个点：1971 Chevrolet Caprice Convertible height 和 1967 Chevrolet Caprice/Kingswood Estate Wagon 独立尺寸来源。若 1967 wagon 找不到独立来源，下一轮建议保持单年待终核，不再把 1966-1967 合并成可入库区间。

下一步


--- Round 5 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Caprice Wagon	值修改	1967 Wagon 找到独立 Automobile-Catalog 数据，宽度由 79.6 修正为 79.9；尺寸为 212.4 / 79.9 / 56.7，状态改为可入库。
汽车目录
+1

Chevrolet Caprice Wagon	稳定	1966 Wagon 保持 212.4 / 79.6 / 56.7，1966 与 1967 宽度不同，不重新合并。
汽车目录

Chevrolet Caprice Convertible	稳定	1971 Convertible 仍未核到独立 convertible 高度；继续保留待终核，不用 Coupe 高度替代。
2) 当前批次进度
状态	说明
🟡 待补强	1967 Wagon 已推进为可入库；当前仅剩 1971 Caprice Convertible height 一个待终核点。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.6	2017/2019 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds proxy	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	53.5	1971 Chevrolet Caprice Custom Coupe 400 V-8 Turbo-Jet, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	53.5	1972 Chevrolet Caprice Custom Coupe 454-4 V-8, Automobile-Catalog / 1972 Chevrolet Caprice brochure coupe dimensions	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			221.9	79.5	53.7	1973 Chevrolet Caprice Classic Coupe 454-4 V-8, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice Custom Station Wagon 396 V-8 Turbo-Jet, Automobile-Catalog	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1967			212.4	79.9	56.7	1967 Chevrolet Caprice Custom Station Wagon 283/327 V-8, Automobile-Catalog	wagon高车身	可入库
4) 下一步优先核对

只剩 1971 Chevrolet Caprice Convertible height。建议下一轮继续找 1971 convertible 独立规格；若找不到，可保持该单行待终核，不影响本 split 其余记录出库。

下一步


--- Round 6 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Caprice Convertible	值修改	1971 Caprice Convertible 这一行不再保留 proxy 三维；资料显示 Caprice Convertible 是 1973 年才从 Impala 转入 Caprice lineup，因此 1971 Caprice Convertible 在当前口径下应标为“未确认独立车型/疑似无此结构”，尺寸清空，避免误入库。
维基百科
+1

Chevrolet Caprice Coupe	稳定	1971/1972/1973 Coupe 保持上一轮已核尺寸与可入库状态。
Chevrolet Caprice Wagon	稳定	1966、1967 Wagon 已拆成年份单行，且 1967 宽度已修正，不再合并。
2) 当前批次进度
状态	说明
🟡 待补强	当前只剩 1971 Caprice Convertible 这一条属于结构/年份存疑；其余记录均可入库。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.6	2017/2019 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds proxy	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971						1971 Caprice Convertible not confirmed; Caprice convertible moved from Impala to Caprice lineup in 1973	1971 Caprice敞篷结构存疑	待终核: 1971 Caprice Convertible是否存在/是否应删除
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	53.5	1971 Chevrolet Caprice Custom Coupe 400 V-8 Turbo-Jet, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	53.5	1972 Chevrolet Caprice Custom Coupe 454-4 V-8, Automobile-Catalog / 1972 Chevrolet Caprice brochure coupe dimensions	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			221.9	79.5	53.7	1973 Chevrolet Caprice Classic Coupe 454-4 V-8, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice Custom Station Wagon 396 V-8 Turbo-Jet, Automobile-Catalog	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1967			212.4	79.9	56.7	1967 Chevrolet Caprice Custom Station Wagon 283/327 V-8, Automobile-Catalog	wagon高车身	可入库
4) 下一步优先核对

只剩一项：确认 1971 Chevrolet Caprice Convertible 是否应删除，或是否其实应该改为 1971 Chevrolet Impala Convertible。在当前 split 不新增 Impala 行，因此先保留为待终核存疑行。

下一步


--- Round 7 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Caprice Convertible	值修改	1971 行继续保留在当前 split 边界内，但状态从“是否存在/是否应删除”收敛为“疑似应删除”。1971 Chevrolet full-size 资料能找到 Caprice hardtop sedan / hardtop coupe / wagon 等车身，但未确认 Caprice Convertible；1971 brochure 也只显示 convertible 相关配置口径，并不能证明 Caprice Convertible 可入库。
汽车目录
+2
汽车目录
+2

Chevrolet Caprice Convertible	稳定	不新增 Impala Convertible，也不把当前行改名为 Impala；只在备注里标记“疑似 Impala convertible 混入”。
Chevrolet Caprice 其余行	稳定	Camaro、Caprice Coupe 1971-1973、Caprice Wagon 1966/1967 继续保持上一轮可入库结果。
2) 当前批次进度
状态	说明
🟡 待补强	当前 split 仅剩 1971 Caprice Convertible 存疑行；其余记录均可入库。
🟢 可用部分	Camaro ZL1 Convertible、Caprice Coupe、Caprice Wagon 已可入库。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.6	2017/2019 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds proxy	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971						1971 Chevrolet full-size brochure / Caprice hardtop coupe & sedan ranges checked; Caprice Convertible not confirmed	疑似Impala Convertible混入	待终核: 疑似应删除
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	53.5	1971 Chevrolet Caprice Custom Coupe 400 V-8 Turbo-Jet, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	53.5	1972 Chevrolet Caprice Custom Coupe 454-4 V-8, Automobile-Catalog / 1972 Chevrolet Caprice brochure coupe dimensions	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			221.9	79.5	53.7	1973 Chevrolet Caprice Classic Coupe 454-4 V-8, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice Custom Station Wagon 396 V-8 Turbo-Jet, Automobile-Catalog	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1967			212.4	79.9	56.7	1967 Chevrolet Caprice Custom Station Wagon 283/327 V-8, Automobile-Catalog	wagon高车身	可入库
4) 下一步优先核对

只剩 1971 Chevrolet Caprice Convertible：下一轮建议若仍找不到独立 Caprice Convertible 证据，就把该行最终标记为“删除/不入库”，而不是继续保留空尺寸待核。

下一步


--- Round 8 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Caprice Convertible	值修改	1971 Convertible 行最终不入库：当前可核来源能确认 1971 Caprice 有 Coupe/Sedan/Wagon 等 Caprice 车身页，但没有可支撑“1971 Caprice Convertible”独立尺寸的可靠规格页；同时资料显示 1971-1972 Chevrolet full-size convertible 主要归 Impala 口径，1973 才明确进入 Caprice Classic convertible 口径。
Facebook
+2
Dezo's Garage
+2

Chevrolet Caprice Convertible	值修改	尺寸继续留空，迭代状态改为 不入库: 疑似Impala Convertible混入，避免空尺寸行被误判为待补强可用记录。
其余记录	稳定	Camaro、Caprice Coupe 1971-1973、Caprice Wagon 1966/1967 均保持可入库。
2) 当前批次进度
状态	说明
🟢 已收尾	当前 split 内可确认记录均已可入库；唯一存疑记录已明确标记为不入库，不再作为待补强尺寸缺口。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.6	2017/2019 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds proxy	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971						1971 Chevrolet full-size brochure / Caprice hardtop coupe & sedan ranges checked; Caprice Convertible not confirmed	疑似Impala Convertible混入	不入库: 疑似Impala Convertible混入
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	53.5	1971 Chevrolet Caprice Custom Coupe 400 V-8 Turbo-Jet, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	53.5	1972 Chevrolet Caprice Custom Coupe 454-4 V-8, Automobile-Catalog / 1972 Chevrolet Caprice brochure coupe dimensions	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			221.9	79.5	53.7	1973 Chevrolet Caprice Classic Coupe 454-4 V-8, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice Custom Station Wagon 396 V-8 Turbo-Jet, Automobile-Catalog	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1967			212.4	79.9	56.7	1967 Chevrolet Caprice Custom Station Wagon 283/327 V-8, Automobile-Catalog	wagon高车身	可入库
4) 下一步优先核对

当前 split_part_03 已无继续待补强的尺寸缺口；后续合并总表时建议过滤 不入库 行，或人工确认后删除该 1971 Caprice Convertible 行。


--- Round 9 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Caprice Convertible	值修改	将 1971 Convertible 存疑行进一步收敛为 不入库: 删除候选-疑似Impala Convertible混入，便于后续合并总表时直接过滤，不再作为待补强尺寸缺口。
Chevrolet Caprice Convertible	值修改	参考车型字段改成更明确的“未确认 Caprice Convertible 独立车型”，尺寸继续留空，避免误入库。
其余记录	稳定	Camaro、Caprice Coupe 1971-1973、Caprice Wagon 1966/1967 均保持可入库。
2) 当前批次进度
状态	说明
🟢 已完成	当前 split_part_03 内可确认尺寸记录均已可入库；唯一异常行已标记为不入库删除候选。
🟢 可出库	过滤 不入库 行后，其余记录可进入后续合并。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	ZL1	gen6 sports car	2017-2019			190.2	75	52.6	2017/2019 Chevrolet Camaro Convertible ZL1, Edmunds / 2018 Chevrolet Camaro Convertible ZL1, Edmunds proxy	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Convertible	Std.	gen2 full-size	1971						1971 Chevrolet Caprice Convertible not confirmed; Caprice hardtop coupe/sedan/wagon checked; likely Impala Convertible mixed in	疑似Impala Convertible混入	不入库: 删除候选-疑似Impala Convertible混入
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1971			216.8	79.5	53.5	1971 Chevrolet Caprice Custom Coupe 400 V-8 Turbo-Jet, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1972			219.9	79.5	53.5	1972 Chevrolet Caprice Custom Coupe 454-4 V-8, Automobile-Catalog / 1972 Chevrolet Caprice brochure coupe dimensions	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	跑车	Chevrolet Caprice	Coupe	Std.	gen2 full-size	1973			221.9	79.5	53.7	1973 Chevrolet Caprice Classic Coupe 454-4 V-8, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice Custom Station Wagon 396 V-8 Turbo-Jet, Automobile-Catalog	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车	Chevrolet Caprice	Wagon	Std.	gen1 full-size	1967			212.4	79.9	56.7	1967 Chevrolet Caprice Custom Station Wagon 283/327 V-8, Automobile-Catalog	wagon高车身	可入库
4) 下一步优先核对

当前批次无继续待补强尺寸项。后续合并总表时，优先过滤或删除 不入库: 删除候选-疑似Impala Convertible混入 这一行，其余行可出库。

本批次完成。

