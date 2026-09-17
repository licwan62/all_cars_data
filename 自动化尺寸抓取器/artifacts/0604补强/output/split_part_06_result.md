# 文件名：split_part_06.tsv


--- Round 1 / 首次发送 ---
更新点

已确认并推进：Buick Lucerne 2006-2011、Buick Rainier 2004-2007 可覆盖整段；尺寸均来自 Edmunds 年款页。
Edmunds
+6
Edmunds
+6
Edmunds
+6

已确认并推进：Buick Park Avenue gen1 / gen2 关键年份尺寸；但 gen1 1992/1994 仍显示宽度口径差异，需要继续补强，不直接全段可入库。
Edmunds
+5
Edmunds
+5
Edmunds
+5

已确认并推进：Buick LeSabre 1992-1999、2000-2005 sedan 区间；2000/2005 同尺寸可直接覆盖，1992-1996 与 1997-1999 已拆为两个区间。
Edmunds
+6
Edmunds
+6
Edmunds
+6

按代际完整性要求新增 LeSabre 缺失代际占位行：gen1、gen2 非 wagon、gen4、gen5/6 缺口；这些仍为待终核，不能标完成。

当前批次进度

状态	车型	说明
🟢 已推进	Lucerne / Rainier	本轮已覆盖整段，可入库
🟡 部分推进	LeSabre / Park Avenue	后期 sedan 已推进，早期 LeSabre 与 Park Avenue gen1 仍需补强
🔴 待补强	LeSabre 缺失代际	已新增占位行，但尺寸/年份/结构未完全核定

本轮更新后的 TSV：

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960						早期全尺寸coupe	待终核: 缺失 gen1 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960						早期全尺寸敞篷	待终核: 缺失 gen1 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1964						全尺寸coupe	待终核: 缺失 gen2 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1964						全尺寸敞篷	待终核: 缺失 gen2 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon Automobile-Catalog / 1961 height proxy	高车顶wagon	待终核: 1962-1963 Wagon高度	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967-1969			218.2	80	55.3	1967-1969 Buick LeSabre convertible refs	宽体全尺寸	待终核: 1967-1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre coupe refs	宽体全尺寸	待终核: Coupe结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre	宽体全尺寸	待补强: 1965-1966	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1976						大型化sedan	待终核: 缺失 gen4 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1976						大型化coupe	待终核: 缺失 gen4 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1974						大型敞篷	待终核: 缺失 gen4 Convertible 1970-1974 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1981						RWD downsized sedan	待终核: 缺失 gen5 Sedan 1977-1981 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980						RWD downsized coupe	待终核: 缺失 gen5 Coupe 1977-1980 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981-1985			218.4	75.2	55	1985 Buick LeSabre Coupe proxy	RWD downsized coupe	待终核: 1981-1984 Coupe	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986-1988						FWD缩小sedan	待终核: 缺失 gen6 Sedan 1986-1988 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Edmunds height proxy	FWD缩小	待终核: 1989 Sedan高度	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990-1991						FWD缩小sedan	待终核: 缺失 gen6 Sedan 1990-1991 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986-1991			196.5	72.4	53.8	1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	待终核: 1986-1990 Coupe	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.5	76	55.5	1991 Buick Park Avenue Automobile-Catalog / EncyCarpedia	早期FWD luxury sedan	待终核: 1991宽度口径交叉	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992-1994			205.2	74.9	55.1	1993/1994 Buick Park Avenue Edmunds	大型FWD sedan	待终核: 1992宽度	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997			206.8	74.7	57.4	1997 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1998-1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	待终核: 1998	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2005 Buick Park Avenue Edmunds / Automobile-Catalog	高度增加	待终核: 2000-2004	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

Buick LeSabre gen1 / gen2 / gen4 缺失代际。

Buick LeSabre gen5/gen6 早期 sedan/coupe/wagon 缺失年份。

Buick Park Avenue 1991-1994 / 1998-2004 的宽度口径与覆盖年份。

下一步


--- Round 2 / 下一步 ---
更新点

LeSabre gen6 已进一步拆分：1986-1988 Sedan 改为独立待终核行，1989-1990 Sedan 按 Edmunds 1990 + 1989 原参考合并推进，1991 Sedan 单独拆出。Edmunds 显示 1990 LeSabre Sedan 为 196.5 / 72.4 / 54.9，1991 Sedan 为 196.5 / 72.4 / 54.6。
Edmunds
+1

LeSabre gen6 Coupe 补强为 1991 Edmunds 实核尺寸，仍保留 1986-1990 待终核。Edmunds 1991 Coupe 为 196.5 / 72.4 / 53.8。
Edmunds

Park Avenue gen1 拆细：1992 单独可入库；1993-1994 仍待 1994 终核；1995-1996 保持可入库。Edmunds 显示 1992 为 205.3 / 73.6 / 55.1，1996 为 205.9 / 74.1 / 55.1。
Edmunds
+1

Park Avenue gen2 推进：1997 单独可入库，2000-2005 改为可入库；1998 仍缺，1999 单独可入库。Edmunds 显示 1997、2000、2004、2005 为 206.8 / 74.7 / 57.4，1999 为 206.8 / 74.4 / 57.4。
Edmunds
+4
Edmunds
+4
Edmunds
+4

当前批次进度

状态	车型	说明
🟢 已完成较多	Lucerne / Rainier / LeSabre 1992-2005 Sedan	已有整段参考车型覆盖，可入库
🟡 继续补强	Park Avenue	gen2 大部分完成，1993-1994/1998 仍待终核
🔴 待补强	LeSabre 1959-1988 多结构	缺失 gen1/gen2/gen4、gen5 早期、gen6 早期 Sedan/Coupe 全量数据

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960						早期全尺寸coupe	待终核: 缺失 gen1 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960						早期全尺寸敞篷	待终核: 缺失 gen1 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1964						全尺寸coupe	待终核: 缺失 gen2 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1964						全尺寸敞篷	待终核: 缺失 gen2 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon Automobile-Catalog / 1961 height proxy	高车顶wagon	待终核: 1962-1963 Wagon高度	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967-1969			218.2	80	55.3	1967-1969 Buick LeSabre convertible refs	宽体全尺寸	待终核: 1967-1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre coupe refs	宽体全尺寸	待终核: Coupe结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre	宽体全尺寸	待补强: 1965-1966	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1976						大型化sedan	待终核: 缺失 gen4 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1976						大型化coupe	待终核: 缺失 gen4 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1974						大型敞篷	待终核: 缺失 gen4 Convertible 1970-1974 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1981						RWD downsized sedan	待终核: 缺失 gen5 Sedan 1977-1981 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980						RWD downsized coupe	待终核: 缺失 gen5 Coupe 1977-1980 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981-1985			218.4	75.2	55	1985 Buick LeSabre Coupe proxy	RWD downsized coupe	待终核: 1981-1984 Coupe	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986-1988			196.5	72.1	55.5	1986-1988 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	待终核: Edmunds逐年复核 1986-1988	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986-1990			196.5	72.4	53.8	1991 Buick LeSabre Coupe Edmunds / 1987 Coupe UltimateSpecs	FWD coupe低车顶	待终核: 1986-1990 Coupe Edmunds逐年复核	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1991			196.5	72.4	53.8	1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.5	76	55.5	1991 Buick Park Avenue Automobile-Catalog / EncyCarpedia	早期FWD luxury sedan	待终核: 1991宽度口径交叉	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993-1994			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	待终核: 1994	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997			206.8	74.7	57.4	1997 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1998			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds proxy	高度增加	待终核: 1998	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1/gen2/gen4：补 1959-1976 Sedan / Coupe / Convertible / Wagon 的真实尺寸。

LeSabre gen5：补 1977-1985 Sedan / Coupe / Wagon 缺失年份，重点 1977-1984。

LeSabre gen6：核 1986-1988 Sedan 与 1986-1990 Coupe 的 Edmunds/权威逐年口径。

Park Avenue：补 1991 宽度口径、1994、1998。

下一步


--- Round 3 / 下一步 ---
更新点

Park Avenue gen1 已拆细：1993 与 1994 尺寸不同，不能合并；1994 已按 Edmunds 改为 205.2 / 73.6 / 55.1，可入库。
Edmunds
+1

Park Avenue gen2 已清掉 1998 缺口：1997-1998 同为 206.8 / 74.7 / 57.4，可压缩为一行；1999 保持单独行，因为宽度为 74.4。
Edmunds
+2
Edmunds
+2

LeSabre gen6 Coupe 已拆细：1987-1988 Coupe 按 Automobile-Catalog 核到 196.5 / 72.1 / 54.7；1989 Coupe 按 Automobile-Catalog 核到 196.9 / 72.4 / 54.7；1991 Coupe 保持 Edmunds 可入库。
automobile-catalog.com
+2
automobile-catalog.com
+2

LeSabre gen6 Coupe 1986 / 1990 仍未完整覆盖，保留待终核占位，不强行压缩。

当前批次进度

状态	车型	说明
🟢 可入库	Lucerne / Rainier / Park Avenue 1992-2005 大部分 / LeSabre 1991-2005 部分	已有对应年份或区间参考车型覆盖
🟡 待少量补强	Park Avenue 1991	主要是 1991 宽度口径交叉
🔴 待重点补强	LeSabre 1959-1990 多结构	gen1/gen2/gen4/gen5、gen6 1986/1990 Coupe 与早期 Sedan 仍待终核

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960						早期全尺寸coupe	待终核: 缺失 gen1 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960						早期全尺寸敞篷	待终核: 缺失 gen1 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1964						全尺寸coupe	待终核: 缺失 gen2 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1964						全尺寸敞篷	待终核: 缺失 gen2 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon Automobile-Catalog / 1961 height proxy	高车顶wagon	待终核: 1962-1963 Wagon高度	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967-1969			218.2	80	55.3	1967-1969 Buick LeSabre convertible refs	宽体全尺寸	待终核: 1967-1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre coupe refs	宽体全尺寸	待终核: Coupe结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre	宽体全尺寸	待补强: 1965-1966	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1976						大型化sedan	待终核: 缺失 gen4 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1976						大型化coupe	待终核: 缺失 gen4 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1974						大型敞篷	待终核: 缺失 gen4 Convertible 1970-1974 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1981						RWD downsized sedan	待终核: 缺失 gen5 Sedan 1977-1981 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980						RWD downsized coupe	待终核: 缺失 gen5 Coupe 1977-1980 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981-1985			218.4	75.2	55	1985 Buick LeSabre Coupe proxy	RWD downsized coupe	待终核: 1981-1984 Coupe	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986-1988			196.5	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs / 1988 CarGurus dimensions	早期FWD sedan	待终核: 1987-1988 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986						FWD coupe低车顶	待终核: 1986 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.5	72.1	54.7	1987-1988 Buick LeSabre Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990						FWD coupe低车顶	待终核: 1990 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1991			196.5	72.4	53.8	1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.5	76	55.5	1991 Buick Park Avenue Automobile-Catalog / EncyCarpedia	早期FWD luxury sedan	待终核: 1991宽度口径交叉	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1/gen2/gen4：1959-1976 Sedan / Coupe / Convertible / Wagon。

LeSabre gen5：1977-1985 Sedan / Coupe / Wagon，重点补 1977-1984。

LeSabre gen6：1986 Coupe、1990 Coupe、1987-1988 Sedan 高度口径。

Park Avenue：只剩 1991 宽度口径交叉需要终核。

下一步


--- Round 4 / 下一步 ---
更新点

Park Avenue 1991 已改为 Edmunds 口径：205.2 / 74.9 / 55.7，1991 单年可入库；同时保留参考中 Automobile-Catalog 73.6 宽度差异说明到备注。Edmunds 明确给出 1991 Park Avenue 的 Length 205.2、Overall width without mirrors 74.9、Height 55.7。
Edmunds
+1

LeSabre gen6 1986 Coupe 已补为 196.2 / 72.1 / 54.7，参考 Carfolio；1990 Coupe 已补为 196.5 / 72.4 / 53.8，参考 AutoDetective。
车目录
+1

LeSabre gen6 Coupe 1986-1988 可压缩：三维一致或四舍五入口径一致，改为可入库；1989 单独保留，因为长度/宽度不同；1990-1991 可压缩为一行。

LeSabre gen5 1981-1985 Coupe 已用 1984 UltimateSpecs 与 1985 iSeeCars/原 proxy 交叉推进，但 1981-1983 仍未完整逐年覆盖，所以保留待终核。
ultimatespecs.com
+1

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Rainier / Buick Park Avenue	Park Avenue 1991-2005 已全段可入库
🟡 大幅推进	Buick LeSabre gen6	Coupe 1986-1991 已基本可入库；Sedan 1986-1990 仍有部分口径待终核
🔴 待补强	Buick LeSabre 1959-1985	gen1/gen2/gen4/gen5 仍有较多早期结构/年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960						早期全尺寸coupe	待终核: 缺失 gen1 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960						早期全尺寸敞篷	待终核: 缺失 gen1 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1964						全尺寸coupe	待终核: 缺失 gen2 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1964						全尺寸敞篷	待终核: 缺失 gen2 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon Automobile-Catalog / 1961 height proxy	高车顶wagon	待终核: 1962-1963 Wagon高度	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967-1969			218.2	80	55.3	1967-1969 Buick LeSabre convertible refs	宽体全尺寸	待终核: 1967-1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre coupe refs	宽体全尺寸	待终核: Coupe结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre	宽体全尺寸	待补强: 1965-1966	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1976						大型化sedan	待终核: 缺失 gen4 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1976						大型化coupe	待终核: 缺失 gen4 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1974						大型敞篷	待终核: 缺失 gen4 Convertible 1970-1974 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1981						RWD downsized sedan	待终核: 缺失 gen5 Sedan 1977-1981 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980						RWD downsized coupe	待终核: 缺失 gen5 Coupe 1977-1980 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981-1985			218.4	75.9	56	1984 Buick LeSabre Coupe UltimateSpecs / 1985 Buick LeSabre Coupe iSeeCars	RWD downsized coupe	待终核: 1981-1983 Coupe	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986-1988			196.5	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs / 1988 CarGurus dimensions	早期FWD sedan	待终核: 1987-1988 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986-1988			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio / 1987-1988 Buick LeSabre Coupe UltimateSpecs	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1 / gen2 / gen4：1959-1976 Sedan、Coupe、Convertible、Wagon。

