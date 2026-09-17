# 文件名：split_part_100.tsv


--- Round 1 / 首次发送 ---
更新点
车型	操作	描述
Nissan Frontier	字段修正	Pikup 修正为 Pickup；regular/king/crew 标准化为 Regular Cab / King Cab / Crew Cab。
Nissan Frontier	拆出	补入 gen1 缺失的 Crew Cab 结构；2004 Crew Cab 有短斗与长斗两种外长，不能只保留 Regular/King Cab。
Edmunds
+1

Nissan Frontier	新增	补入 gen3 2022-2026；2022+ 有 King Cab 6 ft、Crew Cab 5 ft、Crew Cab 6 ft，Crew Cab 长斗外长 224.1 in。
Edmunds
+2
Kbb.com
+2

Nissan Frontier	压缩	gen2 2005-2021 按 King Cab 6.0 / Crew Cab 5.0 / Crew Cab 6.0 合并为连续区间；2005 King Cab、2013/2020 Crew Cab 尺寸来源已核。
Edmunds
+2
Edmunds
+2
当前批次进度
状态	内容
🟡 待补强	gen1 Regular Cab / King Cab 的 1998-2004 最大高度仍建议逐年终核；gen1 Crew Cab 长斗是否覆盖 2002-2004 仍待终核。
🟢 已推进	已补齐 Frontier 从 gen1 到 gen3 的主结构口径，并输出本轮更新后的完整 TSV。
本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998-2004	Regular Cab	6.0	196.1	66.5	67.1	1998-2004 Frontier Regular Cab	标准单排长斗口径	待终核: 1998-2004 Regular Cab逐年最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998-2004	King Cab	6.0	202.9	67.7	67.1	1998-2004 Frontier King Cab	加长驾驶室6ft斗	待终核: 1998-2003 King Cab逐年最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001-2003	Crew Cab	4.5	200.0	71.9	65.9	2001-2003 Frontier Crew Cab SB	短斗Crew Cab	待终核: 2002-2003 Crew Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	71.8	2004 Frontier Crew Cab LE/SVE-V6 LB	长斗Crew Cab	待终核: Crew Cab长斗起始年份
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	68.7	2005-2021 Frontier King Cab	6ft斗	待终核: 2006-2021 King Cab逐年最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	King Cab	6.0	210.2	73.0	72.1	2022-2026 Frontier King Cab 6 ft	6ft斗	待终核: 2022-2023 King Cab逐年最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	6.0	224.1	74.7	72.9	2022-2026 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
下一步优先核对

优先终核 gen1 Regular/King Cab 1998-2004 的逐年最大高度，以及 gen1 Crew Cab 长斗是否只限 2004 或覆盖更早年份。

下一步


--- Round 2 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	值修改	gen1 Regular Cab 不再沿用原表 196.1 in；1998 Regular Cab Edmunds 为 184.3×66.5×62.5，2001 Regular Cab Edmunds 为 191.3×66.5×62.8。
Edmunds
+1

Nissan Frontier	拆出	gen1 Crew Cab 长斗从 2002 已存在，Edmunds 2002 Crew Cab Long Bed 为 217.8×71.2×74.0；KBB 也显示 2002 Crew Cab 有 4.5 ft 与 6 ft 两种床长。
Edmunds
+1

Nissan Frontier	值修改	gen1 2003-2004 King Cab 按 Edmunds 2003 / 2004 King Cab 口径修正为 202.9×67.7×66.7 / 202.9×67.7×63.2，不能继续和 1998-2002 混压。
Edmunds
+1

Nissan Frontier	补强	gen3 2022-2026 保留 King Cab / Crew Cab 5 ft / Crew Cab 6 ft；2026 Edmunds 显示仍有 King Cab，2026 Crew Cab 与 SV 长斗页面可对应短斗/长斗床长。
Edmunds
+2
Edmunds
+2
2) 当前批次进度
状态	内容
🟡 待补强	gen1 1999-2000 Regular Cab、1999-2000 King Cab、2001-2003 Crew Cab 短斗/长斗仍需逐年补强到可入库。
🟢 已推进	本轮已修正原表中 Regular Cab/King Cab/Crew Cab 混用问题，并将 2002-2004 Crew Cab 长斗拆出为独立记录。
🟢 已推进	gen2 2005-2021 与 gen3 2022-2026 已按 cab + bed 结构完整保留。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999-2000	Regular Cab	6.0				1999-2000 Frontier Regular Cab	待补单排尺寸	待终核: 1999-2000 Regular Cab尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998-2000	King Cab	6.0	196.1	66.5	67.1	1998-2000 Frontier King Cab	早期King Cab	待终核: 1999-2000 King Cab逐年尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001-2002	King Cab	6.0	200.0	71.9	65.9	2001-2002 Frontier King Cab	中期King Cab宽体口径	待终核: 2002 King Cab最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000		Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SB	初期Crew Cab短斗	待终核: 2000 Crew Cab尺寸复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001		Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002-2003	Crew Cab	4.5	199.9	71.2	74.0	2002/2003 Frontier Crew Cab SB	短斗Crew Cab; 取高车身口径	待终核: 2003 Crew Cab SB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002-2004	Crew Cab	6.0	217.8	71.2	74.0	2002/2004 Frontier Crew Cab LB	长斗Crew Cab	待终核: 2003 Crew Cab LB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	70.1	2005/2021 Frontier King Cab	6ft斗; 统一按最大高度	待终核: 2006-2020 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	King Cab	6.0	210.2	73.0	72.1	2022/2025/2026 Frontier King Cab 6 ft	6ft斗	待终核: 2023-2024 King Cab逐年最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	6.0	224.1	74.7	72.9	2022/2026 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2023-2025 Crew Cab 6ft逐年确认
4) 下一步优先核对

