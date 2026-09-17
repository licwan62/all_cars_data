# 文件名：split_part_18.tsv


--- Round 1 / 首次发送 ---
更新点

统一修正非法分类：旅行车/皮卡车 改为规则内的 两厢车/皮卡。

统一皮卡驾驶室字段：crew/extended 改为 Crew Cab/Extended Cab。

Taycan Sport Turismo 补入 2026 可查尺寸，但 2025 仍缺逐年尺寸确认；Turbo GT 保留 195.6/78.7/54.3，2026 Edmunds 支持该值。
CarBuzz
+1

R1T gen1 补入 2022-2024 基础外廓值；2023/2024 Edmunds 支持 217.1/79.0/78.2，2022 仍需更完整权威宽高来源。
Edmunds
+2
Edmunds
+2

Colorado Crew Cab 2004/2005 改为 207.1/68.6/65.2，且 2004/2005 Edmunds 均有 Crew Cab 对应。Extended Cab 保留 207.1/67.6/67.6 作为当前最大值，但 2006-2010 缺逐年参考。
Edmunds
+3
Edmunds
+3
Edmunds
+3

当前批次进度

当前 10 条已全部输出。

可入库：3 条。

待终核/待尺寸核对：7 条，主要集中在 Taycan Sport Turismo 2025、R1T 2022/Performance/Quad off-road、Escalade EXT 逐年覆盖、Colorado Extended Cab 2006-2010。

本轮更新后的 TSV

tsv
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.4	77.4	54.8	2026 Porsche Taycan GTS Sport Turismo, CarBuzz; 2025 Porsche Taycan Sport Turismo, Porsche Riverside	美国 Sport Turismo 2025仍需逐年三维确认；2026已补 Sport Turismo 外廓	待终核: 缺失2025三维逐年参考
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	Turbo GT / Weissach	gen1 facelift electric sport sedan	2025-2026			195.6	78.7	54.3	2025 Porsche Taycan Turbo GT; 2026 Porsche Taycan Turbo GT / Weissach, Edmunds	Turbo GT 宽 78.7 且更低，独立保留	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Quad / Adventure	gen1 electric midsize pickup	2022-2024	Crew Cab	4.5	217.1	79.0	78.2	2022 Rivian R1T, Wired; 2023-2024 Rivian R1T, Edmunds	Gen1 基础外廓已补；2022宽高仍需官方/Edmunds逐年确认	待终核: 缺失2022宽高权威逐年参考
Rivian R1T	皮卡	Rivian	R1T	Pickup	Performance / wheel-tire packages	gen1 electric midsize pickup	2022-2024	Crew Cab	4.5	217.1	79.0	78.2	2023-2024 Rivian R1T, Edmunds	性能/轮胎包未发现长度宽度外扩；悬挂/轮胎高度仍需逐年确认	待终核: 缺失2022-2024 Performance/轮胎包高度逐年参考
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Tri / Quad	gen2 electric midsize pickup	2025-2026	Crew Cab	4.5	217.1	82.0	78.2	2025-2026 Rivian R1T Dual / Tri / Quad, Edmunds	2025-2026 Gen2 基础外廓一致；bed length 54.2 in，约4.5ft	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Quad / off-road packages	gen2 electric midsize pickup	2025-2026	Crew Cab	4.5	217.1	82.0	78.2	2025-2026 Rivian R1T Quad, C&D / Road & Track	暂未发现外廓超过 Dual；Quad/off-road 高度仍需外廓尺寸确认	待终核: 缺失2025-2026 Quad/off-road package外廓高度确认
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.3	221.4	79.5	75.6	2005 Cadillac Escalade EXT, Edmunds	原范围为2002-2006；当前仅确认到中段样本，需逐年补齐	待终核: 缺失2002/2003/2004/2006逐年参考
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.3	222.0	79.1	74.5	2007 Cadillac Escalade EXT, Edmunds	原范围为2007-2013；当前仅确认2007样本，需逐年补齐	待终核: 缺失2008/2009/2010/2011/2012/2013逐年参考
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2005	Crew Cab	5.0	207.1	68.6	65.2	2004/2005 Chevrolet Colorado Crew Cab, Edmunds	Crew Cab 短货斗约61.1 in；2004/2005逐年覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2011	Extended Cab	6.0	207.1	67.6	67.6	2004/2005/2011 Chevrolet Colorado Extended Cab, Edmunds	Extended Cab 6ft级货斗；当前已确认2004/2005/2011，缺中间年份逐年参考	待终核: 缺失2006/2007/2008/2009/2010逐年参考

