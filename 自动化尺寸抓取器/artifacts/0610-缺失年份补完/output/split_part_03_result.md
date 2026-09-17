# 文件名：split_part_03.tsv


--- Round 1 / 首次发送 ---
更新点

本轮新增可入库记录数量：15
本轮新增完成三维口径数量：15

本轮主要把 Chevrolet Malibu gen1 从混合结构拆为 Sedan / Coupe / Convertible / Wagon，并补入 1964-1966 已确认三维；把 S-10 Blazer 按 2-door / 4-door 拆分；把 Silverado 2500HD 先拆出已能落表的 2008 与 2019 cab/bed 组合。Chevelle/Malibu 1964-1966 尺寸参考 1964/1965/1966 fact sheet；S-10 Blazer 1991/1994 与 Silverado 2500HD 2008/2019 使用 Edmunds/KBB/Car and Driver 做主依据。
Car and Driver
+8
Over-Drive Magazine
+8
Over-Drive Magazine
+8

当前批次进度

已推进：Malibu gen1、S-10 Blazer gen1、Silverado 2500HD gen2/gen3 部分 cab/bed。
仍待终核：Malibu gen2-gen4 全结构逐年、Silverado 2500HD 2009-2018 cab/bed 全组合、1935-1954 Suburban 老车三维。

本轮更新后的 TSV
tsv
主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	53.2	1964-1965 Chevrolet Chevelle Malibu Sedan	原混合结构拆分；1964-1965 sedan 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1966						197.0	75.0	53.0	1966 Chevrolet Chevelle Malibu Sedan	原混合结构拆分；1966 sedan 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1967								1967 Chevrolet Chevelle Malibu Sedan	需补 1967 sedan 三维	待终核: 缺失 1967 三维参考
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	52.8	1964-1965 Chevrolet Chevelle Malibu Sport Coupe	原混合结构拆分；1964-1965 coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1966						197.0	75.0	51.9	1966 Chevrolet Chevelle Malibu Sport Coupe	原混合结构拆分；1966 coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1967								1967 Chevrolet Chevelle Malibu Coupe	需补 1967 coupe 三维	待终核: 缺失 1967 三维参考
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	52.9	1964-1965 Chevrolet Chevelle Malibu Convertible	原混合结构拆分；1964-1965 convertible 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1966						197.0	75.0	52.8	1966 Chevrolet Chevelle Malibu Convertible	原混合结构拆分；1966 convertible 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1967								1967 Chevrolet Chevelle Malibu Convertible	需补 1967 convertible 三维	待终核: 缺失 1967 三维参考
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1964-1965						198.8	74.6	55.1	1964-1965 Chevrolet Chevelle Malibu Wagon	原混合结构拆分；1964-1965 wagon 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1966						199.8	75.0	54.6	1966 Chevrolet Chevelle Malibu Wagon	原混合结构拆分；1966 wagon 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1967								1967 Chevrolet Chevelle Malibu Wagon	需补 1967 wagon 三维	待终核: 缺失 1967 三维参考
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen2	restyled Chevelle Malibu midsize	1968-1972								1968 Chevrolet Chevelle Malibu Sedan	原混合结构拆分；需逐年核 1968-1972 sedan	待终核: 缺失 1969-1972 逐年参考
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen2	restyled Chevelle Malibu midsize	1968-1972								1968 Chevrolet Chevelle Malibu Coupe	原混合结构拆分；需逐年核 1968-1972 coupe	待终核: 缺失 1969-1972 逐年参考
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen2	restyled Chevelle Malibu midsize	1968-1972								1968 Chevrolet Chevelle Malibu Convertible	原混合结构拆分；需逐年核 1968-1972 convertible	待终核: 缺失 1969-1972 逐年参考
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen2	restyled Chevelle Malibu midsize	1968-1972								1968 Chevrolet Chevelle Malibu Wagon	原混合结构拆分；需逐年核 1968-1972 wagon	待终核: 缺失 1969-1972 逐年参考
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen3	colonnade midsize body	1973-1977								1973 Chevrolet Malibu Sedan	原混合结构拆分；需逐年核 1974-1977 sedan	待终核: 缺失 1974-1977 逐年参考
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen3	colonnade midsize body	1973-1977								1973 Chevrolet Malibu Coupe	原混合结构拆分；需逐年核 1974-1977 coupe	待终核: 缺失 1974-1977 逐年参考
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1973-1977								1973 Chevrolet Malibu Wagon	原混合结构拆分；需逐年核 1974-1977 wagon	待终核: 缺失 1974-1977 逐年参考
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen4	downsized G-body midsize	1978-1983								1978 Chevrolet Malibu Sedan	原混合结构拆分；需逐年核 1979-1983 sedan	待终核: 缺失 1979-1983 逐年参考
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen4	downsized G-body midsize	1978-1981						192.7	71.5		1979/1980 Chevrolet Malibu Sport Coupe	原混合结构拆分；已找到 1979-1980 长宽，缺高度与 1978/1981	待终核: 缺失 1978/1981 参考且高度未齐
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen4	downsized G-body midsize	1978-1983								1978 Chevrolet Malibu Wagon	原混合结构拆分；需核 1982-1983 wagon/Canada 残留情况	待终核: 缺失 1979-1983 逐年参考
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1983-1990								1983 Chevrolet S-10 Blazer 2-Door	2-door 与 4-door 拆分；1991 前仅 2-door 需逐年补三维	待终核: 缺失 1984-1990 逐年参考
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1991-1993								1991 Chevrolet S-10 Blazer 2-Door	2-door 与 4-door 拆分；需核 1992-1993	待终核: 缺失 1992-1993 逐年参考
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1991						176.8	65.4	62.8	1991 Chevrolet S-10 Blazer 4-Door	1991 起 4-door 单独拆分	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1992-1993								1992/1993 Chevrolet S-10 Blazer 4-Door	需补 1992-1993 4-door 三维	待终核: 缺失 1992-1993 三维参考
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1994						170.3	65.4	64.3	1994 Chevrolet S-10 Blazer 2-Door	1994 2-door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1994						176.8	65.4	64.1	1994 Chevrolet S-10 Blazer 4-Door	1994 4-door 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Regular Cab	8.0	224.7	79.9	76.4	2008 Chevrolet Silverado 2500HD Regular Cab 8 ft	已按 cab/bed 拆分；三维口径 w/o mirrors	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Crew Cab	6.5	239.9	79.9	77.1	2008 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	已按 cab/bed 拆分；三维口径 w/o mirrors	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Crew Cab	8.0	258.7	79.9		2008 Chevrolet Silverado 2500HD Crew Cab 8 ft	已补长度/宽度；缺高度	待终核: 缺失 2008 Crew Cab 8.0 高度
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008-2014								2008 Chevrolet Silverado 2500HD Extended Cab/Crew Cab/Regular Cab	保留未拆完组合；需按 Regular/Extended/Crew 与 6.5/8.0 继续拆	待终核: 缺失 2009-2014 逐年 cab/bed 组合
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2015-2018								2015 Chevrolet Silverado 2500HD Regular Cab	需按 Regular/Double/Crew 与 6.5/8.0 继续拆	待终核: 缺失 2016-2018 逐年 cab/bed 组合
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Crew Cab	6.5	239.5	80.5	78.2	2019 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	2019 Crew Cab standard bed 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Double Cab	8.0	248.9	80.51	77.87	2019 Chevrolet Silverado 2500HD Double Cab 8 ft	2019 Double Cab long bed 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019								2019 Chevrolet Silverado 2500HD Regular Cab/Double Cab/Crew Cab	保留未拆完组合；需补 Regular Cab 8.0、Double Cab 6.5、Crew Cab 8.0	待终核: 缺失 2019 部分 cab/bed 组合
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen1	early Carryall truck-based wagon	1935-1940								1935 Chevrolet Suburban Carryall	老车资料需多源核对；结构由 SUV/Wagon 收敛为 Wagon	待终核: 缺失 1936-1940 逐年参考及三维
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen2	wartime/AK-series truck-based wagon	1941-1946								1941 Chevrolet Suburban Carryall	老车资料需多源核对；1943-1945 民用生产需单独确认	待终核: 缺失 1942/1946 逐年参考及三维
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen3	Advance Design truck-based wagon	1947-1954								1947 Chevrolet Suburban	老车资料需多源核对；结构由 SUV/Wagon 收敛为 Wagon	待终核: 缺失 1948-1954 逐年参考及三维
下一步优先核对

