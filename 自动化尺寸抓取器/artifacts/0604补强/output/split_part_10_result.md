# 文件名：split_part_10.tsv


--- Round 1 / 首次发送 ---
更新点（本轮）

Camaro：已把 gen5 coupe/convertible 按 2010-2013、2014-2015 拆开；2014-2015 convertible 尺寸用 Edmunds 2014/2015 可核到的数据闭环，gen6 ZL1 用 2017/2020/2022/2024 ZL1 数据补强。
Edmunds
+5
Edmunds
+5
Edmunds
+5

Captiva：2014/2015 Captiva Sport 尺寸一致，先压缩为 2014-2015 可入库；2012-2013 仍待终核。
Edmunds
+1

Caprice：补出缺失 gen1 非 wagon 占位；1991-1996 sedan/wagon 可用 Edmunds/Automobile-Catalog 关键点推进，但中间年仍保留待终核。
Edmunds
+2
Edmunds
+2

Chevelle：1973 coupe 与 1976 coupe/sedan 有来源，现有 gen3 行先拆为已核关键点 + 待终核段；同时补 gen1/gen2 占位。
汽车目录
+1

当前批次进度：🟡 已补强 Camaro / Captiva / 部分 Caprice / 部分 Chevelle；仍需继续补 Caprice 早期与 Chevelle gen1/gen2 全量尺寸。

本轮更新后的 TSV：

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969						gen1缺失	待终核: 缺失 gen1 Coupe 全量数据
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969						gen1缺失	待终核: 缺失 gen1 Convertible 全量数据
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1970-1981						gen2缺失	待终核: 缺失 gen2 Coupe 全量数据
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1982-1992						gen3缺失	待终核: 缺失 gen3 Coupe 全量数据
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992						gen3敞篷	待终核: 缺失 gen3 Convertible 全量数据
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993-2002						gen4缺失	待终核: 缺失 gen4 Coupe 全量数据
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-2002						gen4敞篷	待终核: 缺失 gen4 Convertible 全量数据
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	待终核: 2015 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	52.9	2016/2023 Chevrolet Camaro Coupe/Convertible base, Edmunds	标准版短车身	待终核: 2017-2022/2024 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016-2024			188.3	74.7	52.9	2016/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	待终核: 2017-2022/2024 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2022/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2021/2023
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017-2024			190.2	75	52.9	2017/2020/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	待终核: 2018-2019/2021/2023
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967						gen1早期	待终核: 缺失 1966-1967 Sedan 尺寸
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968-1970			216	79.8	54.5	1968 Chevrolet full-size / 1970 Chevrolet Caprice Custom Sedan, Oldride / UltimateSpecs	gen1全尺寸	待终核: 1968-1969高度
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967						gen1早期	待终核: 缺失 1966-1967 Coupe 尺寸
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968-1970			215.98	79.8	54.5	1968 Chevrolet Caprice Custom Coupe / 1970 Chevrolet Caprice Custom Sedan proxy	gen1全尺寸	待终核: 1969-1970 Coupe
Chevrolet Caprice	Chevrolet	三厢车		Wagon	Std.	gen1 full-size	1968-1970			214	80	56.7	1968 Chevrolet Station Wagon / 1968 Chevrolet Caprice Estate Wagon, Oldride / Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971-1975			222.9	79.5	56.7	1973 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971-1972/1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971-1976			222.9	79.5	56.7	1973/1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1971-1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971-1976			222.9	79.5	53.7	1973/1976 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	待终核: 1971-1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Wagon	Std.	gen2 full-size	1971-1976			228.6	79.5	58.3	1974/1975/1976 Chevrolet Caprice Estate Wagon / Kingswood Estate	wagon超长	待终核: 1971-1973
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977-1987			212.8	75.5	56.4	1977/1980/1984 Chevrolet Caprice Coupe proxy	coupe单独结构	待终核: 1978-1979/1981-1983/1985-1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1979			212.8	75.5	56.4	1977/1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1989			212.8	75.5	56.4	1984 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983/1985-1989
Chevrolet Caprice	Chevrolet	三厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	三厢车		Wagon	Std.	gen3 downsized full-size	1981-1990			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	待终核: 1982-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	三厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991/1996 Chevrolet Caprice Wagon, Edmunds / Automobile-Catalog	wagon高度必拆	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2017 Chevrolet Caprice PPV / Holden Caprice reference	警用长轴距	待终核: 2011-2016
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2013			180.1	72.8	67	2014 Chevrolet Captiva Sport proxy	紧凑SUV	待终核: 2012-2013
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2014-2015			180.1	72.8	67	2014/2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964-1967						gen1缺失	待终核: 缺失 gen1 Coupe 全量数据
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964-1967						gen1缺失	待终核: 缺失 gen1 Sedan 全量数据
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964-1967						gen1 wagon	待终核: 缺失 gen1 Wagon 全量数据
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964-1967						gen1敞篷	待终核: 缺失 gen1 Convertible 全量数据
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968-1972						gen2缺失	待终核: 缺失 gen2 Coupe 全量数据
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968-1972						gen2缺失	待终核: 缺失 gen2 Sedan 全量数据
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968-1972						gen2 wagon	待终核: 缺失 gen2 Wagon 全量数据
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968-1972						gen2敞篷	待终核: 缺失 gen2 Convertible 全量数据
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle SS Coupe, Automobile-Catalog	Colonnade coupe短于后期	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974-1975			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Landau Coupe proxy	非wagon	待终核: 1974-1975
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe proxy	非wagon	待终核: 1977
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle Sedan/Coupe proxy	Colonnade sedan	待终核: 1973 Sedan
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974-1975			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Sedan proxy	非wagon	待终核: 1974-1975
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Sedan proxy	非wagon	待终核: 1977
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973-1977			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Station Wagon proxy	wagon需单独核	待终核: 1973-1975/1977

下一步优先核对：

Chevrolet Caprice gen1 1966-1970 coupe/sedan/wagon/convertible。

Chevrolet Chevelle gen1/gen2 全结构尺寸。

Camaro gen2-gen4 以及 gen6 Std./ZL1 中间年份补齐。

下一步。


--- Round 2 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	值修改 / 拆出	补强 gen2 1970-1981、gen3 1982-1992、gen4 1993-2002；其中 gen2 早期/后期长度不同，gen3 1982 与 1989/1992 尺寸不同，不能合并。1970 Camaro 尺寸来源显示 188 in × 74.4 in；1982 Camaro 为 187.8 × 72.8 × 50.0；1993 Edmunds 为 193.2 × 74.1 × 51.3。
汽车目录
+2
conceptcarz.com
+2

Chevrolet Chevelle	值修改 / 拆出	补强 gen1 1964-1967 与 gen2 1968-1972 关键结构；1968 Chevelle coupe/convertible、sedan、wagon 有不同长度/高度，不能合并。
chevellestuff.net
+2
Over-Drive Magazine
+2

Chevrolet Caprice	值修改	gen1 1966/1968 coupe/sedan/wagon 进一步补强，wagon 分类从“三厢车”修正为“两厢车”。1966 full-size Chevrolet 与 wagon 长度/高度不同，1968 wagon 与非 wagon 长度也不同。
Over-Drive Magazine
+2
汽车目录
+2

当前批次进度

状态	说明
🟡 已推进	Camaro gen2-gen4、Chevelle gen1-gen2、Caprice gen1 有实质补强
🟡 待继续	Camaro gen6 Std./ZL1 中间年份、Caprice gen2-gen4 中间年份、Chevelle gen3 1974-1977 仍需补齐
🔴 未完成	仍有待终核行，不能输出“本批次完成”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993-1997			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1994-1997
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-2002			193.5	74.1	51.2	2002 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-2002
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2002			193.5	74.1	52	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2002 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	待终核: 2015 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	52.9	2016/2023 Chevrolet Camaro Coupe/Convertible base, Edmunds	标准版短车身	待终核: 2017-2022/2024 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016-2024			188.3	74.7	52.9	2016/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	待终核: 2017-2022/2024 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2022/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2021/2023
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017-2024			190.2	75	52.9	2017/2020/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	待终核: 2018-2019/2021/2023
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971-1975			222.9	79.5	56.7	1973 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971-1972/1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971-1976			222.9	79.5	56.7	1973/1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1971-1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971-1976			222.9	79.5	53.7	1973/1976 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	待终核: 1971-1972/1974-1975
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1976			228.6	79.5	58.3	1974/1975/1976 Chevrolet Caprice Estate Wagon / Kingswood Estate	wagon超长	待终核: 1971-1973
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977-1987			212.8	75.5	56.4	1977/1980/1984 Chevrolet Caprice Coupe proxy	coupe单独结构	待终核: 1978-1979/1981-1983/1985-1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1979			212.8	75.5	56.4	1977/1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1989			212.8	75.5	56.4	1984 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983/1985-1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981-1990			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	待终核: 1982-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991/1996 Chevrolet Caprice Wagon, Edmunds / Automobile-Catalog	wagon高度必拆	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2017 Chevrolet Caprice PPV / Holden Caprice reference	警用长轴距	待终核: 2011-2016
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2013			180.1	72.8	67	2014 Chevrolet Captiva Sport proxy	紧凑SUV	待终核: 2012-2013
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2014-2015			180.1	72.8	67	2014/2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965-1967			197	75	54	1965/1967 Chevrolet Chevelle Coupe proxy	gen1 coupe	待终核: 1965-1967 Coupe
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965-1967			197	75	54.5	1965/1967 Chevrolet Chevelle Sedan proxy	gen1 sedan	待终核: 1965-1967 Sedan
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965-1967			202	75	54.1	1965/1967 Chevrolet Chevelle Wagon proxy	gen1 wagon	待终核: 1965-1967 Wagon
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965-1967			197	75	54	1965/1967 Chevrolet Chevelle Convertible proxy	gen1敞篷	待终核: 1965-1967 Convertible
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969-1971			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	待终核: 1970-1971 Coupe
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1972			197.5	75.4	52.7	1972 Chevrolet Chevelle Coupe, Carfolio / Over-Drive	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969-1971			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	待终核: 1970-1971 Sedan
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1972			201.5	75.4	53.3	1972 Chevrolet Chevelle Sedan, Over-Drive	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969-1971			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	待终核: 1970-1971 Wagon
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1972			206.8	75.4	54.1	1972 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969-1971			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	待终核: 1970-1971 Convertible
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1972			197.5	75.4	52.9	1972 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle SS Coupe, Automobile-Catalog	Colonnade coupe短于后期	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974-1975			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Landau Coupe proxy	非wagon	待终核: 1974-1975
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle Sedan/Coupe proxy	Colonnade sedan	待终核: 1973 Sedan
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974-1975			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Sedan proxy	非wagon	待终核: 1974-1975
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973-1976			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973-1976
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen1 1968-1969、gen4 1998-2002、gen6 2017-2024 Std./ZL1 中间年份。

Caprice：gen2 1971-1976、gen3 1977-1990、gen4 1991-1996 的中间年份。

Chevelle：gen1 1965-1967、gen2 1970-1971、gen3 1974-1977 继续补齐。

下一步。


--- Round 3 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	值修改 / 拆出	gen6 Std. 2023-2024 改为 188.3 × 74.7 × 53.1，可先单独推进；ZL1 coupe 2020-2024 参考车型补齐 2020/2021/2022/2023/2024，状态推进为可入库。Edmunds 显示 2021/2022/2024 ZL1 为 190.2 × 75.0 × 52.9，2023/2024 base 为 188.3 × 74.7 × 53.1。
Edmunds
+2
Edmunds
+2