优先补齐 3 个缺口：1999-2000 Regular Cab、1999-2000 King Cab、2003 Crew Cab 短斗/长斗；然后再把 gen2 King Cab 2006-2020 与 gen3 King/Crew 长斗中间年份补到可入库。

5) 下一步


--- Round 3 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	字段修正	修复上一轮 TSV 中 2000 Crew Cab / 2001 Crew Cab 行字段错位问题：驾驶室类型=Crew Cab、货斗长度_ft=4.5。
Nissan Frontier	值修改	1999-2000 Regular Cab 已推进：2000 Regular Cab Edmunds 核到 184.3×66.5×62.8；1999 参考 Cars.com/KBB 先按 184.3 长度、66.5 宽度、62.2 高度拆出，仍保留待终核。
Edmunds
+1

Nissan Frontier	值修改	2023 King Cab Edmunds 核到 210.2×73.0×72.1；2024 King Cab Edmunds 核到 210.2×73.0×71.7，因此 gen3 King Cab 2022-2026 保留 72.1 最大高度，但仍待补 2025-2026 逐年确认。
Edmunds
+1

Nissan Frontier	状态推进	2002 Crew Cab 短斗已由 Edmunds 确认 199.9×71.2×74.0；KBB 确认 2002 Crew Cab 同时有 4.5 ft 与 6 ft bed。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 已推进	原始输入 20 行已整理为当前 18 行结构化 TSV；字段顺序统一，结构统一为 Pickup，驾驶室/货斗已拆字段。
🟡 待补强	仍有 gen1 1999 Regular Cab、1999-2000 King Cab、2003 Crew Cab SB/LB、gen2 King Cab 中间年份、gen3 King Cab/长斗中间年份待终核。
🟡 当前状态	还不能写“本批次完成”，因为仍存在待终核行。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	66.5	62.2	1999 Frontier Regular Cab	早期单排短车身	待终核: 1999 Regular Cab宽度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998-2000	King Cab	6.0	196.1	66.5	67.1	1998/1999/2000 Frontier King Cab	早期King Cab	待终核: 2000 King Cab高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001-2002	King Cab	6.0	200.0	71.9	65.9	2001/2002 Frontier King Cab	中期King Cab宽体口径	待终核: 2002 King Cab最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SB	初期Crew Cab短斗	待终核: 2000 Crew Cab尺寸复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	74.0	2003 Frontier Crew Cab SB	短斗Crew Cab	待终核: 2003 Crew Cab SB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002-2004	Crew Cab	6.0	217.8	71.2	74.0	2002/2003/2004 Frontier Crew Cab LB	长斗Crew Cab	待终核: 2003 Crew Cab LB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	70.1	2005/2021 Frontier King Cab	6ft斗; 统一按最大高度	待终核: 2006-2020 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	King Cab	6.0	210.2	73.0	72.1	2022/2023/2024/2026 Frontier King Cab 6 ft	6ft斗	待终核: 2025 King Cab逐年最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	6.0	224.1	74.7	72.9	2022/2026 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2023-2025 Crew Cab 6ft逐年确认
4) 下一步优先核对

下一轮优先把 1999 Regular Cab、1998-2000 King Cab、2001-2002 King Cab、2003 Crew Cab SB/LB 这几个 gen1 缺口清掉；之后再集中处理 gen2 King Cab 2006-2020 和 gen3 2025 King Cab / 2023-2025 Crew Cab 6ft。

下一步


--- Round 4 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出	1998-2000 King Cab 不再混压：2000 Edmunds 可核到 196.1×66.5×62.6，单独拆出为可入库；1998-1999 仍保留待终核。
Edmunds

Nissan Frontier	状态推进	1999 Regular Cab 长度/高度由 Cars.com 核到 184.3×62.2，宽度仍沿用同年 Frontier 口径，先保留“宽度复核”。
Cars.com

Nissan Frontier	结构确认	2003 Crew Cab KBB 确认同时存在 4.5 ft 与 6 ft bed，因此 SB/LB 拆分保留，继续待尺寸终核。
Kbb.com

Nissan Frontier	状态推进	gen3 2025 Crew Cab 5 ft 已核到 210.2×74.7×72.9；2025 开始 Crew Cab 长轴/长斗选择扩展，长斗行参考车型补入 2025。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 已推进	本轮新增实际变化：拆出 2000 King Cab 可入库行，缩小 1998-1999 King Cab 待终核范围，并补强 gen3 2025 参考。
🟡 待补强	仍待终核：1999 Regular Cab 宽度、1998-1999 King Cab、2001-2002 King Cab、2000/2003 Crew Cab SB、2003 Crew Cab LB、gen2 King Cab 中间年份、gen3 2025 King Cab 与 2023-2024 Crew Cab 6ft。
🟡 当前状态	仍未完成，不能输出“本批次完成”。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	66.5	62.2	1999 Frontier Regular Cab	早期单排短车身	待终核: 1999 Regular Cab宽度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998-1999	King Cab	6.0	196.1	66.5	67.1	1998/1999 Frontier King Cab	早期King Cab	待终核: 1998-1999 King Cab高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001-2002	King Cab	6.0	200.0	71.9	65.9	2001/2002 Frontier King Cab	中期King Cab宽体口径	待终核: 2002 King Cab最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SB	初期Crew Cab短斗	待终核: 2000 Crew Cab尺寸复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	74.0	2003 Frontier Crew Cab SB	短斗Crew Cab; KBB确认4.5ft bed存在	待终核: 2003 Crew Cab SB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002-2004	Crew Cab	6.0	217.8	71.2	74.0	2002/2003/2004 Frontier Crew Cab LB	长斗Crew Cab; KBB确认2003 6ft bed存在	待终核: 2003 Crew Cab LB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	70.1	2005/2021 Frontier King Cab	6ft斗; 统一按最大高度	待终核: 2006-2020 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	King Cab	6.0	210.2	73.0	72.1	2022/2023/2024/2026 Frontier King Cab 6 ft	6ft斗	待终核: 2025 King Cab逐年最大高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	6.0	224.1	74.7	72.9	2022/2025/2026 Frontier Crew Cab 6 ft	长斗Crew Cab; 2025长轴选择扩展	待终核: 2023-2024 Crew Cab 6ft逐年确认
4) 下一步优先核对

