# 文件名：split_part_04.tsv


--- Round 1 / 首次发送 ---
更新点
车型	操作	描述
Chevrolet Caprice Coupe/Sedan	拆出	1966 与 1967 外宽不同，1967 full-size Chevrolet 外宽为 79.9 in，不能继续压缩在 1966-1967。
Over-Drive Magazine
+1

Chevrolet Caprice Coupe/Sedan	值修改	1969 与 1970 拆单年；1969 采用 215.9/79.8/54.8，1970 采用 216.0/79.8/54.5。
汽车目录
+1

Chevrolet Caprice Wagon	拆出	1968 wagon 已可入库；1969-1970 wagon 仍缺完整三维逐年确认，保留待终核。
当前批次进度
状态	数量
🟢 可入库	8
🟡 待终核	1
🔴 缺数据	0
本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, Over-Drive	gen1早期硬顶Coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1967			213.2	79.9	54.4	1967 Chevrolet Caprice Custom Coupe, Automobile-Catalog / Over-Drive	gen1早期硬顶Coupe	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan, Over-Drive / Oldride	gen1早期Sedan	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1967			213.2	79.9	55.4	1967 Chevrolet Caprice Sedan, Over-Drive	gen1早期Sedan	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon / Chevrolet Station Wagons brochure	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1969-1970			216.7	79.8	56.7	1969/1970 Chevrolet Kingswood Estate Wagon proxy	wagon高车身	待终核: 1969-1970 wagon三维逐年确认
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969			215.9	79.8	54.8	1969 Chevrolet Caprice Custom Coupe / Sedan, Automobile-Catalog	gen1全尺寸硬顶Coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Coupe / Sedan, Automobile-Catalog / UltimateSpecs	gen1全尺寸硬顶Coupe	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969			215.9	79.8	54.8	1969 Chevrolet Caprice Custom Sedan, Automobile-Catalog	gen1全尺寸Sedan	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, Automobile-Catalog / UltimateSpecs	gen1全尺寸Sedan	可入库
下一步优先核对

优先补齐 1969-1970 Chevrolet Kingswood Estate Wagon / Caprice Estate Wagon 的逐年三维来源；确认后这一批大概率可以全部转为可入库。

下一步。


--- Round 2 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Caprice Wagon	值修改	1969 wagon 已核到 216.7 / 79.8 / 57.1，修正上一轮的 56.7 高度。
Ultimate Specs
+1

Chevrolet Caprice Wagon	值修改	1970 wagon 已核到 216.8 / 79.8 / 57.1，与 1969 长度差 0.1 in，但按本批规则可拆单年保留真实来源。
汽车目录
+1

Chevrolet Caprice Wagon	拆出	原 1969-1970 wagon 拆成 1969、1970 两条，参考车型分别覆盖单年，状态改为可入库。
2) 当前批次进度
状态	数量
🟢 可入库	10
🟡 待终核	0
🔴 缺数据	0
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, Over-Drive	gen1早期硬顶Coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1967			213.2	79.9	54.4	1967 Chevrolet Caprice Custom Coupe, Automobile-Catalog / Over-Drive	gen1早期硬顶Coupe	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan, Over-Drive / Oldride	gen1早期Sedan	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1967			213.2	79.9	55.4	1967 Chevrolet Caprice Sedan, Over-Drive	gen1早期Sedan	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon / Chevrolet Station Wagons brochure	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1969			216.7	79.8	57.1	1969 Chevrolet Kingswood Estate Wagon, Automobile-Catalog / UltimateSpecs	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1970			216.8	79.8	57.1	1970 Chevrolet Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969			215.9	79.8	54.8	1969 Chevrolet Caprice Custom Coupe / Sedan, Automobile-Catalog	gen1全尺寸硬顶Coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Coupe / Sedan, Automobile-Catalog / UltimateSpecs	gen1全尺寸硬顶Coupe	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969			215.9	79.8	54.8	1969 Chevrolet Caprice Custom Sedan, Automobile-Catalog	gen1全尺寸Sedan	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, Automobile-Catalog / UltimateSpecs	gen1全尺寸Sedan	可入库
4) 下一步优先核对

当前批次已无待终核项；如果作为最后一轮，可直接进入当前 split 的完整替换/出库确认。

本批次完成。

