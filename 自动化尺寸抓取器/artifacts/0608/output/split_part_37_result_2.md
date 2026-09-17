# 文件名：split_part_37.tsv


--- Round 1 / 首次发送 ---
更新点：

当前批次主要为 Nissan Frontier 皮卡车型补强。

核对了年份范围和参考车型，发现部分 King Cab 和 Crew Cab 记录的参考车型年份存在不连续，需确认中间年份覆盖情况。

按当前 TSV 范围，不拆分年份区间外记录；保留现有代际/结构/版本。

维持版本、驾驶室类型和货斗长度不变。

当前批次更新后的完整 TSV（按要求字段顺序、保留现有记录、未扩展年份）：

主车型	分类	品牌	车型名	结构	版本	代际	年份区间	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	2004	extended	6.0 	202.9	67.7	63.2	2002 Frontier King Cab XE / 2004 Frontier King Cab XE	后期King Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen1 compact pickup	2004	crew	6.0 	217.8	71.2	74	2002 Frontier Crew Cab LB / 2004 Frontier Crew Cab LB	长斗Crew Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2005-2007	extended	6.0 	205.5	72.8	70.1	2005/2006/2007 Frontier King Cab / 2010/2011/2012/2013/2018/2019/2020/2021 Frontier King Cab	6ft斗; 2005高车身口径; 6ft斗; 2013高度按最大口径; 6ft斗	待终核: 确认 2010/2011/2012/2013/2018/2019/2020/2021 年参考车型
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	crew	5.0 	205.5	72.8	70.1	2005-2021 Frontier Crew Cab 5 ft	短斗Crew Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2005-2021	crew	6.0 	219.4	72.8	70.1	2005-2021 Frontier Crew Cab 6 ft	长斗Crew Cab	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2008-2009	extended	6.0 	205.5	72.8	69.7	2008/2009 Frontier King Cab	6ft斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2010-2013	extended	6.0 	205.5	72.8	70.1	2010/2011/2012/2013 Frontier King Cab	6ft斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2014-2015	extended	6.0 	205.5	72.8	68.7	2014/2015 Frontier King Cab SV/S	6ft斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2016	extended	6.0 	205.5	72.8	69.7	2016 Frontier King Cab	6ft斗	可入库
Nissan Frontier	皮卡	Nissan	Frontier	Pickup	Std.	gen2 midsize pickup	2017	extended	6.0 	205.5	72.8	68.7	2017 Frontier King Cab	6ft斗	可入库

本批次完成。