下一轮优先处理 gen1 剩余缺口：1998-1999 King Cab、2001-2002 King Cab、2000 Crew Cab SB、2003 Crew Cab SB/LB。这些清完后，再处理 gen2 King Cab 2006-2020 和 gen3 中间年份。

5) 下一步


--- Round 5 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 值修改	2001-2002 King Cab 拆成 2001 与 2002；2002 King Cab Edmunds 已核到 202.9×67.7×63.2，可入库。
Edmunds

Nissan Frontier	拆出 / 状态推进	gen3 King Cab 不再混写 2022-2026：2025 King Cab Edmunds 为 210.2×73.0×71.5，单独拆出可入库。
Edmunds

Nissan Frontier	状态推进	2025 Crew Cab 6ft 已核到 224.1×74.7×72.9，参考车型补入 2025。
Edmunds

Nissan Frontier	结构确认	2003 Crew Cab 同时存在 4.5 ft 与 6 ft bed，SB/LB 拆分继续保留。
Kbb.com
2) 当前批次进度
状态	内容
🟢 已推进	本轮新增实际 TSV 变化：拆出 2002 King Cab 可入库；拆出 2025 King Cab 可入库；gen3 King Cab 待核范围缩小。
🟡 待补强	剩余重点：1999 Regular Cab 宽度、1998-1999 King Cab、2001 King Cab、2000 Crew Cab SB、2003 Crew Cab SB/LB、gen2 King Cab 2006-2020、gen3 2022-2024/2026 King Cab 与 2023-2024 Crew Cab 6ft。
🟡 当前状态	仍有待终核行，不能输出“本批次完成”。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	66.5	62.2	1999 Frontier Regular Cab	早期单排短车身	待终核: 1999 Regular Cab宽度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998-1999	King Cab	6.0	196.1	66.5	67.1	1998/1999 Frontier King Cab	早期King Cab	待终核: 1998-1999 King Cab高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	200.0	71.9	65.9	2001 Frontier King Cab	中期King Cab宽体口径	待终核: 2001 King Cab尺寸复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SB	初期Crew Cab短斗	待终核: 2000 Crew Cab尺寸复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	74.0	2003 Frontier Crew Cab SB	短斗Crew Cab; KBB确认4.5ft bed存在	待终核: 2003 Crew Cab SB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002-2004	Crew Cab	6.0	217.8	71.2	74.0	2002/2003/2004 Frontier Crew Cab LB	长斗Crew Cab; KBB确认2003 6ft bed存在	待终核: 2003 Crew Cab LB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	70.1	2005/2021 Frontier King Cab	6ft斗; 统一按最大高度	待终核: 2006-2020 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2024	King Cab	6.0	210.2	73.0	72.1	2022/2023/2024 Frontier King Cab 6 ft	6ft斗	待终核: 2022-2024 King Cab高度差异压缩复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	待终核: 2026 King Cab最大高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023-2024	Crew Cab	6.0	224.1	74.7	72.9	2023/2024 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2023-2024 Crew Cab 6ft逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025-2026	Crew Cab	6.0	224.1	74.7	72.9	2025/2026 Frontier Crew Cab 6 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
4) 下一步优先核对

下一轮优先清 gen1：1998-1999 King Cab、2001 King Cab、2000 Crew Cab SB、2003 Crew Cab SB/LB。清完 gen1 后，再处理 gen2 King Cab 2006-2020 与 gen3 2022-2024/2026 King Cab、2023-2024 Crew Cab 6ft。

下一步


--- Round 6 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 值修改	gen3 King Cab 按 2022 / 2023 / 2024 / 2025 / 2026 拆开，不再把高度不同的年份压成 2022-2026；2024 King Cab 为 210.2×73.0×71.8，2026 King Cab 为 210.2×73.0×72.1。
Edmunds
+1

Nissan Frontier	拆出 / 值修改	gen3 Crew Cab 6ft 长斗按 2022 / 2023 / 2024 / 2025 / 2026 拆开；2024 长斗 SV 为 224.1×73.0×71.3，2025 长斗 SL 为 224.1×73.0×72.0。
Edmunds
+1

Nissan Frontier	状态推进	2023 Crew Cab 5ft / 2024 Crew Cab 5ft 继续支持 210.2×74.7×72.9 的最大宽高口径，短斗 2022-2026 保持可入库。
Edmunds
+1

