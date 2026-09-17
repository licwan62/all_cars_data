# 文件名：split_part_02.tsv


--- Round 1 / 首次发送 ---
更新点
车型	操作	描述
Chevrolet Camaro	字段修复	按新统一表头补入“驾驶室类型 / 货斗长度_ft”空列。
Chevrolet Camaro gen4	拆出	Coupe/Convertible 拆成 Coupe 与 Convertible 两条，结构字段保持单一结构。
Chevrolet Camaro gen2	值确认	1978/1980/1981 ConceptCarz 显示晚期 Coupe 为 197.6 / 74.5 / 49.2，保留原尺寸并推进为可入库。
conceptcarz.com
+2
conceptcarz.com
+2

Chevrolet Camaro gen3 Convertible	值修改	1991 Edmunds 显示 Convertible 为 192.6 / 72.8 / 50.4，修正原宽高。
Edmunds
+1

Chevrolet Camaro gen4	值修改	gen4 Coupe/Hatchback 为 193.2 / 74.1 / 51.3；Convertible 为 193.2 / 74.1 / 52.0，拆分后分别填写。
Edmunds
+3
Edmunds
+3
Edmunds
+3
当前批次进度
状态	数量	说明
🟢 可入库	5	gen2 Coupe、gen3 Convertible、gen4 Coupe、gen4 Convertible、gen4 Z28 Coupe
🟡 待终核	1	gen1 Convertible 仍缺 1969 Convertible 终核
🔴 未处理	0	本轮已覆盖当前文件全部输入记录
本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	Std.	gen1 pony car	1967-1969			186	74	51.4	1967/1968 Chevrolet Camaro Convertible, ConceptCarz / 1969 Chevrolet Camaro Convertible proxy	gen1敞篷; 1969车宽需终核	待终核: 1969 Convertible
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1978/1980/1981 Chevrolet Camaro Coupe, ConceptCarz / 1979 Chevrolet Camaro Z28 Coupe, Encycarpedia	晚期保险杠最长	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	Std.	gen3 pony car	1991-1992			192.6	72.8	50.4	1991 Chevrolet Camaro Convertible, Edmunds / 1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Coupe	Std.	gen4 pony car	1994-1997			193.2	74.1	51.3	1994/1995/1996/1997 Chevrolet Camaro Hatchback/Coupe, Edmunds	gen4早期Coupe/Hatchback低车身	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994/1995/1996/1997 Chevrolet Camaro Convertible, Edmunds	gen4敞篷高车身	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	51.3	1996/1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28 Coupe低车身	可入库
下一步优先核对

优先补 1969 Chevrolet Camaro Convertible 的真实尺寸来源；当前仅 gen1 Convertible 还不能标可入库。

下一步


--- Round 2 / 下一步 ---
1) 更新点
车型	操作	描述
Chevrolet Camaro gen1 Convertible	值确认	1969 Convertible 可用 Automobile-Catalog / ConceptCarz 交叉确认，1969 为 186 in 长、74 in 宽、约 51 in 高；因此 1967-1969 区间最大值保留 186 / 74 / 51.4，并把原“待终核: 1969 Convertible”推进为可入库。
conceptcarz.com
+1

Chevrolet Camaro gen1 Convertible	参考车型补强	参考车型补成 1967-1969 Chevrolet Camaro Convertible，覆盖整个年份区间，不再只写 proxy。
Chevrolet Camaro gen4	结构保持	继续保留上一轮拆分后的 Coupe / Convertible 单一结构行，不回退到 Coupe/Convertible 混合结构。
2) 当前批次进度
状态	数量	说明
🟢 可入库	6	当前 split 内 6 条拆分后记录均已覆盖年份/结构/版本
🟡 待终核	0	无
🔴 未处理	0	无
3) 本轮更新后的 TSV
tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	Std.	gen1 pony car	1967-1969			186	74	51.4	1967-1969 Chevrolet Camaro Convertible, GM/ConceptCarz/Automobile-Catalog	gen1敞篷; 1969更宽	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1978/1980/1981 Chevrolet Camaro Coupe, ConceptCarz / 1979 Chevrolet Camaro Z28 Coupe, Encycarpedia	晚期保险杠最长	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	Std.	gen3 pony car	1991-1992			192.6	72.8	50.4	1991 Chevrolet Camaro Convertible, Edmunds / 1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Coupe	Std.	gen4 pony car	1994-1997			193.2	74.1	51.3	1994/1995/1996/1997 Chevrolet Camaro Hatchback/Coupe, Edmunds	gen4早期Coupe/Hatchback低车身	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994/1995/1996/1997 Chevrolet Camaro Convertible, Edmunds	gen4敞篷高车身	可入库
Chevrolet Camaro	Chevrolet	跑车	Chevrolet Camaro	Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	51.3	1996/1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28 Coupe低车身	可入库
4) 下一步优先核对

无。当前 split_part_02 已补到全部可入库。

本批次完成。