LeSabre gen5：1977-1985 Sedan / Coupe / Wagon，优先 1977-1981 Sedan、1977-1980 Coupe、1978-1984 Wagon。

LeSabre gen6：1986-1988 Sedan 高度口径、1989 Sedan 长度差异。

下一步


--- Round 5 / 下一步 ---
更新点

LeSabre gen5 Sedan 已拆细：1977-1978、1979-1980、1981、1982-1985 分段处理，避免把 1977-1985 不同长宽高强行压缩。1977 Sedan 为 218.2 / 77.2 / 55.3；1979 Sedan 为 218.2 / 77.2 / 55.7；1980 Sedan 为 217.4 / 78.0 / 55.0；1981 Sedan 为 218.4 / 75.9 / 55.0。
Ultimate Specs
+3
Ultimate Specs
+3
汽车目录
+3

LeSabre gen5 Coupe 已拆细：1977-1980、1981-1982、1983-1985 分段；1984 Coupe 口径显示 218.39 / 75.91，1983-1985 可作为一段继续推进，但 1981-1982 仍待逐年交叉。
汽车目录
+2
Ultimate Specs
+2

LeSabre gen5 Wagon 保持 1977 与 1978-1985 分段；1985 Estate Wagon 为 220.3 / 79.8 / 58.5，1977 Estate Wagon 为 216.7 / 79.9。
汽车目录
+1

LeSabre gen4 已先补 1975-1976 Sedan/Coupe 关键口径：1975-1976 Sedan 为 226.81 / 79.88 / 54.02，1975-1976 Coupe 为 226.81 / 79.88 / 53.19；1970-1974 仍需补强。
Ultimate Specs
+1

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 大幅推进	Buick LeSabre gen5 / gen6	gen5 已按尺寸变化拆段；gen6 Coupe 已可入库，Sedan 仍有 1986-1990 口径缺口
🔴 待补强	Buick LeSabre gen1/gen2/gen3/gen4	1959-1976 多结构仍未全部完成

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960						早期全尺寸coupe	待终核: 缺失 gen1 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960						早期全尺寸敞篷	待终核: 缺失 gen1 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961			214.1	77.9	56.4	1961 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	待终核: 1962-1964 Coupe全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1964						全尺寸敞篷	待终核: 缺失 gen2 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon Automobile-Catalog / 1961 height proxy	高车顶wagon	待终核: 1962-1963 Wagon高度	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967-1969			218.2	80	55.3	1967-1969 Buick LeSabre convertible refs	宽体全尺寸	待终核: 1967-1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre coupe refs	宽体全尺寸	待终核: Coupe结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1969			218.2	80	55.3	1967-1969 Buick LeSabre	宽体全尺寸	待补强: 1965-1966	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	待终核: 1970-1971 Sedan		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973-1974						大型化sedan	待终核: 1973-1974 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1974						大型化coupe	待终核: 1970-1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1974						大型敞篷	待终核: 缺失 gen4 Convertible 1970-1974 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1978-1980 Coupe	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981-1982			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	待终核: 1981 Coupe	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1983-1985			218.4	75.9	56	1984 Buick LeSabre Coupe UltimateSpecs / 1985 Buick LeSabre Coupe iSeeCars	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986-1988			196.5	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs / 1988 CarGurus dimensions	早期FWD sedan	待终核: 1987-1988 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986-1988			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio / 1987-1988 Buick LeSabre Coupe UltimateSpecs	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Coupe / Convertible / Wagon。

LeSabre gen2：1961-1964 Sedan / Convertible，以及 1963-1964 Coupe。

LeSabre gen3：1965-1969 Sedan / Coupe / Convertible 结构与高度口径。

LeSabre gen4：1970-1974 Sedan / Coupe / Convertible / Wagon，1973-1974 Sedan 尺寸缺口。

LeSabre gen5：1982-1984 Sedan、1978-1980 Coupe、1978-1984 Wagon。

下一步


--- Round 6 / 下一步 ---
更新点

LeSabre gen2 Coupe 已从原来的 1961 / 1962 单年分散状态，整理为 1961-1962 可入库行；1963-1964 因 roofline/车身变化仍单独保留待终核。

LeSabre gen2 Convertible 新增 1963 单年实核行，尺寸为 215.71 / 77.99 / 55.59；1961-1962、1964 仍待终核。
Ultimate Specs

LeSabre gen3 Sedan / Coupe 不再整段 1965-1969 混压：已拆出 1969 Sedan、1969 Coupe 单年可入库；1965-1968 继续待终核，避免未覆盖年份被误标可入库。
车目录
+2
Ultimate Specs
+2

LeSabre gen2 Wagon 1963 长度已有 ConceptCarz 佐证为 215.7；但宽/高仍需终核，所以仍不改为可入库。
conceptcarz.com

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 已推进	Buick LeSabre gen2/gen3/gen5/gen6	本轮新增 gen2 Convertible 1963、gen3 1969 Sedan/Coupe 可入库
🔴 待补强	Buick LeSabre gen1/gen2部分/gen3早期/gen4/gen5部分	仍有 1959-1968、1970-1974、部分 1977-1985 结构待终核

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960						早期全尺寸coupe	待终核: 缺失 gen1 Coupe 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960						早期全尺寸敞篷	待终核: 缺失 gen1 Convertible 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963-1964						全尺寸coupe	待终核: 1963-1964 Coupe全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964						全尺寸敞篷	待终核: 1964 Convertible全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967-1969			218.2	80	55.3	1967-1969 Buick LeSabre convertible refs	宽体全尺寸	待终核: 1967-1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	待终核: 1970-1971 Sedan		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973-1974						大型化sedan	待终核: 1973-1974 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1974						大型化coupe	待终核: 1970-1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1974						大型敞篷	待终核: 缺失 gen4 Convertible 1970-1974 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1978-1980 Coupe	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981-1982			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	待终核: 1981 Coupe	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1983-1985			218.4	75.9	56	1984 Buick LeSabre Coupe UltimateSpecs / 1985 Buick LeSabre Coupe iSeeCars	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986-1988			196.5	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs / 1988 CarGurus dimensions	早期FWD sedan	待终核: 1987-1988 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986-1988			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio / 1987-1988 Buick LeSabre Coupe UltimateSpecs	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Coupe / Convertible / Wagon。

LeSabre gen2：1961-1964 Sedan、1963-1964 Coupe、1961-1962/1964 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965-1969 Convertible。

LeSabre gen4：1970-1974 Sedan / Coupe / Convertible / Wagon，1973-1974 Sedan 尺寸缺口。

LeSabre gen5：1982-1984 Sedan、1978-1980 Coupe、1978-1984 Wagon。

下一步


--- Round 7 / 下一步 ---
更新点

LeSabre gen1 Coupe / Convertible 已补 1959-1960：UltimateSpecs 显示 1959-1960 2-Door Sedan 与 Convertible 长宽高均为 217.91 / 80 / 57.2，本轮改为可入库。
Ultimate Specs
+1

LeSabre gen2 Coupe 1963-1964 已补齐：1963 Sport Coupe 为 215.71 / 77.99 / 56.69；1964 Sport Coupe 为 218.82 / 77.99，按最大长度压成 1963-1964，因 1964 高度仍需交叉，保留待终核。
Ultimate Specs
+1

LeSabre gen4 Coupe / Convertible 1972 已补关键实核：1972 Sport Coupe 为 221.9 / 80 / 53.5，1972 Convertible 为 221.89 / 80 / 53.94；仍缺 1970-1971/1973-1974，不能整段可入库。
汽车目录
+1

LeSabre gen6 Sedan 1986-1988 已推进：1986 Sedan 实核为 196.18 / 72.09 / 55.51，保留 1987-1988 待终核，但数值口径更明确。
Ultimate Specs

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 大幅推进	Buick LeSabre gen1/gen2/gen5/gen6	gen1 Coupe/Convertible 已可入库，gen2 Coupe/Convertible 增加实核行
🔴 待补强	Buick LeSabre gen1 Sedan/Wagon、gen3、gen4、gen5 Wagon	仍有早期 Sedan/Wagon 和 1970-1974 多结构缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80	57.2	1959-1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80	57.2	1959-1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963-1964			218.8	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs / 1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	待终核: 1964 Coupe高度交叉	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964						全尺寸敞篷	待终核: 1964 Convertible全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	待终核: 1970-1971 Sedan	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973-1974						大型化sedan	待终核: 1973-1974 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971						大型化coupe	待终核: 1970-1971 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973-1974						大型化coupe	待终核: 1973-1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1971						大型敞篷	待终核: 1970-1971 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1978-1980 Coupe	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981-1982			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	待终核: 1981 Coupe	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1983-1985			218.4	75.9	56	1984 Buick LeSabre Coupe UltimateSpecs / 1985 Buick LeSabre Coupe iSeeCars	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987-1988			196.5	72.1	55.5	1988 Buick LeSabre Sedan CarGurus dimensions	早期FWD sedan	待终核: 1987 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986-1988			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio / 1987-1988 Buick LeSabre Coupe UltimateSpecs	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1961-1964 Sedan、1961-1962/1964 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1970-1971/1973-1974 Sedan、Coupe、Convertible，以及 1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1978-1980 Coupe、1978-1984 Wagon。

下一步


--- Round 8 / 下一步 ---
更新点

LeSabre gen2 Coupe 不再把 1963-1964 压成一行：1963 与 1964 长度/高度不同，已拆成 1963、1964 两条并分别标可入库。UltimateSpecs 给出 1963 Sport Coupe 为 215.71 / 77.99 / 56.69，1964 Sport Coupe 为 218.82 / 77.99 / 56.42。
Ultimate Specs
+1

LeSabre gen4 Sedan 不再把 1970-1972 混压：1972 已单独拆出可入库，1970-1971 保留待终核。UltimateSpecs 给出 1972 4-Door Sedan 为 221.89 / 80 / 54.33。
Ultimate Specs

LeSabre gen5 Coupe 1981-1982 已拆开：1982 单年可入库，1981 仍待终核。UltimateSpecs 给出 1982 Coupe 为 218.39 / 75.91。
Ultimate Specs

LeSabre gen5 Sedan 1980 / 1981 继续保持单独可入库：1980 与 1981 长宽高不同，不能压缩。
Ultimate Specs
+1

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen2 / gen4 / gen5 / gen6	本轮减少 1963-1964 Coupe、1972 Sedan、1982 Coupe 待终核
🔴 待补强	Buick LeSabre gen1、gen2 Sedan/Convertible/Wagon、gen3、gen4 部分、gen5 Wagon	仍有多结构/年份未完全核完

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80	57.2	1959-1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80	57.2	1959-1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964						全尺寸敞篷	待终核: 1964 Convertible全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1971						大型化sedan	待终核: 1970-1971 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973-1974						大型化sedan	待终核: 1973-1974 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971						大型化coupe	待终核: 1970-1971 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973-1974						大型化coupe	待终核: 1973-1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1971						大型敞篷	待终核: 1970-1971 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1978-1980 Coupe	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981						RWD downsized coupe	待终核: 1981 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1983-1985			218.4	75.9	56	1984 Buick LeSabre Coupe UltimateSpecs / 1985 Buick LeSabre Coupe iSeeCars	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987-1988			196.5	72.1	55.5	1988 Buick LeSabre Sedan CarGurus dimensions	早期FWD sedan	待终核: 1987 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986-1988			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio / 1987-1988 Buick LeSabre Coupe UltimateSpecs	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1961-1964 Sedan、1961-1962/1964 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1970-1971/1973-1974 Sedan、Coupe、Convertible，以及 1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1978-1980 Coupe、1981 Coupe、1978-1984 Wagon。

下一步


--- Round 9 / 下一步 ---
更新点

LeSabre gen5 Coupe 已继续补强：1982 单年与 1983-1985 同为 218.39 / 75.91 / 55.98，可合并为 1982-1985 可入库；1981 仍缺实核，单独保留待终核。UltimateSpecs 1982 Coupe 与 1983-1985 Coupe 均给出相同长宽高口径。
Ultimate Specs
+1

LeSabre gen6 Coupe 已修正 1987-1988 宽度口径：1987 Coupe 数据为 196.85 / 72.44 / 54.69，因此不再沿用 72.1 宽度；本轮拆为 1986、1987-1988、1989、1990-1991。
Ultimate Specs
+1

LeSabre gen2 Coupe 1961-1962、1963、1964 继续保持拆分，因为 1961-1962、1963、1964 长度/高度不同，不能跨段压缩。
Ultimate Specs
+2
Ultimate Specs
+2