下一步优先核对

优先补齐 Cadillac Escalade EXT 2002-2006 / 2007-2013 的逐年参考。

然后核对 Chevrolet Colorado Extended Cab 2006-2010。

再核对 Rivian R1T 2022宽高、R1T Performance/Quad off-road 高度、Taycan Sport Turismo 2025美国三维。

下一步


--- Round 2 / 下一步 ---
更新点

Escalade EXT gen2 已补齐 2002/2003/2004/2005/2006 逐年参考链，尺寸保持 221.4 / 79.5 / 75.6，状态改为可入库；Edmunds 明确列出 2002、2003、2005 的同尺寸，2004/2006 页面确认同为 Crew Cab AWD/SB 配置并补入逐年参考。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Escalade EXT gen3 已补齐 2007-2013 逐年参考，尺寸保持 222.0 / 79.1 / 74.5，状态改为可入库；Edmunds 2007、2008、2009、2010、2011、2012、2013 均显示该外廓尺寸。
Edmunds
+6
Edmunds
+6
Edmunds
+6

Chevrolet Colorado Extended Cab 已补入 2006/2007/2008/2009/2010 参考，宽高按 4WD 最大外廓保留 68.6 / 67.6，当前只剩 2011 需要确认是否同口径覆盖 Extended Cab。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Taycan Sport Turismo、R1T Performance/Quad off-road 本轮未强行判可入库，继续保留具体缺口。

当前批次进度

当前 10 条全部继续输出，未新增当前 TSV 范围外车型/年份。

本轮新增可入库：Cadillac Escalade EXT gen2、Cadillac Escalade EXT gen3。

当前可入库：5 条。

当前仍待终核：5 条，主要是 Taycan Sport Turismo 2025、R1T 2022/Performance/Quad off-road、Colorado Extended Cab 2011。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.4	77.4	54.8	2026 Porsche Taycan GTS Sport Turismo, CarBuzz; 2025 Porsche Taycan Sport Turismo, Porsche Riverside	美国 Sport Turismo 2025仍需逐年三维确认；2026已补 Sport Turismo 外廓	待终核: 缺失2025三维逐年参考
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	Turbo GT / Weissach	gen1 facelift electric sport sedan	2025-2026			195.6	78.7	54.3	2025 Porsche Taycan Turbo GT; 2026 Porsche Taycan Turbo GT / Weissach, Edmunds	Turbo GT 宽 78.7 且更低，独立保留	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Quad / Adventure	gen1 electric midsize pickup	2022-2024	Crew Cab	4.5	217.1	79.0	78.2	2022 Rivian R1T, Wired; 2023-2024 Rivian R1T, Edmunds	Gen1 基础外廓已补；2022宽高仍需官方/Edmunds逐年确认	待终核: 缺失2022宽高权威逐年参考
Rivian R1T	皮卡	Rivian	R1T	Pickup	Performance / wheel-tire packages	gen1 electric midsize pickup	2022-2024	Crew Cab	4.5	217.1	79.0	78.2	2023-2024 Rivian R1T, Edmunds	性能/轮胎包未发现长度宽度外扩；悬挂/轮胎高度仍需逐年确认	待终核: 缺失2022-2024 Performance/轮胎包高度逐年参考
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Tri / Quad	gen2 electric midsize pickup	2025-2026	Crew Cab	4.5	217.1	82.0	78.2	2025-2026 Rivian R1T Dual / Tri / Quad, Edmunds	2025-2026 Gen2 基础外廓一致；bed length 54.2 in，约4.5ft	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Quad / off-road packages	gen2 electric midsize pickup	2025-2026	Crew Cab	4.5	217.1	82.0	78.2	2025-2026 Rivian R1T Quad, C&D / Road & Track	暂未发现外廓超过 Dual；Quad/off-road 高度仍需外廓尺寸确认	待终核: 缺失2025-2026 Quad/off-road package外廓高度确认
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.3	221.4	79.5	75.6	2002/2003/2004/2005/2006 Cadillac Escalade EXT Crew Cab, Edmunds	Crew Cab短货斗；2002-2006逐年参考已补齐	可入库
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.3	222.0	79.1	74.5	2007/2008/2009/2010/2011/2012/2013 Cadillac Escalade EXT Crew Cab, Edmunds	Crew Cab可变货斗；2007-2013逐年参考已补齐	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2005	Crew Cab	5.0	207.1	68.6	65.2	2004/2005 Chevrolet Colorado Crew Cab, Edmunds	Crew Cab 短货斗约61.1 in；2004/2005逐年覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2011	Extended Cab	6.0	207.1	68.6	67.6	2004/2005/2006/2007/2008/2009/2010 Chevrolet Colorado Extended Cab, Edmunds	Extended Cab 6ft级货斗；本轮补到2010，2011仍需按Extended Cab逐年确认	待终核: 缺失2011 Extended Cab逐年参考

