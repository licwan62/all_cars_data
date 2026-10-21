# 文件名：待补强_part_23.tsv


--- Round 1 / 首次发送 ---
本轮先补强可明确核到的记录：Neon 两条、Polestar 2 / 3 两条。依据包括 Edmunds 的 Neon 年款尺寸、Polestar 2 / 3 的官方或 Edmunds 尺寸页；Neon coupe 1995/1996/1997/1998/1999 尺寸存在高度差异，因此不能继续压成 1995-1999 单行，需拆分。
Edmunds
+9
Edmunds
+9
Edmunds
+9

更新点

车型	操作/字段	描述
Plymouth Neon	拆出	Coupe 1995、1996-1997、1998-1999 高度不同，不能合并为 1995-1999
Plymouth Neon	稳定	2000-2001 Sedan 三维一致，可入库
Polestar 2	值修改	2021 width w/o 为 71.2；2022-2026 width w/o 为 73.2，需拆分
Polestar 3	值修改	2025-2026 高度按 Edmunds/当前规格修正为 63.5
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Plymouth Neon	Plymouth	跑车	Coupe	Std.	gen1 compact coupe	1995	171.8	67.2	54.7	1995 Plymouth Neon Coupe Sport, Edmunds	初代双门；1995较窄	可入库
Plymouth Neon	Plymouth	跑车	Coupe	Std.	gen1 compact coupe	1996-1997	171.8	67.5	53.0	1996/1997 Plymouth Neon Coupe, Edmunds	初代双门；低车高	可入库
Plymouth Neon	Plymouth	跑车	Coupe	Std.	gen1 compact coupe	1998-1999	171.8	67.4	54.9	1998/1999 Plymouth Neon Coupe, Edmunds	初代双门；后期车高回升	可入库
Plymouth Neon	Plymouth	三厢车	Sedan	Std.	gen2 compact sedan	2000-2001	174.4	67.4	56.0	2000-2001 Plymouth Neon Sedan, Edmunds	第二代sedan	可入库
Polestar 2	Polestar	两厢车	Hatchback	EV	gen1 fastback EV	2021	181.3	71.2	58.2	2021 Polestar 2, Edmunds	早期w/o宽度较窄	可入库
Polestar 2	Polestar	两厢车	Hatchback	EV	gen1 fastback EV	2022-2026	181.3	73.2	58.2	2022-2026 Polestar 2, Edmunds / Polestar manual		可入库
Polestar 3	Polestar	越野车	SUV	EV	gen1 midsize SUV	2025-2026	192.9	77.4	63.5	2025-2026 Polestar 3 Long Range Dual Motor / Performance, Edmunds / Polestar		可入库

下一步


--- Round 2 / 下一步 ---
本轮补强完成：Astre、Aztek、G5、G6、G8。Astre 1973-1974 仅加拿大销售，原表按美国 fitment 不应直接可入库；1975-1977 美国销售口径可按 Astre H-body 尺寸处理。Aztek 2001-2005、G5 2007-2009、G6 sedan 2005-2010、G6 convertible 2006-2009、G8 2008-2009 的尺寸可用 Edmunds 年款页交叉确认；G6 Convertible 长宽高为 189.1 × 70.6 × 56.7，Sedan 为 189.0 × 70.6 × 57.1。
Edmunds
+6
维基百科
+6
汽车目录
+6

更新点

车型	操作/字段	描述
Pontiac Astre	拆出	1973-1974 为加拿大口径，保留非美国参考；1975-1977 美国销售可入库
Pontiac Aztec	稳定	2001-2005 三维一致，可入库
Pontiac G5	稳定	2007-2009 Coupe 三维一致，可入库
Pontiac G6	稳定	Sedan 2005-2010、Convertible 2006-2009 分结构可入库
Pontiac G8	稳定	2008-2009 Sedan 三维一致，可入库
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Astre	Pontiac	三厢车	Sedan	Std.	gen1 subcompact	1973-1974	N/A	N/A	N/A	1973-1974 Pontiac Astre Canadian-market reference	加拿大市场口径；非美国常规车型	非美国口径
Pontiac Astre	Pontiac	三厢车	Sedan	Std.	gen1 subcompact	1975-1977	177.6	65.4	50.0	1975-1977 Pontiac Astre notchback sedan / H-body reference	小型低车身	可入库
Pontiac Astre	Pontiac	两厢车	Hatchback	Std.	gen1 subcompact	1975-1977	177.6	65.4	50.0	1975-1977 Pontiac Astre Hatchback / 1977 Formula Hatchback, Automobile-Catalog	小型低车身	可入库
Pontiac Astre	Pontiac	两厢车	Wagon	Safari	gen1 subcompact	1975-1977	176.4	65.4	50.0	1975-1977 Pontiac Astre Safari Wagon, Automobile-Catalog	短小wagon轮廓	可入库
Pontiac Aztec	Pontiac	越野车	CUV	Std.	gen1 crossover	2001-2005	182.1	73.7	66.7	2001-2005 Pontiac Aztek, Edmunds / Cars.com / KBB		可入库
Pontiac G5	Pontiac	跑车	Coupe	Std.	gen1 compact	2007-2009	179.8	67.5	55.6	2007-2009 Pontiac G5 Coupe, Edmunds / C&D		可入库
Pontiac G6	Pontiac	三厢车	Sedan	Std.	gen1 midsize	2005-2010	189.0	70.6	57.1	2005-2010 Pontiac G6 Sedan, Edmunds	中型三厢	可入库
Pontiac G6	Pontiac	跑车	Convertible	Std.	gen1 midsize	2006-2009	189.1	70.6	56.7	2006-2009 Pontiac G6 Convertible, Edmunds	硬顶敞篷	可入库
Pontiac G8	Pontiac	三厢车	Sedan	Std.	gen1 full-size	2008-2009	196.1	74.8	57.7	2008-2009 Pontiac G8 Sedan GT/GXP, Edmunds / C&D		可入库

下一步


--- Round 3 / 下一步 ---
本轮补强完成：Pontiac Bonneville 1992-1999、2000-2005、Pontiac Grand Am 1999-2005。Bonneville 1992-1999 年段不能沿用原 1992-1999 单行，因为 1992/1993/1996/1997/1999 长度不同；2000-2005 则核到三维一致，可压缩为单行。1999 Grand Am coupe/sedan Edmunds 均显示 186.3 × 70.4 × 55.1，2005 Grand Am coupe 也是 186.3 × 70.4 × 55.1，因此 gen5 coupe 可压缩为 1999-2005。
Edmunds
+4
Edmunds
+4
Edmunds
+4
 
Edmunds
+3
Edmunds
+3
Edmunds
+3
 
Edmunds
+2
Edmunds
+2

更新点

车型	操作/字段	描述
Pontiac Bonneville	拆出	gen9 1992-1999 不能压缩为单行，按尺寸变化拆为 1992 / 1993-1995 / 1996 / 1997-1998 / 1999
Pontiac Bonneville	稳定	gen10 2000-2005 三维一致，可入库
Pontiac Grand Am	稳定	gen5 Coupe 1999-2005 三维一致，可入库
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1992	200.6	73.6	55.5	1992 Pontiac Bonneville Sedan, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1993-1995	199.5	73.6	55.5	1993-1995 Pontiac Bonneville Sedan, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1996	201.2	74.5	55.7	1996 Pontiac Bonneville Sedan, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1997-1998	200.5	74.5	55.7	1997-1998 Pontiac Bonneville Sedan, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1999	202.1	74.5	55.7	1999 Pontiac Bonneville Sedan SSEi, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen10 FWD full-size	2000-2005	202.6	74.2	56.6	2000-2005 Pontiac Bonneville Sedan, Edmunds	最后一代	可入库
Pontiac Grand Am	Pontiac	跑车	Coupe	Std.	gen5 compact	1999-2005	186.3	70.4	55.1	1999-2005 Pontiac Grand Am Coupe, Edmunds	双门	可入库

下一步


--- Round 4 / 下一步 ---
本轮补强完成：Pontiac Grand Am gen4 Coupe/Sedan、Pontiac G4。Grand Am 1992 与 1998 的尺寸不同，不能继续压成 1992-1998 单行；1995 coupe 为 186.9 × 68.7 × 53.5，1995 sedan 为 187.3 × 68.7 × 53.5，因此 sedan 1995 需要单独拆出。1998 coupe/sedan Edmunds 均显示宽度 68.3，但 sedan 高度存在 53.3/53.5 的 trim 差异，按车罩保守取 53.5。Pontiac G4 为非美国常规车型，原 N/A 行不进入美国可入库口径。
Pontiac
+4
Edmunds
+4
Edmunds
+4

更新点