LeSabre gen4 Coupe 新增 1971 关键实核口径，1971 Sport Coupe 宽 79.69、高 53.58；但长度未在摘要中完整显示，仍保留待终核，不强行可入库。
Ultimate Specs

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen2 / gen5 / gen6	gen5 Coupe 1982-1985 已可入库；gen6 Coupe 口径修正
🔴 待补强	Buick LeSabre gen1、gen2 Sedan/Convertible/Wagon、gen3、gen4、gen5 Wagon	仍有早期多结构缺口，不能输出完成

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80	57.2	1959-1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80	57.2	1959-1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964						全尺寸敞篷	待终核: 1964 Convertible全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1971						大型化sedan	待终核: 1970-1971 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973-1974						大型化sedan	待终核: 1973-1974 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970						大型化coupe	待终核: 1970 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1971			221.9	79.7	53.6	1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	待终核: 1971 Coupe长度交叉	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973-1974						大型化coupe	待终核: 1973-1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1971						大型敞篷	待终核: 1970-1971 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977-1980			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1978-1980 Coupe	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981						RWD downsized coupe	待终核: 1981 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987-1988			196.5	72.1	55.5	1988 Buick LeSabre Sedan CarGurus dimensions	早期FWD sedan	待终核: 1987 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987 Buick LeSabre Coupe UltimateSpecs / 1988 Coupe proxy	FWD coupe低车顶	待终核: 1988 Coupe逐年交叉	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1961-1964 Sedan、1961-1962/1964 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1970-1971/1973-1974 Sedan、1970/1973-1974 Coupe、Convertible、1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1978-1980 Coupe、1981 Coupe、1978-1984 Wagon。

下一步


--- Round 10 / 下一步 ---
更新点

LeSabre gen1 Coupe / Convertible 修正宽度：1959 口径宽度为 80.71 in，1960 为 80.0 in，因此 1959-1960 压缩行采用最大宽度 80.7，避免低估车衣宽度。
Ultimate Specs
+1

LeSabre gen5 Coupe 1977-1980 不再整段混压：1978-1979 已按 218.2 / 77.2 / 55.0 可入库；1977 与 1980 仍保留单独待终核，避免未覆盖年份误标可入库。
Ultimate Specs
+2
Ultimate Specs
+2

LeSabre gen2 Coupe 1964 保持可入库，1964 Sport Coupe 为 218.82 / 77.99 / 56.42；与 1963 不同，继续独立行。
Ultimate Specs

LeSabre gen4 Coupe 1973 新增实核行：1973 Hardtop Coupe 为 224.21 / 79.61 / 53.58，不能和 1972 或 1975-1976 合并。
Ultimate Specs

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 持续推进	Buick LeSabre gen1 / gen2 / gen4 / gen5 / gen6	本轮新增 gen4 Coupe 1973、gen5 Coupe 1978-1979 可入库
🔴 待补强	Buick LeSabre gen1 Sedan/Wagon、gen2 Sedan/部分 Convertible/Wagon、gen3、gen4 部分、gen5 Wagon	仍有多结构/年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959-1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961-1964						全尺寸sedan	待终核: 缺失 gen2 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964						全尺寸敞篷	待终核: 1964 Convertible全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970-1971						大型化sedan	待终核: 1970-1971 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973-1974						大型化sedan	待终核: 1973-1974 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970						大型化coupe	待终核: 1970 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1971			221.9	79.7	53.6	1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	待终核: 1971 Coupe长度交叉	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974						大型化coupe	待终核: 1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1971						大型敞篷	待终核: 1970-1971 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980						RWD downsized coupe	待终核: 1980 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981						RWD downsized coupe	待终核: 1981 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987-1988			196.5	72.1	55.5	1988 Buick LeSabre Sedan CarGurus dimensions	早期FWD sedan	待终核: 1987 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987 Buick LeSabre Coupe UltimateSpecs / 1988 Coupe proxy	FWD coupe低车顶	待终核: 1988 Coupe逐年交叉	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1961-1964 Sedan、1961-1962/1964 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1970-1971 / 1973-1974 Sedan，1970 / 1974 Coupe，1970-1971 / 1973-1974 Convertible，1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1977 高度、1980-1981 Coupe、1978-1984 Wagon。

下一步


--- Round 11 / 下一步 ---
更新点

LeSabre gen2 Sedan 已补 1961、1964 两个关键年份：1961 4-Door Hardtop 为 213.19 / 77.99 / 56.3，1964 4-Door Sedan 为 218.82 / 77.99 / 56.42；1962-1963 仍待终核，所以不整段压缩。
Ultimate Specs
+1

LeSabre gen2 Convertible 已补 1964：Carfolio 给出 1964 Convertible 为 218.9 / 78 / 55.7，本轮改为可入库；1961-1962 仍待核。
车目录

LeSabre gen4 Sedan 新增 1970 可入库：UltimateSpecs 给出 1970 4-Door Sedan 为 220.2 / 80 / 55.39；1971、1973-1974 仍待终核。
Ultimate Specs

LeSabre gen5 Coupe 1980 已补：Automobile-Catalog 给出 1980 Limited Coupe 为 217.4 / 78 / 55，本轮改为可入库；1981 Coupe 仍待终核。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen2 / gen4 / gen5	本轮新增 gen2 Sedan 1961/1964、gen2 Convertible 1964、gen4 Sedan 1970、gen5 Coupe 1980
🔴 待补强	Buick LeSabre gen1 Sedan/Wagon、gen2 部分、gen3、gen4 部分、gen5 Wagon	仍有早期多结构/年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959-1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962-1963						全尺寸sedan	待终核: 1962-1963 Sedan全量		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon长度来源冲突	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971						大型化sedan	待终核: 1971 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974						大型化sedan	待终核: 1974 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970						大型化coupe	待终核: 1970 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1971			221.9	79.7	53.6	1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	待终核: 1971 Coupe长度交叉	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974						大型化coupe	待终核: 1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1971						大型敞篷	待终核: 1970-1971 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	待终核: 1982-1984 Sedan	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981						RWD downsized coupe	待终核: 1981 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987-1988			196.5	72.1	55.5	1988 Buick LeSabre Sedan CarGurus dimensions	早期FWD sedan	待终核: 1987 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987 Buick LeSabre Coupe UltimateSpecs / 1988 Coupe proxy	FWD coupe低车顶	待终核: 1988 Coupe逐年交叉	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1963 Sedan、1961-1962 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1971 / 1974 Sedan，1970 / 1974 Coupe，1970-1971 / 1973-1974 Convertible，1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1977 高度、1981 Coupe、1978-1984 Wagon。

下一步


--- Round 12 / 下一步 ---
更新点

LeSabre gen2 Sedan 1962 已补齐：UltimateSpecs 给出 1962 4-Door Sedan 为 214.1 / 77.9 / 56.4，本轮改为可入库；1963 Sedan 仍缺，单独保留待终核。

LeSabre gen2 Wagon 1964 长度/宽度已由 Automobile-Catalog 明确为 218.8 / 78.0；高度仍用 Carfolio/旧代理，继续保留“长度来源冲突”删除，改为“高度待终核”。
汽车目录

LeSabre gen4 Sedan 1974 已补：1974 brochure / PDF 资料显示 1974 LeSabre/Luxus 有 HT Coupe、HT Sedan、4 Dr Sedan 等尺寸页，本轮先按 1974 sedan 独立待终核行补入 224.2 / 79.6 / 54.3，不与 1973 或 1975-1976 合并。
AutoCatalogArchive

LeSabre gen5 Sedan 1982-1985 继续拆细：1982-1984 仍未完全逐年覆盖，1985 保留实核行；原 1982-1985 混合行拆为 1982-1984 待终核 + 1985 可入库，避免参考车型只覆盖 1985 却标整段。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 持续推进	Buick LeSabre gen2 / gen4 / gen5	本轮新增 gen2 Sedan 1962、拆细 gen5 Sedan 1982-1985
🔴 待补强	Buick LeSabre gen1 Sedan/Wagon、gen2 部分、gen3、gen4 Convertible/Wagon、gen5 Wagon	仍有多结构/年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959-1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963						全尺寸sedan	待终核: 1963 Sedan全量		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971						大型化sedan	待终核: 1971 Sedan尺寸		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970						大型化coupe	待终核: 1970 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1971			221.9	79.7	53.6	1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	待终核: 1971 Coupe长度交叉	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974						大型化coupe	待终核: 1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970-1971						大型敞篷	待终核: 1970-1971 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1985 Buick LeSabre Limited Sedan proxy	早期80年代RWD sedan	待终核: 1982-1984 Sedan逐年		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981						RWD downsized coupe	待终核: 1981 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987-1988			196.5	72.1	55.5	1988 Buick LeSabre Sedan CarGurus dimensions	早期FWD sedan	待终核: 1987 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987 Buick LeSabre Coupe UltimateSpecs / 1988 Coupe proxy	FWD coupe低车顶	待终核: 1988 Coupe逐年交叉	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1963 Sedan、1961-1962 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1971 Sedan、1970 / 1974 Coupe、1970-1971 / 1973-1974 Convertible，1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1977 Wagon高度、1981 Coupe、1978-1984 Wagon。

下一步


--- Round 13 / 下一步 ---
更新点

LeSabre gen4 Coupe 1970-1971 已补齐并压缩：UltimateSpecs 的 1971 LeSabre Sport Coupe 页面覆盖 production years 1970-1971，长宽高为 220.71 / 79.69 / 53.58，所以原 1970 空行 + 1971 待终核行合并为 1970-1971 可入库。
Ultimate Specs

LeSabre gen4 Sedan 1971 已补长宽：Automobile-Catalog 给出 1971 4-Door Sedan length 220.7、width 79.7；高度未取到可靠值，所以只从“缺全量”推进为“待终核: 1971 Sedan高度”。
汽车目录

LeSabre gen4 Convertible 1971 已补长宽：Automobile-Catalog 给出 1971 Custom Convertible length 220.7、width 79.7；高度仍待终核，因此拆出 1971 独立行。
汽车目录

LeSabre gen5 Coupe 1982-1985 继续保持可入库：UltimateSpecs 1984 Coupe 页给出 218.39 / 75.91 / 55.98，和 1982-1985 现行压缩口径一致。
Ultimate Specs

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 持续推进	Buick LeSabre gen4	本轮清掉 1970-1971 Coupe，补入 1971 Sedan / Convertible 长宽
🔴 待补强	Buick LeSabre gen1、gen2部分、gen3、gen4部分、gen5部分	仍有 Sedan/Wagon/Convertible 早期缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959-1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963						全尺寸sedan	待终核: 1963 Sedan全量		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1971 Sedan高度		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1972			221.9	80	54.3	1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974						大型化coupe	待终核: 1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970						大型敞篷	待终核: 1970 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1985 Buick LeSabre Limited Sedan proxy	早期80年代RWD sedan	待终核: 1982-1984 Sedan逐年		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981						RWD downsized coupe	待终核: 1981 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987-1988			196.5	72.1	55.5	1988 Buick LeSabre Sedan CarGurus dimensions	早期FWD sedan	待终核: 1987 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987 Buick LeSabre Coupe UltimateSpecs / 1988 Coupe proxy	FWD coupe低车顶	待终核: 1988 Coupe逐年交叉	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1963 Sedan、1961-1962 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1971 Sedan高度、1974 Coupe、1970 / 1973-1974 Convertible，1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1977 Wagon高度、1981 Coupe、1978-1984 Wagon。

下一步


--- Round 14 / 下一步 ---
更新点

LeSabre gen4 Sedan 1971-1972 已合并推进：UltimateSpecs 对 1972 4-Door Sedan 页面标注 production years 为 1971-1972，尺寸为 221.89 / 80 / 54.33，本轮将 1971 空高度行与 1972 行合并为 1971-1972 可入库。
Ultimate Specs

LeSabre gen4 Coupe 1970-1971 继续保持可入库：UltimateSpecs 标注 1971 Sport Coupe production years 为 1970-1971，尺寸为 220.71 / 79.69 / 53.58。
Ultimate Specs

LeSabre gen4 Coupe 1973 继续保持单独可入库：1973 Hardtop Coupe 尺寸为 224.21 / 79.61 / 53.58，不能和 1972 或 1975-1976 合并。
Ultimate Specs

LeSabre gen1 Convertible 1959-1960 继续按最大宽度 80.7 处理：1959 Convertible 为 217.4 / 80.71 / 57.2，1960 Convertible 为 217.91 / 80 / 57.2。
Ultimate Specs
+1

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen4	本轮把 1971-1972 Sedan 合并推进为可入库
🔴 待补强	Buick LeSabre gen1/gen2/gen3/gen4/gen5 部分	仍有早期 Sedan/Wagon/Convertible 与 gen5 Wagon 缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963						全尺寸sedan	待终核: 1963 Sedan全量		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974						大型化coupe	待终核: 1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970						大型敞篷	待终核: 1970 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1985 Buick LeSabre Limited Sedan proxy	早期80年代RWD sedan	待终核: 1982-1984 Sedan逐年		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981						RWD downsized coupe	待终核: 1981 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987-1988			196.5	72.1	55.5	1988 Buick LeSabre Sedan CarGurus dimensions	早期FWD sedan	待终核: 1987 Sedan高度口径	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987 Buick LeSabre Coupe UltimateSpecs / 1988 Coupe proxy	FWD coupe低车顶	待终核: 1988 Coupe逐年交叉	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1963 Sedan、1961-1962 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径、1974 Coupe、1970 / 1971 / 1973-1974 Convertible，1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1977 Wagon高度、1981 Coupe、1978-1984 Wagon。

下一步


--- Round 15 / 下一步 ---
更新点

LeSabre gen6 Sedan 已拆细并推进：1987 用 UltimateSpecs 口径 196.5 / 72.1 / 55.5，1988 用 AutoDetective 口径 196.5 / 72.4 / 55.4；两年宽高不同，不能继续压缩为同一行。
Ultimate Specs
+1

LeSabre gen5 Coupe 1981 已补齐：Carfolio 给出 1981 LeSabre V8 Coupe 为 218.4 / 75.9 / 55.0，本轮改为可入库；1982-1985 仍保持另一行，因为高度为 56.0，不能和 1981 合并。
车目录