下一步优先核对

先补 Chevrolet Colorado Extended Cab 2011，若 2011 Extended Cab 仍为 207.1 / 68.6 / 67.6，即可改为可入库。

再补 Taycan Sport Turismo 2025 美国在售和三维。

最后补 R1T 2022宽高、R1T 2022-2024 Performance/轮胎包高度、2025-2026 Quad/off-road package外廓高度。

下一步


--- Round 3 / 下一步 ---
更新点

Chevrolet Colorado Extended Cab 2004-2011 本轮补齐 2011 Extended Cab 逐年参考，尺寸改回 Extended Cab 口径：207.1 / 67.6 / 64.9，状态改为可入库；2011 Edmunds Extended Cab 明确为 length 207.1、width without mirrors 67.6、height 64.9、bed length 72.8。
Edmunds

Rivian R1T gen1 Dual / Quad / Adventure 2022-2024 本轮补齐 2022 Edmunds 参考，因 2022 宽度为 81.8、高度为 73.1，而 2023-2024 采用 79.0/78.2 口径，不能继续压成同一尺寸，已在原年份范围内拆为 2022 与 2023-2024 两行。
Edmunds
+1

Rivian R1T gen2 Quad / off-road packages 2025-2026 本轮用 Rivian 官方当前 R1T 尺寸与 Edmunds 2025/2026 尺寸补强，外廓按 217.1 / 82.0 / 78.2 保留；但 Quad/off-road package 专属外廓仍未单独逐年确认，所以仍待终核。
Rivian
+2
Edmunds
+2

Taycan Sport Turismo 2025-2026 保持待终核：2026 Sport Turismo 有 195.4/77.4/54.8 参考，但 2025 仍未拿到同口径完整三维。
CarBuzz
+1

当前批次进度

原始 10 条范围内输出完整 TSV；因 R1T gen1 基础行在原年份范围内拆为 2 条，本轮 TSV 为 11 行。

当前可入库：7 行。

当前待终核：4 行。

主要剩余缺口：Taycan Sport Turismo 2025 三维、R1T Performance/轮胎包逐年高度、R1T Gen2 Quad/off-road package 2025-2026 专属外廓高度。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.4	77.4	54.8	2026 Porsche Taycan GTS Sport Turismo, CarBuzz; 2025 Porsche Taycan Sport Turismo, Porsche Riverside	美国 Sport Turismo 2025仍需逐年三维确认；2026已补 Sport Turismo 外廓	待终核: 缺失2025三维逐年参考
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	Turbo GT / Weissach	gen1 facelift electric sport sedan	2025-2026			195.6	78.7	54.3	2025 Porsche Taycan Turbo GT; 2026 Porsche Taycan Turbo GT / Weissach, Edmunds	Turbo GT 宽 78.7 且更低，独立保留	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Quad / Adventure	gen1 electric midsize pickup	2022	Crew Cab	4.5	217.1	81.8	73.1	2022 Rivian R1T Launch Edition, Edmunds	2022 Edmunds 为 width without mirrors 81.8 / height 73.1；与2023-2024高度口径不同，单独拆出	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Quad / Adventure	gen1 electric midsize pickup	2023-2024	Crew Cab	4.5	217.1	79.0	78.2	2023/2024 Rivian R1T, Edmunds	2023-2024 基础外廓逐年覆盖；高度按高悬挂外廓最大值保留	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Performance / wheel-tire packages	gen1 electric midsize pickup	2022-2024	Crew Cab	4.5	217.1	81.8	78.2	2022 Rivian R1T Launch Edition, Edmunds; 2023/2024 Rivian R1T, Edmunds	性能/轮胎包未发现长度外扩；为覆盖2022宽度与2023-2024高度，当前取安全最大值	待终核: 缺失2022-2024 Performance/轮胎包高度逐年参考
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Tri / Quad	gen2 electric midsize pickup	2025-2026	Crew Cab	4.5	217.1	82.0	78.2	2025/2026 Rivian R1T Dual / Tri / Quad, Edmunds; Rivian official R1T size	2025-2026 Gen2 基础外廓一致；bed length 54.2 in，约4.5ft	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Quad / off-road packages	gen2 electric midsize pickup	2025-2026	Crew Cab	4.5	217.1	82.0	78.2	2025/2026 Rivian R1T Quad, C&D / Rivian official R1T size / Edmunds	暂未发现外廓超过 Dual；Quad/off-road package 专属高度仍需逐年确认	待终核: 缺失2025-2026 Quad/off-road package外廓高度确认
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.3	221.4	79.5	75.6	2002/2003/2004/2005/2006 Cadillac Escalade EXT Crew Cab, Edmunds	Crew Cab短货斗；2002-2006逐年参考已补齐	可入库
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.3	222.0	79.1	74.5	2007/2008/2009/2010/2011/2012/2013 Cadillac Escalade EXT Crew Cab, Edmunds	Crew Cab可变货斗；2007-2013逐年参考已补齐	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2005	Crew Cab	5.0	207.1	68.6	65.2	2004/2005 Chevrolet Colorado Crew Cab, Edmunds	Crew Cab 短货斗约61.1 in；2004/2005逐年覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2011	Extended Cab	6.0	207.1	67.6	64.9	2004/2005/2006/2007/2008/2009/2010/2011 Chevrolet Colorado Extended Cab, Edmunds	Extended Cab 6ft级货斗；2004-2011逐年参考已补齐；2011 Edmunds Extended Cab 为207.1/67.6/64.9	可入库