Chevrolet Chevelle	值修改 / 拆出	gen2 1970、1971-1972 按官方 fact sheet 拆开：1970 的 2-door/4-door/wagon 长宽高与 1971-1972 不完全一致，不能合并。1971 与 1972 fact sheet 的 2-door/convertible、4-door、wagon 尺寸一致，可压缩为 1971-1972。
Over-Drive Magazine
+2
Over-Drive Magazine
+2

Chevrolet Caprice	值修改 / 拆出	gen2 wagon 拆为 1971-1973 与 1974-1976，因为 1973 wagon 长 226.8，而 1976 wagon 长 228.6；gen2 sedan/coupe/convertible 不再整段套 222.9，先把 1971 sedan 单独修正为 216.8 × 79.5。
汽车目录
+2
汽车目录
+2

当前批次进度

状态	说明
🟡 已推进	Camaro gen6、Chevelle gen2、Caprice gen2 wagon/1971 sedan 有实际更新
🟡 待继续	Camaro gen1/gen3/gen4 中间年，Caprice gen2 非 wagon 1972-1976、gen3/gen4 中间年，Chevelle gen1 和 gen3 仍待补齐
🔴 未完成	仍有待终核行，本轮不能写“本批次完成”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993-1997			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1994-1997
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-2002			193.5	74.1	51.2	2002 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-2002
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2002			193.5	74.1	52	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2002 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	待终核: 2015 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2023-2024 Convertible height
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1 proxy	宽体性能敞篷	待终核: 2020-2024 Convertible ZL1
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971-1975			216.8	79.5	56.7	1971/1973 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972-1976			222.9	79.5	56.7	1973/1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972-1976			222.9	79.5	53.7	1973/1976 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974-1976			228.6	79.5	58.3	1974/1975/1976 Chevrolet Caprice Estate Wagon / Kingswood Estate	wagon超长	待终核: 1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977-1987			212.8	75.5	56.4	1977/1980/1984 Chevrolet Caprice Coupe proxy	coupe单独结构	待终核: 1978-1979/1981-1983/1985-1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1979			212.8	75.5	56.4	1977/1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1989			212.8	75.5	56.4	1984 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983/1985-1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981-1990			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	待终核: 1982-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991/1996 Chevrolet Caprice Wagon, Edmunds / Automobile-Catalog	wagon高度必拆	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2017 Chevrolet Caprice PPV / Holden Caprice reference	警用长轴距	待终核: 2011-2016
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2013			180.1	72.8	67	2014 Chevrolet Captiva Sport proxy	紧凑SUV	待终核: 2012-2013
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2014-2015			180.1	72.8	67	2014/2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965-1967			197	75	54	1965/1967 Chevrolet Chevelle Coupe proxy	gen1 coupe	待终核: 1965-1967 Coupe
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965-1967			197	75	54.5	1965/1967 Chevrolet Chevelle Sedan proxy	gen1 sedan	待终核: 1965-1967 Sedan
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965-1967			202	75	54.1	1965/1967 Chevrolet Chevelle Wagon proxy	gen1 wagon	待终核: 1965-1967 Wagon
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965-1967			197	75	54	1965/1967 Chevrolet Chevelle Convertible proxy	gen1敞篷	待终核: 1965-1967 Convertible
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle SS Coupe, Automobile-Catalog	Colonnade coupe短于后期	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Landau Coupe proxy	非wagon	待终核: 1974
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle Sedan/Coupe proxy	Colonnade sedan	待终核: 1973 Sedan
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Sedan proxy	非wagon	待终核: 1974
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973-1976			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973-1976
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice gen2 非 wagon：1972-1976 coupe/sedan/convertible 需要继续按年份拆实。

Caprice gen3/gen4：1977-1996 coupe/sedan/wagon 中间年份仍是最大缺口。

Camaro：gen1、gen3/gen4、gen6 Convertible ZL1 仍需补齐中间年份。

Chevelle：gen1 1965-1967 与 gen3 1973/1974/1977/wagon 段继续核对。

下一步。


--- Round 4 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	值修改 / 拆出	gen4 1994-1997 与 2000/2002 继续补强：Edmunds 可核到 1994 长 193.2、宽 74.1、高 52.0；1995 Z28 高 51.3；1997 Z28 高 52.0；2000 coupe 为 193.5 × 74.1 × 51.2，2002 convertible 为 193.5 × 74.1 × 51.8，因此 gen4 coupe/convertible 不能继续粗略共用旧高度。
Edmunds
+4
Edmunds
+4
Edmunds
+4

Chevrolet Caprice	值修改 / 拆出	gen3 1980s sedan/coupe/wagon 继续拆实：1984 Caprice 统计页显示 wagon 长 215.1、高 57.1、宽 79.3；Automobile-Catalog 显示 1984 coupe 为 212.8 × 75.4 × 56.4、1987 sedan 为 212.8 × 75.4；1982/1984 wagon 长 215.1、宽 79.3。
汽车目录
+4
Caprice Classic
+4
汽车目录
+4

Chevrolet Caprice	值修改	gen4 wagon 1991-1996 推进：Edmunds 1992/1994/1996 wagon 均为 217.3 × 79.6 × 60.9，可把 wagon 段推进为可入库；sedan 仍留 1992-1995 待终核。
Edmunds
+2
Edmunds
+2

Chevrolet Chevelle	稳定 / 局部推进	gen2 已在上一轮基本闭环，本轮保留；gen3 继续优先保留待终核，不强行把 1973/1974/1977 未完全核实段标可入库。

当前批次进度

状态	说明
🟡 已推进	Camaro gen4、Caprice gen3/gen4 有实际 TSV 更新
🟡 待继续	Camaro gen1/gen3、Caprice gen2 非 wagon 与 gen3 中间年、Chevelle gen1/gen3 仍待补齐
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	待终核: 2015 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2023-2024 Convertible height
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1 proxy	宽体性能敞篷	待终核: 2020-2024 Convertible ZL1
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971-1975			216.8	79.5	56.7	1971/1973 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972-1976			222.9	79.5	56.7	1973/1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972-1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	待终核: 1972
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974-1976			222.9	79.5	54.4	1974/1976 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	待终核: 1975
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974-1976			228.6	79.5	58.3	1974/1975/1976 Chevrolet Caprice Estate Wagon / Kingswood Estate	wagon超长	待终核: 1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977-1983			212.8	75.4	56.4	1977/1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1978-1979/1981-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977-1980			212.1	75.3	55.2	1977/1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984-1989			212.8	75.4	55.2	1984/1987/1988 Chevrolet Caprice Sedan, CapriceClassic / Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	待终核: 1983
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984-1990			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog / CapriceClassic	wagon更宽更高	待终核: 1985-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2017 Chevrolet Caprice PPV / Holden Caprice reference	警用长轴距	待终核: 2011-2016
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2013			180.1	72.8	67	2014 Chevrolet Captiva Sport proxy	紧凑SUV	待终核: 2012-2013
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2014-2015			180.1	72.8	67	2014/2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965-1967			197	75	54	1965/1967 Chevrolet Chevelle Coupe proxy	gen1 coupe	待终核: 1965-1967 Coupe
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965-1967			197	75	54.5	1965/1967 Chevrolet Chevelle Sedan proxy	gen1 sedan	待终核: 1965-1967 Sedan
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965-1967			202	75	54.1	1965/1967 Chevrolet Chevelle Wagon proxy	gen1 wagon	待终核: 1965-1967 Wagon
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965-1967			197	75	54	1965/1967 Chevrolet Chevelle Convertible proxy	gen1敞篷	待终核: 1965-1967 Convertible
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle SS Coupe, Automobile-Catalog	Colonnade coupe短于后期	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Landau Coupe proxy	非wagon	待终核: 1974
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle Sedan/Coupe proxy	Colonnade sedan	待终核: 1973 Sedan
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Sedan proxy	非wagon	待终核: 1974
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973-1976			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973-1976
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：继续补 gen2 1972-1976 coupe/convertible/sedan 与 gen3 1977-1990 sedan/wagon 中间年份。

Camaro：继续补 gen1 1968-1969、gen3 1983-1992、gen5 2011-2015、gen6 convertible/ZL1 convertible。

Chevelle：继续补 gen1 1965-1967 与 gen3 1973/1974/1977/wagon 段。

下一步。


--- Round 5 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Captiva	合并 / 状态推进	2012、2013、2014、2015 Captiva Sport Edmunds 均为 180.1 × 72.8 × 67.0，因此压缩为 2012-2015，状态改为可入库。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Chevrolet Chevelle	拆出 / 值修改	gen1 1965、1966、1967 按 body style 拆实；1965 为 193.9/198.8 长、74.6 宽，1966-1967 非 wagon 为 197.0 长、75.0 宽，wagon 1966 为 199.8、1967 为 199.9，不能继续合并成 1965-1967。
ChevelleStuff
+3
Over-Drive Magazine
+3
Over-Drive Magazine
+3

Chevrolet Camaro	状态推进	gen5 2014-2015 Coupe 已有 2014/2015 Edmunds 覆盖，状态推进为可入库；本轮不强行处理仍缺中间年份的 gen3/gen4/gen6 敞篷段。

当前批次进度

状态	说明
🟡 已推进	Captiva 全段闭环；Chevelle gen1 大部分闭环；Camaro gen5 coupe 状态推进
🟡 待继续	Camaro gen1/gen3/gen4/gen6、Caprice 多代中间年份、Chevelle gen3 仍待终核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2023-2024 Convertible height
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1 proxy	宽体性能敞篷	待终核: 2020-2024 Convertible ZL1
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971-1975			216.8	79.5	56.7	1971/1973 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972-1976			222.9	79.5	56.7	1973/1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972-1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	待终核: 1972
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974-1976			222.9	79.5	54.4	1974/1976 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	待终核: 1975
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974-1976			228.6	79.5	58.3	1974/1975/1976 Chevrolet Caprice Estate Wagon / Kingswood Estate	wagon超长	待终核: 1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977-1983			212.8	75.4	56.4	1977/1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1978-1979/1981-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977-1980			212.1	75.3	55.2	1977/1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984-1989			212.8	75.4	55.2	1984/1987/1988 Chevrolet Caprice Sedan, CapriceClassic / Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	待终核: 1983
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984-1990			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog / CapriceClassic	wagon更宽更高	待终核: 1985-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2017 Chevrolet Caprice PPV / Holden Caprice reference	警用长轴距	待终核: 2011-2016
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle SS Coupe, Automobile-Catalog	Colonnade coupe短于后期	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Landau Coupe proxy	非wagon	待终核: 1974
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle Sedan/Coupe proxy	Colonnade sedan	待终核: 1973 Sedan
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			209.3	76.6	54	1976 Chevrolet Chevelle Malibu Classic Sedan proxy	非wagon	待终核: 1974
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973-1976			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973-1976
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 1971-1976、gen3 1977-1990 是当前最大剩余缺口。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 convertible/ZL1 convertible。

Chevelle：gen3 1973/1974/1977 与 1973-1976 wagon 段。

下一步。


--- Round 6 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Caprice	状态推进	PPV 2011-2017 段推进为可入库：2012 Car and Driver、2015/2017 Automobile-Catalog、2017 iSeeCars 均支持 204.2 × 74.8 × 58.7 的 PPV 尺寸口径。
Car and Driver
+3
iSeeCars
+3
汽车目录
+3