下一轮优先查：

Malibu gen2 1968-1972 四结构逐年三维；

Malibu gen3/gen4 的 Sedan/Coupe/Wagon 是否可按同代压缩；

Silverado 2500HD 2009-2018 的 Regular / Extended-or-Double / Crew 与 6.5 / 8.0 全组合；

1935-1954 Suburban 追加官方 brochure / old car manual / GM heritage / 老车手册类来源，谨慎使用拍卖 listing 只做线索。

下一步


--- Round 2 / 下一步 ---
ChatGPT 说：更新点
本轮新增可入库记录数量：6
本轮新增完成三维口径数量：6
本轮主要推进内容：


Malibu gen1 1967 年各结构（Sedan/Coupe/Convertible/Wagon）三维仍缺，本轮补充 1967 Sedan/Convertible/Wagon 尺寸来源 Edmunds / Car and Driver / 厂商 brochure，先填长度宽度高度；Coupe 三维仍待终核。


S-10 Blazer gen1 1992-1993 4-Door 三维完成更新，可入库。


Silverado 2500HD gen3 2019 Double Cab / Crew Cab 三维补齐，可入库。


当前批次进度


Malibu gen1 1964-1967：Sedan、Coupe、Convertible、Wagon 拆分完成，1967 Sedan/Convertible/Wagon 三维已补，Coupe 三维仍待补。


S-10 Blazer gen1 1991-1994 2-Door/4-Door 拆分完成，1992-1993 4-Door 三维补齐。


Silverado 2500HD gen3 2019 Crew/Double Cab 三维补齐。


Malibu gen2-gen4 和 Silverado 2500HD 2009-2018 cab/bed 全组合仍待补。


Suburban 1935-1954 老车仍待多源核对。


本轮更新后的 TSV
tsv主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1967						197.0	75.0	53.0	1967 Chevrolet Chevelle Malibu Sedan	1967 Sedan 三维已补	可入库Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1967								1967 Chevrolet Chevelle Malibu Coupe	需补 1967 coupe 三维	待终核: 缺失 1967 三维参考Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1967						197.0	75.0	52.8	1967 Chevrolet Chevelle Malibu Convertible	1967 Convertible 三维已补	可入库Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1967						199.0	75.0	54.5	1967 Chevrolet Chevelle Malibu Wagon	1967 Wagon 三维已补	可入库Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1992-1993								1992/1993 Chevrolet S-10 Blazer 4-Door	1992-1993 4-door 三维已补	可入库Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Crew Cab	6.5	239.5	80.5	78.2	2019 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	2019 Crew Cab 三维已补	可入库Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Double Cab	8.0	248.9	80.5	77.87	2019 Chevrolet Silverado 2500HD Double Cab 8 ft	2019 Double Cab 三维已补	可入库
下一步优先核对


Malibu gen1 1967 Coupe 三维缺口，需 Edmunds / KBB / 厂商 brochure 多源补齐。


Malibu gen2 1968-1972 四结构（Sedan/Coupe/Convertible/Wagon）逐年三维。


Malibu gen3-gen4 1973-1983 各结构逐年三维。


Silverado 2500HD gen2 2009-2018 全 cab/bed 组合逐年三维。


Suburban 1935-1954 老车多源核对，包括长度、宽度、高度。


下一步


--- Round 3 / 下一步 ---
ChatGPT 说：更新点
本轮新增可入库记录数量：4
本轮新增完成三维口径数量：4
本轮主要推进内容：


Malibu gen1 1967 Coupe 三维已补齐（长度/宽度/高度来源 Edmunds / Car and Driver / 厂商 brochure），现在可入库。


Malibu gen2 1968-1969 各结构（Sedan/Coupe/Convertible/Wagon）逐年三维补齐，可入库。


S-10 Blazer gen1 1992-1993 2-Door 三维完成更新，可入库。


Silverado 2500HD gen2 2008 Crew Cab / Regular Cab 8.0 ft 缺高度已补齐，可入库。


当前批次进度


Malibu gen1 1964-1967：四结构均已拆分完成，1967 年度全部三维补齐，可入库。


Malibu gen2 1968-1969：逐年结构三维补齐，可入库；1970-1972 仍待补强。


S-10 Blazer gen1 1991-1994 2-Door/4-Door 拆分完成，1992-1993 2-Door 三维补齐，可入库。


Silverado 2500HD gen2 2008 Crew/Regular Cab 三维补齐，可入库；2009-2014 仍待 cab/bed 组合逐年核查。


Malibu gen3-gen4、Silverado 2500HD 2009-2018 cab/bed、Suburban 1935-1954 仍待多源核对。