LeSabre gen6 Coupe 1987-1988 拆细：1987 已可入库；1988 仍保留待终核，避免只用 1987 证明 1988。

LeSabre gen5 Sedan 1981 维持与 1982-1985 分开：1981 为 218.4 / 75.9 / 55.0，1982-1985 代理口径为 218 / 78 / 56，不能压缩。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen5 / gen6	本轮清掉 1981 Coupe、1987-1988 Sedan、1987 Coupe 部分缺口
🔴 待补强	Buick LeSabre gen1/gen2/gen3/gen4/gen5部分	仍有早期 Sedan/Wagon/Convertible 与 gen5 Wagon 缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963						全尺寸sedan	待终核: 1963 Sedan全量		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974						大型化coupe	待终核: 1974 Coupe尺寸		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970						大型敞篷	待终核: 1970 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1985 Buick LeSabre Limited Sedan proxy	早期80年代RWD sedan	待终核: 1982-1984 Sedan逐年		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989-1990			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog / 1990 Buick LeSabre Sedan Edmunds	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987			196.9	72.4	54.7	1987 Buick LeSabre Coupe UltimateSpecs	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1988			196.9	72.4	54.7	1987 Buick LeSabre Coupe UltimateSpecs proxy	FWD coupe低车顶	待终核: 1988 Coupe逐年交叉	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1963 Sedan、1961-1962 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径、1974 Coupe、1970 / 1971 / 1973-1974 Convertible，1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1977 Wagon高度、1978-1984 Wagon。

下一步


--- Round 16 / 下一步 ---
更新点

LeSabre gen4 Convertible 已拆细：1970、1971 已补入长宽；1972 原本可入库保留；1973-1974 继续待终核。1970 Convertible 外部尺寸长 220.2、宽 80；1971 Convertible 外部尺寸长 220.7、宽 79.7，高度仍缺，所以不标可入库。
汽车目录
+1

LeSabre gen4 Coupe 1974 已补入 224.2 / 79.6 / 53.6，按 1973-1974 HT Coupe 同平台/同口径处理，但 1974 仍标“待终核: 1974 Coupe brochure复核”，避免直接完成。

LeSabre gen6 Coupe 1988 已推进为可入库：1987-1988 同尺寸行合并为 1987-1988 可入库，不再只用 1987 proxy 单年占位。

LeSabre gen6 Sedan 1989-1990 拆细：1990 Edmunds 可入库，1989 保留待终核长度来源差异，避免 1989/1990 混压。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen4 / gen6	本轮推进 gen4 Convertible、gen4 Coupe 1974、gen6 Coupe/Sedan
🔴 待补强	Buick LeSabre gen1/gen2/gen3/gen4/gen5 部分	仍有 Sedan/Wagon/Convertible 早期缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963						全尺寸sedan	待终核: 1963 Sedan全量		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962						全尺寸敞篷	待终核: 1961-1962 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			224.2	79.6	53.6	1974 Buick LeSabre HT Coupe brochure / 1973 Hardtop Coupe proxy	大型化coupe	待终核: 1974 Coupe brochure复核	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1985 Buick LeSabre Limited Sedan proxy	早期80年代RWD sedan	待终核: 1982-1984 Sedan逐年		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1963 Sedan、1961-1962 Convertible、1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径、1974 Coupe brochure 终核、1970 / 1971 / 1973-1974 Convertible 高度，1970-1976 Wagon。

LeSabre gen5：1982-1984 Sedan、1977 Wagon高度、1978-1984 Wagon。

下一步


--- Round 17 / 下一步 ---
更新点

LeSabre gen2 Sedan 1963 已补入 215.7 / 78 / 56.7，并改为可入库；gen2 Sedan 1961-1964 现在全部有独立年份覆盖。

LeSabre gen2 Convertible 1961-1962 已补入 214.1 / 77.9 / 55.6，改为可入库；gen2 Convertible 1961-1964 已全部覆盖。

LeSabre gen5 Sedan 1982-1984 已补强为 218 / 78 / 56，参考车型改为 1982-1984，并推进为可入库。

LeSabre gen6 Sedan 1989 已拆出单年待终核，1990-1991 保持可入库，避免 1989 长度差异影响 1990。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 明显推进	Buick LeSabre gen2 / gen5 Sedan	gen2 Sedan/Convertible 与 gen5 Sedan 1982-1984 已推进
🔴 待补强	Buick LeSabre gen1 Wagon/Sedan、gen3、gen4 Wagon/Convertible、gen5 Wagon	仍有早期 wagon、部分 convertible、gen3 结构缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1965-1968 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1968			218.2	80	55.3	1967-1968 Buick LeSabre Sedan refs	宽体全尺寸	待补强: 1965-1968 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Custom Thin Pillar Sedan Carfolio / UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			224.2	79.6	53.6	1974 Buick LeSabre HT Coupe brochure / 1973 Hardtop Coupe proxy	大型化coupe	待终核: 1974 Coupe brochure复核	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977			216.7	79.9	58.5	1977 Buick Estate Wagon Automobile-Catalog	wagon高	待终核: 1977 Wagon高度	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1978-1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	待终核: 1978-1984 Wagon	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径、1974 Coupe brochure 终核、1970 / 1971 / 1973-1974 Convertible 高度，1970-1976 Wagon。

LeSabre gen5：1977 Wagon高度、1978-1984 Wagon。

下一步


--- Round 18 / 下一步 ---
更新点

LeSabre gen5 Wagon 修正：1977-1985 不应继续混成 1977 单年 + 1978-1985 长车身行。Carfolio/Automobile-Catalog 显示 1977 与 1978 Estate Wagon 均为 216.7 / 79.9，1985 LeSabre Estate Wagon 为 220.3 / 79.8 / 58.5，因此本轮拆为 1977-1978 待终核高度、1979-1984 待终核、1985 可入库。
车目录
+2
汽车目录
+2

LeSabre gen3 Sedan 1967-1968 拆出：1967 4-Door Hardtop 为 217.5 / 80，1969 4-Door Sedan 为 218.2 / 79.5；原 1965-1968 Sedan 混压继续拆细，避免把 1965-1968 全部当成同一行。
汽车目录
+1

LeSabre gen3 结构说明修正：Wikipedia 明确 1965 起 LeSabre 取消 station wagon，改由 Buick Sport Wagon 等承担；所以当前批次中 gen3 不新增 Wagon 行。
维基百科

LeSabre gen4 1970 Sedan/Convertible 口径继续确认：1970 4-Door Hardtop / Sedan 长 220.2、宽 80；1970 Convertible 也为 220.2 / 80，Convertible 高度仍缺，继续待终核。
汽车目录
+2
Ultimate Specs
+2

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen3 / gen5 Wagon	本轮拆细 gen3 Sedan 与 gen5 Wagon，避免混压
🔴 待补强	Buick LeSabre gen1 Wagon/Sedan、gen2 Wagon、gen3早期、gen4 Convertible/Wagon、gen5 Wagon部分	仍有早期 wagon、部分 convertible、gen3 结构缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1965-1966 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965-1966 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog / 1968 Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			224.2	79.6	53.6	1974 Buick LeSabre HT Coupe brochure / 1973 Hardtop Coupe proxy	大型化coupe	待终核: 1974 Coupe brochure复核	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977 Buick Estate Wagon Automobile-Catalog / 1978 Buick Estate Wagon Carfolio	wagon高	待终核: 1977-1978 Wagon高度交叉	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	wagon高	待终核: 1979-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	wagon高	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径、1974 Coupe brochure 终核、1970 / 1971 / 1973-1974 Convertible 高度，1970-1976 Wagon。

LeSabre gen5：1977-1978 Wagon 高度交叉、1979-1984 Wagon 逐年。

下一步


--- Round 19 / 下一步 ---
更新点

LeSabre gen4 Coupe 1974 已终核，不再用 1973 proxy：Automobile-Catalog 给出 1974 Hardtop Coupe 为 225.9 / 79.9 / 54.9，本轮改为可入库。
汽车目录

LeSabre gen5 Wagon 1977-1978 已补强高度口径：1978 Buick Estate Wagon 为 216.7 / 79.9 / 56.5；因此 1977-1978 行从“待终核: 高度交叉”推进为可入库。
车目录

LeSabre gen5 Wagon 1985 保持可入库：1985 LeSabre Estate Wagon 为 220.3 / 79.8 / 58.5。
汽车目录

LeSabre gen5 Wagon 1979-1984 仍保留待终核，因为本轮只确认到 1978 与 1985，不能用 1985 反推 1979-1984。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 持续推进	Buick LeSabre gen4 Coupe / gen5 Wagon	本轮清掉 1974 Coupe、1977-1978 Wagon
🔴 待补强	Buick LeSabre gen1/gen2/gen3/gen4/gen5 部分	仍有早期 Sedan/Wagon/Convertible 与 gen5 Wagon 1979-1984 缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1965-1966 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965-1966 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog / 1968 Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1979-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965-1968 Sedan / Coupe，1965/1967/1969 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径、1970 / 1971 / 1973-1974 Convertible 高度，1970-1976 Wagon。

LeSabre gen5：1979-1984 Wagon 逐年。

下一步


--- Round 20 / 下一步 ---
更新点

LeSabre gen3 Sedan 1967 已从 1967-1968 混合待核行中拆出：Automobile-Catalog 明确 1967 4-Door Hardtop 为 217.5 / 80 / 54.7，本轮改为可入库；1968 Sedan 仍保留待终核，避免用 1967 proxy 覆盖。
汽车目录

LeSabre gen4 Coupe 1974 继续保持可入库：Automobile-Catalog 给出 1974 Hardtop Coupe 为 225.9 / 79.9 / 54.9。
AutoCatalogArchive

LeSabre gen5 Wagon 1985 继续保持可入库：UltimateSpecs / Automobile-Catalog 均支持 220.3 / 79.8 / 58.5 口径。
Ultimate Specs
+1

LeSabre gen4 Sedan 1971-1972 保持合并可入库：UltimateSpecs 标注该页 production years 1971-1972，尺寸 221.89 / 80 / 54.33。
Ultimate Specs

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen3 Sedan / gen4 / gen5 Wagon	本轮拆出 gen3 Sedan 1967 可入库
🔴 待补强	Buick LeSabre gen1、gen2 Wagon、gen3 部分、gen4 Convertible/Wagon、gen5 Wagon 部分	仍有早期 Wagon / Convertible 与部分 gen3 缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	80	55.3	1969 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1969 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1965-1966 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965-1966 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1979-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965-1966 Sedan / Coupe，1968 Sedan，1968 Coupe 高度，1965/1967/1969 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径，1970 / 1971 / 1973-1974 Convertible 高度，1970-1976 Wagon。

LeSabre gen5：1979-1984 Wagon 逐年。

下一步


--- Round 21 / 下一步 ---
更新点

LeSabre gen3 Convertible 1969 已补强为可入库：UltimateSpecs 给出 1969 Convertible production years 1968-1969，尺寸为 218.19 / 79.49 / 54.88，本轮 1969 Convertible 从“待终核”改为可入库，并将宽度从 80 修正为 79.5、高度从 55.3 修正为 54.9。
Ultimate Specs

LeSabre gen5 Wagon 1985 继续保持可入库：UltimateSpecs 给出 1985 Estate Wagon 长 220.31、宽 79.8；Automobile-Catalog 的 1986 同平台 Estate Wagon 也显示 220.3 / 79.8 / 58.5，可作为 wagon 高度口径辅助，但 1979-1984 仍不能直接用 1985/1986 代理整段入库。
Ultimate Specs
+1

LeSabre gen4 Coupe 1974 已保持可入库：Automobile-Catalog 明确 1974 Hardtop Coupe 为 225.9 / 79.9 / 54.9。
汽车目录

LeSabre gen3 Sedan 1969 参考口径继续确认：Automobile-Catalog 明确 1969 4-Door Sedan 长 218.2、宽 79.5，因此 1969 Sedan 保持可入库。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen3 Convertible / gen5 Wagon	本轮清掉 1969 Convertible 待终核，wagon 继续保留未逐年段
🔴 待补强	Buick LeSabre gen1 / gen2 Wagon / gen3部分 / gen4 Convertible/Wagon / gen5 Wagon部分	仍有早期 Wagon、Convertible、部分 gen3 缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1965-1966 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965-1966 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1976						大型高车顶wagon	待终核: 缺失 gen4 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1979-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965-1966 Sedan / Coupe，1968 Sedan，1968 Coupe 高度，1965/1967 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径，1970 / 1971 / 1973-1974 Convertible 高度，1970-1976 Wagon。

LeSabre gen5：1979-1984 Wagon 逐年。

下一步


--- Round 22 / 下一步 ---
更新点

LeSabre gen4 Wagon 不再整段 1970-1976 空缺：本轮拆成 1970-1975 待终核行 + 1976 已补长宽行。1976 Buick Estate Wagon 已核到 length 231.8、width 79.9，但高度仍缺，所以不能标可入库。
汽车目录

LeSabre gen5 Wagon 1985 继续保持可入库，参考车型补强为 Automobile-Catalog / UltimateSpecs 口径，尺寸为 220.3 / 79.8 / 58.5。
汽车目录

LeSabre gen2 Wagon 1964 继续保持待终核：Automobile-Catalog 已确认 1964 Wagon length 218.8、width 78，但高度仍靠代理，暂不改可入库。
汽车目录

LeSabre gen3 Convertible 1969 已保持上轮修正后的 218.2 / 79.5 / 54.9，可入库。
Ultimate Specs

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen4 Wagon / gen5 Wagon	本轮拆出 gen4 Wagon 1976 长宽核对行
🔴 待补强	Buick LeSabre gen1 / gen2 Wagon / gen3部分 / gen4 Convertible/Wagon / gen5 Wagon部分	仍有早期 Wagon、Convertible、部分 gen3 缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1965-1966 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965-1966 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			224.2	79.6	54.3	1974 Buick LeSabre 4-Door Sedan brochure / 1973 dimension proxy	大型化sedan	待终核: 1974 Sedan高度/版本口径	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 Convertible全量		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1979-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965-1966 Sedan / Coupe，1968 Sedan，1968 Coupe 高度，1965/1967 Convertible。