Nissan Frontier	状态推进	2026 车型仍有 King Cab 与 Crew Cab 两种 cab 口径，且 Crew Cab 长斗继续存在，因此 gen3 延续到 2026 合理保留。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 已推进	本轮将 gen3 待终核范围明显缩小：King Cab 已逐年拆出；Crew Cab 6ft 已逐年拆出，2024/2025 已转可入库。
🟡 待补强	gen1 仍剩：1999 Regular Cab 宽度、1998-1999 King Cab、2001 King Cab、2000 Crew Cab SB、2003 Crew Cab SB/LB。
🟡 待补强	gen2 仍剩：King Cab 2006-2020 逐年确认。
🟡 待补强	gen3 仍剩：2022/2023/2026 Crew Cab 6ft 长斗逐年尺寸终核。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	66.5	62.2	1999 Frontier Regular Cab	早期单排短车身	待终核: 1999 Regular Cab宽度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998-1999	King Cab	6.0	196.1	66.5	67.1	1998/1999 Frontier King Cab	早期King Cab	待终核: 1998-1999 King Cab高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	200.0	71.9	65.9	2001 Frontier King Cab	中期King Cab宽体口径	待终核: 2001 King Cab尺寸复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SB	初期Crew Cab短斗	待终核: 2000 Crew Cab尺寸复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	74.0	2003 Frontier Crew Cab SB	短斗Crew Cab; KBB确认4.5ft bed存在	待终核: 2003 Crew Cab SB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002-2004	Crew Cab	6.0	217.8	71.2	74.0	2002/2003/2004 Frontier Crew Cab LB	长斗Crew Cab; KBB确认2003 6ft bed存在	待终核: 2003 Crew Cab LB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	70.1	2005/2021 Frontier King Cab	6ft斗; 统一按最大高度	待终核: 2006-2020 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	待终核: 2022 King Cab最大高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先清剩余 gen1 缺口：1999 Regular Cab、1998-1999 King Cab、2001 King Cab、2000 Crew Cab SB、2003 Crew Cab SB/LB；然后集中处理 gen2 King Cab 2006-2020 和 gen3 2022/2023/2026 Crew Cab 6ft。

5) 下一步


--- Round 7 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	值修改	2001 King Cab 已从待终核推进：Edmunds 普通 King Cab 为 203.1×67.7×62.6，SC-V6 宽高更大为 203.1×71.9×65.9，本轮按最大外廓改为 203.1×71.9×65.9 并转可入库。
Nissan Frontier	状态推进	2000 Crew Cab 4.5 Edmunds 已核到 193.1×71.9×65.9，本轮转可入库。
Nissan Frontier	状态推进	2026 Crew Cab 5.0 Edmunds 为 210.2×74.7×72.9，继续支撑 Crew Cab 5ft 2022-2026 可入库。
Nissan Frontier	结构修正	2026 Crew Cab 6.0 长斗仍保留单独行，但缺少完整外廓页确认，本轮继续保留待终核，不强行并入短斗。
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际推进 2 条 gen1 待核：2001 King Cab 与 2000 Crew Cab SB 转为可入库。
🟡 待补强	gen1 剩余：1999 Regular Cab、1998-1999 King Cab、2003 Crew Cab SB/LB。
🟡 待补强	gen2 剩余：2005-2021 King Cab 6.0 仍需中间年份终核。
🟡 待补强	gen3 剩余：2022 Crew Cab 6ft、2023 Crew Cab 6ft、2026 Crew Cab 6ft 仍需终核。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	66.5	62.2	1999 Frontier Regular Cab	早期单排短车身	待终核: 1999 Regular Cab宽度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998-1999	King Cab	6.0	196.1	66.5	67.1	1998/1999 Frontier King Cab	早期King Cab	待终核: 1998-1999 King Cab高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	74.0	2003 Frontier Crew Cab SB	短斗Crew Cab; KBB确认4.5ft bed存在	待终核: 2003 Crew Cab SB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002-2004	Crew Cab	6.0	217.8	71.2	74.0	2002/2003/2004 Frontier Crew Cab LB	长斗Crew Cab; KBB确认2003 6ft bed存在	待终核: 2003 Crew Cab LB尺寸
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	70.1	2005/2021 Frontier King Cab	6ft斗; 统一按最大高度	待终核: 2006-2020 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	待终核: 2022 King Cab最大高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先处理剩余 gen1：1999 Regular Cab、1998-1999 King Cab、2003 Crew Cab SB/LB；然后补 gen2 King Cab 2006-2020，最后清 gen3 Crew Cab 6ft 2022/2023/2026。

5) 下一步


--- Round 8 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	值修改	1999 Regular Cab 已由 Edmunds 核到 184.3×71.9×66.1，本轮从待终核转为可入库。
Edmunds

Nissan Frontier	拆出 / 值修改	1998-1999 King Cab 不再混压：1998 Edmunds 核到 196.1×66.5×62.8，1999 参考 KBB 长度与床长，宽高仍待终核。
Edmunds
+1

Nissan Frontier	值修改	2003 Crew Cab 4.5 已由 Edmunds 核到 199.9×71.2×69.9，本轮转可入库。
Edmunds

Nissan Frontier	状态推进	2003 Crew Cab 6.0 由 KBB 确认 6 ft bed 存在，但 Edmunds 当前默认页为 SB，因此 LB 仍保留待终核。
Kbb.com
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际更新：1999 Regular Cab 转可入库；1998 King Cab 转可入库；2003 Crew Cab SB 转可入库。
🟡 待补强	gen1 剩余：1999 King Cab、2003 Crew Cab LB。
🟡 待补强	gen2 剩余：King Cab 2006-2020 逐年确认。
🟡 待补强	gen3 剩余：Crew Cab 6ft 的 2022/2023/2026 仍需终核。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1			1999 Frontier King Cab SE	早期King Cab; KBB确认6ft bed	待终核: 1999 King Cab宽高
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8			2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB宽高
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	70.1	2005/2021 Frontier King Cab	6ft斗; 统一按最大高度	待终核: 2006-2020 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	待终核: 2022 King Cab最大高度复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先清最后几个缺口：1999 King Cab宽高、2003 Crew Cab LB宽高、gen2 King Cab 2006-2020、gen3 Crew Cab 6ft 2022/2023/2026。这些清完后再做连续区间压缩，准备输出完整可替换 TSV。

下一步