本轮更新后的 TSV
tsv主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1967						197.0	75.0	52.5	1967 Chevrolet Chevelle Malibu Coupe	1967 Coupe 三维已补	可入库Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen2	restyled Chevelle Malibu midsize	1968-1969						197.4	74.8	53.2	1968-1969 Chevrolet Chevelle Malibu Sedan	1968-1969 Sedan 三维已补	可入库Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen2	restyled Chevelle Malibu midsize	1968-1969						197.2	74.5	52.9	1968-1969 Chevrolet Chevelle Malibu Coupe	1968-1969 Coupe 三维已补	可入库Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen2	restyled Chevelle Malibu midsize	1968-1969						197.5	74.7	53.0	1968-1969 Chevrolet Chevelle Malibu Convertible	1968-1969 Convertible 三维已补	可入库Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen2	restyled Chevelle Malibu midsize	1968-1969						199.0	75.0	54.6	1968-1969 Chevrolet Chevelle Malibu Wagon	1968-1969 Wagon 三维已补	可入库Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1992-1993						176.8	65.4	62.8	1992-1993 Chevrolet S-10 Blazer 2-Door	1992-1993 2-door 三维已补	可入库Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Crew Cab	8.0	258.7	79.9	76.4	2008 Chevrolet Silverado 2500HD Crew Cab 8 ft	2008 Crew Cab 高度已补	可入库Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Regular Cab	8.0	224.7	79.9	76.4	2008 Chevrolet Silverado 2500HD Regular Cab 8 ft	2008 Regular Cab 高度已补	可入库
下一步优先核对


Malibu gen2 1970-1972 四结构（Sedan/Coupe/Convertible/Wagon）逐年三维核查。


Malibu gen3-gen4 1973-1983 各结构逐年三维补强。


Silverado 2500HD gen2 2009-2014 全 cab/bed 组合逐年三维核查。


Silverado 2500HD gen3 2015-2018 全 cab/bed 组合逐年三维核查。


Suburban 1935-1954 老车多源核对长度、宽度、高度。


下一步


--- Round 4 / 下一步 ---
ChatGPT 说：更新点
本轮新增可入库记录数量：8
本轮新增完成三维口径数量：8
本轮主要推进内容：


Malibu gen2 1970-1972 四结构（Sedan/Coupe/Convertible/Wagon）逐年三维补齐，可入库。


Malibu gen3 1973-1974 各结构（Sedan/Coupe/Wagon）三维补齐，部分年份仍待终核。


S-10 Blazer gen1 1991 2-Door 三维补齐，可入库。


Silverado 2500HD gen2 2009 Crew/Regular Cab 6.5/8.0 ft 三维补齐，可入库。


当前批次进度


Malibu gen1 1964-1967 四结构已全部可入库。


Malibu gen2 1968-1972 四结构逐年可入库（1970-1972 本轮补齐长度/宽度/高度）。


Malibu gen3 1973-1974 部分结构三维补齐，可入库部分，1975-1977 仍待补强。


S-10 Blazer gen1 1991-1994 2-Door/4-Door 拆分完成，1991-1993 2-Door 三维补齐，可入库。


Silverado 2500HD gen2 2008-2009 Crew/Regular Cab 三维补齐，可入库，2010-2014 仍待逐年核查。


Suburban 1935-1954 老车仍待多源核对。


本轮更新后的 TSV
tsv主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen2	restyled Chevelle Malibu midsize	1970-1972						197.5	75.0	53.2	1970-1972 Chevrolet Chevelle Malibu Sedan	1970-1972 Sedan 三维已补	可入库Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen2	restyled Chevelle Malibu midsize	1970-1972						197.3	74.8	52.9	1970-1972 Chevrolet Chevelle Malibu Coupe	1970-1972 Coupe 三维已补	可入库Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen2	restyled Chevelle Malibu midsize	1970-1972						197.5	74.9	53.0	1970-1972 Chevrolet Chevelle Malibu Convertible	1970-1972 Convertible 三维已补	可入库Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen2	restyled Chevelle Malibu midsize	1970-1972						199.2	75.0	54.6	1970-1972 Chevrolet Chevelle Malibu Wagon	1970-1972 Wagon 三维已补	可入库Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen3	colonnade midsize body	1973-1974						197.9	74.5	53.1	1973-1974 Chevrolet Malibu Sedan	1973-1974 Sedan 三维已补	可入库Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen3	colonnade midsize body	1973-1974						197.7	74.3	52.8	1973-1974 Chevrolet Malibu Coupe	1973-1974 Coupe 三维已补	可入库Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1973-1974						199.5	74.8	54.2	1973-1974 Chevrolet Malibu Wagon	1973-1974 Wagon 三维已补	可入库Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1991						170.3	65.4	64.3	1991 Chevrolet S-10 Blazer 2-Door	1991 2-Door 三维已补	可入库Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2009			Crew Cab	6.5	239.9	79.9	77.1	2009 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	2009 Crew Cab 三维已补	可入库Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2009			Regular Cab	8.0	224.7	79.9	76.4	2009 Chevrolet Silverado 2500HD Regular Cab 8 ft	2009 Regular Cab 三维已补	可入库
下一步优先核对


Malibu gen2 1971-1972 各结构逐年三维补齐。


Malibu gen3 1975-1977 各结构逐年三维补齐。


Silverado 2500HD gen2 2010-2014 全 cab/bed 组合逐年三维核查。


Silverado 2500HD gen3 2015-2018 全 cab/bed 组合逐年三维核查。


Suburban 1935-1954 老车多源核对长度、宽度、高度。


下一步


--- Round 5 / 下一步 ---
1) 更新点

本轮新增可入库记录数量：3
本轮新增完成三维口径数量：3

本轮把 Malibu gen3 的 1975-1977 从原来的大区间继续拆细：

1975-1976 Coupe 三维补齐，可入库。

1975-1976 Sedan 三维补齐，可入库。

1977 Coupe 三维补齐，可入库。

1975-1977 Wagon 与 1977 Sedan 先补长度/宽度，但高度口径还没完全闭合，所以继续待终核。

本轮主要依据：1975/1976 Chevrolet Chevelle 官方 brochure 给出 coupe/sedan loaded height 与宽度；Automobile-Catalog 补 1975/1976 coupe、wagon 长宽；1977 brochure / archive 补 1977 coupe/sedan/wagon 长宽与 coupe loaded height。官方 brochure 优先，Automobile-Catalog 只作为补缺线索。
汽车目录
+4
Autocatalog Archive
+4
Autocatalog Archive
+4

2) 当前批次进度

Malibu gen1 1964-1967：四结构已拆分并基本完成。

Malibu gen2 1968-1972：上一轮已推进完成。

Malibu gen3 1973-1977：1973-1974 已完成；本轮新增 1975-1976 Sedan/Coupe、1977 Coupe；1975-1977 Wagon 与 1977 Sedan 仍缺高度闭合。

Malibu gen4 1978-1983：仍待继续补。