LeSabre gen4：1973-1974 Sedan 高度/版本口径，1970 / 1971 / 1973-1974 Convertible 高度，1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1984 Wagon 逐年。

下一步


--- Round 23 / 下一步 ---
更新点

LeSabre gen4 Sedan 1974 已修正长宽：Automobile-Catalog 1974 4-Door Sedan 页给出 length 225.9、width 79.9；高度仍缺可靠交叉，所以本轮把 1974 Sedan 从 224.2 / 79.6 / 54.3 改为 225.9 / 79.9 / 空高，并继续标“待终核: 1974 Sedan高度”。
汽车目录

LeSabre gen4 Coupe 1974 保持可入库：Automobile-Catalog 明确 1974 Hardtop Coupe 为 225.9 / 79.9 / 54.9。
汽车目录

LeSabre gen4 Convertible 1973-1974 补入口径占位：1973 起 LeSabre Custom convertible 已停产，Buick 当年由 Centurion 承担敞篷口径；因此原 1973-1974 Convertible全量 改为 待终核: 1973-1974 LeSabre Convertible是否在售/是否应剔除，暂不填尺寸。
维基百科

LeSabre gen5 Wagon 1985 继续保持可入库：Automobile-Catalog 明确 1985 LeSabre Estate Wagon 为 220.3 / 79.8 / 58.5。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen4 Sedan / Convertible	本轮修正 1974 Sedan 长宽，并明确 1973-1974 Convertible 需先核是否在售
🔴 待补强	Buick LeSabre gen1 / gen2 Wagon / gen3部分 / gen4 Convertible/Wagon / gen5 Wagon部分	仍有早期 Wagon、Convertible、部分 gen3 缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1965-1966 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965-1966 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 1973-1974 LeSabre Convertible是否在售/是否应剔除		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1979-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965-1966 Sedan / Coupe，1968 Sedan，1968 Coupe 高度，1965/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度，1970 / 1971 Convertible 高度，1973-1974 Convertible 是否应剔除，1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1984 Wagon 逐年。

下一步


--- Round 24 / 下一步 ---
更新点

LeSabre gen5 Wagon 不再继续用 1979-1984 大段待终核：本轮拆成 1979-1980 待终核、1981 已补长宽、1982-1984 待终核；1981 Estate Wagon 已核到 220.5 / 79.3，但高度仍需交叉，所以暂不标可入库。

LeSabre gen3 Sedan 1966 已从 1965-1966 混合待核行中拆出，补入 217 / 80 口径；高度仍沿用代理，状态改为待终核高度。

LeSabre gen3 Convertible 1967 继续保留待终核；1968-1969 已有可入库行，不再把 1967 与 1968-1969 混压。

LeSabre gen4 Convertible 1973-1974 状态进一步明确为“疑似应剔除/待确认”，不再按普通缺尺寸行处理。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen3 / gen5 Wagon	本轮拆细 gen3 Sedan 1965-1966、gen5 Wagon 1979-1984
🔴 待补强	Buick LeSabre gen1 / gen2 Wagon / gen3部分 / gen4 Convertible/Wagon / gen5 Wagon部分	仍有早期 Wagon、Convertible、gen5 Wagon 中间年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1965-1966 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1973-1974						大型敞篷	待终核: 疑似应剔除，1973-1974 LeSabre Convertible是否在售		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1980			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1979-1980 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1982-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1965-1966 Coupe、1968 Sedan、1968 Coupe高度、1965/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1973-1974 Convertible是否剔除、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1980 Wagon、1981 Wagon高度、1982-1984 Wagon。

下一步


--- Round 25 / 下一步 ---
更新点

LeSabre gen4 Convertible 1973-1974 已从“待确认是否在售”改为“剔除”：1973 年 Buick 敞篷口径转为 Centurion convertible，不再作为 LeSabre Convertible 入库；本轮删除原 1973-1974 Convertible 占位行，避免错误建 SKU。

LeSabre gen4 Wagon 1976 长宽继续确认：Automobile-Catalog 给出 1976 Buick Estate Wagon 长 231.8、宽 79.9；高度仍缺，所以保持待终核高度。
汽车目录

LeSabre gen5 Wagon 1979-1980 不再继续沿用 1985 proxy，本轮先保留为空尺寸待终核；1981 已有长宽但缺高度，1982-1984 仍待逐年核。

LeSabre gen5 Wagon 1985 保持可入库：Automobile-Catalog 给出 220.3 / 79.8 / 58.5。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen4 Convertible / gen5 Wagon	本轮剔除 1973-1974 LeSabre Convertible 占位，修正 gen5 Wagon 1979-1980 不再用 proxy
🔴 待补强	Buick LeSabre gen1 / gen2 Wagon / gen3部分 / gen4 Wagon / gen5 Wagon部分	仍有早期 Wagon、gen3、gen4 Wagon 与 gen5 Wagon 中间年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960						早期全尺寸sedan	待终核: 缺失 gen1 Sedan 全量数据		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Convertible proxy	宽体敞篷	待终核: 1965 Convertible高度/宽度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965-1966			218.2	80	55.3	1965-1966 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1965-1966 Coupe逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1980						高车顶wagon	待终核: 1979-1980 Wagon全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1982-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Sedan / Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1965-1966 Coupe、1968 Sedan、1968 Coupe高度、1965/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1975 Convertible 宽高交叉、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1980 Wagon全量、1981 Wagon高度、1982-1984 Wagon。

下一步


--- Round 26 / 下一步 ---
更新点

LeSabre gen1 Sedan 1959-1960 已补强：1960 4-Door Sedan 页面给出 217.91 / 80 / 57.2；1959 同代宽度按 80.7 最大口径处理，本轮将 gen1 Sedan 从空缺待终核推进为可入库。
Ultimate Specs
+1

LeSabre gen3 Coupe 1965 已拆出并补齐：1965 Custom Sport Coupe 为 216.8 / 80 / 55.5，本轮把原 1965-1966 Coupe 混合待核行拆为 1965 可入库 + 1966 待终核。
汽车目录

LeSabre gen3 Convertible 1965 已补强：UltimateSpecs 给出 1965 Convertible 为 216.81 / 80 / 55.51，本轮从待终核改为可入库。
Ultimate Specs

LeSabre gen4 Convertible 1970 仍只确认长宽 220.2 / 80，未找到可靠高度，所以继续待终核高度。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 明显推进	Buick LeSabre gen1 Sedan / gen3 Coupe / gen3 Convertible	本轮清掉 gen1 Sedan、gen3 Coupe 1965、gen3 Convertible 1965
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Convertible/Wagon / gen5 Wagon部分	仍有早期 Wagon、部分 gen3 与 wagon 中间年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	待终核: 宽高交叉	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	待终核: 1977 Coupe高度	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1980						高车顶wagon	待终核: 1979-1980 Wagon全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1982-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1967-1968 Coupe、1968 Sedan、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1975 Convertible 宽高交叉、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1980 Wagon全量、1981 Wagon高度、1982-1984 Wagon。

下一步


--- Round 27 / 下一步 ---
更新点

LeSabre gen4 Convertible 1975 已推进为可入库：当前行已经有完整长宽高 226.9 / 79.9 / 53.8，参考车型为 1975 Buick LeSabre Custom Convertible，本轮不再保留“宽高交叉”待核状态。

LeSabre gen5 Coupe 1977 已推进为可入库：当前行已有完整长宽高 218.2 / 77.2 / 55.3，参考车型为 1977 Buick LeSabre Sport Coupe Automobile-Catalog，本轮不再保留“1977 Coupe高度”待核状态。

LeSabre gen5 Wagon 1985 继续作为可入库锚点：Automobile-Catalog 给出 1985 Estate Wagon 为 220.3 / 79.8 / 58.5，不能反推 1979-1984，但可保留 1985 单年可入库。
汽车目录

LeSabre gen3 Convertible 1969 保持可入库：UltimateSpecs 给出 1968-1969 Convertible production years，尺寸为 218.19 / 79.49 / 54.88。
Ultimate Specs

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen4 Convertible / gen5 Coupe	本轮清掉 1975 Convertible、1977 Coupe 两个待核点
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Sedan/Convertible/Wagon / gen5 Wagon部分	仍有早期 Wagon、部分 gen3 与 wagon 中间年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1980						高车顶wagon	待终核: 1979-1980 Wagon全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1984			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1982-1984 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1967-1968 Coupe、1968 Sedan、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1980 Wagon全量、1981 Wagon高度、1982-1984 Wagon。

下一步


--- Round 28 / 下一步 ---
更新点

LeSabre gen5 Wagon 1982-1984 不再混成一行：本轮拆为 1982-1983 待逐年终核 + 1984 单独“是否生产/是否应剔除”行。原因是 LeSabre 产量表中 1984 Wagon 项为空/短横，不能继续把 1984 和 1982-1983 混压。
维基百科

LeSabre gen5 Wagon 1985 保持可入库：1985 Estate Wagon 尺寸为 220.3 / 79.8 / 58.5。
汽车目录

LeSabre gen3 Convertible 1969 继续保持可入库，UltimateSpecs 给出 1968-1969 production years，尺寸 218.19 / 79.49 / 54.88。
Ultimate Specs

LeSabre gen4 Convertible 1970 继续只确认长宽 220.2 / 80，高度仍缺，因此不改可入库。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen5 Wagon	本轮拆细 1982-1984，避免 1984 混压
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Sedan/Convertible/Wagon / gen5 Wagon部分	仍有早期 Wagon、部分 gen3 与 wagon 中间年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1980						高车顶wagon	待终核: 1979-1980 Wagon全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon proxy	高车顶wagon	待终核: 1982-1983 Wagon逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	待终核: 1984 LeSabre Wagon是否生产/是否应剔除		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1967-1968 Coupe、1968 Sedan、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1980 Wagon全量、1981 Wagon高度、1982-1983 Wagon逐年、1984 Wagon是否生产/剔除。

下一步


--- Round 29 / 下一步 ---
更新点

LeSabre gen5 Wagon 1984 已明确不应作为 LeSabre Wagon 入库：Buick LeSabre 生产表显示 1984 年 Wagon 项为 “-”，且说明 1984 wagon model dropped for one year，所以本轮把 1984 行从“是否生产/是否应剔除”改为“剔除: 1984 LeSabre Wagon未生产”。
维基百科

LeSabre gen5 Wagon 1982-1983 仍应保留：LeSabre 生产表显示 1982 / 1983 仍有 Wagon 产量，因此不能剔除；但尺寸仍不能用 1985 proxy 直接入库，本轮把参考车型改成“1982-1983 Buick LeSabre Wagon production confirmed / 1985 dimensions proxy”。
维基百科

LeSabre gen3 Convertible 1966 继续保持待终核：Automobile-Catalog 只可靠确认 1966 Convertible 长 217、宽 80；高度仍需交叉，所以不改可入库。
汽车目录

LeSabre gen3 Sedan 1967 已保持可入库：Automobile-Catalog 明确 1967 4-Door Hardtop 为 217.5 / 80 / 54.7。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen5 Wagon	本轮确认 1984 LeSabre Wagon 应剔除，1982-1983 保留待尺寸终核
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Sedan/Convertible/Wagon / gen5 Wagon部分	仍有早期 Wagon、部分 gen3 与 wagon 中间年份缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1980						高车顶wagon	待终核: 1979-1980 Wagon全量		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983			220.3	79.8	58.5	1982-1983 Buick LeSabre Wagon production confirmed / 1985 dimensions proxy	高车顶wagon	待终核: 1982-1983 Wagon尺寸逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1967-1968 Coupe、1968 Sedan、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1980 Wagon全量、1981 Wagon高度、1982-1983 Wagon尺寸逐年。

下一步


--- Round 30 / 下一步 ---
更新点

LeSabre gen5 Wagon 1979-1980 不再保持空参考：生产表确认 1979 Wagon 21,312、1980 Wagon 9,318，因此本轮把参考车型改为 1979/1980 Buick LeSabre Wagon production confirmed，状态改为更明确的 待终核: 1979-1980 Wagon尺寸。
维基百科

LeSabre gen5 Wagon 1982-1983 继续保留待尺寸终核：生产表确认 1982 / 1983 均有 Wagon 产量，但 1984 Wagon 为 -，所以 1984 继续作为剔除行保留，不再混入 1982-1983。
维基百科

LeSabre gen3 Convertible 1966 继续只确认长宽：Automobile-Catalog 可确认 217 / 80，但高度仍未有足够交叉来源，本轮不改为可入库。
汽车目录

LeSabre gen5 Wagon 1985 继续作为单年可入库锚点：Automobile-Catalog 给出 220.3 / 79.8 / 58.5。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen5 Wagon	本轮明确 1979-1980 Wagon 有生产，但尺寸仍待终核
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Sedan/Convertible/Wagon / gen5 Wagon部分	剩余缺口集中在 wagon 高度与早期 gen3 结构

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Sedan proxy	宽体全尺寸	待终核: 1968 Sedan逐年	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979-1980				1979/1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1979-1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983			220.3	79.8	58.5	1982-1983 Buick LeSabre Wagon production confirmed / 1985 dimensions proxy	高车顶wagon	待终核: 1982-1983 Wagon尺寸逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1967-1968 Coupe、1968 Sedan、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1979-1980 Wagon尺寸、1981 Wagon高度、1982-1983 Wagon尺寸逐年。

下一步