--- Round 9 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	值修改	1999 King Cab 已由 Edmunds 核到 196.1×71.9×68.6，本轮从待终核转为可入库。
Edmunds

Nissan Frontier	状态推进	2003 Crew Cab 6.0 仍只能从 KBB 确认 6 ft 长斗存在，KBB 给出 217.8 in 长度与 71.2 in 宽度，但未给可直接采用的整体高度，因此仍保留待终核。
Kbb.com

Nissan Frontier	值修改	2022 King Cab 已由 Edmunds 核到 210.2×73.0×72.1，本轮转为可入库。
Edmunds

Nissan Frontier	状态推进	gen2 King Cab 补入 2006 / 2020 参考：2006 Edmunds 为 205.5×72.8×69.7，2020 Edmunds 为 205.5×72.8×70.1，仍需补 2007-2019 中间年份。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际变化：1999 King Cab、2022 King Cab 转可入库；gen2 King Cab 参考车型从 2005/2021 扩展为 2005/2006/2020/2021。
🟡 待补强	gen1 只剩 2003 Crew Cab LB宽高。
🟡 待补强	gen2 只剩 King Cab 2007-2019 逐年确认。
🟡 待补强	gen3 只剩 Crew Cab 6ft 2022/2023/2026 终核。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	King Cab	6.0	205.5	72.8	70.1	2005/2006/2020/2021 Frontier King Cab	6ft斗; 统一按最大高度	待终核: 2007-2019 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先清 2003 Crew Cab LB高度、gen2 King Cab 2007-2019、gen3 Crew Cab 6ft 2022/2023/2026。清完这些后再做最终压缩，并输出完整可替换 TSV。

下一步


--- Round 10 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 状态推进	gen2 King Cab 从整段 2005-2021 拆出 2010 King Cab 单年；Edmunds 2010 King Cab 为 205.5×72.8×69.7，本轮转可入库。
Edmunds

Nissan Frontier	参考补强	gen3 Crew Cab 6.0 2026 补入 Edmunds 2026 SV 长斗页面，确认 2026 仍有 73.3 in bed 长斗 Crew Cab 口径，但外廓尺寸仍保留待终核。
Edmunds

Nissan Frontier	状态保持	2003 Crew Cab LB 仍只能确认 6ft 长斗存在，Edmunds 2003 Crew Cab 页面主要返回 56.3 in 短斗口径，长斗高度仍不能转可入库。
Edmunds
+1
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际变化：gen2 King Cab 拆出 2010 可入库，原待核范围缩小为 2007-2009/2011-2019。
🟡 待补强	gen1 剩余：2003 Crew Cab LB高度。
🟡 待补强	gen2 剩余：King Cab 2007-2009/2011-2019。
🟡 待补强	gen3 剩余：Crew Cab 6ft 2022/2023/2026。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2006	King Cab	6.0	205.5	72.8	70.1	2005/2006 Frontier King Cab	6ft斗; 统一按最大高度	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2007-2009	King Cab	6.0	205.5	72.8	70.1	2007-2009 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2007-2009 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010	King Cab	6.0	205.5	72.8	69.7	2010 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2011-2019	King Cab	6.0	205.5	72.8	70.1	2011-2019 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2011-2019 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2020-2021	King Cab	6.0	205.5	72.8	70.1	2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先清 gen2 King Cab 2007-2009/2011-2019，再处理 gen3 Crew Cab 6ft 2022/2023/2026，最后看 2003 Crew Cab LB高度 是否能用替代权威来源补齐。

5) 下一步


--- Round 11 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2011 已由 Edmunds 核到 205.5×72.8×69.7，本轮从待终核段中拆出并转可入库。
Edmunds

Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2012 已由 Edmunds 核到 205.5×72.8×69.7，本轮从待终核段中拆出并转可入库。
Edmunds

Nissan Frontier	状态推进	gen2 King Cab 2015-2016/2019 已补到 Edmunds King Cab 页面，但搜索摘要只稳定返回 bed/overview，三维外廓未完全显示，因此仍保留待终核，不强行可入库。
Edmunds
+2
Edmunds
+2

Nissan Frontier	状态修正	gen2 King Cab 待核范围从 2011-2019 缩小为 2013-2019；当前可入库段变为 2005-2006、2010-2012、2020-2021。
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际变化：2011 King Cab、2012 King Cab 转可入库，gen2 King Cab 待核范围继续缩小。
🟡 待补强	gen1 剩余：2003 Crew Cab LB高度。
🟡 待补强	gen2 剩余：King Cab 2007-2009 / 2013-2019。
🟡 待补强	gen3 剩余：Crew Cab 6ft 2022 / 2023 / 2026。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2006	King Cab	6.0	205.5	72.8	70.1	2005/2006 Frontier King Cab	6ft斗; 统一按最大高度	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2007-2009	King Cab	6.0	205.5	72.8	70.1	2007-2009 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2007-2009 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010-2012	King Cab	6.0	205.5	72.8	69.7	2010/2011/2012 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2013-2019	King Cab	6.0	205.5	72.8	70.1	2013-2019 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2013-2019 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2020-2021	King Cab	6.0	205.5	72.8	70.1	2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先处理 gen2 King Cab 2007-2009 / 2013-2019，再处理 gen3 Crew Cab 6ft 2022 / 2023 / 2026，最后单独处理 2003 Crew Cab LB高度。

下一步


--- Round 12 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2013 已核到 205.5×72.8×70.1，本轮从 2013-2019 待核段拆出并转可入库。
Edmunds

Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2017 已核到 205.5×72.8×68.7，本轮单独拆出并转可入库。
Edmunds