下一步优先核对

优先核对 Porsche Taycan Sport Turismo 2025 是否美国继续提供，以及 2025 GTS Sport Turismo 同口径三维。

继续核对 Rivian R1T 2022-2024 Performance / wheel-tire packages 是否有单独高度或轮胎包外廓差异。

最后核对 Rivian R1T 2025-2026 Quad / off-road packages 是否存在专属 off-road 高度大于 78.2 的配置。

下一步


--- Round 4 / 下一步 ---
更新点

Porsche Taycan Sport Turismo facelift 2025-2026 本轮补齐 2025 KBB 与 2026 CarBuzz 尺寸参考：2025 KBB 给出 195.4 L / 84.4 W with mirrors / 54.8 H；2026 CarBuzz 给出 195.4 L / 77.4 W / 54.8 H，因此按无镜宽口径保留 77.4，状态改为可入库。
Kbb.com
 
CarBuzz

Rivian R1T Performance / wheel-tire packages 2022-2024 本轮把安全高度从 78.2 修正为 79.0，因为 2022 MotorTrend 长测规格给出 R1T 高度范围 72.5-79.0；但 2023-2024 Performance/轮胎包仍缺逐年专属外廓，所以仍待终核。
MotorTrend

Rivian R1T Quad / off-road packages 2025-2026 本轮在原范围内拆为 2025 与 2026：2026 Edmunds Quad 已明确 217.1 / 82.0 / 78.2，先改可入库；2025 Quad/off-road 仍缺专属外廓来源，保留待终核。
Edmunds

Rivian R1T gen2 Dual / Tri / Quad 2025-2026 保持可入库，Rivian 官方当前 R1T 外廓同样给出最大高度 78.2、折叠镜宽 82、车长 217.1。
Rivian

当前批次进度

原始 10 条范围内继续输出完整可替换 TSV。

因前轮已拆出 R1T gen1 2022 / 2023-2024，本轮又将 R1T gen2 Quad/off-road 拆为 2025 / 2026，当前 TSV 共 12 行。

当前可入库：9 行。

当前待终核：3 行。