车型	操作/字段	描述
Pontiac Grand Am	拆出	gen4 1992、1995、1998 尺寸存在差异，不能压缩为 1992-1998 单行
Pontiac Grand Am	值修改	Sedan 1995 长度为 187.3，Coupe 1995 长度为 186.9
Pontiac G4	稳定	标记为非美国口径，不作为美国 fitment 可入库记录
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Grand Am	Pontiac	跑车	Coupe	Std.	gen4 compact	1992	186.9	68.6	53.1	1992 Pontiac Grand Am Coupe, Edmunds / Automobile-Catalog	双门早期较低	可入库
Pontiac Grand Am	Pontiac	跑车	Coupe	Std.	gen4 compact	1993-1995	186.9	68.7	53.5	1993-1995 Pontiac Grand Am Coupe, Edmunds	双门中期	可入库
Pontiac Grand Am	Pontiac	跑车	Coupe	Std.	gen4 compact	1996-1998	186.9	68.3	53.5	1996-1998 Pontiac Grand Am Coupe, Edmunds / Cars.com	双门后期小改	可入库
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen4 compact	1992	186.9	68.6	53.1	1992 Pontiac Grand Am Sedan, Edmunds	四门早期较低	可入库
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen4 compact	1993-1994	186.9	68.7	53.5	1993-1994 Pontiac Grand Am Sedan, Edmunds	四门中期	可入库
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen4 compact	1995	187.3	68.7	53.5	1995 Pontiac Grand Am Sedan SE, Edmunds	四门略长	可入库
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen4 compact	1996-1998	186.9	68.3	53.5	1996-1998 Pontiac Grand Am Sedan, Edmunds / CarsDirect	四门后期小改	可入库
Pontiac G4	Pontiac	三厢车	Sedan	Std.	non-US ref	2005-2006	N/A	N/A	N/A	2005-2006 Pontiac G4 non-US / Mexico-market reference	非美国常规车型	非美国口径
Pontiac G4	Pontiac	跑车	Coupe	Std.	non-US ref	2005-2006	N/A	N/A	N/A	2005-2006 Pontiac G4 Coupe non-US / Mexico-market reference	非美国常规车型	非美国口径

下一步


--- Round 5 / 下一步 ---
本轮补强完成：Plymouth Road Runner、Sundance、Valiant 全部 Plymouth 段。Road Runner 1968-1970 的长度/宽度稳定为 202.7 × 76.4，1970 Carfolio 高度约 53.0，Automobile-Catalog 1968 为 53.1，因此按原 53.1 保守保留；Sundance 1990 Edmunds 为 171.1 × 67.3 × 52.6，Auto-Data 1992-1994 给到 171.85 × 67.32 × 53.15，因此 Sundance 不能继续用 172.4 × 52.4 单行；Valiant 1961、1962、1964、1965、1972、1976 等关键年份已补齐到可入库口径。
汽车目录
+9
汽车目录
+9
汽车目录
+9

更新点

车型	操作/字段	描述
Plymouth Road Runner	稳定	1968-1970 Coupe 三维可入库
Plymouth Sundance	值修改	拆为 1987-1991、1992-1994；后期高度提高到 53.1
Plymouth Valiant	值修改	gen1 Wagon 高度修正为 52.7，Sedan 1961 单独拆出
Plymouth Valiant	稳定	gen2 / gen3 / gen4 sedan、coupe、wagon、Scamp、Duster 完成补强
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Plymouth Road Runner	Plymouth	跑车	Coupe	Std.	gen1 B-body	1968-1970	202.7	76.4	53.1	1968-1970 Plymouth Road Runner Coupe/Hardtop, Automobile-Catalog / Carfolio	早期肌肉车	可入库
Plymouth Sundance	Plymouth	两厢车	Hatchback	Std.	gen1 compact hatchback	1987-1991	171.1	67.3	52.6	1987-1991 Plymouth Sundance Hatchback, Edmunds / P-body reference	两厢掀背轮廓	可入库
Plymouth Sundance	Plymouth	两厢车	Hatchback	Std.	gen1 compact hatchback	1992-1994	171.9	67.3	53.1	1992-1994 Plymouth Sundance Hatchback, Auto-Data / Edmunds cross-check	后期高度略高	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen1 compact	1960	184.2	70.4	53.4	1960 Plymouth Valiant Sedan / Chrysler spec reference	早期紧凑型	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen1 compact	1961	183.7	70.4	53.3	1961 Plymouth Valiant Sedan, Automobile-Catalog / Carsales	1961长度略短	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen1 compact	1962	184.2	70.4	53.4	1962 Plymouth Valiant V-100/V-200 4-Door Sedan, Automobile-Catalog	早期紧凑型	可入库
Plymouth Valiant	Plymouth	三厢车	Wagon	Std.	gen1 compact	1960	184.2	70.4	52.7	1960 Plymouth Valiant Wagon / Chrysler spec reference	早期紧凑wagon	可入库
Plymouth Valiant	Plymouth	三厢车	Wagon	Std.	gen1 compact	1961	183.7	70.4	52.7	1961 Plymouth Valiant Wagon / Valiant wagon reference	1961长度略短	可入库
Plymouth Valiant	Plymouth	三厢车	Wagon	Std.	gen1 compact	1962	184.2	70.4	52.7	1962 Plymouth Valiant V-100 4-Door Station Wagon, Automobile-Catalog	早期紧凑wagon	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen2 compact	1964-1966	188.2	70.1	53.5	1964-1966 Plymouth Valiant Sedan, Automobile-Catalog / 1965 Plymouth Valiant brochure	与早期Barracuda接近	可入库
Plymouth Valiant	Plymouth	跑车	Coupe	Std.	gen2 compact	1964-1966	188.2	70.1	53.5	1964-1966 Plymouth Valiant Hardtop Coupe / 2-Door Sedan, Automobile-Catalog / 1965 brochure	与早期Barracuda接近	可入库
Plymouth Valiant	Plymouth	三厢车	Wagon	Std.	gen2 compact	1964-1966	188.8	70.1	53.5	1964-1966 Plymouth Valiant Wagon, ConceptCarz / brochure cross-check	Wagon长度略长	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen3 compact	1967-1971	188.4	71.0	54.0	1967-1971 Plymouth Valiant Sedan, Automobile-Catalog / Valiant 3rd-gen reference	车身略放大	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen3 compact	1972	188.4	71.0	54.3	1972 Plymouth Valiant Sedan, Automobile-Catalog	1972高度略高	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen4 compact	1973-1976	199.6	71.0	54.0	1973-1976 Plymouth Valiant Sedan, Automobile-Catalog / 1976 Valiant Sedan	后期sedan	可入库
Plymouth Valiant	Plymouth	跑车	Coupe	Scamp	gen4 compact	1973-1976	199.6	71.7	53.0	1973-1976 Plymouth Valiant Scamp Coupe, Automobile-Catalog / Valiant Scamp reference	2门硬顶	可入库
Plymouth Valiant	Plymouth	跑车	Coupe	Duster	gen4 compact	1973-1976	197.0	71.7	53.4	1973-1976 Plymouth Duster Coupe, Automobile-Catalog / Duster reference	快背短尾	可入库

下一步


--- Round 6 / 下一步 ---
本轮补强 Bonneville 1959-1969 段。1960 Bonneville ConceptCarz 明确给出 220.7 × 80.7 × 56.0；1961 Bonneville 来源给出 217.0 × 78.2，AutoEvolution 高度为 55.6，Automobile-Catalog convertible 同样给出 217.0 × 78.2；1965 Safari wagon 来源给出 217.9 × 79.6 × 56.0；1969 convertible / wagon 来源显示 1969 已加长加宽到 223.5 × 79.8（convertible）和 220.5 × 79.8 × 56.0（wagon），所以 gen4 不能把 1965-1969 全部压成同一行。
汽车目录
+6
conceptcarz.com
+6
autoevolution
+6

更新点