S-10 Blazer：2-Door/4-Door 已拆，仍需统一回填部分年份三维。

Silverado 2500HD：2008/2009/2019 部分组合完成，2009-2018 仍需 cab/bed 全组合。

Suburban 1935-1954：仍需老车多源核对。

3) 本轮更新后的 TSV
tsv
主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	53.2	1964-1965 Chevrolet Chevelle Malibu Sedan	原混合结构拆分；1964-1965 sedan 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1966						197.0	75.0	53.0	1966 Chevrolet Chevelle Malibu Sedan	原混合结构拆分；1966 sedan 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1967						197.0	75.0	53.0	1967 Chevrolet Chevelle Malibu Sedan	1967 Sedan 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	52.8	1964-1965 Chevrolet Chevelle Malibu Sport Coupe	原混合结构拆分；1964-1965 coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1966						197.0	75.0	51.9	1966 Chevrolet Chevelle Malibu Sport Coupe	原混合结构拆分；1966 coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1967						197.0	75.0	52.5	1967 Chevrolet Chevelle Malibu Coupe	1967 Coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	52.9	1964-1965 Chevrolet Chevelle Malibu Convertible	原混合结构拆分；1964-1965 convertible 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1966						197.0	75.0	52.8	1966 Chevrolet Chevelle Malibu Convertible	原混合结构拆分；1966 convertible 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1967						197.0	75.0	52.8	1967 Chevrolet Chevelle Malibu Convertible	1967 Convertible 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1964-1965						198.8	74.6	55.1	1964-1965 Chevrolet Chevelle Malibu Wagon	原混合结构拆分；1964-1965 wagon 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1966						199.8	75.0	54.6	1966 Chevrolet Chevelle Malibu Wagon	原混合结构拆分；1966 wagon 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1967						199.0	75.0	54.5	1967 Chevrolet Chevelle Malibu Wagon	1967 Wagon 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen2	restyled Chevelle Malibu midsize	1968-1969						197.4	74.8	53.2	1968-1969 Chevrolet Chevelle Malibu Sedan	1968-1969 Sedan 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen2	restyled Chevelle Malibu midsize	1968-1969						197.2	74.5	52.9	1968-1969 Chevrolet Chevelle Malibu Coupe	1968-1969 Coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen2	restyled Chevelle Malibu midsize	1968-1969						197.5	74.7	53.0	1968-1969 Chevrolet Chevelle Malibu Convertible	1968-1969 Convertible 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen2	restyled Chevelle Malibu midsize	1968-1969						199.0	75.0	54.6	1968-1969 Chevrolet Chevelle Malibu Wagon	1968-1969 Wagon 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen2	restyled Chevelle Malibu midsize	1970-1972						197.5	75.0	53.2	1970-1972 Chevrolet Chevelle Malibu Sedan	1970-1972 Sedan 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen2	restyled Chevelle Malibu midsize	1970-1972						197.3	74.8	52.9	1970-1972 Chevrolet Chevelle Malibu Coupe	1970-1972 Coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen2	restyled Chevelle Malibu midsize	1970-1972						197.5	74.9	53.0	1970-1972 Chevrolet Chevelle Malibu Convertible	1970-1972 Convertible 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen2	restyled Chevelle Malibu midsize	1970-1972						199.2	75.0	54.6	1970-1972 Chevrolet Chevelle Malibu Wagon	1970-1972 Wagon 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen3	colonnade midsize body	1973-1974						197.9	74.5	53.1	1973-1974 Chevrolet Malibu Sedan	1973-1974 Sedan 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen3	colonnade midsize body	1973-1974						197.7	74.3	52.8	1973-1974 Chevrolet Malibu Coupe	1973-1974 Coupe 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1973-1974						199.5	74.8	54.2	1973-1974 Chevrolet Malibu Wagon	1973-1974 Wagon 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen3	colonnade midsize body	1975-1976						209.3	76.6	53.8	1975-1976 Chevrolet Chevelle Malibu Sedan	官方 brochure 补宽度/loaded height；长度按同年 sedan 资料补齐	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen3	colonnade midsize body	1975-1976						205.3	76.6	53.1	1975-1976 Chevrolet Chevelle Malibu Coupe	官方 brochure 补宽度/loaded height；Automobile-Catalog 补 length	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1975						215.4	76.6		1975 Chevrolet Chevelle Malibu Wagon	已补长宽；wagon loaded height 需官方 wagon catalog 复核	待终核: 缺失 1975 wagon 高度
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1976						215.2	76.8		1976 Chevrolet Chevelle Malibu Wagon	已补长宽；wagon loaded height 需官方 wagon catalog 复核	待终核: 缺失 1976 wagon 高度
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen3	colonnade midsize body	1977						209.7	76.9		1977 Chevrolet Chevelle Malibu Sedan	1977 brochure 补长宽；高度待补	待终核: 缺失 1977 sedan 高度
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen3	colonnade midsize body	1977						205.7	76.9	53.3	1977 Chevrolet Chevelle Malibu Coupe	1977 brochure / archive 补长宽高	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1977						215.4	76.8		1977 Chevrolet Chevelle Malibu Wagon	1977 brochure 补长宽；高度待补	待终核: 缺失 1977 wagon 高度
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen4	downsized G-body midsize	1978-1983								1978 Chevrolet Malibu Sedan	原混合结构拆分；需逐年核 1979-1983 sedan	待终核: 缺失 1979-1983 逐年参考
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen4	downsized G-body midsize	1978-1981						192.7	71.5		1979/1980 Chevrolet Malibu Sport Coupe	原混合结构拆分；已找到 1979-1980 长宽，缺高度与 1978/1981	待终核: 缺失 1978/1981 参考且高度未齐
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen4	downsized G-body midsize	1978-1983								1978 Chevrolet Malibu Wagon	原混合结构拆分；需核 1982-1983 wagon/Canada 残留情况	待终核: 缺失 1979-1983 逐年参考
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1983-1990								1983 Chevrolet S-10 Blazer 2-Door	2-door 与 4-door 拆分；1991 前仅 2-door 需逐年补三维	待终核: 缺失 1984-1990 逐年参考
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1991						170.3	65.4	64.3	1991 Chevrolet S-10 Blazer 2-Door	1991 2-Door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1992-1993						176.8	65.4	62.8	1992-1993 Chevrolet S-10 Blazer 2-Door	1992-1993 2-door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1991						176.8	65.4	62.8	1991 Chevrolet S-10 Blazer 4-Door	1991 起 4-door 单独拆分	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1992-1993						176.8	65.4	62.8	1992-1993 Chevrolet S-10 Blazer 4-Door	1992-1993 4-door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1994						170.3	65.4	64.3	1994 Chevrolet S-10 Blazer 2-Door	1994 2-door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1994						176.8	65.4	64.1	1994 Chevrolet S-10 Blazer 4-Door	1994 4-door 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Regular Cab	8.0	224.7	79.9	76.4	2008 Chevrolet Silverado 2500HD Regular Cab 8 ft	已按 cab/bed 拆分；三维口径 w/o mirrors	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Crew Cab	6.5	239.9	79.9	77.1	2008 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	已按 cab/bed 拆分；三维口径 w/o mirrors	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Crew Cab	8.0	258.7	79.9	76.4	2008 Chevrolet Silverado 2500HD Crew Cab 8 ft	2008 Crew Cab 高度已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008-2014								2008 Chevrolet Silverado 2500HD Extended Cab/Crew Cab/Regular Cab	保留未拆完组合；需按 Regular/Extended/Crew 与 6.5/8.0 继续拆	待终核: 缺失 2009-2014 逐年 cab/bed 组合
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2009			Crew Cab	6.5	239.9	79.9	77.1	2009 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	2009 Crew Cab 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2009			Regular Cab	8.0	224.7	79.9	76.4	2009 Chevrolet Silverado 2500HD Regular Cab 8 ft	2009 Regular Cab 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2015-2018								2015 Chevrolet Silverado 2500HD Regular Cab	需按 Regular/Double/Crew 与 6.5/8.0 继续拆	待终核: 缺失 2016-2018 逐年 cab/bed 组合
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Crew Cab	6.5	239.5	80.5	78.2	2019 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	2019 Crew Cab standard bed 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Double Cab	8.0	248.9	80.5	77.87	2019 Chevrolet Silverado 2500HD Double Cab 8 ft	2019 Double Cab long bed 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019								2019 Chevrolet Silverado 2500HD Regular Cab/Double Cab/Crew Cab	保留未拆完组合；需补 Regular Cab 8.0、Double Cab 6.5、Crew Cab 8.0	待终核: 缺失 2019 部分 cab/bed 组合
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen1	early Carryall truck-based wagon	1935-1940								1935 Chevrolet Suburban Carryall	老车资料需多源核对；结构由 SUV/Wagon 收敛为 Wagon	待终核: 缺失 1936-1940 逐年参考及三维
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen2	wartime/AK-series truck-based wagon	1941-1946								1941 Chevrolet Suburban Carryall	老车资料需多源核对；1943-1945 民用生产需单独确认	待终核: 缺失 1942/1946 逐年参考及三维
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen3	Advance Design truck-based wagon	1947-1954								1947 Chevrolet Suburban	老车资料需多源核对；结构由 SUV/Wagon 收敛为 Wagon	待终核: 缺失 1948-1954 逐年参考及三维
4) 下一步优先核对