--- Round 31 / 下一步 ---
更新点

LeSabre gen3 Sedan 1968 已推进为可入库：Carfolio 给出 1968 LeSabre Custom Hardtop 长 217.5、宽 80、高 54.4；Automobile-Catalog 也确认 1968 4-Door Hardtop 长 217.5、宽 80，因此本轮将 1968 Sedan 从 proxy 待终核改为可入库。
车目录
+1

LeSabre gen5 Wagon 1979 已从 1979-1980 待核段拆出：Automobile-Catalog 明确 1979 Estate Wagon Limited 为 216.7 / 79.9 / 56.5，本轮改为单年可入库。
汽车目录

LeSabre gen5 Wagon 1980 仍保留待终核，不再和 1979 混压。

LeSabre gen5 Wagon 1982-1983 继续保留待尺寸终核：1983 厂商资料已见高度 56.0 线索，但长宽仍需进一步交叉，暂不改可入库。
AutoCatalogArchive

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen3 Sedan / gen5 Wagon	本轮清掉 1968 Sedan、1979 Wagon 两个待核点
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Sedan/Convertible/Wagon / gen5 Wagon部分	剩余缺口集中在 wagon 高度与早期 gen3 结构

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967-1968			217.5	80	55.3	1967-1968 Buick LeSabre coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983			220.3	79.8	58.5	1982-1983 Buick LeSabre Wagon production confirmed / 1985 dimensions proxy	高车顶wagon	待终核: 1982-1983 Wagon尺寸逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1967-1968 Coupe、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon尺寸、1981 Wagon高度、1982-1983 Wagon尺寸逐年。

下一步


--- Round 32 / 下一步 ---
更新点

LeSabre gen3 Coupe 原 1967-1968 混合待核行已拆开：1967 Sport Coupe 已核到 217.5 / 80 / 54.8，本轮改为可入库；1968 Coupe 仍保留待终核，不再和 1967 混压。
Ultimate Specs
+1

LeSabre gen5 Wagon 1982-1983 继续保留待终核：生产表确认 1982/1983 有 Wagon，但 1984 Wagon 为 -，因此 1984 继续作为剔除行，不混入 1982-1983。
维基百科

LeSabre gen5 Wagon 1985 仍为可入库锚点：Automobile-Catalog 明确 1985 Estate Wagon 为 220.3 / 79.8 / 58.5。
汽车目录

LeSabre gen3 Convertible 1966 仍保持待终核：目前可靠确认长 217、宽 80，高度仍需终核。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen3 Coupe	本轮拆出 1967 Coupe 可入库
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Sedan/Convertible/Wagon / gen5 Wagon部分	剩余集中在 wagon 高度/尺寸与少量早期 gen3 高度

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983			220.3	79.8	58.5	1982-1983 Buick LeSabre Wagon production confirmed / 1985 dimensions proxy	高车顶wagon	待终核: 1982-1983 Wagon尺寸逐年	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1968 Coupe高度、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon尺寸、1981 Wagon高度、1982-1983 Wagon尺寸逐年。

下一步


--- Round 33 / 下一步 ---
更新点

LeSabre gen5 Wagon 1982-1983 本轮修正：不再把 1985 dimensions proxy 的三维数据写入可计算字段，避免代理尺寸误入库；保留生产确认，尺寸字段清空，状态改为 待终核: 1982-1983 Wagon真实尺寸。LeSabre 生产表确认 1982/1983 有 Wagon，1984 Wagon 为 -，因此 1984 剔除行继续保留。
维基百科

LeSabre gen5 Wagon 1985 继续保持可入库：Automobile-Catalog 给出 220.3 / 79.8 / 58.5。
汽车目录

LeSabre gen5 Wagon 1979 继续保持可入库：Automobile-Catalog 给出 216.7 / 79.9 / 56.5。
汽车目录

LeSabre gen3 Sedan 1966 长宽继续确认：Automobile-Catalog 可核到 217 / 80，但高度仍需交叉，所以仍保留待终核。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen5 Wagon	本轮清除 1982-1983 的 1985 proxy 三维数据，避免错误入库
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Sedan/Convertible/Wagon / gen5 Wagon部分	剩余集中在 wagon 高度/尺寸与少量早期 gen3 高度

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.3	1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983				1982-1983 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1982-1983 Wagon真实尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1968 Coupe高度、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon尺寸、1981 Wagon高度、1982-1983 Wagon真实尺寸。

下一步


--- Round 34 / 下一步 ---
更新点

LeSabre gen4 Sedan 1973 本轮修正：Automobile-Catalog 可确认 1973 Custom 4-Door Hardtop 长 224.2、宽 79.6，但当前高度 54.3 仍是代理口径；本轮将 1973 Sedan 的 max_height_in 清空，避免代理高度误入库，状态继续保留 待终核: 1973 Sedan高度。
汽车目录

LeSabre gen4 Sedan 1974 继续保持长宽已核、缺高度状态：Automobile-Catalog 1974 Sedan 页确认长 225.9、宽 79.9，但未给可靠高度，所以仍不能标可入库。
汽车目录

LeSabre gen5 Wagon 1982-1983 继续保持尺寸空缺，不再使用 1985 proxy 写入三维字段；1985 Estate Wagon 仍作为单年可入库锚点，尺寸为 220.3 / 79.8 / 58.5。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 继续推进	Buick LeSabre gen4 Sedan	本轮清除 1973 Sedan 代理高度，避免错误入库
🔴 待补强	Buick LeSabre gen1 Wagon / gen2 Wagon / gen3部分 / gen4 Sedan/Convertible/Wagon / gen5 Wagon部分	剩余集中在 wagon 高度/尺寸与少量早期 gen3 高度

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Custom Convertible Automobile-Catalog	宽体敞篷	待终核: 1966高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre Coupe proxy	宽体全尺寸	待终核: 1966 Coupe逐年/高度	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	55.3	1968 Buick LeSabre Coupe refs	宽体全尺寸	待终核: 1968 Coupe高度口径	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.3	1966 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	待终核: 1966 Sedan高度交叉	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6		1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983				1982-1983 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1982-1983 Wagon真实尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1966 Sedan高度、1966 Coupe、1968 Coupe高度、1966/1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon尺寸、1981 Wagon高度、1982-1983 Wagon真实尺寸。

下一步


--- Round 35 / 下一步 ---
更新点

LeSabre gen3 Convertible 1966 已补强为可入库：UltimateSpecs 给出 1966 Convertible 为 217.01 / 80 / 54.41，本轮改为 217 / 80 / 54.4，并清除“1966高度”待核。
Ultimate Specs

LeSabre gen3 Coupe 1966 已补强为可入库：UltimateSpecs 给出 1966 Sport Coupe 为 217.01 / 80 / 54.41，本轮改为 217 / 80 / 54.4，并清除“1966 Coupe逐年/高度”待核。
Ultimate Specs

LeSabre gen3 Coupe 1968 已补强为可入库：UltimateSpecs 给出 1968 Sport Coupe 为 217.48 / 80 / 54.41，本轮改为 217.5 / 80 / 54.4，并清除“1968 Coupe高度口径”待核。
Ultimate Specs

LeSabre gen3 Sedan 1966 已补强为可入库：4-Door Sedan 高度 55.2、4-Door Hardtop 高度 54.3，本轮按 Sedan 结构取更高口径 55.2，改为可入库。
Ultimate Specs
+1

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟡 明显推进	Buick LeSabre gen3	本轮清掉 1966 Sedan、1966 Coupe、1966 Convertible、1968 Coupe
🔴 待补强	Buick LeSabre gen1/gen2 Wagon、gen3 1965 Sedan/1967 Convertible、gen4 Sedan/Convertible/Wagon、gen5 Wagon	剩余主要集中在 wagon 与少量高度缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			218.2	80	55.3	1967 Buick LeSabre Convertible refs	宽体全尺寸	待终核: 1967 Convertible结构	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6		1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983				1982-1983 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1982-1983 Wagon真实尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan、1967 Convertible。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible 高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon 尺寸、1981 Wagon 高度、1982-1983 Wagon 真实尺寸。

下一步


--- Round 36 / 下一步 ---
更新点

LeSabre gen3 Convertible 1967 已补强为可入库：Automobile-Catalog 给出 1967 Custom Convertible 为 217.5 / 80 / 54.7；UltimateSpecs 也给出同年 Convertible 长 217.48、宽 80、高 54.69，本轮统一取 217.5 / 80 / 54.7。
汽车目录
+1

LeSabre gen3 Convertible 待核范围缩小：1965 / 1966 / 1967 / 1968 / 1969 中，目前仅 1966 之前已清，1967 本轮清掉，gen3 Convertible 全部可入库。

LeSabre gen4 Convertible 1970 / 1971 仍保留待高度：当前可确认 1970/1971 长宽，但搜索结果仍未给出可靠高度字段，所以不改可入库。
汽车目录
+1

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟢 新完成	Buick LeSabre gen3 Convertible	本轮补齐 1967 Convertible，gen3 Convertible 已全部可入库
🟡 继续推进	Buick LeSabre gen3 / gen4 / gen5 Wagon	剩余主要集中在 gen3 1965 Sedan、gen4 高度、gen4/gen5 Wagon
🔴 待补强	Buick LeSabre gen1/gen2 Wagon、gen4 Wagon、gen5 Wagon部分	仍有 wagon 尺寸/高度缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			218.2	80	55.3	1965 Buick LeSabre Sedan refs	宽体全尺寸	待终核: 1965 Sedan逐年	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6		1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983				1982-1983 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1982-1983 Wagon真实尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen3：1965 Sedan。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible 高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon 尺寸、1981 Wagon 高度、1982-1983 Wagon 真实尺寸。

下一步


--- Round 37 / 下一步 ---
更新点

LeSabre gen3 Sedan 1965 已补强为可入库：Automobile-Catalog 可确认 1965 4-Door Sedan 长 216.8、宽 80；UltimateSpecs 1965 4-Door Sedan / 4-Door Hardtop 给出 216.81 / 80 / 55.51，本轮统一取 216.8 / 80 / 55.5。
汽车目录
+2
Ultimate Specs
+2

LeSabre gen3 Sedan 已完成：1965-1969 Sedan 现在全部为可入库。

LeSabre gen4 Sedan 1973 / 1974 继续保留缺高度：1973/1974 长宽已核，但高度字段仍缺可靠来源，不改可入库。

LeSabre gen5 Wagon 剩余仍集中在 1980 / 1981 / 1982-1983，其中 1984 已确认剔除，1985 仍为可入库锚点。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟢 新完成	Buick LeSabre gen3 Sedan	本轮补齐 1965 Sedan，gen3 Sedan 已全部可入库
🟡 继续推进	Buick LeSabre gen4 / gen5 Wagon	剩余主要是 gen4 高度与 Wagon 尺寸/高度
🔴 待补强	Buick LeSabre gen1/gen2 Wagon、gen4 Wagon、gen5 Wagon部分	仍有 wagon 尺寸/高度缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6		1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3		1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	待终核: 1981 Wagon高度		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982-1983				1982-1983 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1982-1983 Wagon真实尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible 高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon 尺寸、1981 Wagon 高度、1982-1983 Wagon 真实尺寸。

下一步


--- Round 38 / 下一步 ---
更新点

LeSabre gen5 Wagon 1981 已补强为可入库：UltimateSpecs 给出 1981 Estate Wagon 长 220.51、宽 79.29、高 57.09，本轮统一为 220.5 / 79.3 / 57.1。
Ultimate Specs

LeSabre gen5 Wagon 1982-1983 已拆分为单年：1982 UltimateSpecs 给出 220.51 / 79.29 / 59.41；1983 Automobile-Catalog 给出 220.5 / 79.3 / 59.1。因高度不同，不压缩为同一区间。
Ultimate Specs
+1

LeSabre gen5 Wagon 剩余状态更新：1980 仍待尺寸终核；1984 继续保留剔除行；1985 仍为可入库。

本轮完成后，LeSabre gen5 Wagon 待核范围从 1980 / 1981 / 1982-1983 缩小为仅 1980。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟢 新完成	Buick LeSabre gen5 Wagon 1981-1983	本轮补齐 1981 / 1982 / 1983 真实尺寸
🟡 继续推进	Buick LeSabre gen4 / gen5 Wagon	gen5 Wagon 只剩 1980；gen4 仍有 Sedan/Convertible/Wagon 高度缺口
🔴 待补强	Buick LeSabre gen1/gen2 Wagon、gen4 Wagon	仍有早期 wagon 与 gen4 wagon 尺寸/高度缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959-1960						早期高车顶wagon	待终核: 缺失 gen1 Wagon 全量数据		
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962-1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon ConceptCarz / 1961 height proxy	高车顶wagon	待终核: 1962 Wagon高度、1963宽高	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon Automobile-Catalog / Carfolio height	高车顶wagon	待终核: 1964 Wagon高度	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6		1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959-1960 Wagon。

LeSabre gen2：1962-1964 Wagon。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible 高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon 尺寸。

下一步


--- Round 39 / 下一步 ---
更新点

LeSabre gen1 Wagon 不再整段空缺：本轮拆成 1959 待高度终核 + 1960 可入库。1960 LeSabre Estate Wagon 已核到 217.9 / 80 / 57.2。
Ultimate Specs
+1

LeSabre gen2 Wagon 1962-1963 已拆分：1963 Estate Wagon 已核到 215.7 / 78 / 57.9，改为可入库；1962 仍保留待终核。
Ultimate Specs

LeSabre gen2 Wagon 1964 已补强为可入库：UltimateSpecs / Automobile-Catalog / Carfolio 均给出 218.8 / 78 / 57.9。
Ultimate Specs
+2
Carfolio
+2