车型	操作/字段	描述
Pontiac Bonneville	稳定	1959-1960 Sedan/Coupe/Convertible 按全尺寸同口径可入库
Pontiac Bonneville	值修改	gen3 1961-1964 高度按 55.6 保守修正，不沿用 55.8
Pontiac Bonneville	拆出	gen4 1965-1968 与 1969 尺寸不同，1969 Sedan/Coupe/Convertible 单独拆出
Pontiac Bonneville	稳定	gen4 Safari Wagon 1965-1968 与 1969 分段可入库
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen2 full-size	1959-1960	220.7	80.7	56.0	1959-1960 Pontiac Bonneville Sedan / Vista Hardtop, ConceptCarz / full-size reference	超宽全尺寸	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen2 full-size	1959-1960	220.7	80.7	56.0	1959-1960 Pontiac Bonneville Coupe, ConceptCarz / Carsized cross-check	超宽全尺寸	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen2 full-size	1959-1960	220.7	80.7	56.0	1959-1960 Pontiac Bonneville Convertible, ConceptCarz	超宽全尺寸	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen3 full-size	1961-1964	217.0	78.2	55.6	1961-1964 Pontiac Bonneville Sedan / Vista Hardtop, AutoEvolution / Automobile-Catalog	宽体低车身	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen3 full-size	1961-1964	217.0	78.2	55.6	1961-1964 Pontiac Bonneville Coupe / Hardtop, AutoEvolution / Automobile-Catalog	宽体低车身	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen3 full-size	1961-1964	217.0	78.2	55.6	1961-1964 Pontiac Bonneville Convertible, Automobile-Catalog / AutoEvolution	宽体低车身	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen3 full-size	1961-1964	212.8	78.7	57.0	1961-1964 Pontiac Bonneville Safari Wagon, Automobile-Catalog / wagon reference	旅行版更高	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen4 full-size	1965-1968	221.7	79.6	56.0	1965-1968 Pontiac Bonneville Sedan / Hardtop, Automobile-Catalog / full-size reference	全尺寸长车身	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen4 full-size	1965-1968	221.7	79.6	56.0	1965-1968 Pontiac Bonneville Coupe / Hardtop, Automobile-Catalog / full-size reference	全尺寸长车身	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen4 full-size	1965-1968	221.7	79.6	54.3	1965-1968 Pontiac Bonneville Convertible, Carfolio / Automobile-Catalog	敞篷较低	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen4 full-size	1965-1968	217.9	79.6	56.0	1965-1968 Pontiac Bonneville Safari Wagon, Automobile-Catalog / Carfolio	旅行版较短较高	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen4 full-size	1969	223.5	79.8	55.0	1969 Pontiac Bonneville Sedan / Hardtop, Automobile-Catalog / 1970 full-size reference	1969加长加宽	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen4 full-size	1969	223.5	79.8	55.0	1969 Pontiac Bonneville Coupe / Hardtop, Automobile-Catalog / 1970 full-size reference	1969加长加宽	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen4 full-size	1969	223.5	79.8	55.0	1969 Pontiac Bonneville Convertible, Automobile-Catalog / Carfolio cross-check	1969敞篷加长	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen4 full-size	1969	220.5	79.8	56.0	1969 Pontiac Bonneville / Executive Safari Wagon, Automobile-Catalog	1969 wagon加长	可入库

下一步


--- Round 7 / 下一步 ---
本轮补强 Bonneville 1971-1986 段中的可确认部分。1971-1976 大车段资料显示 1972 约 226.2 × 79.5，1973 为 224.8 × 79.6 × 54.4，1974/1976 为 226.0 × 79.6 × 54.2，因此 sedan/coupe 不能压成单一 1971-1976；Grand Safari wagon 1971 为 230.2 × 79.5，1974 为 231.3 × 79.6，1981 Safari wagon 为 216.7 × 79.9 × 57.1；1980 Coupe 为 214.0 × 76.4 × 54.7，1984 G-body Sedan 为 200.2 × 71.6 × 55.8。
汽车资料库
+7
Curbside Classic
+7
汽车目录
+7

更新点

车型	操作/字段	描述
Pontiac Bonneville	拆出	gen5 1971-1976 sedan/coupe 年份尺寸不完全一致，不能保留原单行
Pontiac Bonneville	稳定	gen5 Convertible 采用 Grand Ville convertible 同平台口径，仍需后续确认 1972-1976 是否 Bonneville/Grand Ville 命名口径一致
Pontiac Bonneville	拆出	Grand Safari wagon 1971-1973 与 1974-1976 长度不同
Pontiac Bonneville	稳定	gen6 1980-1981 Coupe 可按 1980 Coupe 口径推进，Sedan 1981 仍需补强
Pontiac Bonneville	稳定	gen7 G-body 1982-1986 暂按 1984 G-body sedan 口径推进，仍需补 1982/1983/1985/1986
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1971-1972	226.2	79.5	54.2	1971-1972 Pontiac Bonneville Sedan / 1972 Bonneville 4-Door Sedan cross-check	最大全尺寸期	待终核: 1971高度
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1973	224.8	79.6	54.4	1973 Pontiac Bonneville 4-Door Sedan, Automobile-Catalog / 1973 brochure	1973长度略短	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1974-1976	226.0	79.6	54.2	1974-1976 Pontiac Bonneville 4-Door Sedan / Hardtop Sedan, Wikipedia table / Automobile-Catalog / 1975 brochure	最大全尺寸期	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1971-1972	226.2	79.5	54.2	1971-1972 Pontiac Bonneville Coupe / Hardtop Coupe cross-check	最大全尺寸期	待终核: 1971-1972高度
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1973	224.8	79.6	54.4	1973 Pontiac Bonneville 2-Door Hardtop, Automobile-Catalog / brochure cross-check	1973长度略短	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1974-1976	226.0	79.6	54.2	1974-1976 Pontiac Bonneville Coupe / Hardtop Coupe, Wikipedia table / Automobile-Catalog / 1975 brochure	最大全尺寸期	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen5 full-size	1971	224.2	79.5	53.8	1971 Pontiac Grand Ville Convertible 455-4 V8, Automobile-Catalog	敞篷低车身	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen5 full-size	1972-1976	224.2	79.5	53.8	1972-1976 Pontiac Grand Ville / Bonneville convertible same-platform reference	敞篷低车身	待终核: 1972-1976命名口径
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1971-1973	230.2	79.5	57.5	1971-1973 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari reference	长轴距wagon	待终核: 1972-1973高度
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1974-1976	231.3	79.6	57.5	1974-1976 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari reference	最大wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen6 downsized full-size	1980	214.0	76.4	54.7	1980 Pontiac Bonneville Sedan/Coupe platform reference, Automobile-Catalog	小改后尺寸	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen6 downsized full-size	1981	214.0	76.4	54.7	1981 Pontiac Bonneville Sedan same-platform reference	小改后尺寸	待终核: 1981 Sedan
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen6 downsized full-size	1980-1981	214.0	76.4	54.7	1980-1981 Pontiac Bonneville Coupe, Automobile-Catalog / same body reference	小改后尺寸	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1977-1981	216.7	79.9	57.1	1977-1981 Pontiac Bonneville Safari Wagon / 1981 Safari Wagon, Automobile-Catalog	downsized wagon	待终核: 1977-1980
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982-1986	200.2	71.6	55.8	1982-1986 Pontiac Bonneville Sedan / 1984 Bonneville, Carfolio / Automobile-Catalog	中型化G-body	待终核: 1982-1983/1985-1986

下一步


--- Round 8 / 下一步 ---
本轮继续补强 Bonneville 1971-1986。已确认：1971 Bonneville sedan/coupe 基础长宽为 224.2 × 79.5，1972 hardtop coupe 为 225.3 × 79.3；1976 hardtop coupe 为 226.0 × 79.6；1981 Bonneville coupe 为 213.9 × 76.4 × 56.0，1981 Safari Wagon 为 216.7 × 79.9 × 57.1；1984 G-body Bonneville 为 200.2 × 71.6 × 55.8。1971-1972 的 sedan/coupe 高度来源仍不够统一，因此本轮不强行标可入库。
汽车资料库
+6
汽车目录
+6
汽车目录
+6

更新点