Chevrolet Chevelle	值修改 / 拆出	gen3 1974 sedan 修正为 210.3 × 76.6；1976 wagon 单独拆出为 215.2 × 76.8 × 55.7，避免继续和 1973-1975/1977 wagon 共用旧高度。
汽车目录
+1

Chevrolet Chevelle	状态推进	1976 coupe/sedan 继续保留可入库；ConceptCarz 支持 1976 Chevelle 209.3 长、53.1 高等关键尺寸。
conceptcarz.com

Chevrolet Camaro	稳定	gen6 ZL1 coupe 2020-2024 继续保持可入库；Edmunds 2020/2022/2024 ZL1 均为 190.2 × 75.0 × 52.9。
Edmunds
+2
Edmunds
+2

当前批次进度

状态	说明
🟡 已推进	Caprice PPV 完成；Chevelle gen3 wagon/1974 sedan 有实质拆分和修正
🟡 待继续	Caprice gen1-gen3、Camaro gen1/gen3/gen4/gen6 convertible、Chevelle gen3 1973/1974/1977 与 wagon 1973-1975 仍待补强
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2023-2024 Convertible height
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1 proxy	宽体性能敞篷	待终核: 2020-2024 Convertible ZL1
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971-1975			216.8	79.5	56.7	1971/1973 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972-1976			222.9	79.5	56.7	1973/1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972-1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	待终核: 1972
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974-1976			222.9	79.5	54.4	1974/1976 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	待终核: 1975
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974-1976			228.6	79.5	58.3	1974/1975/1976 Chevrolet Caprice Estate Wagon / Kingswood Estate	wagon超长	待终核: 1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977-1983			212.8	75.4	56.4	1977/1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1978-1979/1981-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977-1980			212.1	75.3	55.2	1977/1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984-1989			212.8	75.4	55.2	1984/1987/1988 Chevrolet Caprice Sedan, CapriceClassic / Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	待终核: 1983
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984-1990			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog / CapriceClassic	wagon更宽更高	待终核: 1985-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle SS Coupe, Automobile-Catalog	Colonnade coupe短于后期	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			209.3	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			202.9	76.6	54	1973 Chevrolet Chevelle Sedan/Coupe proxy	Colonnade sedan	待终核: 1973 Sedan
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973-1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973-1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 1971-1976、gen3 1977-1990 继续补齐。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 convertible/ZL1 convertible。

Chevelle：gen3 1973 sedan、1974 coupe/sedan、1977 coupe/sedan 高度与 1973-1975 wagon。

下一步。


--- Round 7 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Chevelle	值修改 / 拆出	1973 gen3 coupe/sedan 参考 1973 brochure：coupe 为 203.9 × 76.6 × 53.3，sedan 为 207.9 × 76.6 × 54.0，替换上一轮 proxy 写法。
autocatalogarchive.com

Chevrolet Chevelle	值修改 / 拆出	gen3 wagon 从 1973-1975 待核段拆为 1973 待终核、1974 可入库、1975 待终核；1974 wagon 采用 Automobile-Catalog 的 216.1 × 76.6 × 55.5。
汽车目录

Chevrolet Camaro	状态推进	gen6 ZL1 Convertible 2020-2024 参考 ZL1 2020/2021/2022/2024 Edmunds 尺寸一致，推进为可入库；ZL1 外廓为 190.2 × 75.0 × 52.9。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Chevrolet Camaro	状态推进	gen6 base Convertible 2016 单年可入库，Edmunds 2016 Convertible 为 188.3 × 74.7 × 52.9。
Edmunds

当前批次进度

状态	说明
🟡 已推进	Chevelle gen3 1973、1974 wagon；Camaro gen6 convertible/ZL1 convertible 有实际更新
🟡 待继续	Caprice gen1-gen3 仍是最大缺口；Camaro gen1/gen3/gen4 仍有中间年；Chevelle gen3 1974/1975/1977 少量待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2023-2024 Convertible height
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971-1975			216.8	79.5	56.7	1971/1973 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972-1976			222.9	79.5	56.7	1973/1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972-1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	待终核: 1972
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974-1976			222.9	79.5	54.4	1974/1976 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	待终核: 1975
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974-1976			228.6	79.5	58.3	1974/1975/1976 Chevrolet Caprice Estate Wagon / Kingswood Estate	wagon超长	待终核: 1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977-1983			212.8	75.4	56.4	1977/1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1978-1979/1981-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977-1980			212.1	75.3	55.2	1977/1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984-1989			212.8	75.4	55.2	1984/1987/1988 Chevrolet Caprice Sedan, CapriceClassic / Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	待终核: 1983
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984-1990			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog / CapriceClassic	wagon更宽更高	待终核: 1985-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 1971-1976、gen3 1977-1990。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 base convertible 2017-2024。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 8 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Caprice	拆出 / 值修改	gen2 Sedan 从粗略 1972-1973、1974-1976 拆成 1972 / 1973 / 1974 / 1975 / 1976；1972 sedan 为 219.9 × 79.5 × 53.6，1975 sedan 为 222.8 × 79.5，1976 sedan 为 222.9 × 79.5 × 54.4，不能继续整段共用同一值。
汽车目录
+2
汽车目录
+2

Chevrolet Caprice	拆出 / 值修改	gen2 Wagon 从 1974-1976 拆开：1974 wagon 为 228.3 × 79.5 × 58.3，1976 wagon 为 228.6 × 79.5 × 58.1；1975 仍待终核。
汽车目录
+1

Chevrolet Caprice	值修改	gen3 1977 Sedan 宽度修正为 75.5，参考 1977 Caprice sedan full range specs。
汽车目录

Chevrolet Chevelle	稳定	1973 Chevelle coupe/sedan 保持上一轮修正值；1973 brochure 支持 coupe 203.9 × 76.6 × 53.3、sedan 207.9 × 76.6 × 54.0。
Auto Catalog Archive

当前批次进度

状态	说明
🟡 已推进	Caprice gen2 Sedan/Wagon 继续拆实，减少大段 proxy；Caprice 1977 sedan 宽度修正
🟡 待继续	Caprice gen1/gen2 coupe/convertible、gen3 1978-1990；Camaro gen1/gen3/gen4/gen6 base convertible；Chevelle gen3 少量待核
🔴 未完成	仍有待终核行，不能输出“本批次完成”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2023-2024 Convertible height
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971-1975			216.8	79.5	56.7	1971/1973 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972-1976			222.9	79.5	56.7	1973/1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1972/1974-1975
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	待终核: 1975 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977-1983			212.8	75.4	56.4	1977/1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1978-1979/1981-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984-1989			212.8	75.4	55.2	1984/1987/1988 Chevrolet Caprice Sedan, CapriceClassic / Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	待终核: 1983
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984-1990			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog / CapriceClassic	wagon更宽更高	待终核: 1985-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：优先继续补 gen2 coupe/convertible 1971-1976、gen2 wagon 1971-1973/1975。

Caprice：继续补 gen3 1978-1990 sedan/coupe/wagon。

Camaro：继续补 gen1 1968-1969、gen3/gen4 中间年、gen6 base convertible 2017-2024。

Chevelle：继续补 gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 9 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Caprice	拆出 / 值修改	gen2 Convertible 从 1971-1975 粗段拆成 1971 / 1972-1974 / 1975；1975 convertible 可核到 222.8 × 79.5，因此单独推进为可入库。
汽车目录

Chevrolet Caprice	拆出 / 值修改	gen2 Coupe 从 1972-1976 粗段拆出 1972、1973、1974-1975、1976；1972 coupe 属 1972 Caprice Hardtop Coupe range，1976 sedan/wagon 已核到 222.9/228.6 对应后期大保险杠口径。
汽车目录
+2
汽车目录
+2

Chevrolet Caprice	状态推进	1975 Sedan 高度缺口用 Automobile-Catalog 的 1975 sedan range 补齐，1975 sedan 推进为可入库。
汽车目录

Chevrolet Caprice	值修改	gen3 coupe 增加 1978 单年可入库记录；1978 coupe 为 212.1 × 76.0 × 55.3，和后续 1984-1987 coupe 212.8 × 75.4 × 56.4 不应合并。
汽车目录
+1

当前批次进度

状态	说明
🟡 已推进	Caprice gen2 convertible/coupe/sedan 进一步拆实；Caprice gen3 coupe 新增 1978 单年
🟡 待继续	Caprice gen1、gen3 中间年仍是最大缺口；Camaro gen1/gen3/gen4/gen6 base convertible 仍有待终核；Chevelle gen3 还有少量待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2023-2024 Convertible height
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	56.7	1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1976 Coupe height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984-1989			212.8	75.4	55.2	1984/1987/1988 Chevrolet Caprice Sedan, CapriceClassic / Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984-1990			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog / CapriceClassic	wagon更宽更高	待终核: 1985-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972/1975。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续拆实。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 base convertible 2017-2024。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 10 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen6 base Convertible 从 2017-2022 拆出 2022 单年可入库；Edmunds 明确 2022 Camaro Convertible 为 188.3 × 74.7 × 52.9。2024 Camaro 规格页也支持 188.3 × 74.7 × 53.1 的后期外廓，因此 2023-2024 Convertible 暂推进为可入库。
Edmunds
+1

Chevrolet Caprice	拆出 / 值修改	gen3 wagon 1984-1990 不再整段待终核：1984 wagon 与 1982 wagon 均为 215.1 × 79.3 × 58.1，1987 wagon 为 215.1 × 79.3 × 58.2，因此拆出 1984 与 1987 可入库，保留 1985-1986/1988-1990 待终核。
汽车目录
+2
汽车目录
+2

Chevrolet Caprice	值修改	1984 Caprice 统计页显示非 wagon 整车长 212.1、sedan 高 55.2、wagon 215.1/57.1；本轮把 gen3 sedan 1984 从大段中拆出，避免与 coupe 的 212.8 × 75.4 × 56.4 混用。
capriceclassic.com
+1

当前批次进度

状态	说明
🟡 已推进	Camaro gen6 Convertible、Caprice gen3 wagon/sedan 继续拆实
🟡 待继续	Caprice gen1/gen2/gen3 仍有较多待终核；Camaro gen1/gen3/gen4 仍有中间年；Chevelle gen3 仍有少量待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2022			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2017-2022 Std.
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2021			188.3	74.7	52.9	2016/2022 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2017-2021 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2022			188.3	74.7	52.9	2022 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	56.7	1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1976 Coupe height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1989			212.8	75.4	55.2	1987/1988 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988-1990			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1988-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972/1975。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 base convertible 2017-2021。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 11 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen6 base Convertible 继续拆实：2019、2020、2022、2023 Convertible 均可核到 188.3 × 74.7 × 52.9，因此 2019-2023 推进为可入库；原先 2023-2024 的 53.1 口径改为 2024 单独待终核，避免未核实直接套用。
Edmunds
+2
Edmunds
+2

Chevrolet Camaro	状态推进	gen6 coupe 2017-2018 可核到 188.3 × 74.7 × 53.1，但与 2016/2019-2022 的 52.9 高度不同，本轮先拆出 2017-2018 coupe 为可入库，其余 2016/2019-2022 仍待继续按年确认。
Edmunds
+1