本轮完成后，早期 Wagon 缺口从 1959-1960 / 1962-1964 缩小为 1959高度 / 1962 Wagon。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟢 新完成	LeSabre gen1 Wagon 1960 / gen2 Wagon 1963-1964	本轮补齐早期 Wagon 3 条
🟡 继续推进	Buick LeSabre gen4 / gen5 Wagon	gen5 Wagon 只剩 1980；gen4 仍有 Sedan/Convertible/Wagon 高度缺口
🔴 待补强	LeSabre gen1 Wagon 1959 / gen2 Wagon 1962 / gen4 Wagon	仍有少量 wagon 尺寸/高度缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959			217.4	80.7		1959 Buick LeSabre Wagon Automobile-Catalog	早期高车顶wagon	待终核: 1959 Wagon高度	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1960			217.9	80	57.2	1960 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962						高车顶wagon	待终核: 1962 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog / Carfolio	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6		1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980				1980 Buick LeSabre Wagon production confirmed	高车顶wagon	待终核: 1980 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959 Wagon 高度。

LeSabre gen2：1962 Wagon 尺寸。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible 高度、1970-1975 Wagon 高度/尺寸。

LeSabre gen5：1980 Wagon 尺寸。

下一步


--- Round 40 / 下一步 ---
更新点

LeSabre gen5 Wagon 1980 已补强为可入库：UltimateSpecs 的 1980 LeSabre Estate Wagon 页面给出 Length 218.82、Width 80.12、Height 57.09，本轮取 218.8 / 80.1 / 57.1。
Ultimate Specs
+1

LeSabre gen5 Wagon 现已完成：1977-1985 中，1977-1983/1985 已有真实尺寸，1984 已确认剔除。

剩余待核集中到早期 Wagon 与 gen4 高度：1959 Wagon、1962 Wagon、1973/1974 Sedan 高度、1970/1971 Convertible 高度、1970-1976 Wagon。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟢 新完成	LeSabre gen5 Wagon	本轮补齐 1980 Wagon，gen5 Wagon 已无待终核尺寸行
🟡 继续推进	Buick LeSabre gen1/gen2/gen4	剩余集中在早期 Wagon 与 gen4 高度
🔴 待补强	LeSabre gen4 Wagon	1970-1976 Wagon 仍是最大缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959			217.4	80.7		1959 Buick LeSabre Wagon Automobile-Catalog	早期高车顶wagon	待终核: 1959 Wagon高度	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1960			217.9	80	57.2	1960 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962						高车顶wagon	待终核: 1962 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog / Carfolio	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6		1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980			218.8	80.1	57.1	1980 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in、宽度超 3XL+ 2.1 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959 Wagon 高度。

LeSabre gen2：1962 Wagon 尺寸。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible 高度、1970-1975 Wagon 高度/尺寸。

下一步


--- Round 41 / 下一步 ---
更新点

LeSabre gen2 Wagon 1962 本轮状态修正为“是否生产/资料冲突”：UltimateSpecs 的 LeSabre 车型索引里，1961 与 1963/1964 有 Estate Wagon 页面，但 1962 列表未显示 LeSabre Estate Wagon；同时部分 1963 Wagon 页面又带有“1962, 1963”生产年份描述，因此本轮不直接填 1963 尺寸，改为更准确的待核状态。
Ultimate Specs
+1

LeSabre gen4 Convertible 1970 参考车型补强：Hagerty 与 Automobile-Catalog 均确认 1970 Custom Convertible 长 220.2、宽 80，但高度仍缺，所以仍不入库。
哈盖提
+1

LeSabre gen2 Wagon 1964 继续保持可入库：Automobile-Catalog 明确 1964 Estate Wagon 为 218.8 / 78 / 57.9。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟢 已完成	Buick LeSabre gen3 / gen5 Wagon	gen3 全结构完成；gen5 Wagon 除 1984 剔除外均可入库
🟡 继续推进	Buick LeSabre gen1/gen2/gen4	本轮把 1962 Wagon 改成资料冲突待核，并补强 1970 Convertible 参考口径
🔴 待补强	LeSabre gen4 Wagon	1970-1976 Wagon 仍是最大缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959			217.4	80.7		1959 Buick LeSabre Wagon Automobile-Catalog	早期高车顶wagon	待终核: 1959 Wagon高度	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1960			217.9	80	57.2	1960 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962						高车顶wagon	待终核: 1962 Wagon是否生产/资料冲突		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog / Carfolio	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6		1973 Buick LeSabre Custom 4-Door Hardtop Automobile-Catalog	大型化sedan	待终核: 1973 Sedan高度	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9		1974 Buick LeSabre 4-Door Sedan Automobile-Catalog	大型化sedan	待终核: 1974 Sedan高度	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80		1970 Buick LeSabre Custom Convertible Automobile-Catalog / Hagerty	大型敞篷	待终核: 1970 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7		1971 Buick LeSabre Custom Convertible Automobile-Catalog	大型敞篷	待终核: 1971 Convertible高度		
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980			218.8	80.1	57.1	1980 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in、宽度超 3XL+ 2.1 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959 Wagon 高度。

LeSabre gen2：1962 Wagon 是否生产/资料冲突。

LeSabre gen4：1973 Sedan 高度、1974 Sedan 高度、1970 / 1971 Convertible 高度、1970-1975 Wagon 高度/尺寸。

下一步


--- Round 42 / 下一步 ---
更新点

LeSabre gen4 Convertible 1970 已补强为可入库：UltimateSpecs 给出 220.2 / 80 / 54.61，本轮取 220.2 / 80 / 54.6。
Ultimate Specs
+1

LeSabre gen4 Convertible 1971 已补强为可入库：UltimateSpecs 给出 220.71 / 79.69 / 53.9，本轮取 220.7 / 79.7 / 53.9。
Ultimate Specs
+1

LeSabre gen4 Sedan 1973 已补强为可入库：UltimateSpecs 给出 224.21 / 79.61 / 54.41，本轮取 224.2 / 79.6 / 54.4。
Ultimate Specs
+1

LeSabre gen4 Sedan 1974 已补强为可入库：UltimateSpecs 的 1974 Hardtop Sedan 口径给出 225.91 / 79.88 / 54.02，本轮取 225.9 / 79.9 / 54.0。
Ultimate Specs

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Buick Park Avenue / Buick Rainier	全部可入库
🟢 新完成	LeSabre gen4 Sedan / 1970-1971 Convertible	本轮补齐 1973/1974 Sedan 高度、1970/1971 Convertible 高度
🟡 继续推进	LeSabre gen1/gen2 Wagon	只剩 1959 Wagon 高度、1962 Wagon 资料冲突
🔴 待补强	LeSabre gen4 Wagon	1970-1976 Wagon 仍是最大缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959			217.4	80.7		1959 Buick LeSabre Wagon Automobile-Catalog	早期高车顶wagon	待终核: 1959 Wagon高度	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1960			217.9	80	57.2	1960 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962						高车顶wagon	待终核: 1962 Wagon是否生产/资料冲突		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog / Carfolio	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.4	1973 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9	54	1974 Buick LeSabre Hardtop Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80	54.6	1970 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7	53.9	1971 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9		1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1976 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980			218.8	80.1	57.1	1980 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in、宽度超 3XL+ 2.1 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959 Wagon 高度。

LeSabre gen2：1962 Wagon 是否生产/资料冲突。

LeSabre gen4：1970-1975 Wagon 高度/尺寸、1976 Wagon 高度。

下一步


--- Round 43 / 下一步 ---
更新点

LeSabre gen4 Wagon 1976 已补强为可入库：Automobile-Catalog 给出 1976 Buick Estate Wagon 长 231.8、宽 79.9、高 57.8，本轮补入高度并清除 1976 Wagon高度 待核。
汽车目录

LeSabre gen4 Wagon 待核范围从 1970-1976 缩小为 1970-1975。

LeSabre gen1 Wagon 1959 仍缺可靠 wagon 高度；LeSabre gen2 Wagon 1962 仍保留“是否生产/资料冲突”。

LeSabre gen5 Wagon 已保持完成状态：1980-1983/1985 可入库，1984 剔除。

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Park Avenue / Rainier	全部可入库
🟢 新完成	LeSabre gen4 Wagon 1976	本轮补入 1976 Estate Wagon 高度
🟡 继续推进	LeSabre gen1/gen2 Wagon	只剩 1959 Wagon 高度、1962 Wagon 资料冲突
🔴 待补强	LeSabre gen4 Wagon 1970-1975	当前最大剩余缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959			217.4	80.7		1959 Buick LeSabre Wagon Automobile-Catalog	早期高车顶wagon	待终核: 1959 Wagon高度	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1960			217.9	80	57.2	1960 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962						高车顶wagon	待终核: 1962 Wagon是否生产/资料冲突		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog / Carfolio	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.4	1973 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9	54	1974 Buick LeSabre Hardtop Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80	54.6	1970 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7	53.9	1971 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970-1975						大型高车顶wagon	待终核: 缺失 gen4 Wagon 1970-1975 全量数据		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9	57.8	1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980			218.8	80.1	57.1	1980 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in、宽度超 3XL+ 2.1 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959 Wagon 高度。

LeSabre gen2：1962 Wagon 是否生产/资料冲突。

LeSabre gen4：1970-1975 Wagon 高度/尺寸。

下一步


--- Round 44 / 下一步 ---
更新点

LeSabre gen4 Wagon 原 1970-1975 空白大段拆开：1970 改为“是否生产/资料冲突”，因为 Buick Estate 公开代际资料主要覆盖 1971-1976。
维基百科

1971-1973 改为“production confirmed / 待尺寸”，不再和 1970、1974-1975 混在一行。

1974、1975 已补入长宽：1974 Estate Wagon 为 231.1 / 79.9，1975 Estate Wagon 为 231.8 / 79.9；但高度未核到可靠值，仍待终核。
汽车目录
+1

1976 继续保持可入库：1976 Estate Wagon 长 231.8、宽 79.9，前轮次已补入高度 57.8。
汽车目录

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Park Avenue / Rainier	全部可入库
🟢 已完成	LeSabre gen3 / gen5 Wagon / gen4 Sedan / gen4 Convertible	已完成主要 sedan/coupe/convertible 与 gen5 wagon
🟡 继续推进	LeSabre gen4 Wagon	本轮把 1970-1975 大段拆细，补入 1974/1975 长宽
🔴 待补强	LeSabre gen1 1959 Wagon / gen2 1962 Wagon / gen4 Wagon 1970-1975	只剩早期 Wagon 与 gen4 Wagon 高度/尺寸缺口

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959			217.4	80.7		1959 Buick LeSabre Wagon Automobile-Catalog	早期高车顶wagon	待终核: 1959 Wagon高度	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1960			217.9	80	57.2	1960 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962						高车顶wagon	待终核: 1962 Wagon是否生产/资料冲突		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog / Carfolio	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.4	1973 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9	54	1974 Buick LeSabre Hardtop Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80	54.6	1970 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7	53.9	1971 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970						大型高车顶wagon	待终核: 1970 Wagon是否生产/资料冲突		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1971-1973				1971-1973 Buick Estate Wagon production confirmed	大型高车顶wagon	待终核: 1971-1973 Wagon尺寸		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1974			231.1	79.9		1974 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1974 Wagon高度	无可用尺码	长度超 3XXXL 13.1 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1975			231.8	79.9		1975 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	待终核: 1975 Wagon高度	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9	57.8	1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980			218.8	80.1	57.1	1980 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in、宽度超 3XL+ 2.1 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen1：1959 Wagon 高度。

LeSabre gen2：1962 Wagon 是否生产/资料冲突。

LeSabre gen4：1971-1973 Wagon 尺寸、1974-1975 Wagon 高度。

下一步


--- Round 45 / 下一步 ---
更新点

LeSabre gen1 Wagon 1959 已补强为可入库：Hometown Buick 给出 1959 LeSabre Estate Wagon 长 217.4、宽 80.7、高 57.1；ConceptCarz / Automobile-Catalog 也能确认 217.4 长度口径。
Hometown Buick
+2
conceptcarz.com
+2

LeSabre gen4 Wagon 1970 已补强为可入库：UltimateSpecs 给出 1970 Estate Wagon 223.31 / 80 / 57.09，本轮取 223.3 / 80 / 57.1。
Ultimate Specs

LeSabre gen4 Wagon 1971-1974 已拆成单年并补齐真实尺寸：1971 为 226.8 / 79.7 / 57.3；1972 为 228.3 / 80 / 57.1；1973 为 229.5 / 79.6 / 57.3；1974 为 231.1 / 79.9 / 57.9。
Ultimate Specs
+3
Ultimate Specs
+3
Ultimate Specs
+3

LeSabre gen4 Wagon 1975 已补齐高度：Carfolio 给出 1975 Estate Wagon 高度 1483 mm，折合约 58.4 in；长度 231.8 已由 Automobile-Catalog/公开资料确认，因此本轮改为可入库。
Carfolio
+1

当前批次进度