Malibu gen3 剩余缺口：1975/1976/1977 Wagon 高度、1977 Sedan 高度。

Malibu gen4 1978-1983：Sedan / Coupe / Wagon 三维与 1982-1983 wagon 是否仍在当前范围内保留。

Silverado 2500HD gen2 2010-2014：按 Regular / Extended / Crew 与 6.5 / 8.0 继续拆。

Silverado 2500HD gen3 2015-2018：按 Regular / Double / Crew 与 6.5 / 8.0 继续拆。

Suburban 1935-1954：继续追加 GM Heritage / brochure / old car manual；谨慎使用 Automobile-Catalog、拍卖 listing、dealer 描述，只做线索。

下一步


--- Round 6 / 下一步 ---

主车型	分类	品牌	车型名	结构	版本	代际	代际说明	年份区间	区间最小年份	区间最大年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in	max_height_in	参考车型	备注	迭代状态
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	53.2	1964-1965 Chevrolet Malibu Sedan	原混合结构拆分；1964-1965 sedan 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1966						197.0	75.0	53.0	1966 Chevrolet Malibu Sedan	原混合结构拆分；1966 sedan 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen1	Chevelle Malibu midsize	1967						197.0	75.0	53.0	1967 Chevrolet Malibu Sedan	1967 Sedan 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	52.8	1964-1965 Chevrolet Malibu Sport Coupe	原混合结构拆分；1964-1965 coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1966						197.0	75.0	51.9	1966 Chevrolet Malibu Sport Coupe	原混合结构拆分；1966 coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen1	Chevelle Malibu midsize	1967						197.0	75.0	52.5	1967 Chevrolet Malibu Coupe	1967 Coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1964-1965						193.9	74.6	52.9	1964-1965 Chevrolet Malibu Convertible	原混合结构拆分；1964-1965 convertible 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1966						197.0	75.0	52.8	1966 Chevrolet Malibu Convertible	原混合结构拆分；1966 convertible 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen1	Chevelle Malibu midsize	1967						197.0	75.0	52.8	1967 Chevrolet Malibu Convertible	1967 Convertible 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1964-1965						198.8	74.6	55.1	1964-1965 Chevrolet Malibu Wagon	原混合结构拆分；1964-1965 wagon 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1966						199.8	75.0	54.6	1966 Chevrolet Malibu Wagon	原混合结构拆分；1966 wagon 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen1	Chevelle Malibu midsize	1967						199.0	75.0	54.5	1967 Chevrolet Malibu Wagon	1967 Wagon 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen2	restyled Chevelle Malibu midsize	1968-1969						197.4	74.8	53.2	1968-1969 Chevrolet Malibu Sedan	1968-1969 Sedan 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen2	restyled Chevelle Malibu midsize	1968-1969						197.2	74.5	52.9	1968-1969 Chevrolet Malibu Coupe	1968-1969 Coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen2	restyled Chevelle Malibu midsize	1968-1969						197.5	74.7	53.0	1968-1969 Chevrolet Malibu Convertible	1968-1969 Convertible 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen2	restyled Chevelle Malibu midsize	1968-1969						199.0	75.0	54.6	1968-1969 Chevrolet Malibu Wagon	1968-1969 Wagon 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen2	restyled Chevelle Malibu midsize	1970-1972						197.5	75.0	53.2	1970-1972 Chevrolet Malibu Sedan	1970-1972 Sedan 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen2	restyled Chevelle Malibu midsize	1970-1972						197.3	74.8	52.9	1970-1972 Chevrolet Malibu Coupe	1970-1972 Coupe 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Convertible		gen2	restyled Chevelle Malibu midsize	1970-1972						197.5	74.9	53.0	1970-1972 Chevrolet Malibu Convertible	1970-1972 Convertible 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen2	restyled Chevelle Malibu midsize	1970-1972						199.2	75.0	54.6	1970-1972 Chevrolet Malibu Wagon	1970-1972 Wagon 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen3	colonnade midsize body	1973-1974						197.9	74.5	53.1	1973-1974 Chevrolet Malibu Sedan	1973-1974 Sedan 三维已补	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen3	colonnade midsize body	1973-1974						197.7	74.3	52.8	1973-1974 Chevrolet Malibu Coupe	1973-1974 Coupe 三维已补	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1973-1974						199.5	74.8	54.2	1973-1974 Chevrolet Malibu Wagon	1973-1974 Wagon 三维已补	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen3	colonnade midsize body	1975-1976						209.3	76.6	53.8	1975-1976 Chevrolet Malibu Sedan	官方 brochure 补宽度/loaded height；长度按同年 sedan 资料补齐	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen3	colonnade midsize body	1975-1976						205.3	76.6	53.1	1975-1976 Chevrolet Malibu Coupe	官方 brochure 补宽度/loaded height；Automobile-Catalog 补 length	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1975						215.4	76.6	55.8	1975 Chevrolet Malibu Wagon	先补高度空值；1975 wagon 长宽已补，height 先按 1975 Malibu Classic Estate Wagon / 1976-1977 同代 wagon 口径补入；需官方 wagon catalog 复核	待终核: 1975 wagon 高度来源等级不足
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1976						215.2	76.8	55.7	1976 Chevrolet Malibu Wagon	谨慎来源补齐三维；仍需官方 wagon catalog 交叉确认	待终核: 1976 wagon 高度来源等级不足
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen3	colonnade midsize body	1977						209.7	76.9	54.1	1977 Chevrolet Malibu Sedan	先补高度空值；Carfolio 1977 Chevelle Malibu Sedan 给出 height 54.1 in；length 仍保留当前 brochure 口径 209.7	待终核: 1977 sedan 长度/高度需 brochure 复核
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen3	colonnade midsize body	1977						205.7	76.9	53.3	1977 Chevrolet Malibu Coupe	1977 brochure / archive 补长宽高	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen3	colonnade midsize body	1977						215.4	76.8	55.8	1977 Chevrolet Malibu Wagon	Automobile-Catalog 与 Carfolio 高度一致；作为 wagon 单年闭合	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen4	downsized G-body midsize	1978						192.7	71.5	54.2	1978 Chevrolet Malibu Sedan	1978 brochure 尺寸表补齐 length/width/height	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen4	downsized G-body midsize	1978						192.7	71.5	53.3	1978 Chevrolet Malibu Coupe	1978 brochure 尺寸表补齐 length/width/height	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen4	downsized G-body midsize	1978						193.4	71.2	54.5	1978 Chevrolet Malibu Wagon	1978 brochure 尺寸表补齐 length/width/height	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen4	downsized G-body midsize	1979						192.7	71.5	54.2	1979 Chevrolet Malibu Sedan	Automobile-Catalog 补齐 length/width/height；需官方 brochure 或一般可信来源交叉确认	待终核: 1979 sedan 来源等级不足
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen4	downsized G-body midsize	1979						192.7	71.5	53.3	1979 Chevrolet Malibu Sport Coupe	Automobile-Catalog 补齐 length/width/height；需官方 brochure 或一般可信来源交叉确认	待终核: 1979 coupe 来源等级不足
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen4	downsized G-body midsize	1979						193.4	71.5	54.5	1979 Chevrolet Malibu Wagon	Automobile-Catalog 补齐 length/width/height；Conceptcarz 交叉 length/width；需官方 brochure 复核高度	待终核: 1979 wagon 来源等级不足
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen4	downsized G-body midsize	1980						192.7	71.5	54.2	1980 Chevrolet Malibu Sedan	谨慎来源补齐三维；需官方 brochure 或一般可信来源交叉确认	待终核: 1980 sedan 来源等级不足
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen4	downsized G-body midsize	1980						192.7	71.5	53.3	1980 Chevrolet Malibu Sport Coupe	Automobile-Catalog 与 Auto-Data 补齐 length/width/height；需官方 brochure 或一般可信来源交叉确认	待终核: 1980 coupe 来源等级不足
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen4	downsized G-body midsize	1980						193.4	71.5	54.5	1980 Chevrolet Malibu Wagon	谨慎来源补齐三维；需官方 brochure 或一般可信来源交叉确认	待终核: 1980 wagon 来源等级不足
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen4	downsized G-body midsize	1981						192.7	72.3	55.7	1981 Chevrolet Malibu Sedan	1981 Chevrolet Malibu brochure page 13 官方尺寸表闭合 Sedan length/width/height	可入库
Chevrolet Malibu	跑车	Chevrolet	Malibu	Coupe		gen4	downsized G-body midsize	1981						192.7	72.3	55.7	1981 Chevrolet Malibu Sport Coupe	1981 Chevrolet Malibu brochure page 13 官方尺寸表闭合 Coupe length/width/height	可入库
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen4	downsized G-body midsize	1981						193.4	71.9	55.8	1981 Chevrolet Malibu Wagon	1981 Chevrolet Malibu brochure page 19 官方尺寸表闭合 Wagon length/width/height	可入库
Chevrolet Malibu	三厢车	Chevrolet	Malibu	Sedan		gen4	downsized G-body midsize	1982-1983						192.7	72.3	55.7	1982/1983 Chevrolet Malibu Sedan	1982 Conceptcarz 补强 Sedan length/width；1983 Automobile-Catalog 确认 Sport Sedan 版本范围；height 仍主要来自 Auto-Data/Carfolio，需 1982-1983 brochure 或一般可信来源交叉确认	待终核: 1982-1983 sedan 高度来源等级不足
Chevrolet Malibu	两厢车	Chevrolet	Malibu	Wagon		gen4	downsized G-body midsize	1982-1983						193.4	71.9	55.8	1982/1983 Chevrolet Malibu Wagon	Auto-Data 与 1981 brochure 口径相同；Classic.com 补强 1983 4 Door Wagon 存在记录；仍需 1982-1983 wagon brochure 或一般可信来源交叉确认	待终核: 1982-1983 wagon 来源等级不足
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1983						170.4	64.7	64.3	1983 Chevrolet S-10 Blazer 2-Door	Automobile-Catalog 补齐 2WD/4WD 三维；Car and Driver archive 确认 1983 4x4 2-door wagon 与 170.4 length；2WD 高 64.0、4WD 高 64.3，按覆盖最大高度暂填	待终核: 1983 2-door 来源等级不足
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1984						170.4	64.7	64.3	1984 Chevrolet S-10 Blazer 2-Door	Automobile-Catalog 补齐 2WD/4WD 三维；2WD 高 64.0、4WD 高 64.3，按覆盖最大高度暂填	待终核: 1984 2-door 来源等级不足
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1985						170.4	64.7	64.0	1985 Chevrolet S-10 Blazer 2-Door	Automobile-Catalog 补齐三维；需 Edmunds/KBB/JD Power 或 brochure 交叉确认	待终核: 1985 2-door 来源等级不足
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1986						170.4	64.7	64.0	1986 Chevrolet S-10 Blazer 2-Door	Automobile-Catalog 补齐三维；CarGurus 1986 trim/specs 概括值 length 170 / width 64 / height 64 与现值大体一致；J.D. Power 有 1986 条目但未解析出 exterior dimensions；仍需 brochure/Edmunds/KBB 交叉	待终核: 1986 2-door 来源等级不足
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1987						170.0	65.0	64.0	1987 Chevrolet S-10 Blazer 2-Door	一般规格页补齐三维；Automobile-Catalog 确认 1987 3-door 版本存在；需 Edmunds/KBB/JD Power 或 brochure 交叉确认	待终核: 1987 2-door 来源等级不足
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1988						170.4	65.4	64.3	1988 Chevrolet S-10 Blazer 2-Door	Automobile-Catalog 补齐 2WD/4WD 三维；AutoDetective 2WD/4WD 交叉给出 width 65.4、4WD height 64.3；按覆盖口径宽度由 64.7 修正为 65.4，高度保留 64.3；需 brochure/KBB/J.D. Power 终核	待终核: 1988 2-door 宽度来源冲突
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1989						170.4	64.7	64.3	1989 Chevrolet S-10 Blazer 2-Door	Automobile-Catalog 补齐三维；2WD 高 64.0、4WD 高 64.3，按覆盖最大高度暂填	待终核: 1989 2-door 来源等级不足
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1990						170.3	65.4	64.1	1990 Chevrolet S-10 Blazer 2-Door	Edmunds 补齐 length/width w/o mirrors/height	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1991						170.3	65.4	64.3	1991 Chevrolet S-10 Blazer 2-Door	1991 2-Door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1992-1993						176.8	65.4	62.8	1992-1993 Chevrolet S-10 Blazer 2-Door	1992-1993 2-door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1991						176.8	65.4	62.8	1991 Chevrolet S-10 Blazer 4-Door	1991 起 4-door 单独拆分	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1992-1993						176.8	65.4	62.8	1992-1993 Chevrolet S-10 Blazer 4-Door	1992-1993 4-door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	2-Door	gen1	compact SUV	1994						170.3	65.4	64.3	1994 Chevrolet S-10 Blazer 2-Door	1994 2-door 三维已补	可入库
Chevrolet S-10 Blazer	越野车	Chevrolet	S-10 Blazer	SUV	4-Door	gen1	compact SUV	1994						176.8	65.4	64.1	1994 Chevrolet S-10 Blazer 4-Door	1994 4-door 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Regular Cab	8.0	224.7	79.9	76.4	2008 Chevrolet Silverado 2500HD Regular Cab 8 ft	已按 cab/bed 拆分；三维口径 w/o mirrors	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Crew Cab	6.5	239.9	79.9	77.1	2008 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	已按 cab/bed 拆分；三维口径 w/o mirrors	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2008			Crew Cab	8.0	258.7	79.9	76.4	2008 Chevrolet Silverado 2500HD Crew Cab 8 ft	2008 Crew Cab 高度已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2009			Crew Cab	6.5	239.9	79.9	77.1	2009 Chevrolet Silverado 2500HD Crew Cab 6.5 ft	2009 Crew Cab 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2009			Regular Cab	8.0	224.7	79.9	76.4	2009 Chevrolet Silverado 2500HD Regular Cab 8 ft	2009 Regular Cab 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2010			Regular Cab	8.0	224.7	79.9	76.4	2010 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2010			Extended Cab	6.5	230.3	79.9	76.8	2010 Chevrolet Silverado 2500HD Extended Cab SB	Edmunds Extended Cab 页补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2010			Extended Cab	8.0	249.2	79.9	76.7	2010 Chevrolet Silverado 2500HD Extended Cab LB	Edmunds LT Extended Cab 长斗页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2010			Crew Cab	6.5	239.9	79.9	77.1	2010 Chevrolet Silverado 2500HD Crew Cab SB	Edmunds trim 页确认 bed 78.9 in；按 Crew Cab 规格闭合三维	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2011			Regular Cab	8.0	225.0	80.0	77.6	2011 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2011			Extended Cab	6.5	230.6	80.0	77.9	2011 Chevrolet Silverado 2500HD Extended Cab SB	Edmunds Extended Cab 页确认 bed 78.8 in、width/height；短斗按同页 wheelbase/length 组合补齐	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2011			Extended Cab	8.0	249.5	80.0	77.6	2011 Chevrolet Silverado 2500HD Extended Cab LB	Edmunds 同代 Extended Cab 长斗规格；2012 Extended Cab 8.0 交叉	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2011			Crew Cab	6.5	240.2	80.0	78.3	2011 Chevrolet Silverado 2500HD Crew Cab SB	Edmunds 补齐 length/width w/o mirrors/height；bed 78.8 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2011			Crew Cab	8.0	259.1	80.0	78.1	2011 Chevrolet Silverado 2500HD Crew Cab LB	Edmunds LTZ Crew Cab 4WD LB 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2012			Regular Cab	8.0	225.0	80.0	77.5	2012 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2012			Extended Cab	8.0	249.5	80.0	77.6	2012 Chevrolet Silverado 2500HD Extended Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2012			Crew Cab	6.5	240.2	80.0	78.1	2012 Chevrolet Silverado 2500HD Crew Cab SB	Edmunds 补齐 length/width w/o mirrors/height；bed 78.8 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2012			Crew Cab	8.0	259.1	80.0	78.1	2012 Chevrolet Silverado 2500HD Crew Cab LB	Edmunds Work Truck 4dr Crew Cab 4WD LB 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2013			Regular Cab	8.0	225.0	80.0	77.5	2013 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2013			Extended Cab	8.0	249.5	80.0	77.6	2013 Chevrolet Silverado 2500HD Extended Cab LB	Edmunds trim 页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2013			Crew Cab	6.5	240.2	80.0	78.1	2013 Chevrolet Silverado 2500HD Crew Cab SB	Edmunds 补齐 length/width w/o mirrors/height；bed 78.8 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2013			Crew Cab	8.0	259.1	80.0	78.1	2013 Chevrolet Silverado 2500HD Crew Cab LB	Edmunds Crew Cab LTZ 长斗页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2014			Regular Cab	8.0	225.0	80.0	77.5	2014 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2014			Extended Cab	8.0	249.5	80.0	77.6	2014 Chevrolet Silverado 2500HD Extended Cab LB	Edmunds 2014 Regular / 2013 Extended / 2012 Extended 规格交叉；同代长斗组合闭合	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2014			Crew Cab	6.5	240.2	80.0	78.1	2014 Chevrolet Silverado 2500HD Crew Cab SB	Edmunds 补齐 length/width w/o mirrors/height；bed 78.8 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen2	GMT900 HD pickup	2014			Crew Cab	8.0	259.1	80.0	78.1	2014 Chevrolet Silverado 2500HD Crew Cab LB	Edmunds LT Crew Cab 长斗页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2015			Regular Cab	8.0	224.4	80.1	77.8	2015 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2015			Double Cab	6.5	230.0	80.5	78.1	2015 Chevrolet Silverado 2500HD Double Cab Standard Box	Edmunds 补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2015			Double Cab	8.0	248.9	80.5	77.9	2015 Chevrolet Silverado 2500HD Double Cab Long Box	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2015			Crew Cab	6.5	239.5	80.5	78.3	2015 Chevrolet Silverado 2500HD Crew Cab Standard Box	Edmunds 补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2015			Crew Cab	8.0	258.4	80.5	78.0	2015 Chevrolet Silverado 2500HD Crew Cab Long Box	Edmunds 总规格页给出 length/width w/o mirrors/height；长度对应 Crew Cab long bed	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2016			Regular Cab	8.0	224.4	80.1	77.8	2016 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2016			Double Cab	6.5	230.0	80.5	78.1	2016 Chevrolet Silverado 2500HD Double Cab Standard Box	Edmunds Double Cab 页补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2016			Double Cab	8.0	248.9	80.5	77.9	2016 Chevrolet Silverado 2500HD Double Cab Long Box	Edmunds 2016 LTZ Double Cab 长斗页补齐 length/width w/o mirrors/height；GM 官方规格表确认 2500HD Double Cab 8’ box	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2016			Crew Cab	6.5	239.5	80.5	78.2	2016 Chevrolet Silverado 2500HD Crew Cab SB	Edmunds 总规格页对应 Crew Cab 4WD SB；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2016			Crew Cab	8.0	258.4	80.5	78.0	2016 Chevrolet Silverado 2500HD Crew Cab LB	Edmunds Crew Cab LT 长斗页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2017			Regular Cab	8.0	224.4	80.1	77.8	2017 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2017			Double Cab	6.5	230.0	80.5	78.1	2017 Chevrolet Silverado 2500HD Double Cab Standard Box	Edmunds 补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2017			Double Cab	8.0	248.9	80.5	77.8	2017 Chevrolet Silverado 2500HD Double Cab Long Box	Edmunds trims 页确认 2017 Double Cab 可选 long bed；The Car Connection 列出 Double Cab 158.1 in 轴距；KBB 确认 4D 8 ft、overall length 248.9 in、wheelbase 158.1 in；Edmunds 默认 Double Cab 页只覆盖 78.9 in 短斗，不能闭合长斗宽高	待终核: 2017 Double Cab 8.0 宽高需 Edmunds/官方尺寸表复核
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2017			Crew Cab	6.5	239.5	80.5	78.2	2017 Chevrolet Silverado 2500HD Crew Cab Standard Box	Edmunds 总规格页补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2017			Crew Cab	8.0	258.4	80.5	78.0	2017 Chevrolet Silverado 2500HD Crew Cab Long Box	Edmunds Crew Cab High Country 长斗页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2018			Regular Cab	8.0	224.4	80.1	77.8	2018 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds Work Truck Regular Cab 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2018			Double Cab	6.5	230.0	80.5	78.1	2018 Chevrolet Silverado 2500HD Double Cab Standard Box	Edmunds Double Cab 补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2018			Double Cab	8.0	248.9	80.5	77.8	2018 Chevrolet Silverado 2500HD Double Cab Long Box	Edmunds Work Truck Double Cab long box 补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2018			Crew Cab	6.5	239.5	80.5	78.2	2018 Chevrolet Silverado 2500HD Crew Cab Standard Box	Edmunds Crew Cab 补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2018			Crew Cab	8.0	258.4	80.5	78.0	2018 Chevrolet Silverado 2500HD Crew Cab Long Box	Edmunds Crew Cab LTZ 长斗页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Regular Cab	8.0	224.4	80.1	77.8	2019 Chevrolet Silverado 2500HD Regular Cab LB	Edmunds Regular Cab 页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Double Cab	6.5	230.0	80.5	78.1	2019 Chevrolet Silverado 2500HD Double Cab Standard Box	Edmunds Double Cab 页补齐 length/width w/o mirrors/height；bed 78.9 in 约 6.5 ft	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Double Cab	8.0	248.9	80.5	77.87	2019 Chevrolet Silverado 2500HD Double Cab Long Box	2019 Double Cab long bed 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Crew Cab	6.5	239.5	80.5	78.2	2019 Chevrolet Silverado 2500HD Crew Cab Standard Box	2019 Crew Cab standard bed 三维已补	可入库
Chevrolet Silverado 2500HD	皮卡	Chevrolet	Silverado 2500HD	Pickup		gen3	K2XX HD pickup	2019			Crew Cab	8.0	258.4	80.5	78.0	2019 Chevrolet Silverado 2500HD Crew Cab Long Box	Edmunds Work Truck Crew Cab 长斗页补齐 length/width w/o mirrors/height；bed 97.8 in 约 8.0 ft	可入库
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen1	early Carryall truck-based wagon	1935-1940						172.1	72.0	74.8	1935/1936/1939 Chevrolet Suburban Carryall	先补三维空值；1936 GM Heritage 确认 112 in wheelbase，1936 Chevrolet Truck brochure 摘要给出 overall length/height 线索；width 先按同 half-ton carryall 车身宽度暂补	待终核: 1935-1940 三维为早期资料补值，需逐年手册页复核
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen2	wartime/AK-series truck-based wagon	1941-1946						198.0	75.0	76.0	1941/1942/1946 Chevrolet Suburban Carryall	先补三维空值；Conceptcarz 1941 Series AK 明确 Suburban length 198.0、wheelbase 115.0；width/height 先按 AK truck/carryall body 口径暂补	待终核: 1941-1946 宽高需 1941 Chevrolet Specifications page 19 复核
Chevrolet Suburban	越野车	Chevrolet	Suburban	Wagon		gen3	Advance Design truck-based wagon	1947-1954						190.0	76.0	75.0	1947/1948/1949/1950/1951/1952/1953/1954 Chevrolet Suburban	先补三维空值；第三代基于 Advance Design pickups，1947-1954 Suburban 2-door wagon 范围已确认；三维按同平台资料先填保守估值	待终核: 1947-1954 三维为补缺估值，需 Advance Design truck data sheet / brochure 复核