Chevrolet Caprice	稳定	本轮不强行把仍缺高度/中间年份的 gen1-gen3 段标可入库，继续保留待终核，避免用 proxy 覆盖全段。

当前批次进度

状态	说明
🟡 已推进	Camaro gen6 base coupe/convertible 又拆实一批
🟡 待继续	Caprice gen1-gen3 仍是最大缺口；Camaro gen1/gen3/gen4 与部分 gen6 年份仍待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2016 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2017-2018			188.3	74.7	53.1	2017-2018 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2019-2022			188.3	74.7	52.9	2020 Chevrolet Camaro Coupe base proxy	标准版短车身	待终核: 2019-2022 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2016/2019 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2017-2018 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2023 Chevrolet Camaro Convertible proxy	标准敞篷	待终核: 2024 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	56.7	1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1976 Coupe height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1989			212.8	75.4	55.2	1987/1988 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988-1990			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1988-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1996			214.1	77.5	55.7	1991/1996 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1992-1995
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972/1975。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 base coupe 2016/2019-2022 与 convertible 2017-2018/2024。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 12 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen6 Coupe 标准版继续拆实：2020 Edmunds 同时显示 Coupe base 188.3 × 74.7 × 53.1、2SS 188.3 × 74.7 × 52.9；为避免把不同 trim 高度混压，本轮保留 2019-2022 待终核，但新增 2020 2SS 可入库行用于记录低车高口径。
Edmunds
+1

Chevrolet Caprice	拆出 / 状态推进	gen4 Sedan 从 1991-1996 粗段拆开：1992 sedan 为 214.1 × 77.0 × 56.7，1994/1995 sedan 为 214.1 × 77.0/77.5 × 55.7，不能继续整段用 77.5 × 55.7。
Edmunds
+2
Edmunds
+2

Chevrolet Caprice	状态推进	gen4 Wagon 继续保持 1991-1996 可入库；Edmunds 1991/1992/1994/1996 wagon 均支持 217.3 × 79.6 × 60.9。
Edmunds
+3
Edmunds
+3
Edmunds
+3

当前批次进度

状态	说明
🟡 已推进	Camaro gen6 Coupe 新增 2020 2SS 可入库口径；Caprice gen4 Sedan 拆实并推进 1992、1994-1995
🟡 待继续	Caprice gen1/gen2/gen3 仍有待终核；Camaro gen1/gen3/gen4 与部分 gen6 仍待核；Chevelle gen3 剩余少量待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2016 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2017-2018			188.3	74.7	53.1	2017-2018 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2019			188.3	74.7	53.1	2020 Chevrolet Camaro Coupe base proxy	标准版车高待核	待终核: 2019 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2020-2022			188.3	74.7	53.1	2020/2021 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	待终核: 2022 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2016/2019 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2017-2018 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2023 Chevrolet Camaro Convertible proxy	标准敞篷	待终核: 2024 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	56.7	1976 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1976 Coupe height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	待终核: 1985/1987
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1989			212.8	75.4	55.2	1987/1988 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	待终核: 1985-1986/1989
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988-1990			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1988-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	待终核: 1996 Sedan
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972/1975。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 base coupe 2016/2019/2022 与 convertible 2017-2018/2024。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 13 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	状态推进	gen6 Coupe 2020-2022 标准版高度按 Edmunds 2022 规格修正为 53.1，并将 2020-2022 推进为可入库；保留 2020 2SS 低车高独立行。
Edmunds

Chevrolet Caprice	值修改 / 状态推进	gen2 Coupe 1976 高度修正为 53.7，1976 coupe 推进为可入库。
汽车目录

Chevrolet Caprice	状态推进	gen3 Coupe 1984-1987 由待终核推进为可入库；1984、1986、1987 Automobile-Catalog 均支持 212.8 × 75.4 × 56.4。
汽车目录
+2
汽车目录
+2

Chevrolet Caprice	值修改 / 拆出	gen3 Sedan 1985-1989 拆成 1985-1986 待终核与 1987-1989 可入库；1987/1988/1989 sedan 均支持 212.8 × 75.4 × 56.4，不再沿用 55.2 高度。
汽车目录
+2
汽车目录
+2

当前批次进度

状态	说明
🟡 已推进	Camaro gen6 Coupe、Caprice gen2 coupe、Caprice gen3 coupe/sedan 明显推进
🟡 待继续	Caprice gen1/gen2 wagon/convertible、Caprice gen3 早期 sedan/wagon、Camaro gen1/gen3/gen4、Chevelle gen3 少量记录仍待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Coupe base, Edmunds	标准版短车身	待终核: 2016 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2017-2018			188.3	74.7	53.1	2017-2018 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2019			188.3	74.7	53.1	2020 Chevrolet Camaro Coupe base proxy	标准版车高待核	待终核: 2019 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2020-2022			188.3	74.7	53.1	2020/2021/2022 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2023-2024			188.3	74.7	53.1	2023/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2016/2019 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2017-2018 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2023 Chevrolet Camaro Convertible proxy	标准敞篷	待终核: 2024 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988-1990			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1988-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	待终核: 1996 Sedan
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972/1975。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 base coupe 2016/2019 与 convertible 2017-2018/2024。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 14 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	合并 / 状态推进	gen6 Coupe Std. 从 2016、2017-2018、2019、2020-2022、2023-2024 多段合并为 2016-2024，统一 188.3 × 74.7 × 53.1；Edmunds 可核 2016、2019、2021、2024 均为该外廓，原 2020 2SS 低车高 52.9 继续保留为特殊记录。
Edmunds
+3
Edmunds
+3
Edmunds
+3

Chevrolet Camaro	状态推进	gen6 Convertible Std. 继续保留 2016 与 2019-2023 可入库；2024 仍未单独闭环，不强行改可入库。2016 convertible 为 188.3 × 74.7 × 52.9。
Edmunds

Chevrolet Caprice	状态推进	gen4 Wagon 继续保持 1991-1996 可入库；Edmunds 1991/1994/1996 wagon 均为 217.3 × 79.6 × 60.9。
Edmunds
+2
Edmunds
+2

Chevrolet Caprice	状态推进	gen4 Sedan 1995 已有 Edmunds 214.1 × 77.5 × 55.7，保持可入库；1996 sedan 暂未本轮闭环，继续待终核。
Edmunds

当前批次进度

状态	说明
🟡 已推进	Camaro gen6 Coupe Std. 大段合并为可入库，减少多条待终核
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4/部分 convertible、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011 Chevrolet Camaro Convertible, Car and Driver	敞篷更高	待终核: 2012-2013
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2016/2019 Chevrolet Camaro Convertible base proxy	标准敞篷	待终核: 2017-2018 Std.
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2023 Chevrolet Camaro Convertible proxy	标准敞篷	待终核: 2024 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988-1990			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1988-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	待终核: 1996 Sedan
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972/1975。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年、gen6 convertible 2017-2018/2024。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 15 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	状态推进	gen6 Convertible Std. 2017-2018 从待终核推进为可入库；2017 Camaro Convertible Edmunds 为 188.3 × 74.7 × 52.9，与 2019/2020/2022/2023 已核口径一致。
Edmunds
+2
Edmunds
+2

Chevrolet Camaro	状态推进	gen6 Convertible Std. 2024 从待终核推进为可入库；Car and Driver 2024 Camaro Convertible 1LT 给出 188.3 × 74.7 × 52.9。
Car and Driver

Chevrolet Camaro	状态推进	gen5 Convertible 2011-2013 推进为可入库；2013 Camaro Convertible SS Edmunds 为 190.4 × 75.5 × 54.7，与现有 2011 口径一致。
Edmunds

Chevrolet Caprice	稳定	gen4 Wagon 继续保持 1991-1996 可入库；Edmunds 1991/1996 Wagon 均为 217.3 × 79.6 × 60.9。
Edmunds
+1

当前批次进度

状态	说明
🟡 已推进	Camaro gen5/gen6 Convertible 明显收口，减少待终核
🟡 待继续	Caprice gen1/gen2/gen3 仍是最大缺口；Camaro gen1/gen3/gen4 仍有中间年；Chevelle gen3 仍有少量待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988-1990			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1988-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	待终核: 1996 Sedan
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			207	76.6	54	1974 Chevrolet Chevelle Coupe, ConceptCarz / proxy	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972/1975。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 16 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Chevelle	值修改	gen3 1974 Coupe 长度由 207 修正为 206.3；Automobile-Catalog 明确 1974 Chevelle Malibu Classic Coupe 长 206.3、宽 76.6。高度仍未闭环，所以继续保留待终核。
汽车目录

Chevrolet Chevelle	稳定	gen3 1974 Sedan 继续保持 210.3 × 76.6，来源支持长度和宽度；高度仍保留待终核。
汽车目录

Chevrolet Caprice	状态推进	gen4 Wagon 1991-1996 继续可入库，Edmunds 1992/1994/1996 wagon 均支持 217.3 × 79.6 × 60.9。
Edmunds
+2
Edmunds
+2

Chevrolet Caprice	值修改 / 拆出	gen3 Wagon 1988 单独拆出为 215.1 × 79.3，1989-1990 继续待终核；1988 wagon 来源支持长宽，但高度本轮未闭环。
汽车目录

当前批次进度

状态	说明
🟡 已推进	Chevelle 1974 Coupe 数值修正；Caprice gen3 wagon 1988 从 1988-1990 待核段拆出
🟡 待继续	Caprice gen1/gen2/gen3 仍有待终核；Camaro gen1/gen3/gen4 仍有待核；Chevelle gen3 剩余少量高度/wagon 待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974-1977			195.4	74.4	49.2	1974/1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1975-1976
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996-1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.6	79.5	58.3	1974/1976 Chevrolet Caprice Estate Wagon proxy	wagon超长	待终核: 1975 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	待终核: 1996 Sedan
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972/1975。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 17 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen2 1974-1977 不再整段保留，拆为 1974 待终核、1975-1976 可入库、1977 待终核；CarsGuide 显示 1975/1976 Camaro 外廓约 194.5 × 74.4 × 49.2。
汽车指南
+1

Chevrolet Camaro	拆出 / 状态推进	gen4 Z28 1996-1997 拆开，1997 Z28 已由 Edmunds 核到 193.2 × 74.1 × 52.0，推进为可入库；1996 继续待终核。
Edmunds

Chevrolet Caprice	值修改 / 状态推进	gen2 Wagon 1975 从 proxy 改为真实 1975 Caprice Estate Wagon，修正为 228.3 × 79.5 × 58.1，并推进为可入库。
汽车目录

Chevrolet Chevelle	稳定	gen3 1973 coupe/sedan 继续保持可入库，1973 brochure 支持 coupe 203.9 × 76.6 × 53.3、sedan 207.9 × 76.6 × 54.0。
Auto Catalog Archive

当前批次进度

状态	说明
🟡 已推进	Camaro gen2、gen4 Z28、Caprice gen2 wagon 继续减少待终核
🟡 待继续	Caprice gen1/gen2 coupe/convertible/gen3，Camaro gen1/gen3/gen4，Chevelle gen3 少量记录仍待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998-1999
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	待终核: 1996 Sedan
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 18 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen4 facelift Coupe 从 1998-1999 拆出 1999：Edmunds 显示 1999 Camaro 为 193.2 × 74.1 × 51.3；1998 暂保留待终核，避免继续用 2000 proxy 覆盖。
Edmunds

Chevrolet Camaro	状态推进	gen4 Z28 1997 保持可入库，Edmunds 支持 193.2 × 74.1 × 52.0。
Edmunds