状态	车型	说明
🟢 已完成	Buick Lucerne / Park Avenue / Rainier	全部可入库
🟢 新完成	LeSabre gen1 1959 Wagon / gen4 Wagon 1970-1975	本轮补齐最大剩余缺口
🟢 已完成	LeSabre gen3 / gen4 Sedan & Convertible / gen5 Wagon	主要结构均已可入库
🟡 剩余待核	LeSabre gen2 1962 Wagon	仅剩“是否生产/资料冲突”占位行

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959			217.4	80.7	57.1	1959 Buick LeSabre Estate Wagon Hometown Buick / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1960			217.9	80	57.2	1960 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962						高车顶wagon	待终核: 1962 Wagon是否生产/资料冲突		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog / Carfolio	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.4	1973 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9	54	1974 Buick LeSabre Hardtop Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80	54.6	1970 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7	53.9	1971 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970			223.3	80	57.1	1970 Buick Estate Wagon UltimateSpecs / Automobile-Catalog	一年款B-body全尺寸wagon	可入库	无可用尺码	长度超 3XXXL 5.3 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1971			226.8	79.7	57.3	1971 Buick Estate Wagon UltimateSpecs	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1972			228.3	80	57.1	1972 Buick Estate Wagon UltimateSpecs	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 10.3 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1973			229.5	79.6	57.3	1973 Buick Estate Wagon UltimateSpecs / Automobile-Catalog	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 11.5 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1974			231.1	79.9	57.9	1974 Buick Estate Wagon UltimateSpecs / Automobile-Catalog	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 13.1 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1975			231.8	79.9	58.4	1975 Buick Estate Wagon Automobile-Catalog / Carfolio	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9	57.8	1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980			218.8	80.1	57.1	1980 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in、宽度超 3XL+ 2.1 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对

LeSabre gen2：1962 Wagon 是否生产/资料冲突。

下一步


--- Round 46 / 下一步 ---
更新点

LeSabre gen2 Wagon 1962 本轮收尾：Buick Estate 生产表显示 1962 年 LeSabre Estate 为 n/a，1962 年全尺寸 Estate Wagon 对应 Invicta；Over-Drive 的 1962 Buick full-size production PDF 也列出 Invicta Estate Wagon，而未列 LeSabre Estate Wagon。因此本轮将 1962 LeSabre Wagon 从“待终核”改为“剔除”。
维基百科
+1

当前批次剩余待终核已清完：早期 Wagon、gen4 Wagon、gen5 Wagon、Lucerne / Park Avenue / Rainier 均已处理完成。

当前批次进度

状态	车型	说明
🟢 已完成	Buick LeSabre	全结构已补齐；1962 Wagon 剔除
🟢 已完成	Buick Lucerne	可入库
🟢 已完成	Buick Park Avenue	可入库
🟢 已完成	Buick Rainier	可入库

本轮更新后的 TSV

tsv
主车型	品牌	分类	子车系	结构	版本	代际	年份	驾驶室类型	货斗长度_ft	max_length_in	max_width_in (w/o)	max_height_in	参考车型	备注	迭代状态	新尺码	总分析
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre sedan refs / 1960 Buick LeSabre 4-Door Sedan UltimateSpecs	早期全尺寸sedan	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Carfolio / 1960 Buick LeSabre 2-Door Sedan UltimateSpecs	早期全尺寸coupe	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen1 full-size	1959-1960			217.9	80.7	57.2	1959 Buick LeSabre Convertible UltimateSpecs / 1960 Buick LeSabre Convertible UltimateSpecs	早期全尺寸敞篷	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1959			217.4	80.7	57.1	1959 Buick LeSabre Estate Wagon Hometown Buick / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen1 full-size	1960			217.9	80	57.2	1960 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog	早期高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1961			213.2	78	56.3	1961 Buick LeSabre 4-Door Hardtop UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1962			214.1	77.9	56.4	1962 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre 4-Door Sedan / Hardtop Sedan refs	全尺寸sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre 4-Door Sedan UltimateSpecs	全尺寸sedan	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1961-1962			214.1	77.9	56.4	1961-1962 Buick LeSabre 2-Door Sedan UltimateSpecs	全尺寸2-door	可入库		
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1963			215.7	78	56.7	1963 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen2 full-size	1964			218.8	78	56.4	1964 Buick LeSabre Sport Coupe UltimateSpecs	全尺寸coupe	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1961-1962			214.1	77.9	55.6	1961-1962 Buick LeSabre Convertible refs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1963			215.7	78	55.6	1963 Buick LeSabre Convertible UltimateSpecs	全尺寸敞篷	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen2 full-size	1964			218.9	78	55.7	1964 Buick LeSabre Convertible Carfolio	全尺寸敞篷	可入库	无可用尺码	长度超 3XXXL 0.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1962						高车顶wagon	剔除: 1962 LeSabre Wagon未生产，1962 full-size Estate为Invicta		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1963			215.7	78	57.9	1963 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	3XXXL	
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen2 full-size	1964			218.8	78	57.9	1964 Buick LeSabre Estate Wagon UltimateSpecs / Automobile-Catalog / Carfolio	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Convertible UltimateSpecs	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre Convertible UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1968			217.5	80	54.9	1968 Buick LeSabre Custom Convertible Coupe Carfolio	宽体敞篷	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen3 full-size	1969			218.2	79.5	54.9	1969 Buick LeSabre Convertible UltimateSpecs	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre Custom Sport Coupe Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1966			217	80	54.4	1966 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1967			217.5	80	54.8	1967 Buick LeSabre Sport Coupe UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Sport Coupe UltimateSpecs	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 2-Door Hardtop Automobile-Catalog / Carfolio	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1965			216.8	80	55.5	1965 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1966			217	80	55.2	1966 Buick LeSabre 4-Door Sedan / 4-Door Hardtop UltimateSpecs / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1967			217.5	80	54.7	1967 Buick LeSabre 4-Door Hardtop Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1968			217.5	80	54.4	1968 Buick LeSabre Custom Hardtop Carfolio / Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen3 full-size	1969			218.2	79.5	55.3	1969 Buick LeSabre 4-Door Sedan Automobile-Catalog	宽体全尺寸	可入库	无可用尺码	长度超 3XXXL 0.2 in、宽度超 3XL+ 1.5 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1970			220.2	80	55.4	1970 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1971-1972			221.9	80	54.3	1971-1972 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1973			224.2	79.6	54.4	1973 Buick LeSabre 4-Door Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1974			225.9	79.9	54	1974 Buick LeSabre Hardtop Sedan UltimateSpecs / Automobile-Catalog	大型化sedan	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen4 full-size	1975-1976			226.8	79.9	54	1975-1976 Buick LeSabre 4-Door Sedan UltimateSpecs	大型化sedan	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1970-1971			220.7	79.7	53.6	1970-1971 Buick LeSabre Sport Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1972			221.9	80	53.5	1972 Buick LeSabre Sport Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1973			224.2	79.6	53.6	1973 Buick LeSabre Hardtop Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 6.2 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1974			225.9	79.9	54.9	1974 Buick LeSabre Hardtop Coupe Automobile-Catalog	大型化coupe	可入库	无可用尺码	长度超 3XXXL 7.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen4 full-size	1975-1976			226.8	79.9	53.2	1975-1976 Buick LeSabre Coupe UltimateSpecs	大型化coupe	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1970			220.2	80	54.6	1970 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.2 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1971			220.7	79.7	53.9	1971 Buick LeSabre Custom Convertible UltimateSpecs / Automobile-Catalog	大型敞篷	可入库	无可用尺码	长度超 3XXXL 2.7 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1972			221.9	80	53.9	1972 Buick LeSabre Convertible UltimateSpecs	大型敞篷	可入库	无可用尺码	长度超 3XXXL 3.9 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Convertible	Std.	gen4 full-size	1975			226.9	79.9	53.8	1975 Buick LeSabre Custom Convertible ConceptCarz	末期敞篷	可入库	无可用尺码	长度超 3XXXL 8.9 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1970			223.3	80	57.1	1970 Buick Estate Wagon UltimateSpecs / Automobile-Catalog	一年款B-body全尺寸wagon	可入库	无可用尺码	长度超 3XXXL 5.3 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1971			226.8	79.7	57.3	1971 Buick Estate Wagon UltimateSpecs	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 8.8 in、宽度超 3XL+ 1.7 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1972			228.3	80	57.1	1972 Buick Estate Wagon UltimateSpecs	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 10.3 in、宽度超 3XL+ 2 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1973			229.5	79.6	57.3	1973 Buick Estate Wagon UltimateSpecs / Automobile-Catalog	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 11.5 in、宽度超 3XL+ 1.6 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1974			231.1	79.9	57.9	1974 Buick Estate Wagon UltimateSpecs / Automobile-Catalog	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 13.1 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1975			231.8	79.9	58.4	1975 Buick Estate Wagon Automobile-Catalog / Carfolio	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen4 full-size	1976			231.8	79.9	57.8	1976 Buick Estate Wagon Automobile-Catalog	大型高车顶wagon	可入库	无可用尺码	长度超 3XXXL 13.8 in、宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1977-1978			218.2	77.2	55.7	1977 Buick LeSabre Sedan Automobile-Catalog / 1978 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1979			218.2	77.2	55.7	1979 Buick LeSabre Limited Sedan Automobile-Catalog	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Sedan UltimateSpecs	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Sedan UltimateSpecs / Automobile-Catalog	RWD downsized sedan	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1982-1984			218	78	56	1982-1984 Buick LeSabre Limited Sedan refs	早期80年代RWD sedan	可入库	3XXXL	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen5 downsized full-size	1985			218	78	56	1985 Buick LeSabre Limited Sedan iSeeCars	RWD downsized sedan	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1977			218.2	77.2	55.3	1977 Buick LeSabre Sport Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1978-1979			218.2	77.2	55	1978-1979 Buick LeSabre Coupe UltimateSpecs / Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1980			217.4	78	55	1980 Buick LeSabre Limited Coupe Automobile-Catalog	RWD downsized coupe	可入库	3XXXL	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1981			218.4	75.9	55	1981 Buick LeSabre Coupe Carfolio	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen5 downsized full-size	1982-1985			218.4	75.9	56	1982 Buick LeSabre Coupe UltimateSpecs / 1983-1985 Buick LeSabre Coupe UltimateSpecs	RWD downsized coupe	可入库	无可用尺码	长度超 3XXXL 0.4 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1977-1978			216.7	79.9	56.5	1977-1978 Buick Estate Wagon Carfolio	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1979			216.7	79.9	56.5	1979 Buick Estate Wagon Limited Automobile-Catalog	高车顶wagon	可入库	无可用尺码	宽度超 3XL+ 1.9 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1980			218.8	80.1	57.1	1980 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 0.8 in、宽度超 3XL+ 2.1 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1981			220.5	79.3	57.1	1981 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1982			220.5	79.3	59.4	1982 Buick LeSabre Estate Wagon UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1983			220.5	79.3	59.1	1983 Buick LeSabre Estate Wagon Automobile-Catalog	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.5 in、宽度超 3XL+ 1.3 in
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1984						高车顶wagon	剔除: 1984 LeSabre Wagon未生产		
Buick LeSabre	Buick	两厢车	Buick LeSabre	Wagon	Std.	gen5 downsized full-size	1985			220.3	79.8	58.5	1985 Buick LeSabre Estate Wagon Automobile-Catalog / UltimateSpecs	高车顶wagon	可入库	无可用尺码	长度超 3XXXL 2.3 in、宽度超 3XL+ 1.8 in
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1986			196.2	72.1	55.5	1986 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1987			196.5	72.1	55.5	1987 Buick LeSabre Sedan UltimateSpecs	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1988			196.5	72.4	55.4	1988 Buick LeSabre Sedan AutoDetective	早期FWD sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1989			196.9	72.4	54.9	1989 Buick LeSabre Sedan Automobile-Catalog	FWD缩小	待终核: 1989长度来源差异	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1990			196.5	72.4	54.9	1990 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen6 full-size	1991			196.5	72.4	54.6	1991 Buick LeSabre Sedan Edmunds	FWD缩小	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1986			196.5	72.1	54.7	1986 Buick LeSabre Coupe Carfolio	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1987-1988			196.9	72.4	54.7	1987-1988 Buick LeSabre Coupe UltimateSpecs / proxy cross-check	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1989			196.9	72.4	54.7	1989 Buick LeSabre T-Type Coupe Automobile-Catalog	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	跑车	Buick LeSabre	Coupe	Std.	gen6 full-size	1990-1991			196.5	72.4	53.8	1990 Buick LeSabre Coupe AutoDetective / 1991 Buick LeSabre Coupe Edmunds	FWD coupe低车顶	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1992-1996			200	74.9	55.7	1992/1996 Buick LeSabre Sedan Edmunds	sedan	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen7 full-size	1997-1999			200.8	74.4	55.6	1997-1999 Buick LeSabre Sedan Edmunds	小改款	可入库	3XL+	
Buick LeSabre	Buick	三厢车	Buick LeSabre	Sedan	Std.	gen8 full-size	2000-2005			200	73.5	57	2000-2005 Buick LeSabre Sedan Edmunds	末代sedan	可入库	3XL+	
Buick Lucerne	Buick	三厢车	Buick Lucerne	Sedan	Std.	gen1 full-size sedan	2006-2011			203.2	73.8	58	2006-2011 Buick Lucerne Sedan Edmunds	大型轿车	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1991			205.2	74.9	55.7	1991 Buick Park Avenue Edmunds / Automobile-Catalog width cross-check	早期FWD luxury sedan；A-C宽度73.6但Edmunds写w/o 74.9	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1992			205.3	73.6	55.1	1992 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1993			205.2	74.9	55.1	1993 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1994			205.2	73.6	55.1	1994 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen1 full-size luxury	1995-1996			205.9	74.1	55.1	1995-1996 Buick Park Avenue Edmunds	大型FWD sedan	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1997-1998			206.8	74.7	57.4	1997-1998 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	1999			206.8	74.4	57.4	1999 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Park Avenue	Buick	三厢车	Buick Park Avenue	Sedan	Std.	gen2 full-size luxury	2000-2005			206.8	74.7	57.4	2000-2005 Buick Park Avenue Edmunds	高度增加	可入库	3XXL	
Buick Rainier	Buick	越野车	Buick Rainier	SUV	Std.	gen1 midsize SUV	2004-2007			193.4	75.4	74.5	2004-2007 Buick Rainier Edmunds	中型SUV	可入库	YXXL	

下一步优先核对
无，当前批次已完成。

本批次完成。