Nissan Frontier	范围缩小	gen2 King Cab 待核范围从 2013-2019 缩小为 2014-2016 / 2018-2019。
Nissan Frontier	状态保持	gen3 Crew Cab 6ft 2022 / 2023 / 2026 与 2003 Crew Cab LB高度 仍未完全清掉，继续保留待终核。
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际新增可入库：2013 King Cab、2017 King Cab。
🟡 待补强	gen1 剩余：2003 Crew Cab LB高度。
🟡 待补强	gen2 剩余：King Cab 2007-2009 / 2014-2016 / 2018-2019。
🟡 待补强	gen3 剩余：Crew Cab 6ft 2022 / 2023 / 2026。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2006	King Cab	6.0	205.5	72.8	70.1	2005/2006 Frontier King Cab	6ft斗; 统一按最大高度	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2007-2009	King Cab	6.0	205.5	72.8	70.1	2007-2009 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2007-2009 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010-2013	King Cab	6.0	205.5	72.8	70.1	2010/2011/2012/2013 Frontier King Cab	6ft斗; 2013高度按最大口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2014-2016	King Cab	6.0	205.5	72.8	70.1	2014-2016 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2014-2016 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2017	King Cab	6.0	205.5	72.8	68.7	2017 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2018-2019	King Cab	6.0	205.5	72.8	70.1	2018-2019 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2018-2019 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2020-2021	King Cab	6.0	205.5	72.8	70.1	2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先清 gen2 King Cab 2007-2009 / 2014-2016 / 2018-2019；如果能一次清掉，再继续处理 gen3 Crew Cab 6ft 2022 / 2023 / 2026 和 2003 Crew Cab LB高度。

下一步


--- Round 13 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2016 已核到 205.5×72.8×69.7，本轮从 2014-2016 待核段拆出并转可入库。
Edmunds

Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2018 已核到 205.5×72.8×70.1，本轮从 2018-2019 待核段拆出并转可入库。
Edmunds

Nissan Frontier	范围缩小	gen2 King Cab 待核范围从 2007-2009 / 2014-2016 / 2018-2019 缩小为 2007-2009 / 2014-2015 / 2019。
Nissan Frontier	状态保持	gen3 Crew Cab 6ft 2022 / 2023 / 2026 与 2003 Crew Cab LB高度 仍保留待终核。
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际新增可入库：2016 King Cab、2018 King Cab。
🟡 待补强	gen1 剩余：2003 Crew Cab LB高度。
🟡 待补强	gen2 剩余：King Cab 2007-2009 / 2014-2015 / 2019。
🟡 待补强	gen3 剩余：Crew Cab 6ft 2022 / 2023 / 2026。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2006	King Cab	6.0	205.5	72.8	70.1	2005/2006 Frontier King Cab	6ft斗; 统一按最大高度	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2007-2009	King Cab	6.0	205.5	72.8	70.1	2007-2009 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2007-2009 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010-2013	King Cab	6.0	205.5	72.8	70.1	2010/2011/2012/2013 Frontier King Cab	6ft斗; 2013高度按最大口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2014-2015	King Cab	6.0	205.5	72.8	70.1	2014/2015 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2014-2015 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2016	King Cab	6.0	205.5	72.8	69.7	2016 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2017	King Cab	6.0	205.5	72.8	68.7	2017 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2018	King Cab	6.0	205.5	72.8	70.1	2018 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2019	King Cab	6.0	205.5	72.8	70.1	2019 Frontier King Cab	6ft斗; 待终核	待终核: 2019 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2020-2021	King Cab	6.0	205.5	72.8	70.1	2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先清 gen2 King Cab 2007-2009 / 2014-2015 / 2019，然后处理 gen3 Crew Cab 6ft 2022 / 2023 / 2026，最后处理 2003 Crew Cab LB高度。

下一步


--- Round 14 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2009 已由 Edmunds LE King Cab 核到 205.5×72.8×69.7，本轮从 2007-2009 待核段拆出并转可入库。
Edmunds

Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2014 已补到 Edmunds King Cab 6.1 ft 页面；当前稳定确认 King Cab 73.3 in bed 与 205.5 in 外长口径，本轮单独拆出，但仍保留高度终核。
Edmunds
+1

Nissan Frontier	拆出 / 状态推进	gen2 King Cab 2019 已补到 Edmunds King Cab 页面，确认 King Cab 73.3 in bed；本轮单独拆出并更新参考车型，但仍保留高度终核。
Edmunds

Nissan Frontier	范围缩小	gen2 King Cab 待核范围从 2007-2009 / 2014-2015 / 2019 缩小为 2007-2008 / 2014-2015 / 2019高度终核。
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际新增可入库：2009 King Cab。
🟡 待补强	gen2 剩余：2007-2008 King Cab、2014-2015 King Cab高度、2019 King Cab高度。
🟡 待补强	gen3 剩余：Crew Cab 6ft 2022 / 2023 / 2026。
🟡 待补强	gen1 剩余：2003 Crew Cab LB高度。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2006	King Cab	6.0	205.5	72.8	70.1	2005/2006 Frontier King Cab	6ft斗; 统一按最大高度	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2007-2008	King Cab	6.0	205.5	72.8	70.1	2007/2008 Frontier King Cab	6ft斗; 待中间年份终核	待终核: 2007-2008 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2009	King Cab	6.0	205.5	72.8	69.7	2009 Frontier King Cab LE	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010-2013	King Cab	6.0	205.5	72.8	70.1	2010/2011/2012/2013 Frontier King Cab	6ft斗; 2013高度按最大口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2014	King Cab	6.0	205.5	72.8		2014 Frontier King Cab SV 6.1 ft	6ft斗	待终核: 2014 King Cab高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2015	King Cab	6.0	205.5	72.8		2015 Frontier King Cab	6ft斗	待终核: 2015 King Cab高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2016	King Cab	6.0	205.5	72.8	69.7	2016 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2017	King Cab	6.0	205.5	72.8	68.7	2017 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2018	King Cab	6.0	205.5	72.8	70.1	2018 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2019	King Cab	6.0	205.5	72.8		2019 Frontier King Cab	6ft斗	待终核: 2019 King Cab高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2020-2021	King Cab	6.0	205.5	72.8	70.1	2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab; 2025长轴选择扩展	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先清 2007-2008 King Cab、2014/2015/2019 King Cab高度，然后处理 gen3 Crew Cab 6ft 2022/2023/2026 和 2003 Crew Cab LB高度。