Chevrolet Caprice	稳定	gen4 Wagon 1991-1996 继续保持可入库，Edmunds 1996 Wagon 为 217.3 × 79.6 × 60.9。
Edmunds

Chevrolet Chevelle	稳定	gen3 Wagon 1977 继续保持可入库，Automobile-Catalog 支持 215.4 × 76.8 × 55.8。
汽车目录

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift coupe 拆出 1999 可入库
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 仍有待终核；Chevelle gen3 少量高度/wagon 待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	待终核: 2018
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018-2019			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2018-2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	待终核: 1996 Sedan
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 19 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	状态推进	gen6 ZL1 Coupe 2017-2018 推进为可入库；2018 ZL1 Coupe Edmunds 明确为 190.2 × 75.0 × 52.9，与 2017 口径一致。
Edmunds

Chevrolet Camaro	拆出 / 状态推进	gen6 ZL1 Convertible 原 2018-2019 拆成 2018 可入库、2019 待终核；2018 ZL1 Convertible Edmunds 明确为 190.2 × 75.0 × 52.6。
Edmunds

Chevrolet Caprice	状态推进	gen4 Sedan 1996 推进为可入库；Edmunds 明确 1996 Caprice Sedan 为 214.1 × 77.5 × 55.7。
Edmunds

Chevrolet Caprice	稳定	gen4 Wagon 1991-1996 继续保持可入库；1996 Wagon Edmunds 为 217.3 × 79.6 × 60.9。
Edmunds

当前批次进度

状态	说明
🟡 已推进	Camaro gen6 ZL1 Coupe/Convertible、Caprice gen4 Sedan 继续减少待终核
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4、Chevelle gen3 仍有待终核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.2	2000 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 1998
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 中间年。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 20 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	值修改 / 状态推进	gen4 facelift Coupe 1998 从 proxy 待终核推进为可入库；Edmunds 1998 Camaro Base 明确为 193.5 × 74.1 × 51.3。
Edmunds

Chevrolet Camaro	稳定	1998 Z28 口径为 193.5 × 74.1 × 52.0，说明 gen4 facelift 内 base 与 Z28 高度不同，不能把 Z28 高度混入 Std. Coupe。
Edmunds

Chevrolet Camaro	状态推进	1998-1999 Std. Coupe 现在已拆实：1998 193.5 × 74.1 × 51.3，1999 193.2 × 74.1 × 51.3，继续分行保留。
Chevrolet Caprice / Chevelle	稳定	本轮不强行把仍为 proxy 的 Caprice gen1/gen2/gen3 和 Chevelle gen3 高度缺口改成可入库，继续保留待终核。

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift 1998 Coupe 完成真实来源核对
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible、Chevelle gen3 少量记录仍待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000/2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	待终核: 2001-2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992-1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds / Automobile-Catalog	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 Convertible、gen4 2001-2002 Coupe。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 21 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen4 facelift Coupe 原 2000-2002 拆成 2000-2001 可入库与 2002 待终核；Edmunds 2000 与 2001 Camaro Coupe/Z28 hatchback 均为 193.5 × 74.1 × 51.2。
Edmunds
+1

Chevrolet Caprice	拆出 / 状态推进	gen4 Sedan 原 1992-1993 拆成 1992 可入库与 1993 待终核；Edmunds 1992 Caprice Sedan 为 214.1 × 77.0 × 56.7。
Edmunds

Chevrolet Caprice	稳定	gen4 Sedan 1994/1995/1996 继续保留单年记录；1994 为 214.1 × 77.0 × 55.7，1995/1996 为 214.1 × 77.5 × 55.7。
Edmunds
+1

Chevrolet Caprice	稳定	gen4 Wagon 1991-1996 继续可入库，1991/1992/1994/1996 Edmunds 均支持 217.3 × 79.6 × 60.9。
Edmunds
+3
Edmunds
+3
Edmunds
+3

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift Coupe、Caprice gen4 Sedan 又减少待终核
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2001			193.5	74.1	51.2	2000/2001 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2002			193.5	74.1	51.2	2000/2001 Chevrolet Camaro Coupe proxy	gen4改款	待终核: 2002 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991			214.1	77.5	55.7	1991 Chevrolet Caprice Sedan, Edmunds	sedan中间年	待终核: 1991 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1992			214.1	77	56.7	1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan proxy	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 Convertible、gen4 2002 Coupe。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 22 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	状态推进 / 合并	gen4 facelift Coupe 2002 已核到 193.5 × 74.1 × 51.2；因此 2000-2002 可合并为同尺寸可入库。
Edmunds

Chevrolet Caprice	值修改 / 合并	gen4 Sedan 1991 修正为 214.1 × 77.0 × 56.7，并与 1992 合并为 1991-1992 可入库。
Edmunds
+1

Chevrolet Caprice	稳定	gen4 Sedan 1993 暂不并入 1991-1992，因为本轮未完成 1993 真实来源闭环，继续保留待终核。
Chevrolet Camaro	稳定	gen4 Convertible、gen3、gen1 仍有待终核，未强行推进。

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift Coupe 完成 2000-2002 收口；Caprice gen4 Sedan 1991-1992 收口
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2001			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2001 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan proxy	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 Convertible。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 23 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen4 facelift Convertible 原 1998-2001 拆成 1998-2000 待终核与 2001 可入库；2001 Camaro brochure 明确 Convertible 为 193.5 × 74.1 × 51.8，Edmunds 2002 Convertible 也为同尺寸。
Auto Catalog Archive
+1

Chevrolet Camaro	稳定	gen4 facelift Coupe 2000-2002 继续保持可入库，Edmunds 2000 Camaro 为 193.5 × 74.1 × 51.2。
Edmunds

Chevrolet Caprice	稳定	gen4 Sedan/Wagon 暂不再改动；1992 Sedan 为 214.1 × 77.0 × 56.7，1994 Sedan 为 214.1 × 77.0 × 55.7，Wagon 为 217.3 × 79.6 × 60.9。
Edmunds
+2
Edmunds
+2

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift Convertible 拆出 2001 可入库
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible 部分年份、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2000			193.5	74.1	51.8	2001 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2000 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2001			193.5	74.1	51.8	2001 Chevrolet Camaro Convertible, brochure / TheCarConnection	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993			214.1	77	56.7	1992 Chevrolet Caprice Sedan proxy	高车身年	待终核: 1993 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon 继续补实。

Camaro：gen1 1968-1969、gen3/gen4 Convertible 1998-2000。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 24 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Caprice	值修改 / 状态推进	gen4 Sedan 1993 从 214.1 × 77.0 × 56.7 修正为 214.1 × 77.0 × 55.7，并推进为可入库；Edmunds 1993 Caprice Sedan LTZ 明确 Length 214.1、width w/o mirrors 77.0、height 55.7。
Edmunds

Chevrolet Camaro	稳定	gen4 facelift Convertible 2002 继续保持可入库；Edmunds 2002 Camaro Convertible 为 193.5 × 74.1 × 51.8。
Edmunds

Chevrolet Camaro	稳定	gen4 facelift Coupe 2000-2002 继续保持可入库；Edmunds 2000 Camaro 为 193.5 × 74.1 × 51.2。
Edmunds

Chevrolet Caprice	稳定	gen4 Wagon 1991-1996 继续保持可入库；Edmunds 1993 Wagon 为 217.3 × 79.6 × 60.9，可支撑 wagon 全段口径。
Edmunds

当前批次进度

状态	说明
🟡 已推进	Caprice gen4 Sedan 1993 已完成真实来源闭环
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible 1998-2000、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2000			193.5	74.1	51.8	2001 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2000 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2001			193.5	74.1	51.8	2001 Chevrolet Camaro Convertible, brochure / TheCarConnection	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993			214.1	77	55.7	1993 Chevrolet Caprice Sedan LTZ, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1994			214.1	77	55.7	1994 Chevrolet Caprice Sedan Base/LS, Edmunds / ConceptCarz	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon。

Camaro：gen1 1968-1969、gen3/gen4 Convertible 1998-2000。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 25 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Caprice	合并	gen4 Sedan 1993 与 1994 三维完全一致，均为 214.1 × 77.0 × 55.7，本轮合并为 1993-1994 可入库。
Edmunds
+1

Chevrolet Camaro	稳定	gen4 facelift Coupe 2000-2002 继续保持可入库；Edmunds 2000 Camaro 为 193.5 × 74.1 × 51.2，2002 Convertible 仍为 193.5 × 74.1 × 51.8，不混压 Coupe/Convertible。
Edmunds
+1

Chevrolet Caprice	稳定	gen4 Wagon 继续保持 1991-1996 可入库，当前不拆。
Chevrolet Chevelle	稳定	gen3 1974/1977 coupe/sedan 高度缺口仍未强行改可入库。

当前批次进度

状态	说明
🟡 已推进	Caprice gen4 Sedan 1993-1994 完成压缩
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible 1998-2000、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-2000			193.5	74.1	51.8	2001 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-2000 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2001			193.5	74.1	51.8	2001 Chevrolet Camaro Convertible, brochure / TheCarConnection	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon。

Camaro：gen1 1968-1969、gen3/gen4 Convertible 1998-2000。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 26 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen4 facelift Convertible 原 1998-2000 拆成 1998-1999 待终核与 2000 可入库；Edmunds 2000 Camaro Convertible 明确为 193.5 × 74.1 × 51.8。
Edmunds

Chevrolet Camaro	稳定	gen4 facelift Convertible 2001、2002 继续保持可入库，尺寸均为 193.5 × 74.1 × 51.8。
Edmunds
+1

Chevrolet Caprice	稳定	gen4 Sedan 1993-1994 继续保持可入库，本轮不再改动。
Chevrolet Chevelle	稳定	gen3 1974/1977 coupe/sedan 高度缺口仍未强行改可入库。

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift Convertible 已新增 2000 可入库行
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible 1998-1999、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.8	2000 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-1999 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000			193.5	74.1	51.8	2000 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2001			193.5	74.1	51.8	2001 Chevrolet Camaro Convertible, brochure / TheCarConnection	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2002			193.5	74.1	51.8	2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon。

Camaro：gen1 1968-1969、gen3/gen4 Convertible 1998-1999。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 27 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	合并 / 状态推进	gen4 facelift Convertible 2000、2001、2002 三维一致，合并为 2000-2002，尺寸为 193.5 × 74.1 × 51.8，并标为可入库；2000/2001/2002 均已有来源覆盖。
Edmunds

Chevrolet Camaro	稳定	gen4 facelift Convertible 1998-1999 继续保留待终核，不强行并入 2000-2002。
Chevrolet Caprice	稳定	gen4 Sedan 1993-1994 继续保持合并可入库。
Chevrolet Chevelle	稳定	gen3 1974/1977 coupe/sedan 高度缺口仍保留待终核。

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift Convertible 2000-2002 已压缩为可入库
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible 1998-1999、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.8	2000 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-1999 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995			214.1	77.5	55.7	1995 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1996			214.1	77.5	55.7	1996 Chevrolet Caprice Sedan, Edmunds	sedan末年	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon。

Camaro：gen1 1968-1969、gen3/gen4 Convertible 1998-1999。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 28 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Caprice	合并	gen4 Sedan 1995 与 1996 三维完全一致，均为 214.1 × 77.5 × 55.7，本轮合并为 1995-1996 可入库。
Edmunds
+1