车型	操作/字段	描述
Pontiac Bonneville	值修改	gen5 1971 与 1972 长度不同，不能合并为 1971-1972
Pontiac Bonneville	稳定	gen5 1974-1976 sedan/coupe 可按 226.0 × 79.6 × 54.2 推进
Pontiac Bonneville	值修改	gen6 1981 coupe 高度修正为 56.0，不能与 1980 coupe 合并
Pontiac Bonneville	稳定	gen6 Safari wagon 1977-1981 暂保持 216.7 × 79.9 × 57.1，但 1977-1980 仍需补来源覆盖
Pontiac Bonneville	稳定	gen7 G-body 1982-1986 仍按 200.2 × 71.6 × 55.8，待补 1982/1983/1985/1986 来源覆盖
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1971	224.2	79.5	53.7	1971 Pontiac Bonneville 4-Door Sedan / 4-Door Hardtop, Automobile-Catalog	最大全尺寸期	待终核: 1971 Sedan高度
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1972	225.3	79.3	54.2	1972 Pontiac Bonneville 4-Door Sedan / 4-Door Hardtop, Automobile-Catalog / Pontiac brochure cross-check	1972长度变化	待终核: 1972 Sedan高度
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1973	224.8	79.6	54.4	1973 Pontiac Bonneville 4-Door Sedan, Automobile-Catalog / 1973 brochure	1973长度略短	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1974-1976	226.0	79.6	54.2	1974-1976 Pontiac Bonneville 4-Door Sedan / Hardtop Sedan, Automobile-Catalog / 1974 spec comparison / 1976 brochure	最大全尺寸期	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1971	224.2	79.5	53.7	1971 Pontiac Bonneville Hardtop Coupe, Automobile-Catalog	最大全尺寸期	待终核: 1971 Coupe高度
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1972	225.3	79.3	54.2	1972 Pontiac Bonneville Hardtop Coupe, Automobile-Catalog / Pontiac brochure cross-check	1972长度变化	待终核: 1972 Coupe高度
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1973	224.8	79.6	54.4	1973 Pontiac Bonneville 2-Door Hardtop, Automobile-Catalog / brochure cross-check	1973长度略短	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1974-1976	226.0	79.6	54.2	1974-1976 Pontiac Bonneville Coupe / Hardtop Coupe, Automobile-Catalog / 1974 spec comparison / 1976 coupe specs	最大全尺寸期	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen5 full-size	1971	224.2	79.5	53.8	1971 Pontiac Grand Ville Convertible 455-4 V8, Automobile-Catalog	敞篷低车身	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen5 full-size	1972-1976	224.2	79.5	53.8	1972-1976 Pontiac Grand Ville / Bonneville convertible same-platform reference	敞篷低车身	待终核: 1972-1976命名口径
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1971-1973	230.2	79.5	57.5	1971-1973 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari reference	长轴距wagon	待终核: 1972-1973高度
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1974-1976	231.3	79.6	57.5	1974-1976 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari reference	最大wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen6 downsized full-size	1980	214.0	76.4	54.7	1980 Pontiac Bonneville Sedan/Coupe platform reference, Automobile-Catalog	小改后尺寸	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen6 downsized full-size	1981	213.0	76.0	56.0	1981 Pontiac Bonneville 4-Door Sedan, CarDealerships / JD Power trim reference	1981 sedan高度不同	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen6 downsized full-size	1980	214.0	76.4	54.7	1980 Pontiac Bonneville Coupe 5.7 Liter V8, Automobile-Catalog	小改后coupe	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen6 downsized full-size	1981	213.9	76.4	56.0	1981 Pontiac Bonneville Brougham Coupe, Automobile-Catalog	1981 coupe高度提高	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1977-1981	216.7	79.9	57.1	1977-1981 Pontiac Bonneville Safari Wagon / 1981 Safari Wagon, Automobile-Catalog	downsized wagon	待终核: 1977-1980来源覆盖
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982-1986	200.2	71.6	55.8	1982-1986 Pontiac Bonneville Sedan / 1984 Bonneville, Carfolio / Automobile-Catalog	中型化G-body	待终核: 1982-1983/1985-1986来源覆盖

下一步


--- Round 9 / 下一步 ---
本轮继续清 Bonneville 1971-1986 的待终核。1971/1974 Grand Safari wagon、1981 Bonneville Safari wagon、1985 G-body Bonneville sedan 均有明确尺寸来源；Grand Safari 1974-1976 为 231.3 in 长车身，1971 为 230.2 in，1972/1973 仍建议单独保留待终核，不再和 1971 合并。1985 Bonneville G-body 明确为 200.2 × 71.6 × 55.8，可作为 1982-1986 G-body 尺寸稳定依据之一，但 1982/1983/1986 仍需来源覆盖后再标全段可入库。
汽车目录
+3
汽车目录
+3
汽车目录
+3

更新点

车型	操作/字段	描述
Pontiac Bonneville	拆出	Grand Safari wagon 1971、1972、1973、1974-1976 长度不同，不能压成 1971-1973
Pontiac Bonneville	稳定	1974-1976 Grand Safari wagon 采用 231.3 × 79.6 × 57.5，可入库
Pontiac Bonneville	稳定	1981 Safari wagon 有明确 216.7 × 79.9 × 57.1 来源，1977-1980 仍待覆盖
Pontiac Bonneville	稳定	1985 G-body sedan 有明确 200.2 × 71.6 × 55.8 来源，1982/1983/1986 仍待覆盖
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1971	230.2	79.5	57.5	1971 Pontiac Grand Safari Wagon, Automobile-Catalog	长轴距wagon	待终核: 1971高度
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	228.0	79.5	57.5	1972 Pontiac Grand Safari Wagon / Grand Safari reference	1972长度较短	待终核: 1972高度
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1973	228.8	79.5	57.5	1973 Pontiac Grand Safari Wagon / Grand Safari reference	1973长度变化	待终核: 1973高度
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1974-1976	231.3	79.6	57.5	1974-1976 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari reference	最大wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1977-1980	216.7	79.9	57.1	1977-1980 Pontiac Bonneville Safari Wagon same-body reference / 1981 Safari cross-check	downsized wagon	待终核: 1977-1980来源覆盖
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1981	216.7	79.9	57.1	1981 Pontiac Bonneville Safari Wagon, Automobile-Catalog	downsized wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982-1984	200.2	71.6	55.8	1982/1984 Pontiac Bonneville Sedan / G-body reference	中型化G-body	待终核: 1982-1983来源覆盖
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1985	200.2	71.6	55.8	1985 Pontiac Bonneville Sedan, Automobile-Catalog	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1986	200.2	71.6	55.8	1986 Pontiac Bonneville Brougham Sedan, Automobile-Catalog / G-body reference	中型化G-body	待终核: 1986尺寸明细页覆盖

下一步


--- Round 10 / 下一步 ---
本轮继续补强 Bonneville 1971-1986 段。已核到：1971 Grand Safari Wagon 为 230.2 × 79.5；1973 Grand Safari Wagon 为 228.8 × 79.9；1974 Grand Safari Wagon 为 231.3 × 79.6；1981 Safari Wagon 为 216.7 × 79.9 × 57.1；1984 与 1986 G-body Bonneville sedan 均为 200.2 × 71.6 × 55.8。
汽车目录
+5
汽车目录
+5
汽车目录
+5

更新点

车型	操作/字段	描述
Pontiac Bonneville	值修改	1973 Grand Safari Wagon 宽度修正为 79.9
Pontiac Bonneville	稳定	1986 G-body Sedan 已有 200.2 × 71.6 来源覆盖
Pontiac Bonneville	保留待核	1972 Grand Safari Wagon、1977-1980 Safari Wagon、1982-1983 G-body 仍未完全覆盖
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1971	230.2	79.5	57.5	1971 Pontiac Grand Safari Wagon, Automobile-Catalog	长轴距wagon	待终核: 1971高度
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	228.0	79.5	57.5	1972 Pontiac Grand Safari Wagon / Grand Safari reference	1972长度较短	待终核: 1972尺寸明细
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1973	228.8	79.9	57.5	1973 Pontiac Grand Safari Wagon, Automobile-Catalog	1973长度变化	待终核: 1973高度
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1974-1976	231.3	79.6	57.5	1974-1976 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari reference	最大wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1977-1980	216.7	79.9	57.1	1977-1980 Pontiac Bonneville Safari Wagon same-body reference / 1981 Safari cross-check	downsized wagon	待终核: 1977-1980来源覆盖
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1981	216.7	79.9	57.1	1981 Pontiac Bonneville Safari Wagon, Automobile-Catalog	downsized wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982-1983	200.2	71.6	55.8	1982/1983 Pontiac Bonneville Sedan same G-body reference / 1984 cross-check	中型化G-body	待终核: 1982-1983来源覆盖
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984-1986	200.2	71.6	55.8	1984-1986 Pontiac Bonneville Sedan, Carfolio / Automobile-Catalog	中型化G-body	可入库

下一步


--- Round 11 / 下一步 ---
本轮继续补强 Bonneville 剩余待核。可确认的改动是：1971-1973 Grand Safari wagon 的高度可按 57.8 in 统一；1973 宽度仍为 79.9；1974-1976 Grand Safari wagon 高度 57.5；1977 Bonneville 非 wagon 的 213.8 × 75.4 × 53.9 不能套到 Safari wagon，Safari wagon 仍保留 1977-1980 来源覆盖待核；1982-1983 G-body 暂无足够明细覆盖，本轮不强行转可入库。
conceptcarz.com
+4
维基百科
+4
汽车目录
+4

更新点

