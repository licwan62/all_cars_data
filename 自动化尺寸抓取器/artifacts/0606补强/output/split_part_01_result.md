# 文件名：split_part_01.tsv


--- Round 1 / 首次发送 ---
更新点

车型	操作	描述
Buick LeSabre	值修改	1989 Sedan 长度按多来源差异取更保守值 197.2，高度按 Automobile-Catalog Sedan 55.5；状态推进为可入库。
汽车目录
+1

Chevrolet Camaro	状态推进	1974、1977 gen2 Coupe 尺寸可确认，状态推进为可入库。
汽车目录
+1

Chevrolet Camaro	拆出	1967-1969 gen1 Coupe 因 1969 长宽高与 1967-1968 不同，拆成 1967-1968 与 1969 两行。
汽车目录
+1

当前批次更新后的完整可替换 TSV：

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Buick LeSabre	Buick	三厢车		Sedan	Std.	gen6 full-size	1989			197.2	72.4	55.5	1989 Buick LeSabre Custom/Limited Sedan, Automobile-Catalog / Autodetective	FWD缩小; 多来源取保守长高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Type LT / Z28 Coupe, Automobile-Catalog / GM brochure	保险杠加长	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Sport Coupe / LT Coupe / Z28 Coupe, ConceptCarz / GM brochure	保险杠加长	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1968			184.7	72.5	51.5	1967-1968 Chevrolet Camaro Sport Coupe, Automobile-Catalog	gen1短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1969			186	74	51.1	1969 Chevrolet Camaro Sport Coupe, Automobile-Catalog	1969新钣金更宽更长	可入库

本批次完成。