下一步


--- Round 15 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 状态推进	2008 King Cab 已由 Edmunds 核到 205.5×72.8×69.7，本轮从 2007-2008 待核段拆出并转可入库。
Edmunds

Nissan Frontier	值修改 / 状态推进	2014 King Cab 已由 Edmunds 核到 205.5×72.8×68.7，本轮补齐高度并转可入库。
Edmunds

Nissan Frontier	值修改 / 状态推进	2015 King Cab 已由 Edmunds 核到 205.5×72.8×68.7，本轮补齐高度并转可入库。
Edmunds

Nissan Frontier	范围缩小	gen2 King Cab 待核范围从 2007-2008 / 2014 / 2015 / 2019 缩小为 2007 / 2019。
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际新增可入库：2008 King Cab、2014 King Cab、2015 King Cab。
🟡 待补强	gen2 剩余：2007 King Cab、2019 King Cab高度。
🟡 待补强	gen3 剩余：Crew Cab 6ft 2022 / 2023 / 2026。
🟡 待补强	gen1 剩余：2003 Crew Cab LB高度。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2006	King Cab	6.0	205.5	72.8	70.1	2005/2006 Frontier King Cab	6ft斗; 统一按最大高度	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2007	King Cab	6.0	205.5	72.8	70.1	2007 Frontier King Cab	6ft斗	待终核: 2007 King Cab逐年确认
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2008	King Cab	6.0	205.5	72.8	69.7	2008 Frontier King Cab SE	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2009	King Cab	6.0	205.5	72.8	69.7	2009 Frontier King Cab LE	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010-2013	King Cab	6.0	205.5	72.8	70.1	2010/2011/2012/2013 Frontier King Cab	6ft斗; 2013高度按最大口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2014-2015	King Cab	6.0	205.5	72.8	68.7	2014/2015 Frontier King Cab SV/S	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2016	King Cab	6.0	205.5	72.8	69.7	2016 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2017	King Cab	6.0	205.5	72.8	68.7	2017 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2018	King Cab	6.0	205.5	72.8	70.1	2018 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2019	King Cab	6.0	205.5	72.8		2019 Frontier King Cab	6ft斗	待终核: 2019 King Cab高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2020-2021	King Cab	6.0	205.5	72.8	70.1	2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先清 2007 King Cab、2019 King Cab高度，然后处理 gen3 Crew Cab 6ft 2022/2023/2026，最后处理 2003 Crew Cab LB高度。

下一步


--- Round 16 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	值修改 / 状态推进	2007 King Cab 已由 Edmunds 核到 205.5×72.8×69.7，本轮从待终核转为可入库。
Edmunds

Nissan Frontier	值修改 / 状态推进	2019 King Cab 已由 Edmunds 核到 205.5×72.8×69.7，本轮补齐高度并转为可入库。
Edmunds

Nissan Frontier	压缩	gen2 King Cab 可入库段重新压缩：2005-2007、2008-2009、2010-2013、2014-2015、2016、2017、2018-2021。
Nissan Frontier	待核缩小	gen2 King Cab 已全部推进为可入库；剩余待核集中到 2003 Crew Cab LB高度 与 gen3 Crew Cab 6ft 2022/2023/2026。
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际新增可入库：2007 King Cab、2019 King Cab；gen2 King Cab 已清完。
🟡 待补强	gen1 剩余：2003 Crew Cab LB高度。
🟡 待补强	gen3 剩余：Crew Cab 6ft 2022 / 2023 / 2026。
🟡 当前状态	仍有待终核行，不能输出“本批次完成”。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2007	King Cab	6.0	205.5	72.8	70.1	2005/2006/2007 Frontier King Cab	6ft斗; 2005高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2008-2009	King Cab	6.0	205.5	72.8	69.7	2008/2009 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010-2013	King Cab	6.0	205.5	72.8	70.1	2010/2011/2012/2013 Frontier King Cab	6ft斗; 2013高度按最大口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2014-2015	King Cab	6.0	205.5	72.8	68.7	2014/2015 Frontier King Cab SV/S	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2016	King Cab	6.0	205.5	72.8	69.7	2016 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2017	King Cab	6.0	205.5	72.8	68.7	2017 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2018-2021	King Cab	6.0	205.5	72.8	70.1	2018/2019/2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab	待终核: 2022 Crew Cab 6ft宽高复核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	待终核: 2026 Crew Cab 6ft尺寸终核
4) 下一步优先核对

下一轮优先处理 gen3 Crew Cab 6ft 2022 / 2023 / 2026，然后处理最后一个 gen1 缺口 2003 Crew Cab LB高度。

下一步


--- Round 17 / 下一步 ---
1) 更新点
车型	操作	描述
Nissan Frontier	拆出 / 值修改	gen3 Crew Cab 6.0 2022 不再沿用短斗 PRO-4X 宽高；Edmunds 2022 Crew Cab 页面稳定返回短斗 210.2×74.7×72.9，长斗外长仍按 224.1，宽高保留最大口径但继续待终核。
Edmunds