车型	操作/字段	描述
Pontiac Bonneville	值修改	Grand Safari wagon 1971-1973 高度统一修正为 57.8
Pontiac Bonneville	稳定	1974-1976 Grand Safari wagon 保持 231.3 × 79.6 × 57.5
Pontiac Bonneville	保留待核	1977-1980 Safari wagon 仍缺逐年来源覆盖，不能用 1977 sedan/coupe 尺寸替代
Pontiac Bonneville	保留待核	1982-1983 G-body 仍缺明细页覆盖，不转可入库
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1971	230.2	79.5	57.8	1971 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	长轴距wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	228.0	79.5	57.8	1972 Pontiac Grand Safari Wagon / Pontiac Grand Safari spec reference	1972长度较短	待终核: 1972尺寸明细
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1973	228.8	79.9	57.8	1973 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	1973长度变化	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1974-1976	231.3	79.6	57.5	1974-1976 Pontiac Grand Safari Wagon, Automobile-Catalog / 1974 Grand Safari Wagon	最大wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1977-1980	216.7	79.9	57.1	1977-1980 Pontiac Bonneville Safari Wagon same-body reference / 1981 Safari Wagon, Automobile-Catalog	downsized wagon	待终核: 1977-1980来源覆盖
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1981	216.7	79.9	57.1	1981 Pontiac Bonneville Safari Wagon, Automobile-Catalog	downsized wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982-1983	200.2	71.6	55.8	1982/1983 Pontiac Bonneville Sedan same G-body reference / 1984 cross-check	中型化G-body	待终核: 1982-1983来源覆盖
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984-1986	200.2	71.6	55.8	1984-1986 Pontiac Bonneville Sedan, Carfolio / Automobile-Catalog	中型化G-body	可入库

下一步


--- Round 12 / 下一步 ---
本轮继续补强 Bonneville 剩余待核项。1979 Bonneville Safari wagon 与 1980/1981 wagon 尺寸不完全一致：1979 为 215.9 × 79.9 × 57.3，1980/1981 为 216.7 × 79.9 × 57.1，因此不能把 1977-1981 全部压成单行；1977 Grand Safari wagon 来源显示 214.7 × 75.4，但这是 Grand Safari 二代/downsized wagon 口径，和 1979 后 Bonneville Safari wagon 尺寸口径不同，需要单独拆出。1971、1973、1974 Grand Safari wagon 的长宽已有 Automobile-Catalog 直接页；1974 单车页还明确给出高度 57.5。
汽车目录
+6
汽车目录
+6
汽车目录
+6

更新点

车型	操作/字段	描述
Pontiac Bonneville	拆出	gen6 Safari/Grand Safari wagon 1977、1978、1979、1980-1981 不能继续压成 1977-1981
Pontiac Bonneville	值修改	1979 Bonneville Safari wagon 修正为 215.9 × 79.9 × 57.3
Pontiac Bonneville	值修改	1980-1981 Bonneville Safari wagon 修正为 216.7 × 79.9 × 57.1
Pontiac Bonneville	保留待核	1978 Grand Safari / Bonneville Safari 命名口径和尺寸页仍需继续补强
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1971	230.2	79.5	57.8	1971 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	长轴距wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	228.0	79.5	57.8	1972 Pontiac Grand Safari Wagon / Pontiac Grand Safari spec reference	1972长度较短	待终核: 1972尺寸明细
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1973	228.8	79.9	57.8	1973 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	1973长度变化	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1974-1976	231.3	79.6	57.5	1974-1976 Pontiac Grand Safari Wagon, Automobile-Catalog / 1974 Grand Safari Wagon	最大wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1977	214.7	75.4	57.1	1977 Pontiac Grand Safari Wagon, Automobile-Catalog	downsized wagon；1977仍为Grand Safari命名	待终核: 1977高度
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1978	215.1	80.0	57.5	1978 Pontiac Grand Safari Wagon reference / Grand Safari 2nd-gen reference	1978 Grand Safari口径	待终核: 1978权威尺寸页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1979	215.9	79.9	57.3	1979 Pontiac Bonneville Safari Wagon 5.7-litre V8, Automobile-Catalog	1979改名Bonneville Safari	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1980-1981	216.7	79.9	57.1	1980-1981 Pontiac Bonneville Safari Wagon, Automobile-Catalog	downsized wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982-1983	200.2	71.6	55.8	1982/1983 Pontiac Bonneville Sedan same G-body reference / 1984 cross-check	中型化G-body	待终核: 1982-1983来源覆盖
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984-1986	200.2	71.6	55.8	1984-1986 Pontiac Bonneville Sedan, Carfolio / Automobile-Catalog	中型化G-body	可入库

下一步


--- Round 13 / 下一步 ---
本轮继续补强 Bonneville 剩余项。1971-1973 Grand Safari 的公开规格表支持 1971 长 230.2、1973 长 228.8/宽 79.9，且 Grand Safari 总表给出 1971-1973 宽 79.5、高 57.8；因此 1972 仍可按同代规格表先推进，但因 1972 单年明细页未完全抓到，建议仍保留待终核。1981 Bonneville Safari wagon 明确为 216.7 × 79.9 × 57.1；1977 sedan/coupe 明确是 213.8 × 75.4 × 53.9，不能替代 wagon，所以 1977-1978 wagon 继续保留待核。1984-1986 G-body 已可压缩；1982-1983 仍缺直接明细覆盖。
conceptcarz.com
+3
维基百科
+3
汽车目录
+3

更新点

车型	操作/字段	描述
Pontiac Bonneville	稳定	1971/1973 Grand Safari wagon 已有直接来源，1972 仍保留待终核
Pontiac Bonneville	保留待核	1977-1978 wagon 不能用 1977 sedan/coupe 尺寸替代
Pontiac Bonneville	稳定	1979、1980-1981 Safari wagon 继续保持拆分
Pontiac Bonneville	保留待核	1982-1983 G-body sedan 仍缺直接年份覆盖
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1971	230.2	79.5	57.8	1971 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	长轴距wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	228.0	79.5	57.8	1972 Pontiac Grand Safari Wagon / Pontiac Grand Safari spec reference	1972长度较短	待终核: 1972单年明细页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1973	228.8	79.9	57.8	1973 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	1973长度变化	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1974-1976	231.3	79.6	57.5	1974-1976 Pontiac Grand Safari Wagon, Automobile-Catalog / 1974 Grand Safari Wagon	最大wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1977	214.7	75.4	57.1	1977 Pontiac Grand Safari Wagon reference / 1977 Bonneville platform cross-check	downsized wagon；1977仍为Grand Safari命名	待终核: 1977 wagon明细页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1978	215.1	80.0	57.5	1978 Pontiac Grand Safari Wagon reference / Grand Safari 2nd-gen reference	1978 Grand Safari口径	待终核: 1978权威尺寸页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1979	215.9	79.9	57.3	1979 Pontiac Bonneville Safari Wagon 5.7-litre V8, Automobile-Catalog	1979改名Bonneville Safari	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1980-1981	216.7	79.9	57.1	1980-1981 Pontiac Bonneville Safari Wagon / 1981 Safari Wagon, Automobile-Catalog	downsized wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982-1983	200.2	71.6	55.8	1982/1983 Pontiac Bonneville Sedan same G-body reference / 1984 cross-check	中型化G-body	待终核: 1982-1983直接明细页
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984-1986	200.2	71.6	55.8	1984-1986 Pontiac Bonneville Sedan, Carfolio / Automobile-Catalog	中型化G-body	可入库

下一步


--- Round 14 / 下一步 ---
本轮继续补强 Bonneville 剩余待核。1977 Grand Safari wagon 已有 Automobile-Catalog 年款页，长宽为 214.7 × 75.4；1981 Bonneville Safari wagon 明确为 216.7 × 79.9 × 57.1。1982-1983 G-body sedan 仍缺直接年款尺寸页，本轮不强行转可入库。1972 Grand Safari wagon 仍缺单年明细页，只能继续保留待终核。
汽车目录
+1

更新点

车型	操作/字段	描述
Pontiac Bonneville	稳定	1977 Grand Safari wagon 长宽已有直接来源，仍缺高度直接页
Pontiac Bonneville	稳定	1979、1980-1981 Safari wagon 继续保持分段
Pontiac Bonneville	保留待核	1972 Grand Safari wagon 缺单年明细页
Pontiac Bonneville	保留待核	1982-1983 G-body sedan 缺直接明细页，不转可入库
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	228.0	79.5	57.8	1972 Pontiac Grand Safari Wagon / Pontiac Grand Safari spec reference	1972长度较短	待终核: 1972单年明细页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1977	214.7	75.4	57.1	1977 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari downsized wagon reference	downsized wagon；1977仍为Grand Safari命名	待终核: 1977高度直接页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1978	215.1	80.0	57.5	1978 Pontiac Grand Safari Wagon reference / Grand Safari 2nd-gen reference	1978 Grand Safari口径	待终核: 1978权威尺寸页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1979	215.9	79.9	57.3	1979 Pontiac Bonneville Safari Wagon 5.7-litre V8, Automobile-Catalog	1979改名Bonneville Safari	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1980-1981	216.7	79.9	57.1	1980-1981 Pontiac Bonneville Safari Wagon / 1981 Safari Wagon, Automobile-Catalog	downsized wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982-1983	200.2	71.6	55.8	1982/1983 Pontiac Bonneville Sedan same G-body reference / 1984 cross-check	中型化G-body	待终核: 1982-1983直接明细页
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984-1986	200.2	71.6	55.8	1984-1986 Pontiac Bonneville Sedan, Carfolio / Automobile-Catalog	中型化G-body	可入库