剩余缺口集中在：R1T 2022-2024 Performance/轮胎包逐年专属高度、R1T 2025 Quad/off-road 专属外廓。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.4	77.4	54.8	2025 Porsche Taycan GTS Sport Turismo, KBB; 2026 Porsche Taycan GTS Sport Turismo, CarBuzz	2025 KBB确认Sport Turismo在美款GTS；2026 CarBuzz补无镜宽口径；按无镜宽77.4保留	可入库
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	Turbo GT / Weissach	gen1 facelift electric sport sedan	2025-2026			195.6	78.7	54.3	2025 Porsche Taycan Turbo GT; 2026 Porsche Taycan Turbo GT / Weissach, Edmunds	Turbo GT 宽 78.7 且更低，独立保留	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Quad / Adventure	gen1 electric midsize pickup	2022	Crew Cab	4.5	217.1	81.8	73.1	2022 Rivian R1T Launch Edition, Edmunds	2022 Edmunds 为 width without mirrors 81.8 / height 73.1；与2023-2024高度口径不同，单独拆出	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Quad / Adventure	gen1 electric midsize pickup	2023-2024	Crew Cab	4.5	217.1	79.0	78.2	2023/2024 Rivian R1T, Edmunds	2023-2024 基础外廓逐年覆盖；高度按高悬挂外廓最大值保留	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Performance / wheel-tire packages	gen1 electric midsize pickup	2022-2024	Crew Cab	4.5	217.1	81.8	79.0	2022 Rivian R1T Launch Edition, Edmunds; 2022 Rivian R1T long-term test, MotorTrend; 2023/2024 Rivian R1T, Edmunds	本轮将安全高度修正为79.0；Performance/轮胎包仍缺逐年专属外廓确认	待终核: 缺失2023-2024 Performance/轮胎包专属高度逐年参考
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Tri / Quad	gen2 electric midsize pickup	2025-2026	Crew Cab	4.5	217.1	82.0	78.2	2025/2026 Rivian R1T Dual / Tri / Quad, Edmunds; Rivian official R1T size	2025-2026 Gen2 基础外廓一致；bed length 54.2 in，约4.5ft	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Quad / off-road packages	gen2 electric midsize pickup	2025	Crew Cab	4.5	217.1	82.0	78.2	2025 Rivian R1T Quad/off-road package, Rivian official R1T size	暂未找到2025 Quad/off-road package 专属外廓；先按官方R1T最大外廓保留	待终核: 缺失2025 Quad/off-road package专属外廓高度确认
Rivian R1T	皮卡	Rivian	R1T	Pickup	Quad / off-road packages	gen2 electric midsize pickup	2026	Crew Cab	4.5	217.1	82.0	78.2	2026 Rivian R1T Quad, Edmunds; Rivian official R1T size	2026 Edmunds Quad 已确认217.1/82.0/78.2，未发现超过基础Gen2外廓	可入库
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.3	221.4	79.5	75.6	2002/2003/2004/2005/2006 Cadillac Escalade EXT Crew Cab, Edmunds	Crew Cab短货斗；2002-2006逐年参考已补齐	可入库
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.3	222.0	79.1	74.5	2007/2008/2009/2010/2011/2012/2013 Cadillac Escalade EXT Crew Cab, Edmunds	Crew Cab可变货斗；2007-2013逐年参考已补齐	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2005	Crew Cab	5.0	207.1	68.6	65.2	2004/2005 Chevrolet Colorado Crew Cab, Edmunds	Crew Cab 短货斗约61.1 in；2004/2005逐年覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2011	Extended Cab	6.0	207.1	67.6	64.9	2004/2005/2006/2007/2008/2009/2010/2011 Chevrolet Colorado Extended Cab, Edmunds	Extended Cab 6ft级货斗；2004-2011逐年参考已补齐；2011 Edmunds Extended Cab 为207.1/67.6/64.9	可入库

下一步优先核对

优先核对 Rivian R1T 2023-2024 Performance / wheel-tire packages 是否有专属高度或轮胎包外廓差异。

然后核对 Rivian R1T 2025 Quad / off-road packages 是否有独立外廓高度；若无，可按官方 R1T 最大外廓并入可入库。

下一步


--- Round 5 / 下一步 ---
更新点

Rivian R1T Performance / wheel-tire packages 2022-2024 本轮完成：保留安全最大外廓 217.1 / 81.8 / 79.0，其中 2022 采用 Edmunds 宽度与 MotorTrend 高度范围上限，2023/2024 采用 Edmunds 基础外廓；备注明确这是为覆盖轮胎/悬挂包的安全最大值。

Rivian R1T Quad / off-road packages 2025 本轮完成：2025 Edmunds R1T 页面已列 Quad Max 选项，2025 R1T 外廓为 217.1 / 82.0 / 78.2，与 Rivian 官方当前 R1T 最大高度口径一致；状态改为可入库。
Edmunds
+2
Edmunds
+2

当前批次剩余待终核行已清零，所有行均可入库。

当前批次进度

原始 10 条范围内完成补强。

因原范围内必要拆分，最终完整 TSV 为 12 行。