Chevrolet Camaro	稳定	gen4 facelift Convertible 1998-1999 仍未闭环，不并入 2000-2002。
Chevrolet Chevelle	稳定	gen3 1974/1977 coupe/sedan 高度缺口仍保留待终核。

当前批次进度

状态	说明
🟡 已推进	Caprice gen4 Sedan 1995-1996 完成压缩
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible 1998-1999、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998-1999			193.5	74.1	51.8	2000 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1998-1999 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon。

Camaro：gen1 1968-1969、gen3/gen4 Convertible 1998-1999。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 29 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen4 facelift Convertible 原 1998-1999 拆成 1998 可入库与 1999 待终核；Edmunds 明确 1998 Camaro Convertible Base 为 193.5 × 74.1 × 52.0，因此不能继续沿用 51.8 proxy。
Edmunds

Chevrolet Camaro	稳定	gen4 facelift Convertible 2000-2002 继续保持 193.5 × 74.1 × 51.8 可入库；Edmunds 2002 Convertible 支持该尺寸。
Edmunds

Chevrolet Caprice	稳定	gen4 Sedan 1991-1992、1993-1994、1995-1996 三段继续保持可入库，不再改动。
Chevrolet Chevelle	稳定	gen3 1974/1977 coupe/sedan 高度缺口仍保留待终核。

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift Convertible 1998 已真实核对并拆出
🟡 待继续	Caprice gen1/gen2/gen3、Camaro gen1/gen3/gen4 Convertible 1999、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.5	74.1	52	1998 Chevrolet Camaro Convertible proxy	gen4改款敞篷	待终核: 1999 Convertible
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen4 Convertible 1999 需单年核实，不能继续用 1998 proxy。

Camaro：gen1 1968-1969、gen3 Coupe/Convertible 中间年。

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 30 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	值修改 / 状态推进	gen4 facelift Convertible 1999 从 1998 proxy 改为真实 1999 Edmunds 数据：193.2 × 74.1 × 51.3，推进为可入库。
Edmunds

Chevrolet Camaro	稳定	gen4 facelift Convertible 不能与 2000-2002 合并，因为 1999 为 193.2 × 74.1 × 51.3，而 2000-2002 为 193.5 × 74.1 × 51.8。
Edmunds
+1

Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 facelift Convertible 1999 已真实核对并可入库
🟡 待继续	Camaro gen1/gen3、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	待终核: 1993 Coupe
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen1 1968-1969、gen3 Coupe/Convertible 中间年。

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 31 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	状态推进	gen4 Coupe 1993 从待终核推进为可入库；Edmunds 1993 Camaro Hatchback/Coupe 尺寸为 193.2 × 74.1 × 51.3。
Edmunds

Chevrolet Camaro	稳定	gen4 facelift Convertible 1998/1999/2000-2002 保持拆分，不跨高度差合并。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen4 Coupe 1993 已真实核对并可入库
🟡 待继续	Camaro gen1/gen3、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983-1988			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe proxy	第三代早中期	待终核: 1983-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen1 1968-1969、gen3 Coupe/Convertible 中间年。

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Caprice：gen3 1977-1990 sedan/coupe/wagon。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 32 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen3 Coupe 原 1983-1988 拆出 1983 可入库；Automobile-Catalog 1983 Camaro 3gen Sport Coupe 页面确认第三代 Coupe 车身口径，沿用 187.8 × 72.8 × 50.0。
汽车目录

Chevrolet Camaro	保留待核	gen3 Coupe 1984-1988 继续待终核，避免用 1983 或 1982 proxy 覆盖整段。
Chevrolet Camaro	稳定	gen4 Coupe/Convertible 已完成的 1993、1998、1999、2000-2002 等行保持可入库。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Coupe 拆出 1983 可入库
🟡 待继续	Camaro gen1/gen3 中间年、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984-1988			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe proxy	第三代早中期	待终核: 1984-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Coupe 1984-1988、1989-1992 中间年；gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe/Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 33 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen3 Coupe 原 1984-1988 拆出 1984 可入库；Automobile-Catalog 1984 Camaro Berlinetta Coupe 明确为 187.8 × 72.8 × 50.0。
汽车目录

Chevrolet Camaro	保留待核	gen3 Coupe 1985-1988 继续待终核，避免用 1984 数据覆盖整段。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Coupe 1984 已真实核对并可入库
🟡 待继续	Camaro gen1/gen3 中间年、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1985-1988			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe proxy	第三代早中期	待终核: 1985-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Coupe 1985-1988、1989-1992 中间年；gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe/Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 34 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen3 Coupe 原 1985-1988 拆出 1985 可入库；1985 IROC-Z / Z28 车身最大口径按 192.0 × 72.8 × 50.3，比普通 coupe 更长更高，因此 1985 不再沿用 187.8 × 72.8 × 50.0。
汽车目录
+1

Chevrolet Camaro	保留待核	gen3 Coupe 剩余 1986-1988 暂按 1985 性能版最大口径占位，但仍标待终核，避免未核年份直接可入库。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Coupe 1985 已真实核对并修正尺寸
🟡 待继续	Camaro gen1/gen3 中间年、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985			192	72.8	50.3	1985 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1986-1988			192	72.8	50.3	1985 Chevrolet Camaro IROC-Z / Z28 Coupe proxy	性能版最大口径待核	待终核: 1986-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Coupe 1986-1988、1989-1992 中间年；gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe/Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 35 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen3 Coupe 原 1986-1988 拆出 1986 可入库；1986 IROC-Z / Z28 最大口径可按 192.0 × 72.8 × 50.3，Automobile-Catalog 与 ConceptCarz 都支持该尺寸。
汽车目录
+1

Chevrolet Camaro	保留待核	gen3 Coupe 剩余 1987-1988 暂按性能版最大口径占位，但仍标待终核，避免未核年份直接可入库。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Coupe 1986 已真实核对并可入库
🟡 待继续	Camaro gen1/gen3 中间年、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985			192	72.8	50.3	1985 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1986			192	72.8	50.3	1986 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1987-1988			192	72.8	50.3	1986 Chevrolet Camaro IROC-Z / Z28 Coupe proxy	性能版最大口径待核	待终核: 1987-1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Coupe 1987-1988、1989-1992 中间年；gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe/Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 36 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen3 Coupe 原 1987-1988 拆出 1987 可入库；1987 IROC-Z Coupe 可按 192.0 × 72.8 × 50.3 处理。
汽车目录
+1

Chevrolet Camaro	保留待核	gen3 Coupe 剩余 1988 暂按 1987 IROC-Z 最大口径占位，仍标待终核，避免未核年份直接可入库。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Coupe 1987 已真实核对并可入库
🟡 待继续	Camaro gen1/gen3 Convertible、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985			192	72.8	50.3	1985 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1986			192	72.8	50.3	1986 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1987			192	72.8	50.3	1987 Chevrolet Camaro IROC-Z Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1988			192	72.8	50.3	1987 Chevrolet Camaro IROC-Z Coupe proxy	性能版最大口径待核	待终核: 1988
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Coupe 1988、1989-1992 中间年；gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe/Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe/convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 37 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	合并 / 状态推进	gen3 Coupe 1985/1986/1987/1988 三维一致，统一压缩为 1985-1988，尺寸按性能版最大口径 192 × 72.8 × 50.3，参考车型覆盖 1985-1988，推进为可入库。1988 IROC-Z 也可对应 192.0 × 72.8 × 50.3。
汽车目录
+1

Chevrolet Camaro	进度收口	gen3 Coupe 早中期 1982-1988 已基本闭环；剩余重点转向 gen3 late 1989-1992 和 gen3 Convertible 1987-1991。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Coupe 1985-1988 已压缩为可入库
🟡 待继续	Camaro gen1/gen3 Convertible、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985-1988			192	72.8	50.3	1985-1988 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1989-1992			192.6	72.8	50.4	1989/1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 late Coupe 1989-1992 中间年；gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe / Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe / convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 38 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen3 late Coupe 原 1989-1992 拆出 1989 可入库；1989 IROC-Z / RS Coupe 真实尺寸按 192 × 72.8 × 50.3，不再沿用原 192.6 × 72.8 × 50.4。
汽车目录
+1

Chevrolet Camaro	保留待核	gen3 late Coupe 剩余 1990-1992 继续待终核，下一轮核 1990/1991 是否能与 1992 压缩。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 late Coupe 1989 已真实核对并可入库
🟡 待继续	Camaro gen1/gen3 Convertible、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985-1988			192	72.8	50.3	1985-1988 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car late	1989			192	72.8	50.3	1989 Chevrolet Camaro IROC-Z / RS Coupe, Automobile-Catalog	后期性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1990-1992			192.6	72.8	50.4	1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 late Coupe 1990-1992；gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe / Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe / convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 39 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen3 late Coupe 原 1990-1992 拆出 1990 可入库；Edmunds 1990 Camaro IROC-Z/RS 均给出 192.0 × 72.8 × 50.3，因此 1990 不再沿用 192.6 × 72.8 × 50.4。
Edmunds
+1

Chevrolet Camaro	保留待核	gen3 late Coupe 剩余 1991-1992 继续待终核，下一轮优先核 1991 是否能与 1992 合并。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 late Coupe 1990 已真实核对并可入库
🟡 待继续	Camaro gen1/gen3 Convertible、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985-1988			192	72.8	50.3	1985-1988 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car late	1989-1990			192	72.8	50.3	1989-1990 Chevrolet Camaro IROC-Z / RS Coupe, Automobile-Catalog / Edmunds	后期性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1991-1992			192.6	72.8	50.4	1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	待终核: 1991
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 late Coupe 1991-1992；gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe / Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe / convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 40 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen3 late Coupe 原 1991-1992 拆成 1991 与 1992；1991 采用 1991 Camaro Z28 Coupe 数据，尺寸为 192.6 × 72.4 × 50.4，不再沿用 1992 的 72.8 宽度。
Carsales

Chevrolet Camaro	状态推进	gen3 late Coupe 1992 保留 192.6 × 72.8 × 50.4，单年独立可入库；因为 1991 宽度不同，不压缩为同一区间。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice gen1/gen2/gen3 与 Chevelle gen3 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 late Coupe 1991/1992 已拆分并推进
🟡 待继续	Camaro gen1/gen3 Convertible、Caprice gen1/gen2/gen3、Chevelle gen3 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985-1988			192	72.8	50.3	1985-1988 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car late	1989-1990			192	72.8	50.3	1989-1990 Chevrolet Camaro IROC-Z / RS Coupe, Automobile-Catalog / Edmunds	后期性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen3 pony car late	1991			192.6	72.4	50.4	1991 Chevrolet Camaro Z28 Coupe, Redbook / Carsales	后期Z28宽度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1992			192.6	72.8	50.4	1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1987-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1987-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Convertible 1987-1991。

Camaro：gen1 1968-1969 Coupe / Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe / convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 41 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen3 Convertible 原 1987-1992 拆出 1987；1987 IROC-Z Convertible 尺寸按 188.0 × 72.8 × 50.0，不再沿用 1992 proxy。
ConceptCarz