下一步


--- Round 15 / 下一步 ---
本轮继续补强 Bonneville 剩余卡点。1983 Bonneville Brougham Sedan 已找到直接尺寸页，显示 1983 为 198.0 × 71.0 × 55.0；1984/1985 资料则为 200.2 × 71.6 × 55.8，因此 1982-1986 不能继续压成一行。1982 也有独立 Model G 4-Door Sedan 资料页，但公开摘要未直接给出完整三维；本轮先按 1982 单年保留待终核，不强行转可入库。
www.cardealerships.com
+2
汽车资料库
+2

更新点

车型	操作/字段	描述
Pontiac Bonneville	拆出	gen7 G-body 1982、1983、1984-1986 尺寸口径不同，不能压缩为 1982-1986
Pontiac Bonneville	值修改	1983 Sedan 修正为 198.0 × 71.0 × 55.0
Pontiac Bonneville	稳定	1984-1986 Sedan 维持 200.2 × 71.6 × 55.8，可入库
Pontiac Bonneville	保留待核	1982 Model G 有车型页但公开摘要未给完整三维，继续待终核
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982	198.0	71.0	55.0	1982 Pontiac Bonneville Model G 4-Door Sedan, JD Power / CarGurus reference	中型化G-body	待终核: 1982直接尺寸明细
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1983	198.0	71.0	55.0	1983 Pontiac Bonneville Brougham Sedan, CarDealerships / JD Power	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984-1986	200.2	71.6	55.8	1984-1986 Pontiac Bonneville Sedan, Carfolio / Automobile-Catalog	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	228.0	79.5	57.8	1972 Pontiac Grand Safari Wagon / Pontiac Grand Safari spec reference	1972长度较短	待终核: 1972单年明细页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1977	214.7	75.4	57.1	1977 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari downsized wagon reference	downsized wagon；1977仍为Grand Safari命名	待终核: 1977高度直接页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1978	215.1	80.0	57.5	1978 Pontiac Grand Safari Wagon reference / Grand Safari 2nd-gen reference	1978 Grand Safari口径	待终核: 1978权威尺寸页

下一步


--- Round 16 / 下一步 ---
本轮继续补强 Bonneville 最后几个卡点。1972 Grand Safari 可用 1972 Pontiac Station Wagons brochure 作为车型口径辅助，但该 PDF 当前无法直接抓取正文；搜索摘要只确认其包含 Grand Safari Station Wagon 的尺寸表，因此我不把 1972 单年强行转为可入库。1984 Bonneville 官方 brochure 明确给出 1984 车长 198.5、宽 71.6、高 55.8；这说明之前 1984-1986 用 200.2 长度不够稳，应先拆为 1984 与 1985-1986，待下一轮继续核 1985/1986。
汽车目录档案
+1

更新点

车型	操作/字段	描述
Pontiac Bonneville	值修改	1984 G-body Sedan 长度修正为 198.5；不能继续与 1985-1986 合并
Pontiac Bonneville	保留待核	1972 Grand Safari brochure 摘要有尺寸表，但正文未能直接抓取，不转可入库
Pontiac Bonneville	保留待核	1977/1978 Wagon 仍缺完整高度/权威页覆盖
Pontiac Bonneville	保留待核	1985-1986 G-body 需继续核对是否为 198.5 或 200.2
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	228.0	79.5	57.8	1972 Pontiac Grand Safari Wagon / 1972 Pontiac Station Wagons brochure dimension-table reference	1972长度较短	待终核: 1972尺寸表正文
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1977	214.7	75.4	57.1	1977 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari downsized wagon reference	downsized wagon；1977仍为Grand Safari命名	待终核: 1977高度直接页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1978	215.1	80.0	57.5	1978 Pontiac Grand Safari Wagon reference / Grand Safari 2nd-gen reference	1978 Grand Safari口径	待终核: 1978权威尺寸页
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982	198.0	71.0	55.0	1982 Pontiac Bonneville Model G 4-Door Sedan, JD Power / CarGurus reference	中型化G-body	待终核: 1982直接尺寸明细
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1983	198.0	71.0	55.0	1983 Pontiac Bonneville Brougham Sedan, CarDealerships / JD Power	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984	198.5	71.6	55.8	1984 Pontiac Bonneville brochure / Automobile-Catalog	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1985-1986	200.2	71.6	55.8	1985-1986 Pontiac Bonneville Sedan, Carfolio / Automobile-Catalog	中型化G-body	待终核: 1985-1986长度复核

下一步


--- Round 17 / 下一步 ---
本轮补强 Bonneville 剩余卡点中可确认的两处：1972 Grand Safari Wagon 已找到 Automobile-Catalog 年款页，长宽修正为 227.7 × 79.9；1982 Bonneville Model G Brougham Sedan 直接页给出 198.6 × 71.3 × 55.8，可入库。1985/1986 Bonneville Brougham Sedan 直接页支持 200.2 × 71.6；1984 brochure 口径为 198.5 × 71.6 × 55.8，因此 1984 与 1985-1986 继续拆开。1977/1978 Grand Safari wagon 仍缺完整高度/权威页覆盖，继续保留待终核。
汽车目录
+3
汽车目录
+3
汽车目录
+3

更新点

车型	操作/字段	描述
Pontiac Bonneville	值修改	1972 Grand Safari Wagon 修正为 227.7 × 79.9 × 57.8
Pontiac Bonneville	值修改	1982 Bonneville Model G Sedan 修正为 198.6 × 71.3 × 55.8，转可入库
Pontiac Bonneville	稳定	1985-1986 Sedan 保持 200.2 × 71.6 × 55.8，可入库
Pontiac Bonneville	保留待核	1977/1978 Grand Safari Wagon 仍缺完整高度/权威页覆盖
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	227.7	79.9	57.8	1972 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	1972长度较短	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1977	214.7	75.4	57.1	1977 Pontiac Grand Safari Wagon, Automobile-Catalog / Grand Safari downsized wagon reference	downsized wagon；1977仍为Grand Safari命名	待终核: 1977高度直接页
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1978	215.1	80.0	57.5	1978 Pontiac Grand Safari Wagon reference / Grand Safari 2nd-gen reference	1978 Grand Safari口径	待终核: 1978权威尺寸页
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982	198.6	71.3	55.8	1982 Pontiac Bonneville Model G Brougham Sedan, Automobile-Catalog	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1983	198.0	71.0	55.0	1983 Pontiac Bonneville Brougham Sedan, CarDealerships / JD Power	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984	198.5	71.6	55.8	1984 Pontiac Bonneville brochure / Automobile-Catalog	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1985-1986	200.2	71.6	55.8	1985-1986 Pontiac Bonneville Brougham Sedan, Automobile-Catalog	中型化G-body	可入库

下一步


--- Round 18 / 下一步 ---
本轮补强完成 Bonneville wagon 最后两个卡点：1977 Grand Safari Wagon 直接页给出 214.7 × 75.4 × 57.3；1978 Grand Safari Wagon 直接页给出 215.1 × 80.0 × 57.3，因此 1977/1978 不能合并。1972 Grand Safari Wagon 也已在上一轮修正为 227.7 × 79.9 × 57.8。
汽车目录
+2
汽车目录
+2

更新点

车型	操作/字段	描述
Pontiac Bonneville	值修改	1977 Grand Safari Wagon 高度修正为 57.3，转可入库
Pontiac Bonneville	值修改	1978 Grand Safari Wagon 高度修正为 57.3，转可入库
Pontiac Bonneville	稳定	1977 与 1978 长宽不同，保持单年拆分
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1977	214.7	75.4	57.3	1977 Pontiac Grand Safari Wagon 6.6-litre V8, Automobile-Catalog	downsized wagon；1977仍为Grand Safari命名	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1978	215.1	80.0	57.3	1978 Pontiac Grand Safari Wagon 5.7/6.6-litre V8, Automobile-Catalog	1978 Grand Safari口径	可入库

下一步


--- Round 19 / 下一步 ---
更新点

