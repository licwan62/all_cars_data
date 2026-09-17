# 文件名：split_part_35.tsv


--- Round 1 / 首次发送 ---
更新点

统一分类字段：皮卡车 → 皮卡。

统一驾驶室字段：crew/regular/extended → Crew Cab/Regular Cab/King Cab。

GMC Canyon 2023-2026：长度/宽度稳定为 213.2 / 72.4，2023-2024 AT4X 高度可到 81.6，因此本轮把 max_height_in 从 80.4 修正为 81.6。GMC 2023-2026 Crew Cab 短斗规格参考 Edmunds/KBB/Car and Driver 等来源。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Ineos Quartermaster：2025/2026 已核到 212.6 / 76.5 / 79.5，2024 美国市场年款仍未充分确认，因此 2024 单年改为待终核。
Edmunds
+1

Nissan Frontier：1998 Regular Cab 高度按可查 XE 规格修正为 66.1；2000 Crew Cab / King Cab 参考已补成明确年份车型。
Edmunds
+2
Edmunds
+2

当前批次进度
本轮已完成字段规范化与明显尺寸修正；仍有 Ineos Grenadier Quartermaster 2024 美国市场年款参考不足，需要下一轮继续终核。

本轮更新后的 TSV

tsv
GMC Canyon	皮卡	GMC	Canyon	Pickup	Std. inc: AT4X/Denali	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	72.4	81.6	2023/2024 Canyon AT4X; 2025/2026 Canyon Crew Cab AT4/Denali	含高车身版本; 2023-2024 AT4X拉高最大高度	可入库
Ineos Automotive Grenadier	皮卡	Ineos Automotive	Grenadier	Pickup	Quartermaster	gen1 off-road pickup	2024	Crew Cab	5.1	212.6	76.5	79.4	Grenadier Quartermaster	长车身皮卡; 2024美国市场年款需继续确认	待终核: 缺失2024美国市场年款参考
Ineos Automotive Grenadier	皮卡	Ineos Automotive	Grenadier	Pickup	Quartermaster	gen1 off-road pickup	2025-2026	Crew Cab	5.1	212.6	76.5	79.5	2025-2026 Ineos Grenadier Quartermaster	长车身皮卡	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	66.1	1998 Frontier Regular Cab XE	早期单排短车身; 按可查XE高度修正	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE/XE SB	初期Crew Cab短斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab XE	早期King Cab	可入库

下一步优先核对
优先继续核对 Ineos Grenadier Quartermaster 2024 是否存在美国市场正式年款及对应三维；若确认只是 2025 MY 起售，应在当前 split 内缩小或保留待终核说明。

下一步


--- Round 2 / 下一步 ---
更新点

本轮补强了 Ineos Automotive Grenadier Quartermaster 2024：Edmunds 有 2024 Grenadier Quartermaster 规格页，明确为 4dr Crew Cab 4WD SB，并给出 Length 212.6 / Width without mirrors 76.5 / Height 79.4 / Bed length 61.5 in，因此 2024 行由“待终核”改为“可入库”。
Edmunds

Ineos Automotive Grenadier Quartermaster 2025-2026 保持 2025-2026 拆分行：2025 为 212.6 / 76.5 / 79.5，2026 同为 212.6 / 76.5 / 79.5。
Edmunds
+1

统一参考车型写法：2024 行补成年份参考 2024 Ineos Grenadier Quartermaster Fieldmaster 4dr Crew Cab 4WD SB，不再只写无年份车型名。

当前批次进度
当前 split_part_35 范围内 10 条记录已完成本轮可入库判断；未新增当前 TSV 范围外车型、代际、结构、版本或年份。

本轮更新后的 TSV

tsv
GMC Canyon	皮卡	GMC	Canyon	Pickup	Std. inc: AT4X/Denali	gen3 midsize pickup	2023-2026	Crew Cab	5.0	213.2	72.4	81.6	2023/2024 Canyon AT4X; 2025/2026 Canyon Crew Cab AT4/Denali	含高车身版本; 2023-2024 AT4X拉高最大高度	可入库
Ineos Automotive Grenadier	皮卡	Ineos Automotive	Grenadier	Pickup	Quartermaster	gen1 off-road pickup	2024	Crew Cab	5.1	212.6	76.5	79.4	2024 Ineos Grenadier Quartermaster Fieldmaster 4dr Crew Cab 4WD SB	长车身皮卡; 2024高度低于2025-2026	可入库
Ineos Automotive Grenadier	皮卡	Ineos Automotive	Grenadier	Pickup	Quartermaster	gen1 off-road pickup	2025-2026	Crew Cab	5.1	212.6	76.5	79.5	2025-2026 Ineos Grenadier Quartermaster	长车身皮卡	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	1998	Regular Cab	6.0	184.3	66.5	66.1	1998 Frontier Regular Cab XE	早期单排短车身; 按可查XE高度修正	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	1998	King Cab	6.0	196.1	66.5	62.8	1998 Frontier King Cab	早期King Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	1999	Regular Cab	6.0	184.3	71.9	66.1	1999 Frontier Regular Cab XE	早期单排短车身; 4WD宽高更大	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	1999	King Cab	6.0	196.1	71.9	68.6	1999 Frontier King Cab XE 4WD	早期King Cab; 4WD宽高更大	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	2000	Regular Cab	6.0	184.3	66.5	62.8	2000 Frontier Regular Cab	早期单排短车身	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	2000	Crew Cab	4.5	193.1	71.9	65.9	2000 Frontier Crew Cab SE/XE SB	初期Crew Cab短斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	2000	King Cab	6.0	196.1	66.5	62.6	2000 Frontier King Cab XE	早期King Cab	可入库

下一步优先核对
无，当前批次记录均已给出具体参考车型与可入库状态。

本批次完成。