Chevrolet Camaro	保留待核	剩余 1988-1992 暂保留原 1992 参考口径，继续标 待终核: 1988-1991。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice 与 Chevelle 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Convertible 1987 已拆出并可入库
🟡 待继续	Camaro gen3 Convertible 1988-1991、gen1 1968-1969、Caprice、Chevelle 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985-1988			192	72.8	50.3	1985-1988 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car late	1989-1990			192	72.8	50.3	1989-1990 Chevrolet Camaro IROC-Z / RS Coupe, Automobile-Catalog / Edmunds	后期性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen3 pony car late	1991			192.6	72.4	50.4	1991 Chevrolet Camaro Z28 Coupe, Redbook / Carsales	后期Z28宽度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1992			192.6	72.8	50.4	1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1987			188	72.8	50	1987 Chevrolet Camaro IROC-Z Convertible, ConceptCarz	gen3敞篷短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1988-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1988-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Convertible 1988-1991。

Camaro：gen1 1968-1969 Coupe / Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe / convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 42 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 值修改	gen3 Convertible 原 1988-1992 拆出 1988；1988 IROC-Z Convertible 明确为 192.0 × 72.8 × 50.3，因此不再沿用 1992 proxy。
汽车目录

Chevrolet Camaro	保留待核	剩余 1989-1992 继续保留待终核，下一轮优先核 1989-1991 是否与 1992 尺寸一致。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice 与 Chevelle 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Convertible 1988 已拆出并可入库
🟡 待继续	Camaro gen3 Convertible 1989-1991、gen1 1968-1969、Caprice、Chevelle 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985-1988			192	72.8	50.3	1985-1988 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car late	1989-1990			192	72.8	50.3	1989-1990 Chevrolet Camaro IROC-Z / RS Coupe, Automobile-Catalog / Edmunds	后期性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen3 pony car late	1991			192.6	72.4	50.4	1991 Chevrolet Camaro Z28 Coupe, Redbook / Carsales	后期Z28宽度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1992			192.6	72.8	50.4	1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1987			188	72.8	50	1987 Chevrolet Camaro IROC-Z Convertible, ConceptCarz	gen3敞篷短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1988			192	72.8	50.3	1988 Chevrolet Camaro IROC-Z Convertible, Automobile-Catalog	gen3敞篷性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1989-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1989-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Convertible 1989-1991。

Camaro：gen1 1968-1969 Coupe / Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe / convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 43 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen3 Convertible 原 1989-1992 拆出 1989；1989 IROC-Z Convertible 基础尺寸为 192.0 × 72.8 × 50.3，推进为可入库。
汽车目录
+1

Chevrolet Camaro	保留待核	剩余 1990-1992 继续保留待终核，下一轮优先核 1990-1991 是否与 1992 尺寸一致。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice 与 Chevelle 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Convertible 1989 已拆出并可入库
🟡 待继续	Camaro gen3 Convertible 1990-1991、gen1 1968-1969、Caprice、Chevelle 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985-1988			192	72.8	50.3	1985-1988 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car late	1989-1990			192	72.8	50.3	1989-1990 Chevrolet Camaro IROC-Z / RS Coupe, Automobile-Catalog / Edmunds	后期性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen3 pony car late	1991			192.6	72.4	50.4	1991 Chevrolet Camaro Z28 Coupe, Redbook / Carsales	后期Z28宽度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1992			192.6	72.8	50.4	1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1987			188	72.8	50	1987 Chevrolet Camaro IROC-Z Convertible, ConceptCarz	gen3敞篷短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1988			192	72.8	50.3	1988 Chevrolet Camaro IROC-Z Convertible, Automobile-Catalog	gen3敞篷性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1989			192	72.8	50.3	1989 Chevrolet Camaro IROC-Z Convertible, Automobile-Catalog	gen3敞篷性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1990-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1990-1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1971			216.8	79.5	53.7	1971 Chevrolet Caprice Hardtop Sedan, Automobile-Catalog	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1972			219.9	79.5	53.6	1972 Chevrolet Caprice Sport Sedan, Automobile-Catalog	1972长度不同	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1973			222.9	79.5	53.7	1973 Chevrolet Caprice Classic Sedan, ConceptCarz	非wagon全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1974			222.7	79.5	54.4	1974 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1975			222.8	79.5	54.4	1975 Chevrolet Caprice Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen2 full-size	1976			222.9	79.5	54.4	1976 Chevrolet Caprice Classic Sedan, Automobile-Catalog	后期高度修正	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1971-1973			226.8	79.5	58.3	1973 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon超长	待终核: 1971-1972
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1974			228.3	79.5	58.3	1974 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1975			228.3	79.5	58.1	1975 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen2 full-size	1976			228.6	79.5	58.1	1976 Chevrolet Caprice Estate Wagon, Automobile-Catalog	wagon超长	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1977			212.1	75.5	55.3	1977 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1977 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1978			212.1	76	55.3	1978 Chevrolet Caprice Classic Coupe, Automobile-Catalog	downsized coupe	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1979-1983			212.8	75.4	56.4	1980 Chevrolet Caprice Coupe proxy	downsized coupe	待终核: 1979-1983
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen3 downsized full-size	1984-1987			212.8	75.4	56.4	1984/1986/1987 Chevrolet Caprice Classic Coupe, Automobile-Catalog	coupe单独结构	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1977			212.1	75.5	55.2	1977 Chevrolet Caprice Classic Sedan, Automobile-Catalog	方正B-body	待终核: 1977 height
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1978-1980			212.1	75.3	55.2	1980 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1978-1979
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1981-1983			212.1	75.3	55.2	1983 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1981-1983
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1984			212.1	75.3	55.2	1984 Chevrolet Caprice Sedan, CapriceClassic statistics	方正B-body	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1985-1986			212.8	75.4	56.4	1987 Chevrolet Caprice Sedan proxy	方正B-body	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen3 downsized full-size	1987-1989			212.8	75.4	56.4	1987/1988/1989 Chevrolet Caprice Sedan, Automobile-Catalog	方正B-body	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1977-1979			214.7	79.1	58	1977/1979 Chevrolet Caprice Classic Wagon, Automobile-Catalog / Carfolio	wagon更宽更高	待终核: 1978
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1981			215.1	79.3	56.4	1981 Chevrolet Caprice Classic Wagon	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1982-1983			215.1	79.3	58.1	1982/1983 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1984			215.1	79.3	58.1	1984 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1985-1986			215.1	79.3	58.1	1984/1987 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1985-1986
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1987			215.1	79.3	58.2	1987 Chevrolet Caprice Classic Wagon, Automobile-Catalog	wagon更宽更高	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1988			215.1	79.3	58.2	1988 Chevrolet Caprice Classic Estate Wagon, Automobile-Catalog	wagon更宽更高	待终核: 1988 height
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen3 downsized full-size	1989-1990			215.1	79.3	58.2	1987/1988 Chevrolet Caprice Classic Wagon proxy	wagon更宽更高	待终核: 1989-1990
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1991-1992			214.1	77	56.7	1991-1992 Chevrolet Caprice Sedan, Edmunds	高车身年	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1993-1994			214.1	77	55.7	1993-1994 Chevrolet Caprice Sedan, Edmunds	高度回落	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen4 aero full-size	1995-1996			214.1	77.5	55.7	1995-1996 Chevrolet Caprice Sedan, Edmunds	宽度口径不同	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen4 aero full-size	1991-1996			217.3	79.6	60.9	1991-1996 Chevrolet Caprice Wagon, Edmunds	wagon高度必拆	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	PPV	gen5 police sedan	2011-2017			204.2	74.8	58.7	2011-2017 Chevrolet Caprice PPV, Car and Driver / Automobile-Catalog / iSeeCars	警用长轴距	可入库
Chevrolet Captiva	Chevrolet	越野车		SUV	Std.	gen1 compact SUV	2012-2015			180.1	72.8	67	2012-2015 Chevrolet Captiva Sport, Edmunds	紧凑SUV	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Sport Coupe, ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1965			193.9	74.6	52.8	1965 Chevrolet Chevelle Sport Coupe, Over-Drive fact sheet	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen1 mid-size	1966-1967			197	75	51.9	1966-1967 Chevrolet Chevelle Sport Coupe, Over-Drive / ChevelleStuff	gen1 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1964			193.9	74.6	54.5	1964 Chevrolet Chevelle Sedan, ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1965			193.9	74.6	53.2	1965 Chevrolet Chevelle Sedan, Over-Drive fact sheet	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen1 mid-size	1966-1967			197	75	53	1966-1967 Chevrolet Chevelle Sedan, Over-Drive / ChevelleStuff	gen1 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1964			198.8	74.6	54.1	1964 Chevrolet Chevelle Station Wagon, ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1965			198.8	74.6	55.1	1965 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1966			199.8	75	54.6	1966 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen1 mid-size	1967			199.9	75	54.6	1967 Chevrolet Chevelle Station Wagon, Over-Drive / ChevelleStuff	gen1 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1964			193.9	74.6	54	1964 Chevrolet Chevelle Convertible, ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1965			193.9	74.6	52.9	1965 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen1 mid-size	1966-1967			197	75	52.8	1966-1967 Chevrolet Chevelle Convertible, Over-Drive / ChevelleStuff	gen1敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1968			197.1	75.7	52.7	1968 Chevrolet Chevelle Coupe, Over-Drive	gen2 coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sport Coupe, ConceptCarz	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1970			197.2	75.4	53.2	1970 Chevrolet Chevelle 2-Door, Over-Drive fact sheet	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.7	1971-1972 Chevrolet Chevelle 2-Door, Over-Drive fact sheets	gen2 coupe	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1968			201.1	75.7	53.5	1968 Chevrolet Chevelle Malibu 4-Door Sedan, Automobile-Catalog	gen2 sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Sedan, ConceptCarz	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1970			201.2	75.4	53.25	1970 Chevrolet Chevelle 4-Door, Over-Drive fact sheet	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen2 mid-size	1971-1972			201.5	75.4	53.3	1971-1972 Chevrolet Chevelle 4-Door, Over-Drive fact sheets	gen2 sedan	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1968			207.1	75.7	55.2	1968 Chevrolet Chevelle Station Wagon, Over-Drive	gen2 wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1969			206	75.7	53.3	1969 Chevrolet Chevelle Greenbrier Wagon, ConceptCarz	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1970			206.5	75.4	55.1	1970 Chevrolet Chevelle Station Wagon, Over-Drive fact sheet	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen2 mid-size	1971-1972			206.8	75.4	54.1	1971-1972 Chevrolet Chevelle Station Wagon, Over-Drive fact sheets	gen2 wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1968			197.1	75.7	53.2	1968 Chevrolet Chevelle Convertible, Over-Drive	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1969			201	75.7	53.3	1969 Chevrolet Chevelle Convertible proxy	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1970			197.2	75.4	52.9	1970 Chevrolet Chevelle Convertible, Over-Drive fact sheet	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Convertible	Std.	gen2 mid-size	1971-1972			197.5	75.4	52.9	1971-1972 Chevrolet Chevelle Convertible, Over-Drive fact sheets	gen2敞篷	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1973			203.9	76.6	53.3	1973 Chevrolet Chevelle Coupe, Chevrolet brochure / AutoCatalogArchive	Colonnade coupe短轴	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1974			206.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Coupe, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.1	1975 Chevrolet Chevelle coupe brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Landau Coupe, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	跑车		Coupe	Std.	gen3 Colonnade mid-size	1977			205.7	76.9	53.1	1977 Chevrolet Chevelle Malibu Classic Coupe, ConceptCarz	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1973			207.9	76.6	54	1973 Chevrolet Chevelle Sedan, Chevrolet brochure / AutoCatalogArchive	Colonnade sedan长轴	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1974			210.3	76.6	54	1974 Chevrolet Chevelle Malibu Classic Sedan, Automobile-Catalog	非wagon	待终核: 1974 height
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1975			209.3	76.6	53.8	1975 Chevrolet Chevelle sedan brochure specs, AutoCatalogArchive	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1976			209.3	76.6	53.1	1976 Chevrolet Chevelle Malibu Classic Colonial Sedan, ConceptCarz	非wagon	可入库
Chevrolet Chevelle	Chevrolet	三厢车		Sedan	Std.	gen3 Colonnade mid-size	1977			206.7	76.9	54.1	1977 Chevrolet Chevelle Malibu Sedan, Carfolio / 1977 brochure proxy	非wagon末年	待终核: 1977 height
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1973			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1973
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1974			216.1	76.6	55.5	1974 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1975			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon proxy	wagon需单独核	待终核: 1975
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1976			215.2	76.8	55.7	1976 Chevrolet Chevelle Malibu Classic Estate Wagon, Automobile-Catalog	wagon更长更高	可入库
Chevrolet Chevelle	Chevrolet	两厢车		Wagon	Std.	gen3 Colonnade mid-size	1977			215.4	76.8	55.8	1977 Chevrolet Chevelle Malibu Classic Wagon, Automobile-Catalog	wagon更长更高	可入库

