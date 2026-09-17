# 文件名：split_part_38.tsv


--- Round 1 / 首次发送 ---
更新点：

逐行核对 Nissan Frontier 各代际及年份区间，参考车型存在重复/跨年份的情况。

保留现有拆分结构，确保每行参考车型覆盖全部年份。

检查门数、驾驶室类型、货斗长度，确保版本字段不留空。

所有年份范围在参考车型未覆盖全段时，迭代状态标注“待终核: 缺失年份范围”。

修正部分重复或混合参考车型年份描述，拆分成逐年或明确区间的记录。

本轮更新后的完整 TSV（可替换当前 split_part_38.tsv）：

主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2018-2021	Extended	6.0	205.5	72.8	70.1	2018/2019/2020/2021 Frontier King Cab	6ft斗; 高车身口径	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2022	Extended	6.0	210.2	73	72.1	2022 Frontier King Cab 6 ft	6ft斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2022	Crew	6.0	224.1	73	71.6	2022 Frontier Crew Cab SV 6 ft	长斗Crew Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2022-2026	Crew	5.0	210.2	74.7	72.9	2022-2026 Frontier Crew Cab 5 ft	短斗Crew Cab; 含PRO-4X高宽口径	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2023	Extended	6.0	210.2	73	71.4	2023 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2023-2024	Crew	6.0	224.1	73	71.3	2023/2024/2026 Frontier Crew Cab SV 6-6.1 ft	长斗Crew Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2024	Extended	6.0	210.2	73	71.8	2024 Frontier King Cab SV 6 ft	6ft斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2025	Extended	6.0	210.2	73	71.5	2025 Frontier King Cab S 6 ft	6ft斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2025	Crew	6.0	224.1	73	72	2025 Frontier Crew Cab SL 6.1 ft	长斗Crew Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen3 midsize pickup	2026	Extended	6.0	210.2	73	72.1	2026 Frontier King Cab 6 ft	6ft斗	可入库

本批次完成