Nissan Frontier	状态推进	2026 Crew Cab 6.0 参考补入 Edmunds 2026 Crew Cab 页面，确认 2026 Crew Cab 仍为当前代延续；长斗行继续保留 224.1×73.0×72.0，但仍需长斗具体页终核。
Edmunds

Nissan Frontier	状态保持	2003 Crew Cab LB 仍只由 KBB 确认 6 ft bed 存在；高度不能直接从短斗 Edmunds 页面套用，所以继续保留高度缺失。
Kbb.com

Nissan Frontier	状态压缩	gen2 King Cab 已完成可入库，未再保留 gen2 King Cab 待终核段。
2) 当前批次进度
状态	内容
🟢 已推进	本轮实际变化：2022 Crew Cab 6ft 备注与状态改为更准确的“长斗宽高待终核”，不再写成普通宽高复核；2026 Crew Cab 6ft 补入 2026 Crew Cab 参考。
🟡 待补强	剩余待核仅集中在：2003 Crew Cab LB高度、gen3 Crew Cab 6ft 2022 / 2023 / 2026。
🟡 当前状态	仍有待终核行，不能输出“本批次完成”。
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2		2003 Frontier Crew Cab LB	长斗Crew Cab; KBB确认6ft bed存在	待终核: 2003 Crew Cab LB高度
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2007	King Cab	6.0	205.5	72.8	70.1	2005/2006/2007 Frontier King Cab	6ft斗; 2005高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2008-2009	King Cab	6.0	205.5	72.8	69.7	2008/2009 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010-2013	King Cab	6.0	205.5	72.8	70.1	2010/2011/2012/2013 Frontier King Cab	6ft斗; 2013高度按最大口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2014-2015	King Cab	6.0	205.5	72.8	68.7	2014/2015 Frontier King Cab SV/S	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2016	King Cab	6.0	205.5	72.8	69.7	2016 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2017	King Cab	6.0	205.5	72.8	68.7	2017 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2018-2021	King Cab	6.0	205.5	72.8	70.1	2018/2019/2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	74.7	72.9	2022 Frontier Crew Cab 6 ft	长斗Crew Cab; 长斗宽高待终核	待终核: 2022 Crew Cab 6ft长斗宽高
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	待终核: 2023 Crew Cab 6ft尺寸终核
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	72.0	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab; 已确认Crew Cab延续，长斗外廓待终核	待终核: 2026 Crew Cab 6ft长斗外廓终核
4) 下一步优先核对

下一轮只剩两组：gen3 Crew Cab 6ft 2022 / 2023 / 2026，以及 2003 Crew Cab LB高度。优先用 Edmunds 具体 trim 页补 gen3 长斗，再用 KBB / Automobile-Catalog / Cars.com 查 2003 长斗高度。

下一步

--- Round 18 / 下一步 ---

主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	62.5	1998 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Regular Cab	6.0	191.3	66.5	62.8	2001 Frontier Regular Cab XE	单排后期口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	King Cab	6.0	203.1	71.9	65.9	2001 Frontier King Cab SC-V6	中期King Cab; 按SC-V6最大宽高	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	King Cab	6.0	202.9	67.7	63.2	2002 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	King Cab	6.0	202.9	67.7	66.7	2003 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	King Cab	6.0	202.9	67.7	63.2	2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE SB	初期Crew Cab短斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2001	Crew Cab	4.5	200.0	71.9	65.9	2001 Frontier Crew Cab SE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	4.5	199.9	71.2	74.0	2002 Frontier Crew Cab SC-V6 SB	短斗Crew Cab; 高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	4.5	199.9	71.2	69.9	2003 Frontier Crew Cab SC-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	4.5	199.9	71.2	66.7	2004 Frontier Crew Cab XE-V6 SB	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2002	Crew Cab	6.0	217.8	71.2	74.0	2002 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2003	Crew Cab	6.0	217.8	71.2	66.7	2003 Frontier Crew Cab XE-V6 4x2 LB / Motormatchup	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen1 compact pickup	2004	Crew Cab	6.0	217.8	71.2	74.0	2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2007	King Cab	6.0	205.5	72.8	70.1	2005/2006/2007 Frontier King Cab	6ft斗; 2005高车身口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2008-2009	King Cab	6.0	205.5	72.8	69.7	2008/2009 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2010-2013	King Cab	6.0	205.5	72.8	70.1	2010/2011/2012/2013 Frontier King Cab	6ft斗; 2013高度按最大口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2014-2015	King Cab	6.0	205.5	72.8	68.7	2014/2015 Frontier King Cab SV/S	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2016	King Cab	6.0	205.5	72.8	69.7	2016 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2017	King Cab	6.0	205.5	72.8	68.7	2017 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2018-2021	King Cab	6.0	205.5	72.8	70.1	2018/2019/2020/2021 Frontier King Cab	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	5.0	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	Crew Cab	6.0	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	King Cab	6.0	210.2	73.0	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	King Cab	6.0	210.2	73.0	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	King Cab	6.0	210.2	73.0	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	King Cab	6.0	210.2	73.0	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	King Cab	6.0	210.2	73.0	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew Cab	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew Cab	6.0	224.1	73.0	71.6	2022 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2023	Crew Cab	6.0	224.1	73.0	71.3	2023 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2024	Crew Cab	6.0	224.1	73.0	71.3	2024 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew Cab	6.0	224.1	73.0	72.0	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab	可入库
Nissan Frontier	Nissan	皮卡	Nissan Frontier	Pickup	Std.	gen3 midsize pickup	2026	Crew Cab	6.0	224.1	73.0	71.3	2026 Frontier Crew Cab SV 6.1 ft	长斗Crew Cab	可入库