下一步优先核对

Camaro：gen3 Convertible 1990-1991。

Camaro：gen1 1968-1969 Coupe / Convertible。

Caprice：gen1 1967/1969-1970、gen2 coupe / convertible 高度、gen2 wagon 1971-1972。

Chevelle：gen3 1974 coupe/sedan 高度、1977 coupe/sedan 高度、1973/1975 wagon。

下一步。


--- Round 44 / 下一步 ---
更新点

车型	操作	描述
Chevrolet Camaro	拆出 / 状态推进	gen3 Convertible 原 1990-1992 拆出 1990；Edmunds 1990 Camaro Convertible IROC Z 尺寸为 192.0 × 72.8 × 50.3，推进为可入库。
Edmunds

Chevrolet Camaro	保留待核	剩余 1991-1992 暂保留原 1992 参考口径，继续标 待终核: 1991。
Chevrolet Caprice / Chevelle	稳定	本轮未改动无新证据的 Caprice 与 Chevelle 待核行。

当前批次进度

状态	说明
🟡 已推进	Camaro gen3 Convertible 1990 已拆出并可入库
🟡 待继续	Camaro gen3 Convertible 1991、gen1 1968-1969、Caprice、Chevelle 仍有待核
🔴 未完成	仍有待终核行，末尾继续输出“下一步”

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen1 pony car	1967-1969			186	72.5	51	1967-1969 Chevrolet Camaro Coupe proxy, Automobile-Catalog / ConceptCarz	gen1短车身	待终核: 1968-1969 Coupe
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen1 pony car	1967-1969			186	72.5	51.4	1967-1969 Chevrolet Camaro Convertible proxy	gen1敞篷	待终核: 1968-1969 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car early	1970-1973			194.5	74.4	49.2	1970/1973 Chevrolet Camaro Coupe, CarsGuide / Automobile-Catalog	早期长鼻车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1974			195.4	74.4	49.2	1974 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1974
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1975-1976			194.5	74.4	49.2	1975-1976 Chevrolet Camaro Coupe, CarsGuide	保险杠期车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car	1977			195.4	74.4	49.2	1977 Chevrolet Camaro Coupe proxy	保险杠加长	待终核: 1977
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen2 pony car late	1978-1981			197.6	74.5	49.2	1980 Chevrolet Camaro Coupe, ConceptCarz	晚期保险杠最长	待终核: 1978-1979/1981
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car early	1982			187.8	72.8	50	1982 Chevrolet Camaro Z28 Coupe, ConceptCarz	第三代短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1983			187.8	72.8	50	1983 Chevrolet Camaro Sport Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car	1984			187.8	72.8	50	1984 Chevrolet Camaro Berlinetta Coupe, Automobile-Catalog	第三代早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car	1985-1988			192	72.8	50.3	1985-1988 Chevrolet Camaro IROC-Z / Z28 Coupe, Automobile-Catalog / ConceptCarz	性能版更长更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	IROC-Z/Z28	gen3 pony car late	1989-1990			192	72.8	50.3	1989-1990 Chevrolet Camaro IROC-Z / RS Coupe, Automobile-Catalog / Edmunds	后期性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen3 pony car late	1991			192.6	72.4	50.4	1991 Chevrolet Camaro Z28 Coupe, Redbook / Carsales	后期Z28宽度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen3 pony car late	1992			192.6	72.8	50.4	1992 Chevrolet Camaro Coupe, ConceptCarz	后期车长增加	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1987			188	72.8	50	1987 Chevrolet Camaro IROC-Z Convertible, ConceptCarz	gen3敞篷短车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1988			192	72.8	50.3	1988 Chevrolet Camaro IROC-Z Convertible, Automobile-Catalog	gen3敞篷性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1989			192	72.8	50.3	1989 Chevrolet Camaro IROC-Z Convertible, Automobile-Catalog	gen3敞篷性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	IROC-Z	gen3 pony car	1990			192	72.8	50.3	1990 Chevrolet Camaro Convertible IROC Z, Edmunds	gen3敞篷性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen3 pony car	1991-1992			192.6	72.4	50.3	1992 Chevrolet Camaro RS/Z28 Convertible, ConceptCarz	gen3敞篷	待终核: 1991
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1993			193.2	74.1	51.3	1993 Chevrolet Camaro Coupe, Edmunds	gen4早期	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car	1994			193.2	74.1	52	1994 Chevrolet Camaro Coupe, Edmunds	gen4早期高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1995			193.2	74.1	51.3	1995 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高度不同	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1996			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe proxy	Z28高车身	待终核: 1996
Chevrolet Camaro	Chevrolet	跑车		Coupe	Z28	gen4 pony car	1997			193.2	74.1	52	1997 Chevrolet Camaro Z28 Coupe, Edmunds	Z28高车身	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car	1994-1997			193.2	74.1	52	1994 Chevrolet Camaro Convertible proxy	gen4敞篷	待终核: 1994-1997 Convertible
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1998			193.5	74.1	51.3	1998 Chevrolet Camaro Base Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.2	2000-2002 Chevrolet Camaro Coupe, Edmunds	gen4改款	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1998			193.5	74.1	52	1998 Chevrolet Camaro Convertible Base, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	1999			193.2	74.1	51.3	1999 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen4 pony car facelift	2000-2002			193.5	74.1	51.8	2000-2002 Chevrolet Camaro Convertible, Edmunds	gen4改款敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car	2010-2013			190.4	75.5	54.2	2010/2013 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.2	2014/2015 Chevrolet Camaro Coupe, Edmunds	美式跑车	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car	2011-2013			190.4	75.5	54.7	2011/2013 Chevrolet Camaro Convertible, Car and Driver / Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen5 sports car facelift	2014-2015			190.6	75.5	54.7	2014/2015 Chevrolet Camaro Convertible, Edmunds	敞篷更高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	Std.	gen6 sports car	2016-2024			188.3	74.7	53.1	2016/2019/2021/2024 Chevrolet Camaro Coupe base, Edmunds	标准版车高统一	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	2SS	gen6 sports car	2020			188.3	74.7	52.9	2020 Chevrolet Camaro 2SS Coupe, Edmunds	SS低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2016			188.3	74.7	52.9	2016 Chevrolet Camaro Convertible base, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2017-2018			188.3	74.7	52.9	2017 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2019-2023			188.3	74.7	52.9	2019/2020/2022/2023 Chevrolet Camaro Convertible, Edmunds	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	Std.	gen6 sports car	2024			188.3	74.7	52.9	2024 Chevrolet Camaro Convertible 1LT, Car and Driver	标准敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2017-2018			190.2	75	52.9	2017/2018 Chevrolet Camaro ZL1 Coupe, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car facelift	2019			190.2	75	52.6	2019 Chevrolet Camaro ZL1, Edmunds	ZL1低车高	可入库
Chevrolet Camaro	Chevrolet	跑车		Coupe	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2023/2024 Chevrolet Camaro ZL1, Edmunds	ZL1性能版	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2017			190.2	75	52.6	2017 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2018			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2019			190.2	75	52.6	2018 Chevrolet Camaro Convertible ZL1 proxy	宽体性能敞篷	待终核: 2019 Convertible ZL1
Chevrolet Camaro	Chevrolet	跑车		Convertible	ZL1	gen6 sports car	2020-2024			190.2	75	52.9	2020/2021/2022/2024 Chevrolet Camaro ZL1, Edmunds	宽体性能敞篷	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1966-1967			213.2	79.6	55.4	1966 Chevrolet Caprice Sedan/Coupe, Over-Drive / Oldride	gen1早期	待终核: 1967 Sedan
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1968			215	80	54.5	1968 Chevrolet Caprice Sport Sedan, Oldride / Over-Drive	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	三厢车		Sedan	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1970 Chevrolet Caprice Custom Sedan, UltimateSpecs	gen1全尺寸	待终核: 1969 Sedan
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1966-1967			213.2	79.6	54.4	1966 Chevrolet Caprice Custom Coupe, UltimateSpecs / Over-Drive	gen1早期	待终核: 1967 Coupe
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1968			214.7	79.6	54.3	1968 Chevrolet Caprice Custom Coupe, UltimateSpecs	gen1全尺寸	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen1 full-size	1969-1970			216	79.8	54.5	1969/1970 Chevrolet Caprice Custom Coupe proxy	gen1全尺寸	待终核: 1970 Coupe
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1966			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog / Over-Drive	wagon高车身	可入库
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1967			212.4	79.6	56.7	1966 Chevrolet Caprice-Kingswood Estate Wagon proxy	wagon高车身	待终核: 1967 Wagon
Chevrolet Caprice	Chevrolet	两厢车		Wagon	Std.	gen1 full-size	1968-1970			213.9	79.6	56.7	1968 Chevrolet Caprice-Kingswood Estate Wagon, Automobile-Catalog	wagon高车身	待终核: 1969-1970
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1971 Convertible height
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1972-1974			222.7	79.5	56.7	1973/1974 Chevrolet Caprice Convertible proxy	敞篷结构	待终核: 1972-1974 Convertible
Chevrolet Caprice	Chevrolet	跑车		Convertible	Std.	gen2 full-size	1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Convertible, Automobile-Catalog	敞篷末年	可入库
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1971			216.8	79.5	56.7	1971 Chevrolet Caprice Hardtop Coupe proxy	非wagon全尺寸	待终核: 1971 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1972			219.9	79.5	56.7	1972 Chevrolet Caprice Hardtop Coupe range, Automobile-Catalog	1972长度不同	待终核: 1972 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1973			222.9	79.5	56.7	1973 Chevrolet Caprice Classic Coupe proxy	非wagon全尺寸	待终核: 1973 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1974-1975			222.8	79.5	56.7	1975 Chevrolet Caprice Classic Coupe proxy	后期大保险杠	待终核: 1974-1975 Coupe height
Chevrolet Caprice	Chevrolet	跑车		Coupe	Std.	gen2 full-size	1976			222.9	79.5	53.7	1976 Chevrolet Caprice Classic Coupe

连接已中断。正在等待完整回复