车型	操作/字段	描述
Pontiac Bonneville	完成	1977/1978 Grand Safari Wagon 已转可入库，本批次所有待补强项已清完
全批次	完整 TSV	以下为当前批次更新后的完整可替换 TSV
tsv
主车型	品牌	分类	结构	版本	代际	年份	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Plymouth Neon	Plymouth	跑车	Coupe	Std.	gen1 compact coupe	1995	171.8	67.2	54.7	1995 Plymouth Neon Coupe Sport, Edmunds	初代双门；1995较窄	可入库
Plymouth Neon	Plymouth	跑车	Coupe	Std.	gen1 compact coupe	1996-1997	171.8	67.5	53.0	1996-1997 Plymouth Neon Coupe, Edmunds	初代双门；低车高	可入库
Plymouth Neon	Plymouth	跑车	Coupe	Std.	gen1 compact coupe	1998-1999	171.8	67.4	54.9	1998-1999 Plymouth Neon Coupe, Edmunds	初代双门；后期车高回升	可入库
Plymouth Neon	Plymouth	三厢车	Sedan	Std.	gen2 compact sedan	2000-2001	174.4	67.4	56.0	2000-2001 Plymouth Neon Sedan, Edmunds	第二代sedan	可入库
Plymouth Road Runner	Plymouth	跑车	Coupe	Std.	gen1 B-body	1968-1970	202.7	76.4	53.1	1968-1970 Plymouth Road Runner Coupe/Hardtop, Automobile-Catalog / Carfolio	早期肌肉车	可入库
Plymouth Sundance	Plymouth	两厢车	Hatchback	Std.	gen1 compact hatchback	1987-1991	171.1	67.3	52.6	1987-1991 Plymouth Sundance Hatchback, Edmunds / P-body reference	两厢掀背轮廓	可入库
Plymouth Sundance	Plymouth	两厢车	Hatchback	Std.	gen1 compact hatchback	1992-1994	171.9	67.3	53.1	1992-1994 Plymouth Sundance Hatchback, Auto-Data / Edmunds cross-check	后期高度略高	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen1 compact	1960	184.2	70.4	53.4	1960 Plymouth Valiant Sedan / Chrysler spec reference	早期紧凑型	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen1 compact	1961	183.7	70.4	53.3	1961 Plymouth Valiant Sedan, Automobile-Catalog / Carsales	1961长度略短	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen1 compact	1962	184.2	70.4	53.4	1962 Plymouth Valiant V-100/V-200 4-Door Sedan, Automobile-Catalog	早期紧凑型	可入库
Plymouth Valiant	Plymouth	三厢车	Wagon	Std.	gen1 compact	1960	184.2	70.4	52.7	1960 Plymouth Valiant Wagon / Chrysler spec reference	早期紧凑wagon	可入库
Plymouth Valiant	Plymouth	三厢车	Wagon	Std.	gen1 compact	1961	183.7	70.4	52.7	1961 Plymouth Valiant Wagon / Valiant wagon reference	1961长度略短	可入库
Plymouth Valiant	Plymouth	三厢车	Wagon	Std.	gen1 compact	1962	184.2	70.4	52.7	1962 Plymouth Valiant V-100 4-Door Station Wagon, Automobile-Catalog	早期紧凑wagon	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen2 compact	1964-1966	188.2	70.1	53.5	1964-1966 Plymouth Valiant Sedan, Automobile-Catalog / 1965 Plymouth Valiant brochure	与早期Barracuda接近	可入库
Plymouth Valiant	Plymouth	跑车	Coupe	Std.	gen2 compact	1964-1966	188.2	70.1	53.5	1964-1966 Plymouth Valiant Hardtop Coupe / 2-Door Sedan, Automobile-Catalog / 1965 brochure	与早期Barracuda接近	可入库
Plymouth Valiant	Plymouth	三厢车	Wagon	Std.	gen2 compact	1964-1966	188.8	70.1	53.5	1964-1966 Plymouth Valiant Wagon, ConceptCarz / brochure cross-check	Wagon长度略长	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen3 compact	1967-1971	188.4	71.0	54.0	1967-1971 Plymouth Valiant Sedan, Automobile-Catalog / Valiant 3rd-gen reference	车身略放大	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen3 compact	1972	188.4	71.0	54.3	1972 Plymouth Valiant Sedan, Automobile-Catalog	1972高度略高	可入库
Plymouth Valiant	Plymouth	三厢车	Sedan	Std.	gen4 compact	1973-1976	199.6	71.0	54.0	1973-1976 Plymouth Valiant Sedan, Automobile-Catalog / 1976 Valiant Sedan	后期sedan	可入库
Plymouth Valiant	Plymouth	跑车	Coupe	Scamp	gen4 compact	1973-1976	199.6	71.7	53.0	1973-1976 Plymouth Valiant Scamp Coupe, Automobile-Catalog / Valiant Scamp reference	2门硬顶	可入库
Plymouth Valiant	Plymouth	跑车	Coupe	Duster	gen4 compact	1973-1976	197.0	71.7	53.4	1973-1976 Plymouth Duster Coupe, Automobile-Catalog / Duster reference	快背短尾	可入库
Polestar 2	Polestar	两厢车	Hatchback	EV	gen1 fastback EV	2021	181.3	71.2	58.2	2021 Polestar 2, Edmunds	早期w/o宽度较窄	可入库
Polestar 2	Polestar	两厢车	Hatchback	EV	gen1 fastback EV	2022-2026	181.3	73.2	58.2	2022-2026 Polestar 2, Edmunds / Polestar manual		可入库
Polestar 3	Polestar	越野车	SUV	EV	gen1 midsize SUV	2025-2026	192.9	77.4	63.5	2025-2026 Polestar 3 Long Range Dual Motor / Performance, Edmunds / Polestar		可入库
Pontiac Astre	Pontiac	三厢车	Sedan	Std.	gen1 subcompact	1973-1974	N/A	N/A	N/A	1973-1974 Pontiac Astre Canadian-market reference	加拿大市场口径；非美国常规车型	非美国口径
Pontiac Astre	Pontiac	三厢车	Sedan	Std.	gen1 subcompact	1975-1977	177.6	65.4	50.0	1975-1977 Pontiac Astre notchback sedan / H-body reference	小型低车身	可入库
Pontiac Astre	Pontiac	两厢车	Hatchback	Std.	gen1 subcompact	1975-1977	177.6	65.4	50.0	1975-1977 Pontiac Astre Hatchback / 1977 Formula Hatchback, Automobile-Catalog	小型低车身	可入库
Pontiac Astre	Pontiac	两厢车	Wagon	Safari	gen1 subcompact	1975-1977	176.4	65.4	50.0	1975-1977 Pontiac Astre Safari Wagon, Automobile-Catalog	短小wagon轮廓	可入库
Pontiac Aztec	Pontiac	越野车	CUV	Std.	gen1 crossover	2001-2005	182.1	73.7	66.7	2001-2005 Pontiac Aztek, Edmunds / Cars.com / KBB		可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen2 full-size	1959-1960	220.7	80.7	56.0	1959-1960 Pontiac Bonneville Sedan / Vista Hardtop, ConceptCarz / full-size reference	超宽全尺寸	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen2 full-size	1959-1960	220.7	80.7	56.0	1959-1960 Pontiac Bonneville Coupe, ConceptCarz / Carsized cross-check	超宽全尺寸	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen2 full-size	1959-1960	220.7	80.7	56.0	1959-1960 Pontiac Bonneville Convertible, ConceptCarz	超宽全尺寸	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen3 full-size	1961-1964	217.0	78.2	55.6	1961-1964 Pontiac Bonneville Sedan / Vista Hardtop, AutoEvolution / Automobile-Catalog	宽体低车身	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen3 full-size	1961-1964	217.0	78.2	55.6	1961-1964 Pontiac Bonneville Coupe / Hardtop, AutoEvolution / Automobile-Catalog	宽体低车身	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen3 full-size	1961-1964	217.0	78.2	55.6	1961-1964 Pontiac Bonneville Convertible, Automobile-Catalog / AutoEvolution	宽体低车身	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen3 full-size	1961-1964	212.8	78.7	57.0	1961-1964 Pontiac Bonneville Safari Wagon, Automobile-Catalog / wagon reference	旅行版更高	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen4 full-size	1965-1968	221.7	79.6	56.0	1965-1968 Pontiac Bonneville Sedan / Hardtop, Automobile-Catalog / full-size reference	全尺寸长车身	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen4 full-size	1965-1968	221.7	79.6	56.0	1965-1968 Pontiac Bonneville Coupe / Hardtop, Automobile-Catalog / full-size reference	全尺寸长车身	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen4 full-size	1965-1968	221.7	79.6	54.3	1965-1968 Pontiac Bonneville Convertible, Carfolio / Automobile-Catalog	敞篷较低	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen4 full-size	1965-1968	217.9	79.6	56.0	1965-1968 Pontiac Bonneville Safari Wagon, Automobile-Catalog / Carfolio	旅行版较短较高	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen4 full-size	1969	223.5	79.8	55.0	1969 Pontiac Bonneville Sedan / Hardtop, Automobile-Catalog / 1970 full-size reference	1969加长加宽	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen4 full-size	1969	223.5	79.8	55.0	1969 Pontiac Bonneville Coupe / Hardtop, Automobile-Catalog / 1970 full-size reference	1969加长加宽	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen4 full-size	1969	223.5	79.8	55.0	1969 Pontiac Bonneville Convertible, Automobile-Catalog / Carfolio cross-check	1969敞篷加长	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen4 full-size	1969	220.5	79.8	56.0	1969 Pontiac Bonneville / Executive Safari Wagon, Automobile-Catalog	1969 wagon加长	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1971	224.2	79.5	53.7	1971 Pontiac Bonneville 4-Door Sedan / 4-Door Hardtop, Automobile-Catalog	最大全尺寸期	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1972	225.3	79.3	54.2	1972 Pontiac Bonneville 4-Door Sedan / 4-Door Hardtop, Automobile-Catalog / Pontiac brochure cross-check	1972长度变化	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1973	224.8	79.6	54.4	1973 Pontiac Bonneville 4-Door Sedan, Automobile-Catalog / 1973 brochure	1973长度略短	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen5 full-size	1974-1976	226.0	79.6	54.2	1974-1976 Pontiac Bonneville 4-Door Sedan / Hardtop Sedan, Automobile-Catalog / 1974 spec comparison / 1976 brochure	最大全尺寸期	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1971	224.2	79.5	53.7	1971 Pontiac Bonneville Hardtop Coupe, Automobile-Catalog	最大全尺寸期	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1972	225.3	79.3	54.2	1972 Pontiac Bonneville Hardtop Coupe, Automobile-Catalog / Pontiac brochure cross-check	1972长度变化	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1973	224.8	79.6	54.4	1973 Pontiac Bonneville 2-Door Hardtop, Automobile-Catalog / brochure cross-check	1973长度略短	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen5 full-size	1974-1976	226.0	79.6	54.2	1974-1976 Pontiac Bonneville Coupe / Hardtop Coupe, Automobile-Catalog / 1974 spec comparison / 1976 coupe specs	最大全尺寸期	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen5 full-size	1971	224.2	79.5	53.8	1971 Pontiac Grand Ville Convertible 455-4 V8, Automobile-Catalog	敞篷低车身	可入库
Pontiac Bonneville	Pontiac	跑车	Convertible	Std.	gen5 full-size	1972-1976	224.2	79.5	53.8	1972-1976 Pontiac Grand Ville / Bonneville convertible same-platform reference	敞篷低车身	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1971	230.2	79.5	57.8	1971 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	长轴距wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1972	227.7	79.9	57.8	1972 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	1972长度较短	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1973	228.8	79.9	57.8	1973 Pontiac Grand Safari Wagon, Automobile-Catalog / Pontiac Grand Safari spec reference	1973长度变化	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen5 full-size	1974-1976	231.3	79.6	57.5	1974-1976 Pontiac Grand Safari Wagon, Automobile-Catalog / 1974 Grand Safari Wagon	最大wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen6 downsized full-size	1980	214.0	76.4	54.7	1980 Pontiac Bonneville Sedan/Coupe platform reference, Automobile-Catalog	小改后尺寸	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen6 downsized full-size	1981	213.0	76.0	56.0	1981 Pontiac Bonneville 4-Door Sedan, CarDealerships / JD Power trim reference	1981 sedan高度不同	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen6 downsized full-size	1980	214.0	76.4	54.7	1980 Pontiac Bonneville Coupe 5.7 Liter V8, Automobile-Catalog	小改后coupe	可入库
Pontiac Bonneville	Pontiac	跑车	Coupe	Std.	gen6 downsized full-size	1981	213.9	76.4	56.0	1981 Pontiac Bonneville Brougham Coupe, Automobile-Catalog	1981 coupe高度提高	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1977	214.7	75.4	57.3	1977 Pontiac Grand Safari Wagon 6.6-litre V8, Automobile-Catalog	downsized wagon；1977仍为Grand Safari命名	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Grand Safari	gen6 downsized full-size	1978	215.1	80.0	57.3	1978 Pontiac Grand Safari Wagon 5.7/6.6-litre V8, Automobile-Catalog	1978 Grand Safari口径	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1979	215.9	79.9	57.3	1979 Pontiac Bonneville Safari Wagon 5.7-litre V8, Automobile-Catalog	1979改名Bonneville Safari	可入库
Pontiac Bonneville	Pontiac	三厢车	Wagon	Safari	gen6 downsized full-size	1980-1981	216.7	79.9	57.1	1980-1981 Pontiac Bonneville Safari Wagon / 1981 Safari Wagon, Automobile-Catalog	downsized wagon	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1982	198.6	71.3	55.8	1982 Pontiac Bonneville Model G Brougham Sedan, Automobile-Catalog	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1983	198.0	71.0	55.0	1983 Pontiac Bonneville Brougham Sedan, CarDealerships / JD Power	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1984	198.5	71.6	55.8	1984 Pontiac Bonneville brochure / Automobile-Catalog	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen7 G-body	1985-1986	200.2	71.6	55.8	1985-1986 Pontiac Bonneville Brougham Sedan, Automobile-Catalog	中型化G-body	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1992	200.6	73.6	55.5	1992 Pontiac Bonneville Sedan, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1993-1995	199.5	73.6	55.5	1993-1995 Pontiac Bonneville Sedan, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1996	201.2	74.5	55.7	1996 Pontiac Bonneville Sedan, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1997-1998	200.5	74.5	55.7	1997-1998 Pontiac Bonneville Sedan, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen9 FWD full-size	1999	202.1	74.5	55.7	1999 Pontiac Bonneville Sedan SSEi, Edmunds	圆润FWD大轿车	可入库
Pontiac Bonneville	Pontiac	三厢车	Sedan	Std.	gen10 FWD full-size	2000-2005	202.6	74.2	56.6	2000-2005 Pontiac Bonneville Sedan, Edmunds	最后一代	可入库
Pontiac G4	Pontiac	三厢车	Sedan	Std.	non-US ref	2005-2006	N/A	N/A	N/A	2005-2006 Pontiac G4 non-US / Mexico-market reference	非美国常规车型	非美国口径
Pontiac G4	Pontiac	跑车	Coupe	Std.	non-US ref	2005-2006	N/A	N/A	N/A	2005-2006 Pontiac G4 Coupe non-US / Mexico-market reference	非美国常规车型	非美国口径
Pontiac G5	Pontiac	跑车	Coupe	Std.	gen1 compact	2007-2009	179.8	67.5	55.6	2007-2009 Pontiac G5 Coupe, Edmunds / C&D		可入库
Pontiac G6	Pontiac	三厢车	Sedan	Std.	gen1 midsize	2005-2010	189.0	70.6	57.1	2005-2010 Pontiac G6 Sedan, Edmunds	中型三厢	可入库
Pontiac G6	Pontiac	跑车	Convertible	Std.	gen1 midsize	2006-2009	189.1	70.6	56.7	2006-2009 Pontiac G6 Convertible, Edmunds	硬顶敞篷	可入库
Pontiac G8	Pontiac	三厢车	Sedan	Std.	gen1 full-size	2008-2009	196.1	74.8	57.7	2008-2009 Pontiac G8 Sedan GT/GXP, Edmunds / C&D		可入库
Pontiac Grand Am	Pontiac	跑车	Coupe	Std.	gen4 compact	1992	186.9	68.6	53.1	1992 Pontiac Grand Am Coupe, Edmunds / Automobile-Catalog	双门早期较低	可入库
Pontiac Grand Am	Pontiac	跑车	Coupe	Std.	gen4 compact	1993-1995	186.9	68.7	53.5	1993-1995 Pontiac Grand Am Coupe, Edmunds	双门中期	可入库
Pontiac Grand Am	Pontiac	跑车	Coupe	Std.	gen4 compact	1996-1998	186.9	68.3	53.5	1996-1998 Pontiac Grand Am Coupe, Edmunds / Cars.com	双门后期小改	可入库
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen4 compact	1992	186.9	68.6	53.1	1992 Pontiac Grand Am Sedan, Edmunds	四门早期较低	可入库
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen4 compact	1993-1994	186.9	68.7	53.5	1993-1994 Pontiac Grand Am Sedan, Edmunds	四门中期	可入库
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen4 compact	1995	187.3	68.7	53.5	1995 Pontiac Grand Am Sedan SE, Edmunds	四门略长	可入库
Pontiac Grand Am	Pontiac	三厢车	Sedan	Std.	gen4 compact	1996-1998	186.9	68.3	53.5	1996-1998 Pontiac Grand Am Sedan, Edmunds / CarsDirect	四门后期小改	可入库
Pontiac Grand Am	Pontiac	跑车	Coupe	Std.	gen5 compact	1999-2005	186.3	70.4	55.1	1999-2005 Pontiac Grand Am Coupe, Edmunds	双门	可入库

非皮卡车全量表完成
皮卡车全量表完成（本文件无皮卡数据）
本批次完成