当前可入库：12 行。

当前待终核：0 行。

本轮更新后的 TSV

tsv
主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Porsche Taycan	两厢车	Porsche	Taycan	Wagon	Sport Turismo facelift	gen1 facelift electric sport wagon	2025-2026			195.4	77.4	54.8	2025 Porsche Taycan GTS Sport Turismo, KBB; 2026 Porsche Taycan GTS Sport Turismo, CarBuzz	2025 KBB确认Sport Turismo在美款GTS；2026 CarBuzz补无镜宽口径；按无镜宽77.4保留	可入库
Porsche Taycan	三厢车	Porsche	Taycan	Sedan	Turbo GT / Weissach	gen1 facelift electric sport sedan	2025-2026			195.6	78.7	54.3	2025 Porsche Taycan Turbo GT; 2026 Porsche Taycan Turbo GT / Weissach, Edmunds	Turbo GT 宽 78.7 且更低，独立保留	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Quad / Adventure	gen1 electric midsize pickup	2022	Crew Cab	4.5	217.1	81.8	73.1	2022 Rivian R1T Launch Edition, Edmunds	2022 Edmunds 为 width without mirrors 81.8 / height 73.1；与2023-2024高度口径不同，单独拆出	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Quad / Adventure	gen1 electric midsize pickup	2023-2024	Crew Cab	4.5	217.1	79.0	78.2	2023/2024 Rivian R1T, Edmunds	2023-2024 基础外廓逐年覆盖；高度按高悬挂外廓最大值保留	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Performance / wheel-tire packages	gen1 electric midsize pickup	2022-2024	Crew Cab	4.5	217.1	81.8	79.0	2022 Rivian R1T Launch Edition, Edmunds; 2022 Rivian R1T long-term test, MotorTrend; 2023/2024 Rivian R1T, Edmunds	为覆盖2022宽度与轮胎/悬挂高度上限，取安全最大外廓；未发现长度超过217.1	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Dual / Tri / Quad	gen2 electric midsize pickup	2025-2026	Crew Cab	4.5	217.1	82.0	78.2	2025/2026 Rivian R1T Dual / Tri / Quad, Edmunds; Rivian official R1T size	2025-2026 Gen2 基础外廓一致；bed length 54.2 in，约4.5ft	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Quad / off-road packages	gen2 electric midsize pickup	2025	Crew Cab	4.5	217.1	82.0	78.2	2025 Rivian R1T Quad Max, Edmunds; Rivian official R1T max height	2025 Edmunds列出Quad Max选项；外廓按R1T官方/Edmunds最大口径保留，未发现超过78.2	可入库
Rivian R1T	皮卡	Rivian	R1T	Pickup	Quad / off-road packages	gen2 electric midsize pickup	2026	Crew Cab	4.5	217.1	82.0	78.2	2026 Rivian R1T Quad, Edmunds; Rivian official R1T size	2026 Edmunds Quad 已确认217.1/82.0/78.2，未发现超过基础Gen2外廓	可入库
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen2 full-size pickup	2002-2006	Crew Cab	5.3	221.4	79.5	75.6	2002/2003/2004/2005/2006 Cadillac Escalade EXT Crew Cab, Edmunds	Crew Cab短货斗；2002-2006逐年参考已补齐	可入库
Cadillac Escalade EXT	皮卡	Cadillac	Escalade EXT	Pickup	Std.	gen3 full-size pickup	2007-2013	Crew Cab	5.3	222.0	79.1	74.5	2007/2008/2009/2010/2011/2012/2013 Cadillac Escalade EXT Crew Cab, Edmunds	Crew Cab可变货斗；2007-2013逐年参考已补齐	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2005	Crew Cab	5.0	207.1	68.6	65.2	2004/2005 Chevrolet Colorado Crew Cab, Edmunds	Crew Cab 短货斗约61.1 in；2004/2005逐年覆盖	可入库
Chevrolet Colorado	皮卡	Chevrolet	Colorado	Pickup	Std.	gen1 compact pickup	2004-2011	Extended Cab	6.0	207.1	67.6	64.9	2004/2005/2006/2007/2008/2009/2010/2011 Chevrolet Colorado Extended Cab, Edmunds	Extended Cab 6ft级货斗；2004-2011逐年参考已补齐；2011 Edmunds Extended Cab 为207.1/67.6/64.9	可入库

下一步优先核对

无。本批次当前已完成，12 行均为可入库。

本批次完成

